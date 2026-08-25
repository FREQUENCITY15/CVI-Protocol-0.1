# CVI Protocol 0.1

**Causally Verified Intelligence (CVI)** is an experimental protocol for making AI capability claims harder to fake, overstate, or misattribute.

This release does **not** claim to define intelligence, prove a new scientific theory, or provide a universal AI score. It asks a narrower question:

> **Does this system demonstrate capability X under conditions Y, and does that capability survive relevant interventions?**

CVI 0.1 is a **provisional public research artifact** extracted from an exploratory concept, an implemented pilot, and an adversarial audit of that pilot. Its most important worked example is a result that was **not certified** because the evidence could not separate the intended explanation from competing explanations.

## Why this exists

A model or agent can look better after feedback for many reasons:

- it received more attempts or compute;
- it was told the answer indirectly;
- one arm had tools or a verifier another arm lacked;
- a stochastic baseline happened to be easier;
- the task was already solvable from the prompt;
- the correction existed only inside the current context;
- the transfer test was too easy;
- the hidden test repeated the same template;
- the metric itself was defective.

CVI treats these as experimental questions rather than footnotes.

## Start here

1. **[PROTOCOL.md](PROTOCOL.md)** — the current experimental method.
2. **[CLAIM-CARD.md](CLAIM-CARD.md)** — a one-page template for testing a capability claim.
3. **[INTERVENTION-GUIDE.md](INTERVENTION-GUIDE.md)** — common confounds and the controls that attack them.
4. **[case-studies/CVI-0.1-FAILED-CERTIFICATION.md](case-studies/CVI-0.1-FAILED-CERTIFICATION.md)** — our first worked example.
5. **[research/RELATED-WORK.md](research/RELATED-WORK.md)** — non-exhaustive collision with adjacent research.
6. **[research/NOVELTY-MATRIX.md](research/NOVELTY-MATRIX.md)** — what is established, what is synthesis, and what remains unresolved.

## The CVI evidence chain

CVI 0.1 separates several claims that are often collapsed into one:

```text
successful performance
        ↓
performance after feedback
        ↓
correction attributable to the intervention
        ↓
correction across a retention boundary
        ↓
transfer under changed conditions
        ↓
independent hidden verification
        ↓
bounded capability claim with surviving confounds disclosed
```

Passing an earlier stage does not imply passing a later one.

## Unit of analysis

CVI credentials a **specified system under specified conditions**. A system may include a model, prompts, memory, tools, scaffolding, environment, retry policy, and other components. If the claim is specifically about one component, the experiment must isolate that component rather than silently crediting it for system-level performance.

## Evidence vocabulary

- **OBSERVED** — directly supported by recorded experimental evidence or an inspected source.
- **INFERRED** — a reasoned interpretation consistent with the observations but not directly demonstrated.
- **UNRESOLVED** — the available evidence cannot distinguish relevant explanations.

CVI 0.1 does not provide a magic scalar or an unqualified “verified intelligence” badge. Publish the claim, conditions, gate results, and surviving confounds.

## What the first pilot taught us

The implemented CVI-0.1 pilot mechanically fixed several earlier protocol defects, but it still did not support a CVI claim. Among the observed problems:

- nominally identical baseline prompts produced scores of **0.25 / 1.00 / 0.25** across arms;
- transfer saturated at **1.00 for all arms**;
- the feedback arm corrected **2 of 3** failures in-session;
- those corrections did **not** survive the fresh-context retention boundary;
- hidden verification was **0.25 for all arms**;
- the later KILLBOX audit found additional confounds, including feedback-contingency/tool asymmetry, a damaged private-reasoning control, no-feedback derivability, and a broken retention metric.

The laboratory verdict was **LAB NEEDS REFINEMENT**, and the report explicitly states that no CVI claim was supported.

That failed certification is the first demonstration of the protocol's intended discipline: **do not promote an interesting result into a stronger claim than the instrument can support.**

## Repository map

```text
CVI-Protocol-0.1/
├── README.md
├── PROTOCOL.md
├── CLAIM-CARD.md
├── INTERVENTION-GUIDE.md
├── GLOSSARY.md
├── CONTRIBUTING.md
├── PUBLISHING-NOTES.md
├── case-studies/
├── research/
├── history/
├── evidence/
└── experiments/
```

Historical files are preserved as provenance. They may contain superseded framing, dated literature claims, or ideas that the current protocol deliberately does not adopt. **PROTOCOL.md is the current normative document for CVI 0.1.**

## Status

**Protocol status:** provisional / pre-validation  
**Empirical status:** no CVI capability claim has yet been certified by this project  
**Novelty status:** **UNRESOLVED**; individual components have substantial precedent and this release does not claim invention of causal evaluation  
**License status:** no public license has been selected yet; see `PUBLISHING-NOTES.md` before public release
