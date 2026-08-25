# SURVIVING CONFOUNDS

These confounds are not ruled out by the existing design. They are the reason
the intended CVI interpretation cannot be credited to this experiment as it
stands. Each is marked with its severity and whether it is TESTABLE with an
additional control.

---

## C0. Operator semantics and the trap are disclosed verbatim in the system prompt (highest severity)

**Confound:** `PARTICIPANT_SPEC` — the ordering-stable system prompt on **every**
call of **every** arm — documents the full semantics of every novel operator
(`ordermachine.py:637-735`) and *states the exact trap solution*: "`MIRROR a + 1`
means MIRROR of (a + 1). To add 1 after mirroring, write `(MIRROR a) + 1`"
(`:718-719`), and "no register is modified" (`:684`) — the entire purity-trap
rule. So the "hard" tasks are solvable by reading the spec (which the no-feedback
S arm did at transfer), not by causal inference from interaction. Arm C's
environmental verdict is mechanically irrelevant to acquiring a mapping already
present in every arm's prompt.

**Why it survives:** no phase hides the spec semantics; `arms.py:221-227`
injects it unconditionally.

**TESTABLE:** ablate the semantics/trap text (keep names/arity) and measure
whether the no-feedback arm's S0/S_tr collapses.

---

## C1. Causal contingency is confounded with "you are told you are wrong" (highest severity)

**Confound:** Arm C receives a verdict caused by its own program; no arm
receives a verdict *not* caused by its program. So one cannot tell whether a
possible C advantage comes from the *causal* link (my program ran and produced
failure) or merely from being given a multi-round "revise after being told
you're wrong" loop.

**Why it survives:** the current S' arm is a no-verdict control, not a
non-contingent-verdict control. `ce_sham_verdict_redundant.py` shows the
verdict text is a fixed string for the whole wrong-idiom class, so running the
participant's actual program adds nothing over a sham that replays the string.

**TESTABLE:** add a (given, non-contingent) sham arm.

---

## C2. S' is a damaged/inert control (high severity)

**Confound:** S''s three critique rounds are byte-identical no-ops, and its
correct baseline answer was not "destroyed by self-critique" but simply
re-drawn wrong in the fresh critique context and then frozen. S' therefore
does not measure healthy equal-budget private reasoning; it measures a loop
that breaks the right answer and cannot recover. This mechanically inflates
C > S'.

**Why it survives:** no project control makes S' a best-of-N or non-degrading
private-reasoning condition.

**TESTABLE:** compare S' multi-round vs S' one-shot vs S' best-of-N.

---

## C3. No-feedback derivability of the answers (high severity)

**Confound:** All Family-A (and thus Family-C) answers are derivable from the
public worked examples that appear verbatim in every arm's prompt. A no-feedback
solver reaches hidden_score 1.0 on all four Family-A tasks (`ce_no_feedback_
solve.py`), and S' already scored S0 = 1.00 with zero feedback. The verdict is a
non-load-bearing trigger, not the source of the solved mapping.

**Why it survives:** no control removes the public-example→answer derivability
or tests a no-feedback best-effort arm.

**TESTABLE:** score BOTH a no-feedback best-of-N arm and a non-contingent-verdict
sham arm against C.

---

## C4. Baseline matching is broken by response bimodality (high severity)

**Confound:** Arms are matched on a single one-shot S0, which is bimodal
(0.25 / 1.00 / 0.25 on identical prompts). The §18 premise of "approximately
equal static performance" is not satisfied.

**Why it survives:** no control averages S0 over draws or uses a seed-capable
endpoint; single-shot S0 remains the matching variable.

**TESTABLE:** multi-draw baseline averaging; reject unstable participants.

---

## C5. Transfer saturates to ceiling and is solvable by the no-feedback arm (high severity for S_tr)

**Confound:** S_tr = 1.00 for all arms in both pilots; S solves the S3 novel-
composition rungs with zero interaction. The primary transfer DV carries no
signal.

**Why it survives:** calibration used a 2-replicate mean rule that accepted the
unstable {1.0, 0.333} split; the official batch landed on the ceiling. No
control ensures S scores < 1.0 on transfer.

**TESTABLE:** re-calibrate Family B against the no-feedback arm to force
0.3-0.7 headroom.

---

## C6. Hidden verification Family C re-tests the same templates (high severity for S_ver)

