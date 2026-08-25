# Causally Verified Intelligence (CVI) — Exploration Report

**Status:** adversarial research pass, not validation.
**Authoritative source examined (unchanged):** `/Users/thomasfinlayson/Downloads/causally_verified_intelligence_core_philosophies.md` (605 lines, sections 1–21; cited below as "CVI §N").
**Evidence conventions used throughout:** OBSERVED = directly stated in the CVI source, produced by an experiment, or taken from an external source actually inspected this run. INFERRED = reasoned extension. UNRESOLVED = evidence insufficient. External citations were checked via web search during this run; unverified classics are explicitly flagged.

---

## 1. Executive finding

CVI is best understood **not as a new kind of intelligence, but as an epistemology — a credentialing framework — for claims that an agent has learned something**. Its defensible core is the demand that "the agent improved" be established by an *external, temporal, transfer-based behavioural trajectory* (consequential action → observed failure → correction → retention → generalisation → independent verification), rather than by snapshot benchmarks or by the agent's own assertions. Read that way, CVI is useful, largely sound, and a genuine corrective to current LLM-agent evaluation practice. Read as a theory of a distinct type of intelligence ("True Intelligence" T, the scalar algebra), it is unsupported: the mathematics is explicitly metaphorical, every component of the loop is shared with reinforcement learning, control theory, and cybernetics, and the term "causal" invites confusion with formal causal inference, which CVI does not use.

The strongest single finding: **the theory's most interesting claim is already half-acknowledged in its own source** ("different epistemic status", "the claim of verified intelligence has not passed the gate") — and the strongest version of CVI is obtained by completing that move and abandoning the "new kind of intelligence" framing. What remains is a distinctive *protocol* proposal with real empirical content: the falsifiable prediction that two agents with equal static performance can diverge in verified adaptive capability (§18), a prediction that current agent-evaluation practice does not routinely test and that can be tested cheaply with existing LLM APIs.

---

## 2. Faithful reconstruction

### 2.1 What the source actually says

CVI began from a distinction between **intelligence observed in a static or abstract setting** and **intelligence applied by an agent in a causal world, through time, where actions have consequences and failures can be externally verified** (CVI §1). The source is explicit that the first category "may be real and substantial"; the claim is that it has a **different epistemic status** (CVI §4).

The second category — originally "TRUE INTELLIGENCE", later "Causally Verified Intelligence" — was defined by an eight-step pipeline (CVI §1):

1. entered a causal environment,
2. acted within it,
3. encountered consequences,
4. experienced failure or error,
5. reasoned about that failure,
6. corrected it,
7. retained the correction,
8. and passed an external verification gate.

The core loop (CVI §5):

```
agent → action → world change → consequence → feedback → adaptation
```

The central philosophical distinction (CVI §4):

```
static intelligence  ≠  causally tested intelligence
capability claimed → capability applied → capability tested → capability verified
```

The later state/type-transition formulation (CVI §11):

```
I_static →(causal action through time)→ I_applied →(failure resolved and retained)→ I_adapted →(independent verification)→ I_verified
```

The working definition (CVI §17):

> **Causally Verified Intelligence is intelligence demonstrated by an agent through consequential action over time, successful resolution of observed failure, retention of the correction, and independent confirmation under altered but relevant conditions.**

with the source's own caveat that the "plus signs describe necessary conceptual components, not a validated measurement equation."

The single falsifiable prediction the source states (CVI §18):

> Two agents with equal static reasoning performance can differ in Causally Verified Intelligence if one reliably resolves failures, retains corrections, and generalises them across later causal interactions while the other does not.

### 2.2 Key conceptual components, as the source defines them

| Component | Source's treatment |
|---|---|
| **Static/latent intelligence (I_s)** | Can observe, reason, infer, predict, model, explain, generate coherent representations; in a static setting it has *not necessarily* altered a real environment, suffered consequences, met external causal resistance, demonstrated durable correction, or passed an independent improvement test (§4). Real and substantial; different epistemic status. |
| **Causal action** | A(t) = π(O(t), R(t), I_s) (§13); the agent "occupies spatial dimensions, can choose some directions of action, cannot control every external force, cannot freely move backward through time" (§5). |
| **Environmental consequence** | World change dX/dt = f(X, A, D) under agent action and uncontrollable disturbances D (§13); consequences become observations along time (§6). |
| **Failure** | F(t) = L(X(t), G(t)): deviation of world state from a goal (§13). Failure is *evidence*, not merely penalty (§7, Principle 4). |
| **Unresolved failure** | Distinguished from failure itself: F ≠ U (§7). A capable system can fail often while improving; what matters is whether failure is resolved. |
| **Reasoning about failure** | Detection → reasoning → correction → measurable failure reduction → retention of the correction (§7). |
| **Correction** | "claim of correction ≠ demonstrated correction" (§9). A stated correction is not an effective one (Principle 5). |
| **Retention** | The correction persists after the immediate failure-resolution context has passed (§10, Principle 6); wisdom W is "experience converted into durable behavioural improvement" (§8). |
| **Generalisation** | The correction transfers to "altered but structurally related situations" (§10, Principle 7). |
| **External verification** | The final boundary lies **outside the reasoning process itself** (§9); the system must succeed "without privileged access to the answer that produced the original correction" (§10); verification requires an external test showing the failure was actually reduced, remains reduced, and does not reappear under comparable conditions (§9). |
| **Time** | Constitutive, not an extra multiplier: "the trajectory along which intelligence is either confirmed or disproven" (§6); W, F, T become functions of time. |
| **Wisdom (W)** | Retained improvement produced when intelligence encounters causal consequences, resolves failure, and preserves the correction over time (§8); depends on experience, correction, retention, transfer. |

### 2.3 What the source treats as what

