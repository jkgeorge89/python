# Project Horizon - Continuous State QVI Results

## Purpose

This note records the first stable output from the separate continuous-state dynamic-programming reference solver.

This workstream is designed to be the closest practical approximation in the current Python setup to a more academically rigorous continuous-state strategic valuation.

It does **not** replace the original binomial game-theory methodology in `../game_theory/`. It is a separate reference method used to test whether a more continuous formulation changes the value enough to matter.

## What This Solver Changes

Relative to the original binomial game-theory notebook, this workstream changes the numerical method in three main ways:

- the stock-price state is represented on a dense log-price grid rather than a recombining tree;
- continuation values are propagated on a business-day time grid using a dynamic-programming expectation operator; and
- the remaining Titan stake is controlled on a finer **0.25%** grid from **25.00%** down to **7.00%**, plus **0%**.

The economic contract assumptions themselves were held fixed:

- same SPA-derived base price;
- same call and put coupon schedules;
- same call and put exercise windows;
- same 5% minimum call tranche and 7% residual floor;
- same zero completion-lag simplifying assumption; and
- same 50% same-bucket tie-priority approximation.

So this note addresses numerical refinement, not a new legal interpretation of the contract.

## Stable Convergence Run

| Scenario | Value to Olympus (USD m) | Per option share (USD) | Delta vs original 140.936M monthly binomial value (USD m) | Delta vs high-resolution tree (USD m) |
|---|---:|---:|---:|---:|
| Daily QVI, 0.25% / 801 prices | 145.864 | 105.240 | 4.928 | 3.803 |
| Daily QVI, 0.25% / 1001 prices | 144.227 | 104.058 | 3.291 | 2.166 |
| Daily QVI, 0.25% / 1201 prices | 144.076 | 103.950 | 3.140 | 2.015 |

## Preferred Reference Case

The preferred current reference point from this workstream is:

- **Daily QVI, 0.25% ownership grid, 1201 price nodes**
- **Value to Olympus before DLOM: USD 144.076M**
- **Value per option share before DLOM: USD 103.950**

This sits:

- approximately **USD 3.140M** above the original **USD 140.936M** monthly binomial game-theory value; and
- approximately **USD 2.015M** above the separate **USD 142.061M** high-resolution tree result.

## Interpretation

The main conclusion is that the more continuous-state reference method does increase the value, but not by a transformative amount once the numerical scheme is refined enough to stabilize.

The stable uplift versus the original monthly binomial value is approximately **2.23%**.

The stable uplift versus the separate business-day higher-resolution tree is approximately **1.42%**.

That means the answer to “is it worth it?” is likely:

- **yes**, if the mandate is to push the methodology toward the most technically defensible continuous-state reference available in-house; but
- **no**, if the expectation is that the value should move by tens of millions rather than a low single-digit millions amount.

## Numerical Stability Check

The last refinement step from **1001** to **1201** price nodes changed the value by only **USD 0.151M**, or about **0.10%** of the 1001-node result.

That suggests the current reference value is numerically close to stabilized on the chosen business-day and 0.25% control grid.

As a plain-vanilla validation check, the same expectation operator at the 1201-node setting overprices a 1-year at-the-money European call by only about **0.18%** versus Black-Scholes, which is small enough for the current Project Horizon reference purpose.

## Output Files

- `project_horizon_continuous_state_qvi.py`
- `project_horizon_continuous_state_qvi_results.csv`
