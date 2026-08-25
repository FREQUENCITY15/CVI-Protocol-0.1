# CVI-0.1 Pilot Report

**Run id:** `CVI-0.1_20260817T213225Z`
**Calibration packages:** `CVI-0.1_calibration_20260817T212849Z` (baseline,
sealed), `CVI-0.1_calibration_20260817T213158Z` (rule 1.1 re-selection +
transfer, sealed; pointer: `runs/CVI-0.1_calibration_selection.json`)
**Generated:** 2026-08-17T21:5xZ (written after all raw evidence was on disk)
**Laboratory:** `CVI-Pilot/` (this repository)
**Authoritative sources:** `source/CVI_First_Experiment.md` and
`source/causally_verified_intelligence_core_philosophies.md` were re-read in
full before this refinement; they are preserved read-only.  CVI-0's report
(`CVI_0_Pilot_Report.md`) and all CVI-0 run directories were treated as
immutable evidence and verified hash-for-hash by test suite
(`tests/test_prior_evidence.py`).

> Discipline note: **OBSERVED** = directly supported by authoritative
> files, source code, test output, environment output, API responses, or
> preserved experimental records. **INFERRED** = reasoned interpretation.
> **UNRESOLVED** = evidence insufficient.

---

## 1. Refinements made

Three CVI-0 defects were addressed.  OrderMachine semantics, the S/S′/C
architecture, R=3, causal-feedback rules, the context boundary, the
retention phase, hidden verification, the Family-C gate, the firewall, and
the evidence model were preserved.

### Defect 1 — baseline prompt asymmetry (CVI-0 §8.1)

* **Observed CVI-0 problem:** Phase-0 prompts differed between arms
  (arm-specific headings; S′ had no separate baseline).  S0 = 0.25 / 1.00 /
  0.25 for S / S′ / C could not be compared.
* **Exact change:** a single shared Phase-0 path
  (`arms.build_baseline_prompt` + `ArmRunner.run_phase_0`) is now used by
  every arm, in each arm's own fresh session and own participant call.
  The shared heading is `"Attempt each of the following tasks ONE time.
  Write one OrderMachine program per task."` — no arm names, no
  self-critique/causal/feedback/revise wording (banned-substring list in
  `arms.TREATMENT_LABEL_SUBSTRINGS`).  The Phase-0 prompt's SHA-256 is
  recorded per arm in the evidence package (`prompt_hashes.json`), and the
  official runner mechanically aborts if the hashes ever diverge.  S0 for
  all arms is computed from this shared baseline (`metrics.py`).
* **Test proving the change:** `TestPhase0PromptIdentity` in
  `tests/test_refinements.py` — participant-visible Phase-0 prompt bytes
  identical across S/S′/C (user and system text), each arm makes exactly
  one independent baseline call, no treatment labels in Phase 0.

### Defect 2 — per-instance difficulty variance (CVI-0 §6)

* **Observed CVI-0 problem:** fresh draws at the same nominal tier
  produced S0 ∈ {0.25, 0.75, 1.00}; a single calibration batch could not
  place the band.
* **Exact change:** every task now carries deterministic, recorded
  per-instance difficulty metadata (`generator.difficulty_profile`:
  stratum key, recipe, novel-op trap features, expression/queue
  structure, phrasing, params, naive-misparse discrimination counts).
  Family generation accepts a calibrated per-recipe **spec** (pinned
  parameter strata).  Calibration generates disposable stratified
  instances (one per recipe×stratum entry, 2 replicate batches) with
  disposable seeds, applies a selection rule fixed in code
  (`cvi_lab/calibration.py`, rule 1.1; rule history documented in the
  module docstring), and the official run refuses to start unless the
  selection is accepted.  Calibration seeds (20260818_1xx) and official
  seeds (20260818_001–003) are disjoint namespaces, asserted at run time
  and by tests; CVI-0's seeds are constants used only for the
  no-reuse assertion.  No task selection depends on any arm's outcome.
* **Test proving the change:** `TestPerInstanceDifficulty`,
  `TestSelectionRules`, `test_calibration_seeds_and_official_seeds_disjoint`
  in `tests/test_refinements.py`.

