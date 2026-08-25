# CVI Protocol 0.1

**Status:** provisional experimental protocol  
**Purpose:** test bounded AI capability claims under interventions  
**Not:** a definition of intelligence, a consciousness test, a universal benchmark, or a validated causal-inference framework

## 1. Core question

A CVI investigation begins with one sentence:

> **Does system S demonstrate capability X under conditions Y, and does that capability survive interventions relevant to the explanation being claimed?**

The protocol is about the **epistemic status of a capability claim**. It does not require a position on the system's interior experience or on a general theory of intelligence.

## 2. State the claim before testing

Write a bounded claim that can fail.

Bad:

> This agent learns.

Better:

> Under tool configuration T and budget B, feedback contingent on the agent's own execution reduces errors in task family F, the correction survives a fresh-context boundary, and it transfers to structurally altered hidden instances better than matched controls.

Record:

- the capability;
- the system under test;
- the conditions;
- the comparison or counterfactual implied by the claim;
- what evidence would weaken or falsify it.

## 3. Define the system boundary

Record all components that can contribute to performance:

- model and version;
- system/developer/user prompts;
- sampling parameters and seed support;
- context and memory;
- tools and permissions;
- executor/verifier access;
- retrieval/search;
- environment version;
- retry/branching policy;
- token, time, compute, and monetary budget;
- human intervention, if any.

Default CVI 0.1 unit: **the whole specified system**.

If the claim is about a component, such as “the model learned,” the design must isolate that component. Otherwise conclude only about the system.

## 4. Establish a stable baseline

Do not use a single stochastic baseline as if it were a property of the system.

Before treatment:

1. run repeated matched baseline measurements sufficient to expose obvious response variance;
2. use identical task construction and prompt paths across arms;
3. hash or otherwise record prompts when practical;
4. inspect score distribution, not only the mean;
5. reject or redesign if arms cannot be meaningfully matched;
6. avoid floor and ceiling regions where improvement or separation cannot be observed.

If the baseline is already perfect, the experiment may establish performance but cannot establish **correction after failure** for that task family. Use a harder, pre-specified family if adaptive correction is the claim.

## 5. Enumerate competing explanations

Before treatment, list plausible reasons the target pattern could appear without the claimed mechanism.

At minimum consider:

- additional attempts / private reasoning;
- unequal tokens, time, or compute;
- tool or verifier asymmetry;
- feedback containing answer information;
- non-contingent “you are wrong” effects;
- prompt framing / accountability effects;
- sampling variance or arm order;
- cache or session-state effects;
- contamination / memorised task templates;
- test leakage;
- scoring defects;
- task ceiling/floor;
- hidden test structural similarity;
- persistence supplied by external memory rather than the component being credited.

A CVI design is only as strong as the live alternative explanations it attacks.

## 6. Build matched controls

The control condition should differ from treatment in the smallest mechanism-relevant way available.

Common controls:

### 6.1 Static control

One attempt, no correction loop. Measures ordinary task performance.

### 6.2 Equal-budget private-reasoning control

Receives the same opportunity to reason/revise but no treatment-specific external evidence. It must actually operate on its own prior output; a fresh independent re-draw is not equivalent to self-correction.

### 6.3 Non-contingent feedback sham

Receives feedback matched in wording, timing, and salience, but the verdict is **not caused by the participant's preceding output**. This attacks the hypothesis that merely being told “wrong” or being placed in an accountability frame explains the gain.

### 6.4 Tool-parity control

If treatment can execute, search, inspect, or verify, the relevant control receives equivalent tool capability unless tool access itself is the treatment variable.

## 7. Preserve treatment isolation

Match or explicitly model:

- number of model calls;
- token budgets;
- wall-clock or compute budget when material;
- prompts except for the intended treatment;
- task order and randomisation;
- tool availability;
- feedback format and information content;
- environment state;
- human interaction.

Perfect equality is not always possible. Unequal dimensions must be disclosed, and conclusions narrowed accordingly.

## 8. Measure immediate correction

A claim of correction requires demonstrated behavioural change.

For each observed failure episode, record:

1. pre-feedback output;
2. external outcome;
3. feedback received;
4. revised output;
5. whether the original failure was actually reduced or removed;
6. number of attempts and resources used.

Do not equate verbal acknowledgement (“I fixed it”) with correction.

