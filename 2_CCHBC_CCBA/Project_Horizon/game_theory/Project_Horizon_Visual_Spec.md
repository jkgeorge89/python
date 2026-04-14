# Project Horizon - Visual Specification for Methodology Exhibits
**Purpose:** Detailed handoff specification for the creation of methodology visuals for the final Project Horizon option valuation approach.
**Audience:** Client-facing readers, auditors, valuation reviewers, and internal deal-team users.
**Scope:** Final methodology only. Do not refer in chart titles, subtitles, captions, or legends to earlier modeling iterations, draft builds, proxy models, or internal version labels.

---

## 1. Objective of the Visual Pack

The visual pack should make the final Project Horizon valuation methodology understandable without pretending that one chart can explain the full stochastic game.

The pack should therefore do four things:

1. Show the contract timeline and where each party can act.
2. Show how Olympus call exercise changes Titan's residual put exposure.
3. Show why the overlap region is a strategic decision problem rather than a plain one-sided option problem.
4. Show the most decision-useful outputs of the model without overloading the reader with raw notebook mechanics.

The charts should simplify the methodology, not replicate the notebook line by line.

---

## 2. Non-Negotiable Rules for the Other Agent

1. Treat the visuals as illustrations of the final methodology only.
2. Do not use labels such as proxy, FULL, vGameTheory, draft, initial, prior, legacy, earlier build, or model evolution in any external-facing chart.
3. Do not scrape printed text from notebook outputs as the primary data source if the underlying variables or functions can be called directly.
4. Do not hardcode values that can be derived from notebook variables.
5. Do not create one dense diagram attempting to show the entire tree, all states, all actions, and all sensitivities at once.
6. Do not create visuals that imply probabilities where the notebook is only showing conditional state diagnostics.
7. Do not present the conditional remaining-state valuation table as though it were a time-path forecast.
8. Do not imply that both parties legally complete at the same instant in the overlap region.
9. Use the same underlying assumptions as the notebook unless the chart is explicitly labeled as an illustration.
10. Separate conceptual diagrams from quantitative exhibits.

---

## 3. Source of Truth

The source of truth is the current Project Horizon option notebook in:

- /workspaces/python/2_CCHBC_CCBA/Project_Horizon/game_theory/OPM_Structured_Option_Model_FULL_vGameTheory.ipynb

The charts should pull data from notebook variables and helper functions where possible.

Key variables and functions already present in the notebook include:

- `call_start`, `call_end`, `put_start`, `put_end`
- `COMPLETION_LAG_YEARS`
- `INITIAL_TITAN_PCT`
- `MIN_CALL_TRANCHE_PCT`
- `RESIDUAL_FLOOR_PCT`
- `STATE_PCTS`
- `ALLOW_PARTIAL_CALLS`
- `GAME_TIE_PRIORITY_TO_OLYMPUS`
- `asset_volatility`
- `risk_free_rate`
- `simulations`
- `full_value_total`
- `full_value_per_share`
- `full_value_total_dlom`
- `full_value_per_share_dlom`
- `titan_value_total`
- `titan_value_total_dlom`
- `state_values_total`
- `dlom_terms`
- `allowed_call_targets(current_pct, allow_partial_calls, state_pcts=None)`
- `summarize_call_menu(current_pct, allow_partial_calls)`
- `run_vgame_model_scenario(vol, rf, allow_partial_calls, tie_priority_to_olympus)`
- `shares_for_pct(pct)`

Where a chart needs a derived dataset, the other agent should create that dataset directly from these variables and functions rather than manually keying values into a plotting script.

---

## 4. Deliverables and File Structure

The other agent should create the following output structure if it does not already exist:

- `/workspaces/python/2_CCHBC_CCBA/Project_Horizon/game_theory/visuals/`
- `/workspaces/python/2_CCHBC_CCBA/Project_Horizon/game_theory/visuals/data/`
- `/workspaces/python/2_CCHBC_CCBA/Project_Horizon/game_theory/visuals/svg/`
- `/workspaces/python/2_CCHBC_CCBA/Project_Horizon/game_theory/visuals/png/`

