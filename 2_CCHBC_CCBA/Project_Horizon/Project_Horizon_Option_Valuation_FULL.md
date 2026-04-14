# Project Horizon - Full Valuation of Option Agreement
**Prepared for:** [MD Name]
**Valuation date:** December 31, 2025
**Model source:** OPM_Structured_Option_Model_FULL.ipynb
**Subject:** Fair Value Assessment - Integrated Call / Put Option Agreement over Residual 25% Stake in CCBA

---

## Executive Summary

This memo reports the results of the current FULL Project Horizon option model. Unlike the original proxy memo, this report is based on the integrated contract model in `OPM_Structured_Option_Model_FULL.ipynb`, which treats the signed instrument as one linked, state-dependent agreement rather than as two independent full-block options.

The principal outputs of the current FULL build are:

- **Integrated clean value before DLOM:** **USD 139.6M**
- **Integrated fair value after central DLOM:** **USD 110.2M**
- **Per initial option share after DLOM:** **USD 79.50**
- **Monte Carlo precision at the fixed 1,000,000-path policy:** standard error **USD 0.22M**, equivalent to a **95% confidence interval of +/- USD 0.43M**

The current FULL model improves materially on the original proxy because it captures:

- the agreement as an **integrated contract** rather than separate call and put legs;
- **partial and multiple call exercise** as a state-based action set;
- the **put applying only to Titan's remaining shares** at the relevant exercise date;
- **One Live Notice** interaction in the overlap window through an explicit notice-priority approximation; and
- strike construction consistent with the agreement while applying an explicit zero-lag simplification in the primary valuation.

One source-control item remains open: the **USD 3.2bn SPA-derived reference equity value** and the derived **SPA price per share** still require the exact **SPA paragraph citation** before external circulation. The SPA itself is not present in the current workspace, so that citation cannot be completed from the materials currently available.

---

## 1. Background and Purpose

In connection with CCHBC's acquisition of a 75% interest in Coca-Cola Beverages Africa ("CCBA"), the Option Agreement governs the residual **25% equity stake** retained by Titan at SPA completion.

The relevant parties are:

| Party | Legal Entity | Role |
|---|---|---|
| CCHBC | Coca-Cola HBC Holdings B.V. ("Olympus BV") | Acquiror; holder of the Call Option |
| Titan | European Refreshments Unlimited Company, guaranteed by The Coca-Cola Company | Seller; holder of the Put Option |

This memo is intended to be the separate valuation report for the current FULL model. It does **not** replace or edit the original proxy memo in `Project_Horizon_Option_Valuation.md`, which remains preserved separately as the initial economic approximation.

---

## 2. Contract Characterisation

### 2.1 Legal and Economic Structure

The signed agreement is not best understood as two separate options on the same fixed 25% block. It is better understood as one bilateral, path-dependent contract in which:

- Olympus BV has a delayed-start **call right**;
- Titan has a delayed-start **put right**;
- prior call exercise can reduce the later put exposure by reducing Titan's remaining holding;
- the call can be exercised in **partial tranches** and in multiple exercises, subject to contractual constraints; and
- the overlap period is governed by **One Live Notice**, so the parties' rights are linked rather than independent.

### 2.2 Exercise Style

Legally, the rights are best described as **windowed-American** rights: exercisable within defined windows rather than only at expiry. Numerically, the current FULL notebook approximates these rights on a **monthly Bermudan grid**, which is a practical implementation choice rather than the legal characterisation itself.

### 2.3 How to Read the Reported Value

The reported value should be interpreted as follows:

| Economic component | Effect on Olympus BV | Included in reported value? | Separately reported as a standalone leg? |
|---|---|---|---|
| Call rights | Positive | Yes | No |
| Put obligation | Negative | Yes | No |
| Interaction between the two rights | Can raise or lower the net value | Yes | No |
| Reported fair value | Net value of the linked agreement | Yes | Yes |

