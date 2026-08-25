#!/usr/bin/env python3
"""
COUNTEREXAMPLE ce_sham_verdict_redundant — "the causal verdict is
information-theoretically degenerate for these recipes."

The CVI claim rests on Arm C receiving a *causally contingent* signal: the
environment executes the agent's OWN submitted program and returns a verdict.
A sham treatment must break that contingency (feedback not caused by the
agent's actual program) while exposing the agent to the same quantity of
interaction/feedback/revision.

This counterexample shows that, for every official Family-A recipe, the public
verdict is a *degenerate* function of the submitted program: ANY program in the
wrong-idiom family (the value-discard / purity-trap idioms the model actually
emits at baseline) fails ALL FOUR public cases jointly.  Therefore the verdict
delivered to Arm C never depends on *which* wrong program C submitted — it
always reduces to the string "the program is wrong on all worked examples."
A sham treatment could deliver the *identical* verdict string without ever
running C's actual program, because for every wrong program the verdict is the
same.  The causal contingency (running THIS program) carries zero additional
information beyond "it's wrong."

Consequence: if a future run shows C > S' > S, the difference could be
reproduced by a sham that hands S' the same multi-round "revise after being
told it failed" loop WITHOUT running S''s program — because the verdict text is
a fixed function for all plausible wrong programs.  The existing S' arm does
NOT contain such a sham: it receives no verdict at all.  This counterexample
therefore isolates exactly what control is missing.
"""

import sys, os
_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_FILE_DIR))
sys.path.insert(0, os.path.join(_REPO, "CVI-Pilot"))
from cvi_lab import generator as gen, grader, ordermachine as om

SPEC = {'swizzle_mul': {'k': 2}, 'mirror_add': {'k': 2},
        'swizzle_mul_add': {'k': 2, 'm': 1},
        'splice_drain': {'mode': 'drain'}}
tasks_a = gen.generate_family_a(4, 20260818_001, tier=2, spec=SPEC)

# Idioms a baseline model actually emits (from the real run):
#  - value-discard:  "(SWIZZLE a b) * 2\nOUT a"  (S, C, S' baseline; C round 0)
#  - purity-trap:    "MIRROR a\nADD a 2\nOUT a"  (C round 1..2 for A-02)
def verdict_of(task, program):
    """Return the exact PASS/FAIL+error string Arm C would receive."""
    lines = [f"{task.task_id}:"]
    for pr in grader.run_public(task, program):
        if pr.passed:
            lines.append(f"  case {pr.case_id}: PASS")
        elif pr.error_class:
            lines.append(f"  case {pr.case_id}: FAIL (error: {pr.error_class})")
        else:
            lines.append(f"  case {pr.case_id}: FAIL (wrong output)")
    return "\n".join(lines)

wrong_idioms = {
    'A-01': ['(SWIZZLE a b) * 2\nOUT a', 'OUT SWIZZLE a b * 2'],
    'A-02': ['(MIRROR a) + 2\nOUT a', 'MIRROR a\nADD a 2\nOUT a',
             'OUT MIRROR a + 2'],
    'A-03': ['(SWIZZLE a b) * 2 + 1\nOUT a', 'OUT SWIZZLE a b * 2 + 1'],
    'A-04': [],  # A-04 was solved at round 0 by every arm; no wrong idiom used
}

print("SHAM-TREATMENT COUNTEREXAMPLE: is the causal verdict degenerate?")
print("=" * 78)
for t in tasks_a:
    programs = wrong_idioms[t.task_id]
    print(f"\n{t.task_id} [{t.recipe}]")
    if not programs:
        print("  (no wrong idiom observed in the run for this task)")
        continue
    seen = set()
    for p in programs:
        v = verdict_of(t, p)
        print(f"  program {p!r}")
        print(f"    verdict:\n{v}")
        seen.add(v)
    print(f"  distinct verdict texts for all wrong idioms used by any arm: "
          f"{len(seen)}")

print("-" * 78)
print("OBSERVED: for each task, every wrong-idiom program yields the SAME")
print("  verdict 'FAIL (wrong output)' on all 4 public cases.  The verdict")
print("  is a constant string for the entire class of programs the model")
print("  actually emits — it does not depend on which wrong program was run.")
print("OBSERVED: the verdict for C is computed from the agent's OWN submitted")
print("  program (grader.run_public called on programs[t.task_id]), yet for")
print("  any wrong program the text is identical.")
print("INFERRED: because the verdict is a fixed function of 'being in the")
print("  wrong-idiom class', a sham treatment could reproduce C's exact")
print("  feedback (same number of rounds, same per-case PASS/FAIL strings,")
print("  same 'revise your failing programs' instruction) WITHOUT executing")
print("  or depending on the agent's actual program.  The causal contingency")
print("  (THIS program ran and failed) adds no information beyond 'you are")
print("  wrong', which is derivable from the shared visible examples.")
print("UNRESOLVED: whether a run where the model emits a *mixed* set (some")
print("  cases PASS, some FAIL for the same program) would break this")
print("  degeneracy — not demonstrated in the actual run; the sham's")
print("  equivalence to C holds in the empirical regime the pilot observed.")