### Defect 3 — transfer ceiling (CVI-0 §6, §8)

* **Observed CVI-0 problem:** S_tr = 1.000 for all arms; no
  discriminative range.
* **Exact change:** Family-B S3 was reworked from the trivially solvable
  HELIX/NUDGE one-op tasks to nested/queue novel compositions
  (`fold_helix_add`: FOLD(HELIX a)+k with the swallowed-operand trap;
  `helix_push_drain`: PUSH (HELIX a)+k then DRAIN, multi-line) — different
  surface operators, the same underlying structural challenge as Family A
  (novel-op twist + expression quirk).  S1/S2 rungs keep the calibrated
  A-strata.  Calibration scores disposable transfer batches (2
  replicates per S3 level) and accepts the first level with mean S_tr in
  [0.30, 0.80] and S3 below ceiling 0.90; rejected levels are preserved
  with their reasons.
* **Test proving the change:** `TestTransferFamilyIntegrity` and the
  transfer selection-rule tests in `tests/test_refinements.py`.

---

## 2. Mechanical verification

Command (run from `CVI-Pilot/`, with `pipefail` semantics; the actual
terminal command):

```
python3 -m unittest discover -s tests
```

Result (actual output tail):

```
----------------------------------------------------------------------
Ran 117 tests in 1.078s

OK
```

Exit status: **0**.  96 pre-existing tests (updated where the protocol
legitimately changed) + 21 new/updated refinement tests.  The suite
includes the 16 required checks: Phase-0 prompt identity across arms;
baseline tasks identical; baseline outputs independently generated; no
treatment labels in Phase 0; deterministic per-instance difficulty
metadata; same-seed reproduction; calibration↔official seed disjointness;
transfer-calibration↔official-B disjointness; Family-B instances identical
across arms; Family-C gate; hidden-test inaccessibility; S receives no
feedback; S′ receives no environment feedback; C receives only permitted
feedback; context-reset behaviour; and prior evidence immutability
(verified hash-for-hash against the sealed `sha256_manifest.txt` of every
prior run directory, including all CVI-0 packages).

---

## 3. Calibration

All calibration runs are preserved (sealed) as engineering evidence, not
CVI results.  Summary:

### 3.1 Baseline strata (2 batches, 11 disposable instances each)

Per-stratum scores (2 instances per stratum):

| stratum | scores | mean |
|---|---|---|
| swizzle_mul[k=2], [k=3], [k=5] | 1.0 each | 1.000 |
| mirror_add[k=2], [k=4], [k=7] | 0.0 each | 0.000 |
| swizzle_mul_add[(2,1)], [(3,2)], [(4,3)] | 1.0 each | 1.000 |
| splice_drain[mode=drain], [mode=discard_front] | 1.0 each | 1.000 |

Batch S0 = 0.727 in both batches.  **Difficulty is recipe-degenerate for
this pinned model**: parameter strata inside a recipe do not modulate the
score; the recipe's structural trap does (MIRROR purity trap = 0.0 on 6/6
instances; the other three recipes = 1.0 on 24/24 instances).

Rule history (recorded in `cvi_lab/calibration.py` and in the sealed
packages): rule 1.0 (every selected stratum individually in band) was
unsatisfiable by construction on this evidence; rule 1.1 applies the
design's family-level band criterion with out-of-band strata **flagged** as
recorded structural observations.  Re-selection under rule 1.1 used the
sealed rule-1.0 records (`--resume`), no new baseline calls.

**Baseline selection (rule 1.1): accepted.**  Spec = {swizzle_mul k=2,
mirror_add k=2, swizzle_mul_add k=2,m=1, splice_drain mode=drain};
predicted family S0 = **0.75** (in band).  Flagged strata: mirror_add
(0.0, below band) and the three ceiling recipes (1.0, above band).

### 3.2 Transfer (level 0, 2 replicate batches of 6)

| replicate | S_tr | S3 subfamily |
|---|---|---|
| 1 | 1.000 | 1.000 |
| 2 | 0.333 | 0.000 |
| mean | **0.667** | 0.500 |

