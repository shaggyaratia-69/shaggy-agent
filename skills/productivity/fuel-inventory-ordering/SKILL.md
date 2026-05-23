---
name: fuel-inventory-ordering
description: "Analyze tank readings, burn rate, delivery lead time, headroom, and market/rack price context to recommend fuel orders and prepare dispatch drafts."
version: 1.0.0
license: Customer-safe
metadata:
  shaggy:
    tags: [fuel, inventory, ordering, dispatch, tank-readings]
---

# Fuel Inventory and Ordering

Use this skill when the user asks whether a station needs fuel, how many gallons to order, or to prepare/send a dispatch order.

## Safety-first ordering rules

- Never invent tank readings.
- Never overfill a tank; account for expected sales before delivery and leave safe ullage.
- Use a conservative delivery lead time when estimating projected gallons.
- If a reading is stale/missing, label it and ask for the current reading before recommending an order.
- Treat each location independently.

## Required location profile

For each station, maintain or request:
- tank products and capacities,
- reorder trigger by product,
- absolute safety floor,
- ideal target after delivery,
- max operating target if different from physical capacity,
- typical delivery lead time,
- typical minimum/full load size,
- vendor/dispatch recipient,
- product names dispatch expects.

## Order decision workflow

1. Load latest tank readings and timestamp.
2. Load recent sales/gallon movement to compute burn rate.
3. Load current WFS/vendor prices.
4. Estimate projected gallons at delivery arrival:
   `projected_at_delivery = current_gallons - expected_burn_during_lead_time`
5. Compute headroom at delivery arrival:
   `headroom = operating_target_or_capacity - projected_at_delivery`
6. Decide status per product:
   - `ORDER NOW`: at/below trigger or projected below trigger before delivery.
   - `ORDER TODAY`: projected near trigger within lead time/planning window.
   - `WATCH`: likely within 48 hours.
   - `SAFE`: enough fuel beyond planning window.
7. Recommend gallons that satisfy safety and economics without overfill.
8. Add a market/rate note only after checking current oil/rack context.

## Dispatch email/order rule

Draft first unless the user's message provides exact final approval, exact gallons, products, and recipient/vendor.

Before sending, verify:
- location/site code,
- product names,
- gallons by product,
- recipient/vendor,
- requested delivery timing if any,
- sender account,
- signature.

After sending, verify sent mail/order confirmation and create a reply-check/reminder if available.

## Recommendation format

```text
Location: ____
Status: ____

Current tanks:
- Unleaded: ____ gal, trigger ____
- Premium/Diesel/etc.: ____ gal, trigger ____

Projected at delivery: ____
Recommended order: ____ gallons ____ + ____ gallons ____
Why: ____
Market/rate note: ____
Next action: approve draft / send order / no order needed
```
