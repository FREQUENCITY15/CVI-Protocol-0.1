# STRONGEST ATTACKS — surviving alternative explanations

These are the attacks that survive the defence stage and would, if they hold,
force the intended CVI interpretation to be abandoned for this experiment.
They are ordered by combined damage: (ability to reproduce the predicted
pattern) x (grounding in the implementation) x (how hard they are to
discriminate).

---

## 0. The solution structure is disclosed verbatim in every arm's system prompt

**ATTACK.** The OrderMachine spec — the `PARTICIPANT_SPEC` string served as the
system prompt on *every* participant call of *every* arm — documents the full
semantics of every novel operator **and states the exact answer structure for
the hardest trap**: "`MIRROR a + 1` means MIRROR of (a + 1). To add 1 after
mirroring, write `(MIRROR a) + 1`" (`ordermachine.py:718-719`), and "no register
is modified" (`:684`). The canonical program for the flagship impossible-for-this-
model task (A-02/C-02) is literally `OUT (MIRROR a) + 2`. So the "repair" tasks
measure spec comprehension / instruction-following, not causal inference, and
Arm C's interaction is mechanically irrelevant to acquiring the mapping.

**EVIDENCE (OBSERVED).** `ordermachine.py:637-735`; `arms.py:221-227`
(unconditional injection); `submissions/S/B-*.om` show the no-feedback S arm
writing the exact canonical programs at transfer from the spec alone.

**COUNTEREXAMPLE.** A no-feedback arm (S) already scores S_tr = 1.0 by reading
the disclosed spec. The tasks cannot detect causal learning because the answer
is present in every arm's prompt.

**PREDICTION.** Ablating the semantics/trap text from the spec (keeping only
names/arity) collapses the no-feedback arm's S0/S_tr toward chance; without
ablation, S_tr stays at ceiling for all arms regardless of treatment.

**DISCRIMINATING TEST.** Two-arm ablation (spec-with-semantics-no-examples vs
examples-no-semantics); whichever dominates hidden cases tells whether these
tasks measure instruction-following (Arm C irrelevant) or data-driven inference.

**CLASSIFICATION: SURVIVES.**

---

## 1. The causal contingency is confounded with "you are told you are wrong" (sham-verdict gap)

**ATTACK.** Arm C receives a *causally contingent* verdict: the environment
executes the agent's **own** program and returns PASS/FAIL — and this is the
program's only informational advantage over Arm S'. The experiment has **no arm
that receives a verdict without that verdict being caused by the participant's
own program**. So "verdict provided" and "verdict caused by my program" are
perfectly confounded. If interaction *per se* (being told repeatedly that your
output is wrong, in a multi-round revision loop) is beneficial — regardless of
whether the program actually ran — the design would produce C > S' with no
causal-learning mechanism at play.

**EVIDENCE (OBSERVED).**
- `arms.py:464-546` (run_arm_c_pre) executes the agent's own program; `arms.py:384-448` (run_arm_sprime_pre) gives S' no verdict at all.
- `COUNTEREXAMPLES/ce_sham_verdict_redundant.py` (runnable) proves that for every wrong-idiom program the model actually emits, the verdict string is identical — `FAIL (wrong output)` on all 4 public cases. So the verdict is a *fixed string* over the whole class of wrong programs: running "this specific program" contributes zero extra information beyond "it is wrong".
- `environment_logs/C/A-01/round_00.json`: all four failures have `error_class: null` → the promised per-case "error class" channel delivered no discrimination (all failures are plain "wrong output").

**COUNTEREXAMPLE.** A sham arm that replays the byte-identical
"ENVIRONMENT FEEDBACK … case N: FAIL (wrong output) … Round r/3: revise your
failing programs" strings **without executing the participant's program** is
informationally indistinguishable to the participant and reproduces the same
in-session correction and the same cross-context reversion. This sham has the
same tokens, the same number of revision rounds, and the same verdict text as
C — only the causal link to the participant's own program is severed.

**PREDICTION.** The non-contingent sham reproduces C's S_post and S_ret on
these tasks.

