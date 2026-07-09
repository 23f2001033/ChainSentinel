# %% [markdown]
# ChainSentinel — Stage 1 demo
# ============================
# Zero-shot probabilistic lead-time forecasting with a time-series foundation
# model (Amazon Chronos), and risk = P(arrival later than schedule buffer)
# read directly off the forecast quantiles.
#
# Run:  python chainsentinel_demo.py
# Or open in VS Code / Jupyter — the `# %%` markers make it an interactive notebook.
#
# Outputs (demo/out/):
#   fan_chart.png   — quantile fan forecast for the hero material (rebar)
#   risk_board.png  — per-material delay-risk board across the site
#
# Simulated-data methodology (disclosed, per our proposal):
#   weekly observed supplier lead time (days) = base + slow trend
#   + annual seasonality + AR(1) noise + occasional disruption shocks
#   (a shock adds lead-time days that decay over several weeks).
#   The forecaster is ZERO-SHOT: it never trains on this data, so results
#   are not tuned to flatter the model.

# %%
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

RNG = np.random.default_rng(7)

# Deck palette (chart tokens)
INK = "#1E293B"      # primary text
MUT = "#64748B"      # secondary text / axes
GRID = "#E2E8F0"     # recessive grid
AMBER = "#D97706"    # forecast hue (single-hue sequential)
AMBER_BAND = "#FDE9C8"
HIST = "#475569"     # history line
# Reserved status colors (risk board only, always paired with % labels)
S_LOW, S_MED, S_HIGH = "#059669", "#D97706", "#DC2626"

plt.rcParams.update({
    "font.family": "Arial",
    "text.color": INK, "axes.labelcolor": MUT,
    "xtick.color": MUT, "ytick.color": MUT,
    "axes.edgecolor": GRID, "figure.facecolor": "white",
})

# %% ---------------------------------------------------------------
# 1. Simulate weekly supplier lead-time histories (104 weeks)
# -------------------------------------------------------------------
N_WEEKS = 104

def simulate_lead_time(base, trend_per_wk=0.0, season_amp=0.6, noise_sd=0.9,
                       ar=0.55, shocks=(), recent_drift=0.0, drift_weeks=0):
    """Weekly observed lead time in days. `shocks` = [(week, size_days, decay_weeks)].
    `recent_drift` adds a per-week ramp over the last `drift_weeks` weeks
    (a vendor capacity problem that is still unfolding)."""
    t = np.arange(N_WEEKS)
    series = base + trend_per_wk * t + season_amp * np.sin(2 * np.pi * t / 52)
    eps = np.zeros(N_WEEKS)
    for i in range(1, N_WEEKS):
        eps[i] = ar * eps[i - 1] + RNG.normal(0, noise_sd)
    series = series + eps
    for wk, size, decay in shocks:
        for i in range(wk, min(N_WEEKS, wk + decay)):
            series[i] += size * (1 - (i - wk) / decay)
    if drift_weeks:
        ramp = np.linspace(0, recent_drift * drift_weeks, drift_weeks)
        series[-drift_weeks:] += ramp
    return np.clip(series, 2, None)

# Materials on site: name, vendor, history, schedule buffer (days) for the
# delivery due 4 weeks out, and whether the item is on the critical path.
MATERIALS = {
    "Rebar":            dict(vendor="Vendor A", buffer=16, critical=True,
                             y=simulate_lead_time(13.5, 0.010, shocks=[(30, 6, 8)],
                                                  recent_drift=0.68, drift_weeks=8)),
    "Cement":           dict(vendor="Vendor B", buffer=12, critical=True,
                             y=simulate_lead_time(8.0, 0.000, noise_sd=0.6)),
    "Structural steel": dict(vendor="Vendor C", buffer=27, critical=True,
                             y=simulate_lead_time(24.0, 0.015, noise_sd=1.6,
                                                  shocks=[(70, 8, 10)])),
    "Copper cable":     dict(vendor="Vendor D", buffer=19, critical=False,
                             y=simulate_lead_time(17.0, 0.020, noise_sd=1.2)),
    "HVAC units":       dict(vendor="Vendor E", buffer=55, critical=False,
                             y=simulate_lead_time(45.0, 0.010, noise_sd=2.0)),
    "Glass panels":     dict(vendor="Vendor F", buffer=28, critical=False,
                             y=simulate_lead_time(21.0, 0.005, noise_sd=1.0)),
}

# %% ---------------------------------------------------------------
# 2. Load a Chronos foundation model (zero-shot — no training on our data)
# -------------------------------------------------------------------
HORIZON = 8                      # forecast 8 weeks ahead
QLEVELS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
DELIVERY_WEEK = 4                # the delivery we care about is due 4 weeks out

def load_pipeline():
    try:
        from chronos import Chronos2Pipeline
        p = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cpu")
        return p, "amazon/chronos-2"
    except Exception:
        from chronos import BaseChronosPipeline
        p = BaseChronosPipeline.from_pretrained(
            "amazon/chronos-bolt-small", device_map="cpu", torch_dtype=torch.float32)
        return p, "amazon/chronos-bolt-small"

pipeline, model_name = load_pipeline()
print(f"Loaded foundation model: {model_name} (zero-shot)")

def forecast_quantiles(y):
    """Quantile forecasts, shape (HORIZON, len(QLEVELS))."""
    if model_name == "amazon/chronos-2":
        # Chronos-2 API: inputs is the series; returns [(n_variates, horizon, n_q)]
        q, _ = pipeline.predict_quantiles(
            inputs=np.asarray(y, dtype=np.float32).reshape(1, 1, -1),
            prediction_length=HORIZON, quantile_levels=QLEVELS)
        return q[0][0].numpy()
    # Chronos-Bolt API: context tensor; returns (batch, horizon, n_q)
    q, _ = pipeline.predict_quantiles(
        context=torch.tensor(y, dtype=torch.float32),
        prediction_length=HORIZON, quantile_levels=QLEVELS)
    return q[0].numpy()

