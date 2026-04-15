# Project Horizon - Continuous-State QVI Full Methodology Report

**Prepared for:** internal methodology development  
**Subject:** full start-to-finish methodology narrative for the Project Horizon linked option agreement  
**Model version described:** business-day continuous-state QVI solver in [project_horizon_continuous_state_qvi.py](../project_horizon_continuous_state_qvi.py)

## 1. Purpose of this report

This document is a full methodology narrative for the Project Horizon continuous-state QVI valuation.

It is written as if it were the backbone of a formal white paper.

Its purpose is not to defend the model with vague language. Its purpose is to make the model mechanically understandable from beginning to end.

The report therefore answers five questions in order:

1. What economic problem are we trying to solve?
2. Why does the contract require a state-dependent strategic model rather than a simpler option package?
3. What exact numerical representation did we adopt?
4. How does the solver move through the state space and choose actions?
5. How should the outputs be interpreted in economic terms?

## 2. The valuation question we actually have

The agreement being valued is not a single vanilla option on a fixed block of shares.

It is a linked contract with two important features:

- Olympus has a call right; and
- Titan has a put right.

The two rights are linked because Olympus's earlier call decisions change the future number of shares Titan still holds.

That means the future put exposure is not fixed at the original 25% stake.

It depends on what Olympus chose to do earlier.

This immediately changes the nature of the valuation problem.

The problem is no longer:

`What is the value of a call on 25% minus a put on 25%?`

The real problem is:

`What is the value of a contract in which the future residual stake is endogenous and depends on prior exercise behavior?`

That is the central reason for the dynamic-programming formulation.

## 3. Why a simple call-minus-put decomposition is not enough

There are three reasons a simple decomposition is not contract-faithful.

### 3.1 The underlying block is not fixed

In a plain call-minus-put decomposition, both options are implicitly treated as claims on the same permanent block of shares.

That is not true here.

If Olympus calls part of the stake earlier, Titan no longer owns that part later.

So Titan's later put applies only to the residual block still held by Titan.

### 3.2 The future state depends on today's action

The question is not only whether Olympus should exercise.

The question is also how much Olympus should exercise.

Different call sizes leave different residual stakes.

Different residual stakes imply different future continuation values and different future put exposures.

### 3.3 The overlap period is strategic

During the overlap window both parties can have live rights.

At that point the problem is not simply early exercise by a single holder.

It is a strategic interaction in which Olympus wants to maximize Olympus value and Titan wants to minimize Olympus value.

That makes the problem a linked strategic control problem rather than two separable option legs.

## 4. Why the continuous-state QVI framework was chosen

The chosen methodology is a grid-based dynamic-programming approximation to a quasi-variational inequality type problem.

That wording sounds more abstract than it is.

In practical terms, it means the value of the contract is determined by two layers at once:

- passive market evolution between exercise dates; and
- active intervention rights at dates when one or both parties can act.

This framework was chosen because it directly matches the deal structure.

The contract value depends on:

- time;
- share price;
- remaining Titan stake; and
- the set of actions available from that state.

That is exactly the type of structure for which dynamic programming is natural.

## 5. Core economics embedded in the model

The current implementation uses the following contractual and financial inputs.

### 5.1 Capital structure and spot normalization

- total equity value: USD 3.2bn;
- Titan initial stake: 25.0%;
- option shares: 1,386,020;
- implied total shares: 5,544,080; and
- implied spot price per share at valuation: USD 577.192248.

That spot price is not a path. It is the anchor level used to build the model state space.

### 5.2 Coupon schedules used to roll the strike

Call coupon schedule:

- Year 0-1: 2.75%;
- Year 1-2: 3.00%;
- Year 2-3: 3.00%;
- Year 3-4: 4.20%;
- Year 4 onward: 4.20%.

Put coupon schedule:

- Year 0-1: 2.75%;
- Year 1-2: 3.00%;
- Year 2-3: 3.00%;
- Year 3-4: 4.10%;
- Year 4-5: 4.10%;
- Year 5 onward: 4.10%.

### 5.3 Exercise windows

- call live from Year 3.0 through Year 5.0;
- put live from Year 3.5 through Year 6.0.

### 5.4 Exercise-size rules

