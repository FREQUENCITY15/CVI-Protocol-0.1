# CVI-0 Pilot Report

**Run id:** `CVI-0_20260817T200229Z`
**Generated:** 2026-08-17T20:14Z (after raw evidence was written and inspected)
**Laboratory:** `CVI-Pilot/` (this repository)
**Authoritative sources:** both `source/CVI_First_Experiment.md` and
`source/causally_verified_intelligence_core_philosophies.md` were read in
full before implementation and are preserved read-only.

> Discipline note: **OBSERVED** = directly supported by authoritative
> files, source code, test output, environment output, API responses, or
> preserved experimental records. **INFERRED** = reasoned interpretation.
> **UNRESOLVED** = evidence insufficient.

---

## 1. Laboratory status

A deterministic Python laboratory was built under `CVI-Pilot/` using only
the standard library:

* `cvi_lab/ordermachine.py` — **OrderMachine**: 6 registers + FIFO queue +
  output stream; 15 instructions (SET ADD SUB MUL DIV OUT PUSH POP DRAIN
  plus 6 novel operators **SWIZZLE MIRROR SPLICE HELIX FOLD NUDGE**);
  deterministic parser implementing the documented expression quirks
  (novel operators must begin an expression, their last operand swallows
  everything to the right, unary novel operators are pure value
  computations, binary SWIZZLE writes its target register, SPLICE pushes
  the queue); 9 deterministic error classes (SYNTAX, UNDEF_REGISTER,
  UNDERFLOW, OVERFLOW, DIVZERO, QEMPTY, QFULL, STEP_LIMIT, BAD_LITERAL);
  10,000-step execution protection; versioned, append-only submission
  history; zero runtime randomness.  A participant-facing spec sheet
  (`prompts/spec_sheet.md`) contains only permitted language semantics.
* `cvi_lab/generator.py` — splitmix64-seeded procedural generation.
  **Family A**: K=4 repair tasks (one per recipe template: SWIZZLE×k,
  MIRROR+k, SWIZZLE×k+m, SPLICE+DRAIN).  **Family B**: 2×S1 paraphrase
  (same rule/params/cases as A-01/A-02, reworded), 2×S2 novel-parameter
  (same recipes, new params/registers), 2×S3 novel-composition (HELIX,
  NUDGE — different operators, same structural pattern).  **Family C**:
  4 hidden-verification tasks, fresh seeds, gated behind the protocol
  state machine.  Every task is mechanically verified at generation time:
  the canonical program passes all public+hidden cases; a plausible naive
  misparse fails ≥1 public and ≥2 hidden cases.
* `cvi_lab/grader.py` — deterministic grading with two strictly separated
  faces: public (feedback = per-case PASS/FAIL + error class only) and
  hidden (score only, never participant-facing).
* `cvi_lab/participant.py` — stateless per-call LLM client (imports no
  protected module), usage tracker, runaway guard (60 calls / 300k+300k
  tokens).
* `cvi_lab/arms.py` — Arms S / S′ / C with code-enforced context
  boundaries; per-arm feedback rules verified by tests.
* `cvi_lab/protocol.py` — state machine refusing Family C generation
  before all interaction phases complete.
* `cvi_lab/metrics.py` — measurement vector; undefined metrics are JSON
  `null`, never invented.  No scalar CVI score is computed.
* `cvi_lab/evidence.py` — no-overwrite run directories, `manifest.json`,
  `sha256_manifest.txt`.

## 2. Mechanical verification

Command: `python3 -m unittest discover -s tests`

Result (actual output tail):

```
----------------------------------------------------------------------
Ran 96 tests in 0.543s

OK
```

Exit status: **0**. All deterministic local tests passed before any paid
model call. Coverage includes: VM instruction semantics, novel-operator
behaviour, deterministic seed reproduction, generator validity,
public/hidden split, hidden-test inaccessibility (hostile-participant
simulation), grader determinism, submission versioning, session reset,
context isolation, Arm S receiving no feedback, Arm S′ receiving no
environment feedback, Arm C receiving only permitted feedback, Family C
generation gating, evidence serialization, and metrics calculations.

