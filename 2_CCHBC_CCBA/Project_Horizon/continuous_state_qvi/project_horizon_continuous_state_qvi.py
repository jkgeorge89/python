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


def bp_to_pct(bp: int) -> float:
    return bp / 100.0


def bp_to_fraction(bp: int) -> float:
    return bp / 10_000.0


def shares_for_bp(bp: int) -> float:
    return TOTAL_SHARES * bp_to_fraction(bp)


def format_currency_millions(value: float) -> str:
    return f"{value / 1e6:,.3f}"


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


def run_qvi_scenario(scenario: QviScenario) -> QviResult:
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
    )

    return QviResult(
        label=scenario.label,
        steps_per_year=scenario.steps_per_year,
        time_steps=time_steps,
        state_step_bp=scenario.state_step_bp,
        state_count=len(state_bps),
        price_nodes=scenario.price_nodes,
        value_total=float(result["value_total"]),
        value_per_share=float(result["value_per_share"]),
    )


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
    results = [run_qvi_scenario(scenario) for scenario in scenarios]
    print_results(results)
    output_csv = Path(__file__).with_name("project_horizon_continuous_state_qvi_results.csv")
    write_results_csv(results, output_csv)
    print()
    print(f"Results written to: {output_csv}")


if __name__ == "__main__":
    main()