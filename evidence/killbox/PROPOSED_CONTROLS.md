# PROPOSED CONTROLS

These are the minimal additional controls/experiments that would let the CVI
experiment actually distinguish the intended causal-learning interpretation from
the surviving confounds. **No existing experimental code is modified here;**
these are proposals for a next design iteration.

---

## Control 1 — Non-contingent-verdict sham arm (decisive for C1, C3)

**Problem:** "causal contingency" is confounded with "being told you're wrong."

**Proposal:** add a 4th arm, **S'' (sham-verdict)**, that is byte-for-byte
identical to C's interaction loop (same task round-0 prompt, same R=3 revision
rounds, same number of "ENVIRONMENT FEEDBACK … case N: PASS/FAIL" blocks, same
"revise your failing programs" instruction) **except** the PASS/FAIL verdict is
generated from a *reference* program (e.g., the task's naive misparse), not from
the participant's own submitted program. This severs the causal link while
matching tokens, rounds, and verdict text exactly.

**Interpretation rule:**
- If C ≈ S'' on S_tr/S_ver: the verdict *content*, not its contingency, drives any C advantage → causal contingency adds nothing → CVI's causal claim fails.
- If C > S'' on S_tr/S_ver: contingency matters → supports the CVI claim.

**Minimality:** single new arm reusing the existing C interaction machinery with
a swapped feedback source.

---

## Control 2 — S' of equal but NON-degrading effort (decisive for C2)

**Problem:** S' as implemented is inert and can degrade/freeze a correct answer,
so C > S' is a control artifact.

**Proposal:** add two sub-conditions to the private-reasoning arm:
- (a) **S' one-shot**: generate each task's program once, no critique loop.
- (b) **S' best-of-N**: generate N independent candidate programs per task (no
feedback) and let the harness keep the one maximizing public-example agreement
(scored only as an analysis, not shown to the model).

Compare the current multi-round S' against (a) and (b). If C only beats the
current S', the advantage reflects S''s handicapping, not causal learning.

---

## Control 3 — Stable baseline matching (decisive for C4)

**Problem:** single-shot S0 is bimodal; arms are not actually matched.

**Proposal:** before forming strata, average S0 over ≥3 independent one-shot
draws per participant (or use a seed-capable endpoint with a pinned seed);
exclude participants whose S0 is unstable (spread > 0.5). Report the stratum so
any residual C > S' is only within well-matched cells.

---

## Control 4 — Transfer headroom against the no-feedback arm (decisive for C5)

**Problem:** S_tr = 1.00 ceiling; a no-feedback arm already solves the transfer
rungs.

**Proposal:** calibrate Family B so that the **no-feedback arm S** scores in
[0.30, 0.70] before comparing arms, using a *replicate* rule robust to batch
variance (e.g., accept only if the worst replicate is below 0.85, not the mean).
This guarantees S_tr has headroom to measure a treatment effect.

---

## Control 5 — Structurally novel hidden verification (decisive for C6)

**Problem:** Family C re-uses Family-A recipes/templates, so S_ver re-tests
memorised templates.

**Proposal:** generate Family C from recipes/operators **not** present in
Family A (structurally distinct compositions), keys independently hidden, so
S_ver tests generalised causal structure rather than template re-application.
Even better, require C to transfer to an S4-domain re-skin (different modality,
same underlying pattern).

---

## Control 6 — Corrected retention metric (decisive for C7)

**Problem:** M is null/log broken.

**Proposal:** report per-task retention as the difference in matched hidden-score
`S_ret - S0` per task (well-defined for every arm including C), plus the
design's continuous M alongside; do not gate on a single scalar M when it is
undefined.

---

## Control 7 — Enforced token parity (decisive for C8)

**Proposal:** impose a hard per-task, per-round token budget on C and S' (and
S''), log *post-cache* effective tokens, and only claim compute-parity if
post-cache tokens per task are within a tolerance.

---

## Control 8 — Calibration cross-validation and per-recipe difficulty (decisive for C9)

**Proposal:** require every selected recipe's calibration stratum to be
individually in band (not the family average); select tasks on a held-out model
(or a human difficulty rating) and score on the experiment model; report the
flagged-degenerate strata as a hard exclusion, not a pass.

---

## Control 9 — Neutral treatment framing (decisive for C10)

**Proposal:** give C and S' the *same* task-round wording except for the actual
presence/absence of the verdict ("You will see the results of running your
programs on the worked examples" present for C/S'', absent for S'); remove the
"private scratchpad / no test results / judge your own work" self-doubt primes.

---

## Control 10 — Prompt-cache audit (decisive for C11)

**Proposal:** record `cache_read_input_tokens` per phase; flag any phase-boundary
leak (phase-1 content served into phase-2 cache); enforce a provider-side
`cache_control`/fresh-context where the endpoint supports it.

---

## Suggested smallest decisive experiment

If budget allows only one addition, add the **non-contingent-verdict sham arm
(S'')** (Control 1) and use **best-of-N S'** (Control 2) as the private-reasoning
control. This single pair isolates, respectively, the *contingency* dimension and
the *private-effort* dimension — the two things the current design conflates —
and directly answers whether causal contingency (running *your* program and
seeing *its* verdict) transfers beyond what equal private effort / equal verdict
text can do.
