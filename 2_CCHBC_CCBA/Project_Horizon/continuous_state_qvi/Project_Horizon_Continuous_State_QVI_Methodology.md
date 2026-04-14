# Project Horizon - Continuous State QVI Methodology
**Prepared for:** [MD Name]
**Valuation date:** December 31, 2025
**Model basis:** Continuous-state dynamic-programming solver for the linked call / put Option Agreement over the residual 25% CCBA stake
**Subject:** Methodology note for the continuous-state QVI valuation

---

## Executive Overview

This note explains the continuous-state QVI methodology in plain English and sets out how it should be described to management, the client, and any technical reviewer.

The central point is simple:

- the signed Project Horizon agreement is not a plain call option;
- it is not a plain put option;
- it is not best understood as a simple call-minus-put package on a fixed 25% block; and
- once prior call exercise can reduce Titan's later putable stake, the contract becomes a linked strategic problem.

The continuous-state QVI method values that linked strategic structure directly on a denser continuous-state dynamic-programming framework on a business-day grid.

In plain English, the QVI methodology asks:

`If we keep the same contract logic but solve it on a much finer state space, does the answer move enough to matter?`

That is why this method is best presented as the most technically refined valuation methodology currently adopted for this contract.

---

## 1. What QVI Means in This Context

QVI stands for **quasi-variational inequality**.

That term sounds more intimidating than it needs to be. In this context it just means the value of the contract is determined by two things at once:

1. **Passive evolution of the underlying equity value over time**; and
2. **Active intervention rights**, meaning one or both parties can choose to act rather than wait.

That is exactly what happens here.

Between exercise dates, the equity value evolves stochastically.

At exercise opportunities:

- Olympus may wait or call an admissible amount of the remaining Titan stake; and
- Titan may wait or, once its window is live, put the residual stake.

So the valuation is not only a question of forecasting price evolution. It is also a question of optimal strategic intervention.

That is the type of problem for which QVI language is academically natural.

---

## 2. Why the Contract Naturally Leads to a QVI-Type Framework

The contract has three features that make a QVI-style formulation appropriate.

### 2.1 The relevant stake is state-dependent

If Olympus exercises part of its call early, Titan's later put does not remain a claim on the original 25% block.

It becomes a claim only on the residual shares still held by Titan.

So the remaining Titan stake must be tracked as a state variable.

### 2.2 The amount of call exercise is itself part of the problem

The question is not only:

- should Olympus act now or wait?

It is also:

- if Olympus acts now, how much should it call?

That means the model must compare a menu of admissible intervention sizes, not just a single exercise/no-exercise decision.

### 2.3 The overlap period creates strategic interaction

During the overlap period, both parties may have live rights.

That creates a strategic max/min problem rather than a single-holder stopping problem.

So the contract is better framed as a linked strategic intervention problem than as a standalone option valuation.

---

## 3. Core Modeling Choices

The QVI methodology is designed to remain faithful to the signed contract.

The following economics are built directly into the method:

- SPA-derived base equity price;
- contractual call and put coupon schedules;
- contractual call and put exercise windows;
- 5% minimum call tranche;
- 7% residual floor unless the position goes to zero;
- zero completion-lag simplifying assumption; and
- 50% same-bucket tie-priority approximation.

The methodology uses the following numerical representation:

Specifically, it changes three things:

1. **Time resolution**: business-day steps.
2. **Price-state resolution**: a dense log-price grid.
3. **Ownership-state resolution**: the remaining Titan stake is controlled on a 0.25% grid.

So the right way to describe the method is:

`contract-faithful strategic valuation on a fine dynamic-programming state space`

---

## 4. How the Continuous-State Solver Works

The method solves the value function backward from maturity to the valuation date.

At each business-day step it does three things.

### 4.1 Carry forward the continuation value

The future value is projected back one day under the risk-neutral equity process using a numerical expectation operator on a dense log-price grid.

### 4.2 Evaluate the available actions

At each state the model evaluates the contract-feasible action set.

From Olympus's perspective, that means comparing:

- waiting; and
- each admissible call size on the fine ownership grid.

From Titan's perspective, once its put is live, that means comparing:

- waiting; and
- putting the full residual stake still held in that state.

### 4.3 Solve the overlap node strategically

If both call and put rights are live at the same modeled date, the node is solved as a stage game.

In this implementation:

- Olympus chooses the admissible action that maximizes Olympus value; and
- Titan chooses the response that minimizes Olympus value, which is equivalent to maximizing Titan value under the shared assumptions.

That is how the strategic interaction enters the daily dynamic-programming recursion.

---

## 5. What “Continuous-State” Means Here and What It Does Not Mean

The method is closer to a continuous-time and continuous-state formulation than a coarse discrete valuation, but it is still a numerical approximation.

That distinction matters.

### 5.1 What it does mean

- The stock price is represented on a dense continuous grid rather than only at a sparse discrete set of nodes.
- Time is represented on a business-day grid rather than monthly buckets.
- The remaining stake is represented on a finer 0.25% control grid.

### 5.2 What it does not mean

- It is **not** a literal closed-form continuous-time solution.
- It does **not** solve over every theoretically possible fractional share count.
- It does **not** remove the need for convergence testing or numerical validation.

So the academically accurate way to phrase it is:

`This is a continuous-state dynamic-programming approximation to the underlying QVI problem.`

---

## 6. Why This Method Is More Academic

This method is more academic for two reasons.

### 6.1 It matches the structure of the mathematical problem more directly

The underlying contract is a strategic intervention problem with a stochastic state variable.

That is naturally described by dynamic programming and QVI-style language.

The QVI methodology therefore sits closer to the abstract mathematical form of the problem than a coarse discrete model.

### 6.2 It reduces some discretization artifacts

Any coarse discrete model must approximate:

- intra-month timing;
- stock-price evolution on a simplified grid; and
- partial exercise on a coarser ownership grid.

The continuous-state QVI methodology reduces those approximations materially.

---

## 7. How to Explain This to an MD

The shortest management explanation is:

`We valued the linked option agreement on a business-day and continuous-price dynamic-programming grid so that both price evolution and strategic exercise behavior are represented on a much finer numerical state space.`

If the MD asks what QVI means, the most useful answer is:

`It is the mathematical framework used when value depends both on market evolution and on the parties' rights to intervene strategically rather than just wait.`

If the MD asks whether this is a different deal view, the answer is:

`No. It is the same deal mechanics solved on a more technically refined numerical grid.`

If the MD asks whether it matters economically, the answer is:

`Yes. The QVI valuation produced a pre-DLOM value of USD 144.076M under the current assumptions.`

---

## 8. How to Explain This to the Client

For a client audience, the message should stay commercial rather than mathematical.

Suggested wording:

`Because the option agreement is a linked strategic contract rather than a simple standalone option, we valued it using a continuous-state dynamic-programming formulation. This methodology uses a business-day grid, a dense stock-value state space, and a fine representation of partial exercise so that the linked call / put mechanics are modeled directly rather than through a coarser numerical approximation.`

That wording gives the client the message they need:

- the work was technically serious;
- the valuation framework was designed directly around the contract mechanics; and
- the method is aligned with a more academic strategic valuation approach.

---

## 9. Current Project Horizon Result

The current stable case under this methodology is:

- business-day time grid;
- 0.25% ownership-state grid;
- 1201 price nodes on the continuous log-price grid.

That produced a pre-DLOM value to Olympus of **USD 144.076M**.

The key implication is that the more academic method does increase value, but not by a transformative amount.

---

## 10. Key Limitations

Even this more academic method still contains assumptions and approximations that should be disclosed clearly.

The most important are:

- zero completion lag in the primary valuation;
- same-bucket tie handling remains an approximation to unresolved exact notice ordering;
- regulatory suspension or lapse mechanics remain outside the primary clean value unless modeled explicitly;
- the underlying equity process remains a stylized risk-neutral process rather than a full fundamental valuation engine; and
- the continuous-state solver is still a numerical approximation, not a literal closed-form solution.

These are not defects unique to the QVI method. They are normal model-governance boundaries that should be stated openly.

---

## 11. Bottom Line

The QVI methodology is the most academically correct framework currently built in the Project Horizon repository because it treats the contract as what it really is: a strategic linked intervention problem with a stochastic underlying and state-dependent residual ownership.

At the same time, it is materially more complex than a coarser discrete implementation.

The practical Project Horizon conclusion is therefore balanced:

- the QVI framework is technically stronger;
- it required a much more demanding numerical setup; and
- under the current assumptions, it produced a pre-DLOM value of **USD 144.076M**.

That means the QVI methodology can be presented as a standalone strategic valuation approach for the linked option agreement, with its own assumptions, outputs, and governance boundaries.
