# Time Price And Strike Grids

## Why the grid design matters

The model is a grid-based dynamic-programming solver.

That means the grid design is not a side detail.

It determines:

- how finely exercise timing can be represented;
- how accurately continuation value is captured;
- how precisely ownership states can be carried forward; and
- how interpretable the exported surfaces are.

## Time grid used in the current reference run

The current implementation uses:

- 252 steps per model year;
- 6.0 total years; and
- 1512 time steps plus the valuation date.

So one time step is exactly `1/252` of a year.

This is a business-day modeling grid.

It is much finer than a monthly grid and substantially reduces timing discretization error around exercise windows.

## Why the time grid is the same for everything

The current implementation uses the same 252-step basis for:

- exercise opportunity timing;
- discounting between steps; and
- strike roll progression.

This is deliberate.

Using one consistent clock keeps the solver coherent and makes the exported strike schedule easy to audit.

## Price grid used in the current reference run

The stable reference case uses 1201 price nodes.

The grid is built in log-price space and then mapped back into price levels.

That means price resolution is dense around the center and remains numerically stable across a wide support.

The current exported 25% surfaces therefore have:

- 1201 rows for price; and
- 1513 columns if the price column plus all time columns are included.

## Why the same price rows appear in every time column

This point confused the output interpretation earlier and is worth stating clearly.

The price grid is fixed across time.

That means the row list is the full set of price states available at every date.

So when the value surface shows a row at USD 10,911 in a very early time column, it is not saying the model thinks the stock will be there soon.

It is just one state on the full support of the numerical grid.

## The current price support in the 25% sheet export

The 25% export spans roughly:

- a low tail near USD 30.53 per share; and
- a high tail near USD 10,911.40 per share.

The current spot of about USD 577.19 sits near the center of the grid.

This wide support is intentional. It gives the expectation operator enough room to avoid truncation problems in the tails across a 6-year horizon.

## Strike schedule mechanics

The strike is not solved as a random state.

It is deterministic conditional on time, coupon schedule, and completion lag.

That means the strike schedule can be fully precomputed.

The current implementation now exports that schedule directly in:

`project_horizon_continuous_state_qvi_strike_schedule.csv`

## Annual coupon schedule mapped onto daily model steps

The deal language uses annual coupon schedules.

The model uses daily business-day steps.

So the implementation converts each annual coupon bucket into a one-step model roll.

For a coupon bucket with annual rate `c`, the one-day model roll is:

`(1 + c)^(1/252) - 1`

This is the engine that generates the daily strike path.

## Example from the current strike schedule export

At the very start of the schedule:

- call coupon bucket: 2.75%;
- put coupon bucket: 2.75%; and
- implied one-step model roll: about 0.01076592%.

At Year 1.0 the coupon bucket steps up to 3.00%.

At Year 3.0 the call coupon bucket steps up to 4.20% and the put coupon bucket to 4.10%.

Those bucket changes are reflected in the exported daily strike path.

## Why call and put strikes diverge after Year 3.0

From Year 3 onward, the call and put coupon schedules are no longer identical.

That means the call strike and put strike roll at slightly different daily rates.

This is why the strike schedule export is useful.

It shows exactly when the schedules diverge and by how much.

## Completion lag assumption in the current implementation

The current build sets completion lag to zero.

That means the completion-time strike and the present-value strike coincide in the export.

If a non-zero lag is later imposed, the schedule export will show a meaningful difference between:

- strike at completion; and
- strike discounted to decision date.

## Why the grid design supports explainability

Because the grids are fixed, every output can be interpreted consistently.

- the price row always means the same price state;
- the time column always means the same model date; and
- the stake sheet always means the same residual ownership state.

That fixed geometry is one of the reasons the surface outputs are so useful for explaining the model.

## Bottom line

The time grid gives the model its decision frequency.

The price grid gives the model its market-state support.

The deterministic strike schedule gives the model its evolving contractual exercise economics.

Together, those three ingredients define the static numerical skeleton on which the dynamic optimization runs.