# CVI 0.1 Related-Work Note

**Status:** non-exhaustive literature collision  
**Last checked:** 2026-08-25  
**Purpose:** identify overlap and prevent novelty inflation, not prove uniqueness

CVI 0.1 sits at the intersection of several established traditions. None of the individual ingredients should be presented as invented by this project.

## 1. Evaluation infrastructure

### Inspect AI

The UK AI Security Institute's **Inspect AI** is an open-source evaluation framework with composable datasets, agents, tools, scorers, logs, sandboxes, and a large collection of pre-built evaluations. This means CVI does not need to invent its own general evaluation harness. A future implementation could plausibly be expressed as Inspect tasks, solvers/agents, scorers, and transcript analyses.

Source: https://inspect.aisi.org.uk/

**Relation to CVI:** infrastructure / implementation substrate, not a competing philosophical claim.

### METR and RE-Bench

METR's **RE-Bench** evaluates frontier model agents on realistic ML research-engineering environments, with computer access, scoring functions, time budgets, and comparison to human experts.

Source: https://metr.org/blog/2024-11-22-evaluating-r-d-capabilities-of-llms/

**Relation to CVI:** substantial overlap in realistic agent evaluation, external scoring, and resource-aware capability measurement. CVI's proposed distinctive emphasis is the same-capability chain through controlled correction, retention boundaries, transfer, and competing-explanation interventions.

## 2. Iterative self-correction and feedback

### Reflexion

Reflexion uses verbal feedback and episodic memory to improve language-agent decisions over subsequent trials without updating model weights.

Source: https://arxiv.org/abs/2303.11366

**Relation:** substantial overlap with iterative correction and retained textual state. CVI asks a different question: what experimental controls justify attributing later improvement to a particular feedback mechanism, and what survives a declared boundary?

### Self-Refine

Self-Refine iteratively generates feedback on a model's own output and refines it, without additional training.

Source: https://arxiv.org/abs/2303.17651

**Relation:** strong precedent for equal-budget private refinement as a control. A CVI study of external feedback should compare against this general class of explanation rather than treating a second attempt as unique evidence of learning.

### CRITIC

CRITIC lets LLMs use external tools to validate and revise outputs, and reports benefits from tool-interactive feedback.

Source: https://arxiv.org/abs/2305.11738

**Relation:** direct precedent for external feedback improving test-time behavior. It also highlights why CVI must distinguish **tool access** from **feedback contingency**.

### Self-Debugging

Self-Debugging uses execution results and explanation to improve generated programs, with reported gains when unit-test feedback is available.

Source: https://arxiv.org/abs/2304.05128

**Relation:** direct precedent for execution feedback as a corrective mechanism. A CVI claim must not rename ordinary executor-assisted debugging as a novel causal phenomenon.

### Intrinsic self-correction limitations

Recent work has reported failure modes and biases in intrinsic self-correction when models lack oracle labels or reliable external signals.

Source: https://arxiv.org/abs/2412.14959

**Relation:** supports the need to distinguish self-generated critique from externally grounded evidence, while not proving CVI's full protocol.

## 3. Generalisation and changed conditions

### ScienceWorld

ScienceWorld evaluates agents in an interactive text environment and explicitly probes whether learned scientific concepts can be applied in novel grounded contexts.

Source: https://aclanthology.org/2022.emnlp-main.775/

**Relation:** strong precedent for interactive environments and changed-instance generalisation. CVI does not invent transfer testing.

### WILDS

WILDS standardises evaluation under real-world distribution shifts and demonstrates that in-distribution performance can differ substantially from out-of-distribution performance.

Source: https://arxiv.org/abs/2012.07421

**Relation:** broad precedent for testing capability under altered distributions rather than trusting a single static test distribution.

## 4. Intelligence and skill-acquisition framing

### Chollet, *On the Measure of Intelligence*

Chollet argues that static task skill is heavily shaped by priors and experience and proposes evaluating intelligence in terms of skill-acquisition efficiency and generalisation difficulty.

Source: https://arxiv.org/abs/1911.01547

**Relation:** major conceptual precedent for CVI's dissatisfaction with static task performance as a complete account of capability. CVI should not claim to originate the static-skill critique.

## 5. Formal causal inference

### Pearl, *Causal Diagrams for Empirical Research*

Pearl develops a formal framework for causal inference in which assumptions determine whether causal effects are identifiable from observational or experimental data.

Source: https://doi.org/10.1093/biomet/82.4.669

**Relation:** terminology warning. CVI 0.1 uses interventions and counterfactual controls, but it does **not** thereby inherit the guarantees or formal semantics of structural causal models. Claims of formal causal identification require separate justification.

## 6. What appears to be synthesis rather than novelty in ingredients

The following are all established ideas in neighbouring literatures:

- external outcome feedback;
- repeated attempts and self-refinement;
- tool-assisted correction;
- held-out and hidden verification;
- transfer/generalisation testing;
- distribution shift;
- matched controls and ablations;
- sham/placebo logic;
- resource/budget matching;
- independent scoring;
- robustness to changed conditions.

CVI's candidate value is therefore **not ownership of these components**.

## 7. Candidate contribution, stated cautiously

The project currently proposes a reusable **credentialing sequence** for one bounded capability claim:

```text
baseline
→ controlled intervention
→ demonstrated correction
→ retention boundary
→ structural transfer
→ independent hidden verification
→ surviving-confound disclosure
```

with explicit separation of system-level and component-level attribution.

Whether substantially equivalent protocols already exist in the evaluation literature is **UNRESOLVED**. This note is not a systematic review and should not be cited as proof of novelty.