Recommended file naming convention:

- `PH_Method_01_Exercise_Timeline.svg`
- `PH_Method_01_Exercise_Timeline.png`
- `PH_Method_02_Residual_State_Ladder.svg`
- `PH_Method_03_Overlap_Decision_Logic.svg`
- `PH_Method_04_State_Value_Diagnostics.svg`
- `PH_Method_05_DLOM_Bridge.svg`
- `PH_Method_06_Market_Sensitivity_Heatmap.svg`
- `PH_Method_07_Structural_Sensitivity.svg`
- `PH_Method_08_Admissible_Call_Matrix.svg`

Recommended companion data files:

- `timeline_windows.csv`
- `residual_state_paths.csv`
- `state_values_diagnostic.csv`
- `dlom_terms.csv`
- `market_sensitivity.csv`
- `structural_sensitivity.csv`
- `admissible_call_matrix.csv`

---

## 5. Visual Design System

### 5.1 General design direction

The charts should look like a clean transaction or valuation appendix, not like software documentation.

Use:

- white or very light neutral background;
- muted but distinct party colors;
- strong axis labeling;
- concise subtitles;
- callout annotations only where they materially improve comprehension.

Avoid:

- saturated rainbow palettes;
- dark-mode-first styling;
- 3D effects;
- heavy drop shadows;
- overly thin lines that disappear in print;
- dense gridlines.

### 5.2 Suggested colors

Use a stable palette across all charts:

- Olympus: deep blue, for example `#0B5CAB`
- Titan: deep red, for example `#A61B1B`
- Overlap region / strategic interaction: amber, for example `#C98200`
- Neutral / waiting / continuation: slate gray, for example `#5B6573`
- Exhausted contract / zero state: light gray, for example `#C7CDD4`
- DLOM adjustment: charcoal or dark gray, for example `#364152`
- Base-case highlight border: black or near-black

If the other agent applies a different palette, it must keep the same semantic mapping across all visuals.

### 5.3 Typography and export size

Preferred final format:

- SVG first, PNG second.

Target sizes:

- Slide-ready: 1600 x 900 px or proportional SVG equivalent.
- Memo-ready: 1400 x 900 px or A4-friendly equivalent.

Font guidance:

- use a readable sans-serif available in the environment;
- minimum 11 pt equivalent for annotations;
- minimum 13 pt equivalent for axis labels;
- minimum 16 pt equivalent for title.

---

## 6. Build Workflow the Other Agent Should Follow

1. Read the notebook and confirm the current values and helper functions.
2. Generate explicit intermediate data tables as CSV files in `visuals/data/`.
3. Build charts from those CSVs or directly from the live notebook variables.
4. Export SVG and PNG versions.
5. Add a short source note or caption for each chart.
6. Check that all chart labels match the methodology note and do not refer to internal version labels.

Important implementation rule:

- if a chart is conceptual, Mermaid is acceptable for a draft version;
- if a chart is quantitative, it should be created with Python plotting code, ideally `matplotlib` and optionally `seaborn` if available.

---

## 7. Chart Inventory Overview

The recommended pack has five primary exhibits and three appendix exhibits.

Primary exhibits:

1. Exercise timeline.
2. Residual-state ladder after partial call exercise.
3. Overlap-region decision logic.
4. Contract value by Titan remaining-state.
5. DLOM bridge from clean contract value to primary reported fair value.

Appendix exhibits:

6. Market sensitivity heatmap.
7. Structural sensitivity bar chart.
8. Admissible call matrix.

---

## 8. Detailed Specification by Chart

## PH-Method-01: Exercise Timeline

### Purpose

This chart answers the first client or auditor question: when can each side act?

It should make the time structure legible in one glance.

