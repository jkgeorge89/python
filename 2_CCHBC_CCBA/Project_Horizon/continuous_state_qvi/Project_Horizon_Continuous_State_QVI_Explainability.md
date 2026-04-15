# Project Horizon - Continuous State QVI Explainability Outputs

## Why these files exist

The QVI workstream is **not** a Monte Carlo path simulation.

That means there are no 1,000,000 simulated paths to sample in the same way you would sample a Least-Squares Monte Carlo engine.

Instead, the meaningful audit-facing outputs are:

1. representative **policy path traces**; and
2. representative **policy checkpoint tables**.

These files are intended to show, in a transparent CSV format, what the QVI solver is doing at selected points in time, price, and remaining-stake space.

## Output files

- `project_horizon_continuous_state_qvi_sample_paths.csv`
- `project_horizon_continuous_state_qvi_policy_checkpoints.csv`
- `project_horizon_continuous_state_qvi_strike_schedule.csv`
- `project_horizon_continuous_state_qvi_value_surface_25pct.csv`
- `project_horizon_continuous_state_qvi_action_surface_25pct.csv`

## How to read them

### 1. Strike schedule

The strike-schedule file is the deterministic term structure of the contractual strike on the model grid.

It exists because the strike is fully knowable at every modeled day once you specify:

- the SPA base price;
- the contractual coupon schedule; and
- the completion-lag assumption.

For each business-day step, the file shows:

- whether the call and put windows are live;
- the annual coupon rate currently driving the call and put strike accrual;
- the implied one-model-day roll on the 252-step grid; and
- the resulting call and put strike levels, both at completion and in present-value terms.

The current implementation uses a **252-step business-day year** and samples the contractual annual coupon schedule on that grid.

That means that within a coupon year the modeled daily strike roll is:

`daily roll = (1 + annual coupon)^(1/252) - 1`

So there is no hidden mismatch in the code between "annual coupon" and "daily trading steps". The annual schedule is being applied fractionally on the daily model grid.

What is still a modeling assumption is the **day-count basis**. Right now the solver treats one model year as 252 equal business-day steps. If the legal strike accrual should instead be tied to actual calendar days or a different contractual day-count convention, that should be changed explicitly.

### 2. Sample paths

The sample-path file is **not** a random Monte Carlo sample.

It contains three deterministic representative price paths, and `scenario_label` should really be read as a **representative path label**, not as a separate valuation scenario.

The three labels are:

- `low` = roughly a one-sigma-below path;
- `base` = the central drift path; and
- `high` = roughly a one-sigma-above path.

There is no separate `mid` path in the current outputs. `base` is the middle path.

The new `representative_path_zscore` column makes this explicit:

- `low = -1.0`;
- `base = 0.0`; and
- `high = +1.0`.

For each business-day step, the file shows:

- the sampled price per share;
- the representative path z-score;
- Titan's stake before the decision;
- whether the call and/or put is live;
- the wait value;
- the best call target and associated value;
- the put value if live; and
- the optimal action implied by the QVI recursion.

That gives a start-to-finish trace of how the policy reacts under low, base, and high market states.

### 3. Policy checkpoints

The checkpoint file is a compact review table built from those same representative path labels at selected years and selected Titan stakes.

It is designed for MD, client, and audit review.

The most useful checkpoint years are:

- `t0`;
- Year 3.0 when the call first goes live;
- Year 3.5 when the overlap begins;
- Year 5.0 when the call window closes; and
- Year 6.0 at final put expiry.

The most useful remaining-stake states are:

- 25.0%;
- 20.0%;
- 15.0%;
- 10.0%; and
- 7.0%.

It is therefore a **thin reporting slice**, not the full state space.

### 4. Full 25% state surface

The value-surface and action-surface files are the closest QVI equivalent to a daily tree that can be opened in Excel.

They show, for the initial 25.0% Titan stake state:

- rows = price nodes;
- columns = business-day steps; and
- each cell = either the value at that state or the optimal action at that state.

This is **not** a Pascal triangle or a recombining up/down lattice.

It is a rectangular price-by-time grid for one ownership state, which is the correct visual representation of the QVI solver.

These two files do **not** depend on the `low` / `base` / `high` reporting labels. They are full-grid outputs for the 25% remaining-stake sheet.

## Practical audit message

If the question is "show me what the Python model is doing," the right answer for the QVI workstream is:

- show the deterministic strike schedule explicitly;
- show representative path traces rather than random Monte Carlo paths; and
- show checkpoint tables that compare wait / call / put at key states.

That is the honest equivalent of a path sample for a grid-based dynamic-programming solver.