**Confound:** Family C = Family A recipes/spec re-issued with fresh cases.
S_ver measures re-solving the same four templates, not generalised causal
structure. Observed S_ver = S0 = S_ret = 0.25 for all arms.

**Why it survives:** no control uses structurally distinct recipes for Family C.

**TESTABLE:** Family C from novel recipes.

---

## C7. Retention metric M is algebraically broken (medium severity)

**Confound:** M returns null for C's decisive no-retention case and a false
1.0 pass for a zero-learning arm. The design's own M >= 0.7 retention gate is
not meaningful.

**Why it survives:** the formula (`metrics.py:129-135`) is not corrected;
retention is only readable via raw per-task traces.

**TESTABLE:** per-task matched retention ratio.

---

## C8. Token parity is not actually implemented (medium severity)

**Confound:** "token-matched S'/C" is a design claim with no enforced cap; C's
interaction context and effective compute slightly exceed S'. Server prompt-
cache skews accounting.

**Why it survives:** no per-task token cap exists (`config.py` has only global
runaway guards).

**TESTABLE:** deterministic per-task token cap; log post-cache effective tokens.

---

## C9. Calibration selection is enumeration-order theater (medium severity)

**Confound:** family-level band accepts the first of 54 parameter-equivalent
specs (all predict 0.75 because difficulty is recipe-degenerate); it does not
predict per-recipe difficulty, and the same model calibrates and then runs.

**Why it survives:** selection rule 1.1 deliberately flags rather than rejects
out-of-band degenerate strata; predicted S0 (0.75) missed official S0.

**TESTABLE:** cross-validate selection on a held-out model; require per-recipe
band membership.

---

## C10. Treatment framing asymmetry (medium severity)

**Confound:** C is primed "your programs will be run / you will receive the
outcomes / you may revise"; S' is primed "private scratchpad / NO test results /
judge your own work." This could change emitted idiom and revision behaviour
independent of feedback.

**Why it survives:** the framing difference is inherent to the treatment and is
not separately controlled.

**TESTABLE:** neutralize wording; keep only the verdict/no-verdict difference.

---

## C11. "Fresh session" not verified against server prompt-cache reuse (low severity, TESTABLE)

**Confound:** server-side prompt caching (S baseline 820 vs 52 input tokens)
raises the possibility that nominal phase boundaries don't truly reset provider
context.

**Why it survives:** the client resets its own message list but has no control
over the provider cache; cache_read tokens are recorded but not analysed for
cross-phase leakage.

**TESTABLE:** inspect cache_read per phase; flag any phase-1 material served
into phase-2.

---

## C12. Fixed arm order + prompt-cache state (low severity, TESTABLE / UNRESOLVED)

**Confound:** arms run in the fixed order S → S' → C (`run_pilot.py:422-440`),
with no randomization, and the server-side prompt cache means S's baseline is
served cold (820 input tokens) while S'/C's are warm (52). The observed
0.25 / 1.00 / 0.25 baseline split could therefore be a positional/cache-state
artifact rather than model capability.

**Why it survives:** arm order is hard-coded; the report's own anomaly 6
documents the cache accounting asymmetry.

**TESTABLE:** randomize arm order across participants and/or force a cache-break
prefix per call; test whether the S0 spread persists.

---

## C13. Accountability/engagement prime is not isolated from verdict content (medium severity, TESTABLE)

**Confound:** C is framed "your programs will be run … you will receive the
outcomes"; S' is framed "private scratchpad … NO test results … judge your own
work." No arm receives C's *accountable/external-check* framing without a
verdict, so "being told there will be a check" (engagement) is bundled with
"receiving the actual verdict."

**Why it survives:** the framing difference is not independently varied.

**TESTABLE:** an arm with C's accountable wording but no verdict; or A/B the S'
heading.

---

## Cross-cutting verdict

Three confounds — **sham-verdict contingency (C1)**, **S' as a damaged control
(C2)**, and **no-feedback derivability (C3)** — jointly mean that a future
C > S' >= S on transfer and hidden verification could plausibly be produced by
a non-causal mechanism and is not currently distinguishable from them. Because
these are uncontrolled, the experiment as instrumented cannot justify the
intended CVI interpretation on its own. All are TESTABLE with the controls in
PROPOSED_CONTROLS.md.
