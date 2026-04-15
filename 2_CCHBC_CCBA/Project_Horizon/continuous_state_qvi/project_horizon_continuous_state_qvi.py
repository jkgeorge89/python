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

# Canonical baselines from the existing Project Horizon workstreams.
ORIGINAL_BINOMIAL_MONTHLY_VALUE = 140_936_371.0
HIGH_RESOLUTION_TREE_VALUE = 142_061_172.0


@dataclass(frozen=True)
class QviScenario:
    label: str
    steps_per_year: int
    state_step_bp: int
    price_nodes: int
    quadrature_points: int = 9
    price_std_span: float = 6.0


@dataclass(frozen=True)
class QviResult:
    label: str
    steps_per_year: int
    time_steps: int
    state_step_bp: int
    state_count: int
    price_nodes: int
    value_total: float
    value_per_share: float


@dataclass(frozen=True)
class ExplainabilityArtifacts:
    sample_paths_csv: Path
    policy_checkpoints_csv: Path
    strike_schedule_csv: Path
    explainability_note: Path
    value_surface_csv: Path
    action_surface_csv: Path


ACTION_WAIT = 0
ACTION_CALL = 1
ACTION_PUT = 2
ACTION_TERMINAL = 3

REPRESENTATIVE_PATH_ZS = {
    "low": -1.0,
    "base": 0.0,
    "high": 1.0,
}

CHECKPOINT_STATE_BPS = (2500, 2000, 1500, 1000, 700)
CHECKPOINT_YEARS = (0.0, 1.0, 2.0, 3.0, 3.5, 4.0, 5.0, 6.0)
SURFACE_STATE_BPS = (2500,)


def bp_to_pct(bp: int) -> float:
    return bp / 100.0


def bp_to_fraction(bp: int) -> float:
    return bp / 10_000.0


def shares_for_bp(bp: int) -> float:
    return TOTAL_SHARES * bp_to_fraction(bp)


def format_currency_millions(value: float) -> str:
    return f"{value / 1e6:,.3f}"


def action_code_to_name(action_code: int) -> str:
    return {
        ACTION_WAIT: "wait",
        ACTION_CALL: "call",
        ACTION_PUT: "put",
        ACTION_TERMINAL: "terminal",
    }[action_code]


def build_representative_price_paths(
    time_grid: np.ndarray,
    spot0: float,
    rf: float,
    vol: float,
) -> dict[str, np.ndarray]:
    drift = (rf - 0.5 * vol * vol) * time_grid
    sqrt_time = np.sqrt(time_grid)
    return {
        label: spot0 * np.exp(drift + z_score * vol * sqrt_time)
        for label, z_score in REPRESENTATIVE_PATH_ZS.items()
    }


def representative_path_zscore(label: str) -> float:
    return float(REPRESENTATIVE_PATH_ZS[label])


def coupon_rate_at_time(coupons: np.ndarray, t_years: float) -> float:
    if t_years <= 0.0:
        return float(coupons[0])
    bucket_idx = min(max(int(math.ceil(t_years) - 1), 0), len(coupons) - 1)
    return float(coupons[bucket_idx])


def implied_model_daily_roll_pct(coupon_rate: float, steps_per_year: int) -> float:
    return ((1.0 + coupon_rate) ** (1.0 / steps_per_year) - 1.0) * 100.0


def initialize_explainability_store(
    time_grid: np.ndarray,
    state_bps: np.ndarray,
    call_strike_completion: np.ndarray,
    call_strike_pv: np.ndarray,
    call_completion_grid: np.ndarray,
    put_strike_completion: np.ndarray,
    put_strike_pv: np.ndarray,
    put_completion_grid: np.ndarray,
    price_count: int,
) -> dict[str, object]:
    n_steps = len(time_grid)
    n_states = len(state_bps)
    price_paths = build_representative_price_paths(time_grid, SPA_PRICE, RISK_FREE_RATE, ASSET_VOLATILITY)
    stores: dict[str, dict[str, np.ndarray]] = {}
    state_set = {int(x) for x in state_bps}
    surface_states = tuple(int(bp) for bp in SURFACE_STATE_BPS if int(bp) in state_set)

    for label, prices in price_paths.items():
        stores[label] = {
            "prices": prices,
            "wait_value": np.full((n_steps, n_states), np.nan, dtype=float),
            "best_call_target_bp": np.full((n_steps, n_states), -1, dtype=int),
            "best_call_value": np.full((n_steps, n_states), np.nan, dtype=float),
            "put_value": np.full((n_steps, n_states), np.nan, dtype=float),
            "state_value": np.full((n_steps, n_states), np.nan, dtype=float),
            "optimal_action_code": np.full((n_steps, n_states), ACTION_TERMINAL, dtype=np.int8),
            "optimal_target_bp": np.zeros((n_steps, n_states), dtype=int),
            "call_intrinsic_per_share": np.full((n_steps, n_states), np.nan, dtype=float),
            "put_intrinsic_per_share": np.full((n_steps, n_states), np.nan, dtype=float),
        }

    return {
        "time_grid": time_grid,
        "state_bps": state_bps,
        "call_strike_completion": call_strike_completion,
        "call_strike_pv": call_strike_pv,
        "call_completion_grid": call_completion_grid,
        "put_strike_completion": put_strike_completion,
        "put_strike_pv": put_strike_pv,
        "put_completion_grid": put_completion_grid,
        "stores": stores,
        "surface_states": surface_states,
        "surface_value": {bp: np.full((n_steps, price_count), np.nan, dtype=float) for bp in surface_states},
        "surface_action_code": {bp: np.full((n_steps, price_count), ACTION_TERMINAL, dtype=np.int8) for bp in surface_states},
        "surface_action_target_bp": {bp: np.zeros((n_steps, price_count), dtype=int) for bp in surface_states},
    }