### Audience question answered

- When is the call live?
- When is the put live?
- Where does the overlap occur?
- What is the time horizon of the valuation?

### Recommended format

- Primary: polished timeline chart in SVG and PNG.
- Draft alternative: Mermaid Gantt chart.

### Required data inputs

Pull directly from the notebook:

- `call_start = 3.0`
- `call_end = 5.0`
- `put_start = 3.5`
- `put_end = 6.0`
- `COMPLETION_LAG_YEARS = 0.0`

### Required data table schema

Create `timeline_windows.csv` with columns:

- `phase_label`
- `start_year`
- `end_year`
- `actor`
- `status_type`
- `display_order`

Suggested rows:

- No exercise region, 0.0, 3.0, Neither, neutral, 1
- Olympus call-only region, 3.0, 3.5, Olympus, olympus, 2
- Overlap region, 3.5, 5.0, Both, overlap, 3
- Titan put-only region, 5.0, 6.0, Titan, titan, 4

### How to build it

1. Use a horizontal axis from Year 0.0 to Year 6.0.
2. Add four contiguous horizontal bands or bars.
3. Shade the overlap band differently from the one-party bands.
4. Add vertical markers at 3.0, 3.5, 5.0, and 6.0.
5. Label the bands directly rather than relying only on a legend.
6. Add a small note under the chart that the primary valuation assumes zero completion lag between notice and completion for modeling purposes.

### Text that must appear on the chart or caption

- `Year 0-3.0: no exercise`
- `Year 3.0-3.5: Olympus call-only`
- `Year 3.5-5.0: overlap / strategic region`
- `Year 5.0-6.0: Titan put-only`

### Styling guidance

- neutral band in light gray;
- Olympus band in blue;
- Titan band in red;
- overlap band in amber.

### Caption draft

`The Option Agreement is valued over a six-year horizon with separate call-only, overlap, and put-only regions. The overlap window is the period in which strategic interaction becomes relevant.`

### QA checks

1. Overlap must begin exactly at Year 3.5 and end exactly at Year 5.0.
2. The call-only region must not extend beyond Year 3.5.
3. The put-only region must not begin before Year 5.0.
4. The chart must not imply that both rights start on the same date.

### Mermaid draft guidance

If the other agent wants a Mermaid draft first, use a Gantt-style chart with one row per phase. The polished export should still be rebuilt in Python or a vector-friendly tool if the Mermaid result looks too generic.

---

## PH-Method-02: Residual-State Ladder

### Purpose

This chart explains the most important linked-contract mechanic: Olympus call exercise reduces Titan's residual holding, and Titan's future put applies only to what remains.

### Audience question answered

- Why is this not just a fixed-block call less a fixed-block put?
- How does partial call exercise change the future state of the contract?

### Recommended format

- Primary: multi-panel SVG/PNG diagram.
- Draft alternative: Mermaid flowchart or state diagram.

### Required data inputs

Pull from notebook variables and helper functions:

- `STATE_PCTS`
- `MIN_CALL_TRANCHE_PCT`
- `RESIDUAL_FLOOR_PCT`
- `ALLOW_PARTIAL_CALLS`
- `allowed_call_targets(current_pct, ALLOW_PARTIAL_CALLS)`

### Required data table schema

Create `residual_state_paths.csv` with columns:

- `current_pct`
- `target_pct`
- `call_size_pct`
- `target_type`
- `is_zero_target`

For each `current_pct` in at least `[25, 20, 15, 10]`, compute:

- `target_pct` for every admissible target from `allowed_call_targets`
- `call_size_pct = current_pct - target_pct`
- `target_type = exhausted` if `target_pct == 0`, else `residual`

### How to build it

Use one of the two structures below.

Preferred structure:

