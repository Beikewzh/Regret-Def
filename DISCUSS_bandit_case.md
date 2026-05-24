# Discussion memo: the bandit as the worked case

*For talking through with my partner. Goal: fill the section currently marked
"Pls show a case, e.g. bandit related to the definition, and how could we use it" in
`main.tex`. Everything below is checked against our Definitions 1–4 and Results
(Prop 1 / Lemma 1 / Theorem 1), and against the numbers from `examiner_bandit_demo.py`.*

---

## The one-sentence argument

In the simplest world that has no state — a multi-armed bandit — our four definitions
turn into plain arithmetic on arm-pull counts, our three results turn into three
pictures, and the whole "the examiner must out-learn the learner and stay honest"
story can be read directly off who-pulled-what. That is exactly why the bandit is the
right first example: it is concrete enough to compute by hand, and it is the standard
sanity check any theorist will run on a new definition.

## Why a bandit, specifically

A bandit is our general stream with the state collapsed to a single point and the
look-ahead set to one step ($|\mathcal{S}|=1$, $H=1$). This matters for two reasons.
First, if our definitions did *not* reduce cleanly to the textbook bandit here, that
would be evidence the definitions are wrong — the special-case reduction is the
cheapest test we can run. They do reduce cleanly. Second, the bandit is where the two
gaps in Theorem 1 (coverage and bias) are easiest to see, because "an arm you never
pulled" is the most transparent possible version of "a behaviour you never tried."

## The setting (plain, then formal)

Plain: a row of slot machines. Every machine pays a fair coin-flip on average,
**except one** "special" machine that pays a little better. We do not know which one.
We pull levers one at a time and want to end up on the good machine.

Formal: $N$ arms; pulling arm $i$ returns a reward $r \in \{0,1\}$ with mean $\mu_i$,
so $R_{\max}=1$. All means equal $\tfrac12$ except one special arm with
$\mu_{i^\star} = \tfrac12 + \epsilon$. The means are unknown; we act on a single
never-resetting stream.

## How each definition becomes bandit arithmetic

This is the "linked with the bandit math" part — the table is the heart of the memo.

| Paper object | Bandit instance | One-line meaning |
|---|---|---|
| **Def 1.** value $f^{\pi}_t$ | $\mu_i$ for the policy "pull arm $i$" | with $H=1$, value of a behaviour *is* the arm mean |
| **Def 2.** within-capacity optimum $f^{K_L}_t$ | $\mu^\star = \tfrac12+\epsilon$ (if all arms representable) | the best machine we could name |
| **Def 2.** structural gap $\Delta^{\mathrm{str}}_t$ | $0$ when all arms representable | nothing is lost to being "too small to express" here |
| **Def 3.** learner $\mathcal{L}$ | the UCB rule that picks the arm | acts; learns only the arm it plays |
| **Def 3.** examiner $\mathcal{E}$ | the confidence-bound calculator | reports a ceiling and a floor |
| **Def 3.** aspiration $V^{\mathrm{hi}}_t$ | $\max_i (\hat\mu_i + c_i)$ | best any arm *could* be, given the data |
| **Def 3.** guarantee $V^{\mathrm{lo}}_t$ | $\hat\mu_{a_t} - c_{a_t}$ | safe floor on the arm we played |
| **Def 3.** inductive bias $\mathcal{M}_E$ | the concentration rule (Hoeffding) | the assumption that lets $c_i$ shrink with data |
| **Def 4.** examiner regret $\rho_t$ | $\max_i(\hat\mu_i+c_i) - (\hat\mu_{a_t}-c_{a_t})$ | the confidence *width* = self-graded room to improve |

Here $\hat\mu_i$ is the empirical mean of arm $i$, $n_i$ its pull count, and
$c_i = \sqrt{2\ln(t)/n_i}$ the confidence width (with $c_i$ at its maximum for an arm
never pulled). Note $\rho_t$ uses only counts and means — it never looks at the true
$\mu$ or at $\mu^\star$, exactly as Definition 4 requires.

**Sanity check (the reason we trust the reduction).** With $|\mathcal{S}|=1$ this is
literally the classical bandit: the regret $\sum_t (f^{K_L}_t - f^{\pi_t}_t)$ becomes
$\sum_t (\mu^\star - \mu_{a_t})$, the standard pseudo-regret of Lai–Robbins / Auer, and
$\sum_t \rho_t$ is the familiar UCB confidence-width sum of order
$O(\sqrt{N T \log T})$. So our objects are not a new invention bolted onto the bandit;
they are the bandit's own quantities, renamed as "examiner" objects. *[verified by
reduction; matches Auer et al. 2002]*

## One subtlety worth a sentence in the paper

Definition 2 measures capacity in **bits** (can we *represent* the policy?), while
Theorem 1's coverage gap is about **time** (can we *try* it within horizon $T$?). In
the bandit they look similar but they are different resources. In our Theorem 1
construction the learner *can represent* every arm (so $f^{K_L}=\mu^\star$ and
$\Delta^{\mathrm{str}}=0$), yet still cannot *try* them all when $T<N$. We should add
one clause distinguishing "too small to express" from "too rushed to explore," or a
reader will conflate them.

## Soundness, in the bandit — and where "stay honest" lives

