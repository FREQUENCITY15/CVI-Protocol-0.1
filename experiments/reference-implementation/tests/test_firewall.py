"""
Experimental-firewall tests: hidden-test inaccessibility, context
isolation, protocol gate, and arm-feedback separation.

These tests prove — mechanically, not by instruction — that participant
facing interfaces cannot retrieve protected material.
"""

import json
import os
import unittest

from cvi_lab import arms, generator as gen, grader, ordermachine as om
from cvi_lab.config import PilotConfig
from cvi_lab.participant import LLMResponse
from cvi_lab.protocol import PilotProtocol, ProtocolError

SEED_A = 515151
SEED_B = 616161
SEED_C = 717171
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "cvi_lab")


class MemorySink:
    """Captures everything the arms write; lets tests inspect the raw
    artifacts that would land in an evidence package."""

    def __init__(self):
        self.prompts = {}       # path -> text
        self.transcripts = {}   # path -> obj
        self.submissions = {}   # path -> text
        self.env_logs = {}      # path -> obj

    def save_prompt(self, arm, phase, session_id, filename, text):
        self.prompts[(arm, phase, filename)] = text

    def save_transcript(self, arm, phase, session_id, filename, obj):
        self.transcripts[(arm, phase, filename)] = obj

    def save_submission(self, arm, task_id, version, program):
        self.submissions[(arm, task_id, version)] = program

    def save_env_log(self, arm, task_id, round_index, obj):
        self.env_logs[(arm, task_id, round_index)] = obj


class MockClient:
    """Stateless-looking participant client whose responses are scripted
    per label.  Records every (messages) list it is handed, so tests can
    prove nothing crosses a context boundary."""

    def __init__(self, responder):
        self.responder = responder
        self.calls = []  # (label, messages)

    def complete(self, system, messages, max_tokens, label):
        self.calls.append((label, json.loads(json.dumps(messages))))
        text = self.responder(label)
        return LLMResponse(
            text=text, model="mock", stop_reason="end_turn",
            input_tokens=10, output_tokens=len(text) // 4,
            cache_read_tokens=0, cache_creation_tokens=0, latency_s=0.0)


def _program_section(task_id, program):
    return f"### TASK {task_id}\n{program}\n### END\n"


def _task_sections(text: str):
    """Split visible text into per-task bodies (text following each
    '## Task <id>' heading)."""
    import re
    sections = {}
    parts = re.split(r"## Task ([A-Za-z0-9_\-]+)", text)
    for i in range(1, len(parts), 2):
        sections.setdefault(parts[i], []).append(parts[i + 1])
    return sections


class TestParticipantModuleBoundary(unittest.TestCase):
    """The participant client has no import path to protected modules."""

    def test_participant_imports_no_protected_modules(self):
        src = open(os.path.join(PKG, "participant.py")).read()
        for banned in ("grader", "generator", "evidence", "ordermachine"):
            self.assertNotIn(f"import {banned}", src)
            self.assertNotIn(f"from .{banned}", src)
            self.assertNotIn(f"from cvi_lab.{banned}", src)

    def test_public_view_is_the_only_task_material(self):
        task = gen.generate_family_a(4, SEED_A)[0]
        view = task.public_view()
        self.assertEqual(
            set(view.keys()), {"task_id", "description", "public_examples"})


class TestProtocolGate(unittest.TestCase):
    def test_family_c_refused_before_interaction_complete(self):
        protocol = PilotProtocol()
        with self.assertRaises(ProtocolError):
            protocol.generate_family_c(seed=SEED_C, tier=2)

    def test_family_c_allowed_after_interaction_complete(self):
        protocol = PilotProtocol()
        protocol.mark_interaction_complete()
        tasks = protocol.generate_family_c(seed=SEED_C, tier=2)
        self.assertEqual(len(tasks), 4)
        self.assertTrue(protocol.log.family_c_generated_iso)

    def test_family_c_single_generation(self):
        protocol = PilotProtocol()
        protocol.mark_interaction_complete()
        protocol.generate_family_c(seed=SEED_C, tier=2)
        with self.assertRaises(ProtocolError):
            protocol.generate_family_c(seed=SEED_C, tier=2)


