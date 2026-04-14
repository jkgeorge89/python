# Project Horizon - Continuous State QVI

This folder contains a separate continuous-state dynamic-programming reference solver.

It is intentionally kept outside `../game_theory/` so the original binomial game-theory work remains unchanged.

Current contents:

- `generate_qvi_ascii_visual.py` — generator for the rendered ASCII visual note
- `project_horizon_continuous_state_qvi.py` — business-day continuous-state QVI-style reference solver
- `project_horizon_continuous_state_qvi_results.csv` — output from the current convergence run
- `Project_Horizon_Continuous_State_QVI_ASCII_Visual.md` — simplified ASCII visual showing the daily grid, price states, and decision logic
- `Project_Horizon_Continuous_State_QVI_Methodology.md` — methodology note explaining the QVI framework for MD/client use
- `Project_Horizon_QVI_Methodology_Selection.md` — note explaining why QVI is selected and why simpler methods are insufficient
- `Project_Horizon_Continuous_State_QVI_Results.md` — short results note summarizing the stable reference value