1. Create four small horizontal panels, one each for current states 25%, 20%, 15%, and 10%.
2. In each panel, place the current state on the left.
3. Place all admissible target states to the right in descending order.
4. Draw one arrow from current state to each target state.
5. Label each arrow with the call size, for example `call 5%`, `call 12%`, `call 25% to zero`.
6. Use a visually distinct style for the arrow that goes to zero.
7. Add a footnote that Titan may put all remaining shares in the current state if the put is live.

Alternative structure for technical appendix:

1. Build an admissible-transition matrix instead of a ladder.
2. Rows are current Titan remaining states.
3. Columns are admissible target states.
4. Fill a cell if that target is contract-feasible.
5. Show call size inside the filled cell.

### Why this chart matters

This is the chart that replaces the false intuition that the contract is always about the same 25% block.

### Required annotations

Include a direct callout that says:

`After any call exercise, Titan's future putable block becomes the residual holding, not the original 25%.`

### Caption draft

`Olympus can call a contract-feasible amount of the residual stake, subject to the minimum tranche and residual-floor constraints. After any call exercise, Titan's future put applies only to the shares still held.`

### QA checks

1. No arrow may represent a call smaller than 5%.
2. No non-zero target state may fall below 7%.
3. The zero target must remain admissible where the whole residual block can be called.
4. The chart must not show Titan putting less than all remaining shares.

### Mermaid draft guidance

Mermaid is acceptable for a simplified explanatory draft, but the final client-ready version is likely better as SVG to avoid a spaghetti diagram.

---

## PH-Method-03: Overlap Decision Logic

### Purpose

This chart explains why the overlap window is treated as a strategic two-party decision problem.

### Audience question answered

- What happens when both sides have live rights?
- How does the model think about wait versus act now?
- What does same-bucket timing mean in practice?

### Recommended format

- Primary: flowchart or decision schematic.
- Draft alternative: Mermaid flowchart.

### Required data inputs

This is mainly conceptual, but it should reflect the notebook logic in `value_game_contract_tree`.

Relevant elements:

- `wait_value`
- `put_value`
- `call_then_wait`
- `olympus_first_then_titan_puts_residual`
- `simultaneous_value`
- `GAME_TIE_PRIORITY_TO_OLYMPUS`

### How to build it

1. Start with a node labeled `Overlap month: both call and put are live`.
2. Split the logic into Olympus and Titan branches.
3. Show that Olympus compares waiting with each admissible call amount.
4. Show that Titan compares waiting with putting all remaining shares.
5. Show that in the overlap region Titan is modeled as minimizing Olympus value.
6. Show that if both sides prefer immediate action in the same modeled month, the same-bucket priority parameter approximates who effectively gets there first on the monthly grid.
7. End with a node labeled `Node value = best Olympus action after Titan best response`.

### Critical wording rules

The chart must not say or imply:

- both parties exercise simultaneously in legal time;
- both notices complete at the same instant;
- the tie-priority parameter is a legal clause rather than a monthly-grid approximation.

The chart should say:

- `same-bucket means both sides prefer immediate action in the same modeled month`;
- `the monthly grid does not observe exact intra-month notice ordering`.

### Suggested box sequence

Use this structure:

1. `Overlap node: call live, put live`
2. `Compute continuation / wait value`
3. `For each admissible Olympus call target, compute immediate call value`
4. `Titan best response = min(call-then-wait, same-bucket resolution)`
5. `Olympus chooses the action with the highest resulting value`
6. `Resulting node value stored for backward induction`

### Caption draft

`In the overlap region the model does not treat the contract as a passive option. Olympus evaluates each feasible call action, Titan evaluates whether to put the residual block, and the node value is determined by strategic interaction on the monthly grid.`

### QA checks

1. The chart must clearly distinguish waiting from acting.
2. The chart must clearly distinguish Olympus optimization from Titan best response.
3. Titan's put action must be all remaining shares, not an arbitrary fraction.
4. Same-bucket handling must be presented as a numerical approximation.

---

## PH-Method-04: Contract Value by Titan Remaining-State

