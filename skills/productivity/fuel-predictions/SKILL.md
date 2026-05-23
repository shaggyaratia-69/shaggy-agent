---
name: fuel-predictions
description: "Create fuel price and inventory predictions using tank trends, WFS/rack prices, competitor prices, crude/oil market direction, and local sales history."
version: 1.0.0
license: Customer-safe
metadata:
  shaggy:
    tags: [fuel, prediction, oil, crude, market, inventory]
---

# Fuel Predictions

Use this skill for daily/weekly fuel prediction reports: whether prices may rise/fall, whether to bridge or fill, and when each station may need fuel.

## Prediction discipline

- Predictions are probabilities, not guarantees.
- Tank safety comes before price speculation.
- Use current data: vendor prices, latest tank readings, recent burn rate, competitor prices, crude/oil headlines, and delivery lead time.
- Label stale/missing sources.
- Compare yesterday's prediction against today's actual outcome when available and improve the method.

## Inputs

- Latest WFS/vendor wholesale prices by product/location.
- Historical WFS/vendor prices.
- Latest tank readings and burn rates.
- Delivery lead times and order constraints.
- Competitor prices.
- Current crude/oil/refinery/geopolitical headlines.
- Optional local sales history.

## Workflow

1. Build a source snapshot with timestamps.
2. Calculate daily burn and time-to-trigger.
3. Compare current WFS/vendor prices against recent trend.
4. Check current oil/crude/news direction using current web/news tools.
5. Decide whether market risk favors:
   - normal order,
   - smaller bridge order until a likely price drop window,
   - earlier/larger order before likely increase,
   - no change because operational safety dominates.
6. Produce a concise recommendation and, for larger jobs, a PDF/report with source evidence.

## Output

```text
Fuel prediction for [location/date]
Bottom line: ____
Tank safety: ____
Price direction: bullish/bearish/mixed because ____
Recommended action: ____
Confidence: low/medium/high
Missing/stale data: ____
```
