# ChainSentinel — Memory-Augmented Supply Chain Sentinel Agent
**Kaya AI IIT India Hackathon 2026 — Supply Chain Track**

> Working name — alternatives: SiteFlow, Kaya Lens, ChainPilot. Decide as a team.

## 1. One-line pitch
A supply-chain copilot that forecasts **delay, cost, demand, and risk** per material with calibrated probabilities, and an **agent with long-term memory** that acts on those forecasts — retrieving the relevant PO/contract, alerting the responsible committee with evidence, and completing the mitigation workflow — while learning from every past disruption it has handled.

## 2. Why this wins (mapped to judging criteria)
| Criterion | How we score |
|---|---|
| Problem Relevance & Industry Fit | Mirrors the track text verbatim (predict delays/costs/demand/risks + agentic workflows). Also mirrors Kaya's own product thesis. |
| Technical Feasibility & Innovation | Zero-shot time-series foundation models + OptiGuide-style what-if optimization + episodic agent memory — a 2024–2026 research stack, not an API wrapper. |
| Impact & Scalability | Zero-shot forecasting = works on a brand-new site with no training data. That IS the scalability story. |
| Clarity & Quality | Demo is one narrative loop: disruption → forecast → memory recall → evidence → alert → action → memory write-back. |
| Originality & Creativity | The memory layer ("the agent remembers how the last cement delay was resolved and what it cost") — no other team will build this. |

## 3. The "technique nobody else thought to apply" (research-backed)