It is directionally helpful to think of the contract as **long call / short put** from Olympus BV's perspective. However, the reported value in the FULL notebook is **not** a standalone call value less a standalone put value priced independently. It is the direct fair value of the **integrated agreement**, including the interaction between the two rights.

### 2.4 Key Commercial Terms Reflected in the FULL Model

| Term | Current FULL treatment | Primary citation |
|---|---|---|
| Initial option stake | 25% of total equity, 1,386,020 shares | Option Agreement Schedule 3 definition of `Option Shares`; Clause 13.2.2 |
| Call window | Year 3.0 to Year 5.0 | Clause 4.1; Schedule 3 definition of `Call Option Period` |
| Put window | Year 3.5 to Year 6.0 | Schedule 3 definition of `Put Option Period` |
| Overlap | Year 3.5 to Year 5.0 | Schedule 3 definition of `Overlap Period`; Clause 8.1 |
| Call flexibility | Partial / multiple exercise enabled in base case | Clause 2.2 |
| Put scope | All remaining Titan shares only | Clause 5.2; Schedule 3 definition of `Exercise Shares` |
| Strike basis | SPA price + Applicable Coupon accrued to option completion | Clause 9.1; Schedule 3 definition of `Applicable Coupon` |
| Completion lag in primary valuation | Set to zero as explicit simplifying assumption | Schedule 3 definition of `Option Completion Date`; modeling assumption |
| Regulatory lapse risk | Qualitative only; not deducted | Modeling scope decision |
| Leakage / dividends / SPA claims | Excluded from primary clean value | Clause 11.2 and Clause 11.3 inform the exclusions |

---

## 3. Valuation Methodology

### 3.1 Model Architecture

The current FULL notebook values the agreement as an **integrated state-based contract** from Olympus BV's perspective.

The model tracks:

- current time;
- current equity value per share;
- Titan's remaining shareholding under the option agreement; and
- the admissible action set at each step.

The state space for Titan's remaining holding in the current build is:

- 25%
- 20%
- 15%
- 10%
- 0%

This grid is a discrete state approximation, not an averaging device. The contract starts today in the **25% state**, so that is the current initial condition from which the base-case value is calculated. The 20%, 15%, and 10% states are conditional reduced states the model could move into if prior call exercises had already reduced Titan's holding. The 0% state means the contract has been exhausted because Titan no longer holds any shares under the agreement.

At each eligible decision date, the model compares:

- continuation value;
- Olympus BV's admissible call actions; and
- Titan's right to put all remaining shares.

Continuation values are estimated by least-squares regression in the Longstaff-Schwartz style, but applied to the **integrated contract state**, not to separate call and put legs.

Accordingly, the model does **not** assume that the entire 25% block must transact together in the base case. From the 25% state, Olympus BV may wait or call to 20%, 15%, 10%, or 0%, subject to the contractual tranche and residual-floor rules. The current build is therefore a discrete state-grid approximation of the linked contract, not a standalone call-minus-put model and not a full game-theoretic stopping model.

From a financial valuation perspective, exercising a call on a tranche does **not** mean Olympus BV loses the upside on that tranche. It means Olympus BV converts option value on that tranche into owned equity. In the model, the immediate exercise value of the called tranche is the current share value less the contractual strike on that tranche. After that, continuation is valued only on the **remaining contract state**, because continuing to model option upside on shares already acquired would double count value. What is given up by exercising is therefore not the economic upside of the acquired shares; what is given up is the **optionality to wait** on that same tranche.

### 3.2 Call and Put Logic

The current FULL build uses the following action logic:

- **Call:** Olympus BV may do nothing, call an allowed tranche, or call to zero.
- **Put:** Titan may do nothing or put all shares still held at that time.
- **Overlap period:** where both rights would be exercised in the same modeled bucket, the current base case applies a **50/50 notice-priority split** as a practical approximation to One Live Notice.

This is a material improvement on the original proxy model, although it is still not a full game-theoretic stopping solution.

### 3.2A How Exercise Is Applied Inside the Valuation

