# Project Horizon - QVI Methodology Selection
**Prepared for:** [MD Name]
**Valuation date:** December 31, 2025
**Subject:** Why the continuous-state QVI approach is selected, and why simpler approaches are insufficient

---

## Executive Summary

This note explains the methodology choice for the Project Horizon option valuation.

The key conclusion is:

- a simple `call minus put` valuation is not contract-faithful;
- a naive Monte Carlo simulation is not, by itself, a solution to the strategic exercise problem;
- a monthly + 1.0% binomial / dynamic-programming build is a valid rough approximation because it captures the core linked-contract mechanics; and
- a business-day + 0.25% continuous-state QVI-style solver is the preferred refined methodology because it materially reduces discretization error without attempting an impossible or unnecessary literal continuous-time exact solve.

So the methodology decision is not driven by mathematical elegance for its own sake. It is driven by what the contract actually requires the valuation to solve.

---

## 1. The Valuation Problem We Actually Have

The Project Horizon agreement is not a standalone option on a fixed 25% block.

The valuation problem has four defining features:

1. Olympus has a call right that can be exercised partially, subject to contractual thresholds.
2. Titan has a put right that applies only to the shares Titan still holds at that time.
3. Olympus's earlier call exercise changes Titan's later putable block.
4. During the overlap period, both sides may prefer to act, so the valuation problem is strategic rather than passive.

That means the value depends on:

- time;
- the underlying equity value;
- Titan's remaining stake; and
- the strategic actions available to both parties.

Once that is true, the valuation can no longer be reduced cleanly to two independent vanilla option legs.

---

## 2. Why A Single `Call Minus Put` Approach Is Insufficient

The simplest possible framing would be:

```text
value of contract = value of call on 25% - value of put on 25%
```

That is attractive because it is simple, quick, and familiar.

It is also inadequate for this contract.

### 2.1 It assumes the underlying block is fixed

A `call minus put` decomposition implicitly treats both legs as claims on the same permanent 25% block.

That is not what the contract does.

If Olympus calls part of the stake early, Titan's later put exposure shrinks to the residual stake actually still held.

So the put leg is not a claim on a fixed 25% block throughout the life of the instrument.

### 2.2 It assumes the legs can be valued independently

In a simple `call minus put` approach, the call leg and put leg are usually valued separately and then netted.

That independence assumption fails here because one leg changes the future state space of the other.

Olympus's call exercise changes the remaining stake.

That remaining stake determines the later put exposure.

So the legs are linked, not separable.

### 2.3 It cannot handle endogenous partial exercise properly

The contract does not only ask whether Olympus should exercise.

It asks how much Olympus should exercise.

That decision is part of value, because different call amounts leave different future residual stakes and therefore different future put exposure.

A plain `call minus put` framework does not naturally solve that problem.

### 2.4 It misses the strategic overlap problem

In the overlap period, both parties can have live rights.

That creates a strategic timing problem.

A simple `call minus put` framework has no natural mechanism for solving a node at which Olympus wants to call and Titan wants to put.

### 2.5 Bottom line on `call minus put`

`Call minus put` is insufficient because it assumes fixed block size, leg independence, and no strategic state transition.

Those assumptions are exactly the features that are not true in the signed contract.

---

## 3. Why A Naive Monte Carlo Approach Is Insufficient

It is tempting to think that Monte Carlo is automatically more sophisticated because it simulates many paths.

That is not correct here.

### 3.1 Plain path simulation is not the same as solving the contract

If we simply simulate equity paths and apply a naive rule such as:

```text
exercise when intrinsic value is positive
```

then we are not solving the actual problem.

We are imposing an exercise heuristic.

The Project Horizon contract requires the model to solve an optimal strategic control problem, not just evaluate pre-set rules on simulated paths.

### 3.2 Monte Carlo does not naturally solve dynamic strategic control

At each relevant date the model must determine:

- whether Olympus waits or calls;
- if Olympus calls, how much it calls;
- whether Titan then waits or puts; and
- how that decision changes the future continuation value.