def evaluate_state_policy_at_price(
    price: float,
    current_bp: int,
    continuation_at_price: np.ndarray,
    call_live: bool,
    put_live: bool,
    call_strike_pv: float,
    put_strike_pv: float,
    state_index: dict[int, int],
    target_map: dict[int, np.ndarray],
    called_shares_map: dict[tuple[int, int], float],
    remaining_shares_map: dict[int, float],
    tie_priority_to_olympus: float,
) -> dict[str, float | int]:
    if current_bp == 0:
        return {
            "wait_value": 0.0,
            "best_call_target_bp": -1,
            "best_call_value": math.nan,
            "put_value": math.nan,
            "optimal_action_code": ACTION_TERMINAL,
            "optimal_target_bp": 0,
            "call_intrinsic_per_share": 0.0,
            "put_intrinsic_per_share": 0.0,
        }

    current_idx = state_index[current_bp]
    wait_value = float(continuation_at_price[current_idx])
    call_intrinsic = max(price - call_strike_pv, 0.0) if call_live else 0.0
    put_intrinsic = max(put_strike_pv - price, 0.0) if put_live else 0.0

    best_call_target_bp = -1
    best_call_value = math.nan

    if call_live:
        for target_bp in target_map[current_bp]:
            target_bp = int(target_bp)
            target_idx = state_index[target_bp]
            called_shares = called_shares_map[(current_bp, target_bp)]
            call_immediate = call_intrinsic * called_shares

            if put_live:
                put_value_current = -(put_intrinsic * remaining_shares_map[current_bp])
                call_then_wait = call_immediate + float(continuation_at_price[target_idx])
                olympus_first_then_titan_puts_residual = call_immediate - put_intrinsic * shares_for_bp(target_bp)
                simultaneous_value = (
                    tie_priority_to_olympus * olympus_first_then_titan_puts_residual
                    + (1.0 - tie_priority_to_olympus) * put_value_current
                )
                candidate_value = min(call_then_wait, simultaneous_value)
            else:
                candidate_value = call_immediate + float(continuation_at_price[target_idx])

            if math.isnan(best_call_value) or candidate_value > best_call_value:
                best_call_target_bp = target_bp
                best_call_value = candidate_value

    put_value = -(put_intrinsic * remaining_shares_map[current_bp]) if put_live else math.nan
    optimal_action_code = ACTION_WAIT
    optimal_target_bp = current_bp
    state_value = wait_value

    if call_live and not put_live:
        if not math.isnan(best_call_value) and best_call_value > state_value:
            optimal_action_code = ACTION_CALL
            optimal_target_bp = best_call_target_bp
            state_value = best_call_value

    elif put_live and not call_live:
        if put_value <= wait_value:
            optimal_action_code = ACTION_PUT
            optimal_target_bp = 0
            state_value = put_value

    elif call_live and put_live:
        if put_value <= wait_value:
            optimal_action_code = ACTION_PUT
            optimal_target_bp = 0
            state_value = put_value
        if not math.isnan(best_call_value) and best_call_value > state_value:
            optimal_action_code = ACTION_CALL
            optimal_target_bp = best_call_target_bp
            state_value = best_call_value

    return {
        "wait_value": wait_value,
        "best_call_target_bp": best_call_target_bp,
        "best_call_value": best_call_value,
        "put_value": put_value,
        "optimal_action_code": optimal_action_code,
        "optimal_target_bp": optimal_target_bp,
        "call_intrinsic_per_share": call_intrinsic,
        "put_intrinsic_per_share": put_intrinsic,
    }


def record_explainability_step(
    explainability: dict[str, object],
    step: int,
    price_grid: np.ndarray,
    continuation: np.ndarray,
    current_values: np.ndarray,
    call_live: bool,
    put_live: bool,
    call_strike_pv: float,
    put_strike_pv: float,
    state_bps: np.ndarray,
    state_index: dict[int, int],
    target_map: dict[int, np.ndarray],
    called_shares_map: dict[tuple[int, int], float],
    remaining_shares_map: dict[int, float],
    tie_priority_to_olympus: float,
) -> None:
    for store in explainability["stores"].values():
        price = float(store["prices"][step])
        continuation_at_price = np.array(
            [float(np.interp(price, price_grid, continuation[:, idx])) for idx in range(len(state_bps))],
            dtype=float,
        )

        for current_bp in (int(bp) for bp in state_bps):
            current_idx = state_index[current_bp]
            metrics = evaluate_state_policy_at_price(
                price=price,
                current_bp=current_bp,
                continuation_at_price=continuation_at_price,
                call_live=call_live,
                put_live=put_live,
                call_strike_pv=call_strike_pv,
                put_strike_pv=put_strike_pv,
                state_index=state_index,
                target_map=target_map,
                called_shares_map=called_shares_map,
                remaining_shares_map=remaining_shares_map,
                tie_priority_to_olympus=tie_priority_to_olympus,
            )
            store["wait_value"][step, current_idx] = float(metrics["wait_value"])
            store["best_call_target_bp"][step, current_idx] = int(metrics["best_call_target_bp"])
            store["best_call_value"][step, current_idx] = float(metrics["best_call_value"])
            store["put_value"][step, current_idx] = float(metrics["put_value"])
            store["optimal_action_code"][step, current_idx] = int(metrics["optimal_action_code"])
            store["optimal_target_bp"][step, current_idx] = int(metrics["optimal_target_bp"])
            store["call_intrinsic_per_share"][step, current_idx] = float(metrics["call_intrinsic_per_share"])
            store["put_intrinsic_per_share"][step, current_idx] = float(metrics["put_intrinsic_per_share"])
            store["state_value"][step, current_idx] = float(np.interp(price, price_grid, current_values[:, current_idx]))


