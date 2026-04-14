# Project Horizon - Email Draft to Neel

**Subject:** Project Horizon valuation framing

Neel / Javier,

I think we should start framing the Project Horizon option as a linked, state-dependent purchase agreement rather than as a standalone option on a fixed 25% block.

The valuation problem has four defining features:

1. Olympus has a call right that can be exercised partially, subject to the contractual thresholds.
2. Titan has a put right that applies only to the shares Titan still holds at that time.
3. Olympus's earlier call exercise changes the size of Titan's later putable block.
4. During the overlap period, both sides may have an incentive to act, so the valuation is strategic rather than passive.

That means the value depends on:

- time;
- the underlying equity value;
- Titan's remaining stake; and
- the actions available to both parties under the agreement.

Once you frame the agreement that way, it cannot be reduced cleanly to two independent vanilla option legs on a fixed 25% block.

There are therefore two practical ways we can present the valuation:

1. **The correct approach:** value the agreement directly as a linked, state-dependent contractual structure, using a daily grid and tracking both the underlying equity value and Titan's remaining ownership position, while enforcing the contractual exercise limits. On that basis, the current pre-DLOM value is approximately **USD 144.1m**. This is the more defensible valuation approach, but it would likely imply a recurring bespoke valuation exercise alongside the annual impairment process if the derivative position needs to be remeasured.
2. **The rough approximation:** approximate the agreement as long a European call on the full 25% block and short a European put only on the 7% residual tail. That is much simpler to explain and implement, and gets us broadly into the same value range, with a current pre-DLOM value of approximately **USD 137m**. The important caveat is that we only know this is a close approximation because we ran the long-form valuation first. Without that benchmark, it would be harder to defend under audit that a long 25% call less a short 7% put is a reasonable shortcut for this agreement.

In other words, the simplified proxy saves most of the work and gets us close to the same economic answer, but it does not fully capture partial exercise over time, the dynamic resizing of Titan's putable block, or the strategic overlap period. It is therefore best viewed as a practical shortcut rather than the technically correct valuation.

Happy to talk it through if helpful.