Monte Carlo can simulate paths, but it does not by itself tell you the continuation value needed to make those decisions optimally.

To do that with Monte Carlo, you would need additional machinery such as:

- regression-based continuation estimation;
- least-squares Monte Carlo variants;
- dual methods; or
- nested simulation.

At that point it is no longer a naive Monte Carlo approach.

### 3.3 Strategic interaction makes naive Monte Carlo even weaker

This is not only an early-exercise problem.

It is an early-exercise problem with strategic interaction between two counterparties.

That is a materially harder problem for a plain Monte Carlo engine than for a dynamic-programming solver.

### 3.4 Monte Carlo is not automatically more correct

Even with a very large number of simulated paths, a naive Monte Carlo engine can still be wrong if:

- the exercise rule is misspecified;
- the continuation-value approximation is poor; or
- the strategic interaction is not solved correctly.

Large path counts remove sampling noise. They do not remove modeling error.

### 3.5 Bottom line on naive Monte Carlo

Monte Carlo is not rejected because simulation is bad.

It is rejected as the primary methodology because plain path simulation does not solve the actual strategic control problem. To make Monte Carlo adequate, one would need a much more elaborate stochastic-control implementation, and for this state dimension that is not cleaner or easier to verify than dynamic programming.

---

## 4. Why A Monthly + 1.0% Binomial / Dynamic-Programming Build Is A Valid Rough Approximation

Although the simpler methods above are insufficient, that does not mean every coarse discretization is invalid.

The monthly + 1.0% binomial / dynamic-programming approach is a valid rough approximation because it captures the essential linked-contract structure.

### 4.1 It captures the correct state variable

The monthly binomial build tracks Titan's remaining stake explicitly.

That is already a major improvement over `call minus put`.

### 4.2 It captures endogenous partial exercise

Olympus's call amount is solved within the model over an admissible menu rather than imposed externally.

That means the model is already solving a linked control problem rather than narrating one.

### 4.3 It captures the overlap game

The monthly build can solve the overlap region as a strategic node problem rather than as two disconnected options.

So it gets the core economic logic of the signed contract broadly right.

### 4.4 Why it is still only a rough approximation

It is still coarse because it approximates:

- time on monthly steps;
- stock evolution on a sparse tree; and
- remaining stake on 1.0% increments.

So it is a good rough methodology, but not the most refined one.

### 4.5 Bottom line on the monthly + 1.0% build

This approach is valid as a rough approximation because it captures the right problem structure.

Its weakness is not conceptual failure. Its weakness is numerical granularity.

---

## 5. Why The Selected Refined Method Is Daily + 0.25% QVI-Style Dynamic Programming

The selected refined method is a business-day, continuous-price, QVI-style dynamic-programming solver with a 0.25% ownership-state grid.

That choice is deliberate.

### 5.1 It solves the right problem class

The contract is a strategic intervention problem with a stochastic underlying and a state-dependent residual block.

That is exactly the kind of problem for which a QVI-style dynamic-programming framework is appropriate.

### 5.2 It materially reduces time discretization error

Moving from monthly to business-day steps gives a much finer representation of exercise timing and overlap behavior.

That matters because the contract is sensitive to when the parties can act.

### 5.3 It materially reduces control discretization error

Moving from 1.0% to 0.25% stake increments gives a much finer partial-exercise ladder.

That matters because the economic value depends on how much Olympus calls and how much residual put exposure remains.

### 5.4 It uses a dense stock-price state instead of a sparse tree

The QVI-style solver represents the equity value on a dense log-price grid rather than a sparse branching tree.

That is closer to a continuous-state representation and therefore more academically aligned with the underlying stochastic-control problem.

### 5.5 It remains computationally and governance-wise manageable

The chosen refined method is still something we can:

- run repeatedly;
- convergence-test;
- audit; and
- explain.

That matters.

The goal is not to choose the theoretically infinite model. The goal is to choose the most refined model that remains defensible in practice.

---

## 6. Why We Do Not Go All The Way To Literal Continuous Time And Continuous Share Control

