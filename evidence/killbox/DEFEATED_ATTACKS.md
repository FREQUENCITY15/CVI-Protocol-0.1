# DEFEATED ATTACKS

The defence stage attempted to defeat every attack using actual project
evidence. These specific attack mechanisms are **DEFEATED** by the existing
design (the controls hold), so they do NOT count against the CVI
interpretation. Each entry states the attack, the evidence that rules it out,
and why.

---

## D1. Hidden-verifier leakage (the agent can read hidden tests / answer keys)

**ATTACK DEFEATED.** The hidden-verification keys, seeds, canonical/naive
programs, and hidden-case inputs could leak to the participant, inflating
S_ver without any learning.

**RULED OUT (OBSERVED).**
- `participant.py` imports none of `grader/generator/evidence/ordermachine` (firewall module-boundary test).
- `Task.public_view()` (`generator.py:139-151`) drops hidden cases, seeds, parameters, and all programs.
- `feedback_text`/`feedback_block` (`grader.py:77-105`) render only task id, case id, PASS/FAIL, error class — never the output value, never hidden material.
- `tests/test_firewall.py` hostile-participant simulation: a participant that demands hidden inputs/seeds/keys in its response never receives them; tests assert hidden input vectors never appear in any visible section; 117/117 tests pass pre- and post-run.
- The participant is a stateless text-only LLM with no filesystem, so the plaintext on-disk `environment_logs`/`scores.json` are not a participant channel.

**STATUS: DEFEATED.**

---

## D2. Phase-0 baseline prompt asymmetry (arm-specific headings leaking treatment identity)

**ATTACK DEFEATED.** In the current (CVI-0.1) design, the Phase-0 baseline
prompt differs between arms, so S0 is not arm-prompt-identical. **Note: this
was a real defect in CVI-0; CVI-0.1 fixed it.**

**RULED OUT (OBSERVED).**
- `arms.build_baseline_prompt` is the single shared builder; `BASELINE_HEADING` contains no treatment-identifying text.
- `tests/test_refinements.py` asserts baseline prompt bytes and system prompt bytes identical across S/S'/C; `TREATMENT_LABEL_SUBSTRINGS` banned substring check; the runner mechanically aborts if the hash-enforced baseline differs (`run_pilot.py:448-463`).
- Recorded Phase-0 prompt hashes equal across arms in the CVI-0.1 package.

**STATUS: DEFEATED** (for CVI-0.1; acknowledged as a CVI-0 defect that was fixed).

---

## D3. Feedback leaks the expected output or a richer diagnostic that gives away the answer

**ATTACK DEFEATED.** C's feedback could reveal the correct output value or a
rich error signal that directly encodes the answer.

**RULED OUT (OBSERVED).**
- `feedback_block` never includes the output value; only "case N: PASS | FAIL (wrong output) | FAIL (error: CLASS)".
- In the actual run every failure was `error_class: null`, i.e. the error-class channel delivered nothing; the feedback did not reveal expected outputs. (This is a separate weakness of *diagnostic power*, which is a SURVIVES point, not a leakage one.)
- Tests assert expected-output values never appear in feedback text.

**STATUS: DEFEATED as a leakage/acquisition-of-hidden-answer channel.**

---

## D4. Task-instance identity differs across arms (unequal task difficulty)

**ATTACK DEFEATED.** Arms could receive different task instances (e.g., C gets
easier Family-A/B tasks than S').

**RULED OUT (OBSERVED).**
- `run_pilot.py:386-392` builds Family A and Family B once and passes the same `tasks_a`/`tasks_b` to all three arm runners.
- Family-B instance checksums identical across arms (tests assert the transfer prompt text is byte-identical across arms).
- Calibration and official seeds are in disjoint namespaces (asserted at runtime and by tests).

**STATUS: DEFEATED.**

---

## D5. S receives environmental feedback or extra time (treatment bleed into the no-feedback static arm)

**ATTACK DEFEATED.** Arm S (static, no revisions) could accidentally receive
feedback or a chance to revise.

**RULED OUT (OBSERVED).**
- `run_arm_s` runs only baseline + ret/transfer/hidden/probe (one-shot, no-feedback headings).
- `tests/test_firewall.py::test_arm_s_receives_no_feedback` asserts no user-role message contains FEEDBACK/PASS/FAIL/ENVIRONMENT and the baseline session has exactly one turn.

**STATUS: DEFEATED.**

---

## D6. Family-C generation happens before interaction (hidden keys generated/leaked early)

**ATTACK DEFEATED.** Family C could be generated before the interaction phase,
so the protocol gate (hiddenness) is not temporally enforced.

**RULED OUT (OBSERVED).**
- `protocol.py` `PilotProtocol` refuses `generate_family_c` until `mark_interaction_complete()`; tests (`test_family_c_refused_before_interaction_complete`) enforce this.
- `run_pilot.py:465-469` calls `mark_interaction_complete()` only after all arm pre-interaction phases complete, then generates Family C.
- `seeds_family_c.json` records `generated_after_interaction_iso`.

**STATUS: DEFEATED.**

---

## D7. Runaway / unlimited interaction (C could iterate far beyond S' budget)

**ATTACK DEFEATED (partially).** C could spend unbounded tokens/calls, creating
a computation asymmetry. The hard runaway *call* budget **is** enforced, though
per-task *token* parity is NOT (that later point is the SURVIVES A8 issue).

**RULED OUT (OBSERVED).**
- `participant.UsageTracker` hard-caps total calls (60) and total input/output tokens (300k each), and stops the phase on breach — so C cannot run away.
- `config.r = 3` bounds C's interaction rounds; the revision loop breaks early when all public cases pass.

**STATUS: DEFEATED as a runaway/call-budget control; the related token-*parity* gap (not runaway) is listed separately as A8/SURVIVES.**

---

## D8. The model "knows" the experiment is CVI and is told which arm it is (demand/identification bias)

**ATTACK DEFEATED (in Phase 0 only).** Revealing the arm identity could induce
demand characteristics. Phase-0 baseline is treatment-label-free. However, the
Phase-1 treatment prompts **do** legitimately differ (C is told it will receive
outcomes; S' that it will not). That residual framing asymmetry is the separate
SURVIVES point A13, not a fully defeated identity leak.

**RULED OUT (OBSERVED).**
- `TREATMENT_LABEL_SUBSTRINGS` + tests: no arm names, no "causal/self-critique/feedback/revise" wording in any Phase-0 prompt.
- Baseline prompt bytes and hashes identical across arms.

**STATUS: DEFEATED for Phase 0; framing asymmetry in Phase 1 listed separately (A13).**

---

## What survives (cross-ref)

The defence stage could NOT defeat the sham-verdict/contingency confound, the
damaged-inert S' control, no-feedback derivability, broken baseline matching,
the broken retention metric M, the Family-C re-issue, the token-parity gap, the
calibration selection theater, or the transfer ceiling. See
STRONGEST_ATTACKS.md and SURVIVING_CONFOUNDS.md.