## 3. Participant configuration

| Parameter | Value |
|---|---|
| provider | `deepseek-official` (API host `api.deepseek.com`) |
| endpoint / style | `https://api.deepseek.com/anthropic/v1/messages` (Anthropic-compatible) |
| model | `deepseek-v4-pro` |
| temperature | `0.0` |
| seed | not supported by this endpoint (recorded as unavailable) |
| thinking | disabled (`{"type":"disabled"}`) — pinned for deterministic text-only output |
| max_tokens per call | `6000` |
| timeout / retries | 600 s / 3 (exponential backoff) |
| protocol constants | K=4, R=3, generator tier=2 |
| family seeds | A=`20260817_001`, B=`20260817_002`, C=`20260817_003` (C drawn only after interaction) |
| timestamp | run started 2026-08-17T20:02:29Z; usage recorded per call |

## 4. Arm results

| arm | S0 | S_post | S_ret | S_tr | S_ver | G_F mean | M | revisions |
|---|---|---|---|---|---|---|---|---|
| S | 0.250 | undefined | 0.250 | 1.000 | 0.750 | undefined | undefined | 0 |
| S′ | 1.000 | 1.000 | 0.250 | 1.000 | 0.750 | undefined (no failures) | 0.250 | 3 |
| C | 0.250 | 0.750 | 0.250 | 1.000 | 0.750 | 0.667 | undefined (zero denominator) | 3 |

Per-task detail for Arm C (the only arm with a causal interaction phase):

| task | S0 | S_post | G_F | outcome |
|---|---|---|---|---|
| A-01 (SWIZZLE×k) | 0.000 | 1.000 | 1.000 | failure resolved at revision 1 |
| A-02 (MIRROR+k) | 0.000 | 0.000 | 0.000 | **failure never resolved in 3 rounds** |
| A-03 (SWIZZLE×k+m) | 0.000 | 1.000 | 1.000 | failure resolved at revision 1 |
| A-04 (SPLICE+DRAIN) | 1.000 | 1.000 | undefined (no failure) | solved at round 0 |

## 5. Measurement vector

* S0: S=0.250, S′=1.000, C=0.250
* S_post: S=null, S′=1.000, C=0.750
* S_ret: S=0.250, S′=0.250, C=0.250
* S_tr: 1.000 for all arms (S1=1.0, S2=1.0, S3=1.0)
* S_ver: 0.750 for all arms
* failure events (logged episodes): C=72; S=0; S′=0
* pre/post failure magnitude (C): F_before=1.0 on A-01..A-03; F_after=0.0
  (A-01, A-03), 1.0 (A-02)
* G_F per task (C): A-01=1.000, A-02=0.000, A-03=1.000, A-04=null;
  mean 0.667
* retention ratio M: C=null (S0−F_after=0), S′=0.250, S=null
* gaming index (C): rate 0.0 — no task passed all public cases while
  failing hidden cases (every failing program failed publicly too)
* revision counts: S=0, S′=3, C=3
* token consumption (official run): input 3,620; output 1,977;
  cache_read 42,752 (server-side prompt cache); cache_creation 0
* API calls: 21 (official run)
* elapsed: see `elapsed.json` in the evidence package
* self-report probe: see §8 (probe unusable — recorded as anomaly)

## 6. Difficulty assessment

**Calibration band target: 0.30–0.80.**

* OBSERVED: calibration with the final pinned configuration (tier 2,
  fresh calibration seeds) scored S0 = **0.75** — inside the band on the
  first attempt.
* OBSERVED: the pilot's own Family-A baselines were **0.25 (S), 0.25 (C),
  1.00 (S′)** on a different fresh draw of the same generator tier.  The
  per-instance variance across fresh draws of the same tier is therefore
  large (0.25 / 0.75 / 1.00 observed at tier 2).
* OBSERVED: S_tr = 1.0 for all arms — the transfer batch was at ceiling
  and provides no headroom for measuring transfer gains.
