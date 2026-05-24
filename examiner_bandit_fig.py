"""
Illustrative figure for the examiner-regret position paper. Three panels, all with
NO external optimum visible to the agent (rho_t uses only counts/means; mu, mu* used
only to SCORE, never by the agent).

  (A) Enough budget (coverable, N<=T): the slack vanishes and examiner regret shrinks
      to zero ALONGSIDE the true regret. It is an upper bound, so it does not equal the
      true regret, but it becomes a tight, vanishing certificate.

  (B) Big world (T<N): the special arm is never reached. Examiner regret stays a valid
      bound on the true (static) regret, while the plug-in estimate of static regret
      (empirical best arm minus played arm) underestimates it: a false "done".

  (C) Non-stationary: the special arm switches. Examiner regret stays a valid bound on
      the true (dynamic) regret, while the windowed plug-in estimate of dynamic regret
      again underestimates it.
"""
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(1)


def confidence(t, n, window=None):
    base = np.log(max(t, 2)) if window is None else np.log(min(t, window) + 1)
    c = np.sqrt(2 * base / np.maximum(n, 1))
    c[n == 0] = 1.0
    return c


def run_bandit(N, T, eps, special, examiner):
    """Stationary bandit; returns per-step rho and true regret."""
    mu = np.full(N, 0.5); mu[special] = 0.5 + eps
    mu_star = mu.max()
    n = np.zeros(N); s = np.zeros(N)
    rho, treg = [], []
    for t in range(1, T + 1):
        muhat = np.divide(s, n, out=np.full(N, 0.5), where=n > 0)
        c = confidence(t, n)
        a = int(np.argmax(muhat + c))
        if examiner == "sound":
            V_hi = float(np.max(muhat + c)); V_lo = muhat[a] - c[a]
        else:  # plug-in static regret: empirical best minus played, no uncertainty
            seen = n > 0
            V_hi = float(np.max(muhat[seen])) if seen.any() else 0.5
            V_lo = muhat[a]
        rho.append(max(V_hi - V_lo, 0.0)); treg.append(mu_star - mu[a])
        r = float(rng.random() < mu[a]); n[a] += 1; s[a] += r
    return np.array(rho), np.array(treg)


def run_nonstat(N, T, eps, tau, W, examiner):
    """Non-stationary bandit with sliding-window estimates; per-step rho, true regret."""
    hist = []; rho, treg = [], []; special = 0
    for t in range(1, T + 1):
        if t % tau == 1 and t > 1:
            special = (special + 3) % N
        mu = np.full(N, 0.5); mu[special] = 0.5 + eps
        win = hist[-W:]
        n = np.zeros(N); s = np.zeros(N)
        for (ai, ri) in win:
            n[ai] += 1; s[ai] += ri
        muhat = np.divide(s, n, out=np.full(N, 0.5), where=n > 0)
        c = confidence(t, n, window=W)
        a = int(np.argmax(muhat + c))
        if examiner == "sound":
            V_hi = float(np.max(muhat + c)); V_lo = muhat[a] - c[a]
        else:  # plug-in dynamic regret: windowed empirical best minus played
            seen = n > 0
            V_hi = float(np.max(muhat[seen])) if seen.any() else 0.5
            V_lo = muhat[a]
        rho.append(max(V_hi - V_lo, 0.0)); treg.append(mu.max() - mu[a])
        r = float(rng.random() < mu[a]); hist.append((a, r))
    return np.array(rho), np.array(treg)


def smooth(x, k=80):
    return np.convolve(x, np.ones(k) / k, mode="valid")


fig, ax = plt.subplots(1, 3, figsize=(16, 4))

# ---- Panel A: enough budget (coverable), per-step, both vanish ----
rho_s, treg = run_bandit(N=10, T=4000, eps=0.3, special=0, examiner="sound")
xs = np.arange(len(smooth(rho_s)))
ax[0].plot(xs, smooth(treg), "k", lw=2, label="true regret")
ax[0].plot(xs, smooth(rho_s), lw=2, label=r"examiner regret $\rho_t$ (ours)")
ax[0].set_title(r"(A) Enough budget ($N\leq T$): both vanish")
ax[0].set_xlabel("step $t$"); ax[0].set_ylabel(r"per-step regret")
ax[0].legend(fontsize=8, loc="upper right")

# ---- Panel B: big world, cumulative ----
rho_s, treg = run_bandit(N=400, T=300, eps=0.2, special=399, examiner="sound")
rho_b, _ = run_bandit(N=400, T=300, eps=0.2, special=399, examiner="biased")
ax[1].plot(np.cumsum(treg), "k", lw=2, label=r"true (static) regret $\approx\epsilon T$")
ax[1].plot(np.cumsum(rho_s), lw=2, label=r"examiner regret $\sum\rho_t$ (valid bound)")
ax[1].plot(np.cumsum(rho_b), "--", lw=2, label=r"plug-in static regret (underestimates)")
ax[1].set_title("(B) Big world ($T<N$): the unreached arm")
ax[1].set_xlabel("step $t$"); ax[1].set_ylabel("cumulative")
ax[1].legend(fontsize=8, loc="upper left")

# ---- Panel C: non-stationary, cumulative ----
N, T, eps, tau, W = 12, 4000, 0.35, 800, 300
rho_s, treg = run_nonstat(N, T, eps, tau, W, examiner="sound")
rho_b, _ = run_nonstat(N, T, eps, tau, W, examiner="biased")
ax[2].plot(np.cumsum(treg), "k", lw=2, label="true (dynamic) regret")
ax[2].plot(np.cumsum(rho_s), lw=2, label=r"examiner regret $\sum\rho_t$ (valid bound)")
ax[2].plot(np.cumsum(rho_b), "--", lw=2, label=r"plug-in dynamic regret (underestimates)")
for k in range(tau, T, tau):
    ax[2].axvline(k, color="gray", ls=":", lw=0.8)
ax[2].set_title("(C) Non-stationary: arm switches at dotted lines")
ax[2].set_xlabel("step $t$"); ax[2].set_ylabel("cumulative")
ax[2].legend(fontsize=8, loc="upper left")

plt.tight_layout()
plt.savefig("examiner_bandit_fig.pdf")
plt.savefig("examiner_bandit_fig.png", dpi=140)
print("panel A final per-step: true=%.3f  examiner=%.3f (both -> 0 = enough budget)"
      % (smooth(treg)[-1], smooth(rho_s)[-1] if False else smooth(run_bandit(10,4000,0.3,0,'sound')[0])[-1]))