In a purely abstract mathematical sense, one could ask for:

- continuous time;
- continuous stock-price state;
- continuous control over exercise amount; and
- exact strategic solution with no discretization at all.

That is not the practical objective.

### 6.1 Exact continuity is not operationally necessary

The contractual thresholds themselves are already coarse:

- there is a 5% minimum call tranche; and
- there is a 7% residual floor unless the position goes to zero.

So the economics are not infinitely fine in the first place.

### 6.2 Exact continuity would create disproportionate numerical burden

A literal continuous-time / continuous-control implementation would create a much heavier numerical problem that is harder to:

- calibrate;
- validate;
- explain; and
- govern.

### 6.3 Daily + 0.25% is the right compromise

Business-day time steps and 0.25% control increments are fine enough to reduce the coarse discretization artifacts materially, but still coarse enough to keep the model computationally tractable and auditable.

In the current stable implementation, that compromise corresponds roughly to:

- 1,512 business-day time steps over six years;
- 1,201 price nodes on the dense log-price grid; and
- 74 ownership states from 25.00% down to 7.00%, plus 0.00%.

That is already a very large state space for a strategic valuation model.

So the point is not that daily + 0.25% is mathematically perfect. The point is that it is fine enough to be meaningfully closer to the continuous-state problem without becoming computationally or governance-wise unreasonable.

So the selected methodology is a deliberate compromise:

`granular enough to be technically meaningful, but not so fine that the model becomes an opaque numerical science project.`

---

## 7. The Practical Selection Logic

The methodology decision can therefore be summarized as follows.

| Candidate approach | Main strength | Main failure or limitation | Selection outcome |
|---|---|---|---|
| `Call minus put` | Simple and familiar | Wrong problem structure; assumes fixed 25% block and independent legs | Rejected |
| Naive Monte Carlo | Simulates many paths | Does not solve strategic optimal control by itself | Rejected |
| Monthly + 1.0% dynamic programming | Captures the correct linked-contract logic | Coarse in time, price, and control resolution | Accepted as valid rough approximation |
| Business-day + 0.25% QVI-style dynamic programming | Captures the correct problem and materially reduces discretization error | More complex, but still tractable and auditable | Selected refined methodology |

Numerically, the rough monthly approximation produced a pre-DLOM value of approximately **USD 140.936M**, while the selected refined QVI methodology produced approximately **USD 144.076M**.

So the refined methodology increased value by approximately **USD 3.140M**, or about **2.23%**.

That is large enough to justify taking the refined method seriously, but small enough to show that the monthly method was a rough approximation rather than a fundamentally wrong model.

---

## 8. How To Explain The Selection To An MD

The shortest management version is:

`We rejected simple call-minus-put because the contract is linked and state-dependent, and we rejected naive Monte Carlo because path simulation alone does not solve the strategic exercise problem. A monthly binomial / dynamic-programming model is a valid rough approximation, but the selected refined methodology is a business-day QVI-style solver with a 0.25% exercise grid because that is the best practical compromise between academic correctness and computational tractability.`

---

## 9. How To Explain The Selection To The Client

Suggested client wording:

`We considered whether the instrument could be valued using simpler option techniques, but those methods would not capture the linked nature of the contract, the effect of prior call exercise on later put exposure, or the strategic interaction during the overlap period. We therefore selected a dynamic-programming formulation capable of modeling the contract directly. For robustness, we note that a coarser monthly-state implementation provides a valid rough approximation, while the selected business-day and fine exercise-grid methodology provides the more refined valuation framework.`

---

## 10. Bottom Line

The reason QVI is selected is not that it sounds more advanced.

It is selected because:

1. `call minus put` does not solve the signed contract;
2. naive Monte Carlo does not solve the strategic control problem;
3. monthly + 1.0% dynamic programming is a valid rough approximation; and
4. business-day + 0.25% QVI-style dynamic programming is the most refined practical methodology that stays granular without trying to force a literal infinite-state continuous solve.

That is the methodology selection logic.
