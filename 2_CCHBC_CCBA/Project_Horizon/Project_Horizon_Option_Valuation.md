# Project Horizon – Valuation of Structured Option Instrument
**Prepared for:** [MD Name]
**Date:** December 31, 2025
**Subject:** Fair Value Assessment – Call and Put Option over 25% Stake in CCBA

---

## 1. Background and Agreement Summary

In connection with CCHBC's acquisition of a 75% interest in Coca-Cola Beverages Africa ("CCBA"), the Option Agreement governs the treatment of the remaining **25% equity stake** (1,386,020 E ordinary shares) retained by The Coca-Cola Company ("TCCC") at SPA completion.

The agreement is between:

| Party | Legal Entity | Role |
|---|---|---|
| **CCHBC** | Coca-Cola HBC Holdings B.V. ("Olympus BV") | Acquiror; granted the **Call Option** |
| **TCCC** | European Refreshments Unlimited Co. ("Titan"), guaranteed by The Coca-Cola Company | Seller; granted the **Put Option** |

The instrument creates a bilateral option structure: CCHBC has the right to acquire the remaining 25% stake at any time within the Call window; TCCC has the right to force a sale of that same stake at any time within the Put window. The underlying in both cases is the same block of shares, at the same contractually-determined price.

---

## 2. Key Commercial Terms

### 2.1 Option Shares
- **1,386,020 E ordinary shares**, representing **25% of total equity**
- Implied value at SPA price: **USD 800 million** (25% × USD 3.2bn total equity consideration)

### 2.2 Exercise Windows

| Option | Holder | Opens | Expires | Duration |
|---|---|---|---|---|
| **Call** | CCHBC (Olympus BV) | Year 3 from SPA Completion | Year 5 | 2 years |
| **Put** | TCCC (Titan) | Year 3.5 from SPA Completion | Year 6 | 2.5 years |

The windows overlap between **Year 3.5 and Year 5** (1.5 years). During this overlap period, both options are simultaneously live. The agreement provides that exercise by either party extinguishes the other's option (the "One Live Notice" mechanism). Outside the overlap:

- **Year 3.0 – 3.5:** Call only — CCHBC may acquire; TCCC has no right to force a sale
- **Year 3.5 – 5.0:** Overlap — both parties hold live options
- **Year 5.0 – 6.0:** Put only — Call has expired; TCCC may force a sale

```
Year:  0────1────2────3───3.5──────5──────────6
                      │    │        │           │
CCHBC  (Call)         ├────┼────────┤           │
TCCC   (Put)          │    ├────────┼───────────┤
                      │    │        │           │
                   Call  OVERLAP  Put           │
                   only  Yr3.5-5  only          │
                   0.5yr  1.5yr   1yr           │
```

### 2.3 Strike Price – Applicable Coupon

The strike is not an assumption — it is fully contractually determined. Per the Option Agreement (Schedule 3), the **Purchase Price Per Share** equals the SPA price per share **plus the Applicable Coupon**, defined as interest capitalised annually from SPA Completion Date to (but excluding) the Option Completion Date.

The coupon schedule **steps up over time** and differs between the Call and Put:

| Year | Call Coupon | Put Coupon |
|---|---|---|
| 0 – 1 | 2.75% | 2.75% |
| 1 – 2 | 3.00% | 3.00% |
| 2 – 3 | 3.00% | 3.00% |
| 3 – 4 | 4.20% | 4.10% |
| 4 – 5 | 4.20% | 4.10% |
| 5 – 6 | n/a | 4.10% |

The call coupon is marginally higher than the put coupon in years 3–5 (4.20% vs 4.10%), reflecting a slight contractual advantage to CCHBC as the call holder. Implied strike values at key dates (based on USD 577.19 SPA price per share):

| Date | Call Strike | Put Strike |
|---|---|---|
| Year 3 | USD 629.18 | USD 629.18 |
| Year 4 | USD 655.61 | USD 654.98 |
| Year 5 | USD 683.14 | USD 681.83 |
| Year 6 | — | USD 709.79 |

### 2.4 Simplifying Assumptions

The following items are provided for in the agreement but excluded from this valuation for simplicity, consistent with a clean-value analysis:

- **No Gaia Leakage:** No deduction to the SPA base price
- **No dividends:** No reduction to the Purchase Price
- **No SPA Claim Adjustments:** No post-completion price adjustments
- Equity value at SPA Completion = USD 3.2bn (agreed deal consideration)

---

## 3. Valuation Methodology

### 3.1 Approach – Least-Squares Monte Carlo (LSM)

Both the Call and Put are **Bermudan options** — they are exercisable at any point within a defined window, not solely at expiry. A standard Black-Scholes (European) framework would materially misprice these instruments by ignoring the value of early exercise.

We employ the **Longstaff-Schwartz Least-Squares Monte Carlo ("LSM")** method, which is the market-standard technique for pricing Bermudan and American options. The approach:

1. Simulates a large number of equity value paths under the risk-neutral measure (Geometric Brownian Motion)
2. At each exercise date within the window, estimates the **continuation value** via cross-sectional regression of discounted future cash flows on current equity value (polynomial basis)
3. Exercises the option on a given path wherever **intrinsic value exceeds estimated continuation value**
4. Averages the resulting cash flows, discounted back to valuation date

