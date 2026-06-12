const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const { execFileSync } = require('node:child_process');

const desktopRoot = path.resolve(__dirname, '..');
const repoRoot = path.resolve(desktopRoot, '..', '..');

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(desktopRoot, relativePath), 'utf8'));
}

function gitTrackedDesktopFiles() {
  return execFileSync('git', ['ls-files', 'apps/desktop'], {
    cwd: repoRoot,
    encoding: 'utf8',
  })
    .trim()
    .split('\n')
    .filter(Boolean);
}

function isTextFile(file) {
  return /\.(cjs|mjs|js|jsx|ts|tsx|json|html|css|md|yml|yaml|toml|plist|txt|in|config|lock)$/.test(file);
}

test('Shaggy desktop contains the full upstream desktop application surface', () => {
  const tracked = gitTrackedDesktopFiles();

  assert.ok(
    tracked.length >= 450,
    `expected the full desktop app tree, found only ${tracked.length} tracked desktop files`,
  );

  for (const requiredFile of [
    'apps/desktop/electron/backend-probes.cjs',
    'apps/desktop/electron/bootstrap-runner.cjs',
    'apps/desktop/electron/dashboard-token.cjs',
    'apps/desktop/electron/hardening.cjs',
    'apps/desktop/electron/port-pool.cjs',
    'apps/desktop/electron/update-remote.cjs',
    'apps/desktop/src/app/chat/composer/index.tsx',
    'apps/desktop/src/app/settings/index.tsx',
    'apps/desktop/src/store/session.ts',
    'apps/desktop/src/store/gateway.ts',
    'apps/desktop/vite.config.ts',
  ]) {
    assert.ok(tracked.includes(requiredFile), `missing ${requiredFile}`);
  }
});

test('Shaggy desktop product metadata is white-labeled for Cherries and Co', () => {
  const pkg = readJson('package.json');

  assert.equal(pkg.name, 'shaggy-the-agent-desktop');
  assert.equal(pkg.productName, 'Shaggy The Agent');
  assert.equal(pkg.main, 'electron/main.cjs');
  assert.equal(pkg.build.appId, 'com.cherriesandco.shaggy.agent');
  assert.equal(pkg.build.productName, 'Shaggy The Agent');
  assert.equal(pkg.build.mac.extendInfo.CFBundleDisplayName, 'Shaggy The Agent');
  assert.equal(pkg.build.mac.extendInfo.CFBundleName, 'Shaggy The Agent');
  assert.equal(pkg.build.mac.executableName, 'Shaggy The Agent');
  assert.equal(pkg.build.dmg.title, 'Install Shaggy The Agent');
  assert.equal(pkg.build.nsis.shortcutName, 'Shaggy The Agent');
  assert.deepEqual(pkg.build.mac.target, ['dmg', 'zip']);
  assert.ok(pkg.scripts.typecheck, 'typecheck script must exist');
  assert.ok(pkg.scripts['test:desktop'], 'desktop test script must exist');
  assert.ok(pkg.scripts['dist:mac'], 'mac desktop distribution script must exist');
});

test('Shaggy desktop preserves local hardened runtime and tokenized desktop startup', () => {
  const main = fs.readFileSync(path.join(desktopRoot, 'electron/main.cjs'), 'utf8');
  const sessionWindows = fs.readFileSync(path.join(desktopRoot, 'electron/session-windows.cjs'), 'utf8');

  assert.match(main, /127\.0\.0\.1/);
  assert.match(main, /contextIsolation:\s*true/);
  assert.match(main, /nodeIntegration:\s*false/);
  assert.match(main, /sandbox:\s*true/);
  assert.match(main, /SHAGGY_DASHBOARD_SESSION_TOKEN/);
  assert.match(main, /buildSessionWindowUrl/);
  assert.match(sessionWindows, /HashRouter/);
});

test('tracked Shaggy desktop files do not expose old public Hermes branding', () => {
  const tracked = gitTrackedDesktopFiles();
  const forbiddenTerms = [
    ['Her', 'mes Agent'].join(''),
    ['Her', 'mes'].join(''),
    ['No', 'us Research'].join(''),
    ['NO', 'US SHAGGY'].join(''),
    ['Har', 'vey'].join(''),
    ['com.', 'nousresearch.', 'hermes'].join(''),
    ['github.com/', 'NousResearch'].join(''),
  ];
  const allowed = new Set([
    'apps/desktop/tests/full-product-sync.test.cjs',
  ]);

  const findings = [];
  for (const file of tracked) {
    if (allowed.has(file)) continue;
    if (/\bhermes\b/i.test(file)) findings.push(`${file}: filename contains old brand`);
    if (!isTextFile(file)) continue;
    const absolute = path.join(repoRoot, file);
    let text;
    try {
      text = fs.readFileSync(absolute, 'utf8');
    } catch {
      continue;
    }
    for (const term of forbiddenTerms) {
      if (text.includes(term)) findings.push(`${file}: contains ${term}`);
    }
  }

  assert.deepEqual(findings, []);
});
