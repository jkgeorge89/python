# Project Horizon - High Resolution Tree Results

## Purpose

This note records the first output from the separate higher-resolution strategic tree workstream.

It does **not** replace the original binomial game-theory methodology in `../game_theory/`.

The purpose of this workstream is narrower: test whether a finer time grid and finer remaining-state grid materially change the pre-DLOM integrated contract value.

## What Was Held Fixed

The high-resolution tree run carries forward the same core economics used in the original game-theory notebook:

- same SPA-derived base price;
- same call and put coupon schedules;
- same call and put exercise windows;
- same 5% minimum call tranche and 7% residual floor;
- same zero completion-lag simplifying assumption; and
- same 50% same-bucket tie-priority approximation.

So this is not a new contract view. It is a higher-resolution numerical implementation of the same strategic framing.

## What Changed

The separate high-resolution method increases numerical resolution in two ways:

- time grid increased from monthly to weekly and then business-day steps; and
- remaining-state grid increased from 1.0% steps to 0.5% steps.

This remains a recombining strategic tree, not a Monte Carlo engine.

## Pre-DLOM Results

| Scenario | Value to Olympus (USD m) | Per option share (USD) | Delta vs current monthly build (USD m) | Delta vs current monthly build (%) |
|---|---:|---:|---:|---:|
| Current monthly tree, 1.0% state grid | 140.936 | 101.684 | 0.000 | 0.000% |
| Weekly tree, 1.0% state grid | 141.857 | 102.348 | 0.920 | 0.653% |
| Business-day tree, 1.0% state grid | 142.061 | 102.496 | 1.125 | 0.798% |
| Business-day tree, 0.5% state grid | 142.061 | 102.496 | 1.125 | 0.798% |

## Interpretation

The first convergence run suggests that the original monthly simplification is **not** driving the valuation materially.

Moving from the current monthly strategic tree to a business-day strategic tree increases the clean contract value by approximately **USD 1.1M**, or roughly **0.8%**.

Refining the remaining-state grid from **1.0%** to **0.5%** after moving to a business-day time grid produced no further change in the reported value at the displayed precision.

That is a useful result because it means the original binomial game-theory build appears directionally robust to finer numerical resolution, at least under the current core assumptions.

## Preferred Output From This Workstream

If this separate high-resolution tree workstream is cited, the preferred current reference point is:

- **Business-day tree, 0.5% state grid**
- **Value to Olympus before DLOM: USD 142.061M**
- **Value per option share before DLOM: USD 102.496**

## Output Files

- `project_horizon_high_resolution_tree.py`
- `project_horizon_high_resolution_tree_results.csv`
