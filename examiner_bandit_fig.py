"""
Illustrative figure for the examiner-regret position paper.
Two panels, both with NO external optimum visible to the agent:

  (A) Big world, T < N: the special arm is never reached. A SOUND examiner keeps
      rho_t large (honest "room I cannot rule out"); a BIASED examiner that assumes
      a shared mean collapses rho_t below the true regret (a false "done").

  (B) Non-stationary: the special arm SWITCHES every tau steps. A sound examiner
      re-inflates rho_t at each switch (detects new room to improve); a biased
      examiner stays falsely low.

rho_t uses only counts/means; mu, mu* used only to SCORE (never by the agent).
"""
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(1)


def confidence(t, n, window=None):
    base = np.log(max(t, 2)) if window is None else np.log(min(t, window) + 1)
    c = np.sqrt(2 * base / np.maximum(n, 1))
    c[n == 0] = 1.0
    return c


# ---------- Panel A: big world, stationary, T < N ----------
def run_bigworld(N, T, eps, special, examiner):
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
        else:  # biased: trusts a shared-mean prior, no optimism for unseen, no pessimism
            seen = n > 0
            V_hi = float(np.max(muhat[seen])) if seen.any() else 0.5
            V_lo = muhat[a]
        rho.append(max(V_hi - V_lo, 0.0)); treg.append(mu_star - mu[a])
        r = float(rng.random() < mu[a]); n[a] += 1; s[a] += r
    return np.cumsum(rho), np.cumsum(treg)


# ---------- Panel B: non-stationary, sliding-window estimates ----------
def run_nonstat(N, T, eps, tau, W, examiner):
    # sliding window of the last W (arm, reward) pulls
    hist = []
    rho, treg = [], []
    special = 0
    for t in range(1, T + 1):
        if t % tau == 1 and t > 1:
            special = (special + 3) % N            # the good arm moves
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
        else:
            seen = n > 0
            V_hi = float(np.max(muhat[seen])) if seen.any() else 0.5
            V_lo = muhat[a]
        rho.append(max(V_hi - V_lo, 0.0)); treg.append(mu.max() - mu[a])
        r = float(rng.random() < mu[a]); hist.append((a, r))
    return np.array(rho), np.array(treg)


def smooth(x, k=50):
    return np.convolve(x, np.ones(k) / k, mode="valid")


fig, ax = plt.subplots(1, 2, figsize=(11, 4))

# Panel A
N, T, eps = 400, 300, 0.2
rho_s, treg = run_bigworld(N, T, eps, special=399, examiner="sound")
rho_b, _ = run_bigworld(N, T, eps, special=399, examiner="biased")
ax[0].plot(treg, "k", lw=2, label=r"true regret $\approx \epsilon T$")
ax[0].plot(rho_s, lw=2, label=r"sound $\sum\rho_t$ (honest)")
ax[0].plot(rho_b, "--", lw=2, label=r"biased $\sum\rho_t$ (false 'done')")
ax[0].set_title("(A) Big world, $T<N$: the unreached arm")
ax[0].set_xlabel("step $t$"); ax[0].set_ylabel("cumulative")
ax[0].legend(fontsize=8, loc="upper left")

# Panel B
N, T, eps, tau, W = 12, 4000, 0.35, 800, 300
rho_s, treg_s = run_nonstat(N, T, eps, tau, W, examiner="sound")
rho_b, _ = run_nonstat(N, T, eps, tau, W, examiner="biased")
ax[1].plot(np.cumsum(treg_s), "k", lw=2, label="true regret")
ax[1].plot(np.cumsum(rho_s), lw=2, label=r"sound $\sum\rho_t$ (honest, stays above)")
ax[1].plot(np.cumsum(rho_b), "--", lw=2, label=r"biased $\sum\rho_t$ (false 'done')")
for k in range(tau, T, tau):
    ax[1].axvline(k, color="gray", ls=":", lw=0.8)
ax[1].set_title("(B) Non-stationary: special arm switches at dotted lines")
ax[1].set_xlabel("step $t$"); ax[1].set_ylabel("cumulative")
ax[1].legend(fontsize=8, loc="upper left")

plt.tight_layout()
plt.savefig("examiner_bandit_fig.pdf")
plt.savefig("examiner_bandit_fig.png", dpi=140)

print("A: sound sum_rho=%.1f  biased sum_rho=%.1f  true regret=%.1f"
      % (rho_s[-1] if False else run_bigworld(400,300,0.2,399,'sound')[0][-1],
         run_bigworld(400,300,0.2,399,'biased')[0][-1],
         run_bigworld(400,300,0.2,399,'sound')[1][-1]))
print("B: mean sound rho=%.3f  mean biased rho=%.3f  mean true regret=%.3f"
      % (rho_s.mean(), rho_b.mean(), treg_s.mean()))