### Purpose

This chart visualizes the state-diagnostic outputs already printed by the notebook and helps explain the role of the remaining-state variable.

### Audience question answered

- What does the model say the contract is worth in different residual states?
- How should the 25%, 20%, 15%, 10%, 7%, and 0% rows be interpreted?

### Recommended format

- Primary: bar chart.
- Optional second panel: table strip below chart for per-remaining-share values.

### Required data inputs

Pull directly from:

- `state_values_total`
- `INITIAL_TITAN_PCT`
- `shares_for_pct(pct)`

At minimum chart these states:

- 25%
- 20%
- 15%
- 10%
- 7%
- 0%

### Required data table schema

Create `state_values_diagnostic.csv` with columns:

- `titan_remaining_pct`
- `contract_value_total_usd`
- `contract_value_total_usd_m`
- `per_remaining_share_usd`
- `state_role`

Where:

- `state_role = current initial state` for 25%
- `state_role = conditional reduced state` for other positive states
- `state_role = exhausted contract` for 0%

### How to build it

1. Use the x-axis for Titan remaining stake percentage.
2. Use the y-axis for contract value to Olympus in USD millions.
3. Highlight the 25% bar in a stronger blue because it is the actual initial state.
4. Use lighter blue or slate for the conditional reduced-state bars.
5. Use a gray zero-height or outlined bar for the 0% exhausted state.
6. Add a subtitle or footnote that these are conditional state diagnostics and not a probability-weighted path forecast.
7. If space permits, add a small label above each positive bar showing the per-remaining-share value.

### Required annotation

Include a prominent note such as:

`These state values are diagnostics for distinct residual holdings. They are not averaged together and they are not a forecast of the path the contract will take.`

### Caption draft

`The contract value depends on Titan's residual holding because the future action set changes as prior call exercise changes the residual block. The chart shows conditional state values, not a path-probability distribution.`

### QA checks

1. 25% must be labeled as the current initial state.
2. 0% must be labeled as exhausted contract.
3. The chart must not imply monotonicity unless the actual data show it.
4. The chart must not present the state bars as sequential time steps.

### Reference check

The other agent should reconcile the base 25% value in this chart to the notebook's pre-DLOM contract value output for Olympus.

---

## PH-Method-05: DLOM Bridge

### Purpose

This chart connects the clean contract value to the primary reported fair value after marketability adjustment.

### Audience question answered

- How does the reported fair value move from the clean contract value to the post-DLOM figure?
- What restriction horizons are considered for DLOM?

### Recommended format

Preferred structure is a two-panel figure:

- Panel A: DLOM percentage by restriction horizon.
- Panel B: waterfall from clean value to post-DLOM primary value.

### Required data inputs

Pull directly from:

- `dlom_terms`
- `full_value_total`
- `full_value_total_dlom`
- `full_value_per_share`
- `full_value_per_share_dlom`

### Required data table schema

Create `dlom_terms.csv` with columns:

- `restriction_years`
- `lookback_value`
- `dlom_pct`
- `is_central_case`

Also create a simple waterfall table if useful with columns:

- `step_label`
- `amount_usd`
- `display_order`
- `step_type`

Suggested waterfall rows:

- Clean contract value before DLOM
- Less DLOM adjustment
- Primary fair value after DLOM

### How to build it

Panel A:

1. Plot 3.0-year, 4.0-year, and 5.0-year DLOM percentages as vertical bars.
2. Highlight the 4.0-year bar as the central case.
3. Label each bar with the DLOM percent.
4. If space permits, add the lookback value below each bar label or in a small companion table.

Panel B:

1. Start with the clean contract value bar.
2. Show the DLOM adjustment as a negative step.
3. End with the post-DLOM primary fair value bar.
4. Label the ending value in USD millions.
5. If space permits, add the per-share value as a secondary annotation.

### Critical wording rules