- minimum call tranche: 5.0%;
- residual floor: 7.0%, unless the position is taken fully to 0%; and
- partial calls are allowed, subject to the two constraints above.

### 5.5 Market assumptions used by the current reference run

- risk-free rate: 4.929%;
- asset volatility: 20.0%; and
- total horizon: 6.0 years.

### 5.6 Simplifying implementation assumptions in the current build

- completion lag is set to zero; and
- same-bucket tie priority is approximated by a 50% Olympus weighting in the overlap-stage approximation.

These assumptions are not hidden. They are explicit modeling choices in the implementation.

## 6. What the three state variables are

The model's value function depends on three state variables:

`V(t, p, s)`

where:

- `t` is time;
- `p` is price per share; and
- `s` is Titan's remaining stake.

This is the most important conceptual sentence in the entire methodology.

If a reader does not understand that the state includes remaining stake, the rest of the model will look arbitrary.

## 7. How to visualize the state space

The correct visual is not a tree. It is a stack of 2D sheets.

Each sheet corresponds to one remaining-stake state.

Inside a sheet:

- the horizontal axis is time;
- the vertical axis is price; and
- each cell is value or optimal action for that `(time, price, stake)` node.

So the full model looks like this conceptually:

```text
stake = 25.00%   value sheet over (time, price)
stake = 24.75%   value sheet over (time, price)
stake = 24.50%   value sheet over (time, price)
...
stake = 7.00%    value sheet over (time, price)
stake = 0.00%    terminal zero sheet
```

The exported `value_surface_25pct` and `action_surface_25pct` files are only the 25.00% sheet from that full stack.

## 8. The ownership slice question: what the solver is and is not doing

This is the point that most needs to be stated plainly.

The solver is not freely searching across all ownership sheets and picking whichever one looks best in the abstract.

That would be economically wrong.

The current ownership sheet is dictated by the current remaining Titan stake.

If the current state is `(t, p, 25%)`, then the model starts on the 25% sheet.

From that sheet it compares only contract-feasible actions.

Those actions imply the following state transitions.

- `wait` keeps the state on the 25% sheet.
- `call to 20%` jumps from the 25% sheet to the 20% sheet.
- `call to 15%` jumps from the 25% sheet to the 15% sheet.
- `call to 0%` jumps from the 25% sheet to the zero sheet.
- `put` jumps the state to the zero sheet because Titan exits the residual holding.

So yes, conceptually the full solution requires `N` ownership sheets.

But no, the optimization is not "pick the best sheet."

The optimization is:

`from the current sheet, compare the feasible transitions implied by wait, call, and put`

That is a completely different statement.

## 9. The ownership grid in the current model

The stable run uses a 0.25% ownership grid.

That means ownership states are represented in 25 basis-point increments.

The grid is:

- 0.00%; and
- every 0.25% level from 7.00% through 25.00%.

That produces 74 ownership states in total.

This is much finer than the earlier 1.0% grid and is one of the main reasons the current solver is the preferred refined methodology.

## 10. The action set from a given ownership state

At a positive remaining-stake state, the model compares three action families.

### 10.1 Wait

Waiting means Olympus does nothing now and Titan does nothing now.

The contract simply rolls forward one model step and the value becomes the discounted continuation value.

### 10.2 Call

If the call is live, Olympus can choose any target residual stake that satisfies the contract rules:

- target stake must be below current stake;
- the called tranche must be at least 5.0%; and
- the residual stake after the call must be either 0% or at least 7.0%.

This is an important practical implication of the rules.

Examples:

- from 25.00%, Olympus can target 20.00%, 19.75%, 19.50%, ..., 7.00%, or 0.00%;
- from 20.00%, Olympus can target 15.00%, 14.75%, ..., 7.00%, or 0.00%;
- from 10.00%, Olympus can only target 0.00% because leaving 5.00% would breach the 7.0% residual floor.

So the set of reachable lower sheets depends on the current sheet.

### 10.3 Put

If the put is live, Titan can put the entire residual stake in that state.

This is not a special simplification we introduced. It is the contract rule translated into the state model.

In implementation terms, the put always acts on all shares still held in the current residual-stake node.

So if the current state is 25%, the put is on the full remaining 25%.