def risk_of_late(qrow, buffer_days):
    """P(lead time > buffer) by interpolating the quantile function.
    qrow: quantile values at one horizon step (monotone in QLEVELS)."""
    if buffer_days <= qrow[0]:
        return 1 - QLEVELS[0] / 2            # beyond observed range, ~>90%
    if buffer_days >= qrow[-1]:
        return (1 - QLEVELS[-1]) / 2         # ~<5%
    cdf = np.interp(buffer_days, qrow, QLEVELS)
    return float(1 - cdf)

# %% ---------------------------------------------------------------
# 3. Forecast every material, compute delay risk at the delivery week
# -------------------------------------------------------------------
results = {}
for name, m in MATERIALS.items():
    q = forecast_quantiles(m["y"])
    risk = risk_of_late(q[DELIVERY_WEEK - 1], m["buffer"])
    results[name] = dict(q=q, risk=risk, **m)
    flag = "CRITICAL PATH" if m["critical"] else ""
    print(f"{name:18s} {m['vendor']:9s} buffer {m['buffer']:>3d}d "
          f"P50@wk{DELIVERY_WEEK} {q[DELIVERY_WEEK-1][4]:5.1f}d "
          f"risk {risk:5.1%}  {flag}")

# %% ---------------------------------------------------------------
# 4. Fan chart — hero material (rebar)
# -------------------------------------------------------------------
HERO = "Rebar"
r = results[HERO]
hist_wks = 26
y_hist = r["y"][-hist_wks:]
xh = np.arange(-hist_wks + 1, 1)
xf = np.arange(1, HORIZON + 1)
q = r["q"]

fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
ax.fill_between(xf, q[:, 0], q[:, 8], color=AMBER_BAND, label="P10–P90 range")
ax.fill_between(xf, q[:, 2], q[:, 6], color=AMBER, alpha=0.30)
ax.plot(xh, y_hist, color=HIST, lw=2, label="Observed lead time")
ax.plot(np.r_[xh[-1], xf], np.r_[y_hist[-1], q[:, 4]], color=AMBER, lw=2.5,
        label="P50 forecast")
ax.axhline(r["buffer"], color=MUT, lw=1.4, ls=(0, (5, 4)))
ax.text(xh[0], r["buffer"] + 0.35, f"schedule buffer — {r['buffer']} days",
        fontsize=9.5, color=MUT)
ax.axvline(DELIVERY_WEEK, color=GRID, lw=1.2)
ax.text(DELIVERY_WEEK, ax.get_ylim()[0] + 0.4, " delivery due", fontsize=9.5,
        color=MUT)

risk_pct = f"{r['risk']:.0%}"
ax.annotate(f"{risk_pct} risk of missing the buffer",
            xy=(DELIVERY_WEEK, q[DELIVERY_WEEK - 1, 6]),
            xytext=(DELIVERY_WEEK - 13, q[:, 8].max() - 0.5),
            fontsize=12, fontweight="bold", color=S_HIGH,
            arrowprops=dict(arrowstyle="->", color=S_HIGH, lw=1.4))

ax.set_title(f"{HERO} ({r['vendor']}) — lead-time forecast, zero-shot {model_name.split('/')[-1]}",
             fontsize=13, fontweight="bold", color=INK, loc="left", pad=12)
ax.set_xlabel("Weeks (0 = today)")
ax.set_ylabel("Supplier lead time (days)")
ax.grid(axis="y", color=GRID, lw=0.6)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="upper left", frameon=False, fontsize=9.5)
fig.tight_layout()
fig.savefig(OUT / "fan_chart.png", bbox_inches="tight")
print(f"\nwrote {OUT/'fan_chart.png'}")

# %% ---------------------------------------------------------------
# 5. Risk board — every material on site
# -------------------------------------------------------------------
order = sorted(results, key=lambda k: results[k]["risk"], reverse=True)
risks = [results[k]["risk"] for k in order]
labels = [f"{k}  ·  {results[k]['vendor']}" + ("  ▲ critical path" if results[k]["critical"] else "")
          for k in order]
colors = [S_HIGH if r > 0.60 else S_MED if r > 0.20 else S_LOW for r in risks]

fig, ax = plt.subplots(figsize=(9, 4.2), dpi=150)
bars = ax.barh(range(len(order)), [r * 100 for r in risks], color=colors, height=0.62)
for i, (b, r) in enumerate(zip(bars, risks)):
    lab = "HIGH" if r > 0.60 else "MED" if r > 0.20 else "LOW"
    ax.text(b.get_width() + 1.2, i, f"{r:.0%}  {lab}", va="center",
            fontsize=10.5, fontweight="bold", color=colors[i])
ax.set_yticks(range(len(order)), labels, fontsize=10.5)
ax.invert_yaxis()
ax.set_xlim(0, 108)
ax.set_xlabel(f"P(delivery misses schedule buffer), week {DELIVERY_WEEK} — zero-shot forecast")
ax.set_title("Site risk board — delay probability per material",
             fontsize=13, fontweight="bold", color=INK, loc="left", pad=12)
ax.grid(axis="x", color=GRID, lw=0.6)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "risk_board.png", bbox_inches="tight")
print(f"wrote {OUT/'risk_board.png'}")