**Transfer selection: accepted** (mean in band, S3 below ceiling) at S3
level 0: {fold_helix_add k=2, helix_push_drain k=1}.  Note the large
replicate spread (1.000 vs 0.333) — batch-context sensitivity, recorded as
an anomaly (§9) and relevant to the transfer outcome (§7).

Disjointness: calibration seeds {20260818101, 20260818102, 20260818201,
20260818202, 20260818211, 20260818212} vs official seeds {20260818_001,
002, 003} — disjoint namespaces, mechanically asserted; calibration
instance checksums vs official instance checksums disjoint (tests).

Calibration participant cost: 4 API calls (2 baseline + 2 transfer).

---

## 4. Baseline integrity

* Phase-0 prompt hashes (SHA-256, user text), recorded in
  `prompt_hashes.json` of the run package:
  S = S′ = C = `0d01b023f88224da…` (identical; equality mechanically
  enforced before the run continued).
* System prompt SHA-256 recorded; identical across arms by construction
  (`build_system_prompt`).
* Task instances: the same `tasks_a` served to all arms; per-task
  sections in the baseline prompts are byte-identical (tests).
* Model configuration: provider `deepseek-official`, endpoint
  `https://api.deepseek.com/anthropic/v1` (Anthropic-style), model
  `deepseek-v4-pro` (exact API identifier returned by the provider in
  every call), temperature 0.0, thinking disabled, max_tokens 6000,
  no tools — identical for every arm and phase.
* No treatment labels in any Phase-0 prompt (banned substrings absent;
  tests).

**S0 results:** S = **0.25**, S′ = **1.00**, C = **0.25**.

Per-task S0: S and C identical pattern {A-01 0, A-02 0, A-03 0, A-04 1};
S′ {1, 1, 1, 1}.  S and C wrote the value-discard idiom
(`(SWIZZLE a b) * 2` / `OUT a`); S′ wrote `SET c SWIZZLE a b` /
`MUL c 2` / `OUT c`.  Prompts, tasks, and configuration were mechanically
identical — the 0.75-point spread is **model/API-side response variance on
byte-identical requests**, not a protocol difference.  (CVI-0's S′=1.00
was previously attributed to prompt asymmetry; this run shows the same
S′=1.00 without any asymmetry.)  See §9 anomaly 1 and §10.

---

## 5. S / S′ / C results

| arm | S0 | S_post | S_ret | S_tr | S_ver | G_F mean | M | revisions |
|---|---|---|---|---|---|---|---|---|
| S | 0.250 | undefined | 0.250 | 1.000 | 0.250 | undefined | undefined (no S_post) | 0 |
| S′ | 1.000 | 0.250 | 0.250 | 1.000 | 0.250 | 0.000 | −2.000 | 3 |
| C | 0.250 | 0.750 | 0.250 | 1.000 | 0.250 | 0.667 | undefined (zero denominator) | 3 |

Arm C interaction rounds (hidden scores):

| task | round 0 | round 1 | round 2 | round 3 | G_F | outcome |
|---|---|---|---|---|---|---|
| A-01 (SWIZZLE×k) | 0 | 1 | 1 | 1 | 1.000 | resolved at revision 1 |
| A-02 (MIRROR+k) | 0 | 0 | 0 | 0 | 0.000 | **never resolved in 3 rounds** |
| A-03 (SWIZZLE×k+m) | 0 | 1 | 1 | 1 | 1.000 | resolved at revision 1 |
| A-04 (SPLICE+DRAIN) | 1 | 1 | 1 | 1 | undefined (no failure) | solved at round 0 |

Failure events logged: C = 72; S = 0; S′ = 0.  Gaming index (C) = 0.0
(no public-pass/hidden-fail pair).  Token consumption (official run):
input 7,203; output 2,240; cache_read 43,392 (server-side prompt cache);
cache_creation 0.  API calls: 23.  Elapsed: 46.5 s.  Self-report probe:
unusable (see §9 anomaly 5).

---

## 6. Retention

* **Immediate correction (Arm C, within-session):** A-01 and A-03 fixed
  at revision 1 and stable through round 3 (G_F = 1.000 each); A-02 never
  fixed (G_F = 0.000).  Mean G_F = 0.667.
