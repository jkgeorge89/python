# Project Horizon - QVI Methodology Overview

## What this model is trying to answer

The model is trying to answer one practical question:

What is the value of the linked Olympus call / Titan put agreement once we respect the fact that Olympus can reduce Titan's future residual stake before Titan decides whether to put?

That is the whole reason the problem becomes more complicated than a simple call minus put framework.

If Olympus calls part of Titan's stake early, Titan does not still own the original 25% block later.

Titan only owns the residual stake that remains after Olympus's earlier actions.

That means the future state of the contract depends on today's exercise decision.

## Why the model has three dimensions

The model tracks three things at once:

1. time;
2. price per share; and
3. Titan's remaining stake.

That third variable is the source of most of the confusion, but it is also the core of the contract.

If you ignore remaining stake as a state variable, you are no longer solving the signed deal.

## How to picture the model

The cleanest picture is not a tree.

It is a stack of rectangular sheets.

Each sheet is one remaining-stake level.

Inside each sheet:

- rows are price states;
- columns are time states; and
- each cell is the value or action at that exact state.

So the full object is:

`Value(time, price, remaining stake)`

The 25% value and action surfaces that open in Excel are only one sheet from that larger stack.

## What the solver is actually doing at one node

Suppose the current state is:

- time = Year 4.0;
- price = USD 650 per share; and
- Titan remaining stake = 25%.

The solver does not ask, "which sheet do I like best in the abstract?"

It asks, from the current 25% sheet, what actions are allowed right now?

Those actions are:

- wait and stay on the 25% sheet;
- call and jump to a lower residual-stake sheet if that call size is contract-feasible; or
- if Titan's put is live, allow for Titan's put decision, which can jump the state to 0%.

So the solver compares feasible transitions out of the current sheet.

## Why the model is not Monte Carlo and not a binomial tree

It is not Monte Carlo because it is not simulating thousands of random paths and then fitting a stopping rule.

It is not a binomial tree because it does not branch up and down across a Pascal-triangle lattice.

Instead it uses:

- a fixed business-day time grid;
- a fixed log-price grid; and
- a fixed ownership-state grid.

That makes it a grid-based dynamic-programming solver.

## What the current implementation looks like

The current stable reference case uses:

- 252 model steps per year for 6 years, giving 1512 time steps plus `t0`;
- 1201 price nodes on the fixed log-price grid;
- a 0.25% ownership grid from 25.00% down to 7.00%, plus 0.00%; and
- contractual call and put strike schedules rolled on the same daily model grid.

That produces 74 ownership states in total.

## What the outputs mean

There are four different output families and they should not be mixed up.

- `project_horizon_continuous_state_qvi_results.csv` is the convergence summary across different price-grid sizes.
- `project_horizon_continuous_state_qvi_strike_schedule.csv` is the deterministic daily strike schedule.
- `project_horizon_continuous_state_qvi_sample_paths.csv` and `project_horizon_continuous_state_qvi_policy_checkpoints.csv` are explainability traces, not the full state space.
- `project_horizon_continuous_state_qvi_value_surface_25pct.csv` and `project_horizon_continuous_state_qvi_action_surface_25pct.csv` are the full Excel-friendly surfaces for the 25% ownership sheet.

## Headline behavioral picture from the current 25% sheet

The current 25% action surface behaves as follows.

- Before Year 3.0, the full sheet is `wait` because no exercise right is live.
- At Year 3.0, the sheet is still `wait` almost everywhere; only the most extreme high-price rows call.
- By Year 3.496, the 25% sheet has become all `call->0.00%`.
- At Year 4.0, the 25% sheet is effectively all call, with a one-row numerical tie around the strike.
- Just after Year 5.0, once the call window closes, the sheet becomes a `put` versus `wait` region.
- At Year 6.0, the sheet is all `put->0.00%`.

That alone already tells you an important economic story.

Before the overlap starts, Olympus mostly waits. During the overlap, Olympus often calls to extinguish Titan's residual put exposure. After the call window closes, the remaining problem is Titan's put versus wait decision.

## Why this methodology exists

This methodology exists because the contract is a linked strategic control problem.

The question is not just whether a call is in the money or a put is in the money.

The real question is:

What is the value of waiting versus changing the future state of the contract now?

That is what the full methodology report explains in detail.