Soundness (Def 5) asks two things, both of which Hoeffding gives with high
probability: the floor is real, $\hat\mu_{a_t} - c_{a_t} \le \mu_{a_t}$; and the
ceiling is real, $\max_i(\hat\mu_i + c_i) \ge \mu^\star$. The slack $\delta_t$ is just
the Hoeffding failure margin, which shrinks as pull counts grow.

The mechanism behind "the examiner stays honest" is one line: **an arm that has never
been pulled keeps its confidence width $c_i$ at maximum**, so its optimistic index
stays high, so the ceiling $V^{\mathrm{hi}}_t$ refuses to drop. The examiner is
*structurally forbidden* from claiming "no room to improve" about a machine it has not
inspected. A dishonest examiner is precisely one that throws this away — assumes the
unseen arm is ordinary and lets the ceiling fall.

## The three results as three pictures

(Numbers below are the actual output of the demo; figure is
`examiner_bandit_demo.png` / `.pdf`, three panels.)

**Proposition 1 — a self-report alone certifies nothing.** Give both a good learner
(UCB) and a bad learner (always pull a fixed mediocre arm) the same trivial examiner
that reports $\rho_t \equiv 0$. Both "self-report" a perfect score, yet the good
learner's true regret levels off near $154$ while the bad learner's climbs linearly to
$\sim 600$. Identical report, opposite reality. *(Panel A.)*

**Lemma 1 — soundness turns the report into a certificate.** Now make the world
coverable ($N=5$, $T=3000$) and use the real UCB/LCB examiner. The certificate
$\sum_t \rho_t \approx 1354$ sits **above** the true regret $\approx 147$ for the whole
run: a valid (if loose) ceiling on the regret we can still remove. The looseness is
honest — $\rho_t$ measures the gap between the *best* optimistic index and the floor of
the *played* arm, which is wider than the instantaneous regret. *(Panel B.)*

**Theorem 1 — no free self-evaluation in a big world.** Make the world bigger than the
horizon ($N=400$, $T=300$) and hide the special arm beyond reach. True regret is
linear, $\epsilon T = 60$. The **sound** examiner keeps reporting a large
$\sum\rho_t \approx 878$ — honestly saying "lots of room left, I have not covered the
world." The **biased** examiner (assumes all arms share one mean) collapses to
$\sum\rho_t \approx 49$, *below* the true regret — a confident "I'm basically done"
that is simply false. The collapse is the lie the theorem predicts, and it shows up as
a self-report that breaks the Lemma-1 certificate exactly because the examiner is no
longer sound. *(Panel C.)*

## How we could use it (the partner's "how could we use it")

Three concrete uses, all available without ever knowing $V^\star$:

1. **Monitor.** Plot $\rho_t$ online for a deployed agent (a recommender, a robot). A
   sound, shrinking $\rho_t$ means it is still improving; a small $\rho_t$ that is *not*
   backed by coverage is the warning sign of unearned confidence.
2. **Compare.** Run two algorithms on the same stream and compare their $\rho_t$
   trajectories. The one whose self-graded room-to-improve shrinks faster is nearer its
   own capacity-constrained optimum — a fair comparison with no external optimum needed.
3. **Audit.** Because soundness is calibration on what has been seen, a low $\rho_t$ is
   trustworthy precisely on the covered region. Theorem 1 tells the operator when no
   audit is possible, so apparent convergence should trigger more exploration or an
   external test rather than trust.

## Claim–evidence–status map

- Claim: the four definitions reduce to standard bandit quantities. | Evidence:
  table above + Lai–Robbins/Auer reduction. | Status: **supported (by reduction).**
- Claim: a sound examiner's $\rho_t$ upper-bounds reducible regret. | Evidence:
  Lemma 1 telescoping + Panel B ($1354 \ge 147$). | Status: **supported.**
- Claim: in a big world a confident self-report can be false. | Evidence: Theorem 1 +
  Panel C (unsound $49 <$ true $60$). | Status: **supported.**
- Claim: this matches the classical UCB rate when coverable. | Evidence: $\sum\rho_t =
  O(\sqrt{NT\log T})$. | Status: **cited (Auer et al. 2002), illustrated.**

## Open questions to settle with my partner

1. **Lead with which bandit?** Suggest: lead with the *coverable* one (Lemma 1 works,
   feels constructive), then *break* it with the big-world one (Theorem 1). This keeps
   the polarity constructive, which the critique memo argued for.
2. **Clip $V^{\mathrm{lo}}$ at $0$?** Letting the floor go negative makes Panel B's
   certificate look loose. Clipping tightens the picture but slightly changes the
   story. Which do we prefer for the figure?
3. **Bits vs time.** Do we add the one clause distinguishing representational capacity
   ($K_L$) from horizon coverage ($T<N$), or fold it into a footnote?
4. **Under-capacity illustration.** Limitation L3 says we never show
   $\Delta^{\mathrm{str}}>0$. We could add a bandit variant where some arms are *not
   representable* to make $\Delta^{\mathrm{str}}$ visible. Worth the space?

## Why this structure

- Argument first, then the table, then the pictures — a reader can stop after the
  table and still have the link.
- Numbers are the demo's real output, so the figure and the prose cannot drift apart.
- Open questions are separated out so the partner discussion has a clear agenda.