* **Retained correction (all arms, fresh context):** S_ret = 0.250 for
  every arm.  Arm C's retention programs were byte-identical to its
  baseline programs (the same value-discard idiom reappeared in a fresh
  session).  **The immediate correction did not survive the context
  boundary.**  Retention ratio M: C undefined (S0 − F_after = 0); S′ =
  −2.000 (its critique phase regressed below its own baseline, then
  retention stayed at 0.250); S undefined (no S_post).
* No claim of retained learning is made: what C demonstrated is
  in-session, feedback-driven correction only.

---

## 7. Transfer

**Family B sat at ceiling again.**  S_tr = 1.000 for all arms; per-
subfamily S1 = S2 = S3 = 1.000 for all arms; every one of the 6 official
B instances was solved by every arm (18/18).

Calibration had predicted mean 0.667 (replicates 1.000 and 0.333), which
passed the acceptance rule, but the official batch landed on the ceiling
side of that replicate distribution.  **Transfer is explicitly marked
non-discriminative**: no ceiling/floor headroom exists in the official
family, and no arm separation on S_tr can be interpreted as evidence of
anything (ceiling equality is not arm equivalence).

---

## 8. Hidden verification

* Family C generated only after all interaction phases completed
  (protocol gate: `interaction_completed_iso` ≤ `family_c_generated_iso`,
  `family_c_attempted_before = []`), from fresh seeds (20260818_003) with
  the calibrated A-spec; its keys were never participant-facing.
* S_ver = **0.250** for all arms (per-task: C-01 0, C-02 0, C-03 0, C-04 1
  — the MIRROR/SWIZZLE traps failed, SPLICE passed).  Uniform across arms.
* Firewall status: **PASS** — the 117-test suite (including hostile-
  participant simulation and hidden-material inaccessibility) passed
  before and after the run; live spot checks of every Arm-C feedback
  message confirmed feedback consists solely of `task: case N: PASS |
  FAIL (wrong output | error: CLASS)` clauses — no expected outputs, no
  hidden material, no grader internals.  Participant client imports no
  protected module and is stateless.

---

## 9. Anomalies

1. **Baseline bimodality on identical prompts.**  With byte-identical
   Phase-0 prompts (hashes equal, enforced), S and C produced the
   value-discard idiom (S0 = 0.25) while S′ produced the SET/MUL idiom
   (S0 = 1.00).  The protocol cannot explain the spread; the model
   responds bimodally to identical requests at temperature 0.
2. **S′ self-critique regressed its own correct baseline.**  S′ scored
   1.00 at baseline, then its critique round 0 produced the wrong idiom
   (0.25) and rounds 1–3 could not recover it without feedback
   (S_post = 0.25).  Private self-critique destroyed correct answers.
3. **Transfer replicate variance.**  Calibration transfer replicates were
   1.000 and 0.333 on the same level-0 S3 spec; the official batch
   resolved to 1.000.  Batch context dominates transfer difficulty.
4. **mirror_add solved at transfer, failed at baseline/retention/hidden.**
   B-S1-02/B-S2-02 (MIRROR) scored 1.0 for all arms while A-02 (same
   trap) scored 0.0 in baseline, retention, and hidden phases — idiom
   choice is context-sensitive, not a stable skill level.
5. **Self-report probe unusable (again).**  All three arms answered the
   probe with a demo program in `### TASK` format instead of answering
   the question; the system-prompt format instruction dominates.  Answers
   preserved; no claim built on them.
6. **Cache accounting asymmetry.**  The first baseline call reported 820
   input tokens; the byte-identical S′/C baseline calls reported 52
   (server-side prompt cache).  Requests were identical; accounting
   differs.  (Same phenomenon recorded in CVI-0 §8.7.)
7. **Calibration rule history.**  Rule 1.0 (every stratum individually
   in band) was unsatisfiable on the recipe-degenerate calibration
   evidence; rule 1.1 (family-level band + flagged strata) is documented
   in code with its history and was applied to the sealed rule-1.0
   records without new baseline calls (§3.1).

---

