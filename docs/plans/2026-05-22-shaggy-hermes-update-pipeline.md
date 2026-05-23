# Shaggy Agent Update Pipeline Implementation Plan

> **For Shaggy maintainers:** use this plan whenever upstream runtime changes must be ported into Shaggy Agent.

**Goal:** Maintain a repeatable local-first pipeline that pulls useful upstream Shaggy Agent improvements into Shaggy Agent, preserves Shaggy branding and customer protections, rebuilds the install package, and verifies a clean update path.

**Architecture:** Treat the private upstream runtime checkout as implementation input and `[LOCAL_USER_HOME]/Projects/shaggy-agent` as the product source. Copy or cherry-pick changes deliberately, reapply Shaggy branding/product guards, then rebuild from Shaggy source into the customer ZIP. Dashboard/Kanban changes are accepted only when the Shaggy dashboard remains writable and customer-facing.

**Tech Stack:** Python 3.11+, setuptools wheel build, pytest, Shaggy dashboard React bundle/plugin assets, shell/PowerShell installers, local browser QA.

---

## Safety gates

1. Do not deploy to Cloudflare or update any live public website unless Rahim explicitly says **deploy live** or **publish**.
2. Always create a timestamped backup of `[LOCAL_USER_HOME]/Projects/shaggy-agent` before changing source.
3. Never copy live runtime secrets, `.env`, auth files, memory, tokens, credentials, private local paths, or business data into Shaggy packages.
4. Public/customer files must not expose old upstream branding, private implementation paths, tokens, or installer passwords.
5. Keep implementation/provider internals only where technically required; do not expose them publicly.

## Source update steps

1. Inspect upstream runtime status:
   ```bash
   git -C [LOCAL_USER_HOME]/private-upstream-runtime status --short
   git -C [LOCAL_USER_HOME]/private-upstream-runtime log -1 --oneline
   ```
2. Inspect Shaggy status:
   ```bash
   git -C [LOCAL_USER_HOME]/Projects/shaggy-agent status --short
   git -C [LOCAL_USER_HOME]/Projects/shaggy-agent log -1 --oneline
   ```
3. Backup Shaggy before edits:
   ```bash
   BACKUP=[LOCAL_USER_HOME]/ShaggyAgent_Backups/shaggy-agent_before_update_$(date +%Y%m%d_%H%M%S)
   rsync -a --exclude '.venv' --exclude 'venv' --exclude 'node_modules' --exclude 'build' --exclude '.pytest_cache' \
     [LOCAL_USER_HOME]/Projects/shaggy-agent/ "$BACKUP/"
   echo "$BACKUP"
   ```
4. Compare target files with upstream. Prefer small patches over blind overwrite. If upstream contains visible old-brand copy, convert to Shaggy copy before committing.

## Dashboard / Kanban acceptance

Shaggy dashboard/Kanban must remain a Shaggy-branded writable board:

- The visible dashboard should say Shaggy/Shaggy Agent where product identity is shown.
- The Kanban route must be `/kanban`.
- It must support adding tasks, moving/updating statuses, completing/archiving, and deleting tasks.
- It must use Shaggy runtime paths/imports such as `shaggy_cli.kanban_db` and Shaggy dashboard session token names.
- Browser QA must verify no console errors and no visible old public branding.

Current Shaggy source has a richer plugin Kanban surface than the simple upstream localStorage page. Keep the plugin route unless an upstream change is strictly better, then port the behavior into the plugin while preserving the writable API.

## Required regression tests

Run these focused tests after every update:

```bash
cd [LOCAL_USER_HOME]/Projects/shaggy-agent
[LOCAL_USER_HOME]/.local/bin/uv run --with pytest --with pytest-xdist --with pytest-timeout --python [LOCAL_USER_HOME]/.local/bin/python3.11 \
  pytest tests/test_shaggy_update_pipeline_contract.py tests/plugins/test_kanban_dashboard_plugin.py tests/test_project_metadata.py -q -o 'addopts='
```

The contract test asserts:

- CLI aliases include `shaggy`, `shaggy-agent`, `shaggy_agent`, `shaggy-core`, `shaggy_core`, `shaggy-acp`, `shaggy_acp`.
- Dashboard Kanban plugin is writable (`POST`, `PATCH`, `DELETE`) and can complete/archive/move tasks.
- Dashboard public shell/manifest avoids old public branding.
- This update plan exists and keeps live deployment blocked by default.

## Build and package

1. Compile check touched Python files:
   ```bash
   cd [LOCAL_USER_HOME]/Projects/shaggy-agent
   [LOCAL_USER_HOME]/.local/bin/python3.11 -m py_compile \
     cli.py shaggy_cli/main.py shaggy_cli/doctor.py shaggy_cli/kanban.py shaggy_cli/kanban_db.py \
     plugins/kanban/dashboard/plugin_api.py shaggy_constants.py shaggy_state.py
   ```
2. Build the Shaggy wheel from source:
   ```bash
   cd [LOCAL_USER_HOME]/Projects/shaggy-agent
   rm -rf build dist
   [LOCAL_USER_HOME]/.local/bin/uv run --with build --python [LOCAL_USER_HOME]/.local/bin/python3.11 python -m build --wheel
   ```
3. Verify the wheel contains the dashboard plugin assets and no forbidden public terms in customer-facing bundle files.
4. Replace the wheel inside the customer product ZIP, update `SHA256SUMS.txt`, and write a sidecar `.sha256`.
5. Test installer syntax and ZIP integrity:
   ```bash
   bash -n /path/to/install-shaggy-agent-macos.sh
   bash -n /path/to/install-shaggy-agent-linux-wsl.sh
   unzip -t /path/to/Shaggy-Agent-Product-All-Systems.zip
   shasum -a 256 /path/to/Shaggy-Agent-Product-All-Systems.zip
   ```

## Local install/update verification

Use a clean temporary install/home when possible:

```bash
TMP_HOME=$(mktemp -d /tmp/shaggy_update_home.XXXXXX)
TMP_VENV=$(mktemp -d /tmp/shaggy_update_venv.XXXXXX)
[LOCAL_USER_HOME]/.local/bin/python3.11 -m venv "$TMP_VENV"
"$TMP_VENV/bin/pip" install [LOCAL_USER_HOME]/Projects/shaggy-agent/dist/shaggy_agent-*.whl
SHAGGY_HOME="$TMP_HOME" "$TMP_VENV/bin/shaggy" --version
SHAGGY_HOME="$TMP_HOME" "$TMP_VENV/bin/shaggy" doctor --no-fix || true
```

For dashboard/Kanban browser QA, start Shaggy dashboard on a non-conflicting port if Hermes or Sadi is already using 9119. Recommended local verification port for this pipeline: `9121`.

```bash
SHAGGY_HOME="$TMP_HOME" "$TMP_VENV/bin/shaggy" dashboard --host 127.0.0.1 --port 9121
```

Open the printed tokenized dashboard URL. Verify `/kanban` loads, add a test task, move it to another lane, complete/delete it, check browser console, then stop the server.

## Final report format

Report only verified facts:

- Source repo path
- Backup path
- Upstream Hermes commit inspected
- Shaggy commit/status inspected
- Files changed
- Built wheel path
- Product ZIP path
- SHA256
- Local install/update command
- Dashboard/Kanban browser QA result
- Scan result for forbidden public branding/secrets
- Remaining risks or manual approval needed

Do not claim live deployment or live package verification unless Cloudflare deploy and live download checks were actually performed after explicit approval.