def record_surface_step(
    explainability: dict[str, object],
    step: int,
    price_grid: np.ndarray,
    continuation: np.ndarray,
    current_values: np.ndarray,
    call_live: bool,
    put_live: bool,
    call_strike_pv: float,
    put_strike_pv: float,
    state_index: dict[int, int],
    target_map: dict[int, np.ndarray],
    called_shares_map: dict[tuple[int, int], float],
    remaining_shares_map: dict[int, float],
    tie_priority_to_olympus: float,
) -> None:
    for current_bp in explainability["surface_states"]:
        current_idx = state_index[current_bp]
        explainability["surface_value"][current_bp][step, :] = current_values[:, current_idx]
        action_codes = explainability["surface_action_code"][current_bp][step, :]
        action_targets = explainability["surface_action_target_bp"][current_bp][step, :]

        for price_idx, price in enumerate(price_grid):
            metrics = evaluate_state_policy_at_price(
                price=float(price),
                current_bp=current_bp,
                continuation_at_price=continuation[price_idx, :],
                call_live=call_live,
                put_live=put_live,
                call_strike_pv=call_strike_pv,
                put_strike_pv=put_strike_pv,
                state_index=state_index,
                target_map=target_map,
                called_shares_map=called_shares_map,
                remaining_shares_map=remaining_shares_map,
                tie_priority_to_olympus=tie_priority_to_olympus,
            )
            action_codes[price_idx] = int(metrics["optimal_action_code"])
            action_targets[price_idx] = int(metrics["optimal_target_bp"])


def nearest_time_step_index(time_grid: np.ndarray, year_value: float) -> int:
    return int(np.argmin(np.abs(time_grid - year_value)))


def write_sample_paths_csv(
    explainability: dict[str, object],
    output_path: Path,
    initial_titan_bp: int,
) -> None:
    time_grid = explainability["time_grid"]
    state_bps = explainability["state_bps"]
    call_strike_pv = explainability["call_strike_pv"]
    put_strike_pv = explainability["put_strike_pv"]
    state_index = {int(bp): idx for idx, bp in enumerate(state_bps)}

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "scenario_label",
                "representative_path_zscore",
                "step_index",
                "time_years",
                "price_per_share_usd",
                "current_titan_stake_pct_before",
                "call_live",
                "put_live",
                "call_strike_pv_per_share_usd",
                "put_strike_pv_per_share_usd",
                "call_intrinsic_per_share_usd",
                "put_intrinsic_per_share_usd",
                "wait_value_usd_m",
                "best_call_target_pct",
                "best_call_value_usd_m",
                "put_value_usd_m",
                "optimal_action",
                "optimal_target_pct",
                "state_value_usd_m",
                "current_titan_stake_pct_after",
            ]
        )

        for label, store in explainability["stores"].items():
            current_bp = initial_titan_bp
            z_score = representative_path_zscore(label)
            for step, time_years in enumerate(time_grid):
                current_idx = state_index[current_bp]
                action_code = int(store["optimal_action_code"][step, current_idx])
                optimal_target_bp = int(store["optimal_target_bp"][step, current_idx])
                next_bp = current_bp
                if action_code == ACTION_CALL:
                    next_bp = optimal_target_bp
                elif action_code == ACTION_PUT:
                    next_bp = 0

                call_live = in_window(float(time_years), CALL_START_YEARS, CALL_END_YEARS)
                put_live = in_window(float(time_years), PUT_START_YEARS, PUT_END_YEARS)
                best_call_target_bp = int(store["best_call_target_bp"][step, current_idx])
                writer.writerow(
                    [
                        label,
                        round(z_score, 6),
                        step,
                        round(float(time_years), 6),
                        round(float(store["prices"][step]), 6),
                        round(bp_to_pct(current_bp), 6),
                        int(call_live),
                        int(put_live),
                        round(float(call_strike_pv[step]), 6),
                        round(float(put_strike_pv[step]), 6),
                        round(float(store["call_intrinsic_per_share"][step, current_idx]), 6),
                        round(float(store["put_intrinsic_per_share"][step, current_idx]), 6),
                        round(float(store["wait_value"][step, current_idx]) / 1e6, 6),
                        "" if best_call_target_bp < 0 else round(bp_to_pct(best_call_target_bp), 6),
                        "" if math.isnan(float(store["best_call_value"][step, current_idx])) else round(float(store["best_call_value"][step, current_idx]) / 1e6, 6),
                        "" if math.isnan(float(store["put_value"][step, current_idx])) else round(float(store["put_value"][step, current_idx]) / 1e6, 6),
                        action_code_to_name(action_code),
                        round(bp_to_pct(optimal_target_bp), 6),
                        round(float(store["state_value"][step, current_idx]) / 1e6, 6),
                        round(bp_to_pct(next_bp), 6),
                    ]
                )
                current_bp = next_bp


