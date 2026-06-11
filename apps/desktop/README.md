# Shaggy The Agent Desktop

Native Electron shell for the Shaggy Agent local dashboard/chat workspace.

## What it does

- Starts a local Shaggy dashboard backend on `127.0.0.1`.
- Enables the embedded `/chat` TUI experience with `shaggy dashboard --no-open --tui`.
- Generates a fresh per-launch dashboard session token in the Electron main process.
- Opens the private local workspace inside a sandboxed Electron window.

## Local development

```bash
cd apps/desktop
npm install
npm test
npm run pack
npm start
```

Useful overrides:

```bash
SHAGGY_DESKTOP_REPO_ROOT=/path/to/shaggy-agent npm start
SHAGGY_DESKTOP_BACKEND_URL=http://127.0.0.1:9120 npm start
```

## Verification standard

Before shipping a desktop change:

1. Run `node --check electron/main.cjs electron/preload.cjs src/boot.js`.
2. Run `npm test`.
3. Run `npm run pack` and verify the generated app metadata says `Shaggy The Agent`.
4. Run the web build from `../../web` because the desktop shell loads the dashboard `/chat` bundle.
5. Confirm `node_modules/`, `release/`, and `dist/` remain ignored and are not committed.

## Privacy / security notes

- The desktop app is local-first. It binds to loopback and does not publish the dashboard externally.
- The dashboard session token is generated at launch and passed to the backend through environment variables, not written into package files.
- The Electron renderer keeps `contextIsolation: true`, `nodeIntegration: false`, and `sandbox: true`.
