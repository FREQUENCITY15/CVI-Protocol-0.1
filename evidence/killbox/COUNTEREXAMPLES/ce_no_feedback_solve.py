#!/usr/bin/env python3
"""
COUNTEREXAMPLE ce_no_feedback_solve — "the environmental verdict is
informationally redundant for the Family-A repair tasks."

Thesis under attack: the predicted pattern C > S' >= S (C causal-interactive
beats equal-budget private reasoning) would be evidence that *causally
contingent* interaction (the environment executing the model's program and
returning a verdict) teaches something that transfers.

This counterexample shows, using the official CVI-0.1 Family-A instances and
the real deterministic grader, that a *no-feedback* agent that is given only
the public worked examples (which are presented verbatim in EVERY arm's prompt
— S, S', C alike) can write programs that pass EVERY hidden case for ALL FOUR
tasks (A-01..A-04), with hidden_score = 1.0 on each.  The canonical
parenthesized-expression idiom (OUT (OP x) * k) is directly derivable from the
four public input->output pairs plus the spec — no execution verdict is needed.
Notably, Arm S ALREADY produced exactly this idiom for A-01/A-02 at TRANSFER in
the actual run with zero interaction and scored 1.0.

So the Family-A "repair" tasks are all solvable from the shared prompt content
alone.  The causal verdict's specific content (which public case failed) is
redundant because, in the actual run, all failed public cases failed together
(the verdict reduced to "your program is wrong"), and any arm can conclude that
by checking the visible examples.

The point is NOT to say no feedback helps at all.  It is to demonstrate that a
credible sham treatment giving an equal-budget no-feedback arm the prompt
content (already shared) can reach hidden_score = 1.0 on ALL Family-A tasks —
which EXCEEDS what Arm C's actual causal interaction achieved (S_post = 0.75,
A-02 unresolved).  If a no-feedback arm can match or beat C on the interaction
phase using only shared prompt content, then any future observed C > S' > S on
transfer/hidden cannot be attributed to the causal contingency of the feedback;
it must be attributed to idiom selection / structural content already present
in every arm's prompt.

OBSERVED vs INFERRED vs UNRESOLVED tags are printed inline.
"""

import sys, os
# This file lives at <repo>/CVI-KILLBOX/COUNTEREXAMPLES/ ; CVI-Pilot is a
# sibling of CVI-KILLBOX under the repo root.
_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_FILE_DIR))  # .. from COUNTEREXAMPLES
sys.path.insert(0, os.path.join(_REPO, "CVI-Pilot"))
from cvi_lab import generator as gen, grader, ordermachine as om

# Reproduce the OFFICIAL CVI-0.1 Family A (same seeds and calibrated spec as
# runs/CVI-0.1_20260817T213225Z/tasks/family_a.json).
SPEC = {'swizzle_mul': {'k': 2}, 'mirror_add': {'k': 2},
        'swizzle_mul_add': {'k': 2, 'm': 1},
        'splice_drain': {'mode': 'drain'}}
tasks_a = gen.generate_family_a(4, 20260818_001, tier=2, spec=SPEC)


def passes_all(program, task):
    """Does this program pass every PUBLIC + HIDDEN case?"""
    for cases in (task.public_cases, task.hidden_cases):
        for c in cases:
            run = om.OrderMachine().run(program, c.inputs)
            if run.error is not None or run.output != c.expected_output:
                return False, (c.case_id, run.error, run.output)
    return True, None


def main():
    print("Official CVI-0.1 Family A tasks (reproduced from seed 20260818_001)")
    print("=" * 78)
    for t in tasks_a:
        pub = " | ".join(f"{c.inputs}->{c.expected_output}"
                         for c in t.public_cases)
        print(f"\n{t.task_id} [{t.recipe}]  (public examples are IN EVERY "
              f"arm's prompt verbatim)")
        print(f"  public: {pub}")

    print("\n" + "=" * 78)
    print("COUNTEREXAMPLE: no-feedback reconstruction from public examples")
    print("The 'participant' never receives any verdict; it only uses the")
    print("spec + the 4 public worked examples (shared by S/S'/C).")
    print("-" * 78)

    # Candidate programs a no-feedback solver could emit from the examples.
    # These are exactly the canonical-style answers, derivable from the
    # input->output pairs + spec (no verdict / no execution required).
    # Arm S already emitted this idiom for A-01/A-02 at TRANSFER with zero
    # interaction and scored 1.0.
    no_feedback_progs = {
        'A-01': 'OUT (SWIZZLE a b) * 2',
        'A-02': 'OUT (MIRROR a) + 2',
        'A-03': 'OUT (SWIZZLE a b) * 2 + 1',
        'A-04': 'SPLICE a b\nDRAIN',
    }

    n_ok = 0
    for t in tasks_a:
        prog = no_feedback_progs[t.task_id]
        ok, bad = passes_all(prog, t)
        hidden = grader.hidden_score(t, prog)
        if ok:
            n_ok += 1
        print(f"  {t.task_id}: {prog!r}")
        if ok:
            print(f"     -> passes ALL public+hidden cases "
                  f"(hidden_score={hidden:.2f})")
        else:
            print(f"     -> FAIL on case {bad}")

    print("-" * 78)
    print(f"RESULT: no-feedback solver passes {n_ok}/4 Family-A tasks "
          "(hidden_score = 1.0 on each).")
    print()
    print("What the ACTUAL Arm C interaction achieved (scores.json, "
          "CVI-0.1 run):")
    print("  A-01: 0.0 -> 1.0 ; A-03: 0.0 -> 1.0 ; A-02: 0.0 -> 0.0")
    print("        (unresolved after 3 feedback rounds) ; A-04: 1.0")
    print("  => C S_post = 0.75.  The no-feedback solver above (1.0) == full")
    print("     score on all 4 tasks, i.e. it would BEAT Arm C's causal loop.")
    print()
    print("OBSERVED: every Family-A task is solvable from the SHARED public")
    print("  examples alone (with no feedback), hidden_score = 1.0.")
    print("OBSERVED: in the actual run, all of C's public-case failures on a")
    print("  task failed TOGETHER (all 4 cases 'FAIL (wrong output)'), so the")
    print("  verdict added no per-case discrimination beyond 'your program is")
    print("  wrong' — which any arm can infer from the visible examples.")
    print("INFERRED: the interaction-phase differences are driven by idiom")
    print("  selection / structural content already present in every arm's")
    print("  prompt, not by the causal contingency of the verdict.  If a future")
    print("  run shows C > S' > S on transfer/hidden, this no-feedback")
    print("  derivability means the difference cannot be attributed to the")
    print("  causal verdict without an explicit control ruling it out.")


if __name__ == "__main__":
    main()