If Olympus has already called down the position and the current state is 20%, 15%, 10%, or 7%, the put is on that full residual state, not on the original 25% block.

## 11. Time discretization and why the model uses 252 steps per year

The current model uses a business-day grid with 252 equal steps per year.

Since the horizon is 6 years, that gives:

- 1512 time steps; and
- 1513 time points including `t0`.

This is a modeling basis choice.

It means one model step is exactly `1/252` of a year.

The model therefore represents action timing on a business-day basis rather than monthly buckets.

## 12. The strike schedule and the coupon-versus-trading-day question

This is a point that deserved to be explicit from the beginning.

The contractual strike schedule is fully knowable once three things are specified:

- the SPA base price;
- the coupon schedule; and
- the completion-lag assumption.

The current implementation rolls the strike on the same 252-step business-day model grid.

Within a coupon bucket with annual coupon `c`, the one-step model roll is:

`(1 + c)^(1/252) - 1`

This is how the code reconciles an annual coupon schedule with daily model steps.

So there is no missing strike path in the current implementation anymore. It is now exported explicitly in `project_horizon_continuous_state_qvi_strike_schedule.csv`.

What remains a modeling choice is the day-count convention.

Right now the solver assumes the legal accrual should be represented on a 252-step business-day year.

If the final methodology report concludes that the contract should instead roll strikes on actual calendar days or another formal day-count convention, the strike engine should be rebuilt on that basis.

## 13. The price grid and why the surface rows look strange at early dates

The price grid is a fixed log-price grid built over the full 6-year horizon.

For the stable reference case it contains 1201 price nodes.

That means every time column in the value and action surfaces uses the same list of price states.

This is why early columns contain very low and very high price rows that do not look like realistic near-term moves.

Those rows are not forecasts.

They are support points of the numerical state grid.

The current spot price is approximately USD 577.192248 and sits near the middle row of the exported surface.

Rows such as USD 30.53 and USD 10,911.40 are far-tail grid nodes, not path projections.

## 14. How continuation value is computed

Between intervention opportunities, the underlying share price is assumed to evolve under a risk-neutral geometric Brownian motion.

The solver does not simulate random paths.

Instead it computes the continuation value on the fixed grid using a numerical expectation operator.

The key ingredients are:

- risk-neutral drift;
- volatility;
- one-step discounting; and
- interpolation across the fixed log-price grid.

The implementation uses Gauss-Hermite quadrature to approximate the one-step conditional expectation.

So at each time step the future value surface is projected backward by one model day.

This is why the method is a grid-based dynamic-programming solver rather than Monte Carlo.

## 15. The backward recursion in plain English

The solver works backward from maturity to the valuation date.

At each time step it performs the following sequence.

### 15.1 Compute the continuation surface

Take tomorrow's value surface and project it back one model day under the risk-neutral process.

This gives the value of waiting at each `(price, stake)` node before allowing any immediate exercise decision.

### 15.2 Determine which rights are live at this date

For the current time step, determine whether:

- the call is live;
- the put is live; or
- both are live.

### 15.3 Evaluate immediate action payoffs

For each current ownership state and each price node, compute:

- the value of waiting;
- the value of each admissible call target if the call is live; and
- the value of the put if the put is live.

### 15.4 Apply the contract logic for the relevant regime

There are four regimes.

- no right live: only wait is possible;
- call only: compare wait to each admissible call target;
- put only: Titan compares wait to immediate put;
- overlap: Olympus and Titan are in a strategic node.

### 15.5 Write today's value surface and move one step back

Once the best action outcome is known at this date, that becomes the current value surface.

Then the recursion moves one day earlier and repeats.

## 16. How the call-only region is solved

When only the call is live, Olympus compares:

- wait; and
- every admissible call target.

For a call target `s'`, the value is:

- immediate call intrinsic on the tranche being acquired now; plus
- continuation value on the lower residual ownership sheet `s'`.

Olympus selects the target that gives the highest value.

If no call target beats waiting, the optimal action remains wait.

## 17. How the put-only region is solved

When only the put is live, the relevant comparison is simpler.

Titan compares:

- waiting; and
- putting the full residual stake.

