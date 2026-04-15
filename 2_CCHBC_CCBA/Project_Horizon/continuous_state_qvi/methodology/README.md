# Project Horizon QVI Methodology Pack

This folder is a full methodology pack for the continuous-state QVI workstream.

It is intended to be read in one of two ways:

1. Start with [overview.md](./overview.md) if you want the shortest possible 30,000-foot explanation.
2. Start with [full_methodology_report.md](./full_methodology_report.md) if you want the complete start-to-finish narrative as a draft white paper.

The remaining files break the methodology into individual topics so that each moving part can be understood separately.

Recommended reading order:

- [overview.md](./overview.md) - short commercial and conceptual summary.
- [full_methodology_report.md](./full_methodology_report.md) - full sequential methodology narrative.
- [contract_and_economics.md](./contract_and_economics.md) - what contract is being valued and why the problem is state-dependent.
- [state_space_and_slices.md](./state_space_and_slices.md) - the 3D state space and what the ownership "slices" mean.
- [time_price_and_strike_grids.md](./time_price_and_strike_grids.md) - time basis, price grid, and strike schedule mechanics.
- [backward_recursion_and_game_logic.md](./backward_recursion_and_game_logic.md) - the actual numerical solution logic.
- [outputs_and_interpretation.md](./outputs_and_interpretation.md) - how to read each CSV and what it is not saying.
- [exercise_regions_and_examples.md](./exercise_regions_and_examples.md) - concrete wait / call / put regions from the current 25% sheet.
- [assumptions_limitations_and_next_steps.md](./assumptions_limitations_and_next_steps.md) - simplifications, caveats, and what a formal report should still add.

The most important conceptual point in the whole pack is this:

The model is not freely "picking whichever ownership sheet looks best."

The current ownership sheet is fixed by the current remaining Titan stake. At a node with state `(time, price, remaining stake)`, the solver compares only the contract-feasible actions from that state:

- wait, which stays on the same ownership sheet;
- call to a lower residual stake sheet that is contract-feasible; or
- put to zero if Titan's put right is live.

So the optimization is over actions and feasible state transitions, not over arbitrary slices.