def write_policy_checkpoints_csv(
    explainability: dict[str, object],
    output_path: Path,
) -> None:
    time_grid = explainability["time_grid"]
    state_bps = explainability["state_bps"]
    call_strike_pv = explainability["call_strike_pv"]
    put_strike_pv = explainability["put_strike_pv"]
    state_index = {int(bp): idx for idx, bp in enumerate(state_bps)}
    checkpoint_steps = sorted({nearest_time_step_index(time_grid, year_value) for year_value in CHECKPOINT_YEARS})
    checkpoint_state_bps = [bp for bp in CHECKPOINT_STATE_BPS if bp in state_index]

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "scenario_label",
                "representative_path_zscore",
                "step_index",
                "time_years",
                "price_per_share_usd",
                "titan_stake_pct",
                "call_live",
                "put_live",
                "call_strike_pv_per_share_usd",
                "put_strike_pv_per_share_usd",
                "call_intrinsic_per_share_usd",
                "put_intrinsic_per_share_usd",
                "wait_value_usd_m",
                "best_call_target_pct",
                "best_call_value_usd_m",
                "put_value_usd_m",
                "optimal_action",
                "optimal_target_pct",
                "state_value_usd_m",
            ]
        )

        for label, store in explainability["stores"].items():
            z_score = representative_path_zscore(label)
            for step in checkpoint_steps:
                time_years = float(time_grid[step])
                call_live = in_window(time_years, CALL_START_YEARS, CALL_END_YEARS)
                put_live = in_window(time_years, PUT_START_YEARS, PUT_END_YEARS)
                for current_bp in checkpoint_state_bps:
                    current_idx = state_index[current_bp]
                    action_code = int(store["optimal_action_code"][step, current_idx])
                    best_call_target_bp = int(store["best_call_target_bp"][step, current_idx])
                    optimal_target_bp = int(store["optimal_target_bp"][step, current_idx])
                    writer.writerow(
                        [
                            label,
                            round(z_score, 6),
                            step,
                            round(time_years, 6),
                            round(float(store["prices"][step]), 6),
                            round(bp_to_pct(current_bp), 6),
                            int(call_live),
                            int(put_live),
                            round(float(call_strike_pv[step]), 6),
                            round(float(put_strike_pv[step]), 6),
                            round(float(store["call_intrinsic_per_share"][step, current_idx]), 6),
                            round(float(store["put_intrinsic_per_share"][step, current_idx]), 6),
                            round(float(store["wait_value"][step, current_idx]) / 1e6, 6),
                            "" if best_call_target_bp < 0 else round(bp_to_pct(best_call_target_bp), 6),
                            "" if math.isnan(float(store["best_call_value"][step, current_idx])) else round(float(store["best_call_value"][step, current_idx]) / 1e6, 6),
                            "" if math.isnan(float(store["put_value"][step, current_idx])) else round(float(store["put_value"][step, current_idx]) / 1e6, 6),
                            action_code_to_name(action_code),
                            round(bp_to_pct(optimal_target_bp), 6),
                            round(float(store["state_value"][step, current_idx]) / 1e6, 6),
                        ]
                    )


def write_strike_schedule_csv(
    explainability: dict[str, object],
    output_path: Path,
    steps_per_year: int,
) -> None:
    time_grid = explainability["time_grid"]
    call_strike_completion = explainability["call_strike_completion"]
    call_strike_pv = explainability["call_strike_pv"]
    call_completion_grid = explainability["call_completion_grid"]
    put_strike_completion = explainability["put_strike_completion"]
    put_strike_pv = explainability["put_strike_pv"]
    put_completion_grid = explainability["put_completion_grid"]

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "step_index",
                "time_years",
                "steps_per_year_model",
                "call_live",
                "put_live",
                "call_coupon_rate_pct",
                "put_coupon_rate_pct",
                "call_model_daily_roll_pct",
                "put_model_daily_roll_pct",
                "call_completion_time_years",
                "put_completion_time_years",
                "call_strike_completion_per_share_usd",
                "call_strike_pv_per_share_usd",
                "put_strike_completion_per_share_usd",
                "put_strike_pv_per_share_usd",
            ]
        )

        for step, time_years in enumerate(time_grid):
            call_coupon_rate = coupon_rate_at_time(CALL_COUPONS, float(call_completion_grid[step]))
            put_coupon_rate = coupon_rate_at_time(PUT_COUPONS, float(put_completion_grid[step]))
            writer.writerow(
                [
                    step,
                    round(float(time_years), 6),
                    steps_per_year,
                    int(in_window(float(time_years), CALL_START_YEARS, CALL_END_YEARS)),
                    int(in_window(float(time_years), PUT_START_YEARS, PUT_END_YEARS)),
                    round(call_coupon_rate * 100.0, 4),
                    round(put_coupon_rate * 100.0, 4),
                    round(implied_model_daily_roll_pct(call_coupon_rate, steps_per_year), 8),
                    round(implied_model_daily_roll_pct(put_coupon_rate, steps_per_year), 8),
                    round(float(call_completion_grid[step]), 6),
                    round(float(put_completion_grid[step]), 6),
                    round(float(call_strike_completion[step]), 6),
                    round(float(call_strike_pv[step]), 6),
                    round(float(put_strike_completion[step]), 6),
                    round(float(put_strike_pv[step]), 6),
                ]
            )


def build_surface_header(time_grid: np.ndarray) -> list[str]:
    return ["price_per_share_usd"] + [f"day_{step:04d}_y{time_years:.6f}" for step, time_years in enumerate(time_grid)]


def write_value_surface_csv(
    explainability: dict[str, object],
    output_path: Path,
    state_bp: int,
) -> None:
    time_grid = explainability["time_grid"]
    state_values = explainability["surface_value"][state_bp]
    price_grid = build_log_price_grid(SPA_PRICE, ASSET_VOLATILITY, TOTAL_YEARS, state_values.shape[1], 6.0)[1]

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(build_surface_header(time_grid))
        for price_idx, price in enumerate(price_grid):
            writer.writerow([round(float(price), 6)] + [round(float(value) / 1e6, 6) for value in state_values[:, price_idx]])