## 9. Cross a retention boundary

Immediate in-context improvement is not retained improvement.

Pre-specify a boundary appropriate to the claim, for example:

- fresh conversation/context;
- removal of scratchpad or episodic memory;
- delayed re-test;
- process restart;
- new machine/session;
- weight checkpoint boundary;
- external memory preserved vs removed.

State exactly **what state is allowed to persist**.

Retention conclusions apply only across the boundary actually tested.

## 10. Test structural transfer

Use changed-but-relevant tasks that require the corrected relation rather than the exact practiced instance.

A useful transfer set should:

- have headroom below ceiling and above floor;
- be disjoint from practice items;
- alter surface form and at least one structural feature relevant to the claimed capability;
- prevent simple replay of the corrected answer;
- be generated or selected before seeing treatment outcomes where practical.

Report transfer performance for all controls, including a no-feedback baseline.

## 11. Use an independent hidden verification gate

The final verification should not be controlled by the system being evaluated.

Prefer:

- hidden unit tests;
- held-out environment state;
- independently generated instances;
- external measurement;
- deterministic programmatic checks;
- blinded human assessment when necessary.

The gate should test the capability rather than merely repeat the training/practice template.

Record whether the participant had any direct or indirect access to the answers, scoring function, hidden instances, or verifier outputs.

## 12. Validate the metric

Every summary metric is another hypothesis.

Before relying on one:

- test boundary cases;
- test no-learning and perfect-learning cases;
- check range and monotonicity;
- verify that a zero-gain system cannot accidentally pass;
- preserve raw component scores so the result does not depend on one formula.

CVI 0.1 prefers a **measurement vector** over a single scalar:

```text
baseline
immediate correction
retention
transfer
hidden verification
resource use
surviving confounds
```

## 13. Precommit thresholds and stop rules

Before the official run, record:

- primary outcomes;
- minimum effect or separation of interest;
- acceptable baseline variance;
- ceiling/floor rejection rules;
- failure-episode requirements;
- retention boundary;
- transfer construction;
- hidden-verification construction;
- budget ceiling;
- abort conditions.

Calibration data and official test instances should be disjoint.

## 14. Preserve evidence

For reproducibility, retain when practical:

- configuration;
- prompts;
- seeds;
- model/provider metadata;
- task definitions;
- transcripts;
- tool/environment logs;
- submissions;
- scores;
- raw metric inputs;
- API/resource usage;
- anomalies;
- code version/commit;
- manifests or hashes.

A report written after the fact must not replace the raw record.

## 15. Report with three evidence classes

### OBSERVED

Direct experimental results and inspected source facts.

### INFERRED

Interpretations that fit the observations but are not uniquely established.

### UNRESOLVED

Live alternatives the evidence cannot distinguish.

Do not silently promote an inference because it is the story the experiment was designed to find.

## 16. Credential only the bounded claim

CVI 0.1 does **not** issue a universal intelligence score.

The strongest acceptable conclusion has this form:

> Under system specification S and conditions Y, capability X was observed to survive interventions I, retention boundary R, transfer set T, and independent verification V, subject to surviving confounds C.

If a decisive confound remains, use **UNRESOLVED**.

If treatment improves immediate performance but the correction disappears across the declared retention boundary, report **in-context correction without demonstrated retention**.

If transfer is at ceiling for every arm, report **transfer uninformative** rather than “transfer passed.”

If the hidden verifier repeats the same template, report the limited scope of verification.

## 17. Minimum CVI 0.1 publication bundle

A public CVI result should include:

- completed Claim Card;
- system specification;
- preregistered or timestamped design;
- controls and treatment descriptions;
- raw/derivable outcome data;
- retention and transfer definitions;
- verification method;
- resource-use disclosure;
- OBSERVED / INFERRED / UNRESOLVED report;
- surviving-confound list;
- code and environment details when executable.

## 18. What CVI 0.1 does not establish

Even a clean result would not by itself establish:

- general intelligence;
- consciousness or subjective experience;
- permanent model-weight learning;
- capability outside the tested system boundary;
- safety or reliability in arbitrary deployment conditions;
- formal causal identification in the Pearl/Rubin sense unless a design separately meets those requirements.

The word **causal** in CVI is therefore a research commitment to interventions and competing explanations, not a shortcut around formal causal-inference assumptions.
