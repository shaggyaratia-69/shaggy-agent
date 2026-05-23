---
name: fuel-wfs-pricing
description: "Extract WFS/World Fuel rack prices by location, calculate pump-price suggestions, and optionally update customer fuel-pricing sheets."
version: 1.0.0
license: Customer-safe
metadata:
  shaggy:
    tags: [fuel, wfs, world-fuel, pricing, pump-prices]
---

# Fuel WFS / World Fuel Pricing

Use this skill for current wholesale fuel pricing, pump-price suggestions, and WFS/World Fuel portal extraction.

## Required customer configuration

The customer must provide or configure:
- WFS/MyWorld portal URL and login stored securely.
- Location list with site names, addresses, site IDs/customer numbers if known.
- Customer spreadsheet target, if Shaggy is allowed to update one.
- Product mapping for each site: 87/unleaded, 89/midgrade, 93/premium, diesel, or local equivalents.

Never embed real portal passwords in skill files or reports.

## Source-of-truth rules

- Official fuel vendor portal values are the source of truth.
- Use the delivered/customer-visible `TOTAL`/delivered price, not only base fuel, freight, or tax components.
- Select each location explicitly and wait for the page/API data to refresh before reading rows.
- Capture effective date/time and checked-at time.
- If portal UI is stale but authenticated API/GraphQL returns all product rows, API extraction is acceptable; record that method.

## Pump price calculation

Default margins are customer-configurable. If not configured, ask once and save the preference.

Common default template:
- Unleaded: wholesale + margin
- Midgrade: wholesale + margin
- Premium: wholesale + margin
- Diesel: wholesale + margin

If the user wants register-formatted prices, apply their ending rule, such as prices ending in `.99` or `.009` depending on register format. State the final pump price and the margin used.

## Workflow

1. Identify location(s) and products.
2. Log into the vendor portal using secure stored credentials or the user's active browser session.
3. Extract product rows and effective timestamps.
4. Validate each product row by label and location.
5. Compute pump suggestions if asked.
6. If asked to update a sheet, show write target and wait for confirmation unless the user already gave exact approval.
7. Verify any write by reading the row back.

## Output

For quick chat output:

```text
[Location]
World Fuel/WFS total:
- Unleaded: $____
- Midgrade: $____
- Premium: $____
- Diesel: $____
Effective: ____

Suggested pump, if requested:
- Unleaded: $____
- Midgrade: $____
- Premium: $____
- Diesel: $____
```