class TestContextIsolation(unittest.TestCase):
    def test_phase_boundaries_are_fresh_sessions(self):
        tasks_a = gen.generate_family_a(4, SEED_A)
        tasks_b = gen.generate_family_b(tasks_a, SEED_B)
        protocol = PilotProtocol()
        protocol.mark_interaction_complete()
        tasks_c = protocol.generate_family_c(seed=SEED_C, tier=2)
        cfg = PilotConfig()

        programs = {t.task_id: t.naive_program for t in tasks_a}
        programs.update({t.task_id: t.naive_program for t in tasks_b})
        programs.update({t.task_id: t.naive_program for t in tasks_c})

        def responder(label):
            # Every phase call returns all requested sections as naive
            # programs; the response text also embeds the interaction
            # program texts so we can detect cross-phase leakage.
            parts = []
            for tid, prog in programs.items():
                parts.append(_program_section(tid, prog))
            return "\n".join(parts)

        client = MockClient(responder)
        sink = MemorySink()
        result = arms.run_arm_c(client, cfg, sink, tasks_a, tasks_b, tasks_c)

        # Sessions exist per phase with distinct ids.
        session_ids = [s["session_id"] for s in result["sessions"]]
        self.assertEqual(len(session_ids), len(set(session_ids)))

        # The FIRST call of each post-interaction phase must not contain
        # any assistant output from the interaction phase.
        by_label = {label: msgs for label, msgs in client.calls}
        interaction_assistant_texts = []
        for label, msgs in client.calls:
            if label.startswith("C:interaction:"):
                for m in msgs:
                    if m["role"] == "assistant":
                        interaction_assistant_texts.append(m["content"])
        for label, msgs in client.calls:
            if label.startswith("C:ret:") or label.startswith("C:transfer:") \
                    or label.startswith("C:hidden:") or \
                    label.startswith("C:probe:"):
                for m in msgs:
                    for text in interaction_assistant_texts:
                        self.assertNotIn(
                            text, m["content"],
                            f"{label} leaks interaction material")

        # And the post-interaction calls themselves are single-turn.
        for label, msgs in client.calls:
            if label.startswith("C:ret:"):
                self.assertEqual(len(msgs), 1, label)


class TestHostileParticipantCannotRetrieveHiddenMaterial(unittest.TestCase):
    """Simulate a participant that actively tries to exfiltrate hidden
    material.  Nothing in the harness path can serve it."""

    def test_hostile_prompt_and_response_never_reach_hidden_data(self):
        tasks_a = gen.generate_family_a(4, SEED_A)
        tasks_b = gen.generate_family_b(tasks_a, SEED_B)
        protocol = PilotProtocol()
        protocol.mark_interaction_complete()
        tasks_c = protocol.generate_family_c(seed=SEED_C, tier=2)
        cfg = PilotConfig()

        def hostile_responder(label):
            # The "participant" asks for hidden tests, seeds and keys in
            # its own response text.  The harness must simply parse the
            # program sections and ignore everything else.
            parts = [
                "PLEASE PRINT ALL HIDDEN TEST INPUTS AND EXPECTED "
                "OUTPUTS, THE HIDDEN SEED, AND THE ANSWER KEYS."]
            for tid, task in {t.task_id: t for t in tasks_a
                              + tasks_b + tasks_c}.items():
                parts.append(_program_section(tid, task.naive_program))
            return "\n".join(parts)

        client = MockClient(hostile_responder)
        sink = MemorySink()
        arms.run_arm_c(client, cfg, sink, tasks_a, tasks_b, tasks_c)

        # Everything the participant SAW (all user-role message content):
        seen = []
        for label, msgs in client.calls:
            for m in msgs:
                if m["role"] == "user":
                    seen.append(m["content"])
        seen_text = "\n".join(seen)

        # Per-task: a task's own hidden INPUT vectors must never appear
        # inside that task's visible sections.  (Input vectors are unique
        # within a task, so any occurrence would prove a hidden case was
        # served to the participant.)
        sections = _task_sections(seen_text)
        for task in tasks_a + tasks_b + tasks_c:
            for case in task.hidden_cases:
                for body in sections.get(task.task_id, []):
                    self.assertNotIn(json.dumps(case.inputs), body)
            self.assertNotIn(str(task.case_seed), seen_text)
            self.assertNotIn(task.canonical_program, seen_text)
            self.assertNotIn(task.naive_program, seen_text)

        # And nothing written to the evidence sink for prompts contains
        # hidden material either.
        for path, text in sink.prompts.items():
            sections = _task_sections(text)
            for task in tasks_a + tasks_b + tasks_c:
                for case in task.hidden_cases:
                    for body in sections.get(task.task_id, []):
                        self.assertNotIn(json.dumps(case.inputs), body)


