# Exercise Regions And Examples

## Purpose of this note

This note translates the current 25% action surface into plain-English exercise-region statements.

The aim is to answer the commercial question:

When does the model prefer wait, call, or put?

These statements are based on the current exported 25% surface.

They are state-contingent results from the current parameterization, not universal truths for every calibration.

## The clean regime picture on the 25% sheet

The 25% action surface says the following.

### Before Year 3.0

The entire 25% sheet is `wait`.

This is purely contractual because no exercise right is live.

### At Year 3.0

The 25% sheet is still `wait` almost everywhere.

Only the 7 highest price rows, roughly above USD 10,595, switch to `call->0.00%`.

Interpretation:

At ordinary prices, Olympus still values continuation more than immediate full exercise at the first call date.

### By Year 3.496032

The full 25% sheet is `call->0.00%`.

Interpretation:

Just before Titan's put becomes live, Olympus wants to remove Titan completely from the deal in the current calibration.

### At Year 3.523810

The sheet is effectively all call.

There is one isolated `put->0.00%` row at about USD 642.88 surrounded by call on both sides.

Interpretation:

That single-row switch should be treated as a numerical boundary artifact around an exercise indifference line, not as a broad economic region.

### At Year 4.0

The sheet remains effectively all call.

Again there is a one-row `put->0.00%` switch near USD 655.60, with call on both sides.

Interpretation:

The robust economic message is still that the overlap region strongly favors Olympus calling out the 25% residual block.

### At Year 5.0

The 25% sheet is all `call->0.00%` through the last day of the call window.

Interpretation:

In the current parameterization, Olympus continues to prefer full clean-out right up to the end of the call period.

### Just after Year 5.0

At Year 5.003968, the call window is gone and the sheet becomes a `put` versus `wait` boundary.

Current approximate threshold:

- `put->0.00%` below about USD 474.48;
- `wait` above about USD 476.81.

Interpretation:

Once Olympus can no longer call, Titan exercises the put in sufficiently weak price states and waits in stronger states.

### At Year 5.5

Current approximate threshold:

- `put->0.00%` below about USD 525.89;
- `wait` above about USD 528.47.

Interpretation:

The put boundary rises as expiry approaches because the remaining time value of waiting shrinks.

### One business day before expiry

At Year 5.996032 the sheet shows:

- `put->0.00%` below about USD 688.52;
- `wait` in a mid band from about USD 691.90 to USD 751.99; and
- `put->0.00%` again above about USD 755.68.

Interpretation:

That upper-tail return to put should be read as a one-step numerical boundary effect rather than a broad commercial conclusion.

Very near expiry, narrow tie bands and one-step continuation effects can create small non-monotone edge behavior.

### At Year 6.0

The entire 25% sheet is `put->0.00%`.

Interpretation:

There is no continuation option left. The remaining decision is immediate terminal exercise.

## What these regions mean economically

The model is not saying that Olympus calls only when the call is in the money and Titan puts only when the put is in the money in a static sense.

The model is comparing immediate action to continuation.

That creates three broad messages.

### Message 1: early call-only region is mostly continuation

When only Olympus's call is live, Olympus generally prefers to preserve optionality unless price is extremely strong.

That is why Year 3.0 is still mostly `wait`.

### Message 2: overlap strongly favors eliminating residual put exposure

Once Titan's put is about to matter, Olympus often prefers to call out the residual stake rather than leave Titan sitting on downside protection.

That is why the 25% sheet becomes overwhelmingly call during the overlap in the current run.

### Message 3: after the call window, the problem becomes a classic put boundary

Once Olympus loses the call right, the remaining policy on the 25% sheet becomes Titan's put-versus-wait decision.

That is why the surface turns into a clean price threshold after Year 5.0.

## Example narratives from the representative checkpoint logic

The representative checkpoint outputs tell a consistent story.

- before Year 3.0, all representative paths show `wait`;
- around Year 3.0, the base and high checkpoints still often show `wait`;
- around Year 3.5 and Year 4.0, the representative paths commonly flip to `call->0.0%` on the 25% state; and
- by final expiry the remaining decision is `put`.

This aligns with the full 25% action surface and gives a readable storyline for non-technical review.

## A practical answer to "above x or below y"

The honest answer is:

There is no single permanent `x` or `y` for the full contract.

The thresholds move over time and depend on which ownership sheet you are on.

For the exported 25% sheet in the current run, the most useful examples are:

- at Year 5.003968, put below about USD 474.48 and wait above about USD 476.81;
- at Year 5.5, put below about USD 525.89 and wait above about USD 528.47; and
- during most of the overlap, the 25% sheet is effectively all call.

So the correct commercial summary is dynamic, not static.

## Why one-row anomalies should not drive the narrative

The isolated one-row `put` lines during the overlap and the narrow upper-tail put region one day before expiry are artifacts of solving a discrete numerical grid very close to an indifference boundary.

They are useful for technical completeness, but they are not the main economic conclusion.

The main economic conclusion is the broad regime shape.

## Bottom line

For the current 25% sheet, the policy evolves like this:

- all wait before rights are live;
- mostly wait at the first call date;
- effectively all call through most of the overlap and up to the end of the call window; and
- a moving put-versus-wait boundary after the call window closes.

That is the simplest and most accurate verbal summary of the current exercise-region behavior.