# Project Horizon - Continuous State QVI

This folder contains a separate continuous-state dynamic-programming reference solver.

It is intentionally kept outside `../game_theory/` so the original binomial game-theory work remains unchanged.

Current contents:

- `methodology/` — dedicated methodology pack with a 30,000-foot overview, a full start-to-finish methodology report, and topic notes on slices, grids, recursion, outputs, and exercise regions
- `generate_qvi_ascii_visual.py` — generator for the rendered ASCII visual note
- `project_horizon_continuous_state_qvi.py` — business-day continuous-state QVI-style reference solver
- `project_horizon_continuous_state_qvi_results.csv` — output from the current convergence run
- `project_horizon_continuous_state_qvi_sample_paths.csv` — representative low / base / high daily policy traces; `base` is the middle path and the file now includes the path z-score
- `project_horizon_continuous_state_qvi_policy_checkpoints.csv` — selected checkpoint rows built from those same representative paths across key dates and remaining-stake states
- `project_horizon_continuous_state_qvi_strike_schedule.csv` — deterministic daily call/put strike schedule showing coupon bucket, implied model-day roll, and strike level at each business-day step
- `project_horizon_continuous_state_qvi_value_surface_25pct.csv` — Excel-friendly price-by-day value surface for the initial 25% Titan state
- `project_horizon_continuous_state_qvi_action_surface_25pct.csv` — Excel-friendly price-by-day optimal-action surface for the initial 25% Titan state
- `Project_Horizon_Continuous_State_QVI_ASCII_Visual.md` — simplified ASCII visual showing the daily grid, price states, and decision logic
- `Project_Horizon_Continuous_State_QVI_Explainability.md` — note explaining why QVI should be reviewed through path traces and checkpoint tables rather than Monte Carlo path samples
- `Project_Horizon_Continuous_State_QVI_Methodology.md` — methodology note explaining the QVI framework for MD/client use
- `Project_Horizon_QVI_Methodology_Selection.md` — note explaining why QVI is selected and why simpler methods are insufficient
- `Project_Horizon_Continuous_State_QVI_Results.md` — short results note summarizing the stable reference value