- **Necessary conditions.** The source explicitly says the components in `CVI = capacity + causal exposure + resolution + retention + verification` are *necessary conceptual components* (§17), and the verification gate V is a necessary condition for the label: if V = 0, T_true = 0 **even though the system may have intelligence** (§13: "This does **not** imply that the system has no intelligence. It means the claim of verified intelligence has not passed the gate."). Note the precise force: these are necessary conditions **for the label "verified"** (a credential), not claimed sufficient conditions for intelligence.
- **Sufficient conditions.** None are claimed. §20 explicitly denies that failure automatically creates wisdom or that passing one test proves general intelligence.
- **Metaphors.** The 2D/3D imagery, the square/cube algebra of §3, the "flat internal representation vs operational depth" (§14), and the "volume collapses if any required dimension approaches zero" image (§14). The source itself says the original equations "began as conceptual language" (§20).
- **Provisional mathematical formulations.** Everything in §3 and §13–14. The source calls them historical starting points and conceptual language, not validated measurement equations (§4's scope note, §17, §20).
- **Empirical claims.** (1) The §18 falsifiable prediction; (2) the black-box claim that the observable questions of §15 ("Does the same failure recur in a fresh context? Does a correction survive later testing? …") can be answered through interventions, trials, and controlled perturbations (§15); (3) the implicit existence claim that static and verified-adaptive capability can come apart in real systems.
- **Philosophical claims.** Principles 1–10 (§16); the categorical epistemic-status distinction (§4, Principle 10); verification must be external (Principle 8); time is constitutive (Principle 9); failure is evidence (Principle 4); lack of introspective access changes the method but does not eliminate the possibility of evidence (§15).

### 2.4 Three layers in the source, honestly labelled

The document itself preserves a development arc, which this report respects rather than flattens:

1. **Layer 1 (historical algebra, §1–3):** O, R, E, F, I, W, T with square/cube formulas. Metaphor; retained "as the historical starting point" (§4 scope note).
2. **Layer 2 (philosophy, §4–10):** the epistemic-status distinction, failure vs unresolved failure, wisdom as retained improvement, the external verification gate, retention/generalisation requirements.
3. **Layer 3 (operational attempt, §11–19):** type transitions, time-indexed variables, the state-space equations, the G_F gate, the falsifiable prediction, and the mapping onto the "Agent Runner" project (§19) where model output = candidate capability, replay = causal test, failed checks = failure, repair = correction, later replay = independent verification.

---

## 3. Strongest existing intellectual relatives

For each entry: **A** = what the existing idea claims; **B** = resemblance to CVI; **C** = difference; **D** = does it subsume CVI? Sources marked ✔ were inspected this run via web search.

### 3.1 The agent–environment loop: reinforcement learning and control

**A.** Reinforcement learning (Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed. 2018 — standard textbook, not re-verified this run) models an agent choosing actions in an environment to maximise reward; learning proceeds through interaction, error, and feedback. Control theory and cybernetics (Wiener, *Cybernetics*, 1948; Ashby, *An Introduction to Cybernetics*, 1956 — standard books, not re-verified this run) built the same loop — sense, act, error, correct — with negative feedback as the universal mechanism of goal-directed regulation.
**B.** CVI's §5 loop is literally this loop, and its "cannot control every external force / cannot move backward through time" (§5) is the standard disturbance-and-irreversibility framing of control theory.
**C.** CVI's purpose is *credentialing*: the loop is a precondition for a verification claim about the agent, not an optimisation algorithm. RL/control ask "what policy maximises return / stability?"; CVI asks "what evidence entitles us to say this system has learned?"
**D.** Subsumption: the loop itself is fully subsumed (and was, since 1948). The verification-gate-as-epistemology is not the subject of RL/control at all.
**Classification: PARTIAL OVERLAP** (loop shared; purpose disjoint). References (verified this run via search): Sutton & Barto 2018, official book pages at [incompleteideas.net](http://www.incompleteideas.net/book/the-book.html); Wiener 1948, [HathiTrust full view](https://babel.hathitrust.org/cgi/ssd?id=wu.89074767054); Ashby 1956, [PhilPapers record](https://api.philpapers.org/rec/ASHAIT-6).

### 3.2 Skill vs skill-acquisition: Chollet's "On the Measure of Intelligence"

**A.** Chollet (arXiv:1911.01547, inspected via [ar5iv](https://ar5iv.labs.arxiv.org/html/1911.01547) and [arXiv abs](https://arxiv.org/abs/1911.01547)) argues intelligence should be measured as **skill-acquisition efficiency** (how much new skill is gained per unit of experience/priors) on tasks with minimal prior knowledge and maximum novelty — not as static skill. His ARC benchmark operationalises this.
**B.** This is the closest published relative to CVI's central distinction: static skill (CVI's "static intelligence") is deliberately demoted relative to demonstrated acquisition (CVI's "adapted/verified").
**C.** CVI is a *verification protocol with an epistemic gate* (labels and conditions on evidence), whereas Chollet is a *measurement program* (a quantity, a benchmark, priors-control). CVI also makes failure, retention, and independent verification explicit requirements; Chollet's efficiency metric does not require failure or an external gate, and his priors-control machinery is far more developed than anything in CVI.
**D.** Subsumption: no — CVI's credential logic is absent from Chollet; Chollet's priors/sample-efficiency machinery is absent from CVI. Each supplies what the other lacks.
**Classification: SUBSTANTIAL OVERLAP** on the core claim; **COMPLEMENTARY** in apparatus. Sources: [arXiv:1911.01547](https://arxiv.org/abs/1911.01547) ✔.

### 3.3 Falsification and trial-and-error epistemology: Popper, Dewey, pragmatism

**A.** Popper (*Conjectures and Refutations*, 1963 — classic, not re-verified this run): scientific claims earn status only by surviving attempted refutation; knowledge grows by conjecture and error-elimination. Dewey's pragmatism/learning-by-doing makes experience and consequence the engine of knowing.
**B.** CVI's "claim of correction ≠ demonstrated correction" and its external gate are Popperian falsification applied to *agent capability claims*; the loop is Dewey's learning-by-doing.
**C.** CVI is narrower (about individual agents' learned capabilities, verified empirically, in software) and adds retention/transfer/independence requirements Popper never needed.
**D.** Partly: the epistemic stance is subsumed; the operational credential structure is not.
**Classification: COMPLEMENTARY**. References (verified this run via search): Popper 1963, [PhilPapers record](https://dc2.philarchive.org/rec/POPCAR-5); Dewey 1916, [Google Books record](https://books.google.com/books?id=vibDAgAAQBAJ) and [MCPHS guide on "learning by doing"](https://mcphs.libguides.com/centerteachinglearning/sotl/Meet-John-Dewey-The-man-behind-learning-by-doing).

Also philosophically adjacent: **Piaget's equilibration** (disequilibrium → accommodation → re-equilibration is the failure → correction → retention cycle at schema level; verified via the [SAGE "Cognitive Equilibrium" entry](https://sk.sagepub.com/ency/edvol/humandevelopment/chpt/cognitive-equilibrium); **PARTIAL OVERLAP** — no external gate), **deliberate practice** (Ericsson, Krampe & Tesch-Römer 1993: effortful practice with immediate feedback produces durable, transferable improvement — CVI's loop as a theory of expertise; verified via [APA PsycNET](https://psycnet.apa.org/doiLanding?doi=10.1037%2F0033-295X.100.3.363); **SUBSTANTIAL OVERLAP** — but the feedback source is a coach, not an agent-independent gate), and **enactivism** (Varela, Thompson & Rosch 1991: cognition as enaction in a world; verified via the [IEP Enactivism entry](https://iep.utm.edu/enactivism/); **COMPLEMENTARY**).

### 3.4 Static benchmarks are broken: Dynabench

**A.** Kiela et al., *Dynabench: Rethinking Benchmarking in NLP* (arXiv:2104.14337, inspected via [arXiv](https://browse.arxiv.org/abs/2104.14337)) argue static benchmarks saturate and become gamed; they propose dynamic, human-and-model-in-the-loop benchmark generation that adapts to defeat current models.
**B.** Directly supports CVI's claim that static demonstration has weaker epistemic status, and its concern (§10) that one-shot passes reflect leakage/easy cases.
**C.** Dynabench attacks *benchmark construction* (static vs dynamic datasets); CVI attacks *evidence structure for a single agent's improvement claim* (trajectory, retention, transfer, gate).
**D.** Partly subsumes the "static is insufficient" premise; does not subsume the trajectory credential.
**Classification: COMPLEMENTARY / PARTIAL OVERLAP**. Source: [arXiv:2104.14337](https://browse.arxiv.org/abs/2104.14337) ✔.

### 3.5 Process vs outcome verification: "Let's Verify Step by Step"

**A.** Lightman et al. (arXiv:2305.20050, inspected via [arXiv](https://browse.arxiv.org/abs/2305.20050) and [ICLR 2024](https://mlanthology.org/iclr/2024/lightman2024iclr-let/)) show process-supervision reward models (per-step correctness) outperform outcome-supervision for training/selecting reasoning solutions.
**B.** Shares CVI's instinct that *how* the answer was produced (and whether intermediate claims hold) matters for crediting capability — a cousin of CVI's "reasoning is not verification".
**C.** Process supervision still lives inside one static answer's generation; it does not test persistence, transfer, or independence from the agent. CVI's gate is behavioural across time.
**D.** No.
**Classification: PARTIAL OVERLAP**. Source: [arXiv:2305.20050](https://browse.arxiv.org/abs/2305.20050) ✔.

### 3.6 Self-correction without external feedback is unreliable: Huang et al.

**A.** Huang et al., *Large Language Models Cannot Self-Correct Reasoning Yet* (arXiv:2310.01798, ICLR 2024; inspected via [mlanthology](https://mlanthology.org/iclr/2024/huang2024iclr-large/) and [ar5iv](https://ar5iv.labs.arxiv.org/html/2310.01798)) show intrinsic self-correction often degrades or fails to improve accuracy on reasoning tasks when no external ground truth is supplied.
**B.** This is empirical vindication of CVI's Principle 8 (the agent cannot certify its own competence by asserting it has learned) and of the anti-self-report stance of §9.
**C.** CVI's prescription (external gate) is exactly the remedy Huang et al. imply; CVI generalises the point to retention and transfer.
**D.** No — it *supports* the distinctive part of CVI rather than subsuming it.
**Classification: COMPLEMENTARY** (evidence for CVI's principle). Source: [arXiv:2310.01798](https://arxiv.org/abs/2310.01798) ✔.

### 3.7 Verbal reinforcement loops in LLM agents: Reflexion

**A.** Shinn et al., *Reflexion: Language Agents with Verbal Reinforcement Learning* (arXiv:2303.11366, inspected via [axi.lims.ac.uk entry](https://axi.lims.ac.uk/paper/2303.11366) and [web3.arxiv](https://web3.arxiv.org/tb/2303.11366)) have the agent act, receive an evaluation signal, verbally self-reflect on the failure, store the reflection in memory, and retry across episodes.
**B.** This implements most of the CVI loop in software: action → consequence → failure → reasoned correction → memory → retry. It is the closest *implementation* of CVI's loop among LLM methods.
**C.** Reflexion is a scaffolding technique for task success; its self-reflection is often *internal* (the model judges itself) unless an environment evaluator is used, and it has no independent verification gate, no delayed-retention requirement, and no generalisation test. CVI would grade a Reflexion agent's improvement as *claimed* until externally verified.
**D.** Partly: the loop is subsumed; the credential is not.
**Classification: SUBSTANTIAL OVERLAP** on mechanism, **IMPORTANT DIFFERENCE** on the verification requirement. Source: [arXiv:2303.11366](https://arxiv.org/abs/2303.11366) ✔.

### 3.8 Static imitation vs interactive correction: DAgger

**A.** Ross, Gordon & Bagnell, *A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning* (arXiv:1011.0686, inspected via [ar5iv](https://ar5iv.labs.arxiv.org/html/1011.0686)) prove that pure supervised imitation of an expert (static learning from demonstrations) compounds errors and can fail catastrophically, while interactive expert-in-the-loop correction (querying the expert on states the learner actually visits) achieves no-regret bounds.
**B.** This is a rigorous ML existence proof of CVI's central distinction: static supervision ≠ causally interactive correction, and the difference is *measurable and decisive* in the same task domain.
**C.** DAgger is about training policies with an expert oracle; CVI is about credentialing an agent's demonstrated learning. DAgger's "expert queries" are a privileged oracle — precisely the kind of access CVI's independence gate would have to account for.
**D.** No, but it demonstrates the distinction CVI names is real and operationally consequential.
**Classification: COMPLEMENTARY** (strong prior art for the static/causal distinction). Source: [arXiv:1011.0686](https://arxiv.org/abs/1011.0686) ✔.

### 3.9 Stateful, consequential agent benchmarks: SWE-bench, GAIA, OSWorld, ToolSandbox

**A.** Modern LLM-agent benchmarks put agents in *stateful* environments with externally scored consequences: SWE-bench (real GitHub issue resolution, [arXiv:2310.06770](https://arxiv.org/abs/2310.06770) ✔ via [ICLR 2024](https://mlanthology.org/iclr/2024/jimenez2024iclr-swebench/)), GAIA (assistant tasks with hidden answers, [arXiv:2311.12983](https://arxiv.org/abs/2311.12983) ✔), OSWorld (open-ended computer tasks, [arXiv:2404.07972](https://browse.arxiv.org/abs/2404.07972) ✔), ToolSandbox (stateful, conversational, interactive tool-use evaluation, [arXiv:2408.04682](https://katalog.lib.cas.cz/EdsRecord/edsarx,edsarx.2408.04682?sid=46581133) ✔).
**B.** These already supply most of CVI's *machinery*: causal environments, observable failure, external scoring, hidden test cases (SWE-bench's held-out tests are a literal verification gate).
**C.** They measure *performance* (one-shot or many-shot scores), not *verified learning trajectories*: no benchmark routine requires an observed failure → correction → retention → delayed transfer → hidden re-verification chain before crediting improvement, and none distinguishes "capability claimed" from "capability verified" as a label.
**D.** Partly: the environment-and-gate machinery exists; the trajectory credential does not.
**Classification: COMPLEMENTARY / PARTIAL OVERLAP**. Sources: ✔ as linked above.

### 3.10 Formal definitions of intelligence: Legg & Hutter

**A.** Legg & Hutter, *Universal Intelligence: A Definition of Machine Intelligence* (arXiv:0712.3329, inspected via [ADS record](https://ui.adsabs.harvard.edu/abs/2007arXiv0712.3329L/exportcitation)) define intelligence as expected performance across a distribution of environments (reward-weighted, Solomonoff prior).
**B.** Both refuse to equate intelligence with any single static demonstration; both are time-and-interaction aware.
**C.** Legg–Hutter is a *theoretical definition* (an expectation over environments, uncomputable in general); CVI is an *empirical credential* (a realised trajectory with gates). CVI measures no expectation; Legg–Hutter imposes no verification gate.
**D.** No; different epistemic projects.
**Classification: COMPLEMENTARY / IMPORTANT DIFFERENCE**. Source: [ADS record for arXiv:0712.3329](https://ui.adsabs.harvard.edu/abs/2007arXiv0712.3329L/exportcitation) ✔.

### 3.11 Further verified relatives (condensed; full map in `CVI_Related_Work_Map.md`)

- **Model-reference adaptive control (MRAC)** — Whitaker 1958; Åström & Wittenmark 1995 (verified via [ScienceDirect topic page](https://www.sciencedirect.com/topics/mathematics/control-loop) and [Open Library](https://openlibrary.org/works/OL3332633W/Adaptive_control?edition=adaptivecontrol0002edastr)). A: controller parameters adapt online so plant output tracks an external reference model. B: act → mismatch against an external reference (= observed failure) → error-driven adaptation (= correction) → persistent tracking (= retention). C: no reasoned correction, no transfer requirement, no epistemic claim. D: partly — the loop mechanics, yes; the credential, no. **SUBSTANTIAL OVERLAP**. This is arguably the closest *engineering* relative.
- **Continual learning / catastrophic forgetting** — Parisi et al. 2019 ([arXiv:1802.07569](http://arxiv.org/pdf/1802.07569v1), [PubMed 30780045](https://pubmed.ncbi.nlm.nih.gov/30780045/)). A: sequential training degrades prior skills; stability–plasticity trade-off. B: CVI's retention clause names this requirement. C: no action, correction, or verification. D: partly (retention leg only). **PARTIAL OVERLAP**.
- **Error-driven learning** — Rescorla & Wagner 1972 ([Semantic Scholar](https://www.semanticscholar.org/paper/A-theory-of-Pavlovian-conditioning-%3A-Variations-in-Rescorla-Wagner/afaf65883ff75cc19926f61f181a687927789ad1)); Schultz, Dayan & Montague 1997, dopamine reward-prediction error ([Semantic Scholar](https://www.semanticscholar.org/paper/A-Neural-Substrate-of-Prediction-and-Reward-Schultz-Dayan/12b9019f99a315a137400389ee7c6faa4cceef35)). A: learning is driven by prediction error, not by success. B: CVI's "failure is evidence" is this principle at the level of explicit reasoning. C: automatic scalar updates; no gate. D: partly. **PARTIAL OVERLAP**.
- **Online learning / no-regret** — Zinkevich 2003 ([mlanthology](https://mlanthology.org/icml/2003/zinkevich2003icml-online/)). A: algorithms with bounded regret against adversarially chosen environments. B: formalises *persistent* performance under an external, possibly hostile world — a formal cousin of CVI's persistence clause. C: no correction/verification semantics. D: partly. **PARTIAL OVERLAP**.
- **In-context learning is transient learning** — Akyürek et al. 2023, "What learning algorithm is in-context learning?" ([arXiv:2211.15661](https://arxiv.org/abs/2211.15661)). A: linear transformers implement gradient-descent-like updates inside the forward pass; nothing persists beyond the context. B: mechanistically explains *why* CVI's retention requirement is non-trivial: session learning leaves no weight trace. C: no verification claims. D: no. **COMPLEMENTARY**.
- **MemGPT** — Packer et al. 2023 ([arXiv:2310.08560](https://arxiv.org/abs/2310.08560)). A: OS-style external memory hierarchy gives LLMs multi-session persistence. B: an established mechanism CVI's retention leg can ride on. C: recall, not verification or transfer. D: no. **COMPLEMENTARY**.
- **Self-Debug** — Chen, Lin, Schärli & Zhou 2023 ([arXiv:2304.05128](https://arxiv.org/abs/2304.05128)). A: code LLMs fix their own code using execution/unit-test feedback; large gains vs no feedback. B: a clean miniature of CVI's external gate (the executing program judges the correction). C: per-example, in-session; no retention/transfer measurement. D: no. **COMPLEMENTARY** — supports CVI's Principle 8 alongside Huang et al.
- **"Self-Verification" in the LLM literature** — Weng et al. 2022 ([arXiv:2212.09561](https://arxiv.org/abs/2212.09561)). A: model scores its own candidates via internal token-probability consistency. B: shares the word "verification". C: entirely internal — precisely what CVI declares insufficient. D: no. **IMPORTANT DIFFERENCE** (terminological warning: literature "self-verification" is the opposite of CVI's external gate).
- **WILDS distribution-shift benchmark** — Koh et al. 2021 ([PMLR v139/koh21a](http://proceedings.mlr.press/v139/koh21a/koh21a.pdf)). A: standard protocol showing in-distribution success degrades under real shifts. B: operationalises "altered but related situations" as a measurement problem. C: static train/test; no loop. D: no. **PARTIAL OVERLAP**.
- **τ-bench** — Yao et al. 2024 ([arXiv:2406.12045](https://huggingface.co/papers/2406.12045)). A: agent–user–tool conversations graded by policies checking dialogue *and resulting database state*. B: verification inspects environment state against ground truth, not self-report. C: single episode; no retention/transfer. D: partly. **SUBSTANTIAL OVERLAP** (on the gate leg).
- **ScienceWorld** — Wang et al. 2022 ([ACL Anthology](https://aclanthology.org/2022.emnlp-main.775/), [arXiv:2203.07540](https://huggingface.co/papers/2203.07540)). A: interactive text environment whose tasks come in many *parametrised instances* — changed objects/quantities/locations. B: "altered but related situations" is literally the design; a stateful world. C: goal-completion grading per episode; no correction/retention loop. D: partly. **SUBSTANTIAL OVERLAP** (on the generalisation leg).
- **MLE-bench** — Chan et al. 2024 ([arXiv:2410.07095](https://arxiv.org/abs/2410.07095)). A: full ML pipelines scored against Kaggle *private* test sets. B: a genuinely agent-inaccessible external gate at scale. C: grades a final artifact; no trajectory credential. D: partly. **SUBSTANTIAL OVERLAP** (gate leg).
- **RE-Bench** — Wijk et al. (METR) 2024 ([arXiv:2411.15114](https://arxiv.org/html/2411.15114v1)). A: ML-research environments, time budgets, scripted external scoring, human-expert comparison. B: closest existing act-observe-revise-under-external-scoring loop. C: no retention/transfer requirement. D: partly. **SUBSTANTIAL OVERLAP**.
- **SWE-bench Verified** — OpenAI 2024 ([announcement](https://openai.com/index/introducing-swe-bench-verified/)). A: human re-validation showed ~40% of SWE-bench labels unreliable; curated 500-instance subset. B: implements CVI's implicit requirement that *the gate itself* be trustworthy. C: static curation, no temporal loop. D: partly. **COMPLEMENTARY**.
- **Prover–verifier games** — Scheurer et al., Anthropic 2024 ([arXiv:2407.13692](https://ar5iv.labs.arxiv.org/html/2407.13692)). A: adversarial prover/verifier training; shows verifiers can be gamed and how to harden them. B: formalises CVI's concern that the verified party must not control the verifier. C: verifier is a trained model inside the system, not an external world gate. D: no. **COMPLEMENTARY**.
- **Test-set contamination** — Schaeffer et al. (EleutherAI): controlled quantification that contamination inflates generative-eval scores ([EleutherAI blog](https://www.eleuther.ai/papers-blog/quantifying-the-effect-of-test-set-contamination-on-generative-evaluations)). A: memorisation can masquerade as capability. B: direct support for CVI's premise that passing static tests is weak evidence. C: remedies static data hygiene, not temporal verification. D: partly. **COMPLEMENTARY**.
- **Specification gaming / reward hacking** — Krakovna et al., DeepMind 2020 ([blog](https://deepmind.google/blog/specification-gaming-the-flip-side-of-ai-ingenuity/)). A: agents satisfy the letter of the reward while failing its intent. B: the canonical evidence that any gate — including CVI's — can be gamed, and why CVI's §10 warnings matter. C: diagnostic, not a remedy. D: no. **COMPLEMENTARY**.
- **Pearl's do-calculus and causal representation learning** — Pearl 1995, Biometrika 82(4) ([zbMATH record](https://zbmath.org/0860.62045)); Schölkopf et al. 2021, "Toward Causal Representation Learning", Proc. IEEE ([MPI-IS page](https://is.mpg.de/en/publications/scholkopfetal21)). A: "causal" = effects of interventions (do-calculus) or learning generative causal variables with mechanism independence/invariance. B: none at mechanism level. C: CVI's "causal" is agentic temporality (actions causing observable failures), sharing only the word. D: no. **IMPORTANT DIFFERENCE** (terminology; see §6.9).

**Cross-cutting finding from the parallel verified research:** no existing benchmark or method found operationalises the *full* CVI chain — the closest items each implement one or two legs (SWE-bench/MLE-bench: the gate; ScienceWorld: altered-instance generalisation; RE-Bench: iterative work under external scoring; Reflexion: the loop without the gate). The conjunction is unoperationalised, which is CVI's strongest claim to distinctiveness (and, symmetrically, its least-tested claim).

---

## 4. What appears already known

The following are OBSERVED as established in the inspected literature, and each is a component of CVI:

1. **The interaction loop as the substrate of adaptive behaviour** — RL, control theory, cybernetics (since the 1940s). CVI §5 adds nothing technically.
2. **Static/one-shot demonstrations have weaker evidential value than interactive performance** — Chollet 2019; Dynabench 2021; DAgger 2011; the entire agent-benchmark movement (SWE-bench, GAIA, OSWorld, ToolSandbox).
3. **Self-reported or intrinsic self-correction is unreliable without external signal** — Huang et al. 2023/2024; process-vs-outcome supervision (Lightman et al. 2023).
4. **Improvement claims require retention and transfer tests** — standard ML discipline (held-out sets, distribution-shift robustness, continual learning), largely absent from routine agent evals.
5. **Verification must be external and ideally hidden/adversarial** — held-out test suites, TDD, Dynabench, contamination studies.
6. **Failure/prediction error is the engine of learning** — Rescorla–Wagner 1972 and dopamine reward-prediction error (Schultz, Dayan & Montague 1997); adaptive control's error signals (MRAC, Whitaker 1958); Popper's error-elimination.
7. **Agents game their tests** — Goodhart's law, specification gaming, reward hacking (Krakovna et al. 2020, DeepMind), and verifier-gaming (Anthropic prover–verifier games 2024).
8. **Contamination and unreliable gates are documented problems** — contamination inflates static scores (Schaeffer et al., EleutherAI); ~40% of SWE-bench instances had unreliable resolution labels (SWE-bench Verified, OpenAI 2024).
9. **The full CVI chain is unoperationalised anywhere** — per the parallel verified survey: existing benchmarks each implement at most one or two legs of the action → failure → correction → retention → transfer → external-gate chain (§3.11).

**Verdict:** none of CVI's *components* is new. Any claim of novelty must rest on the assembled **credential structure** and its emphasis, examined next.

## 5. What may be distinctive

Candidates, each stated with honesty about where it overlaps:

1. **The mandatory chain as a single label.** Existing practice checks individual links (a benchmark here, a held-out set there). CVI's proposal is that the label "verified" be *refused* unless the whole chain — action, failure, resolution, retention, transfer, external gate — is evidenced for the same agent on the same capability. This conjunction-as-credential is close to certification practice (e.g., safety certification), but not standard in ML evaluation. (INFERRED: distinctive as protocol, not as discovery.)
2. **Time/retention made constitutive of the claim.** "The agent improved" is a diachronic claim; CVI refuses to infer it from a snapshot. Continual-learning research shares this, but agent-eval culture largely does not. (OBSERVED in source §6, §10.)
3. **Failure as required evidence, not just a metric to be averaged away** — including the failure/unresolved-failure distinction (F ≠ U). Evaluation practice typically *minimises* exposure to failure in reporting; CVI makes observed failure part of the evidence base. (OBSERVED §7.)
4. **The anti-self-report gate applied to improvement claims.** LLM agents routinely narrate learning ("I have corrected…"); CVI's §9/Principle 8 states that such narration is not evidence — now empirically supported from two directions: intrinsic self-correction fails without external signal (Huang et al. 2023), while execution/unit-test feedback produces real gains (Self-Debug, Chen et al. 2023). (OBSERVED §9; external support verified.)
5. **Black-box, system-level credentialing.** Mechanism-agnosticism (§15) means CVI grades *systems* (model + memory + tools + scaffolding), not minds — a useful and unusual clarity for agent evaluation.
6. **Categorical epistemic-status distinction.** Static vs verified as *different evidential kinds*, not points on one score axis (Principle 10). Almost all evaluation frameworks are quantitative-only.

**Overall verdict:** CVI's plausible distinctiveness is as a *evaluation/credentialing philosophy with a required trajectory structure*, not as a new scientific theory of intelligence. The risk it collapses into "good eval design" is real and is addressed in §13.

---

## 6. Strongest criticisms

Each attack is stated at full strength, followed by the best available reply (labelled). 

### 6.1 Intelligence vs learning (mislabeled construct)

**Attack.** Every operative CVI quantity — failure resolution, retention, transfer — measures **learning/adaptation quality**, plus memory, tools, and feedback quality. A mediocre reasoner with excellent memory and fast rote correction scores high CVI; a brilliant static reasoner with poor persistence scores low. "Intelligence" is doing no work except in the name; CVI is measuring a composite of learnability, memory, and reliability. Worse, because CVI's score depends on the difficulty of the failures encountered (easy failures resolve easily), the measure is hostage to environment choice.
**Reply.** Accepted in part. The source's own definition includes "capacity" as only one of five necessary components, and the differential prediction (§18) is driven by the adaptation components. The defensible fix is to rename the target construct "verified adaptive capability" and treat "intelligence" as an umbrella the credential *supports* rather than *is*. This is a change of name and scope, not of mechanism. (INFERRED.)

### 6.2 Causal exposure: must there be a real world?

**Attack.** The source's language ("alter a real environment", "occupies spatial dimensions", §1, §5) suggests embodiment. But its own operational example (§19, Agent Runner: replay, failed checks, repair, rerun) is pure software. If a sandboxed interpreter or a text world counts, then "causal" has been quietly weakened to "external and stateful"; if it doesn't count, CVI can never be tested on LLMs, its apparent target. Theorem proving shows the boundary sharply: an interactive proof assistant (Lean/Coq) is external, stateful, consequential, and unforgiving — does passing from failed proof attempts to a verified proof satisfy CVI? If yes, the "world" requirement is purely formal; if no, the criterion is covertly about physicality.
**Reply.** The defensible reading is: **an external stateful consequence-bearing system whose state the agent does not control**, with one-way time and observable outcomes. Software environments satisfy this — the source's §19 confirms it. Theorem proving satisfies it too (the kernel is the external gate). The spatial phrasing in §5 is metaphor for non-omnipotence and irreversibility, which hold in software. This is a clarification, not a change. (INFERRED from §5/§15/§19.)

### 6.3 Must failure actually occur?

**Attack.** An agent that succeeds on every attempt generates no failure evidence, so the pipeline (steps 4–6) never fires and V is untestable. The *best possible* agent is therefore un-credentialable — a degenerate case at exactly the point the theory cares about. "Avoided failure" (the agent caught its own error before committing) is invisible except against a counterfactual comparison agent. CVI thus punishes competence: the credential is only available to agents bad enough to fail first.
**Reply.** Two fixes, both preserving the theory's intent. (a) The source already defines F as *deviation from a goal* (F = L(X,G), §13), i.e., graded loss, not binary error — sub-optimal performance generates F even without outright errors. (b) Failure exposure can be engineered by *difficulty titration* (staircase/adversarial task selection) so that any finite agent eventually fails; CVI then measures the quality of recovery from induced failure. Residual weakness: zero-loss agents on a closed task family remain un-credentialable; the theory should state that explicitly rather than imply completeness. (INFERRED refinement.)

### 6.4 Retention: how long is long enough?

**Attack.** "After the immediate failure-resolution context has passed" (§10) is undefined. Does one prompt boundary suffice? A new session? A model update? An environment change? Every choice changes the meaning of the credential; a system that holds a correction for one hour and loses it in one day is different from one that holds it for a year, and CVI says nothing about this scale.
**Reply.** Retention must be operationalised as a *graded ladder of context boundaries* (same session → fresh context window → fresh session → environment instance change → model/checkpoint update), with the credential stating which boundary was crossed. This is operationalisation, not theory change. The source's silence here is a gap, not a contradiction. (INFERRED.)

### 6.5 Generalisation: how different is "structurally related"?

**Attack.** "Altered but structurally related" (§10) has no metric. Reworded paraphrase ≠ novel parameter values ≠ novel composition ≠ novel domain. Without a similarity ladder, any transfer claim can be dismissed as memorisation (make tasks maximally similar) or inflated (make them trivially different), and lookup-table agents can pass if the test distribution is small and enumerable. This is the classic generalisation-measurement problem, which CVI inherits without solving.
**Reply.** Adopt the standard apparatus CVI lacks: hidden generative task families with novel parameter draws, plus a pre-registered similarity ladder (S1 paraphrase → S2 novel parameters → S3 novel composition → S4 novel domain). Note this problem is *not unique to CVI* — it is the central measurement problem of all ML generalisation research; CVI inherits it but does not worsen it. The transfer requirement remains the load-bearing anti-memoisation clause, more important than retention (see §10, counterexample 3). (INFERRED.)

### 6.6 Who verifies the verifier?

**Attack.** The external gate V is itself a claim by a test harness — infinite regress. Automated tests can be badly written; environments can be buggy; "independent" graders can share the agent's blind spots. If CVI demands absolute independence, no verification is possible.
**Reply.** The source's actual requirement is weaker and coherent: the gate must lie **outside the agent's reasoning process** (§9) — independence *from the agent*, not from all fallible systems. Independence is therefore gradable: agent-written tests (weakest) < harness-written < hidden from the agent < adversarially generated (Dynabench-style) < external-world consequences (strongest). The regress terminates in shared practice and community standards, exactly as in test-driven development, hardware certification, and audit. Automated tests count (the source's §19 uses failed checks as the causal test). (OBSERVED §9/§19; grading scheme INFERRED.)

### 6.7 Static capability can be indirect evidence

**Attack.** Static tests give *probabilistic* evidence about future interactive performance — they correlate. So the categorical separation (Principle 10: "categorical as well as quantitative") is too strong: it implies an ontological wall where there is only a difference in evidential strength. Worse, the source concedes static intelligence "may be real and substantial" (§4) — so the only defensible reading is that *the evidence types differ*, not the underlying quantities. If the underlying ability is the same thing, "T_true = 0 without V" (§13) is credential bookkeeping, not a fact about the system.
**Reply.** This attack succeeds against the ontic reading and fails against the epistemic reading. The honest CVI claim is: static evidence and trajectory evidence support different *kinds of conclusions* — a snapshot supports "can produce answer X in context Y"; a verified trajectory supports "learned and retains capability Z". The source already gestures here ("different epistemic status"); completing the move means deleting the suggestion that T_true is a magnitude of intelligence. Also, "static" reasoning tests are not epistemically worthless: they are *weak* evidence for the same construct, and CVI should say so rather than imply categorical exclusion. (INFERRED; this is attack #10's seed.)

### 6.8 Confounders

**Attack.** Two agents with identical "intelligence" can differ on every CVI measure because of unequal memory (context length, external stores), attempts (budget), tools (interpreter, calculators), compute (inference-time scaling), feedback quality (one gets richer error messages), environment access (one can reset/roll back, or read the verifier), or training-data contamination (one already saw the tasks). CVI attributes the difference to "verified intelligence" unless every one of these is controlled or ablated — and with LLM agents, "the agent" is always a composite of model + scaffolding + tools + memory.
**Reply.** CVI must be declared a **system-level** credential (consistent with §15's black-box stance), with matched budgets, pinned tool versions, feedback-format equality, contamination screens (novel generative task families), and ablation arms (e.g., a no-feedback-but-same-budget control, as in `CVI_First_Experiment.md`). The source is silent on all of this — a serious gap in its current form. (INFERRED.)

### 6.9 The word "causal"

**Attack.** CVI's "causal" is the everyday sense — actions produce consequences — not Pearl's causal inference (do-calculus, counterfactuals, confounding), and not causal representation learning. Evidence: the world model is an ODE `dX/dt = f(X,A,D)` (§13), a dynamical system with no structural equations or interventions; "causal consequence" means "consequence of action". The name "Causally Verified" therefore invites a misreading — that the verification uses formal causal inference — which the theory does not deliver. If "causal" means "through interaction with consequences", it should be called "interactively verified" or "consequentially verified".
**Reply.** The distinction is real and should be made explicit in the theory: CVI uses causal in the *common-sense/dynamical* sense. Two options: rename (honest, costs branding) or keep the name and add a definitional sentence (cheap, retains continuity). The underlying content is unaffected. (OBSERVED in source; renaming suggestion INFERRED.)

### 6.10 Verification vs intelligence itself

**Attack.** The strongest version of this objection: **CVI is an epistemology of intelligence claims, not a type of intelligence.** Every sentence that survives scrutiny is about *warrant*: "different epistemic status" (§4), "the claim of verified intelligence has not passed the gate" (§13), "claim of correction ≠ demonstrated correction" (§9). The pipeline is a protocol for *when one is entitled to assert* learned capability. There is no new quantity. If so, CVI's contribution is to evaluation methodology — valuable but not a theory of intelligence, and its "type transition" (I_static → … → I_verified) is a bookkeeping device, not a natural kind.
**Reply.** Treat this seriously — and accept it. The steelman (§7) adopts this reading wholesale: CVI as a credentialing epistemology. This is not a defeat; an epistemology of capability claims is precisely what agent evaluation lacks, and CVI's principles become *testable methodology* rather than metaphysics. The one thing lost is the branding claim of a new intelligence type. (INFERRED; this report's position.)

### 6.11 Further attacks (beyond the mandated ten)

- **Goodhart/gaming of the gate.** Any fixed external test becomes a target; agents learn to pass the gate rather than the capability (specification gaming, reward hacking). Mitigation: hidden, adversarially regenerated verification instances never reused; the gate itself must be part of the dynamic loop (Dynabench's lesson).
- **Sample-efficiency silence.** CVI cannot distinguish learning in 3 failures from learning in 300 — an intelligence-relevant distinction (Chollet's whole program). Fix: add an efficiency axis (attempts per unit of verified improvement); note this moves CVI toward Chollet's territory and should be optional, not core.
- **Trivial-loop objection.** A thermostat acts, corrects deviation, and retains its correction policy — does it have CVI? Fixed-rule correctors fail the *novelty* requirement (they correct only pre-programmed error classes, so transfer to altered situations fails), which is exactly why the transfer clause is load-bearing. But an *adaptive* controller (online system identification) would pass most gates — and adaptive control is engineering, not "intelligence". Conclusion: CVI grades adaptivity, and calling the top grade "intelligence" is a naming choice, not a finding.
- **The verification event is just another static snapshot.** "Verified adaptive performance" is a finite-sample statistical claim (a few hidden instances at a delay). The source says nothing about effect sizes, power, replication, or false-positive control, so a lucky pass (§10's own list) can produce a false credential. Fix: pre-registered thresholds, multiple hidden families, replication.
- **Circularity.** If CVI is "passes tests of retained generalised improvement" and those tests are just tests, then CVI = "does well on our suite" — tautological. The non-tautological content is the *structure of the evidence demanded* (trajectory, independence, transfer). The theory should state this openly: its content is a protocol, not a latent.

---

## 7. Strongest surviving version

### 7.1 The minimal core

> **CVI-minimal:** *A claim that an agent has learned something is not established by its answer generation or self-report. It is established only by an externally auditable trajectory in which the agent acted on a stateful system it does not control, encountered observable failure, produced a change that reduced that failure, retained the reduction across a stated context boundary, transferred it to unseen related cases, and passed verification conditions it could neither access nor control in advance.*

Even smaller, for the name-plate: **"Learned capability is a trajectory property, not a snapshot property; claims of it require external, temporal, transfer-based evidence."**

This is the smallest claim that is still (a) useful — it dictates eval design; (b) distinctive — it excludes snapshot benchmarks, self-report, and unverified self-correction; (c) testable — §18's prediction operationalises it. Everything else in the source is either supporting principle or discardable apparatus.

### 7.2 The surviving package

| Element (source) | Survives as | Status |
|---|---|---|
| Static ≠ verified, epistemic-status distinction (§4, Principle 10) | Distinction between *evidence types* (snapshot vs trajectory), not between kinds of mind | Kept, re-framed |
| Loop (§5) | Standard RL/control loop; retained as the required evidence substrate, credited to its true owners | Kept, de-novelised |
| Failure is evidence; F ≠ U (§7) | Required-failure exposure with difficulty titration | Kept |
| Claim ≠ demonstrated correction (§9, Principle 5) | Anti-self-report rule | Kept, empirically supported |
| External verification gate (§9, Principle 8) | Graded-independence gate (agent-written < harness < hidden < adversarial < world) | Kept, operationalised |
| Retention (§10, Principle 6) | Stated context-boundary ladder | Kept, operationalised |
| Generalisation (§10, Principle 7) | Pre-registered similarity ladder + hidden generative families | Kept, operationalised |
| Time constitutive (§6, Principle 9) | Trajectory requirement for *learning* claims | Kept |
| Black-box empiricism (§15) | System-level credentialing; mechanisms optional | Kept |
| Wisdom W (§8) | "Retained improvement" — kept as a *name for the measured quantity*, not an independent construct | Kept, renamed |
| Type transition (§11) | Credential state machine (labels, not kinds) | Kept as protocol |
| Scalar algebra (§3, §13, §14) | Dropped as measurement; kept as history/metaphor; G_F gate salvaged (see §9) | Dropped/rehabilitated |
| "True Intelligence" T (§1, §13) | Renamed "verified adaptive capability"; no claim of a new intelligence type | Renamed |
| "Causal" in the name | Explicitly defined as everyday/dynamical sense, or rename to "interactive verification" | Disambiguated |

### 7.3 Refinements, itemised as required

For each: CURRENT CVI CLAIM → PROBLEM → PROPOSED REFINEMENT → WHY IT HELPS → CHANGES-OR-CLARIFIES.

1. **"TRUE INTELLIGENCE" is a distinct type of intelligence (§1, §13).** → Problem: no supporting quantity; contradicts the source's own epistemic reading; invites the mislabel objection (6.1). → Refinement: treat T as a credential (verified adaptive capability), never as an intelligence magnitude. → Why: preserves all testable content, removes the unsupported ontology. → **CHANGES the theory** (narrowing), in line with the source's own §13 caveat.
2. **"Real environment", spatial dimensions (§1, §5).** → Problem: inconsistent with the software example in §19 and with black-box empiricism. → Refinement: "external stateful consequence-bearing system the agent does not control". → Why: makes the requirement satisfiable by LLM agents and proof assistants; removes covert physicalism. → **CLARIFIES.**
3. **Verification "external" (§9).** → Problem: no independence metric; regress objection (6.6). → Refinement: graded independence scale; gate must be *hidden from and uncontrollable by the agent*. → Why: makes Principle 8 operational and gradable. → **CLARIFIES.**
4. **"Altered but structurally related" (§10).** → Problem: undefined similarity (6.5). → Refinement: pre-registered similarity ladder + hidden generative task families. → Why: makes transfer measurable and distinguishes it from memorisation. → **CLARIFIES.**
5. **Failure must be *experienced* (§1 pipeline).** → Problem: perfect agents degenerate the gate (6.3). → Refinement: graded loss F = L(X,G) plus engineered difficulty titration. → Why: restores testability at the high end; keeps failure-as-evidence. → **CLARIFIES + small extension.**
6. **Retention duration (§10).** → Problem: undefined boundary. → Refinement: ladder of context boundaries, stated in the credential. → Why: turns Principle 6 into a measurable claim. → **CLARIFIES.**
7. **Single scalar T_true (§13).** → Problem: arbitrary algebra, dimensional incoherence (see §9). → Refinement: measurement *vector* [static score, resolution G_F, retention, transfer, independence grade, efficiency] + Boolean credential thresholds. → Why: matches the source's own conjunction logic ("volume collapses if any dimension zero"), resists gaming, shows *which* component failed. → **CHANGES the apparatus** (drops scalar), **preserves the intent**.
8. **"Causal" (§name).** → Problem: technical ambiguity (6.9). → Refinement: define as everyday/dynamical sense; optionally rename. → Why: prevents misreading as causal-inference verification. → **CLARIFIES.**
9. **Silence on statistics/confounders.** → Problem: lucky passes, budget/tool/memory confounds (6.4, 6.8). → Refinement: pre-registered thresholds, replication, matched budgets, ablation arms. → Why: makes the §18 prediction testable without vacuous wins. → **EXTENDS the method**, no theory change.
10. **Agent identity.** → Problem: model vs system ambiguity. → Refinement: CVI grades *systems* (agent + scaffolding + memory + tools), with the model as a pinned component. → Why: consistent with §15. → **CLARIFIES.**

**What survives is: CVI as a certification protocol for adaptive capability.** The smallest useful claim (§7.1) requires no equation, no new kind of intelligence, and no physical embodiment — and it is exactly what the current LLM-agent evaluation culture most lacks.

---

## 8. Conceptual ambiguities

1. **Intelligence vs adaptivity/learning** — the operative measures are learning measures; whether the construct is "intelligence" is unresolved (§6.1).
2. **"Causal"** — everyday action→consequence sense (OBSERVED in source) vs Pearl-style causal inference vs causal representation learning. Three different meanings; the source uses only the first (§6.9).
3. **Failure** — binary error vs graded deviation-from-goal; observer-relative (goals G(t) are exogenous and could drift); F(t) defined but G(t) never constrained (a goal-redefining agent could "resolve" anything).
4. **Retention** — behavioural persistence vs internal mechanism; duration undefined; system-level memory counts or doesn't (source never says).
5. **Generalisation** — "structurally related" undefined; similarity ladder absent.
6. **Verification** — degree of independence undefined; automated tests count (yes, per §19) but grading is absent; the verifier-regress is unaddressed.
7. **Time** — constitutive (§6) vs measurement convenience: if verification only needs two time points, "time is constitutive" reduces to "improvement is diachronic", which is analytic rather than substantive.
8. **Static vs interactive** — confounded with *feedback availability*: a "static" agent in most real comparisons is also a no-feedback agent; the distinction may be about feedback, not about acting (see experiment design).
9. **Agent identity** — model vs system; the source is silent; §15 implies system-level.
10. **Wisdom W** — is "retained improvement" a distinct construct or merely a label for the integral of η·C·G_F·M? The source never distinguishes.
11. **Claim vs capability** — the deepest ambiguity: is the static/causal divide about the *agent's abilities* (ontology) or about *our warrant for claims* (epistemology)? The source contains both readings; only the epistemic reading survives attack (§6.7, §6.10).
12. **Notation collisions** — C(t) is "causal consequence" in §13 but "adaptive performance axis" in §14; A(t) is "action" in §13 but "adaptive performance" in §14; V is a gate in §13 and an axis in §14. The symbol reuse is a real (minor) hazard for anyone formalising CVI.

---

## 9. Mathematical assessment

### 9.1 Equation-by-equation classification

| # | Equation (source §) | Classification | Problems found |
|---|---|---|---|
| 1 | √(O+R) = I ⟺ O+R = I² (§3) | **Metaphorical notation** | O and R are never defined as quantities; units unknown; the "2D" reading is imagery, not mathematics. |
| 2 | I²/E − F/R = W (§3) | **Unsupported formalisation** | Dimensionally incoherent: I²/E and F/R must share units to subtract; E=0 or R=0 is a singularity; no normalisation; the combination is arbitrary. |
| 3 | W·R·I = T³ (§3) | **Metaphorical notation** | Cube exponent arbitrary (justifies "3D" imagery); T³ vs T scaling undefined; only salvageable content: T>0 requires all factors >0 — a conjunction, not arithmetic. |
| 4 | Static ≠ causally tested; claimed→applied→tested→verified (§4) | **Definition / type system** (philosophical claim) | Fine as labels; testable only after states are operationalised. |
| 5 | agent→action→world→consequence→feedback→adaptation (§5) | **Mathematical model sketch** (qualitative) | The standard RL/control loop; no equations; correct as a diagram. |
| 6 | A(t)=π(O(t),R(t),I_s) (§13) | **Definition** | Policy definition; π unspecified; fine. |
| 7 | dX/dt = f(X,A,D) (§13) | **Mathematical model (template)** | Standard ODE control form; f unspecified; D as disturbances is orthodox; one-way time assumed. Fine as a template, unfalsifiable as stated. |
| 8 | F(t) = L(X(t),G(t)) (§13) | **Definition / candidate metric** | Sound in form; requires L and G to be fixed and pre-registered, else goal drift (an unaddressed loophole). |
| 9 | G_F = max(0, F_before−F_after)/(F_before+ε) (§13) | **Candidate metric (salvageable)** | Dimensionless, bounded [0,1], ε guards zero. Problems: (a) max(0,·) discards worsening magnitude — F_after > F_before gives G_F=0, losing information (a signed version (F_before−F_after)/F_before ∈ (−∞,1] is better for research); (b) must hold task difficulty constant or the ratio is meaningless (improvement on an easier instance ≠ resolution); (c) floor effects: F_before≈0 → ratio undefined/meaningless (no headroom, no resolution possible); (d) the time window for before/after is unspecified. |
| 10 | dW/dt = η·C·G_F·M; W(τ)=W(0)+∫… (§13) | **Mathematical model sketch / unsupported as measurement** | Units undefined; η unexplained; C(t) never given a numerical definition; M(t) undefined as a function; W(0) unspecified. Conceptually fine (improvement accumulates through resolved, retained corrections); numerically empty. |
| 11 | T_true = V·∛(I_s·R_eff·W) (§13) | **Definition of a credential** (logical conjunction dressed as algebra) | Cube root is retained metaphor; I_s and W scales undefined, so the number is meaningless. The only content: T>0 ⟺ V=1 and all factors >0. That is credential logic and is *defensible as logic*, not as arithmetic. |
| 12 | T(t) = C(t)·A(t)·V(t) (§14) | **Metaphor** | Symbol collisions with §13 (C, A, V reused with different meanings); "volume collapses" is a conjunction claim. |
| 13 | CVI = capacity + causal exposure + resolution + retention + verification (§17) | **Definition** (component list) | Source itself says: not a validated measurement equation. The "+" is conjunction, not addition — the source says so. |

### 9.2 Verdict

- The algebra (§3) is metaphor, and the source already says so (§14, §20). It should be treated as history, not mathematics.
- The state-space templates (§13, eqs. 6–8) are standard control/RL notation and are *fine as templates* — they are the one place the source's instinct is technically orthodox.
- **G_F is the one genuinely salvageable metric** (a normalised improvement ratio), with the fixes listed in row 9.
- **T_true is credential logic**, not a measurement: keep the gate, drop the arithmetic.
- The source's own best insight (§11's type transition) is a **state machine**, and that is the right formalism. A finite-state labelling protocol with pre-registered predicates for each transition (action occurred? failure observed? resolution ≥ threshold? retention across stated boundary? transfer on hidden instances? gate independence grade?) is more faithful to the theory's logic than any scalar, and is directly implementable.

### 9.3 Why a vector/automaton beats a scalar

A scalar CVI score would (a) require arbitrary weights across incommensurable axes (violating the source's own "no substitution" clause, §14); (b) hide *which* requirement failed — the diagnostic value of the framework; (c) invite gaming (a single number to chase). A measurement vector [static score; G_F; retention; transfer-by-ladder; independence grade; efficiency] plus a Boolean credential (all components above pre-registered thresholds) matches the source's conjunction logic ("the volume collapses if any dimension approaches zero", §14), supports ablations, and is statistically honest. A causal-graph or probabilistic formulation could additionally represent the *evaluation* structure (agent ability → performance, with memory/feedback/tools as measured confounders to condition or ablate), but the primary rehabilitated representation is: **state machine for the credential; measurement vector for the evidence; no scalar.**

---

## 10. Counterexamples

For each: what the system is, what CVI (as written) says, which definition causes trouble, and the diagnosis.

| # | System | CVI's verdict (as written) | Troubled definition | Diagnosis |
|---|---|---|---|---|
| 1 | **Brilliant static reasoner, no persistent memory** — near-perfect first-contact performance on every novel task; nothing is ever "retained" because nothing needs to be. | Never fails → pipeline steps 4–8 never fire → **unverifiable**; classified as high-static, unverified. | Failure requirement (§1, §7) | The gate degenerates exactly for the best agents (§6.3). CVI conflates "verified learning" with "intelligence"; the credential-reading of CVI handles this, the ontic reading does not. |
| 2 | **Mediocre reasoner, superb learner** — low baseline, fast failure resolution, perfect retention and transfer. | High CVI. | The name ("intelligence") | CVI grades a *learning* system as maximally intelligent. Defensible only if CVI is renamed "verified adaptive capability" (§6.1). |
| 3 | **Rote memoriser** — stores every correction verbatim; perfect retention; fails on novel parameter values. | Blocked at generalisation — correctly. | None | This is CVI's strongest case: the transfer clause is what excludes lookup tables. Works *only if* transfer instances are truly novel and hidden (§6.5). |
| 4 | **Generalises without ever failing** — strong priors, first-contact success everywhere. | Same as #1: unverifiable. | Failure requirement | Duplicate of the degenerate case; same diagnosis. |
| 5 | **Frozen weights, external memory** — model never changes; corrections written to a file and retrieved. | Passes all behavioural gates (retention and transfer are observable in behaviour). | None | Consistent with §15 black-box empiricism — CVI must accept that it grades *systems*, not minds. A paper notebook plus lookup could be "CVI" on a closed task family; the theory should say so openly. |
| 6 | **Improves only because its tools improve** — compiler/tool upgrade mid-run. | Apparent CVI, real confound. | Attribution (unstated) | CVI has no tool-version pinning or ablation requirement; apparent "wisdom" is environmental. Fixable by protocol (§6.8), currently a hole. |
| 7 | **Perfect-feedback agent** — oracle ground truth after every error. | Passes everything. | Independence clause (§10) if the oracle is also the verifier; otherwise silent. | Credit misattribution: the agent is a channel for the oracle's competence. If verification blocks the oracle and demands hidden transfer, the agent fails on transfer (instance-level feedback doesn't generalise) — the gate *can* catch this, but only if feedback granularity is recorded and the gate is truly independent. |
| 8 | **Passes by luck** — one lucky pass, G_F high on one instance. | False credential. | Statistics (unstated) | The source's §10 lists luck as a threat but offers no control (replication, thresholds, power). Fixable; currently a hole. |
| 9 | **Deterministic error-correcting software** — PID controller, ECC memory, TCP retransmission. | Fixed-rule correctors fail the *novelty* clause (they correct only pre-programmed error classes → no transfer to altered situations) → excluded. But an **adaptive controller** (online system identification) would pass most gates. | Novelty/transfer (§10) and the name | The transfer clause does real work here and should be credited for it; but adaptive control passing CVI shows CVI grades *adaptivity*, and calling the top grade "intelligence" is a naming choice (§6.11). |
| 10 | **Prompt-leakage learner** — sees expected answers, memorises them. | Passes retention; fails hidden verification (§10's "independent re-verification" clause). | Independence (§10) | The gate catches this *if and only if* hiddenness is enforced. This counterexample shows the independence clause is load-bearing — and that CVI collapses without it. |
| 11 | **Environment-overfitter** — learns to exploit simulator bugs rather than the task. | Passes in-simulator verification; fails out-of-simulator verification. | Verification scope (§9) | Environment-overfitting is the analogue of test-set overfitting; verification must span multiple environment instances/generators. Unstated in the source. |
| 12 | **Self-critiquing agent with no external feedback** (Reflexion-style, no environment scores). | Claims correction (step 6) but no external demonstration → not CVI-verified. | Principle 8 | Correct and important: this is where CVI adds real value over self-correction scaffolding, and Huang et al. 2023 supplies the empirical backing (§3.6). |

**Summary:** CVI classifies sensibly in 6 of 12 cases (3, 5, 10, 12, and the fixed-rule half of 9, plus 2 under renaming); the trouble cases (1, 4, 7, 8, 6) trace to the *failure requirement*, *missing statistics*, *missing attribution controls*, or the *intelligence naming* — all fixable by the §7 refinements, except the degenerate perfect-agent case, which is inherent and must be accepted and stated.

---

## 11. Operational definitions

For each concept: operational definition, measurements, confounders, edge cases, and what would falsify the measurement. All quantities are behavioural, per the source's black-box principle (§15).

### 1. Static capability (I_s)
- **Definition:** expected score of the agent on held-out, non-interactive, non-adaptive instances sampled from a task generator the agent never saw, with no environment feedback during the attempt.
- **Measurements:** accuracy/quality on a pre-registered hidden instance set; score variance across generators; contamination probe (does the model reproduce generator internals?).
- **Confounders:** training-data contamination, scaffolding, compute budget, prompt cosmetics.
- **Edge cases:** open-ended tasks without gold answers (use rubric or pairwise judging); near-ceiling baselines (no headroom for later failure).
- **Falsifies the measurement:** scores shift with prompt paraphrase alone, or collapse on novel generator draws while matching public-benchmark scores.

### 2. Action (A)
- **Definition:** an agent message or tool call that produces an externally recorded change in the state of a system the agent does not control.
- **Measurements:** state deltas attributable to the agent; write events; tool-call log.
- **Confounders:** read-only browsing mislabeled as action; simulator accepting no-ops.
- **Edge cases:** pure information actions (queries) — count only if they change external state or incur irreversible costs.
- **Falsifies:** no state delta across an entire episode → no causal exposure occurred.

### 3. Causal consequence (C)
- **Definition:** the externally evaluated effect of the agent's action on the environment's state, measured by a fixed scoring function over the state.
- **Measurements:** environment score before/after each action; attribution via action-state pairs; stochastic environments: score expectations over seeded trials.
- **Confounders:** environment noise, other agents, time pressure.
- **Edge cases:** stochastic worlds where "the" consequence is a distribution — use seeded replications.
- **Falsifies:** consequences statistically independent of actions (no causal link — the exposure is illusory).

### 4. Failure magnitude (F)
- **Definition:** pre-registered loss of the world/goal state relative to the task goal, F = L(X, G), with L and G fixed before the trial.
- **Measurements:** task score shortfall, test-failure rate, resource overshoot; graded (not binary) where possible.
- **Confounders:** goal redefinition by the agent, difficulty differences between instances.
- **Edge cases:** binary pass/fail tasks (use failure rate over a batch); near-miss thresholding.
- **Falsifies:** F uncorrelated with expert judgment of failure, or manipulable by goal drift.

### 5. Failure resolution (G_F)
- **Definition:** normalised improvement ratio on matched-difficulty instances, G_F = (F_before − F_after)/F_before computed on instances of equal calibrated difficulty (signed version preferred in research; the source's max(0,·) form for the credential).
- **Measurements:** per-instance-class deltas; batch averages with confidence intervals.
- **Confounders:** difficulty mismatch (the big one), instance leakage, extra attempts.
- **Edge cases:** F_before ≈ 0 (no headroom — resolution undefined; report as inapplicable); F_after > F_before (worsening — signed version records it, source version discards it).
- **Falsifies:** resolution vanishes once difficulty is balanced; or resolution is fully explained by attempt count in a budget-matched control.

### 6. Retained correction (M)
- **Definition:** the survival of the correction across a stated context boundary: M = 1 − (F_delayed − F_after)/(F_before − F_after), measured in a fresh context that does not contain the correction episode.
- **Measurements:** delayed retest at graded boundaries (new context window / new session / new environment instance / new model checkpoint); decay curves.
- **Confounders:** external memory stores (allowed — record them), context leakage, retraining between measurements.
- **Edge cases:** agent that re-derives rather than remembers (behaviourally identical — pass, per §15).
- **Falsifies:** F_delayed ≈ F_before across replications (no persistence); or persistence explained entirely by an external notes file the *task*, not the capability, provides.

### 7. Transfer / generalisation
- **Definition:** improvement on unseen instances sharing generative structure with the corrected task but differing on a pre-registered similarity ladder: S1 paraphrase → S2 novel parameter values → S3 novel composition → S4 novel domain.
- **Measurements:** improvement per ladder rung on hidden instances; control family (unrelated structure) showing no improvement.
- **Confounders:** hidden overlap between families, contamination, instance memorisation.
- **Edge cases:** agents with perfect first-contact performance (transfer measured as maintained ceiling, not improvement).
- **Falsifies:** improvement confined to S1 (paraphrase) while S2+ shows nothing → memorisation, not generalisation.

### 8. Independent verification (V)
- **Definition:** pass rate on hidden instances whose keys/answers the agent never accessed, produced by a process independent of the agent, with the agent having no control over gate mechanics, graded: agent-written tests (grade 0) < harness-written < hidden < adversarially generated < external-world consequences (grade 4).
- **Measurements:** hidden-set pass rate; independence grade; leakage audit (log all agent accesses to test material).
- **Confounders:** grader bias, harness bugs, oracle leakage through feedback channels.
- **Edge cases:** environments that are their own verifier (scoreboards) — acceptable at grade 2–3.
- **Falsifies:** pass rate collapses when hiddenness is enforced (leakage detected) or when the generator is adversarially refreshed (gaming detected).

### 9. Verified adaptive performance (the credential)
- **Definition:** the conjunction: static baseline recorded; ≥1 observed failure; G_F ≥ τ_r; retention ≥ τ_m across a stated boundary; transfer ≥ τ_t on a stated ladder rung; verification independence ≥ grade 2; all thresholds pre-registered; system-level (model + scaffolding + memory + tools pinned).
- **Measurements:** the vector [I_s, G_F, M, transfer-by-rung, independence grade, attempts-per-improvement], plus the Boolean credential.
- **Confounders:** everything in §6.8 (budgets, tools, compute, feedback, contamination) — controlled or ablated.
- **Edge cases:** zero-failure agents (credential "not testable", recorded as such); luck (addressed by replication and thresholds).
- **Falsifies the whole construct:** the credential's components fail to predict performance on novel external tasks — i.e., the "verified" label carries no information beyond the static baseline (then the trajectory gate is ceremony, and CVI's core claim fails).

---

## 12. Novel testable predictions

Beyond the source's §18 prediction, the following are derived from the CVI structure. Each states what CVI predicts, what a competing explanation predicts, the experiment, and the two decisive outcomes. All are implementable with current LLM APIs.

**P1 — Self-report is uncorrelated with verified improvement.**
- *CVI predicts:* agents' verbal claims of correction ("I have fixed the bug in my approach") are uncorrelated with subsequently measured transfer, while externally verified corrections are.
- *Competing:* self-report tracks actual competence (introspection is informative).
- *Experiment:* in every correction episode, record the agent's claim; measure later hidden transfer. Compare claim-conditional transfer rates.
- *Favours CVI:* claim-conditional transfer ≈ unconditional transfer (claims carry no signal beyond the measured correction); measured G_F predicts transfer.
- *Weakens CVI:* self-report adds predictive power over behavioural measures.

**P2 — External feedback beats equal-budget self-critique.**
- *CVI predicts:* per unit of interaction budget, agents receiving external outcome feedback improve more on a measurable task family than agents spending the same budget on self-generated critique without environment signal.
- *Competing:* attempt count/compute alone drives improvement (self-critique ≈ external feedback).
- *Experiment:* three arms — static one-shot, static multi-attempt self-critique, interactive with environment feedback — all token/budget matched (this is the core of `CVI_First_Experiment.md`).
- *Favours CVI:* interactive > self-critique ≥ one-shot on hidden transfer.
- *Weakens CVI:* self-critique ≈ interactive (feedback adds nothing).

**P3 — Context-boundary decay is predicted by verification quality.**
- *CVI predicts:* corrections demonstrated only in-context decay across a fresh-context boundary; corrections backed by external verification artefacts decay less; the decay gradient predicts later novel-task success.
- *Competing:* the context boundary is irrelevant (what's learned stays learned).
- *Experiment:* retest the same task family at graded boundaries; correlate decay with verification grade.
- *Favours CVI:* significant boundary decay in unverified arms only, and the decay gradient predicts transfer.
- *Weakens CVI:* no decay difference across arms.

**P4 — Hidden-instance drop isolates non-learning.**
- *CVI predicts:* the gap between practice-instance improvement and hidden-isomorphic-instance improvement (the "hidden drop") isolates instance-specific (memorised) "improvement", and the hidden drop predicts failure on genuinely novel tasks.
- *Competing:* practice gains transfer fully; hidden drop is noise.
- *Experiment:* measure per-agent practice gain vs hidden gain on isomorphic instances; regress against novel-family performance.
- *Favours CVI:* hidden drop > 0 and predictive.
- *Weakens CVI:* hidden drop ≈ 0 even for agents showing memorisation markers (paraphrase-only transfer).

**P5 — Induced failure is necessary for measurable learning curves.**
- *CVI predicts:* agents that never experience failure show no measurable improvement trajectory; titration-induced failure produces a learning curve whose post-failure slope predicts transfer beyond what baseline talent predicts.
- *Competing:* prior knowledge alone explains all variance; failure events add nothing.
- *Experiment:* difficulty-staircase protocol; regress transfer on [baseline talent, failure-event count, post-failure slope].
- *Favours CVI:* post-failure slope adds predictive variance beyond baseline talent.
- *Weakens CVI:* baseline talent explains everything; failure events are inert.

**P6 — Predictive validity rises with verifier independence.**
- *CVI predicts:* a "verified" label's predictive validity for novel external tasks is monotonic in the independence grade of the gate that issued it.
- *Competing:* all tests are equally valid; independence is theatre.
- *Experiment:* issue credentials at different independence grades for the same agents; measure validity on a fresh external task battery.
- *Favours CVI:* validity increases with grade.
- *Weakens CVI:* flat validity across grades.

**P7 — The three phases are dissociable.**
- *CVI predicts:* immediate correction gain, delayed retention, and transfer are partially dissociable components (e.g., systems with high immediate gain but zero retention exist), and only the retention+transfer components predict later novel-task success.
- *Competing:* a single "adaptability" factor suffices.
- *Experiment:* measure the three per agent across many agents/tasks; factor analysis + predictive regression.
- *Favours CVI:* multi-factor structure with retention+transfer predictive.
- *Weakens CVI:* one factor explains all variance.

---

## 13. Overall assessment

**Not novel in components; potentially useful and distinguishable in structure; unsupported in its strongest rhetorical form; salvageable in its modest form.**

- CVI's loop is RL/control/cybernetics; its anti-static stance is Chollet + Dynabench + DAgger; its anti-self-report stance is now empirical fact (Huang et al.); its retention/transfer demands are standard ML discipline. **As a theory of a new kind of intelligence, CVI is not supportable and should not be pursued.**
- CVI's **candidate contribution** is the *conjunction credential*: refusing the label "verified" unless action, observed failure, resolution, retention, transfer, and an agent-independent gate are all evidenced for the same agent–system on the same capability, with time treated as constitutive. That conjunction, as a *protocol*, is genuinely absent from routine agent evaluation, and its falsifiable prediction (§18) is testable tomorrow with existing APIs.
- The mathematics is metaphor (the source admits it); one piece (G_F) survives as a metric; the right formalism is a state machine plus a measurement vector, not a scalar.
- The biggest internal tensions: (a) the epistemology-vs-ontology ambiguity (resolved only by adopting the epistemology reading); (b) the failure requirement's degenerate case for near-perfect agents; (c) the naming ("causal", "intelligence") promising more than the content delivers.
- The most productive next step is the first experiment (`CVI_First_Experiment.md`), which discriminates static answer-generation from verified adaptive capability under matched budgets — an outcome with value for agent evaluation regardless of whether the "CVI" brand survives.

**One-sentence verdict:** CVI is best treated as a *proposal for how to credential learned capability* — likely useful, worth testing, and importantly different from how agents are evaluated today — rather than as a new theory of intelligence.

---

## 14. OBSERVED / INFERRED / UNRESOLVED summary

### OBSERVED — in the CVI source (quoted/paraphrased, section refs)
- The static-vs-causal distinction and 8-step pipeline (§1); the different-epistemic-status claim (§4); the loop (§5); time as trajectory (§6); F ≠ U, failure as evidence (§7); wisdom as retained improvement (§8); the external verification gate and claim≠demonstration (§9); retention/generalisation/independent re-verification requirements (§10); the type transition (§11); the state-space template and the V-gate caveat that V=0 means "not verified", not "no intelligence" (§13); the volume-collapse metaphor (§14); black-box empiricism (§15); the ten principles (§16); the working definition and its "necessary conceptual components" caveat (§17); the falsifiable prediction (§18); the Agent Runner mapping (§19); the disclaimers (§20); the one-sentence core (§21).
- The source explicitly flags itself as "a conceptual framework under development, not a validated scientific theory" (scope note) and denies that its equations are established physical laws (§20).

### OBSERVED — external sources inspected this run (all via web search)
- Chollet, *On the Measure of Intelligence*, arXiv:1911.01547 (skill-acquisition efficiency vs static skill).
- Huang et al., *LLMs Cannot Self-Correct Reasoning Yet*, arXiv:2310.01798 / ICLR 2024.
- Kiela et al., *Dynabench*, arXiv:2104.14337.
- Ross, Gordon & Bagnell, *DAgger*, arXiv:1011.0686.
- Lightman et al., *Let's Verify Step by Step*, arXiv:2305.20050 / ICLR 2024.
- Shinn et al., *Reflexion*, arXiv:2303.11366.
- Jimenez et al., *SWE-bench*, arXiv:2310.06770 / ICLR 2024; and *SWE-bench Verified*, OpenAI 2024.
- Mialon et al., *GAIA*, arXiv:2311.12983.
- Xie et al., *OSWorld*, arXiv:2404.07972.
- Lu et al., *ToolSandbox*, arXiv:2408.04682.
- Legg & Hutter, *Universal Intelligence*, arXiv:0712.3329 (via ADS record).
- Sutton & Barto, *Reinforcement Learning: An Introduction* (incompleteideas.net); Wiener, *Cybernetics* (HathiTrust); Ashby, *An Introduction to Cybernetics* (PhilPapers).
- MRAC/adaptive control: Whitaker 1958, Åström & Wittenmark 1995 (ScienceDirect topic page; Open Library).
- Parisi et al., continual learning review, arXiv:1802.07569 (PubMed).
- Rescorla & Wagner 1972; Schultz, Dayan & Montague 1997 (Semantic Scholar records).
- Popper, *Conjectures and Refutations* 1963 (PhilPapers); Dewey, *Democracy and Education* 1916 (Google Books); Piaget equilibration (SAGE entry); Ericsson et al. 1993 (APA PsycNET); enactivism (IEP entry).
- Zinkevich 2003, online convex programming (mlanthology).
- Madaan et al., *Self-Refine*, arXiv:2303.17651.
- Weng et al., LLM "self-verification", arXiv:2212.09561.
- Chen et al., *Self-Debug*, arXiv:2304.05128.
- Akyürek et al., in-context learning analysis, arXiv:2211.15661.
- Wang et al., continual learning of LLMs survey, arXiv:2404.16789.
- Packer et al., *MemGPT*, arXiv:2310.08560.
- Koh et al., *WILDS*, PMLR v139.
- Yao et al., *τ-bench*, arXiv:2406.12045.
- Wang et al., *ScienceWorld*, arXiv:2203.07540.
- Chan et al., *MLE-bench*, arXiv:2410.07095.
- Wijk et al. (METR), *RE-Bench*, arXiv:2411.15114.
- Scheurer et al. (Anthropic), prover–verifier games, arXiv:2407.13692.
- Schaeffer et al. (EleutherAI), contamination quantification (EleutherAI blog).
- Krakovna et al. (DeepMind), specification gaming blog, 2020.
- Pearl, *Causal Diagrams for Empirical Research* (zbMATH record); Schölkopf et al., *Toward Causal Representation Learning* (MPI-IS page).
- Also inspected but not used as anchors: WebArena (arXiv:2307.13854), LiveBench (arXiv:2406.19314), AgentBench (arXiv:2308.03688), TextWorld (arXiv:1806.11532), Guo et al. calibration (arXiv:1706.04599).

### INFERRED (my reasoned conclusions, clearly labelled throughout)
- CVI is an epistemology of capability claims, not a new type of intelligence (§6.10, §7).
- Every component of the loop predates CVI (§3, §4).
- The distinctive content, if any, is the mandatory conjunction credential with time as a constitutive requirement (§5).
- The scalar mathematics is unsalvageable as measurement; G_F is salvageable; a state machine + vector is the right formalism (§9).
- The failure requirement degenerates for near-perfect agents; difficulty titration is the pragmatic fix, with an inherent residual case (§6.3).
- "Causal" in CVI is the everyday/dynamical sense, not formal causal inference (§6.9).
- Huang et al. 2023 provides direct empirical support for CVI's Principle 8.

### UNRESOLVED
- Whether a CVI-style trajectory credential adds predictive validity over a good static benchmark suite (the decisive empirical question — addressed by P6 and the first experiment).
- The correct similarity metric for "altered but structurally related" (§6.5) — no general solution exists in the field.
- How long retention must last for a credential to be meaningful across real deployment timescales (§6.4).
- Whether the independence of a verification gate can be maintained against agents that optimise against it (Goodhart dynamics; §6.11).
- Whether "verified adaptive capability" and "intelligence" are the same construct under different evidence, or different constructs (§6.1, §6.7).
- Whether any zero-failure agent can ever be credentialed under CVI's letter (§6.3) — unresolved because the source does not address the degenerate case.