Because the value function is recorded from Olympus's perspective, Titan's put creates a negative value to Olympus when it is in the money.

So the model takes the minimum of:

- Olympus continuation value if Titan waits; and
- Olympus value if Titan immediately puts.

## 18. How the overlap region is solved

The overlap region is the most important part of the model conceptually.

When both rights are live, Olympus and Titan may each want to act.

The implementation solves this approximately as a stage game.

Olympus evaluates each admissible call target.

For each candidate call target, the model compares two possibilities:

- Olympus calls and Titan then waits on the residual state; and
- Olympus calls and Titan responds by putting the residual stake if that is worse for Olympus.

The model then applies a tie-priority approximation with a 50% weighting when actions fall into the same bucket.

This is a simplification, but it is an explicit one.

The important point is that the overlap node is treated strategically, not as two disconnected option legs.

## 19. What the outputs are designed to show

The model writes several output types because no single file can explain everything.

### 19.1 Convergence output

`project_horizon_continuous_state_qvi_results.csv` compares price-grid refinements.

For the current run:

- 801 prices: USD 145.864m;
- 1001 prices: USD 144.227m; and
- 1201 prices: USD 144.076m.

So the stable reference case is the 1201-price result at USD 144.076m.

### 19.2 Strike schedule output

`project_horizon_continuous_state_qvi_strike_schedule.csv` shows the deterministic daily strike path.

This file exists because the strike is not a random state variable in the current model.

It is a deterministic function of time and the chosen day-count / coupon basis.

### 19.3 Explainability traces

`project_horizon_continuous_state_qvi_sample_paths.csv` and `project_horizon_continuous_state_qvi_policy_checkpoints.csv` are explainability artifacts.

They do not define the model state space.

They are thin reporting slices intended to illustrate behavior.

The labels `low`, `base`, and `high` are not separate valuation scenarios. They are deterministic representative path labels.

### 19.4 Full-state surfaces

`project_horizon_continuous_state_qvi_value_surface_25pct.csv` and `project_horizon_continuous_state_qvi_action_surface_25pct.csv` are the full time-price sheets for the 25% ownership state.

These are the closest Excel-friendly representation of the full QVI object that can be opened and inspected directly.

## 20. How to read the 25% value and action surfaces

The 25% surface files should be read as follows.

- each row is a price node from the fixed 6-year price grid;
- each column is a model day from `t0` to Year 6.0; and
- each cell is the value or optimal action at that exact `(time, price, 25%)` node.

The first column `price_per_share_usd` is not a path.

It is the full list of price states.

So a row around USD 577.19 is the current spot row.

A row at USD 30.53 is a deep low tail state.

A row at USD 10,911.40 is a deep high tail state.

These are alternative price states at the same time, not one path evolving through time.

## 21. Concrete exercise-region behavior from the current 25% action surface

The current 25% action surface contains several clean regime messages.

### 21.1 Before Year 3.0

The full 25% sheet is `wait`.

This is not a numerical surprise. It is contract mechanics.

Before Year 3.0, neither the call nor the put is exercisable.

### 21.2 At Year 3.0

At the first call-live date, the 25% sheet is still `wait` almost everywhere.

Only the top 7 extreme high-price rows switch to `call->0.00%`, corresponding to prices roughly above USD 10,595.

So at normal price levels, Olympus still prefers continuation rather than immediate full exercise.

### 21.3 Just before the overlap begins

By Year 3.496032, the full 25% sheet has become `call->0.00%`.

That means that, in the current parameterization, once the overlap is about to begin, Olympus prefers to extinguish Titan's residual stake rather than risk entering the overlap with the 25% block still outstanding.

### 21.4 During the overlap

At Year 4.0 the surface is effectively all call, with a one-row numerical switch around the strike neighborhood.

That one-row `put` line near USD 655.60 should be read as a boundary / tie artifact, not as a broad economic region.

The economic message is that the overlap region strongly favors Olympus calling out the residual block on the 25% sheet.

### 21.5 Just after the call window ends

At Year 5.003968, once the call window is gone, the 25% sheet becomes a classic `put` versus `wait` region.

For the current 25% sheet:

- `put` is optimal below roughly USD 474.48; and
- `wait` is optimal above roughly USD 476.81.