The remaining-state logic is applied **inside** the backward-induction Monte Carlo, not after the simulation as a separate adjustment.

For each monthly decision date, for each simulated path, and for each current remaining-state, the model compares:

- the value of **waiting**;
- the value of each **admissible call action** from that state; and
- if the put window is open, Titan's right to **put all shares remaining in that current state**.

The base-case action menu is therefore:

| Current Titan state | Admissible call actions in the base case | Put action once live |
|---|---|---|
| 25% | Call 5% -> 20%; Call 10% -> 15%; Call 15% -> 10%; Call 25% -> 0% | Put all remaining 25% |
| 20% | Call 5% -> 15%; Call 10% -> 10%; Call 20% -> 0% | Put all remaining 20% |
| 15% | Call 5% -> 10%; Call 15% -> 0% | Put all remaining 15% |
| 10% | Call 10% -> 0% | Put all remaining 10% |
| 0% | Contract exhausted | Not applicable |

This means, for example, that if on a particular path and month the model chooses the 25% -> 20% call action, the immediate payoff is calculated only on the **5% actually called**, and the remaining **20%** continues to be valued from the 20% state. If later the contract is in the 20% state when the put becomes relevant, Titan's put is tested on **20%**, not on the original 25%.

The current build does **not** solve for an arbitrary optimal fractional exercise such as 7.518%. The admissible call sizes are restricted to the discrete state grid used in the model. That discretisation is not random: it is anchored to the contractual **5% minimum call tranche** and the **7% residual floor unless the position goes to zero**. The model therefore approximates the action set with the tractable states 25%, 20%, 15%, 10%, and 0%.

That point is important for interpretation. The model is saying that partial exercise is a permitted and economically sensible flexibility because it can reduce future put exposure while preserving optionality on the residual shares. It is **not** saying that 5% is uniquely optimal in continuous finance terms. It is the smallest permitted tranche in the current numerical approximation.

### 3.3 Strike Construction and Completion-Lag Assumption

The agreement defines the purchase price by reference to the SPA price plus the Applicable Coupon accrued through the **Option Completion Date**.

The contract itself contemplates an Option Completion Date falling on the **20th Business Day** after notice, absent any required approval extensions. The current primary valuation does **not** carry that 20-business-day lag into the reported fair value. Instead, it sets **completion lag to zero** as an explicit simplifying assumption, so that notice date and completion date are aligned for valuation purposes.

This assumption is about the mechanics of **option notice versus option completion** under the Option Agreement. It is **not** an assumption that the original SPA closing, transaction completion, or any post-signing process remained unfinished after the valuation date.

### 3.4 DLOM

DLOM is retained using a **Longstaff lookback-put** approach. The central reported DLOM is based on a **4-year restriction horizon**, with 3-year and 5-year outputs shown as reference bounds.

### 3.5 Simulation Policy

All reported results in this memo, including the main valuation and the sensitivity sections, use a fixed **1,000,000 simulation** policy.

---

## 4. Input Provenance and Assumption Register

For external-facing use, every contract-derived input should carry an exact clause or schedule reference, every external market input should carry provider and date, and every SPA-derived input should carry the exact SPA paragraph number.

The current source register is as follows:

