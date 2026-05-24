# Critique: "Examiner Regret" position paper, read through a Sutton / Precup lens

Short version: the *setting* is exactly what the big-world / continual-RL community
is reaching for, but the *claim as currently headlined* is the part they will not buy.
The fix is a polarity flip, not a new result.

## Is the claim good?

**The setup is good and on-trend.** Dropping the external yardstick $V^\*$, taking the
agent's-eye view, judging a bounded agent against its own within-capacity optimum
$f^{K_L}$ — this is squarely aligned with the big-world hypothesis (Javed & Sutton),
the *Three Dogmas* critique (Abel et al.: shed the environment-spotlight and the
"learning = finding a fixed solution" dogmas), and the CRL definition (Abel et al.
2023). A reviewer from that camp nods along through Section 1.

**The headline claim is where they stop nodding.** Two problems.

1. **The theorem reads as relabeled no-free-lunch.** Theorem 1 is a two-point bandit
   lower bound: a *coverage gap* ("you can't know about an arm you never pulled") and a
   *bias gap* ("you need a model class that contains the truth"). A theorist recognizes
   this instantly as the classical *explore-or-assume* dichotomy and the realizability
   requirement. As a *headline*, "no free self-evaluation" therefore lands as old wine:
   the impossibility direction is genuinely not new, and the paper currently leans its
   whole weight on it.

2. **The corollary "the examiner must be the more strongly *biased* module" is the
   weakest sentence in the paper, and it is also your stated worry.** "Bias" reads as a
   liability, and your own Theorem 1 says the bias is *unverifiable*. So the headline
   message reduces to: *the load-bearing module must rely on something that can be wrong
   and that you can't check.* That is defeatist, and it is the opposite of what the OaK
   / Alberta-Plan audience wants to hear, which is a story about an agent that **keeps
   getting better forever**.

So: good bones, wrong polarity. The paper sells the *price* and hides the *product*.

## What Sutton & Precup would actually buy

Flip it to a **constructive, architectural** thesis:

> In a big world no policy can be optimal and learning never stops, so the only honest
> internal measure of progress is a self-evaluation — and that self-evaluation must
> itself be a **continually-learning predictive model that out-learns the policy it
> grades.** Evaluation is not a fixed yardstick; it is the fastest-learning part of the
> agent.

This is a claim that camp *wants* to be true, and it is defensible. The impossibility
result then becomes the supporting "and here is the price," not the headline.

## The crux you flagged: how is the examiner "better than the learner" in practice?

