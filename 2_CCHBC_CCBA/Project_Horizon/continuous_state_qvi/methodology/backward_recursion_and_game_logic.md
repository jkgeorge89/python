# Backward Recursion And Game Logic

## What the solver is doing at a high level

The solver is performing backward induction on a 3D state grid.

At each node it asks a simple question:

What is the contract worth today, given what both parties can do now and what the contract will be worth tomorrow if it survives?

That question is answered repeatedly, one business day at a time, working backward from maturity.

## Why backward induction is the right logic

At maturity the continuation value is gone.

So the value there is straightforward.

Once maturity values are known, the value one day before maturity can be solved.

Once that day is solved, the previous day can be solved.

And so on back to the valuation date.

That is exactly what backward induction is designed for.

## The data structure being solved

At each time step the solver effectively stores a full surface over:

- price states; and
- ownership states.

Tomorrow's surface is known from the previous iteration of the recursion.

Today's surface is then computed from that future surface.

## Step 1: compute continuation value

The first step at a given time is to compute the value of doing nothing immediately.

This is the continuation value, or wait value.

The solver takes tomorrow's surface and applies a one-step expectation operator under the risk-neutral price dynamics.

That expectation is then discounted back one time step.

So the wait value already includes:

- the full next-day value function;
- expected price movement;
- discounting; and
- the fact that the future contract may later move across ownership sheets through future actions.

## Step 2: compute immediate exercise alternatives

Once the wait value is known, the solver computes immediate intervention values.

### Call alternatives

If the call is live, the solver evaluates every admissible target residual stake.

For a current state `(t, p, s_current)` and a feasible target `s_target`, the call value is:

- immediate economics of acquiring `s_current - s_target`; plus
- continuation value on the `s_target` sheet.

### Put alternative

If the put is live, the solver computes the value of Titan putting the full residual stake immediately.

From Olympus's perspective this is an adverse value when the put is in the money.

## Step 3: apply the right regime logic

There are four regime blocks.

### Regime A: no exercise rights live

Only wait is possible.

Today's value equals continuation value.

### Regime B: call only

Olympus chooses the maximum among:

- wait; and
- all feasible call targets.

The action surface records the target that wins.

### Regime C: put only

Titan chooses the action that is worst for Olympus among:

- wait; and
- immediate put.

From Olympus's perspective, this means today's value is the minimum of those two outcomes.

### Regime D: overlap

This is the strategic region.

Olympus wants the highest value.

Titan wants the lowest Olympus value.

So the node is solved as a stage game approximation.

## Overlap logic in plain English

In the overlap region the solver is not simply checking which intrinsic value is larger.

It is asking:

If Olympus calls now, what residual problem is left behind?

If Olympus waits, what future put exposure is preserved?

If Titan can put now, is that worse for Olympus than waiting?

That is why the overlap policy often differs sharply from what a plain vanilla option intuition would suggest.

## Tie-priority approximation

The current implementation uses a 50% Olympus tie-priority approximation in the overlap-stage logic.

This is a pragmatic implementation choice.

It is not pretending that simultaneous strategic rights have a perfectly clean legal ordering from the current inputs.

Instead it uses an explicit midpoint approximation when the relevant actions fall into the same decision bucket.

This should be treated as a documented approximation rather than a hidden assumption.

## Why the model is not a binomial tree

A binomial tree would propagate value across an explicitly branching up/down lattice.

That is not what is happening here.

The current solver works on a fixed price grid.

Tomorrow's surface is mapped back to today through a numerical expectation operator and interpolation.

So the geometry is a rectangular grid over time and price for each ownership slice, not a branching triangle.

## Why the model is not Monte Carlo

Monte Carlo would simulate many random paths and estimate value from pathwise exercise logic.

That is also not what is happening here.

The solver directly computes the value function on the state grid.

The representative `low`, `base`, and `high` traces are generated only after the policy has already been solved.

They explain the model. They do not drive the valuation.

## Simple pseudocode for the recursion

```text
initialize terminal value surface

for time step from maturity-1 back to 0:
    compute wait value from next-step surface

    for each ownership state:
        for each price state:
            if no rights live:
                value = wait
                action = wait

            if call only:
                compare wait vs all feasible calls
                value = max(...)
                action = argmax(...)

            if put only:
                compare wait vs put
                value = min(... from Olympus perspective)
                action = Titan-optimal action

            if overlap:
                solve stage-game approximation
                value = Olympus/Titan strategic outcome
                action = recorded best policy label
```

## Why continuation value can beat intrinsic value

A common mistake is to assume that if immediate exercise has positive intrinsic value, it must be optimal.

That is not true in an option problem with remaining time value.

Continuation may still be better because it preserves future favorable states.

The recursion makes that comparison explicit at every node.

## Why the 0% state is absorbing

Once the residual stake is zero, the contract is economically over.

There is no future strategic optionality left.

That makes the 0% sheet an absorbing state and simplifies both full calls and puts.

## Bottom line

The solver is a backward dynamic program with explicit intervention choices.

Its defining feature is that immediate actions can move the problem from one ownership slice to another.

That is the mechanism that makes the recursion contract-faithful.