This correctly captures the strategic optionality of both parties — CCHBC will optimally call early when equity values are high; TCCC will optimally put early when equity values are low.

### 3.2 Key Parameters

| Parameter | Value | Source |
|---|---|---|
| Equity value at SPA | USD 3.2bn | Agreed SPA consideration |
| SPA price per share | USD 577.19 | USD 3.2bn ÷ 5,544,080 total shares |
| **Asset volatility** | **20.0%** | Unlevered (historical) equity volatility of global KO bottler peers; average per Capital IQ as at 31 December 2025, rounded to nearest 25bps |
| **Risk-free rate** | **4.929%** | USD risk-free rate per Bloomberg as at valuation date |
| Simulations | 1,000,000 paths | See convergence analysis in §3.3 |
| Time steps | Monthly (12/yr) | — |
| Drift (risk-neutral) | = Risk-free rate | Standard risk-neutral pricing; no dividend yield |

**On asset volatility:** The σ parameter in the GBM represents forward expected asset volatility. We use **unlevered (asset) volatility** — not raw equity volatility — because the option is written on equity value. Unlevering strips out the amplifying effect of each peer's capital structure, leaving a comparable measure of underlying business risk. The peer set consists of publicly listed Coca-Cola bottlers with global operations. The resulting 20.0% asset volatility is considered appropriate given CCBA's operations, noting that a pure African-market vol assumption would likely be higher; the peer-based approach is a conservative and defensible proxy.

### 3.3 Simulation Count and Convergence

Monte Carlo methods produce estimates subject to simulation noise, with standard error scaling as σ/√N. The table below shows the 95% confidence interval on the **net total value to CCHBC** at increasing simulation counts, derived from the observed payoff variance at 1,000,000 paths:

| Simulations | ±95% CI on Net Total Value |
|---|---|
| 10,000 | ±USD 7.3M |
| 50,000 | ±USD 3.3M |
| 100,000 | ±USD 2.3M |
| 250,000 | ±USD 1.5M |
| 500,000 | ±USD 1.0M |
| **1,000,000** | **±USD 0.7M** |

At 1,000,000 simulations the confidence interval of **±USD 0.7M** is below any practical materiality threshold relative to a ~USD 44M net value, and represents a conventional stopping point from a statistical standpoint. Further increases in simulation count yield diminishing precision improvements that are not meaningful in the context of the broader valuation uncertainty (principally the asset volatility assumption).

### 3.4 Model Scope and Limitations

| Risk Factor | Captured? | Approach |
|---|---|---|
| FX risk (14 African markets) | No | USD-denominated payoff; operational FX embedded in equity volatility assumption |
| Regulatory/antitrust conditionality | **Acknowledged — not applied** | Theoretical only; see §4.3 and Project_Horizon_Regulatory_Risk.md |
| Non-marketability of the option | **Yes — applied** | DLOM per Longstaff (1995) per §4.3 |
| TCCC optimal exercise (cross-party) | No | Modelled independently; Dynkin game theory not captured |

---

## 4. Results

### 4.1 Base Case

*Asset volatility: 20.0% | Risk-free rate: 4.929% | SPA price: USD 577.19/share*

| | Per Share | Total (×1,386,020 shares) |
|---|---|---|
| **Call Option Value** (CCHBC asset) | USD 118.18 | **USD 163.8M** |
| **Put Option Value** (CCHBC liability) | USD 86.66 | **USD 120.1M** |
| **Net Value to CCHBC** | USD 31.52 | **USD 43.7M** |

The net position is positive for CCHBC, reflecting:
1. The call's earlier opening (Year 3 vs 3.5) — 0.5 years of exclusive optionality
2. The marginally higher call coupon in years 3–5 (4.20% vs 4.10%), which makes the call strike slightly more favourable relative to the put strike at any given exercise date in the overlap period
3. Higher risk-free rate benefits call holders (higher drift) more than it hurts put holders, since the call has a shorter maximum duration

### 4.2 Sensitivity Analysis — Volatility and Rate

Net value to CCHBC (USD millions) across asset volatility and risk-free rate scenarios. Base case marked *.

| Asset Vol | rf = 4.00% | rf = 4.929% | rf = 6.00% |
|---|---|---|---|
| 15% | +$14.9M | +$50.1M | +$89.4M |
| **20%** | +$13.6M | **+$48.1M*** | +$86.5M |
| 25% | +$7.6M | +$42.5M | +$82.5M |
| 30% | +$4.6M | +$40.9M | +$75.6M |
| 35% | +$2.5M | +$39.6M | +$70.8M |

**Key observations:**
- The **risk-free rate is the dominant driver** — a 1% move in rf shifts net value by ~$35–40M. This is because the put has a longer duration (to Year 6) and is therefore more sensitive to discounting; a higher rf benefits CCHBC as the short-put party.
- **Asset volatility has secondary impact** on the net — higher vol increases both call and put roughly proportionally; at the base rf of 4.929% the net is relatively stable across the vol range ($40–50M).
- The net is **positive across all scenarios at rf ≥ 4.929%**. It turns negative only at rf ~3.5% or below, which would require a material decline from current USD rates.

