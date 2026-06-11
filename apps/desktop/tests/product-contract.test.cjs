const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const test = require('node:test')

const root = path.resolve(__dirname, '..')
const read = relative => fs.readFileSync(path.join(root, relative), 'utf8')
const packageJson = JSON.parse(read('package.json'))

test('desktop package is branded as Shaggy The Agent', () => {
  assert.equal(packageJson.name, 'shaggy-the-agent-desktop')
  assert.equal(packageJson.productName, 'Shaggy The Agent')
  assert.equal(packageJson.build.appId, 'com.cherriesandco.shaggy.agent')
  assert.equal(packageJson.build.productName, 'Shaggy The Agent')
  assert.equal(packageJson.build.executableName, 'Shaggy The Agent')
  assert.match(packageJson.build.artifactName, /^Shaggy-The-Agent-/)
  assert.equal(packageJson.build.mac.extendInfo.CFBundleDisplayName, 'Shaggy The Agent')
})

test('desktop bundle only ships the Electron shell assets', () => {
  assert.deepEqual(packageJson.build.files, [
    'electron/**',
    'src/**',
    'assets/**',
    'package.json'
  ])
  assert.equal(packageJson.build.asar, true)
})

test('boot screen uses customer-facing Shaggy The Agent wording', () => {
  const html = read('src/boot.html')
  const js = read('src/boot.js')
  const main = read('electron/main.cjs')

  assert.match(html, /<title>Shaggy The Agent<\/title>/)
  assert.match(html, /Shaggy<br \/>The Agent/)
  assert.match(html, /Private Local Agent/)
  assert.match(html, /private desktop workspace/)
  assert.match(js, /Starting Shaggy The Agent/)
  assert.match(main, /const APP_NAME = 'Shaggy The Agent'/)
  assert.doesNotMatch(html + js + main, /Shaggy Desktop/)
})

test('desktop main process keeps backend local and passes token through env/query', () => {
  const main = read('electron/main.cjs')

  assert.match(main, /127\.0\.0\.1/)
  assert.match(main, /SHAGGY_DASHBOARD_SESSION_TOKEN: token/)
  assert.match(main, /crypto\.randomBytes\(32\)\.toString\('base64url'\)/)
  assert.match(main, /dashboard', '--no-open', '--tui'/)
  assert.match(main, /encodeURIComponent\(token\)/)
  assert.match(main, /nodeIntegration: false/)
  assert.match(main, /contextIsolation: true/)
  assert.match(main, /sandbox: true/)
})

test('ignored generated desktop artifacts stay out of git source package', () => {
  const ignore = read('.gitignore')
  assert.match(ignore, /^node_modules\/$/m)
  assert.match(ignore, /^release\/$/m)
  assert.match(ignore, /^dist\/$/m)
})