* INFERRED: the current generator tier knob does not tightly control
  per-instance difficulty; difficulty is dominated by parameter draws and
  by prompt-phrasing sensitivity (§8).  A single calibration batch is not
  sufficient to place the band reliably.
* Assessment: difficulty calibration is **partially successful** — the
  band was hit on calibration, but baseline variance across fresh draws
  and the transfer ceiling mean the generator needs refinement before
  CVI-1 (§11).  No calibration run was discarded; all are preserved under
  `runs/calibration_*/` with `runs/calibration_summary.json`.

## 7. Experimental-firewall assessment

**PASS (mechanical).** Verified by the 96-test suite and by construction:

* `participant.py` contains no import of any protected module
  (generator/grader/ordermachine/evidence).
* Participant prompts are built only from `Task.public_view()` —
  description + public examples.  Automated tests assert that a task's
  hidden input vectors never appear in that task's visible sections, and
  that a hostile participant simulation cannot retrieve hidden inputs,
  seeds, canonical/naive programs, or keys.
* Arm C feedback is generated only by `grader.feedback_block()`: task id,
  case id, PASS/FAIL, error class.  Automated tests assert no
  expected-output value ever appears in feedback text.
* Family C generation was refused before interaction completion
  (protocol gate; `family_c_attempted_before=[]`, generation timestamp
  after `interaction_completed_iso`).
* Every phase ran in a fresh session (fresh message list; new session id;
  tests assert no message carry-over across boundaries).
* Live-run spot checks of the C transcripts confirm feedback consisted
  solely of `case N: PASS/FAIL (wrong output|error: X)` clauses.

## 8. Anomalies