| Input | Value | Nature | Source / citation | Status |
|---|---|---|---|---|
| Total equity reference value at SPA (`TOTAL_EQUITY_USD`) | USD 3.2bn | SPA-derived | Exact SPA paragraph citation required; SPA file not present in current workspace | **Pending** |
| Derived SPA price per share (`SPA_price`) | USD 577.19 | Derived from SPA input and share count | Derives from the SPA reference equity value and the Option Shares definition; exact SPA paragraph still required for the base value | **Pending** |
| Initial Titan stake (`INITIAL_TITAN_PCT`) | 25% | Contract-derived | Option Agreement Schedule 3 definition of `Option Shares`; Clause 13.2.2 | Complete |
| Option share count (`OPTION_SHARES`) | 1,386,020 shares | Contract-derived | Option Agreement Schedule 3 definition of `Option Shares`; Clause 13.2.2 | Complete |
| Call coupon schedule (`CALL_COUPONS`) | 2.75%, 3.00%, 3.00%, 4.20%, 4.20% | Contract-derived | Option Agreement Schedule 3 definition of `Applicable Coupon` | Complete |
| Put coupon schedule (`PUT_COUPONS`) | 2.75%, 3.00%, 3.00%, 4.10%, 4.10%, 4.10% | Contract-derived | Option Agreement Schedule 3 definition of `Applicable Coupon` | Complete |
| Call exercise window | Year 3.0 to Year 5.0 | Contract-derived | Clause 4.1; Schedule 3 definition of `Call Option Period` | Complete |
| Put exercise window | Year 3.5 to Year 6.0 | Contract-derived | Schedule 3 definition of `Put Option Period` | Complete |
| Overlap period | Year 3.5 to Year 5.0 | Contract-derived | Schedule 3 definition of `Overlap Period`; Clause 8.1 | Complete |
| Minimum call tranche / residual floor | 5% / 7% | Contract-derived | Clause 2.2 | Complete |
| Completion lag assumption (`COMPLETION_LAG_YEARS`) | 0.0 years | Modeling assumption | Schedule 3 definition of `Option Completion Date` informs the contract mechanics; zero lag is an explicit valuation simplification | Complete as assumption |
| Overlap priority (`OLYMPUS_PRIORITY_IN_OVERLAP`) | 50% | Modeling assumption | Clause 8.1 establishes earlier notice priority; 50/50 is the model's neutral same-bucket approximation | Complete as assumption |
| Asset volatility (`asset_volatility`) | 20.0% | External market data / judgment | Selected KO bottler peer asset-volatility analysis, Capital IQ, as of 31-Dec-2025 | Complete |
| Risk-free rate (`risk_free_rate`) | 4.929% | External market data | Bloomberg USD risk-free input, as of 31-Dec-2025 | Complete |
| Simulation count | 1,000,000 | Model policy | User-directed reporting convention | Complete |

Because the SPA is not present in the workspace, the exact SPA paragraph citation for the USD 3.2bn reference value cannot be inserted from the currently available documents. That item should be completed before the memo is circulated externally.

---

## 5. Results - Base Case

### 5.1 Primary Results

| Measure | Result |
|---|---|
| Integrated contract value before DLOM | **USD 139.6M** |
| Integrated contract value per initial option share | **USD 100.74** |
| Central DLOM | **21.08%** |
| Integrated fair value after DLOM | **USD 110.2M** |
| Fair value per initial option share after DLOM | **USD 79.50** |

### 5.2 Monte Carlo Precision

| Metric | Result |
|---|---|
| Fixed simulation count | 1,000,000 |
| Standard error at base run | USD 0.22M |
| 95% confidence interval | +/- USD 0.43M |

This level of simulation noise is small relative to the size of the instrument and is appropriate for valuation-reporting purposes.

### 5.3 Remaining-State Values

The current FULL model also reports the contract value conditional on Titan's remaining stake having already been reduced by prior call exercises:

| Titan remaining stake | Contract value | Per remaining share |
|---|---|---|
| 25% | USD 139.6M | USD 100.74 |
| 20% | USD 111.7M | USD 100.74 |
| 15% | USD 83.8M | USD 100.74 |
| 10% | USD 55.8M | USD 100.74 |
| 0% | USD 0.0M | Contract exhausted |

This table should be read as a **diagnostic of conditional states**, not as a probability-weighted average across future states.

- The **25%** row matches the base-case value because the contract currently starts in the 25% state.
- The **20%, 15%, and 10%** rows are hypothetical reduced states that would only arise if earlier call exercises had already reduced Titan's holding.
- The **0%** row means the contract has been exhausted.
- The fact that the per-remaining-share values are almost identical is an output of the current implementation and indicates near-linearity across these states; it is **not** an assumption that all states are economically identical or that the full 25% must transact together.

