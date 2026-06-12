# Shaggy the Agent Product Sync Pipeline

## Purpose

Shaggy the Agent is Rahim's customer-facing product fork built from the upstream engine. The product goal is simple: customers should get the same agent capability, desktop direction, CLI behavior, tools, gateway behavior, and update path, but the public product identity must be Shaggy the Agent / Shaggy Agent.

This is not a raw upstream mirror. The approved flow is:

1. Fetch upstream updates into a separate staging area.
2. Transform/rebrand files before they enter the Shaggy product branch.
3. Verify product behavior and public branding.
4. Push a Shaggy-branded branch/PR to Rahim's repo.
5. Package/deploy only after verification and release approval.

## Current verified repo facts

- Verified at: 2026-06-11 18:46:02 CDT
- Active repo path: `/Users/shaagy/.shaggy/shaggy-agent`
- Active branch for this work: `product-sync-hermes-to-shaggy-rebrand-pipeline`
- Main/origin baseline: `71931a781`
- Upstream remote name: `upstream-hermes`
- Upstream head observed during setup: `9102d4a588c8`
- Origin repo: `shaggyaratia-69/shaggy-agent`

## Product identity rules

Customer-facing output must use:

- Product name: `Shaggy the Agent`
- Short name: `Shaggy Agent`
- CLI command: `shaggy`
- Repo/package identity: `shaggy-agent`
- Customer install/update source: Shaggy repo/package channel, ideally behind a branded Cherries/Shaggy domain

Customer-facing output must not show raw upstream product/company identity except where legally required by license attribution.

## Sync architecture

### Stage 1 — upstream fetch

- Fetch upstream into the local `upstream-hermes` remote.
- Do not commit fetched files directly.
- Create a product branch from clean `main`.

### Stage 2 — safe staging outside repo

The helper `tools/shaggy_product_sync.py` builds staging paths outside the repo checkout:

- `upstream-hermes/` for raw upstream files
- `rebranded-shaggy/` for transformed files
- `reports/` for local verification reports

Raw upstream files should stay outside the product repo until transformed and scanned.

### Stage 3 — deterministic Shaggy transform

The transform layer converts customer-facing command, package, home-folder, docs, and company/product identity to Shaggy terms.

Important classification rule:

- Public/customer-facing upstream identity is a blocker.
- Technical provider slugs may remain only when classified as internal and non-customer-facing.

### Stage 4 — verification gates

Minimum gates before pushing a product-sync branch:

- Product sync pipeline tests
- Public branding guard
- Shaggy update pipeline contract
- Gateway update command tests
- Portable product update tests
- Desktop app tests/build if desktop files changed
- Secret scan
- Generated artifact scan
- `git diff --check`

### Stage 5 — publish branch/PR

The branch should be pushed only after tests/scans pass. Do not auto-merge to main unless Rahim explicitly approves that release policy.

## Customer install/update contract

Normal customer path:

```bash
curl -fsSL https://get.cherriesandco.com/shaggy | bash
```

After install:

```bash
shaggy setup
shaggy doctor
shaggy
```

Update path:

```bash
shaggy update
```

Rules:

- Customers should not need to use a raw GitHub link.
- Updates must come from the Shaggy repo/package channel.
- Portable installs must preserve `SHAGGY_PRODUCT_DIR` support.
- The update path must not require the customer install to be a git checkout.

## Weekly sync policy

Weekly sync should be created only after the first manual pipeline run is verified and Rahim approves scheduling. The weekly job should prepare a branch/PR and report results. It should not silently merge/release production updates unless Rahim approves that policy separately.