### 21.6 Midway through the final put-only window

At Year 5.5:

- `put` is optimal below roughly USD 525.89; and
- `wait` is optimal above roughly USD 528.47.

So the put boundary rises as expiry approaches, which is economically sensible because the time value of waiting diminishes.

### 21.7 At maturity

At Year 6.0 the full 25% sheet is `put->0.00%`.

There is no continuation value left. The terminal decision is immediate.

## 22. Why the exercise rule is not simply "above strike call, below strike put"

This point matters a great deal.

The solver is not just checking intrinsic value against zero.

It is comparing immediate action value against continuation value.

That means an in-the-money call can still be dominated by waiting if waiting preserves enough option value.

Likewise, an out-of-the-money put can still matter strategically during the overlap because its existence affects Olympus's incentive to remove Titan's residual stake before Titan can benefit from downside later.

So the relevant thresholds are not just strike levels.

They are dynamic exercise boundaries produced by the competition between:

- intrinsic value now; and
- continuation value of staying alive.

## 23. What the representative `low`, `base`, and `high` paths are for

The sample-path and checkpoint files exist only for explainability.

They are deterministic representative paths built around z-scores of `-1.0`, `0.0`, and `+1.0`.

They do not define the valuation.

They are simply a readable way to show how the already-solved policy behaves under a low, middle, and high market narrative.

This distinction matters because otherwise a reader can mistakenly think the model has only three scenarios.

It does not.

The full valuation uses the entire state grid.

## 24. Current headline result and what it means

The stable reference case is the daily QVI run with:

- 252 steps per year;
- 0.25% ownership step size; and
- 1201 price nodes.

That produces a value to Olympus of approximately USD 144.076m before DLOM.

Relative to earlier workstreams, this tells us something important.

The refined methodology does move the answer upward, but it does not blow up the economics.

So the benefit of the refined methodology is primarily:

- better contract faithfulness;
- better interpretability of the strategic mechanism; and
- lower discretization error.

It is not a completely different economic story.

## 25. Key simplifications and limitations

The current implementation is refined, but it is not perfect.

Its key limitations are the following.

### 25.1 Ownership is still discretized

The state grid is finer than before, but it is still a grid.

It is not literal continuous share control.

### 25.2 Completion lag is simplified to zero

That affects the strike present value and the decision timing logic.

If a non-zero notice-to-completion lag is contractually required, it should be added explicitly.

### 25.3 Day-count basis is a modeling choice

The 252-step business-day year may or may not match the legal accrual convention intended for the strike schedule.

### 25.4 Market dynamics are simple

The current build uses a one-factor lognormal process with constant volatility and a constant risk-free rate.

### 25.5 Overlap resolution is approximate

The 50% tie-priority approximation is practical, but it is still an approximation of simultaneous strategic rights.

### 25.6 Only one full ownership sheet is currently exported

The solver internally uses all ownership sheets, but the current exported full surfaces are only for the 25% state.

If a reviewer needs full visual inspection of other ownership states, those sheets should also be exported.

## 26. What a formal final white paper should still add

This document is already close to the backbone of the final methodology report, but the final white paper should still include:

- a formal mapping from legal clauses to model rules;
- a clearly stated day-count convention decision for the strike schedule;
- sensitivity analysis on volatility, risk-free rate, and tie-priority;
- sensitivity analysis on completion lag if that assumption changes;
- additional exported ownership sheets beyond 25%; and
- governance language around convergence testing and validation.

## 27. Final summary

The Project Horizon continuous-state QVI model is best understood as a three-dimensional dynamic-programming valuation of a linked strategic contract.

Its state is not just time and price. It is time, price, and remaining Titan stake.

That third variable is why the model needs multiple ownership sheets.

But those sheets are not optional views that the solver picks from freely.

They are the state space of the contract, and the solver transitions between them only through contract-feasible actions.

The methodology therefore does four essential things:

1. tracks the residual stake explicitly;
2. evaluates the contractual strike schedule on a daily grid;
3. compares wait, call, and put through backward induction; and
4. resolves the overlap period as a strategic node problem.

Once that structure is understood, the outputs stop looking arbitrary.

They become readable as a direct map from state to value and from state to action.