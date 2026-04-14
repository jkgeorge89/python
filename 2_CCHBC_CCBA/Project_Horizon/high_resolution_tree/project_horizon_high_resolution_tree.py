from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import math

import numpy as np


TOTAL_EQUITY_USD = 3_200_000_000
INITIAL_TITAN_PCT = 25.0
INITIAL_TITAN_BP = int(round(INITIAL_TITAN_PCT * 100))
OPTION_SHARES = 1_386_020
TOTAL_SHARES = OPTION_SHARES / (INITIAL_TITAN_PCT / 100.0)
SPA_PRICE = TOTAL_EQUITY_USD / TOTAL_SHARES

CALL_COUPONS = np.array([0.0275, 0.0300, 0.0300, 0.0420, 0.0420], dtype=float)
PUT_COUPONS = np.array([0.0275, 0.0300, 0.0300, 0.0410, 0.0410, 0.0410], dtype=float)

CALL_START_YEARS = 3.0
CALL_END_YEARS = 5.0
PUT_START_YEARS = 3.5
PUT_END_YEARS = 6.0

MIN_CALL_TRANCHE_BP = 500
RESIDUAL_FLOOR_BP = 700
COMPLETION_LAG_YEARS = 0.0
ALLOW_PARTIAL_CALLS = True
GAME_TIE_PRIORITY_TO_OLYMPUS = 0.50

ASSET_VOLATILITY = 0.20
RISK_FREE_RATE = 0.04929
TOTAL_YEARS = 6.0


@dataclass(frozen=True)
class GridScenario:
    label: str
    steps_per_year: int
    state_step_bp: int


@dataclass(frozen=True)
class ScenarioResult:
    label: str
    steps_per_year: int
    n_steps: int
    state_step_bp: int
    state_count: int
    value_total: float
    value_per_share: float


def bp_to_pct(bp: int) -> float:
    return bp / 100.0


def bp_to_fraction(bp: int) -> float:
    return bp / 10_000.0


def shares_for_bp(bp: int) -> float:
    return TOTAL_SHARES * bp_to_fraction(bp)


def accrued_price(base_price: float, coupons: np.ndarray, t_years: float) -> float:
    acc = float(base_price)
    remaining = max(float(t_years), 0.0)
    for rate in coupons:
        if remaining <= 0.0:
            break
        year_slice = min(1.0, remaining)
        acc *= (1.0 + rate) ** year_slice
        remaining -= year_slice
    if remaining > 0.0:
        acc *= (1.0 + coupons[-1]) ** remaining
    return acc