### 3a. Zero-shot probabilistic forecasting via time-series foundation models
Most teams will train XGBoost/LSTM on synthetic data — judges will (rightly) distrust accuracy numbers trained on data the team generated themselves. We instead use a **pretrained time-series foundation model, zero-shot**, producing **quantile forecasts** (P10/P50/P90 arrival dates, cost bands):
- **amazon/chronos-2** (Apache-2.0, 15.9M downloads) — https://hf.co/amazon/chronos-2 — paper: https://hf.co/papers/2403.07815 (Chronos), https://arxiv.org/abs/2510.15821 (Chronos-2). Supports covariates.
- **google/timesfm-2.5-200m** (Apache-2.0) — https://hf.co/google/timesfm-2.5-200m-transformers — paper: https://hf.co/papers/2310.10688
- Backup/ensemble: Lag-Llama (probabilistic, https://hf.co/papers/2310.08278), Sundial (https://hf.co/papers/2502.00816)

**Risk score = P(delay > schedule buffer), read directly off the forecast quantiles.** Calibrated risk, not a vibes-based score. Cold-start on any new site → scalability claim is technical, not marketing.

### 3b. OptiGuide pattern: LLM + optimization for what-if analysis
Microsoft Research, "Large Language Models for Supply Chain Optimization" — https://hf.co/papers/2307.03875. The LLM never does the math: it translates "what if the steel vendor slips 2 weeks?" into parameters for a real optimizer (critical-path / reorder-point model), runs it, and explains the result. We apply the same pattern to construction materials.

### 3c. Agent memory (the differentiator)
Direct precedent, published Feb 2026: **"AI Agent Systems for Supply Chains: Structured Decision Prompts and Memory Retrieval"** — https://hf.co/papers/2602.05524 — LLM supply-chain agents retrieving similar historical experiences measurably improve decisions. Also: InvAgent (multi-agent LLM inventory management, https://hf.co/papers/2407.11384); memory architectures: Hindsight — retain/recall/reflect (https://hf.co/papers/2512.12818), SYNAPSE episodic-semantic graph memory (https://hf.co/papers/2601.02744).

Our memory design (simple, buildable):
- **Episodic memory**: every disruption case = structured record {material, vendor, cause, actions taken, outcome, cost impact, resolution time} + embedding. New disruption → similarity retrieval → "3 similar past cases; expediting via Vendor B resolved in 4 days at +4% cost."
- **Procedural/outcome memory**: which actions worked, per vendor ("Vendor A ignores email, responds to calls"; "committee X needs 48h lead time"). Feeds action selection.
- **Write-back loop**: after each workflow completes, the agent reflects and stores the outcome. The agent demonstrably gets smarter during the demo.
- Implementation: pgvector/Chroma + structured JSON records. Optionally Mem0/Letta, but hand-rolled is more explainable to judges.

### 3d. Evaluation framing (bonus credibility)
**SupChain-Bench** (Feb 2026, https://hf.co/papers/2602.07342) benchmarks LLMs on real-world supply-chain orchestration and finds they struggle with long-horizon multi-step tool use — we cite it as the gap our structured agent + memory design addresses, and borrow its SOP-style task framing for our eval.

## 4. Architecture
```
┌────────────────────────────────────────────────────────────┐
│ UI: React dashboard — risk board, forecast fans, agent log │
└──────────────▲─────────────────────────────────────────────┘
               │
┌──────────────┴───────────────┐   ┌───────────────────────────┐
│ AGENT (LangGraph orchestrator│◄──┤ MEMORY                    │
│  tools:                      │   │  episodic case store      │
│  - retrieve_document (RAG    │   │  outcome/procedural store │
│    over POs/contracts)       │   │  reflect + write-back     │
│  - alert_committee (email/   │   └───────────────────────────┘
│    Slack draft, human-in-    │
│    the-loop approve)         │   ┌───────────────────────────┐
│  - create_expedite_rfq       │◄──┤ DECISION LAYER            │
│  - schedule_followup         │   │  critical-path / reorder  │
│  - run_whatif(params)        │   │  optimizer (OR-Tools /    │
└──────────────▲───────────────┘   │  heuristic CPM)           │
               │                   └────────────▲──────────────┘
┌──────────────┴───────────────────────────────┴──────────────┐
│ FORECAST LAYER (two-layer — see RELIABILITY-AUDIT.md §2a): │
│  1. Baseline: Chronos-2 / TimesFM zero-shot quantile       │
│     forecasts from history → delay/demand/cost;            │
│     risk = P(late) from quantiles                          │
│  2. Shock layer: explicit disruption events (vendor        │
│     notices, news, weather) → Bayesian/rule risk           │
│     adjustment on top. TSFMs documentedly miss             │
│     covariate-driven regime changes — shocks are handled   │
│     explicitly, not implicitly                             │
└──────────────▲──────────────────────────────────────────────┘
               │
┌──────────────┴──────────────────────────────────────────────┐
│ DATA: simulated multi-site event stream (POs, deliveries,  │
│ prices) + document corpus (POs, contracts, schedules)      │
└─────────────────────────────────────────────────────────────┘
```

## 5. Demo narrative (2-min video / finale)
1. Live risk board: 40 materials across 3 sites, green/amber/red from forecast quantiles.
2. Disruption event lands (vendor ship date slips). Rebar risk goes red: "62% probability of missing the schedule buffer — this material is on the critical path." (Number matches the live demo output in demo/chainsentinel_demo.py.)
3. Agent wakes: retrieves the PO + the contract's penalty clause (document intelligence), recalls 3 similar past cases from memory, runs what-if through the optimizer.
4. Agent drafts an alert to the responsible committee: evidence attached, recommendation ranked by memory of past outcomes, cost delta quantified. Human approves → action executes.
5. Outcome written back to memory. Show memory growing — "the system that gets smarter with every disruption."

## 6. Timeline & team split (4 people)
**Stage 1 — due Jul 10/11 (~4 days):** proposal doc + ≤10 slides + 2-min video. Build a thin real slice for the video: Chronos-2 forecasting a delay series in a notebook + one scripted agent loop. Roles: A=forecast notebook, B=agent loop demo, C=slides+proposal, D=video+data story.
**Stage 2 — due Jul 31 (~3 weeks):** full prototype.
- Person 1 (ML): data simulator + Chronos-2/TimesFM pipeline + risk calibration
- Person 2 (ML/OR): optimizer + what-if engine (OptiGuide pattern)
- Person 3 (agents): LangGraph agent, tools, memory store, RAG over docs
- Person 4 (full-stack): dashboard, event stream, integration, demo polish

## 7. Risks & mitigations
| Risk | Mitigation |
|---|---|
| Synthetic data credibility | Zero-shot TSFM = no training on our own synthetic data; disclose simulator methodology openly; anchor price series to real public commodity indices (steel/cement) where possible |
| Memory demo needs history | Pre-seed episodic memory from a simulated "past project log" (say so honestly); live write-back shown during demo |
| Agent reliability (SupChain-Bench failure modes) | Structured decision prompts (per 2602.05524), constrained tool schemas, human-in-the-loop approval gate |
| Scope creep (4 forecast targets) | One forecasting engine, four series types — same pipeline; delay is the hero, demand/cost/risk derived views |
| LLM does math | Never — all numbers from TSFM quantiles + optimizer (OptiGuide separation) |

## 8. Papers to cite in the deck
1. Chronos / Chronos-2 (Amazon) — 2403.07815 / 2510.15821
2. TimesFM (Google) — 2310.10688
3. Li et al., LLMs for Supply Chain Optimization (Microsoft, OptiGuide) — 2307.03875
4. Yoshizato et al., AI Agent Systems for Supply Chains: Structured Decision Prompts and Memory Retrieval (2026) — 2602.05524
5. InvAgent: LLM Multi-Agent Inventory Management — 2407.11384
6. Hindsight: Agent Memory that Retains, Recalls, Reflects — 2512.12818
7. SupChain-Bench (2026) — 2602.07342

## 9. Hackathon facts (reference)
- Stage 1 due **Jul 10/11** (proposal + ≤10 slides + 2-min video — missing video/slides = ineligible)
- Stage 2 prototype due **Jul 31**; finalists Aug 7; in-person finale Bangalore **Aug 14**
- Judging: Problem Relevance & Fit / Technical Feasibility & Innovation / Impact & Scalability / Clarity & Quality / Originality & Creativity (no weights published)
- Any language/framework/open-source tool allowed; pre-trained models explicitly permitted
- Kaya platform access on request: hackathon@usekaya.ai
