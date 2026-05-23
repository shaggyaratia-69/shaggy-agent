---
name: fuel-competitor-prices
description: "Check fuel competitor pump prices for each station, compare against WFS/vendor cost and margins, and recommend customer-facing pump price adjustments."
version: 1.0.0
license: Customer-safe
metadata:
  shaggy:
    tags: [fuel, competitors, gasbuddy, pump-prices, margins]
---

# Fuel Competitor Prices

Use this skill when the user asks for competitor pricing, GasBuddy-like checks, pump price positioning, or margin comparison.

## Rules

- Check the exact competitor station for the exact location; do not reuse another store's competitor prices.
- Record source, checked-at time, and whether price appears user-reported/stale.
- Compare competitor pump prices against the user's current pump price and WFS/vendor cost.
- Keep recommendations practical: match, beat, hold, or raise based on margin and market position.

## Workflow

1. Identify target station and competitor set.
2. Pull public competitor prices using browser/web tools or configured APIs.
3. Load current WFS/vendor cost for the same product/location.
4. Load current pump prices if available.
5. Compute margin and competitor gap.
6. Recommend a price move only if the data is fresh enough.

## Output

```text
[Location]
Competitor check: ____
Current pump: ____
WFS/vendor cost: ____
Estimated margin: ____
Recommendation: hold / match / beat by __ / raise to __
Reason: ____
```
