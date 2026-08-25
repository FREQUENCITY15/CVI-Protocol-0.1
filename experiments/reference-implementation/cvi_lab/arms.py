"""
The three experimental arms: S (static one-shot), S' (static
self-critique, no environment feedback), C (causal interactive).

Context-boundary discipline (enforced in code):

* Each PHASE of an arm runs in its own session.  A session is a message
  list; at a phase boundary the list is destroyed and a new one starts.
  Nothing — no messages, no scratchpads, no model state — crosses a
  boundary.
* Arm S receives NO feedback of any kind, ever.
* Arm S' may generate -> self-critique -> revise within its private
  critique session, but NEVER receives any environment feedback.  Its
  programs are never executed during the critique phase.
* Arm C's interaction session receives ONLY the permitted public-test
  feedback (pass/fail + error class per public case).  Hidden results are
  graded by the harness and never placed in any participant-facing text.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple

from . import grader, ordermachine as om
from .config import PilotConfig
from .generator import Task
from .participant import LLMResponse, ParticipantClient

PROGRAM_SECTION_RE = re.compile(
    r"###\s*TASK\s+([A-Za-z0-9_\-]+)\s*\n(.*?)###\s*END",
    re.DOTALL | re.IGNORECASE)

SELF_REPORT_QUESTION = (
    "Did your approach to OrderMachine tasks change during this "
    "experiment? If so, describe the rule you now apply.")

# ---------------------------------------------------------------------------
# Phase 0 (baseline) — CVI-0.1 refinement 1
# ---------------------------------------------------------------------------
# A SINGLE shared prompt-construction path for all three arms.  The
# participant-visible bytes (system text + user text) are identical across
# S / S' / C; each arm still makes its own independent participant call in
# its own session.  This heading contains NO treatment-identifying text
# (no arm names, no self-critique/causal/feedback/revise wording).

BASELINE_HEADING = (
    "Attempt each of the following tasks ONE time. Write one OrderMachine "
    "program per task.")

# Substrings that must never appear in a Phase-0 participant prompt.
TREATMENT_LABEL_SUBSTRINGS = (
    "arm s", "arm s'", "arm s\u2032", "arm c", "self-critique", "causal",
    "scratchpad", "feedback", "revise", "test results",
)


def build_baseline_prompt(tasks: List[Task]) -> str:
    """The ONE Phase-0 prompt builder used by every arm.  Identical
    input task list => identical prompt bytes."""
    return build_batch_prompt(tasks, BASELINE_HEADING)


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def build_system_prompt(spec: str) -> str:
    return (
        "You are a participant in a controlled experiment about writing "
        "programs in a small language called OrderMachine. The full "
        "language specification is given below. Solve each task by writing "
        "an OrderMachine program. You have no tools and cannot execute "
        "code; the only thing you can do is write program text.\n"
        "When asked for programs, use this strict format for every task:\n\n"
        "### TASK <task-id>\n"
        "<the program text>\n"
        "### END\n\n"
        "Any text outside these sections is ignored by the grader.\n\n"
        "---- OrderMachine language specification ----\n\n" + spec)


def build_batch_prompt(tasks: List[Task], heading: str,
                       notes: str = "") -> str:
    parts = [heading, notes.strip(), ""]
    for task in tasks:
        view = task.public_view()
        parts.append(f"## Task {task.task_id}")
        parts.append(view["description"])
        parts.append("Worked examples (inputs -> expected output):")
        for ex in view["public_examples"]:
            parts.append(f"  case {ex['case_id']}: inputs "
                         f"{json.dumps(ex['inputs'])} -> "
                         f"{json.dumps(ex['expected_output'])}")
        parts.append("")
    return "\n".join(parts)


def parse_programs(text: str, task_ids: List[str]
                   ) -> Tuple[Dict[str, str], List[str]]:
    """Extract per-task program sections.  Missing sections yield empty
    programs (which deterministically score 0) and an anomaly note."""
    found: Dict[str, str] = {}
    anomalies: List[str] = []
    for match in PROGRAM_SECTION_RE.finditer(text):
        found[match.group(1).upper()] = match.group(2).strip()
    for tid in task_ids:
        key = tid.upper()
        if key not in found:
            anomalies.append(f"missing program section for {tid}")
            found[tid] = ""
    return {tid: found.get(tid.upper(), "") for tid in task_ids}, anomalies


# ---------------------------------------------------------------------------
# Evidence sink (arms write through this; tests use an in-memory stand-in)
# ---------------------------------------------------------------------------

class EvidenceSink(Protocol):
    def save_prompt(self, arm: str, phase: str, session_id: str,
                    filename: str, text: str) -> None: ...
    def save_transcript(self, arm: str, phase: str, session_id: str,
                        filename: str, obj: Dict[str, Any]) -> None: ...
    def save_submission(self, arm: str, task_id: str, version: int,
                        program: str) -> None: ...
    def save_env_log(self, arm: str, task_id: str, round_index: int,
                     obj: Dict[str, Any]) -> None: ...


# ---------------------------------------------------------------------------
# Session record
# ---------------------------------------------------------------------------

@dataclass
class Session:
    arm: str
    phase: str
    session_id: str
    started_iso: str
    messages: List[Dict[str, str]] = field(default_factory=list)
    turns: List[Dict[str, Any]] = field(default_factory=list)

    def add_turn(self, role: str, content: str, response: LLMResponse,
                 label: str) -> None:
        self.messages.append({"role": role, "content": content})
        if response is not None:
            self.messages.append({"role": "assistant",
                                  "content": response.text})
        self.turns.append({
            "label": label,
            "role": role,
            "content": content,
            "response_text": response.text if response else None,
            "stop_reason": response.stop_reason if response else None,
            "input_tokens": response.input_tokens if response else 0,
            "output_tokens": response.output_tokens if response else 0,
            "cache_read_tokens": response.cache_read_tokens
            if response else 0,
            "cache_creation_tokens": response.cache_creation_tokens
            if response else 0,
            "latency_s": round(response.latency_s, 3) if response else 0.0,
        })

    def finished(self) -> str:
        return _now()


# ---------------------------------------------------------------------------
# Arm runner
# ---------------------------------------------------------------------------

@dataclass
class ArmResult:
    arm: str
    result: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"arm": self.arm, "result": self.result}


class ArmRunner:
    def __init__(self, arm: str, client: ParticipantClient, config: PilotConfig,
                 sink: EvidenceSink):
        self.arm = arm
        self.client = client
        self.config = config
        self.sink = sink
        self.session_counter = 0
        self.anomalies: List[str] = []
        self.sessions: List[Session] = []
        self.result: Dict[str, Any] = {}
        # Submission versioning is per (arm, task) ACROSS phases: each new
        # attempt — baseline, revision, retention, transfer, hidden — gets
        # the next version number.  Version history is append-only.
        self.submission_counts: Dict[str, int] = {}

    def next_version(self, task_id: str) -> int:
        self.submission_counts[task_id] = \
            self.submission_counts.get(task_id, 0) + 1
        return self.submission_counts[task_id]

    def new_session(self, phase: str) -> Session:
        self.session_counter += 1
        session = Session(
            arm=self.arm, phase=phase,
            session_id=f"{self.arm}-{phase}-{self.session_counter}",
            started_iso=_now())
        self.sessions.append(session)
        return session

    def call(self, session: Session, role: str, content: str, label: str,
             max_tokens: Optional[int] = None) -> LLMResponse:
        self.sink.save_prompt(
            self.arm, session.phase, session.session_id,
            f"prompt_{len(session.turns):03d}_{label}.txt", content)
        response = self.client.complete(
            system=build_system_prompt(om.PARTICIPANT_SPEC),
            messages=[{"role": m["role"], "content": m["content"]}
                      for m in session.messages] + [{"role": role,
                                                     "content": content}],
            max_tokens=max_tokens or self.config.model.max_tokens_per_call,
            label=f"{self.arm}:{session.phase}:{label}")
        session.add_turn(role, content, response, label)
        self.sink.save_transcript(
            self.arm, session.phase, session.session_id,
            f"turn_{len(session.turns):03d}_{label}.json",
            {"session_id": session.session_id,
             "turns": session.turns})
        return response

    # -- shared phases ------------------------------------------------------

    def run_phase_0(self, tasks: List[Task]) -> Dict[str, Any]:
        """Phase 0 baseline: every arm uses the SAME shared prompt path
        (build_baseline_prompt) in its OWN fresh session and makes its own
        independent participant call.  The prompt bytes and its SHA-256 are
        recorded for cross-arm identity verification."""
        session = self.new_session("baseline")
        prompt = build_baseline_prompt(tasks)
        started = time.monotonic()
        response = self.call(session, "user", prompt, "baseline")
        elapsed = time.monotonic() - started
        programs, anomalies = parse_programs(response.text,
                                             [t.task_id for t in tasks])
        self.anomalies.extend(f"baseline: {a}" for a in anomalies)
        per_task: Dict[str, Any] = {}
        for task in tasks:
            program = programs[task.task_id]
            score = grader.hidden_score(task, program)
            self.sink.save_submission(self.arm, task.task_id,
                                      self.next_version(task.task_id),
                                      program)
            per_task[task.task_id] = {
                "program": program,
                "hidden_score": score,
                "hidden_results": [r.to_dict()
                                   for r in grader.run_hidden(task, program)],
            }
        record = {"tasks": per_task, "elapsed_s": round(elapsed, 3),
                  "label": "baseline", "session_id": session.session_id}
        self.result["phase_0"] = record
        self.result["phase_0_prompt_sha256"] = hashlib.sha256(
            prompt.encode("utf-8")).hexdigest()
        return record

    def one_shot(self, session: Session, tasks: List[Task], heading: str,
                 label: str) -> Dict[str, Any]:
        prompt = build_batch_prompt(tasks, heading)
        started = time.monotonic()
        response = self.call(session, "user", prompt, label)
        elapsed = time.monotonic() - started
        programs, anomalies = parse_programs(response.text,
                                             [t.task_id for t in tasks])
        self.anomalies.extend(
            f"{label}: {a}" for a in anomalies)
        per_task: Dict[str, Any] = {}
        for task in tasks:
            program = programs[task.task_id]
            score = grader.hidden_score(task, program)
            self.sink.save_submission(self.arm, task.task_id,
                                      self.next_version(task.task_id),
                                      program)
            per_task[task.task_id] = {
                "program": program,
                "hidden_score": score,
                "hidden_results": [r.to_dict()
                                   for r in grader.run_hidden(task, program)],
            }
        return {"tasks": per_task, "elapsed_s": round(elapsed, 3),
                "label": label}

    def run_ret_transfer(self, tasks_a: List[Task],
                         tasks_b: List[Task]) -> None:
        """Retention + transfer legs: fresh sessions, one-shot, no
        feedback.  These run BEFORE Family C exists."""
        phases: List[Tuple[str, List[Task], str]] = [
            ("ret", tasks_a,
             "Attempt each of the following tasks ONE time. Write one "
             "OrderMachine program per task. You will receive no feedback."),
            ("transfer", tasks_b,
             "Attempt each of the following tasks ONE time. Write one "
             "OrderMachine program per task. You will receive no feedback."),
        ]
        for phase_name, tasks, heading in phases:
            session = self.new_session(phase_name)
            record = self.one_shot(session, tasks, heading, phase_name)
            record["session_id"] = session.session_id
            self.result[f"phase_{phase_name}"] = record

    def run_hidden_probe(self, tasks_c: List[Task]) -> None:
        """Hidden-verification leg + self-report probe: fresh sessions.
        tasks_c is generated only after every interaction phase has
        completed (protocol gate)."""
        session = self.new_session("hidden")
        record = self.one_shot(
            session, tasks_c,
            "Attempt each of the following tasks ONE time. Write one "
            "OrderMachine program per task. You will receive no feedback.",
            "hidden")
        record["session_id"] = session.session_id
        self.result["phase_hidden"] = record
        # Self-report probe: separate session, separate storage.
        session = self.new_session("probe")
        started = time.monotonic()
        response = self.call(session, "user", SELF_REPORT_QUESTION, "probe")
        self.result["self_report"] = {
            "question": SELF_REPORT_QUESTION,
            "answer": response.text,
            "session_id": session.session_id,
            "elapsed_s": round(time.monotonic() - started, 3),
        }

    def finish(self) -> Dict[str, Any]:
        self.result["sessions"] = [
            {"session_id": s.session_id, "phase": s.phase,
             "turns": len(s.turns),
             "input_tokens": sum(t["input_tokens"] for t in s.turns),
             "output_tokens": sum(t["output_tokens"] for t in s.turns)}
            for s in self.sessions]
        self.result["anomalies"] = list(self.anomalies)
        return self.result


# ---------------------------------------------------------------------------
# Arm S — static one-shot
# ---------------------------------------------------------------------------

def run_arm_s_pre(client: ParticipantClient, config: PilotConfig,
                  sink: EvidenceSink, tasks_a: List[Task],
                  tasks_b: List[Task]) -> ArmRunner:
    runner = ArmRunner("S", client, config, sink)
    # Phase 0: shared, prompt-identical baseline (independent call).
    runner.run_phase_0(tasks_a)
    # Arm S has no Phase-1 interaction.
    runner.result["phase_a"] = {"note": "Arm S has no Phase-1 phase"}
    runner.result["phase_post"] = None  # no interaction exists in Arm S
    runner.run_ret_transfer(tasks_a, tasks_b)
    return runner


def run_arm_s(client: ParticipantClient, config: PilotConfig,
              sink: EvidenceSink, tasks_a: List[Task], tasks_b: List[Task],
              tasks_c: List[Task]) -> Dict[str, Any]:
    runner = run_arm_s_pre(client, config, sink, tasks_a, tasks_b)
    runner.run_hidden_probe(tasks_c)
    return runner.finish()


# ---------------------------------------------------------------------------
# Arm S' — static self-critique, NO environment feedback
# ---------------------------------------------------------------------------

def run_arm_sprime_pre(client: ParticipantClient, config: PilotConfig,
                       sink: EvidenceSink, tasks_a: List[Task],
                       tasks_b: List[Task]) -> ArmRunner:
    runner = ArmRunner("S_PRIME", client, config, sink)
    # Phase 0: shared, prompt-identical baseline (independent call).
    runner.run_phase_0(tasks_a)
    # Phase 1': private critique (no environment feedback).
    session = runner.new_session("critique")
    tasks = tasks_a
    heading = ("Attempt each of the following tasks. You will work in a "
               "private scratchpad. You will receive NO test results of any "
               "kind — you must judge your own work.")
    prompt = build_batch_prompt(tasks, heading)
    response = runner.call(session, "user", prompt, "round_0")
    programs, anomalies = parse_programs(response.text,
                                         [t.task_id for t in tasks])
    runner.anomalies.extend(f"round_0: {a}" for a in anomalies)
    rounds: List[Dict[str, Any]] = []
    rounds.append({"round": 0, "programs": {
        t.task_id: {"program": programs[t.task_id],
                    "hidden_score": grader.hidden_score(t, programs[t.task_id]),
                    "hidden_results": [
                        r.to_dict() for r in grader.run_hidden(
                            t, programs[t.task_id])]}
        for t in tasks}})
    for t in tasks:
        runner.sink.save_submission(runner.arm, t.task_id,
                                    runner.next_version(t.task_id),
                                    programs[t.task_id])
    for r in range(1, config.r + 1):
        critique = (
            f"Round {r}/{config.r} — self-critique. Review each of your "
            f"programs above against the task requirements and the language "
            f"specification. If you believe a program is wrong, write a "
            f"corrected version. You receive no execution results in this "
            f"phase; judge purely from the specification. Output all "
            f"{len(tasks)} programs again in the required format.\n\n"
            f"Your programs from the previous round:\n")
        for t in tasks:
            critique += (f"\n### TASK {t.task_id}\n{programs[t.task_id]}\n"
                         f"### END\n")
        response = runner.call(session, "user", critique, f"round_{r}")
        programs, anomalies = parse_programs(response.text,
                                             [t.task_id for t in tasks])
        runner.anomalies.extend(f"round_{r}: {a}" for a in anomalies)
        rounds.append({"round": r, "programs": {
            t.task_id: {"program": programs[t.task_id],
                        "hidden_score": grader.hidden_score(
                            t, programs[t.task_id]),
                        "hidden_results": [
                            r_.to_dict() for r_ in grader.run_hidden(
                                t, programs[t.task_id])]}
            for t in tasks}})
        for t in tasks:
            runner.sink.save_submission(runner.arm, t.task_id,
                                        runner.next_version(t.task_id),
                                        programs[t.task_id])
    runner.result["phase_a"] = {
        "session_id": session.session_id,
        "rounds": rounds,
        "revision_rounds_used": len(rounds) - 1,
        "initial": {tid: rounds[0]["programs"][tid]
                    for tid in [t.task_id for t in tasks]},
        "final": {tid: rounds[-1]["programs"][tid]
                  for tid in [t.task_id for t in tasks]},
    }
    runner.result["phase_post"] = {
        "tasks": {tid: rounds[-1]["programs"][tid]
                  for tid in [t.task_id for t in tasks]}}
    runner.run_ret_transfer(tasks_a, tasks_b)
    return runner


def run_arm_sprime(client: ParticipantClient, config: PilotConfig,
                   sink: EvidenceSink, tasks_a: List[Task],
                   tasks_b: List[Task], tasks_c: List[Task]
                   ) -> Dict[str, Any]:
    runner = run_arm_sprime_pre(client, config, sink, tasks_a, tasks_b)
    runner.run_hidden_probe(tasks_c)
    return runner.finish()


# ---------------------------------------------------------------------------
# Arm C — causal interactive (permitted public feedback only)
# ---------------------------------------------------------------------------

def run_arm_c_pre(client: ParticipantClient, config: PilotConfig,
                  sink: EvidenceSink, tasks_a: List[Task],
                  tasks_b: List[Task]) -> ArmRunner:
    runner = ArmRunner("C", client, config, sink)
    # Phase 0: shared, prompt-identical baseline (independent call).
    runner.run_phase_0(tasks_a)
    # Phase 1: causal interaction (permitted public feedback only).
    session = runner.new_session("interaction")
    tasks = tasks_a
    prompt = build_batch_prompt(
        tasks, "Attempt each of the following tasks. After you submit, your "
        "programs will be run on the worked examples and you will receive "
        "the outcomes, after which you may revise.")
    response = runner.call(session, "user", prompt, "round_0")
    programs, anomalies = parse_programs(response.text,
                                         [t.task_id for t in tasks])
    runner.anomalies.extend(f"round_0: {a}" for a in anomalies)

    rounds: List[Dict[str, Any]] = []
    public_all_pass_tasks: set = set()

    def grade_round(round_idx: int, progs: Dict[str, str]) -> None:
        record: Dict[str, Any] = {"round": round_idx, "tasks": {}}
        for t in tasks:
            program = progs[t.task_id]
            public = grader.run_public(t, program)
            hidden = grader.run_hidden(t, program)
            runner.sink.save_submission(runner.arm, t.task_id,
                                        runner.next_version(t.task_id),
                                        program)
            runner.sink.save_env_log(runner.arm, t.task_id, round_idx, {
                "round": round_idx,
                "public_results": [r.to_dict() for r in public],
                "hidden_results": [r.to_dict() for r in hidden],
                "hidden_score": sum(1 for r in hidden if r.passed)
                / len(hidden) if hidden else 0.0,
                "public_all_pass": grader.public_all_pass(public),
            })
            record["tasks"][t.task_id] = {
                "program": program,
                "public_results": [r.to_dict() for r in public],
                "hidden_results": [r.to_dict() for r in hidden],
                "hidden_score": (sum(1 for r in hidden if r.passed)
                                 / len(hidden)) if hidden else 0.0,
                "public_all_pass": grader.public_all_pass(public),
            }
            if grader.public_all_pass(public):
                public_all_pass_tasks.add(t.task_id)
        rounds.append(record)

    grade_round(0, programs)
    for r in range(1, config.r + 1):
        if public_all_pass_tasks == {t.task_id for t in tasks}:
            break  # causal stop signal: every task passes its public tests
        feedback_parts = [
            "ENVIRONMENT FEEDBACK — results of running your programs on the "
            "worked examples (this is the only information you will "
            "receive about your programs):",
            ""]
        for t in tasks:
            public = grader.run_public(t, programs[t.task_id])
            feedback_parts.append(grader.feedback_block(t.task_id, public))
        feedback_parts.append("")
        feedback_parts.append(
            f"Round {r}/{config.r}: revise any failing programs and output "
            f"all {len(tasks)} programs again in the required format.")
        response = runner.call(session, "user", "\n".join(feedback_parts),
                               f"revise_{r}")
        programs, anomalies = parse_programs(response.text,
                                             [t.task_id for t in tasks])
        runner.anomalies.extend(f"revise_{r}: {a}" for a in anomalies)
        grade_round(r, programs)

    runner.result["phase_a"] = {
        "session_id": session.session_id,
        "rounds": rounds,
        "revision_rounds_used": len(rounds) - 1,
        "initial": rounds[0]["tasks"],
        "final": rounds[-1]["tasks"],
    }
    runner.result["phase_post"] = {"tasks": rounds[-1]["tasks"]}
    runner.run_ret_transfer(tasks_a, tasks_b)
    return runner


def run_arm_c(client: ParticipantClient, config: PilotConfig,
              sink: EvidenceSink, tasks_a: List[Task], tasks_b: List[Task],
              tasks_c: List[Task]) -> Dict[str, Any]:
    runner = run_arm_c_pre(client, config, sink, tasks_a, tasks_b)
    runner.run_hidden_probe(tasks_c)
    return runner.finish()


ARM_RUNNERS = {"S": run_arm_s, "S_PRIME": run_arm_sprime, "C": run_arm_c}