def write_action_surface_csv(
    explainability: dict[str, object],
    output_path: Path,
    state_bp: int,
) -> None:
    time_grid = explainability["time_grid"]
    action_codes = explainability["surface_action_code"][state_bp]
    action_targets = explainability["surface_action_target_bp"][state_bp]
    price_grid = build_log_price_grid(SPA_PRICE, ASSET_VOLATILITY, TOTAL_YEARS, action_codes.shape[1], 6.0)[1]

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(build_surface_header(time_grid))
        for price_idx, price in enumerate(price_grid):
            row = [round(float(price), 6)]
            for step in range(action_codes.shape[0]):
                action_code = int(action_codes[step, price_idx])
                target_bp = int(action_targets[step, price_idx])
                if action_code == ACTION_CALL:
                    row.append(f"call->{bp_to_pct(target_bp):.2f}%")
                elif action_code == ACTION_PUT:
                    row.append("put->0.00%")
                elif action_code == ACTION_TERMINAL:
                    row.append("terminal")
                else:
                    row.append("wait")
            writer.writerow(row)


def write_explainability_note(
    output_path: Path,
    sample_paths_csv: Path,
    policy_checkpoints_csv: Path,
    strike_schedule_csv: Path,
    value_surface_csv: Path,
    action_surface_csv: Path,
) -> None:
    output_path.write_text(
        """# Project Horizon - Continuous State QVI Explainability Outputs

## Why these files exist

The QVI workstream is **not** a Monte Carlo path simulation.

That means there are no 1,000,000 simulated paths to sample in the same way you would sample a Least-Squares Monte Carlo engine.

Instead, the meaningful audit-facing outputs are:

1. representative **policy path traces**; and
2. representative **policy checkpoint tables**.

These files are intended to show, in a transparent CSV format, what the QVI solver is doing at selected points in time, price, and remaining-stake space.

## Output files

- `project_horizon_continuous_state_qvi_sample_paths.csv`
- `project_horizon_continuous_state_qvi_policy_checkpoints.csv`
- `project_horizon_continuous_state_qvi_strike_schedule.csv`
- `project_horizon_continuous_state_qvi_value_surface_25pct.csv`
- `project_horizon_continuous_state_qvi_action_surface_25pct.csv`

## How to read them

### 1. Strike schedule

The strike-schedule file is the deterministic term structure of the contractual strike on the model grid.

It exists because the strike is fully knowable at every modeled day once you specify:

- the SPA base price;
- the contractual coupon schedule; and
- the completion-lag assumption.

For each business-day step, the file shows:

- whether the call and put windows are live;
- the annual coupon rate currently driving the call and put strike accrual;
- the implied one-model-day roll on the 252-step grid; and
- the resulting call and put strike levels, both at completion and in present-value terms.

The current implementation uses a **252-step business-day year** and samples the contractual annual coupon schedule on that grid.

That means that within a coupon year the modeled daily strike roll is:

`daily roll = (1 + annual coupon)^(1/252) - 1`

So there is no hidden mismatch in the code between "annual coupon" and "daily trading steps". The annual schedule is being applied fractionally on the daily model grid.

What is still a modeling assumption is the **day-count basis**. Right now the solver treats one model year as 252 equal business-day steps. If the legal strike accrual should instead be tied to actual calendar days or a different contractual day-count convention, that should be changed explicitly.

### 2. Sample paths

The sample-path file is **not** a random Monte Carlo sample.

It contains three deterministic representative price paths, and `scenario_label` should really be read as a **representative path label**, not as a separate valuation scenario.

The three labels are:

- `low` = roughly a one-sigma-below path;
- `base` = the central drift path; and
- `high` = roughly a one-sigma-above path.

There is no separate `mid` path in the current outputs. `base` is the middle path.

The new `representative_path_zscore` column makes this explicit:

- `low = -1.0`;
- `base = 0.0`; and
- `high = +1.0`.

For each business-day step, the file shows:

- the sampled price per share;
- the representative path z-score;
- Titan's stake before the decision;
- whether the call and/or put is live;
- the wait value;
- the best call target and associated value;
- the put value if live; and
- the optimal action implied by the QVI recursion.

That gives a start-to-finish trace of how the policy reacts under low, base, and high market states.

### 3. Policy checkpoints

The checkpoint file is a compact review table built from those same representative path labels at selected years and selected Titan stakes.

It is designed for MD, client, and audit review.

The most useful checkpoint years are:

- `t0`;
- Year 3.0 when the call first goes live;
- Year 3.5 when the overlap begins;
- Year 5.0 when the call window closes; and
- Year 6.0 at final put expiry.

The most useful remaining-stake states are:

- 25.0%;
- 20.0%;
- 15.0%;
- 10.0%; and
- 7.0%.

It is therefore a **thin reporting slice**, not the full state space.

### 4. Full 25% state surface

The value-surface and action-surface files are the closest QVI equivalent to a daily tree that can be opened in Excel.

They show, for the initial 25.0% Titan stake state:

- rows = price nodes;
- columns = business-day steps; and
- each cell = either the value at that state or the optimal action at that state.

This is **not** a Pascal triangle or a recombining up/down lattice.

It is a rectangular price-by-time grid for one ownership state, which is the correct visual representation of the QVI solver.

These two files do **not** depend on the `low` / `base` / `high` reporting labels. They are full-grid outputs for the 25% remaining-stake sheet.

## Practical audit message

If the question is "show me what the Python model is doing," the right answer for the QVI workstream is:

- show the deterministic strike schedule explicitly;
- show representative path traces rather than random Monte Carlo paths; and
- show checkpoint tables that compare wait / call / put at key states.

That is the honest equivalent of a path sample for a grid-based dynamic-programming solver.
""",
        encoding="utf-8",
    )


