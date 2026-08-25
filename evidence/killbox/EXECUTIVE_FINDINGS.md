# CVI KILLBOX — EXECUTIVE FINDINGS

**Subject:** The Causally Verified Intelligence (CVI) experiment in
`/Users/thomasfinlayson/Projects/CVI_Test_0/CVI-Pilot`, its design
(`source/CVI_First_Experiment.md`), philosophy (`source/causally_verified_
intelligence_core_philosophies.md`, §18 claim), implementation (`cvi_lab/`, `run_pilot.py`),
and both pilot runs and their sealed artifacts.

**Method:** Five independent adversarial investigators, each targeting a cluster
of attack areas, run in parallel; plus primary-agent construction of two
runnable counterexamples against the actual generator/grader. Then a
prosecution stage (strengthen the best attacks), a defence stage (attempt to
defeat each attack with real project evidence), and a methodological judge
classifying every attack. This report is the judge's synthesis.

**Allegiance:** falsification, not CVI. A negative result is a success.

---

## 1. What the experiment claims

CVI's falsifiable prediction (§18 of the philosophy, restated in the design
`CVI_First_Experiment.md:6,20`): two configurations with *approximately equal
static performance* can differ in *verified adaptive performance* on three legs
— retention across a context boundary, transfer to altered-but-related tasks,
and success on hidden verification — if one (Arm C) undergoes causal interaction
with a stateful environment (its program runs, it sees the verdict) and the
other does not (Arm S static; Arm S' equal-budget private critique with no
environment feedback). The support criterion (`§6`): **C > S' on S_tr and
S_ver** (with ≥ δ), G_F > 0 on ≥ 80% of failure episodes, retention ratio M ≥
0.7, S_ver ≥ S_tr − ε, and improvement not confined to paraphases.

## 2. What actually happened (OBSERVED)

Both pilots **do not produce C > S' ≥ S** on the outcomes the CVI claim must
move:

| leg | CVI-0 | CVI-0.1 |
|---|---|---|
| S_tr | 1.000 all arms (ceiling) | 1.000 all arms (ceiling) |
| S_ver | 0.750 all arms | 0.250 all arms |
| S_ret | 0.250 all arms (= S0) | 0.250 all arms (= S0) |
| S_post (within-session) | C 0.75, S' 1.00 | C 0.75, S' 0.25 (+S runs no interaction) |
| S0 | S 0.25, S' 1.00, C 0.25 | S 0.25, S' 1.00, C 0.25 |

Arm C corrected two of its three Phase-1 failures within the interaction session
(G_F mean 0.667) but its retention and hidden programs are byte-identical to its
baseline wrong idiom — i.e., the correction did **not** survive the context
boundary (S_ret = S0 = 0.25, S_ver = 0.25). Transfer is a ceiling with no
between-arm separation. This is precisely the design's own falsification branch
("C > S' at Phase 1 but S_ret ≈ S0 ⇒ in-context patchwork", `CVI_First_
Experiment.md:90`). The pilots themselves state "no CVI claim is made or
supported" and "LAB NEEDS REFINEMENT."

Therefore the *empirical* result does not support the CVI claim. The KILLBOX
value is assessing whether the design, **as instrumented**, could ever support it
— and the honest verdict is that it currently **cannot**, for the reasons below.

## 3. What the defence could NOT defeat (SURVIVES)

These attacks survived genuine adversarial review and would each, on their own,
let an apparent **C > S' ≥ S** appear without causal learning:

1. **Causal-contingency confound (sham-verdict gap), sharpened as a verifier-oracle / tool asymmetry.** Arm C receives a verdict
   caused by its own program. **No arm receives a non-contingent verdict.** So
   "the environment ran *my* program and it was wrong" is never compared to "I
   am told my output is wrong." A sham that replays the identical feedback text
   without executing the participant's program is informationally
   indistinguishable for these tasks (`COUNTEREXAMPLES/ce_sham_verdict_redundant.py`:
   every wrong-idiom program yields the same "FAIL on all 4" string). The causal
   link contributes nothing beyond "you are wrong." Reframed: C is given a
   compute tool that S' is denied — C has an *executor + verifier oracle* (its
   program is run and graded against the visible worked answers each round),
   while S' is told "You will receive NO test results of any kind" and its
   program is never executed (`arms.py:78-79,388-389,485-512`). This is a
   tool/compute asymmetry as much as a causal-contingency one; the two are not
   separated.

2. **S' is a damaged, inert control.** S''s three critique rounds are
   byte-identical no-ops; its "correct baseline → wrong critique" pattern is
   actually two **independent** bimodal draws, because `run_arm_sprime_pre`
   (`arms.py:378-406`) runs the baseline in its own session and then starts a
   *fresh* critique session whose round_0 is a new one-shot attempt — the
   baseline programs are never re-presented for critique. So S' never actually
   self-corrected its own work, does not measure "equal-budget private
   reasoning," and its low S_post reflects the loop's inertness + a bimodal
   re-draw rather than a controlled handicap. A future C > S' is trivially
   explained by S''s incapacity.

3. **No-feedback derivability of the answers.** The Family-A (and Family-C)
   answers are derivable from the public worked examples that are injected into
   *every* arm's prompt. `ce_no_feedback_solve.py` reaches hidden_score 1.0 on all
   four Family-A tasks with no feedback; S' already scored S0 = 1.00 at baseline
   with zero feedback. The verdict is a non-load-bearing trigger, not the source
   of the solved mapping.

4. **Broken baseline matching.** §18's premise "approximately equal static
   performance" is not met: single-shot S0 is bimodal (0.25 / 1.00 / 0.25 on
   byte-identical, hash-enforced prompts), so the arms are not matched.