The chart should not imply that DLOM is part of the strategic game engine itself.

The chart should say or imply that:

- DLOM is applied after the clean integrated contract value is determined.

### Caption draft

`The primary reported fair value is the clean integrated contract value adjusted by the central DLOM estimate. DLOM is treated as a separate marketability adjustment rather than as part of the core strategic exercise engine.`

### QA checks

1. The central case must be the same restriction horizon used in the notebook's primary reported value.
2. The waterfall must reconcile exactly to the notebook's reported post-DLOM value.
3. The chart must distinguish clean value from post-DLOM value.

### Reference check

The other agent should confirm that the post-DLOM Olympus value reconciles to the notebook's current primary reported output before finalizing the chart.

---

## PH-Method-06: Market Sensitivity Heatmap

### Priority

Appendix only.

### Purpose

This chart shows how pre-DLOM Olympus value changes across the market assumption grid already embedded in the notebook.

### Audience question answered

- How sensitive is the clean contract value to volatility and the risk-free rate?

### Required data inputs

Generate from the notebook by running:

- `run_vgame_model_scenario(vol, rf, allow_partial_calls=ALLOW_PARTIAL_CALLS, tie_priority_to_olympus=GAME_TIE_PRIORITY_TO_OLYMPUS)`

Use the notebook's existing grid:

- `vol_range = [0.15, 0.20, 0.25, 0.30]`
- `rf_range = [0.04, risk_free_rate, 0.06]`

### Required data table schema

Create `market_sensitivity.csv` with columns:

- `asset_volatility`
- `risk_free_rate`
- `value_total_usd`
- `value_total_usd_m`
- `is_base_case`

### How to build it

1. Use a heatmap with volatility on the y-axis and risk-free rate on the x-axis.
2. Put the pre-DLOM Olympus value in USD millions inside each cell.
3. Outline the base-case cell with a thick border.
4. Use a single-hue sequential palette or a restrained diverging palette.
5. Add a subtitle that this is pre-DLOM and that the core contract value is deterministic on the tree for a given parameter set.

### Caption draft

`The clean contract value is sensitive to market inputs, particularly the level of asset volatility and the discounting environment. The base case is highlighted.`

### QA checks

1. The base-case cell must match the notebook's current pre-DLOM Olympus value.
2. The chart must be labeled pre-DLOM.
3. The chart must not imply that these are confidence intervals.

---

## PH-Method-07: Structural Sensitivity

### Priority

Appendix only.

### Purpose

This chart shows how much value changes when contract-structure assumptions change while market inputs remain fixed.

### Audience question answered

- How much does value depend on partial-call flexibility?
- How much does value depend on the same-bucket priority assumption?

### Required data inputs

Generate from the notebook's structural cases:

- Base case: partial calls, 50/50 tie priority
- Full-block only, 50/50 tie priority
- Partial calls, Olympus 25% tie priority
- Partial calls, Olympus 75% tie priority

Using the existing helper:

- `run_vgame_model_scenario(vol=asset_volatility, rf=risk_free_rate, allow_partial_calls=..., tie_priority_to_olympus=...)`

### Required data table schema

Create `structural_sensitivity.csv` with columns:

- `case_label`
- `allow_partial_calls`
- `tie_priority_to_olympus`
- `value_total_usd`
- `value_total_usd_m`
- `delta_vs_base_usd_m`
- `is_base_case`

### How to build it

Preferred structure:

1. Build a horizontal bar chart of `delta_vs_base_usd_m`.
2. Keep the base case at zero and show the other cases relative to it.
3. Use one visual treatment for `partial calls on/off` changes and another for `tie priority` changes.
4. Add a narrow right-hand annotation column showing the absolute value in USD millions.

Alternative structure:

1. Grouped bar chart of absolute USD millions by case.

### Caption draft

`Structural assumptions matter because the contract value depends on both the feasible call menu and the modeled treatment of same-bucket timing in the overlap region.`