def write_explainability_outputs(
    explainability: dict[str, object],
    output_dir: Path,
    initial_titan_bp: int,
    steps_per_year: int,
) -> ExplainabilityArtifacts:
    sample_paths_csv = output_dir / "project_horizon_continuous_state_qvi_sample_paths.csv"
    policy_checkpoints_csv = output_dir / "project_horizon_continuous_state_qvi_policy_checkpoints.csv"
    strike_schedule_csv = output_dir / "project_horizon_continuous_state_qvi_strike_schedule.csv"
    explainability_note = output_dir / "Project_Horizon_Continuous_State_QVI_Explainability.md"
    value_surface_csv = output_dir / "project_horizon_continuous_state_qvi_value_surface_25pct.csv"
    action_surface_csv = output_dir / "project_horizon_continuous_state_qvi_action_surface_25pct.csv"

    write_sample_paths_csv(explainability, sample_paths_csv, initial_titan_bp)
    write_policy_checkpoints_csv(explainability, policy_checkpoints_csv)
    write_strike_schedule_csv(explainability, strike_schedule_csv, steps_per_year)
    write_value_surface_csv(explainability, value_surface_csv, initial_titan_bp)
    write_action_surface_csv(explainability, action_surface_csv, initial_titan_bp)
    write_explainability_note(
        explainability_note,
        sample_paths_csv,
        policy_checkpoints_csv,
        strike_schedule_csv,
        value_surface_csv,
        action_surface_csv,
    )

    return ExplainabilityArtifacts(
        sample_paths_csv=sample_paths_csv,
        policy_checkpoints_csv=policy_checkpoints_csv,
        strike_schedule_csv=strike_schedule_csv,
        explainability_note=explainability_note,
        value_surface_csv=value_surface_csv,
        action_surface_csv=action_surface_csv,
    )


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
    if (initial_bp - residual_floor_bp) % state_step_bp != 0:
        raise ValueError("state_step_bp must divide the distance between the floor and initial stake")
    positive_states = np.arange(residual_floor_bp, initial_bp + state_step_bp, state_step_bp, dtype=int)
    positive_states = positive_states[positive_states <= initial_bp]
    if positive_states[-1] != initial_bp:
        raise ValueError("state grid must include the initial Titan stake exactly")
    return np.concatenate(([0], positive_states))


def allowed_call_targets_bp(current_bp: int, allow_partial_calls: bool, state_bps: np.ndarray) -> np.ndarray:
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


def build_log_price_grid(
    spot0: float,
    vol: float,
    total_years: float,
    price_nodes: int,
    price_std_span: float,
) -> tuple[np.ndarray, np.ndarray]:
    if price_nodes % 2 == 0:
        raise ValueError("price_nodes must be odd so the initial spot sits on the center node")
    log_spot = math.log(spot0)
    log_span = price_std_span * vol * math.sqrt(total_years)
    log_grid = np.linspace(log_spot - log_span, log_spot + log_span, price_nodes)
    return log_grid, np.exp(log_grid)


