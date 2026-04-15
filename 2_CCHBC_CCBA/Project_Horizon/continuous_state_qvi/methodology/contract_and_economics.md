# Contract And Economics

## Why this contract is different from a plain option package

The Project Horizon agreement is not just a call option attached to a put option.

The key economic feature is that Olympus can change the future size of Titan's residual holding before Titan decides whether to put.

That means the future contract is path-dependent through control, not just through market moves.

In plain English:

- if Olympus calls part of Titan's stake, Titan owns less later;
- if Titan owns less later, Titan's future put applies to a smaller residual block; and
- if the future put exposure is smaller, today's call decision changes tomorrow's economics.

That is the root cause of the state-dependent methodology.

## Initial economic setup in the current reference build

The current reference implementation normalizes the contract using the following core quantities.

- total equity value: USD 3.2bn;
- total shares implied by the model: 5,544,080;
- option shares: 1,386,020;
- initial Titan stake: 25.0%; and
- implied current share price: USD 577.192248.

The share price is simply:

`total equity value / total shares`

The initial stake matters because it defines the opening ownership state in the model.

## What the call right means economically

Olympus's call right gives Olympus the ability to acquire Titan's stake, but not necessarily all at once.

The current contractual representation embedded in the solver allows partial calls, subject to:

- a minimum 5.0% called tranche; and
- a residual stake floor of 7.0%, unless the residual is taken fully to zero.

Economically, this means Olympus can reduce future put exposure without always needing to go directly from 25% to 0%.

That flexibility is what creates a family of possible state transitions rather than a single one-off exercise event.

## What the put right means economically

Titan's put gives Titan downside protection on whatever residual stake Titan still owns when the put is exercisable.

That last phrase matters.

The put does not automatically remain a 25% put forever.

If Olympus has already called down the position to 20%, 15%, 10%, or 7%, then Titan's put exposure is on that smaller residual holding.

So the economic value of the put is endogenous to Olympus's earlier behavior.

## Why the overlap period matters so much

The overlap period is when the contract becomes a strategic control problem rather than a simple stopping problem.

During the overlap, Olympus may prefer to call because leaving Titan in the deal preserves Titan's downside put protection.

Titan may prefer to preserve the put or exercise it depending on the state.

That means the overlap is where the linked rights really matter.

Without the overlap, the contract would be much easier to summarize with simpler techniques.

## Current exercise windows in the implementation

- call live from Year 3.0 through Year 5.0;
- put live from Year 3.5 through Year 6.0.

This creates three economically distinct time zones.

### Zone 1: before Year 3.0

No one can act.

The contract is pure continuation value.

### Zone 2: Year 3.0 through Year 3.5

Only Olympus can act.

This is a call-only region.

Olympus compares immediate call value against the value of waiting.

### Zone 3: Year 3.5 through Year 5.0

Both parties have live rights.

This is the strategic overlap region.

### Zone 4: Year 5.0 through Year 6.0

Only Titan can act.

This becomes a put-versus-wait region.

## Why the strike schedule is central to the economics

The call and put strikes are not constant.

They roll over time using contractual coupon schedules.

That means a decision boundary is never just a comparison to one static strike.

It is always a comparison to:

- today's rolled strike;
- the expected future rolled strike if the position survives; and
- the future residual stake left outstanding.

That is why the strike schedule is exported explicitly in the current build.

## Contract rules that directly shape the state transitions

Three rules matter mechanically.

### Minimum call tranche

Olympus cannot call a tiny amount just to fine-tune the state.

The called amount must be at least 5.0%.

### Residual floor

Olympus cannot leave an arbitrary tiny residual state lying around.

The residual must be either:

- at least 7.0%; or
- exactly 0.0%.

### Partial-call feasibility depends on the current state

This means the set of allowed future states depends on the current remaining stake.

Examples:

- from 25.0%, many lower residual states are reachable;
- from 12.5%, only 7.5%, 7.25%, 7.0%, and 0.0% remain feasible; and
- from 10.0%, only 0.0% remains feasible because a 5.0% residual would violate the 7.0% floor.

That is exactly why ownership must be part of the state vector.

## The main economic intuition behind Olympus behavior

Olympus typically values optionality when only Olympus can act.

That means the model will often prefer to wait early in the call window unless the immediate call is strongly attractive.

Once Titan's put is approaching or already live, Olympus has a new incentive.

Olympus may want to remove Titan's residual stake not because the call is deeply in the money in a vanilla sense, but because leaving Titan in the deal preserves future put exposure.

That is why the overlap region often pushes the optimal action toward calling.

## The main economic intuition behind Titan behavior

Titan's put is fundamentally downside protection.

When the call window has closed and Titan still holds a residual block, Titan compares:

- taking the strike now; or
- waiting to see whether the residual stake becomes more valuable.

This naturally creates a put boundary below which immediate put is optimal and above which waiting retains enough upside or time value.

## Bottom line

The contract is economically state-dependent because Olympus controls the future size of Titan's residual holding.

That single fact makes the residual stake an essential state variable.

Once that is accepted, the need for a time-price-ownership model stops being optional and becomes mechanical.