def build_notice_strike_path(
    base_price: float,
    coupons: np.ndarray,
    time_grid: np.ndarray,
    completion_lag_years: float,
    rf: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    strike_completion = np.zeros_like(time_grid)
    strike_pv = np.zeros_like(time_grid)
    completion_grid = np.zeros_like(time_grid)

    for idx, t_notice in enumerate(time_grid):
        t_completion = t_notice + completion_lag_years
        strike_completion[idx] = accrued_price(base_price, coupons, t_completion)
        strike_pv[idx] = math.exp(-rf * completion_lag_years) * strike_completion[idx]
        completion_grid[idx] = t_completion

    return strike_completion, strike_pv, completion_grid


def build_state_grid_bp(initial_bp: int, residual_floor_bp: int, state_step_bp: int) -> np.ndarray:
    if state_step_bp <= 0:
        raise ValueError("state_step_bp must be positive")
    positive_states = np.arange(residual_floor_bp, initial_bp + state_step_bp, state_step_bp, dtype=int)
    positive_states = positive_states[positive_states <= initial_bp]
    if positive_states[-1] != initial_bp:
        raise ValueError("state grid must include the initial Titan stake exactly")
    return np.concatenate(([0], positive_states))


def allowed_call_targets_bp(
    current_bp: int,
    allow_partial_calls: bool,
    state_bps: np.ndarray,
) -> np.ndarray:
    if current_bp == 0:
        return np.array([], dtype=int)
    if not allow_partial_calls:
        return np.array([0], dtype=int)
    targets = [
        int(target)
        for target in state_bps
        if target < current_bp
        and (current_bp - int(target)) >= MIN_CALL_TRANCHE_BP
        and (int(target) == 0 or int(target) >= RESIDUAL_FLOOR_BP)
    ]
    return np.array(sorted(targets, reverse=True), dtype=int)


def summarize_call_menu_bp(current_bp: int, allow_partial_calls: bool, state_bps: np.ndarray) -> str:
    targets = allowed_call_targets_bp(current_bp, allow_partial_calls, state_bps)
    if targets.size == 0:
        return "no admissible calls"
    partial_targets = targets[targets != 0]
    parts: list[str] = []
    if partial_targets.size:
        call_sizes = sorted(current_bp - int(target) for target in partial_targets)
        remaining_states = sorted(int(target) for target in partial_targets)
        parts.append(
            "partial calls "
            f"{bp_to_pct(call_sizes[0]):.1f}%-{bp_to_pct(call_sizes[-1]):.1f}% "
            f"in {bp_to_pct(state_bps[2] - state_bps[1]):.1f}% steps -> leave "
            f"{bp_to_pct(remaining_states[0]):.1f}%-{bp_to_pct(remaining_states[-1]):.1f}% remaining"
        )
    if 0 in targets:
        parts.append(f"call {bp_to_pct(current_bp):.1f}% -> 0.0% remaining")
    return "; ".join(parts)


def build_recombining_stock_tree(
    spot0: float,
    rf: float,
    vol: float,
    dt: float,
    n_steps: int,
) -> tuple[list[np.ndarray], float, float]:
    up = math.exp(vol * math.sqrt(dt))
    down = 1.0 / up
    growth = math.exp(rf * dt)
    up_prob = (growth - down) / (up - down)
    if up_prob <= 0.0 or up_prob >= 1.0:
        raise ValueError("Risk-neutral probability is outside (0, 1); tree parameters are invalid.")

    stock_tree: list[np.ndarray] = []
    for step in range(n_steps + 1):
        up_moves = np.arange(step + 1)
        down_moves = step - up_moves
        stock_tree.append(spot0 * (up ** up_moves) * (down ** down_moves))
    return stock_tree, up_prob, math.exp(-rf * dt)


def tree_continuation(next_values: np.ndarray, discount: float, up_prob: float) -> np.ndarray:
    return discount * ((1.0 - up_prob) * next_values[:-1] + up_prob * next_values[1:])


def in_window(t: float, start: float, end: float, tol: float = 1e-10) -> bool:
    return (t + tol) >= start and (t - tol) <= end


def value_game_contract_tree(
    time_grid: np.ndarray,
    dt: float,
    rf: float,
    spot0: float,
    vol: float,
    call_strike_pv: np.ndarray,
    put_strike_pv: np.ndarray,
    allow_partial_calls: bool,
    tie_priority_to_olympus: float,
    state_bps: np.ndarray,
    initial_titan_bp: int,
    option_shares: float,
) -> dict[str, object]:
    n_steps = len(time_grid) - 1
    stock_tree, up_prob, discount = build_recombining_stock_tree(spot0, rf, vol, dt, n_steps)
    positive_states = [int(bp) for bp in state_bps if int(bp) > 0]
    state_index = {int(bp): idx for idx, bp in enumerate(state_bps)}
    target_map = {bp: allowed_call_targets_bp(bp, allow_partial_calls, state_bps) for bp in positive_states}
    called_shares_map = {
        (bp, int(target)): shares_for_bp(bp - int(target))
        for bp in positive_states
        for target in target_map[bp]
    }
    remaining_shares_map = {bp: shares_for_bp(bp) for bp in positive_states}
    next_values_by_state: list[np.ndarray] | None = None

    for step in range(n_steps, -1, -1):
        t = time_grid[step]
        node_count = step + 1
        current_spot = stock_tree[step]

        if next_values_by_state is None:
            continuation_by_state = [np.zeros(node_count, dtype=float) for _ in state_bps]
        else:
            continuation_by_state = [tree_continuation(next_values, discount, up_prob) for next_values in next_values_by_state]

        call_live = in_window(t, CALL_START_YEARS, CALL_END_YEARS)
        put_live = in_window(t, PUT_START_YEARS, PUT_END_YEARS)
        call_intrinsic = np.maximum(current_spot - call_strike_pv[step], 0.0) if call_live else np.zeros(node_count, dtype=float)
        put_intrinsic = np.maximum(put_strike_pv[step] - current_spot, 0.0) if put_live else np.zeros(node_count, dtype=float)

        current_values_by_state: list[np.ndarray] = [np.zeros(node_count, dtype=float)]

        for current_bp in positive_states:
            wait_value = continuation_by_state[state_index[current_bp]]

            if call_live and not put_live:
                state_value = wait_value.copy()
                for target_bp in target_map[current_bp]:
                    call_value = (
                        call_intrinsic * called_shares_map[(current_bp, int(target_bp))]
                        + continuation_by_state[state_index[int(target_bp)]]
                    )
                    state_value = np.maximum(state_value, call_value)

            elif put_live and not call_live:
                put_value = -(put_intrinsic * remaining_shares_map[current_bp])
                state_value = np.minimum(wait_value, put_value)

            elif call_live and put_live:
                put_value = -(put_intrinsic * remaining_shares_map[current_bp])
                state_value = np.minimum(wait_value, put_value)
                for target_bp in target_map[current_bp]:
                    target_idx = state_index[int(target_bp)]
                    called_shares = called_shares_map[(current_bp, int(target_bp))]
                    call_immediate = call_intrinsic * called_shares
                    call_then_wait = call_immediate + continuation_by_state[target_idx]
                    olympus_first_then_titan_puts_residual = call_immediate - (put_intrinsic * shares_for_bp(int(target_bp)))
                    simultaneous_value = (
                        tie_priority_to_olympus * olympus_first_then_titan_puts_residual
                        + (1.0 - tie_priority_to_olympus) * put_value
                    )
                    titan_best_response = np.minimum(call_then_wait, simultaneous_value)
                    state_value = np.maximum(state_value, titan_best_response)

            else:
                state_value = wait_value

            current_values_by_state.append(state_value)

        next_values_by_state = current_values_by_state

    if next_values_by_state is None:
        raise RuntimeError("Tree valuation failed to initialize state values")

    initial_idx = state_index[initial_titan_bp]
    value_total = float(next_values_by_state[initial_idx][0])
    state_values_total = {int(bp): float(next_values_by_state[idx][0]) for idx, bp in enumerate(state_bps)}
    return {
        "value_total": value_total,
        "value_per_share": value_total / option_shares,
        "state_values_total": state_values_total,
        "tree_up_probability": up_prob,
        "tree_discount": discount,
    }


def run_scenario(grid_scenario: GridScenario) -> ScenarioResult:
    n_steps = int(round(TOTAL_YEARS * grid_scenario.steps_per_year))
    dt = TOTAL_YEARS / n_steps
    time_grid = np.arange(n_steps + 1, dtype=float) * dt
    state_bps = build_state_grid_bp(INITIAL_TITAN_BP, RESIDUAL_FLOOR_BP, grid_scenario.state_step_bp)
    _, call_strike_pv, _ = build_notice_strike_path(
        SPA_PRICE,
        CALL_COUPONS,
        time_grid,
        COMPLETION_LAG_YEARS,
        RISK_FREE_RATE,
    )
    _, put_strike_pv, _ = build_notice_strike_path(
        SPA_PRICE,
        PUT_COUPONS,
        time_grid,
        COMPLETION_LAG_YEARS,
        RISK_FREE_RATE,
    )
    result = value_game_contract_tree(
        time_grid=time_grid,
        dt=dt,
        rf=RISK_FREE_RATE,
        spot0=SPA_PRICE,
        vol=ASSET_VOLATILITY,
        call_strike_pv=call_strike_pv,
        put_strike_pv=put_strike_pv,
        allow_partial_calls=ALLOW_PARTIAL_CALLS,
        tie_priority_to_olympus=GAME_TIE_PRIORITY_TO_OLYMPUS,
        state_bps=state_bps,
        initial_titan_bp=INITIAL_TITAN_BP,
        option_shares=OPTION_SHARES,
    )
    return ScenarioResult(
        label=grid_scenario.label,
        steps_per_year=grid_scenario.steps_per_year,
        n_steps=n_steps,
        state_step_bp=grid_scenario.state_step_bp,
        state_count=len(state_bps),
        value_total=float(result["value_total"]),
        value_per_share=float(result["value_per_share"]),
    )


def format_currency_millions(value: float) -> str:
    return f"{value / 1e6:,.2f}"


def write_results_csv(results: list[ScenarioResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    monthly_value = results[0].value_total
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "label",
                "steps_per_year",
                "tree_steps",
                "state_step_pct",
                "state_count",
                "value_usd_m",
                "per_share_usd",
                "delta_vs_monthly_usd_m",
                "delta_vs_monthly_pct",
            ]
        )
        for result in results:
            delta = result.value_total - monthly_value
            delta_pct = delta / monthly_value if monthly_value else 0.0
            writer.writerow(
                [
                    result.label,
                    result.steps_per_year,
                    result.n_steps,
                    result.state_step_bp / 100.0,
                    result.state_count,
                    round(result.value_total / 1e6, 6),
                    round(result.value_per_share, 6),
                    round(delta / 1e6, 6),
                    round(delta_pct, 8),
                ]
            )


def print_results(results: list[ScenarioResult]) -> None:
    monthly_value = results[0].value_total
    print("Project Horizon - High Resolution Tree Analysis")
    print("=" * 78)
    print("Base economics carried forward from the original binomial game-theory notebook.")
    print("Change in this workstream: finer time grid and finer remaining-state grid.")
    print("Core values below are pre-DLOM strategic contract values to Olympus.")
    print("=" * 78)
    print(
        f"{'Scenario':40} {'Value (USD m)':>14} {'Per share':>11} {'Delta vs monthly':>18}"
    )
    print("-" * 78)
    for result in results:
        delta = result.value_total - monthly_value
        print(
            f"{result.label:40} "
            f"{format_currency_millions(result.value_total):>14} "
            f"{result.value_per_share:>11.2f} "
            f"{format_currency_millions(delta):>18}"
        )
    print("-" * 78)
    preferred = results[-1]
    print(
        "Preferred high-resolution tree case: "
        f"{preferred.label} -> USD {format_currency_millions(preferred.value_total)}M "
        f"({preferred.value_per_share:.2f} per option share)"
    )
    print(
        "Interpretation: if the value stabilizes as the grid is refined, "
        "the monthly simplification is not driving the result materially."
    )


def print_action_menu_examples() -> None:
    state_bps = build_state_grid_bp(INITIAL_TITAN_BP, RESIDUAL_FLOOR_BP, 50)
    print("Action-menu diagnostics on the finer 0.5% state grid")
    print("-" * 78)
    for current_bp in [2500, 2000, 1500, 1000, 800]:
        print(f"State {bp_to_pct(current_bp):>4.1f}% | {summarize_call_menu_bp(current_bp, True, state_bps)}")


def main() -> None:
    scenarios = [
        GridScenario("Current monthly tree, 1.0% state grid", 12, 100),
        GridScenario("Weekly tree, 1.0% state grid", 52, 100),
        GridScenario("Business-day tree, 1.0% state grid", 252, 100),
        GridScenario("Business-day tree, 0.5% state grid", 252, 50),
    ]
    results = [run_scenario(scenario) for scenario in scenarios]
    print_results(results)
    print()
    print_action_menu_examples()

    output_csv = Path(__file__).with_name("project_horizon_high_resolution_tree_results.csv")
    write_results_csv(results, output_csv)
    print()
    print(f"Results written to: {output_csv}")


if __name__ == "__main__":
    main()