def build_expectation_operator(
    log_price_grid: np.ndarray,
    dt: float,
    rf: float,
    vol: float,
    quadrature_points: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.hermite.hermgauss(quadrature_points)
    weights = weights / math.sqrt(math.pi)

    x_min = float(log_price_grid[0])
    dx = float(log_price_grid[1] - log_price_grid[0])
    n_prices = len(log_price_grid)

    mu = (rf - 0.5 * vol * vol) * dt
    sigma = vol * math.sqrt(dt)

    x_current = log_price_grid[:, None]
    x_next = x_current + mu + math.sqrt(2.0) * sigma * nodes[None, :]
    idx_float = (x_next - x_min) / dx

    idx_low = np.floor(idx_float).astype(int)
    alpha = idx_float - idx_low

    idx_low = np.clip(idx_low, 0, n_prices - 2)
    alpha = np.where(idx_float <= 0.0, 0.0, alpha)
    alpha = np.where(idx_float >= (n_prices - 1), 1.0, alpha)

    idx_high = idx_low + 1
    return idx_low, idx_high, alpha * 1.0, weights


def apply_expectation_operator(
    next_values: np.ndarray,
    idx_low: np.ndarray,
    idx_high: np.ndarray,
    alpha: np.ndarray,
    weights: np.ndarray,
    discount: float,
) -> np.ndarray:
    lower_vals = np.take(next_values, idx_low, axis=0)
    upper_vals = np.take(next_values, idx_high, axis=0)
    interpolated = (1.0 - alpha[..., None]) * lower_vals + alpha[..., None] * upper_vals
    return discount * np.tensordot(interpolated, weights, axes=([1], [0]))


def in_window(t: float, start: float, end: float, tol: float = 1e-10) -> bool:
    return (t + tol) >= start and (t - tol) <= end


def value_game_contract_qvi(
    time_grid: np.ndarray,
    rf: float,
    price_grid: np.ndarray,
    idx_low: np.ndarray,
    idx_high: np.ndarray,
    alpha: np.ndarray,
    quadrature_weights: np.ndarray,
    call_strike_pv: np.ndarray,
    put_strike_pv: np.ndarray,
    allow_partial_calls: bool,
    tie_priority_to_olympus: float,
    state_bps: np.ndarray,
    initial_titan_bp: int,
    option_shares: float,
    dt: float,
    explainability: dict[str, object] | None = None,
) -> dict[str, object]:
    discount = math.exp(-rf * dt)
    n_prices = len(price_grid)
    state_index = {int(bp): idx for idx, bp in enumerate(state_bps)}
    positive_states = [int(bp) for bp in state_bps if int(bp) > 0]
    next_values = np.zeros((n_prices, len(state_bps)), dtype=float)

    target_map = {bp: allowed_call_targets_bp(bp, allow_partial_calls, state_bps) for bp in positive_states}
    called_shares_map = {
        (bp, int(target)): shares_for_bp(bp - int(target))
        for bp in positive_states
        for target in target_map[bp]
    }
    remaining_shares_map = {bp: shares_for_bp(bp) for bp in positive_states}

    for step in range(len(time_grid) - 1, -1, -1):
        t = time_grid[step]
        continuation = apply_expectation_operator(
            next_values,
            idx_low,
            idx_high,
            alpha,
            quadrature_weights,
            discount,
        )

        call_live = in_window(t, CALL_START_YEARS, CALL_END_YEARS)
        put_live = in_window(t, PUT_START_YEARS, PUT_END_YEARS)
        call_intrinsic = np.maximum(price_grid - call_strike_pv[step], 0.0) if call_live else np.zeros_like(price_grid)
        put_intrinsic = np.maximum(put_strike_pv[step] - price_grid, 0.0) if put_live else np.zeros_like(price_grid)

        current_values = np.zeros_like(next_values)

        for current_bp in positive_states:
            current_idx = state_index[current_bp]
            wait_value = continuation[:, current_idx]

            if call_live and not put_live:
                state_value = wait_value.copy()
                for target_bp in target_map[current_bp]:
                    target_idx = state_index[int(target_bp)]
                    call_value = call_intrinsic * called_shares_map[(current_bp, int(target_bp))] + continuation[:, target_idx]
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
                    call_then_wait = call_immediate + continuation[:, target_idx]
                    olympus_first_then_titan_puts_residual = call_immediate - put_intrinsic * shares_for_bp(int(target_bp))
                    simultaneous_value = (
                        tie_priority_to_olympus * olympus_first_then_titan_puts_residual
                        + (1.0 - tie_priority_to_olympus) * put_value
                    )
                    titan_best_response = np.minimum(call_then_wait, simultaneous_value)
                    state_value = np.maximum(state_value, titan_best_response)

            else:
                state_value = wait_value

            current_values[:, current_idx] = state_value

        if explainability is not None:
            record_explainability_step(
                explainability=explainability,
                step=step,
                price_grid=price_grid,
                continuation=continuation,
                current_values=current_values,
                call_live=call_live,
                put_live=put_live,
                call_strike_pv=float(call_strike_pv[step]),
                put_strike_pv=float(put_strike_pv[step]),
                state_bps=state_bps,
                state_index=state_index,
                target_map=target_map,
                called_shares_map=called_shares_map,
                remaining_shares_map=remaining_shares_map,
                tie_priority_to_olympus=tie_priority_to_olympus,
            )
            record_surface_step(
                explainability=explainability,
                step=step,
                price_grid=price_grid,
                continuation=continuation,
                current_values=current_values,
                call_live=call_live,
                put_live=put_live,
                call_strike_pv=float(call_strike_pv[step]),
                put_strike_pv=float(put_strike_pv[step]),
                state_index=state_index,
                target_map=target_map,
                called_shares_map=called_shares_map,
                remaining_shares_map=remaining_shares_map,
                tie_priority_to_olympus=tie_priority_to_olympus,
            )

        next_values = current_values

    initial_price_value = float(np.interp(SPA_PRICE, price_grid, next_values[:, state_index[initial_titan_bp]]))
    state_values_total = {
        int(bp): float(np.interp(SPA_PRICE, price_grid, next_values[:, idx])) for idx, bp in enumerate(state_bps)
    }
    return {
        "value_total": initial_price_value,
        "value_per_share": initial_price_value / option_shares,
        "state_values_total": state_values_total,
    }


def run_qvi_scenario_collect(
    scenario: QviScenario,
    explainability_output_dir: Path | None = None,
) -> tuple[QviResult, ExplainabilityArtifacts | None]:
    time_steps = int(round(TOTAL_YEARS * scenario.steps_per_year))
    dt = TOTAL_YEARS / time_steps
    time_grid = np.arange(time_steps + 1, dtype=float) * dt
    state_bps = build_state_grid_bp(INITIAL_TITAN_BP, RESIDUAL_FLOOR_BP, scenario.state_step_bp)
    log_price_grid, price_grid = build_log_price_grid(
        SPA_PRICE,
        ASSET_VOLATILITY,
        TOTAL_YEARS,
        scenario.price_nodes,
        scenario.price_std_span,
    )
    idx_low, idx_high, alpha, quadrature_weights = build_expectation_operator(
        log_price_grid,
        dt,
        RISK_FREE_RATE,
        ASSET_VOLATILITY,
        scenario.quadrature_points,
    )
    call_strike_completion, call_strike_pv, call_completion_grid = build_notice_strike_path(
        SPA_PRICE,
        CALL_COUPONS,
        time_grid,
        COMPLETION_LAG_YEARS,
        RISK_FREE_RATE,
    )
    put_strike_completion, put_strike_pv, put_completion_grid = build_notice_strike_path(
        SPA_PRICE,
        PUT_COUPONS,
        time_grid,
        COMPLETION_LAG_YEARS,
        RISK_FREE_RATE,
    )

    explainability = None
    if explainability_output_dir is not None:
        explainability = initialize_explainability_store(
            time_grid,
            state_bps,
            call_strike_completion,
            call_strike_pv,
            call_completion_grid,
            put_strike_completion,
            put_strike_pv,
            put_completion_grid,
            len(price_grid),
        )

    result = value_game_contract_qvi(
        time_grid=time_grid,
        rf=RISK_FREE_RATE,
        price_grid=price_grid,
        idx_low=idx_low,
        idx_high=idx_high,
        alpha=alpha,
        quadrature_weights=quadrature_weights,
        call_strike_pv=call_strike_pv,
        put_strike_pv=put_strike_pv,
        allow_partial_calls=ALLOW_PARTIAL_CALLS,
        tie_priority_to_olympus=GAME_TIE_PRIORITY_TO_OLYMPUS,
        state_bps=state_bps,
        initial_titan_bp=INITIAL_TITAN_BP,
        option_shares=OPTION_SHARES,
        dt=dt,
        explainability=explainability,
    )

    qvi_result = QviResult(
        label=scenario.label,
        steps_per_year=scenario.steps_per_year,
        time_steps=time_steps,
        state_step_bp=scenario.state_step_bp,
        state_count=len(state_bps),
        price_nodes=scenario.price_nodes,
        value_total=float(result["value_total"]),
        value_per_share=float(result["value_per_share"]),
    )

    artifacts = None
    if explainability_output_dir is not None and explainability is not None:
        artifacts = write_explainability_outputs(
            explainability,
            explainability_output_dir,
            INITIAL_TITAN_BP,
            scenario.steps_per_year,
        )

    return qvi_result, artifacts


def run_qvi_scenario(scenario: QviScenario) -> QviResult:
    result, _ = run_qvi_scenario_collect(scenario)
    return result


def write_results_csv(results: list[QviResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "label",
                "steps_per_year",
                "time_steps",
                "state_step_pct",
                "state_count",
                "price_nodes",
                "value_usd_m",
                "per_share_usd",
                "delta_vs_140_936m_usd_m",
                "delta_vs_140_936m_pct",
                "delta_vs_high_resolution_tree_usd_m",
                "delta_vs_high_resolution_tree_pct",
            ]
        )
        for result in results:
            delta_vs_monthly = result.value_total - ORIGINAL_BINOMIAL_MONTHLY_VALUE
            delta_vs_tree = result.value_total - HIGH_RESOLUTION_TREE_VALUE
            writer.writerow(
                [
                    result.label,
                    result.steps_per_year,
                    result.time_steps,
                    result.state_step_bp / 100.0,
                    result.state_count,
                    result.price_nodes,
                    round(result.value_total / 1e6, 6),
                    round(result.value_per_share, 6),
                    round(delta_vs_monthly / 1e6, 6),
                    round(delta_vs_monthly / ORIGINAL_BINOMIAL_MONTHLY_VALUE, 8),
                    round(delta_vs_tree / 1e6, 6),
                    round(delta_vs_tree / HIGH_RESOLUTION_TREE_VALUE, 8),
                ]
            )


def print_results(results: list[QviResult]) -> None:
    print("Project Horizon - Continuous-State QVI Reference")
    print("=" * 88)
    print("This workstream approximates the strategic contract on a business-day time grid,")
    print("a continuous stock-price state, and a fine remaining-stake control grid.")
    print("It is a reference dynamic-programming solver, not the original binomial notebook.")
    print("=" * 88)
    print(
        f"{'Scenario':34} {'Value (USD m)':>14} {'Per share':>11} {'vs 140.936M':>14} {'vs HR tree':>14}"
    )
    print("-" * 88)
    for result in results:
        delta_vs_monthly = result.value_total - ORIGINAL_BINOMIAL_MONTHLY_VALUE
        delta_vs_tree = result.value_total - HIGH_RESOLUTION_TREE_VALUE
        print(
            f"{result.label:34} "
            f"{format_currency_millions(result.value_total):>14} "
            f"{result.value_per_share:>11.3f} "
            f"{format_currency_millions(delta_vs_monthly):>14} "
            f"{format_currency_millions(delta_vs_tree):>14}"
        )
    print("-" * 88)
    preferred = results[-1]
    print(
        "Preferred reference case: "
        f"{preferred.label} -> USD {format_currency_millions(preferred.value_total)}M "
        f"({preferred.value_per_share:.3f} per option share)"
    )
    print(
        "Increment versus the original 140.936M monthly binomial build: "
        f"USD {format_currency_millions(preferred.value_total - ORIGINAL_BINOMIAL_MONTHLY_VALUE)}M "
        f"({(preferred.value_total - ORIGINAL_BINOMIAL_MONTHLY_VALUE) / ORIGINAL_BINOMIAL_MONTHLY_VALUE:.3%})"
    )
    print(
        "Increment versus the separate high-resolution tree build: "
        f"USD {format_currency_millions(preferred.value_total - HIGH_RESOLUTION_TREE_VALUE)}M "
        f"({(preferred.value_total - HIGH_RESOLUTION_TREE_VALUE) / HIGH_RESOLUTION_TREE_VALUE:.3%})"
    )
    if len(results) >= 2:
        last_step = results[-1].value_total - results[-2].value_total
        print(
            "Last price-grid refinement step: "
            f"USD {format_currency_millions(last_step)}M "
            f"({last_step / results[-2].value_total:.3%})"
        )


def main() -> None:
    scenarios = [
        QviScenario("Daily QVI, 0.25% / 801 prices", 252, 25, 801),
        QviScenario("Daily QVI, 0.25% / 1001 prices", 252, 25, 1001),
        QviScenario("Daily QVI, 0.25% / 1201 prices", 252, 25, 1201),
    ]
    results: list[QviResult] = []
    explainability_artifacts = None
    for idx, scenario in enumerate(scenarios):
        if idx == len(scenarios) - 1:
            result, explainability_artifacts = run_qvi_scenario_collect(
                scenario,
                Path(__file__).resolve().parent,
            )
        else:
            result, _ = run_qvi_scenario_collect(scenario)
        results.append(result)
    print_results(results)
    output_csv = Path(__file__).with_name("project_horizon_continuous_state_qvi_results.csv")
    write_results_csv(results, output_csv)
    print()
    print(f"Results written to: {output_csv}")
    if explainability_artifacts is not None:
        print("Explainability outputs written to:")
        print(f" - {explainability_artifacts.sample_paths_csv}")
        print(f" - {explainability_artifacts.policy_checkpoints_csv}")
        print(f" - {explainability_artifacts.strike_schedule_csv}")
        print(f" - {explainability_artifacts.explainability_note}")
        print(f" - {explainability_artifacts.value_surface_csv}")
        print(f" - {explainability_artifacts.action_surface_csv}")


if __name__ == "__main__":
    main()