---

## 6. DLOM Results

The DLOM outputs from the current FULL notebook are:

| Restriction horizon | Lookback value | DLOM |
|---|---|---|
| 3.0 years | 107.947 | 18.70% |
| **4.0 years - central** | **121.699** | **21.08%** |
| 5.0 years | 132.735 | 23.00% |

Applying the central DLOM reduces the integrated value from **USD 139.6M** to **USD 110.2M**.

---

## 7. Sensitivity Analysis

All reported sensitivities below use the same fixed **1,000,000-path** policy as the main valuation.

### 7.1 Market Sensitivities

Integrated fair value to Olympus BV before DLOM (USD millions):

| Asset vol | rf = 4.00% | rf = 4.93% | rf = 6.00% |
|---|---|---|---|
| 15% | 100.2 | 112.0 | 126.0 |
| 20% | 128.5 | **139.6** | 152.1 |
| 25% | 157.4 | 167.1 | 179.5 |
| 30% | 185.2 | 194.7 | 206.2 |

Observations:

- Under the current FULL build, both higher volatility and higher risk-free rates increase value to Olympus BV.
- The model remains especially sensitive to the risk-free rate because the strike is contractual and accrues over time.

### 7.2 Contract-Specific Structural Sensitivities

Structural sensitivity before DLOM (USD millions):

| Case | Value |
|---|---|
| Base case: partial calls, 50/50 overlap | 139.6 |
| Full-block only, 50/50 overlap | 139.1 |
| Partial calls, Olympus 25% overlap priority | 139.1 |
| Partial calls, Olympus 75% overlap priority | 137.5 |

These results imply that, in the current quantitative implementation, the model is:

- only modestly sensitive to the partial-call toggle under the present assumptions; and
- only modestly sensitive to the overlap-priority parameter.

In practical terms, that means partial-call flexibility is included for contract faithfulness, but it is **not** the main driver of the current uplift versus the old proxy. The base case of **USD 139.6M** versus the full-block-only case of **USD 139.1M** indicates that the large difference against the old proxy is driven mainly by correcting the proxy's overstated full-block put liability, not by a large embedded value from finely tuned partial-call optimisation.

That does **not** mean those linked mechanics are irrelevant as a matter of contract. It means that, given the current stylised equity dynamics and payoff construction, those mechanics are not yet generating very large nonlinear value effects.

---

## 8. Reporting Scope and Limitations

The present memo reports the current FULL notebook as it stands today. The principal scope limitations are:

- **Overlap mechanics are approximated:** One Live Notice is represented through a same-bucket notice-priority approximation rather than a full stopping-game solution.
- **Zero completion lag is an explicit simplifying assumption:** the reported value assumes notice date and completion date coincide for valuation purposes.
- **Regulatory lapse risk is not quantified:** this is deliberate and appropriate for the current evidence base, but it means the fair value is a primary clean estimate rather than a regulatory-risk-adjusted value.
- **Leakage, dividends, and SPA claims are excluded:** the output remains a clean-value estimate subject to those exclusions.
- **One source citation is still open:** the SPA-derived USD 3.2bn input and derived SPA price per share still require the exact SPA paragraph reference before external issue.

These limitations do not invalidate the current FULL model. They define what the current build does and does not do.

---

## 9. Conclusion

The current FULL Project Horizon option model produces a **clean integrated contract value of USD 139.6M** and a **primary fair value of USD 110.2M after central DLOM**.

This is the appropriate separate valuation memo for the current FULL notebook build. It is distinct from the original proxy memo and should be read as the report corresponding to the integrated contract model now implemented in `OPM_Structured_Option_Model_FULL.ipynb`.

In summary:

- the original memo remains the preserved proxy write-up;
- this memo reports the current FULL integrated valuation build;
- all reported scenarios use **1,000,000 simulations**; and
- the remaining open control item before external issue is the exact **SPA paragraph citation** for the SPA-derived base equity reference.
