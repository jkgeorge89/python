# Assumptions Limitations And Next Steps

## Why this note exists

The current QVI implementation is materially better than the earlier simplified methods, but it is still a model.

That means it contains assumptions, approximations, and implementation choices that should be visible in any serious methodology pack.

## 1. Ownership is finely discretized, not literally continuous

The solver uses 0.25% ownership steps.

That is much more refined than the earlier coarse grid and is adequate for a practical reference model.

But it is still a grid approximation.

So the model is continuous-state in spirit relative to the earlier coarse frameworks, not literally continuous in the mathematical sense of every infinitesimal ownership level being represented.

## 2. Completion lag is currently set to zero

The current implementation assumes zero lag between decision and completion.

That simplifies the strike treatment and makes the completion-time strike equal to the present-value strike in the export.

If the legal reading of the contract requires a non-zero completion lag, the model should be rerun with an explicit notice-to-completion period.

## 3. Strike accrual uses a 252-step business-day year

The model converts annual coupon schedules into daily rolls using a 252-step basis.

This is a coherent implementation choice, but it is still a choice.

If the legal or accounting basis requires actual calendar-day accrual or another day-count convention, the strike engine should be aligned to that convention.

## 4. Market dynamics are one-factor and time-homogeneous

The current reference model uses:

- a single price factor;
- constant volatility; and
- a constant risk-free rate.

That is standard and tractable, but it omits richer effects such as stochastic volatility, jumps, regime shifts, or state-dependent financing assumptions.

## 5. Overlap treatment is approximate

The overlap is handled through a practical stage-game approximation with a 50% Olympus tie-priority assumption.

This is not necessarily the only defensible overlap rule.

It is simply the one embedded in the current implementation.

Any final external-facing white paper should make this explicit and, ideally, show sensitivity to alternative tie-priority assumptions.

## 6. Only selected ownership surfaces are currently exported

The solver internally values all ownership sheets on the full grid.

But the current folder exports only the 25% full surfaces in Excel form.

That is adequate for understanding the starting state, but a fuller governance pack would also export additional ownership sheets such as 20%, 15%, 10%, and 7% for visual review.

## 7. Representative path labels are explainability labels only

The `low`, `base`, and `high` labels are not separate solved scenarios.

They are deterministic reporting paths.

This is not a limitation of the model itself, but it is a limitation of what those files can prove.

They help explain the policy. They do not substitute for the full state surfaces.

## 8. Boundary artifacts can appear on a discrete grid

The current 25% action surface shows isolated one-row action switches and a narrow non-monotone upper-tail effect one day before expiry.

These are normal discrete-grid artifacts near indifference boundaries and at the horizon.

They should be disclosed but not over-interpreted.

## 9. Current validation evidence is necessary but not exhaustive

The model has already been strengthened through:

- grid refinement;
- convergence output;
- explainability exports; and
- strike schedule export.

But a full validation pack would still benefit from:

- sensitivity tables;
- alternative overlap assumptions;
- alternative day-count assumptions; and
- documented legal-to-model mapping for each contractual rule.

## Recommended next steps for a formal white paper

### Technical next steps

- export additional ownership-state surfaces beyond 25%;
- produce a compact table of action boundaries by sheet and by date;
- run sensitivity cases for volatility, rates, and tie-priority; and
- test any alternative completion-lag assumptions.

### Documentation next steps

- map each contractual clause directly to the implemented rule;
- document the day-count choice explicitly;
- separate assumptions that are legal interpretations from those that are purely numerical approximations; and
- include a short FAQ that answers common misunderstandings about slices, rows, columns, and representative paths.

### Governance next steps

- preserve the current convergence outputs as the baseline reference;
- record any future calibration changes alongside methodology changes; and
- maintain versioned explainability exports so reviewers can trace changes in policy geometry across iterations.

## Bottom line

The current model is already a serious and defensible reference framework for this contract.

Its main remaining gaps are not that the structure is wrong. The main gaps are disclosure, calibration transparency, and sensitivity coverage.

Those are exactly the areas a final white paper should tighten.