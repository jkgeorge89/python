# Project Horizon - Method Comparison
**Prepared for:** [MD Name]
**Valuation date:** December 31, 2025
**Subject:** Comparison of the main Project Horizon valuation methodologies from the original proxy to the continuous-state QVI approach

---

## Executive Summary

The Project Horizon work progressed through five main valuation stages:

1. the original proxy `call minus put` Monte Carlo;
2. the linked-contract FULL Monte Carlo;
3. the monthly 1.0% game-theory tree;
4. the business-day higher-resolution tree; and
5. the business-day continuous-state QVI methodology.

The large conceptual jump happened between the original proxy and the linked-contract formulations.

After the model became contract-faithful, the later refinements mainly tightened the number rather than changing the story.

---

## 1. Method Comparison Table

| Stage | Core framing | Numerical engine | Time grid | Call menu from 25% state | Put exposure | Pre-DLOM value (USD m) | Post-DLOM value (USD m) | Main message |
|---|---|---|---|---|---|---:|---:|---|
| **Proxy** | Fixed-block `call minus put` on the same 25% stake | Least-squares Monte Carlo | Monthly | Effectively full 25% block option logic rather than linked residual-state control | Treated as put on the same fixed 25% block | **43.7** | **34.5** | Simple but not contract-faithful; materially understates value because it overstates the persistent put block and does not model linked residual ownership |
| **FULL** | Linked contract with coarse residual-state ladder | Backward-induction Monte Carlo | Monthly | From 25%: call 5% -> 20%, 10% -> 15%, 15% -> 10%, or 25% -> 0% | Put tested on the actual remaining state | **139.6** | **110.2** | First contract-faithful linked model; major conceptual correction versus proxy |
| **Game Theory** | Linked strategic contract with overlap solved as a game | Deterministic recombining stock tree | Monthly | From 25%: partial calls 5%-18% in 1% steps, or 25% -> 0% | Put tested on residual stake; overlap solved strategically | **140.936** | **111.2** | Monthly + 1.0% strategic tree; valid rough approximation once the contract framing is correct |
| **High-Resolution Tree** | Same strategic framing, finer numerical grid | Deterministic recombining stock tree | Business-day | From 25%: partial calls 5.0%-18.0% in 0.5% steps, or 25.0% -> 0.0% | Put tested on residual stake | **142.061** | n/a | Shows that finer time steps and finer control grid add only a modest uplift |
| **Continuous-State QVI** | Linked strategic intervention problem on dense state space | Continuous-state dynamic programming / QVI-style solver | Business-day | From 25%: partial calls 5.00%-18.00% in 0.25% steps, or 25.00% -> 0.00% | Put tested on residual stake at each state point | **144.076** | n/a | Most refined practical methodology built so far; adds a few million rather than changing the whole valuation story |

---

## 2. Value Bridge Across Methods

| Method | Pre-DLOM value (USD m) | Change vs prior stage (USD m) | Commentary |
|---|---:|---:|---|
| Proxy | **43.7** | — | Fixed-block option decomposition; not directly contract-faithful |
| FULL | **139.6** | **+95.9** | Large correction from modeling the linked residual-state mechanics properly |
| Game Theory monthly 1.0% tree | **140.936** | **+1.336** | Strategic tree refinement with finer 1% call-size menu |
| High-resolution tree | **142.061** | **+1.125** | Business-day timing and 0.5% state ladder |
| Continuous-state QVI | **144.076** | **+2.015** | Dense price-state / 0.25% control refinement |

---

## 3. What This Means In Plain English

The key takeaways are:

1. The original proxy was not wrong because Monte Carlo is bad; it was wrong because it valued the instrument as though the call and put were independent claims on the same permanent 25% block.
2. The FULL model fixed the main economic issue by making the contract linked and state-dependent.
3. The monthly 1.0% game-theory tree is already a credible rough approximation because it solves the right strategic problem.
4. The high-resolution tree and the continuous-state QVI mainly reduce discretization error.
5. The additional refinement from the monthly 1.0% strategic tree to the QVI methodology is approximately **USD 3.140M**, or about **2.23%**.

So the practical answer is:

- the **big** valuation change came from moving away from the naive fixed-block proxy; and
- the later technical refinements are important, but they move the number by low single-digit millions rather than by tens of millions.

---

## 4. Short MD Summary

`The original proxy materially understated value because it treated the instrument as a simple fixed-block call less put. Once the contract was modeled properly as a linked residual-state instrument, value increased to about USD 140M pre-DLOM. Subsequent refinements from the monthly 1.0% strategic tree to business-day and then continuous-state QVI added only a few million more, taking the value to about USD 144.1M.`
