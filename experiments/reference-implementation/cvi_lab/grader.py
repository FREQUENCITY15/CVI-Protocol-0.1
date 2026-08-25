"""
Deterministic grader for OrderMachine task instances.

The grader has two strictly separated faces:

* PUBLIC face  — runs a program on a task's public examples and produces
  the ONLY feedback a participant may ever receive: per-case PASS/FAIL and
  the error class on failure.  Expected outputs are never included in
  feedback text.
* HIDDEN face  — runs a program on a task's hidden cases and returns the
  score.  Hidden results are visible only to the harness, never to the
  participant (no code path exposes them to participant-facing text).

All functions are pure and deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from . import ordermachine as om
from .generator import Task


@dataclass
class CaseResult:
    case_id: int
    passed: bool
    error_class: Optional[str] = None
    output: Optional[List[int]] = None
    # `output` is internal bookkeeping; it must never appear in feedback.

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _run_cases(task: Task, program: str, cases,
               vm: om.OrderMachine) -> List[CaseResult]:
    results: List[CaseResult] = []
    for case in cases:
        run = vm.run(program, case.inputs)
        passed = run.error is None and run.output == case.expected_output
        results.append(CaseResult(
            case_id=case.case_id,
            passed=passed,
            error_class=run.error.error_class if run.error else None,
            output=list(run.output)))
    return results


def run_public(task: Task, program: str,
               vm: Optional[om.OrderMachine] = None) -> List[CaseResult]:
    return _run_cases(task, program, task.public_cases, vm or om.OrderMachine())


def run_hidden(task: Task, program: str,
               vm: Optional[om.OrderMachine] = None) -> List[CaseResult]:
    """Hidden grading. Callers must never forward these results to the
    participant."""
    return _run_cases(task, program, task.hidden_cases, vm or om.OrderMachine())


def hidden_score(task: Task, program: str,
                 vm: Optional[om.OrderMachine] = None) -> float:
    """Fraction of hidden cases passed, in [0, 1]."""
    results = run_hidden(task, program, vm)
    if not results:
        return 0.0
    return sum(1 for r in results if r.passed) / len(results)


def public_all_pass(results: List[CaseResult]) -> bool:
    return bool(results) and all(r.passed for r in results)


def feedback_text(task_id: str, results: List[CaseResult]) -> str:
    """Build the ONLY permitted feedback string for public-case results.

    Contains: task id, case ids, PASS/FAIL, and error class on failure.
    Contains NOT: expected outputs, input values beyond the case id,
    hidden-test material, or grader internals.
    """
    parts = [f"{task_id}:"]
    for r in results:
        if r.passed:
            parts.append(f"case {r.case_id}: PASS")
        elif r.error_class:
            parts.append(f"case {r.case_id}: FAIL (error: {r.error_class})")
        else:
            parts.append(f"case {r.case_id}: FAIL (wrong output)")
    return " | ".join(parts)


def feedback_block(task_id: str, results: List[CaseResult]) -> str:
    """Multi-line feedback used in Arm C environment messages."""
    lines = [f"{task_id}:"]
    for r in results:
        if r.passed:
            lines.append(f"  case {r.case_id}: PASS")
        elif r.error_class:
            lines.append(f"  case {r.case_id}: FAIL (error: {r.error_class})")
        else:
            lines.append(f"  case {r.case_id}: FAIL (wrong output)")
    return "\n".join(lines)