## 10. OBSERVED

* All three CVI-0 defects are fixed at the protocol level and each fix is
  mechanically proven by tests: Phase-0 prompts byte-identical
  (hash-enforced); per-instance difficulty metadata recorded and strata
  calibrated; Family-B S3 replaced with harder compositions.
* Calibration produced a usable baseline prediction (0.75) and an
  accepted transfer level (mean 0.667); all calibration instances are
  disjoint from official instances (seeds and checksums).
* Official S0 = 0.25 (S), 1.00 (S′), 0.25 (C) on identical prompts —
  a 0.75-point spread with no protocol difference.
* Official S_tr = 1.000 for all arms (18/18 B instances solved):
  transfer saturated.
* Arm C's causal loop worked: 2 of 3 baseline failures resolved at
  revision 1 and stayed resolved in-session (A-01, A-03); A-02 (MIRROR)
  never resolved; hidden results stayed invisible during interaction.
* C's correction did not cross the context boundary: S_ret(C) = 0.25 =
  S0(C), with retention programs identical to baseline programs.
* S_ver = 0.25 for all arms; Family C gated correctly; firewall PASS.
* 117/117 tests pass (exit 0); prior run packages verify hash-for-hash.

## 11. INFERRED

* The CVI-0 baseline asymmetry was real, and this pilot removed it — but
  the removal exposed that the pinned model's single-shot responses to
  identical requests are bimodal (two stable idioms), so one-shot S0
  remains a poor matching variable for this model.  Single-shot baseline
  matching cannot make the S/S′/C comparison clean while this instability
  persists.
* Transfer difficulty for this model is dominated by batch context and
  phrasing, not by the mechanical stratum parameters; a 2-replicate mean
  cannot reliably screen against a ceiling when replicate spread is
  1.000/0.333.  The S3 compositions used here are not hard enough (or
  not stably hard) for this model in the official batch context.
* Within-session public feedback gives C real corrective value (G_F mean
  0.667) but, as in CVI-0, none of it survives a context reset — the
  "in-context patchwork" pattern.  n=1, single model, baseline spread,
  and transfer ceiling forbid any scientific conclusion (this is an
  engineering pilot, not a CVI test).

## 12. UNRESOLVED

* Whether the S′=1.00 / S=C=0.25 baseline split is positional, cached-
  context, or pure sampling — 3 observations cannot distinguish these.
* Whether a deterministic-temperature model (or a provider with seed
  support) would collapse the baseline spread.
* Whether harder S3 compositions exist that stay below ceiling for this
  model without leaving the "same structural challenge" family.
* Whether A-02's persistent failure reflects spec ambiguity for MIRROR
  purity or a genuine model limitation (same question as CVI-0).
* Whether the self-report probe can be made usable with a separate
  system prompt.

## 13. Laboratory verdict

**LAB NEEDS REFINEMENT.**

CVI-0.1 succeeded as an engineering exercise: the three CVI-0 defects were
fixed, each fix is mechanically proven (117 tests, exit 0), calibration
and official instances are provably disjoint, the firewall held, and
S/S′/C completed (23 participant calls).  But the pilot did **not**
produce a clean, interpretable arm comparison, for two demonstrated
reasons: (a) baseline scores spread 0.25/1.00/0.25 across arms on
mechanically identical Phase-0 prompts (model-side response bimodality
defeats single-shot baseline matching), and (b) Family B saturated again
(S_tr = 1.000, 18/18 instances) despite below-ceiling calibration,
because transfer difficulty is batch-context-dominated and the replicate
spread (1.000/0.333) made the mean-based acceptance rule too weak.  Both
are concrete, evidence-backed refinements for the next iteration; neither
is a CVI result, and no CVI claim is made or supported here.

---

*Raw evidence: `runs/CVI-0.1_20260817T213225Z/` (config, seeds, task
definitions with difficulty metadata, prompts, prompt hashes, transcripts,
submissions, environment logs, scores, metrics, API usage, protocol log,
anomalies, manifest, SHA-256 manifest).  Calibration packages sealed
alongside.  This report was written after the raw evidence was on disk;
the evidence package was sealed afterwards.*