This is the make-or-break, and the current draft asserts it ("more biased," "more
compute") without a concrete, non-circular mechanism. The circularity a reviewer will
pounce on: *the examiner sees the same stream as the learner, so how can it know more?*
And: *the thing that makes it "better" (bias) is exactly what your theorem says can't be
trusted.*

There are **three concrete senses** in which the examiner genuinely out-learns the
learner on the *same* stream, all grounded in this audience's own machinery:

1. **It learns off-policy about policies the learner never executes.** The learner only
   learns about the one policy it runs. The examiner learns a *family* of value
   predictions — General Value Functions / Horde, with off-policy TD and recognizers
   (Sutton et al. 2011; Precup, Sutton & Dasgupta 2001). Predicting the value of untried
   policies is *exactly* what judging "could I have done better?" requires, and GVFs are
   exactly the tool. This is the rigorous, non-circular sense of "more informed from the
   same data."

2. **Asymmetric capacity and a slower timescale.** A critic may carry privileged
   information and more capacity than the actor (asymmetric actor-critic, Pinto et al.
   2018), and in two-timescale actor-critic the critic is driven to track *faster* than
   the policy it evaluates (Konda & Tsitsiklis 2000). So "examiner ahead of learner" is
   not a wish — it is a standard, analyzed design.

3. **It is trained to a calibration / soundness target.** "Is the examiner learning?"
   becomes operational: its calibrated slack $\delta_t$ shrinks on the *covered* region
   while it honestly *widens* $\rho_t$ off-coverage. A **sound-and-shrinking $\rho_t$ =
   real progress; a small-but-unsound $\rho_t$ = unearned confidence**, and Theorem 1
   tells you precisely which regime you are in.

Together these turn "the examiner is better" from an assertion into a design rule with a
test attached.

## Honesty / positioning gaps to close

- **Cite and distinguish model-value inconsistency** (Filos et al. 2022): the gap
  between two value estimates as an epistemic-uncertainty signal is a close relative of
  $\rho_t$. Your novelty is the *certificate* framing (soundness) plus the continual
  *out-learning* architecture — not the gap-as-uncertainty idea itself. Say so.
- **Own the no-free-lunch resemblance explicitly.** One sentence: "the impossibility
  direction is the classical explore-or-assume dichotomy; our contribution is what it
  implies for *how to build the examiner*, not the dichotomy itself." Pre-empting the
  objection disarms it.
- **Drop "more biased" as the headline word.** Reframe bias as the ordinary inductive
  generalization any learner needs; the differentiator is *out-learning* (the three
  senses above), of which a prior is just one instance.

## What stays exactly as is

The math. Proposition 1, the bridge Lemma, and Theorem 1 are correct and survive intact
— the rewrite re-pitches the prose around them, it does not touch the proved statements.
Status tags ([proved]/[cited]/[heuristic]/[GAP]) and the honest limitations stay.

## Net

Same length, same theorems, flipped polarity: lead with "evaluation must out-learn
action," ground the examiner in GVFs / off-policy prediction, give the three concrete
out-learning mechanisms, demote the impossibility to "the price," and pre-empt the
no-free-lunch read. That is the version this audience buys.

## Originality: how original is the theory, honestly?

Verdict: **moderately original as a position; not original as theory.** Be upfront
about this in the paper rather than overclaiming, because a sharp reviewer will see
through inflation immediately.

What is **not** new (and the paper now says so explicitly):
- The impossibility direction. Gaps (i) coverage and (ii) realizability are the
  classical explore-or-assume dichotomy and the realizability requirement, priced for
  decades (Lai & Robbins 1985; Kearns & Singh 2002; Brafman & Tennenholtz 2002; Azar
  et al. 2017). Theorem 1 is a two-point construction in that tradition.
- The gap-of-two-value-estimates as an uncertainty signal. That is UCB width, ensemble
  disagreement (Osband et al. 2016), and model-value inconsistency (Filos et al. 2022).
- Judging a bounded agent against its own capacity. Capacity-limited Bayesian RL
  (Arumugam & Van Roy 2024), bounded optimality (Simon 1955; Russell & Subramanian
  1995), resource-rational analysis (Lieder & Griffiths 2020).

What **is** the contribution (modest but real, and defensible):
1. Making the evaluator an *explicit, separate, capacity-bounded module* and asking the
   question nobody states this way: what is its self-report worth?
2. The clean thesis that the self-report *certifies nothing* without soundness, and that
   soundness turns it into a certificate (Prop. 1 + bridge Lemma 1).
3. The design principle **"evaluation must out-learn action"** — that the evaluator must
   be the strictly-more-learning module — grounded in off-policy / GVF / asymmetric-
   critic machinery. This synthesis-as-principle is the freshest part. It is a reframing,
   not a new theorem.
4. Examiner regret as a unit-ful, $V^*$-free online progress-and-comparison signal for
   CRL.

The honest framing for the paper: this is a *position / synthesis* paper. Its originality
is the framing, the principle, and the coherent stance assembled from existing pieces,
not new mathematics. That is a legitimate contribution for a workshop position paper
**provided** the framing is compelling and the borrowed parts are credited — which the
current draft now does (Limitations L1–L9, and the "what is and is not new" passage in
Section 5).

## Math / logic consistency check

Checked end to end and internally consistent. Definitions 1–4 are well-posed
($f^{K_L}\le f^{*}$ so $\Delta^{\mathrm{str}}_t\ge 0$; $\rho_t\ge 0$). Proposition 1 is a
valid one-line counterexample. Lemma 1's telescoping decomposition is exact and each
term is bounded as claimed by the two soundness inequalities ($f^{K_L}_t-V^{\mathrm{hi}}
\le\delta_t$ from the ceiling, $V^{\mathrm{lo}}-f^{\pi_t}_t\le 0$ from the floor), so the
inequality and its global version hold. Theorem 1's coverage gap is a correct
indistinguishability (two worlds differing only on an unpulled arm yield identical
histories, hence identical examiner outputs, forcing $\rho_t\ge\epsilon-\delta_t$ under
soundness); the bias gap is the matching realizability argument. All proved statements
are tagged [proved]; the out-learning claim is honestly tagged [GAP]/design-argument
(L5), not a theorem. No contradictions were introduced by the rewrite — the proofs are
unchanged from the original.
