# CVI Intervention Guide 0.1

This guide translates common capability-claim confounds into experimental controls.

| Threat to the claim | Why it matters | Useful intervention/control | What remains if the control fails |
|---|---|---|---|
| More attempts / more private reasoning | Improvement may be inference-time compute, not external learning | Equal-budget private-reasoning arm that revises its own previous output | Mechanism attribution UNRESOLVED |
| “You are wrong” effect | Salient negative feedback may explain correction without causal outcome information | Non-contingent/sham verdict matched in wording and timing | Feedback contingency UNRESOLVED |
| Tool/verifier asymmetry | One arm may receive an executor, tests, search, or oracle the other lacks | Tool-parity control or explicitly make tool access the treatment | Component attribution UNRESOLVED |
| Feedback leaks the answer | Correction may be copying | Reduce information content; use binary verdict; hidden transfer | Learning/generalisation UNRESOLVED |
| Baseline stochasticity | Arm differences may exist before treatment | Repeated baselines; randomised arm order; distribution matching | Between-arm comparison uninterpretable |
| Prompt framing | “Be accountable / reflect carefully” can itself change performance | Neutral framing across arms; isolate wording changes | Treatment mechanism UNRESOLVED |
| Cache/session state | Provider or local state may couple supposedly fresh calls | Session isolation; cache audit; order randomisation | Independence of runs UNRESOLVED |
| Contamination / memorisation | Tasks may already be known | Novel/generated families; held-out transforms; contamination checks | Capability source UNRESOLVED |
| Transfer ceiling | Every arm passes, so transfer cannot distinguish them | Harder pre-calibrated transfer with repeated replicates | Transfer uninformative |
| Transfer floor | No arm can succeed, masking genuine differences | Easier calibrated family with headroom | Transfer uninformative |
| Hidden test repeats template | “Novel” verification may only be paraphrase | Structural transformation / independently generated family | Generalisation scope narrow |
| External memory supplies retention | System remembers, but model/component may not | Compare memory-preserved vs memory-removed boundaries | Only system-level retention supported |
| Metric pathology | Formula can pass no-learning cases or hide regressions | Unit-test metric on synthetic boundary cases; publish raw vector | Summary statistic invalid |
| Human intervention | Human may be the actual correcting component | Log human inputs; isolate human-assisted and unassisted arms | Model-only claim unsupported |
| Best-of-N selection | Selection can mimic learning | Match N and selection mechanism across controls | Treatment attribution UNRESOLVED |

## The sham-verdict test

A particularly important CVI control is the **non-contingent verdict**.

Suppose treatment receives:

```text
attempt → environment executes it → FAIL → revise
```

A matched sham can receive:

```text
attempt → no execution relevant to verdict → replayed/matched FAIL → revise
```

If both improve equally, the experiment has not shown that the causal link between the participant's action and the external outcome did useful work. It may have shown only that explicit negative feedback triggered another solution attempt.

The sham must be designed so that its feedback distribution does not trivially reveal which arm the participant is in.

## The tool-parity test

If treatment can execute its code against examples while the control can only think privately, treatment has both:

- environmental feedback; and
- an executor/verifier tool.

Those mechanisms must be separated before attributing the gain specifically to causal feedback.

Possible designs:

1. give both arms the executor, but make only treatment feedback contingent on its own output;
2. reduce treatment feedback to a minimal verdict and give the control a matched self-check tool;
3. treat tool access itself as the intervention and narrow the claim accordingly.

## The fresh-context test

A correction that disappears when the conversational context is removed is still useful, but it supports a narrower claim:

> **in-context correction occurred**

not:

> **the correction was retained across contexts**

Explicitly state what crosses the boundary: nothing, a compact memory record, tool state, retrieved notes, model weights, or some combination.

## The transfer-headroom test

Before an official transfer comparison:

- run calibration on disjoint instances;
- use more than one replicate when stochasticity is material;
- inspect distribution, not only a mean;
- reject a family that routinely produces all-correct or all-wrong results;
- preserve the same underlying capability while changing enough structure to prevent replay.

## Metric sanity tests

For any retention or adaptation metric, create synthetic cases such as:

- no improvement at all;
- immediate improvement fully retained;
- immediate improvement completely lost;
- regression after feedback;
- perfect baseline;
- zero baseline;
- missing episodes.

Write down the expected output before running the metric. If the formula surprises you, the formula has not earned authority over the experiment.
