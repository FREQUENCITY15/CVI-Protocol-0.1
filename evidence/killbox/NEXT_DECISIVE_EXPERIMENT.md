# NEXT DECISIVE EXPERIMENT

A single experiment (in two arms) that would empirically separate the intended
CVI claim — *durable, generalising capability produced by CAUSALLY CONTINGENT
interaction* — from the surviving alternative explanations.

---

## Question it must answer

Does **causally contingent** feedback (the environment runs *the participant's
own program* and returns *its* verdict) produce durable, generalising gains
**over and above**:
(i) the same verdict *content* delivered without the causal link (sham), and
(ii) equal-budget private reasoning that does not degrade the participant (the
damaged-control problem)?

---

## Design (two new arms, everything else unchanged)

Keep the existing OrderMachine, generator, grader, protocol gate, and prompt
identity machinery exactly as they are. Add **two** arms and one analysis rule:

**Arm S'' — non-contingent verdict (sham).**
Byte-for-byte identical to Arm C's interaction loop: same round-0 task prompt,
same R=3 revision rounds, same "ENVIRONMENT FEEDBACK … case N: PASS/FAIL (wrong
output|error) … revise your failing programs" strings, same per-task public
cases. The ONLY difference: the PASS/FAIL verdict is computed by running a fixed
**reference** program (the task's naive misparse) on the public cases, **not**
the participant's own submitted program. Thus S'' receives the same verdict text
and the same quantity of interaction/feedback/revision as C, but the verdict is
not caused by S''.'s submissions. Lock the reference program's verdicts into a
constant tape so they are phase-identical and reproducible.

**Arm S'★ — best-of-N private reasoning (healthy control).**
For each Family-A task, prompt the participant to produce N ≥ 3 independent
candidate programs (no feedback, no shared context between candidates — separate
session per candidate). Score all N offline; the analysis uses the best public-
agreement candidate (never shown back to the model). This is the "private
reasoning at equal candidate-budget, non-degrading" control that the fragile
multi-round S' was meant to be.

**Analysis rule.**
Compare the *primary* DVs — S_tr (transfer) and S_ver (hidden verification) —
across C, S'', S'★, S. Use the design's pair-blocked permutation tests.

---

## Interpretation

| Observed pattern (primary DVs) | What it says |
|---|---|
| C > S'' and C > S'★ | Causally contingent feedback adds durable, generalising value not reproducible by the same verdict text nor by best-of-N private effort → supports the CVI claim. |
| C ≈ S'' > S'★ | The verdict *content* (not contamination or contingency) explains C; causal contingency adds nothing → causal claim fails. |
| C ≈ S'★ | Private effort alone reproduces C → causal claim fails. |
| C > S'', C > S'★, but S_ret ≈ S0 or S_tr = S_ver (ceiling / no headroom) | Correction is in-context patchwork, not durable learning → strict CVI claim fails (design's own criterion #2). |

---

## Why this is decisive against the three strongest attacks

- **Against the sham/contingency confound (C1):** the C vs S'' contrast directly
  isolates the contingency dimension.
- **Against the damaged-control problem (C2):** the best-of-N S'★ provides a
  non-degrading equal-effort control.
- **Against no-feedback derivability (C3):** S'★ (best-of-N with no verdict) and
  S (no-feedback) bound the "the answer is already in the prompt" channel; if S'★
  already solves the tasks from the shared examples, then C > S'' > S'★ is
  required before any causal claim.
- **Against ceiling / memorised hidden verification (C5/C6):** re-run Family C
  and Family B with genuinely novel structure (Control 5) so S_tr/S_ver have
  headroom and S_ver is an independent verification gate.

---

## Minimal footprint

- Two new arms reusing the existing arms.C machinery.
- One hard-coded verdict tape (reference-program public PASS/FAIL) for S''.
- One best-of-N scoring branch for S'★.
- The existing 117-test harness, protocol gate, firewall, and prompt-identity
  checks are unchanged and re-asserted.

This is the smallest experimental intervention that would let a future run's
**C > S' ≥ S** result be credited to causally contingent learning rather than
to the surviving confounds in this KILLBOX.