### QA checks

1. The base case must match the main pre-DLOM value.
2. The case labels must be externally understandable; avoid internal shorthand.
3. The chart must not imply that these are statistically estimated parameter distributions.

---

## PH-Method-08: Admissible Call Matrix

### Priority

Technical appendix only.

### Purpose

This is the auditor-friendly companion to the residual-state ladder. It shows the full call menu implied by the state grid and contract constraints.

### Audience question answered

- What exact target states are contract-feasible from each current residual state?

### Required data inputs

Generate directly from:

- `STATE_PCTS`
- `allowed_call_targets(current_pct, ALLOW_PARTIAL_CALLS)`

Use all positive current states in the grid.

### Required data table schema

Create `admissible_call_matrix.csv` with columns:

- `current_pct`
- `target_pct`
- `call_size_pct`
- `is_admissible`

### How to build it

1. Use rows for current state and columns for target state.
2. Fill a cell if the transition is admissible.
3. Put the call size inside the cell, for example `8%`.
4. Use a distinct fill for transitions to zero.
5. Leave inadmissible cells blank or lightly hatched.
6. Sort rows descending from 25 to 7.
7. Sort columns descending from 25 to 0.

### Caption draft

`The admissible call menu is constrained by the minimum-tranche rule, the residual-floor rule, and the state grid. The matrix shows which target residual states are feasible from each current residual state.`

### QA checks

1. No row may include a target equal to the current state.
2. No cell may imply a residual state below 7% unless the target is 0%.
3. No cell may imply a call smaller than 5%.

---

## 9. What Not to Build

The other agent should explicitly avoid the following visual ideas unless specifically asked for an internal-only appendix:

1. A full recombining stock tree with all nodes shown.
2. A spaghetti diagram connecting all residual states across all time periods.
3. A Sankey chart with arbitrary flow widths implying probabilities that the model has not exported.
4. A single chart combining timeline, residual-state logic, overlap rules, DLOM, and sensitivities.
5. A payoff diagram that makes the contract look like a plain vanilla call or put.

---

## 10. Recommended Implementation Order

The other agent should implement in this order:

1. PH-Method-01 Exercise Timeline
2. PH-Method-02 Residual-State Ladder
3. PH-Method-03 Overlap Decision Logic
4. PH-Method-04 Contract Value by Titan Remaining-State
5. PH-Method-05 DLOM Bridge
6. PH-Method-08 Admissible Call Matrix
7. PH-Method-06 Market Sensitivity Heatmap
8. PH-Method-07 Structural Sensitivity

This order matters because the first five charts are the ones most likely to be used in the main methodology note or client pack. The last three are more technical and belong in an appendix unless specifically requested.

---

## 11. Reasonableness Checks Before Final Export

Before the other agent declares the chart pack complete, it should confirm all of the following:

1. The timeline chart reflects the exact window boundaries in the notebook.
2. The residual-state charts reflect the actual `allowed_call_targets` output rather than a simplified narrative invented by hand.
3. The overlap chart presents same-bucket handling as a monthly-grid approximation, not as simultaneous legal completion.
4. The state-value chart reconciles the 25% bar to the notebook's clean pre-DLOM Olympus value.
5. The DLOM bridge reconciles exactly to the notebook's primary reported post-DLOM value.
6. The market and structural sensitivity charts are labeled as appendix exhibits.
7. No chart title, caption, or subtitle uses internal model-history language.

---

## 12. Optional Extension if Time Allows

If the other agent has time and the main pack is already complete, one additional chart could be useful:

### PH-Method-09: Value Bridge from Standalone Intuition to Linked-Contract Intuition

This should not compare model versions. It should be a purely conceptual chart showing why the final methodology must track residual state rather than a fixed notional block.

It should be explanatory only and should not contain separate valuation figures from any prior internal build.

This extension is optional and should be excluded if there is any risk it will reintroduce version-history language.