5. **Broken retention metric M.** `metrics.py:129-135` M returns `null` for C's
   decisive no-retention case and a false `1.0` pass for a zero-learning arm; the
   design's M ≥ 0.7 gate is not meaningful. (Verified numerically: `S0=S_post=
   S_ret=0.3` ⇒ M=1.0, a false pass; `S0=0.3,S_post=0.8,S_ret=0.8` ⇒ M=6.0,
   unbounded; C's corrected-then-lost pilot case ⇒ M=null.) Relatedly, the §6.2
   G_F episode gate ("G_F > 0 on ≥80% of failure episodes") is **not met** — C
   resolved 2/3 failing tasks (66.7%) — yet the displayed "G_F mean 0.667" is a
   mean magnitude that reads as moderate success, and S′'s −0.75 regression is
   hidden by the round-0 anchor + `max(0,..)` clamp.

6. **Transfer ceiling + uninformative hidden verification.** S_tr = 1.00 for all
   arms (S solves the novel-composition S3 rungs with zero interaction), and
   Family C re-issues Family-A templates (same recipes/spec/purity traps with
   fresh cases), so S_ver = S0 = S_ret = 0.25 re-tests memorised templates, not
   generalised causal structure.

Also surviving: token parity is not actually enforced (S ran with a cold prompt
cache at 820 baseline input tokens vs 52 for S'/C on byte-identical prompts,
then S' vs C interaction tokens also diverge), the gaming index is
vacuous because public/hidden cases are drawn i.i.d., calibration selection is
enumeration-order theater on recipe-degenerate difficulty, and treatment framing
(C "will receive outcomes/revise" vs S' "private scratchpad/no results/judge
your own work") primes different engagement independent of feedback. Compounding
all of these, the **operator semantics and the exact trap solution are disclosed
verbatim in every arm's system prompt** (`ordermachine.py:718-719` gives the
`(MIRROR a) + 1` structure that is the canonical answer for the flagship hard
task; `arms.py:221-227` injects it unconditionally), so the "repair" tasks measure
spec comprehension rather than causal inference from interaction.

## 4. What the defence DID defeat (DEFEATED)

The firewall held: hidden tests/keys/seeds/programs are inaccessible to the
participant (module-boundary, public_view, hostile-participant, and feedback-
content tests all pass; 117/117). Phase-0 baseline prompts are byte/hash-
identical across arms with no treatment labels. Task instances are identical
across arms and calibration/official seeds disjoint. Family-C generation is
gated until after interaction. Arm S receives no feedback; Arm C receives only
permitted feedback. Runaway call budget protected. These controls are real and
rule out the corresponding attacks.

## 5. Counterexamples produced

- `COUNTEREXAMPLES/ce_no_feedback_solve.py` — a no-feedback solver reaches
  hidden_score 1.0 on all four Family-A tasks (beating Arm C's actual 0.75).
- `COUNTEREXAMPLES/ce_sham_verdict_redundant.py` — shows the causal verdict is a
  fixed string over the whole wrong-idiom class, so a non-contingent sham
  reproduces C's feedback.

## 6. What a valid test requires

The next decisive experiment adds two arms: a **non-contingent-verdict sham**
(C with the feedback tape decoupled from its own program) and a **best-of-N
private-reasoning control** (S' without the damaging critique loop), and forces
transfer/hidden headroom and a corrected retention metric (see
NEXT_DECISIVE_EXPERIMENT.md and PROPOSED_CONTROLS.md).

---

## FINAL JUDGMENT

**BROKEN.**

A simpler alternative mechanism can plausibly reproduce the key predicted result
(C > S' ≥ S on transfer and hidden verification) and is **not currently
controlled** by this experimental design. The most direct uncontrolled mechanism
is the combination of (a) the absence of any non-causal-contingency control, so
"the environment ran my program" is never contrasted with "I am told I am
wrong," and (b) a damaged, inert S' control that mechanically lowers S' and so
manufactures an apparent C advantage; compounded by (c) no-feedback derivability
of the answers, which means the solved mapping is already present in every arm's
prompt and (d) broken baseline matching, which leaves the §18 premise unmet.

This classification is **not** a claim that the CVI mechanism is false, nor that
it cannot be supported by a better-controlled study. It is the rigorous, evidence-
grounded conclusion that **the experiment as currently instrumented cannot
produce a C > S' ≥ S result on the legs the CVI claim must move that would be
attributable to causally contingent learning** — because each plausible
simpler alternative is uncontrolled today. The pilot's own data already fall in
the design's falsification branch (no retention, no transfer separation), and the
fortitude of this KILLBOX is precisely that one can build a no-feedback arm and a
sham arm that match or exceed the C treatment on the very tasks where the CVI
claim would have to show a causal advantage.

**Why BROKEN rather than "SURVIVES, BUT...".** The gentler reading ("the intended
interpretation remains plausible but alternatives are unresolved") is defensible,
and the honest caveat is that the two pilots have not *reported* a C > S' ≥ S
result to explain. BROKEN is nonetheless the correct classification for the
**design's current validity as a discriminative test of CVI**: the surviving
attacks are not merely *unresolved* — some are *demonstrated* (S' is an inert
broken control; the answers are provably no-feedback-derivable via the runnable
counterexample; baseline matching provably fails on identical prompts; the
retention metric is provably algebraically wrong), and a simpler mechanism
(S' incapacity + no-feedback derivability + token non-parity, un-separated from
contingency) can *plausibly and measurably* manufacture an apparent C > S' ≥ S.
That is the definition of BROKEN: a simpler alternative that plausibly reproduces
the key predicted result and is not currently controlled.

A properly controlled rerun (decisive sham arm + best-of-N S' + non-saturating
transfer + corrected M + genuinely novel Family C) could re-establish the
design's validity; the current implementation, unmodified, does not.