### 4.3 Extended Model: DLOM

#### Discount for Lack of Marketability (DLOM) — Longstaff (1995)

The option is a private bilateral instrument between TCCC and CCHBC. Unlike a listed option, it cannot be sold, transferred, or hedged in a secondary market. **Longstaff (1995)** shows that the upper bound on this illiquidity cost equals the value of a **floating-strike lookback put** — the right to sell at the highest price achieved over the restriction period T:

$$\text{DLOM}(\%) = \frac{E\left[e^{-rT}\left(\max_{0 \leq t \leq T} S_t - S_T\right)\right]}{S_0}$$

Computed via Monte Carlo over the existing 1M paths at three restriction periods:

| Restriction Period T | DLOM (%) |
|---|---|
| 3 years (earliest call exercise) | 18.7% |
| **4 years — central estimate** | **21.1%** |
| 5 years (latest call exercise) | 23.1% |

The central estimate of **21.1%** (T = 4 years, midpoint of call window) is applied below.

#### DLOM Results

| Model | Call ($/sh) | Put ($/sh) | Net ($/sh) | Net ($M) |
|---|---|---|---|---|
| **LSM — Marketable baseline** | 118.18 | 86.66 | 31.52 | **43.7** |
| **LSM — Non-Marketable (DLOM 21.1%, T=4yr)** | 93.23 | 68.37 | 24.86 | **34.5** |
| LSM — Non-Marketable (DLOM 18.7%, T=3yr) | 96.14 | 70.47 | 25.67 | 35.6 |
| LSM — Non-Marketable (DLOM 23.1%, T=5yr) | 90.87 | 66.59 | 24.28 | 33.7 |

The DLOM reduces net value by approximately **USD 9M (~21%)**, from USD 43.7M to **USD 34.5M** at the central estimate, with a range of USD 33.7M–35.6M across restriction period assumptions.

#### Note on Regulatory Risk

The Option Agreement contains a **12-month cap** on obtaining merger control approvals for the option exercise (Clause 3.2 / L62). If approvals are not obtained within 12 months, the exercise lapses. This creates a theoretical regulatory timing risk.

However, on analysis this risk is assessed as **not material enough to quantify or apply as a valuation adjustment**, for the following reasons:

1. **The COMESA conduct investigation targets passive sales restrictions** — a minor amendment to the franchise agreement (adding a passive sales carve-out) is the expected outcome, consistent with the Heineken and Diageo precedents. This does not impair CCBA's core territorial exclusivity or franchise economics.

2. **TCCC has fully aligned economic incentives post-close.** As an indirect 25% owner with a structured put option stepping up annually at 2.75–4.10%, TCCC has every incentive to settle the conduct case quickly and cleanly, and to cooperate on obtaining regulatory approvals for the option exercise.

3. **The 12-month cap covers a second-step merger filing** — once the conduct case is resolved (the most likely state at Year 3–5), this is a routine step-up merger notification. There is no basis to assume COMESA would treat it as contested.

The theoretical risk is acknowledged and documented in *Project_Horizon_Regulatory_Risk.md*. It is not applied as a deduction to the option fair value.

---

## 5. Conclusion

At a USD risk-free rate of 4.929% and asset volatility of 20.0%, the structured option instrument has a **gross fair value to CCHBC of approximately USD 44 million** on a marketable basis (USD 164M call asset less USD 120M put liability). The simulation standard error is ±USD 0.7M (95% CI at 1,000,000 paths), below any practical materiality threshold.

Applying the DLOM adjustment for non-marketability of the instrument (21.1%, Longstaff 1995, T = 4 years central estimate), the **primary net value estimate is approximately USD 34.5 million**, with a range of **USD 33.7M – 35.6M** across restriction period assumptions.

A theoretical regulatory timing risk exists — the Option Agreement contains a 12-month cap on obtaining merger control approvals for the option exercise, after which the exercise lapses. On analysis this risk is assessed as not material enough to quantify or apply as a valuation adjustment. The expected COMESA conduct case outcome is a minor franchise amendment (passive sales carve-out) that does not impair core franchise economics; TCCC's 25% ownership post-close creates fully aligned incentives to resolve the conduct case and cooperate on approvals; and the second-step merger filing is expected to be routine once the conduct case is settled. The theoretical risk is acknowledged and documented in *Project_Horizon_Regulatory_Risk.md*.

The valuation is robust to volatility assumptions at the base risk-free rate; the primary market risk to net value is a significant reduction in USD risk-free rates. All key economic terms — exercise windows, coupon schedule, share count — are sourced directly from the Option Agreement. The judgement inputs are the SPA equity value (agreed deal consideration), the USD risk-free rate (Bloomberg), the asset volatility (KO bottler peer analysis, Capital IQ), and the DLOM restriction period (midpoint of call window).

---

*This note has been prepared for internal discussion purposes. The model and assumptions are subject to review.*
