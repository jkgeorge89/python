# Outputs And Interpretation

## Why multiple output files exist

The model produces several outputs because each file answers a different question.

No single file can simultaneously show:

- convergence quality;
- strike mechanics;
- full policy geometry; and
- human-readable example paths.

The outputs should therefore be read as complementary, not redundant.

## 1. Convergence output

File:

`project_horizon_continuous_state_qvi_results.csv`

Purpose:

Show how the value changes as the price grid is refined.

Current headline numbers:

- 801 prices: USD 145.864m;
- 1001 prices: USD 144.227m;
- 1201 prices: USD 144.076m.

Interpretation:

The price-grid refinement is stabilizing. The 1201-price case is the current preferred reference value.

## 2. Strike schedule output

File:

`project_horizon_continuous_state_qvi_strike_schedule.csv`

Purpose:

Show the deterministic day-by-day strike path used by the model.

Key columns include:

- time step and time in years;
- whether call or put is live;
- coupon bucket in force;
- implied one-step model roll; and
- strike at completion and strike in present-value terms.

Interpretation:

This file is the clean answer to the question, "what strike is the model using on a given day?"

## 3. Representative path output

File:

`project_horizon_continuous_state_qvi_sample_paths.csv`

Purpose:

Provide readable policy traces along three representative deterministic reporting paths.

Important caveat:

The labels `low`, `base`, and `high` are not separate solved scenarios.

They are reporting paths drawn from the already-solved policy.

Interpretation:

This file is for intuition, not valuation.

## 4. Checkpoint output

File:

`project_horizon_continuous_state_qvi_policy_checkpoints.csv`

Purpose:

Summarize policy behavior at selected dates, representative paths, and remaining-stake levels.

Interpretation:

This is a management-review file. It helps you see how the policy changes at key dates without opening the full surfaces.

## 5. Full value surface export

File:

`project_horizon_continuous_state_qvi_value_surface_25pct.csv`

Purpose:

Show the full value surface for the 25% starting ownership sheet.

How to read it:

- rows are price states;
- columns are time states; and
- each cell is Olympus value at that `(time, price, 25%)` state.

Important warning:

The row labels are the fixed full-horizon price grid. They are not a realized price path.

## 6. Full action surface export

File:

`project_horizon_continuous_state_qvi_action_surface_25pct.csv`

Purpose:

Show the optimal action at every `(time, price, 25%)` node on the 25% sheet.

Typical cell labels are:

- `wait`;
- `call->0.00%`;
- `put->0.00%`; and
- potentially other call targets in future exports if those dominate somewhere on the exported sheet.

Interpretation:

This is the cleanest file for visualizing exercise regions.

## What the rows and columns do not mean

The surfaces do not show a path through time.

Each column is a different date.

Each row is a different price state that is available at every date.

So the surface is a state map, not a scenario trace.

This is why an early column may contain both very low and very high rows.

## How to find the current spot row

The initial spot price is approximately USD 577.192248.

That row is the most relevant row for discussing the valuation date.

If you want to read the policy at the valuation date on the 25% sheet, the row nearest USD 577.19 is the row that corresponds to the current market state.

## Why the representative paths can disagree with isolated cells you inspect

The representative paths move through the state map along one deterministic reporting trajectory.

A manually inspected surface cell may sit at a price state never visited by those reporting paths.

That is normal.

The surface is the full map. The representative paths are a few narrated walks through that map.

## Recommended workflow for review

If the goal is understanding rather than debugging, the best order is:

1. read the strike schedule to understand the economics of the strike over time;
2. read the checkpoint table to see broad policy behavior at key dates;
3. open the 25% action surface to see the full boundary geometry; and
4. use the 25% value surface only when you want the value attached to a specific state.

## Bottom line

The outputs answer different questions.

The surfaces are the full state map.

The checkpoint and sample-path files are explainability aids.

The strike schedule is the deterministic contract mechanics.

The convergence file is model-quality evidence.