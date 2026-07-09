# ChainSentinel — 2-Minute Video Script (Stage 1)

**Target: ~290 words spoken ≈ 1:55 at natural pace. One speaker, or split by section.**
**Visuals: slides + one screen-recorded notebook demo (Chronos-2 forecast chart). No live product needed.**

---

## [0:00–0:20] The hook — one shipment (visual: photo of rebar delivery / site)

> "On a data-center build in Chennai, 40 tons of rebar is due in 12 days. The pour is scheduled around it. Today, the site team will find out it's late the way every site team does — when the truck doesn't show up. That single miss cascades: crews idle, cranes rebooked, penalty clauses triggered. 98% of construction projects run late, and supply chain failures drive 70% of them."

## [0:20–0:45] The problem, sharpened (visual: slide with 3 stats)

> "The industry doesn't lack data — POs, delivery logs, vendor emails all exist. What's missing is a system that turns them into a probability, and a probability into an action, before the truck fails to arrive. That's ChainSentinel — our entry in the Supply Chain track."

## [0:45–1:20] The solution loop (visual: architecture-lite diagram, then notebook forecast chart)

> "ChainSentinel forecasts delay, cost, demand, and risk for every material — using zero-shot time-series foundation models like Amazon's Chronos-2, so it works on a brand-new site with no training data. Research shows these models miss sudden shocks, so we layer explicit disruption signals — vendor notices, weather, port status — on top. [show forecast chart] Here it is running: P90 arrival date, and a risk score that's a real probability, not a gut feeling."

## [1:20–1:45] The agent + memory (visual: agent workflow mock — alert draft with quoted clause)

> "When risk crosses the threshold on a critical-path material, an agent acts: it retrieves the PO and the exact contract penalty clause, recalls how similar disruptions were resolved before — 'expediting via Vendor B worked in March, at plus 4% cost' — and drafts an alert to the responsible committee with evidence attached. A human approves; the agent executes; the outcome is written back to memory. Every disruption makes it smarter."

## [1:45–2:00] Close (visual: team slide)

> "Built on 2026 research in forecasting foundation models and agent memory. We're Team Perceptron — Aman, Sai Nikhil, Abhishek, and Aditya from IIT Madras — and by July 31, this loop will be running end to end."

---

## Recording notes
- Record screen + voiceover in Loom or OBS; upload unlisted YouTube or Loom link
- The ONLY live demo element needed: a notebook cell running Chronos-2 on a simulated lead-time series showing a quantile fan chart (person 1 builds this first — it's also Stage 2 groundwork)
- The agent alert can be a designed mock (Figma/HTML) — it's Stage 1; judges expect vision, not product
- Rehearse to hit under 2:00 — judges may hard-stop
- Speak the stats slowly; they're the anchor
