# State Space And Slices

## The shortest answer to the slice question

Yes, the full model can be pictured as many ownership sheets stacked on top of each other.

No, the solver does not just pick whichever sheet has the highest value.

It starts from the current ownership sheet and compares the contract-feasible actions from that sheet.

That is the key distinction.

## The full state variable

The model value is a function of:

`V(time, price, remaining stake)`

Each piece plays a different role.

- `time` tells us what rights are currently live and what strike applies.
- `price` tells us the market state.
- `remaining stake` tells us how much of Titan's original position is still outstanding.

If any of those variables are removed, the contract is no longer represented faithfully.

## What a "slice" actually is

A slice is just one fixed remaining-stake level.

For example, the 25% slice is the full time-price surface when Titan still owns 25%.

The 20% slice is the full time-price surface when Titan owns 20%.

The 15% slice is the full time-price surface when Titan owns 15%.

And so on.

Inside each slice:

- rows are price states;
- columns are time states; and
- cells hold either contract value or optimal action.

## Why the exported 25% surface is only part of the solution

The exported `value_surface_25pct` and `action_surface_25pct` files show only one slice from the full 3D object.

They do not mean the model knows only about 25%.

They mean that 25% is the most relevant starting sheet and the most useful one to export for review.

The solver still uses all lower ownership sheets internally, because Olympus can jump to them through partial calls.

## The current ownership grid

The current build uses 25 basis-point increments.

That means the ownership grid is:

- 25.00%;
- 24.75%;
- 24.50%;
- and so on;
- down to 7.00%;
- plus 0.00%.

This gives 74 ownership states in total.

## How the current state determines the current slice

Suppose the current state is:

- time = Year 4.0;
- price = USD 650;
- remaining stake = 25%.

Then the model is on the 25% sheet.

It is not allowed to pretend it is on the 12.5% sheet unless a call actually moves the contract there.

The ownership state is not a choice variable by itself.

It is a state variable.

## What the optimizer is actually comparing

At a current state `(t, p, s_current)`, the optimizer compares actions, not arbitrary sheets.

Those actions imply the following transitions.

### Wait

Stay on the same sheet:

`(t, p, s_current) -> (t + dt, future price, s_current)`

### Call to a feasible target `s_target`

Jump to a lower residual-stake sheet:

`(t, p, s_current) -> immediate call payoff + (t + dt, future price, s_target)`

### Put

Jump to the zero sheet:

`(t, p, s_current) -> immediate put outcome + 0-sheet`

So yes, the solver references multiple sheets when evaluating a node.

But it references them only because actions can move the contract to those sheets.

## Why this matters so much

If someone says, "we are picking the slice that is most optimal," that statement is close to the truth but still not precise enough.

The correct statement is:

At a given node, the solver compares the values implied by feasible actions, and those feasible actions may transition the contract to lower ownership slices.

That is much tighter and contract-faithful.

## Examples of feasible transitions

### Example 1: current stake 25.0%

Because the minimum call tranche is 5.0%, Olympus cannot call from 25.0% to 24.5%.

That would only call 0.5%.

Olympus can instead target any residual state at or below 20.0%, provided the residual is either:

- at least 7.0%; or
- zero.

So examples include:

- 20.0%;
- 19.75%;
- 18.0%;
- 10.0%;
- 7.0%;
- 0.0%.

### Example 2: current stake 12.5%

Now the 5.0% minimum call means the residual must be at or below 7.5%.

The residual floor means the residual cannot be below 7.0% unless it is zero.

So feasible targets are:

- 7.5%;
- 7.25%;
- 7.0%;
- 0.0%.

### Example 3: current stake 10.0%

Calling 5.0% would leave a 5.0% residual.

That breaches the 7.0% floor.

So once the state is 10.0%, the only feasible call target is 0.0%.

## Why intermediate ownership levels like 12.5% are valid

Yes, intermediate levels such as 12.5% are valid in the current refined model.

They are not theoretical only.

They are actual grid states because the model uses 0.25% increments.

So a move from 25.0% to 12.5% is allowed if:

- the called amount is 12.5%, which exceeds the 5.0% minimum; and
- the residual 12.5% is above the 7.0% floor.

This is one of the big advantages of the refined state grid.

## ASCII picture of the state stack

```text
                 higher remaining stake

slice s = 25.00%   [time x price surface]
slice s = 24.75%   [time x price surface]
slice s = 24.50%   [time x price surface]
...
slice s = 12.50%   [time x price surface]
...
slice s = 7.00%    [time x price surface]
slice s = 0.00%    [absorbing zero sheet]

                 lower remaining stake
```

At any current node, the model starts on one of these sheets and evaluates whether it should:

- stay where it is;
- jump downward by calling; or
- jump to zero through the put.

## Why the 0% sheet matters

The 0% sheet is important because it is the absorbing exit state.

Once Titan has fully exited, there is no residual strategic optionality left.

That makes the 0% sheet a natural terminal state used by both full calls and puts.

## Practical interpretation for reviewers

If you are looking at the 25% action surface and you see `call->0.00%`, the model is saying:

From the current 25% slice, the best admissible action is a full clean-out to the zero slice.

If future exports show `call->15.00%`, that would mean:

From the current slice, the best action is to leave Titan with 15% and continue the problem on the 15% sheet.

That is how slices and actions connect.

## Bottom line

The slice structure is not a reporting convenience. It is the actual state space of the contract.

The solver does not optimize over slices in the abstract.

It optimizes over feasible actions, and those actions determine whether the state stays on the current slice or moves to a lower one.