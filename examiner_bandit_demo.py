"""
Examiner-regret bandit demo.
Three panels = the paper's three results:
  A: Proposition 1  -- self-report alone certifies nothing
  B: Lemma 1        -- soundness turns rho_t into a certificate (coverable world)
  C: Theorem 1      -- no free self-evaluation in a big world
Author: demo for the examiner-regret position paper.
"""
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(0)


# --- bandit world: one "special" arm pays 1/2 + eps, the rest pay 1/2 ---
def make_world(N, eps, special):
    mu = np.full(N, 0.5)
    mu[special] = 0.5 + eps
    return mu


def pull(mu, i):
    """Bernoulli reward from arm i."""
    return float(rng.random() < mu[i])


# --- learner (UCB or fixed) + examiner that reads V_hi / V_lo off the same counters ---
def run(N, T, eps, special, examiner="sound", policy="ucb", fixed_arm=1):
    mu = make_world(N, eps, special)
    n = np.zeros(N)          # pull counts
    s = np.zeros(N)          # reward sums
    mu_star = mu.max()       # best TRUE mean (used only to SCORE regret, never by the agent)

    rho, true_reg = [], []
    for t in range(1, T + 1):
        muhat = np.divide(s, n, out=np.full(N, 0.5), where=n > 0)
        c = np.sqrt(2 * np.log(t + 1) / np.maximum(n, 1))   # confidence width
        c[n == 0] = 1.0                                     # unpulled = max uncertainty

        # learner picks the action
        a = int(np.argmax(muhat + c)) if policy == "ucb" else fixed_arm

        # examiner's two numbers, both from the SAME counters
        if examiner == "sound":
            V_hi = float(np.max(muhat + c))                 # optimism over ALL arms (incl. unseen)
            V_lo = muhat[a] - c[a]                           # pessimistic floor on played arm
        elif examiner == "biased":                          # trusts "all arms share one mean"
            seen = n > 0
            V_hi = float(np.max(muhat[seen])) if seen.any() else 0.5  # NO optimism for unseen
            V_lo = muhat[a]                                  # NO pessimism: trusts its estimate
        elif examiner == "zero":
            V_hi = V_lo = 0.0                                # empty all-zero examiner (Prop 1)

        rho.append(max(V_hi - V_lo, 0.0))
        true_reg.append(mu_star - mu[a])                    # real per-step regret

        r = pull(mu, a)
        n[a] += 1
        s[a] += r
    return np.array(rho), np.array(true_reg)


fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))

# ---- Panel A: Proposition 1 -- two agents, identical zero report, different truth ----
N, T, eps = 5, 3000, 0.2
rho_zero, treg_good = run(N, T, eps, special=0, examiner="zero", policy="ucb")    # good learner
_,        treg_bad  = run(N, T, eps, special=0, examiner="zero", policy="fixed")  # bad learner
ax[0].plot(np.cumsum(rho_zero),  label=r"both agents' self-report $\sum\rho_t=0$", lw=2)
ax[0].plot(np.cumsum(treg_good), label="true regret, good (UCB) learner", lw=2)
ax[0].plot(np.cumsum(treg_bad),  label="true regret, bad (fixed-arm) learner", lw=2, ls="--")
ax[0].set_title("A. Prop 1: self-report certifies nothing")
ax[0].set_xlabel("step t"); ax[0].set_ylabel("cumulative")
ax[0].legend(fontsize=8)

# ---- Panel B: Lemma 1 -- coverable world, rho_t upper-bounds true regret ----
N, T, eps = 5, 3000, 0.2
rho_s, treg_s = run(N, T, eps, special=0, examiner="sound")
ax[1].plot(np.cumsum(rho_s),  label=r"certificate $\sum\rho_t$", lw=2)
ax[1].plot(np.cumsum(treg_s), label="true within-cap regret", lw=2)
ax[1].set_title("B. Lemma 1: sound $\\rho_t$ bounds real regret (coverable)")
ax[1].set_xlabel("step t"); ax[1].legend(fontsize=8)

# ---- Panel C: Theorem 1 -- big world (T < N), special arm hides ----
N, T, eps = 400, 300, 0.2          # horizon < #arms => cannot cover
special = 399                       # special arm sits beyond the horizon's reach
rho_sound,  treg_c = run(N, T, eps, special=special, examiner="sound")
rho_biased, _      = run(N, T, eps, special=special, examiner="biased")
ax[2].plot(np.cumsum(treg_c),     label="true regret $\\approx \\epsilon T$", lw=2, color="k")
ax[2].plot(np.cumsum(rho_sound),  label=r"sound $\sum\rho_t$ (honest, $\geq\epsilon T$)", lw=2)
ax[2].plot(np.cumsum(rho_biased), label=r"unsound $\sum\rho_t$ (lies $\to 0$)", lw=2, ls="--")
ax[2].set_title("C. Thm 1: big world -- unsound examiner lies")
ax[2].set_xlabel("step t"); ax[2].legend(fontsize=8)

plt.tight_layout()
plt.savefig("examiner_bandit_demo.png", dpi=140)
plt.savefig("examiner_bandit_demo.pdf")

# numeric summary printed for the walk-through
print(f"A: zero-examiner final self-report = {np.cumsum(rho_zero)[-1]:.2f} "
      f"(claims perfect); good-learner true regret = {np.cumsum(treg_good)[-1]:.2f}")
print(f"B: certificate sum_rho = {np.cumsum(rho_s)[-1]:.1f}  >=  true regret = {np.cumsum(treg_s)[-1]:.1f}  "
      f"(bound holds: {np.cumsum(rho_s)[-1] >= np.cumsum(treg_s)[-1]})")
print(f"C: true regret = {np.cumsum(treg_c)[-1]:.1f} | sound rho = {np.cumsum(rho_sound)[-1]:.1f} "
      f"(tracks truth) | unsound rho = {np.cumsum(rho_biased)[-1]:.1f} (false 'done')")
