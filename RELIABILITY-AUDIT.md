# ChainSentinel — Reliability Audit & Risk Register
**Pre-commitment due diligence, 2026-07-09**

## 1. Is the problem real? — YES, with hard numbers for the deck

- 98% of North American construction projects face delays; average project runs **37% longer** than planned ([Buildern 2026 metrics](https://buildern.com/resources/blog/project-delays-in-construction/))
- Large projects typically run 20% behind schedule with budget overruns up to 80% ([Cottingham & Butler](https://www.cottinghambutler.com/post/project-delays-and-cost-overruns))
- **Supply chain disruptions impact ~70% of all projects** ([WSI 2026](https://www.wsinc.com/blog/construction-supply-chain-disruptions-2026))
- SEM study: material supply shortage and supply-chain disruption are the top explanatory factors for cost overruns ([MDPI Sustainability 2025](https://www.mdpi.com/2071-1050/17/5/2119))
- Good logistics management alone can improve project performance by up to 30% ([Trangistics](https://trangistics.com/2025/02/the-financial-impact-of-construction-delays/))

**Use in deck:** "98% of projects delayed / 70% supply-chain-driven / 30% recoverable through better logistics" = problem, cause, and addressable headroom in three numbers.

## 2. Real-world reliability audit (honest, per component)

### 2a. Forecasting layer — ONE REAL WEAKNESS FOUND → design revision
**Finding:** Literature is clear that most TSFMs (Chronos, TimesFM, Lag-Llama, Sundial) forecast from numerical history alone and **ignore exogenous covariates**; accuracy degrades exactly when covariates drive "spikes, discontinuities, or regime changes" ([TA-PFN 2026](https://arxiv.org/html/2603.15802), [covariates via ICL](https://arxiv.org/html/2506.03128v1)). Construction delays are precisely regime-change events (port closure, vendor insolvency, strike) — a pure-history forecaster cannot see a shock that hasn't started showing in the series. Also: per-SKU lead-time histories are short/irregular; short-sample instability is documented ([TSFM under data sparsity](https://arxiv.org/abs/2602.12120)).

**Design revision (makes us stronger, not weaker):** split forecasting into two explicit layers —
1. **Baseline layer:** TSFM zero-shot quantile forecast from historical series (lead times, prices, demand). Handles trend/seasonality/vendor-level patterns.
2. **Event/shock layer:** explicit disruption signals (vendor notices, news, weather, port status) ingested by the agent, mapped to risk adjustments via simple Bayesian updating / rules on top of the baseline quantiles.

This is honest about a documented TSFM limitation, cites the research, and turns the limitation into an architecture slide. Judges who know the field will recognize we did our homework; the two-layer split is also closer to how real systems (and Kaya itself) must work.

**Residual risks + mitigations:**
- Short per-SKU histories → forecast at material-category/vendor level and share strength (hierarchical pooling); per-SKU only where history supports it
- Quantile miscalibration → conformal calibration on held-out simulated data; report coverage, not just point accuracy
- Always benchmark against naive/seasonal-naive baselines and show the comparison — claiming "beats naive baseline by X%" is more credible than any absolute number

### 2b. Optimization layer
- **Failure mode:** CPM/reorder model is only as good as the task-dependency and inventory data; real-world schedules are chronically stale. **Mitigation:** position as decision-support with human-validated schedule import; show sensitivity analysis ("recommendation holds across ±3 days of schedule error").
- **Failure mode:** over-claiming optimality. **Mitigation:** use a small, correct model (OR-Tools CP-SAT or transparent heuristic CPM) and never say "optimal" in the deck — say "ranked mitigation options."

### 2c. Agent layer
- **Failure mode:** long-horizon multi-step tool orchestration is a documented LLM weakness ([SupChain-Bench 2026](https://hf.co/papers/2602.07342)). **Mitigation:** short, structured workflows (per [Yoshizato et al. 2026](https://hf.co/papers/2602.05524)); constrained tool schemas; every workflow ≤5 steps; human approval gate before any outward action.
- **Failure mode:** hallucinated evidence (citing a clause that isn't there). **Mitigation:** citation verification — alert must quote exact contract text + page ref, verified by string match before send.
- **Failure mode:** alert fatigue (real-world killer of alerting systems). **Mitigation:** alert only on risk × criticality threshold (critical-path items only); daily digest for everything else. Say this in the deck — judges with industry experience will look for it.

### 2d. Memory layer
- **Failure mode:** cold start — memory is empty on day one. **Mitigation:** bootstrap by batch-ingesting historical project logs as episodic cases (honest: "pre-seeded from project history"); value grows with use.
- **Failure mode:** memory poisoning — a wrongly-recorded outcome gets retrieved and repeated. **Mitigation:** outcomes require human confirmation before commit; provenance-typed records separating evidence from inference (this exact failure is studied in [MemIR 2026](https://hf.co/papers/2605.25869)); confidence decay on old cases.
- **Failure mode:** spurious similarity — retrieving a superficially similar but causally different case. **Mitigation:** structured similarity (material + cause + vendor-type match) not just embedding cosine; agent must state *why* the retrieved case is analogous.

## 3. Hackathon guideline compliance checklist

| Rule | Status |
|---|---|
| Fits a named track (Supply Chain) | ✅ — mirrors track text (predict delays/costs/demand/risk, agentic workflows) |
| Team of 2–4, one team per person | ✅ (4 people) — **verify all 4 members' IITs are on the eligible list before registering** |
| Original work created during hackathon period | ✅ — start code fresh; pretrained models + open-source libs explicitly permitted |
| Any language/framework/OSS tool allowed | ✅ |
| Stage 1: proposal + ≤10 slides + 2-min video (missing = ineligible) | ⚠️ deliverables not started — due Jul 10/11 |
| Must clearly state track entered | ✅ — put "Track: Supply Chain" on slide 1 |
| Stage 2 prototype by Jul 31 | planned |

**Action:** email hackathon@usekaya.ai for Kaya platform access NOW — any real data reference kills the synthetic-data objection.

## 4. Winning-criteria fit (honest self-scores)

| Criterion | Score | Weak spot & fix |
|---|---|---|
| Problem Relevance & Fit | 5/5 | None — track-verbatim + industry numbers |
| Technical Feasibility & Innovation | 4.5/5 | Two-layer forecast revision makes the innovation claim defensible |
| Impact & Scalability | 4.5/5 | Zero-shot = cold-start on new sites; quantify impact via the 30%-logistics-headroom stat |
| Clarity & Quality | **3.5/5 — biggest gap** | Architecture is complex; non-technical judges must follow it. Fix: the entire video = ONE hero narrative (one rebar shipment, disruption → alert → action), architecture gets 1 slide max |
| Originality & Creativity | 4.5/5 | Memory layer + research-cited design; no other team will have Feb-2026 citations |

**The thing most likely to lose us Stage 1 is not the tech — it's an unclear 2-minute video.** Allocate real effort there.

## 5. Fallback plan (if X fails → Y)

| If this fails | Fall back to |
|---|---|
| Chronos-2 quantiles unreliable on our series | Quantile gradient boosting / Croston + conformal intervals; keep TSFM as comparison baseline (still a story: "we evaluated the latest foundation models") |
| Covariate/shock handling weak | Already handled by two-layer design — shock layer is independent of TSFM |
| Agent tool-calling flaky near demo deadline | Deterministic scripted workflow; LLM only drafts natural-language content (alerts, explanations); record video with retries |
| Memory retrieval noisy | Curated case library (k≈10 hand-authored episodic cases) for demo; keep write-back live |
| Integration/dashboard slips | Cut dashboard to the hero loop only: risk board + agent action log; notebook demos for the rest |
| A teammate drops / time crunch | Priority order: forecast notebook > agent loop > memory > optimizer > dashboard polish |

## 6. Fields of improvement (roadmap slide / finale Q&A ammo)

1. **Real data:** Kaya platform integration (access already offered to teams); fine-tune Chronos-2 on real construction lead-time data
2. **Multimodal forecasting:** feed document/text/image signals into the forecast itself (frontier research — [Aurora 2025](https://hf.co/papers/2509.22295))
3. **Evaluation:** benchmark agent workflows on SupChain-Bench-style SOP tasks; report success rate
4. **Cross-project learning:** federated/pooled memory across contractors without sharing proprietary data
5. **Vendor-communication loop:** learn response-channel effectiveness per vendor from outcome memory (already designed, deepen it)
6. **VLM site-verification hook:** photo of delivered material vs PO line items — bridges toward Physical AI track, mention as extension only

## 7. Bottom line

- Problem: real, quantified, industry-verified ✅
- Compliance: clean, two actions pending (IIT eligibility check, Kaya access email) ✅
- Reliability: one genuine weakness found (TSFM covariate blindness) → fixed by two-layer forecast design, which *improves* the proposal ✅
- Biggest true risk: **video/deck clarity**, not technology ⚠️
- Decision: GO, with revised architecture