**DISCRIMINATING TEST.** A 2×2 factorial: verdict (given / withheld) ×
contingency (verdict caused by the participant's own program / verdict
generated independently, e.g., from a reference program). The current design
only occupies (given, contingent) and (withheld, n/a); the (given, non-
contingent) cell is the missing sham that separates causal contingency from
"being told you're wrong."

**CLASSIFICATION: SURVIVES.** No project evidence defeats it; the current S'
arm supplies a no-verdict control, not a non-contingent-verdict control.

---

## 2. S' is a damaged and inert control, not equal-budget private reasoning

**ATTACK.** The comparison "C > S'" is meant to show causal feedback beats
equal-effort private reasoning. But S' as implemented is (a) *inert* — its
three self-critique rounds emit byte-identical text and change nothing — and
(b) *actively degrading* — its baseline produced the correct program, then the
fresh critique-round re-drew the *wrong* value-discard idiom and froze there.
So S' does not measure "private reasoning at equal budget"; it measures "a
no-verdict critique loop that breaks the right answer and cannot recover
it." Any C > S' on S_post is trivially explained by S''s incapacitation.

**EVIDENCE (OBSERVED).**
- S' baseline A-01 = correct `SET c SWIZZLE a b / MUL c 2 / OUT c` (hidden 1.0); critique round-0 = wrong `(SWIZZLE a b) * 2 / OUT a`; rounds 1-3 emitted byte-identical text (`transcripts/S_PRIME/critique/*`). The "regression" happens **before any critique round** — it is a fresh-context re-draw of a bimodal sampler, not destructive self-effort.
- `metrics.py` reports G_F(S') = 0.0 (the `max(0,..)` clamp hides the −0.75 regression), making S' look like a mere non-improver rather than a damaged control.
- The report's own claim "self-critique destroyed correct answers" (`CVI_0_1_Pilot_Report.md:296`) misattributes a fresh bimodal draw; the critique rounds changed nothing.

**COUNTEREXAMPLE.** S' would lose to C even if C's interaction were inert and C simply left its correct baseline idiom unchanged; S' is structurally handicapped to a *lower* S_post. A future C > S' pattern therefore cannot be attributed to causal learning without separately establishing that S' actually represents healthy private reasoning.

**PREDICTION.** An S' variant asked for a single best one-shot attempt per task (no "judge your own work" loop) scores ≥ the current S'.

**DISCRIMINATING TEST.** Compare the current multi-round S' against (i) a one-shot S' (no critique loop) and (ii) an S' that produces N independent attempts and keeps the best (best-of-N private effort). If C only beats the current S', the advantage is a control artifact.

**CLASSIFICATION: SURVIVES.** This actively *inflates* C > S' and must be re-controlled for the comparison to interpret.

---

## 3. No-feedback derivability: the Family-A (and Family-C) answers are in every arm's shared prompt

**ATTACK.** The "repair" tasks are solvable *ab initio* from the public
worked examples that are injected verbatim into **every** arm's prompt
(S, S', C alike). A no-feedback solver reaches hidden_score = 1.0 on all four
Family-A tasks (and, since Family C re-uses the same recipes, on Family C).
The environmental verdict is therefore not the source of the solved mapping —
it is merely a trigger that tells C its own program is wrong.

**EVIDENCE (OBSERVED).**
- `arms.py:88-101` injects `task.public_view()` (description + 4 public input→output pairs) into every arm's every phase prompt.
- `COUNTEREXAMPLES/ce_no_feedback_solve.py` (runnable) shows `OUT (SWIZZLE a b) * 2` etc. pass all public+hidden cases (hidden_score 1.0) for A-01..A-04.
- S', with zero feedback and zero execution, scored S0 = 1.00 at baseline — already solving every task from the examples+spec alone (the hidden-verifier investigator's "decisive counterexample").

**COUNTEREXAMPLE.** Replace C's interaction with nothing; a no-feedback arm that emits the canonical parenthesized idiom scores hidden = 1.0 on the whole Family A, *beating* the observed C (0.75). Any between-arm difference on the interaction leg reflects idiom-choice, not causal learning.

**PREDICTION.** A sham S'' (prompt content + R=3 best-effort attempts, never executed) matches or exceeds C's interaction score.

**DISCRIMINATING TEST.** Score an arm that receives the same prompt and revision opportunities but is never told which cases fail (already S'), AND separately score a no-feedback best-of-N arm; compare all against C.

**CLASSIFICATION: SURVIVES.**

---

## 4. Baseline matching is broken, so the §18 premise ("approximately equal static performance") is not established

**ATTACK.** CVI's falsifiable prediction requires two agents/configurations
with *approximately equal static performance*. The experiment matches arms on
a single Phase-0 one-shot baseline S0. For this model the baseline is
bimodal: S0 measured 0.25 / 1.00 / 0.25 across S / S' / C on byte-identical,
hash-enforced prompts. The arms are not matched at all; the "matching
variable" carries only which bimodal idiom the session happened to emit.

**EVIDENCE (OBSERVED).**
- S0 = 0.25 (S), 1.00 (S'), 0.25 (C) on identical prompts (report §4; §9 anomaly 1).
- CVI-0 calibration drew 0.25 / 0.75 / 1.00 across fresh draws of the same tier (§6).

**COUNTEREXAMPLE / PREDICTION.** Repeated baseline draws under identical
prompts yield a bimodal {0.25, 1.00}, not a stable match. Any subsequent
C > S' on transfer/hidden could be the artefactual consequence of which idiom
each treatment session tends to elicit, not of durable learning.

**DISCRIMINATING TEST.** Average S0 over several independent one-shot draws
per participant (or use a seed-capable endpoint) before forming matching
strata; reject any participant whose S0 is not stable.

**CLASSIFICATION: SURVIVES.**

---

## 5. Retention metric M is algebraically broken and can yield a false pass

**ATTACK.** The design's retention gate "M ≥ 0.7" is computed by a formula
that returns `null` precisely when C's no-retention case arises, returns a
false `1.0` for a zero-learning arm, and returns `-2.0` for S'. The gate is
not a valid measure of whether corrections survive the context boundary.

**EVIDENCE (OBSERVED).**
- `metrics.py:129-135` computes `1 - (S0 - S_ret)/(S0 - F_after)` with `F_after = 1 - S_post`, i.e. `1 - (S0 - S_ret)/(S0 + S_post - 1)`.
- M(C) = null in the pilot (denominator 0); M(S') = -2.0; an arm with S0 = S_post = S_ret yields M = 1.0 (a false pass). C's decisive "did not retain" case is unmeasurable, while S' gets a defined (if pathological) value.

**COUNTEREXAMPLE.** An arm that learns nothing (baseline==post==ret) is scored M = 1.0, falsely satisfying the design's own M ≥ 0.7 retention criterion.

**DISCRIMINATING TEST.** Replace M with a per-task, matched-instance retention ratio and force it to be reported for C even when S0 - F_after = 0.

**CLASSIFICATION: SURVIVES.**

---

## 6. Hidden verification Family C re-tests the same recipes/templates as Family A

**ATTACK.** The "independent hidden verification" leg re-issues Family A
(same four recipes, same calibrated spec, same purity traps) with fresh random
cases. So S_ver measures "re-solve these four templates," not "succeed without
the material that produced the original correction." Combined with the
observed S_ver = S0 = S_ret = 0.25 (every arm emitted the same wrong idiom at
all three phases), S_ver offers no independent check of generalised causal
structure.

**EVIDENCE (OBSERVED).**
- `generator.py:874-883` Family C = `generate_family_a(..., spec=spec)`; `run_pilot.py:468` passes the *same* calibrated spec as Family A.
- `family_c.json` descriptions/canonical programs byte-identical to `family_a.json`; C-02 has the identical `purity_trap: true`.

**PREDICTION.** S_ver tracks Family-A idiom choice, equals S0, and cannot rise above the two template idioms regardless of what C learned.

**DISCRIMINATING TEST.** Generate Family C from structurally different recipes (novel operators not in Family A) with independently hidden keys; require C to transfer there.

**CLASSIFICATION: SURVIVES.**

---

## Summary of strength

The three attacks that most directly threaten the CVI interpretation are
**(1) the sham-verdict / contingency confound**, **(2) S' as a damaged control**,
and **(3) no-feedback derivability**. Together they mean: even a *clean*
C > S' >= S on transfer and hidden verification in a future run would likely be
reproducible by a non-causal arm, so the current design cannot justify the
intended causal-learning interpretation on its own.
