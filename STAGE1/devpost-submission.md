# Devpost form — copy-paste content

## Elevator pitch (≤200 chars — this is 193)

ChainSentinel forecasts material delays with foundation models, then an agent pulls the contract, alerts the right people, and remembers how every disruption was fixed. Built for construction.

## About the project (paste into the big Markdown box)

## Inspiration

On a typical construction site, the team finds out a critical material is late the same way they did thirty years ago: the truck doesn't arrive. 98% of projects run late, supply chain failures drive ~70% of them, and up to 30% of that loss is recoverable with earlier decisions. The strange part is that the data to predict the miss — POs, delivery logs, vendor emails — already exists. It's just never turned into a probability, and a probability is never turned into an action. We built ChainSentinel to close that gap.

## What it does

ChainSentinel is a supply-chain copilot for construction with two halves:

- **A forecasting engine** that predicts delay, cost, demand and risk for every tracked material. We use zero-shot time-series foundation models (Amazon Chronos-2) to produce quantile forecasts, so risk is a real probability — P(arrival later than the schedule buffer) — read directly off the distribution. Because the models are zero-shot, the system cold-starts on a brand-new site with no training data.
- **An agent with long-term memory** that acts on those forecasts. When risk crosses a threshold on a critical-path material, it retrieves the PO and the exact contract penalty clause (string-verified — no hallucinated citations), recalls how similar past disruptions were resolved and at what cost, runs what-if scenarios through a real critical-path optimizer, and drafts an alert to the responsible committee with evidence attached. A human approves; the agent executes; the outcome is written back to memory. Every disruption makes the next one cheaper.

## How we built it

For Stage 1 we built the forecasting core end to end: a multi-site lead-time simulator with disclosed methodology, running against the actual amazon/chronos-2 foundation model (zero-shot, CPU inference), producing quantile fan charts and a per-material site risk board. Our rebar scenario shows a 62% probability of missing the schedule buffer — a genuine model output, not a mockup.

The design is grounded in current research: Chronos-2/TimesFM for zero-shot quantile forecasting; Microsoft Research's OptiGuide pattern (the LLM never does the math — it parameterizes a real optimizer); and memory-retrieval agent designs validated in supply-chain research published February 2026 (Yoshizato et al.). Because published work shows history-only forecasters miss covariate-driven regime changes, we split forecasting into two layers: a foundation-model baseline plus an explicit shock layer for disruption events (vendor notices, weather, port status).

## Challenges we ran into

- **Foundation models can't see shocks.** The literature is clear that time-series foundation models degrade exactly when external events cause regime changes — and construction disruptions are regime changes. Rather than hide this, we redesigned around it: explicit shock signals adjust risk on top of the baseline quantiles.
- **No public construction logistics dataset exists.** We built a transparent simulator and kept the forecaster zero-shot so results are not tuned to flatter the model. We've requested Kaya platform access to ground Stage 2 in real data structures.
- **LLM agents fail at long-horizon orchestration** (SupChain-Bench, 2026). Our answer: short structured workflows (≤5 steps), constrained tool schemas, and a human approval gate before any outward action.

## Accomplishments that we're proud of

- A working zero-shot forecasting pipeline on a real foundation model, with calibrated risk probabilities — built in days.
- A design that turns documented research limitations into architecture decisions instead of hiding them.
- A memory layer design (episodic disruption cases + per-vendor outcome memory with human-confirmed write-back) that we believe no other team will attempt.

## What we learned

That the newest research is genuinely usable: the memory-retrieval agent pattern we adopted was published five months ago. And that honesty is a feature — decision support with calibrated probabilities, verified evidence, and a human gate is both more credible and closer to what the industry will actually adopt than a fully autonomous black box.

## What's next

By July 31 (Stage 2): the full loop running end to end — two-layer forecasting with conformal calibration evaluated against naive baselines, a critical-path optimizer with a what-if interface, the agent with document retrieval and citation verification, episodic + outcome memory, and a live risk-board dashboard. Then: real data via the Kaya platform, and fine-tuning Chronos on construction lead times.

## Built with (tags)

python, pytorch, hugging-face, amazon-chronos, transformers, numpy, pandas, matplotlib, langgraph, or-tools, fastapi, react, postgresql, pgvector, conformal-prediction

## "Try it out" links

- GitHub repo: [create a public repo, push the `demo/` folder + PROPOSAL.md, paste URL here]
- Demo video: [your unlisted YouTube / Loom link]