1. **Baseline prompt asymmetry (protocol deviation).** The three arms'
   Phase-A initial prompts used arm-specific headings (S: "…no feedback
   and you cannot revise"; S′: "…private scratchpad… you must judge your
   own work"; C: "…you will receive the outcomes…").  OBSERVED: S and C
   produced an identical wrong idiom `(SWIZZLE a b) * 2 / OUT a`
   (treating an expression statement as if its value were stored in the
   register), while S′ produced the correct `OUT (SWIZZLE a b) * 2`
   idiom and scored 1.0.  The authoritative design uses a **separate,
   prompt-identical Phase 0 baseline**; this pilot collapsed baseline into
   Phase A, so S0 is not arm-prompt-identical.  All S0 comparisons carry
   this caveat.
2. **Self-report probe unusable.** All three arms answered the probe with
   a demo program in the `### TASK` format instead of answering the
   question (the system prompt's format instruction dominated).  Probe
   answers are preserved but carry no information; no claim is built on
   them (self-report is never evidence of learning anyway).
3. **The intended precedence-quirk trap did not drive failures.** The
   model parenthesized novel operators correctly in every single
   submission; all failures came from (a) expression-statement
   value-discard semantics and (b) treating the pure unary operators
   (MIRROR) as register-writing.  Arm C's A-02 remained unresolved after
   3 rounds of "FAIL (wrong output)" feedback — a persistent
   misunderstanding, not a transient slip.
4. **Retention answers were identical to baseline answers** in Arm C
   (same wrong idiom reappeared in fresh context), while transfer and
   hidden phases used different (correct) idioms.  Phrasing sensitivity
   is visible across phases.
5. **Superseded calibration configuration.** The first three calibration
   attempts ran with thinking *enabled*; attempt 1 consumed the full
   12,000-token output budget in thinking and produced no program text
   (S0=0.0 artifact, not task difficulty).  These runs are preserved and
   labeled; the final pinned configuration disables thinking.
6. **Two aborted pilot attempts** (submission-versioning collision;
   checkpoint overwrite) — both bugs fixed, both run directories
   preserved as `aborted_bugfix` evidence.
7. **Cache accounting:** the API reports `input_tokens=3,620` plus
   `cache_read_tokens=42,752` — the repeated spec-sheet system prompt is
   served from the provider's prompt cache across calls.

## 9. Pilot interpretation

**OBSERVED**
* Arm C's causal loop functioned: submit → execute → receive public
  PASS/FAIL + error class → revise; two of three baseline failures were
  resolved by revision 1 and stayed resolved (A-01, A-03); one failure
  (A-02) was never resolved; all four tasks' hidden results remained
  invisible to the participant during interaction.
* C's within-session correction did **not** survive the context boundary:
  S_ret(C) = 0.250 = S0(C), with retention submissions identical to the
  baseline submissions.
* No arm separation appeared on the legs the CVI claim must move:
  S_tr = 1.000 for all arms; S_ver = 0.750 for all arms.  S′ ≥ C on
  every leg except S_post.
* Transfer gains were uniform and at ceiling (all arms, all subfamilies
  1.0), and hidden verification was uniform (0.75).
* The measurement machinery collected every planned quantity except a
  usable self-report; G_F and M were correctly recorded as `null` where
  mathematically undefined (e.g., M for Arm C).

**INFERRED**
* For this pinned model+configuration and this task set, public-test
  feedback added within-session corrective value but no advantage that
  crossed the context boundary; the observed pattern resembles the
  design's "C > S′ at Phase 1 but S_ret ≈ S0 — no retention; in-context
  patchwork" falsification branch (§6.2 of the authoritative design), but
  n=1, K=4, single model, and the §8.1 baseline-prompt confound forbid
  any scientific conclusion.
* Difficulty variance across fresh draws (§6) is the single largest
  threat to CVI-1's calibration plan; transfer tasks need headroom.

**UNRESOLVED**
* Whether the S′ S0=1.0 ceiling hid any self-critique effect; whether
  A-02's persistent failure reflects spec ambiguity (MIRROR purity) or
  genuine model limitation; whether the retention collapse is specific to
  the phrasing of the A-family descriptions.

## 10. CVI verdict

**LAB NEEDS REFINEMENT.**

This pilot is *not* a scientific test of CVI and is not reported as one.
The laboratory machinery itself worked — arms ran, isolation held,
measurements were collected, the firewall passed — which is what CVI-0
exists to prove.  But the pilot is not ready to pre-register CVI-1
because: (a) baseline prompts were not arm-identical (protocol
deviation, §8.1); (b) per-instance difficulty variance across fresh
draws of one tier was too large to trust a single calibration batch
(§6); (c) the transfer batch sat at ceiling, leaving no headroom for the
primary dependent variable; (d) the self-report probe returned no
usable data; and (e) the intended precedence-quirk trap did not drive
difficulty, so the generator's difficulty mechanism needs rework (§8.3).
None of these flaws invalidate the machinery demonstration; each is a
concrete, fixable refinement.

## 11. Changes required before CVI-1

1. **Separate, prompt-identical Phase 0 baseline** (shared heading for
   all arms); arm-specific framing only in Phase 1/1′.  [§8.1]
2. **Difficulty control:** replace the coarse tier knob with
   per-instance difficulty estimation (e.g., stratified parameter draws
   or pilot-screening batches), and verify the transfer tier leaves
   headroom below 1.0.  [§6, §8.3]
3. **Transfer headroom:** the S3 tier used here was too easy for this
   model; add a harder S3 tier for CVI-1 calibration.  [§6]
4. **Spec clarity for pure unary operators:** make the "MIRROR/HELIX/
   FOLD/NUDGE compute a value and do not write registers" rule more
   prominent (example programs), or accept it as a deliberate difficulty
   feature and instrument it.  [§8.3]
5. **Self-report probe:** run it with a separate system prompt that does
   not impose the program-output format.  [§8.2]
6. **Retention delay:** decide and record the ≥1h context-boundary delay
   policy for CVI-1 (this pilot used fresh-context only, per the pilot
   brief).  [design §3]
7. **Decide the thinking parameter policy** (disabled here; recorded) and
   pin it in the pre-registration.  [§3, §8.5]

---

*Raw evidence: `runs/CVI-0_20260817T200229Z/` (tasks, prompts,
transcripts, submissions, environment logs, scores, metrics, API usage,
protocol log, manifest, SHA-256 manifest). Calibration and aborted
attempts preserved alongside.  This report was written after the raw
evidence was written to disk, and the evidence package was sealed
afterwards.*
