# Weekly Shaggy Product Sync Draft — Not Enabled

## Status

DO NOT ENABLE until Rahim approves after a complete manual verified run.

This is a draft operating prompt for a future weekly Hermes upstream → Shaggy rebrand sync. It is intentionally documentation only. No cron job has been created from this file.

## Future schedule idea

- Cadence: weekly
- Delivery: origin chat or local report, depending on Rahim's approval
- Behavior: prepare a branch/PR and report, not auto-merge

## Draft prompt for future cron job

```text
You are running the weekly Shaggy the Agent product sync check.

Repo path:
/Users/shaagy/.shaggy/shaggy-agent

Goal:
Check the upstream engine for new updates, stage new changes outside the Shaggy repo, apply the Shaggy rebrand transform, run tests/scans, and prepare a Shaggy-branded branch/PR only if clean.

Rules:
1. Do not commit raw upstream files directly.
2. Do not copy private local configs, .env files, auth files, memory, credentials, customer data, or local runtime state.
3. Preserve Shaggy product identity, desktop branding, install behavior, update behavior, and portable `SHAGGY_PRODUCT_DIR` support.
4. Customer-facing copy must use Shaggy the Agent / Shaggy Agent and the `shaggy` command.
5. Keep technical provider slugs only if they are internal and non-customer-facing.
6. Run product sync tests, public branding guard, update tests, desktop tests if touched, secret scan, generated-artifact scan, and `git diff --check`.
7. If clean, push a branch/PR and report the URL.
8. Do not auto-merge or auto-release without Rahim's explicit approval.

Final report must include:
- upstream head checked
- branch created or reason no branch was needed
- files transformed summary
- tests/scans run and results
- PR URL if pushed
- any blockers or release approval needed
```

## Future creation note

If Rahim approves scheduling later, create the cron only after loading the Shaggy product skill and using a self-contained prompt. Do not schedule from this draft automatically.
