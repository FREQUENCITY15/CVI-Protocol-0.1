# Case Study: CVI-0.1 and a Failed Certification

**Status:** historical worked example  
**Source basis:** `CVI_0_1_Pilot_Report.md` and the subsequent CVI KILLBOX audit contained in the supplied experimental archive

## Why publish a failed result?

Because the method is supposed to distinguish an interesting trajectory from a justified capability claim.

CVI-0.1 produced genuine-looking within-session correction, but the experiment also produced evidence that blocked the stronger interpretation. The correct output was therefore not “CVI demonstrated.” It was **LAB NEEDS REFINEMENT**.

## Experimental intent

The pilot compared three broad configurations:

- **S** — static baseline;
- **S′** — an intended equal-budget private-critique control without environmental verdicts;
- **C** — interaction with an environment that executed and graded the participant's program, allowing revision after feedback.

The project sought separation on correction, retention, transfer, and hidden verification rather than merely a higher one-shot score.

## OBSERVED: protocol repairs before CVI-0.1

The CVI-0.1 report states that three CVI-0 defects were repaired and mechanically tested:

1. Phase-0 baseline prompts were made byte-identical and hash-enforced.
2. Per-instance difficulty metadata and disjoint calibration were introduced.
3. The transfer family was replaced with intended harder compositions.

The implementation test suite reported **117/117 tests passing**.

## OBSERVED: official CVI-0.1 outcomes

### Baseline instability

Despite identical Phase-0 prompts:

| Arm | S0 |
|---|---:|
| S | 0.25 |
| S′ | 1.00 |
| C | 0.25 |

The report described this as a **0.75-point spread with no protocol difference** and concluded that single-shot baseline matching remained inadequate for the pinned model.

### Within-session correction

Arm C began with three failing baseline tasks. During interaction:

- 2 of 3 failures were resolved at revision 1 and stayed resolved in-session;
- 1 of 3 remained unresolved;
- mean recorded correction gain was 0.667.

This is evidence that the feedback loop had useful **within-session corrective value** under those conditions.

### Retention

After the context boundary:

```text
S_ret(C) = 0.25 = S0(C)
```

The retained programs were reported as identical to baseline programs. The corrections did not survive the tested context reset.

### Transfer

```text
S_tr = 1.000 for all arms
```

All 18 transfer instances were solved. This created a ceiling and prevented the transfer leg from distinguishing the arms.

### Hidden verification

```text
S_ver = 0.25 for all arms
```

No between-arm separation appeared at the hidden-verification stage.

## Pilot verdict

The pilot report states:

> **LAB NEEDS REFINEMENT.**

It further states that neither the baseline instability nor transfer ceiling constituted a CVI result and that **no CVI claim was made or supported**.

## What the KILLBOX added

A subsequent adversarial audit asked a stronger question: even if a future run had produced the desired `C > S′ ≥ S` pattern, could the existing instrument have attributed that pattern to the intended mechanism?

Several attacks survived.

### 1. Feedback-contingency and tool asymmetry

C received an executor/verifier oracle: its program was run and graded. S′ did not receive equivalent execution results. Therefore an advantage could be explained by **tool/compute asymmetry** rather than by the causal contingency of feedback.

The audit also noted that no arm received a **non-contingent matched verdict**, so “feedback caused by my action” was never isolated from “I am explicitly told I am wrong.”

### 2. The S′ control did not cleanly measure private self-correction

The audit found that the critique phase began from a fresh independent attempt rather than actually re-presenting S′'s own baseline program for critique. This allowed stochastic re-draw and control degradation to masquerade as a comparison with private reasoning.

### 3. No-feedback derivability

The audit produced a counterexample showing that relevant answers could be derived from public worked examples without environmental feedback. This made the verdict potentially non-load-bearing.

### 4. Baseline matching remained broken

The observed 0.25 / 1.00 / 0.25 baseline split violated the experiment's own approximately-equal-static-performance premise.

### 5. The retention metric was defective

The audit tested the metric on synthetic cases and found pathological behavior, including a false pass for a no-learning case and an undefined result for the decisive corrected-then-lost case.

### 6. Transfer and hidden verification were not discriminating enough

Transfer saturated. The audit also argued that hidden verification reused the same broad task templates too closely to establish the desired degree of structural novelty.

## Evidence status after audit

### OBSERVED

- C showed within-session correction on 2/3 failures.
- The tested correction did not survive the fresh-context boundary.
- Transfer saturated for all arms.
- Hidden verification did not separate arms.
- Baseline matching was unstable.
- The audit demonstrated defects in controls and at least one summary metric.

### INFERRED

- Environmental feedback may have helped C correct in-session, but the experiment cannot isolate how much of that gain came from causal contingency versus explicit negative feedback, execution access, or another asymmetric mechanism.

### UNRESOLVED

- Whether a properly matched contingent-feedback arm would outperform an equal-information non-contingent sham.
- Whether equivalent private reasoning without environmental feedback would produce comparable gains.
- Whether stronger structurally novel transfer/verification would reveal separation.
- Whether the broader CVI protocol has predictive or explanatory value beyond existing evaluation methods.

## What changed in CVI Protocol 0.1 because of this failure

The public protocol now requires or strongly recommends:

- repeated baselines rather than single-shot matching;
- non-contingent feedback sham controls;
- genuine equal-budget private reasoning;
- tool parity;
- transfer headroom checks;
- structural novelty in hidden verification;
- metric sanity tests;
- explicit resource parity/disclosure;
- bounded conclusions rather than a scalar badge.

## Why this case matters

The experiment did not validate CVI. It did something more modest and immediately useful: it generated a concrete catalogue of ways an adaptive-capability experiment can fool its designer.

That catalogue is now part of the protocol.