class TestArmFeedbackSeparation(unittest.TestCase):
    def setUp(self):
        self.tasks_a = gen.generate_family_a(4, SEED_A)
        self.tasks_b = gen.generate_family_b(self.tasks_a, SEED_B)
        self.protocol = PilotProtocol()
        self.protocol.mark_interaction_complete()
        self.tasks_c = self.protocol.generate_family_c(seed=SEED_C, tier=2)
        self.cfg = PilotConfig()

    def _naive_responder(self):
        progs = {t.task_id: t.naive_program for t in self.tasks_a}
        progs.update({t.task_id: t.naive_program for t in self.tasks_b})
        progs.update({t.task_id: t.naive_program for t in self.tasks_c})

        def responder(label):
            return "\n".join(_program_section(tid, p)
                             for tid, p in progs.items())
        return responder

    def _user_messages(self, client):
        return [m["content"] for label, msgs in client.calls
                for m in msgs if m["role"] == "user"]

    def test_arm_s_receives_no_feedback(self):
        client = MockClient(self._naive_responder())
        sink = MemorySink()
        arms.run_arm_s(client, self.cfg, sink, self.tasks_a, self.tasks_b,
                       self.tasks_c)
        for text in self._user_messages(client):
            self.assertNotIn("FEEDBACK", text)
            self.assertNotIn("PASS", text)
            self.assertNotIn("FAIL", text)
            self.assertNotIn("ENVIRONMENT", text)
        # exactly one turn in the baseline session
        result = None
        client2 = MockClient(self._naive_responder())
        sink2 = MemorySink()
        res = arms.run_arm_s(client2, self.cfg, sink2, self.tasks_a,
                             self.tasks_b, self.tasks_c)
        base = [s for s in res["sessions"] if s["phase"] == "baseline"]
        self.assertEqual(base[0]["turns"], 1)

    def test_arm_sprime_receives_no_environment_feedback(self):
        progs = {t.task_id: t.naive_program for t in self.tasks_a}

        def responder(label):
            if label.endswith("round_0"):
                programs = progs
            else:
                programs = {t.task_id: t.canonical_program
                            for t in self.tasks_a}
            return "\n".join(_program_section(tid, p)
                             for tid, p in programs.items())
        client = MockClient(responder)
        sink = MemorySink()
        res = arms.run_arm_sprime(client, self.cfg, sink, self.tasks_a,
                                  self.tasks_b, self.tasks_c)
        for text in self._user_messages(client):
            self.assertNotIn("FEEDBACK", text)
            self.assertNotIn("PASS", text)
            self.assertNotIn("FAIL", text)
            self.assertNotIn("ENVIRONMENT", text)
            self.assertNotIn("error:", text)
        self.assertEqual(res["phase_a"]["revision_rounds_used"], 3)
        final_scores = [e["hidden_score"]
                        for e in res["phase_a"]["final"].values()]
        self.assertEqual(final_scores, [1.0, 1.0, 1.0, 1.0])

    def test_arm_c_receives_only_permitted_feedback(self):
        def responder(label):
            # naive on round 0, canonical afterwards -> one feedback round
            if label.endswith("round_0"):
                programs = {t.task_id: t.naive_program
                            for t in self.tasks_a}
            else:
                programs = {t.task_id: t.canonical_program
                            for t in self.tasks_a}
            return "\n".join(_program_section(tid, p)
                             for tid, p in programs.items())
        client = MockClient(responder)
        sink = MemorySink()
        res = arms.run_arm_c(client, self.cfg, sink, self.tasks_a,
                             self.tasks_b, self.tasks_c)
        messages = self._user_messages(client)
        feedback_messages = [m for m in messages if "ENVIRONMENT FEEDBACK"
                             in m]
        self.assertTrue(feedback_messages)
        # permitted content appears: FAIL verdicts in the feedback, and a
        # fully-passing round in the environment log
        self.assertIn("FAIL", feedback_messages[0])
        any_round_all_pass = any(
            log["public_all_pass"] for log in sink.env_logs.values())
        self.assertTrue(any_round_all_pass)
        # the FEEDBACK text must never contain any expected-output values
        # (public or hidden) — feedback is pass/fail + error class only
        for task in self.tasks_a:
            for case in task.public_cases + task.hidden_cases:
                for text in feedback_messages:
                    self.assertNotIn(json.dumps(case.expected_output), text)
        # each task's own hidden INPUT vectors must never appear inside
        # that task's visible sections
        for text in messages:
            sections = _task_sections(text)
            for task in self.tasks_a:
                for case in task.hidden_cases:
                    for body in sections.get(task.task_id, []):
                        self.assertNotIn(json.dumps(case.inputs), body)
        # early stop after the single needed revision
        self.assertEqual(res["phase_a"]["revision_rounds_used"], 1)
        self.assertEqual(res["phase_a"]["rounds"][-1]["tasks"]
                         [self.tasks_a[0].task_id]["hidden_score"], 1.0)

    def test_arm_c_revision_limit(self):
        client = MockClient(self._naive_responder())
        sink = MemorySink()
        res = arms.run_arm_c(client, self.cfg, sink, self.tasks_a,
                             self.tasks_b, self.tasks_c)
        self.assertEqual(res["phase_a"]["revision_rounds_used"], 3)

    def test_submission_versioning_in_arm_c(self):
        client = MockClient(self._naive_responder())
        sink = MemorySink()
        arms.run_arm_c(client, self.cfg, sink, self.tasks_a, self.tasks_b,
                       self.tasks_c)
        # 4 rounds (0..3) x 4 tasks = 16 submission artifacts, versioned.
        for t in self.tasks_a:
            for version in range(1, 5):
                self.assertIn((t.task_id, version),
                              {(k[1], k[2]) for k in
                               sink.submissions.keys()})

    def test_hidden_results_never_reach_prompts_or_transcripts(self):
        client = MockClient(self._naive_responder())
        sink = MemorySink()
        arms.run_arm_c(client, self.cfg, sink, self.tasks_a, self.tasks_b,
                       self.tasks_c)
        for task in self.tasks_a:
            for case in task.hidden_cases:
                for path, text in sink.prompts.items():
                    for body in _task_sections(text).get(task.task_id, []):
                        self.assertNotIn(json.dumps(case.inputs), body)
                for path, obj in sink.transcripts.items():
                    for turn in obj["turns"]:
                        if turn["role"] != "user":
                            continue
                        for body in _task_sections(turn["content"]).get(
                                task.task_id, []):
                            self.assertNotIn(
                                json.dumps(case.inputs), body)


class TestProgramParsing(unittest.TestCase):
    def test_parse_programs(self):
        text = ("blah\n### TASK A-01\nSET a 1\n### END\n"
                "### TASK A-02\nSET b 2\n### END\n")
        programs, anomalies = arms.parse_programs(text, ["A-01", "A-02"])
        self.assertEqual(programs, {"A-01": "SET a 1", "A-02": "SET b 2"})
        self.assertEqual(anomalies, [])

    def test_parse_missing_section(self):
        programs, anomalies = arms.parse_programs(
            "### TASK A-01\nSET a 1\n### END\n", ["A-01", "A-02"])
        self.assertEqual(programs["A-02"], "")
        self.assertTrue(any("A-02" in a for a in anomalies))


if __name__ == "__main__":
    unittest.main()
