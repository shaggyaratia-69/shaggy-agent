const { app, BrowserWindow, Menu, shell } = require('electron')
const crypto = require('node:crypto')
const fs = require('node:fs')
const http = require('node:http')
const net = require('node:net')
const os = require('node:os')
const path = require('node:path')
const { spawn } = require('node:child_process')
const { pathToFileURL } = require('node:url')

const APP_NAME = 'Shaggy The Agent'
const PORT_FLOOR = 9120
const PORT_CEILING = 9199
const DEV_BACKEND = process.env.SHAGGY_DESKTOP_BACKEND_URL
const DEV_REPO_ROOT = process.env.SHAGGY_DESKTOP_REPO_ROOT
const SHAGGY_HOME = process.env.SHAGGY_HOME || path.join(os.homedir(), '.shaggy')

let mainWindow = null
let backendProcess = null
let connectionPromise = null
let bootLogs = []
let bootState = {
  phase: 'boot.idle',
  message: 'Preparing Shaggy The Agent',
  progress: 0,
  error: null
}

function rememberLog(chunk) {
  const text = Buffer.isBuffer(chunk) ? chunk.toString('utf8') : String(chunk || '')
  for (const line of text.split(/\r?\n/)) {
    if (!line.trim()) continue
    bootLogs.push(`[${new Date().toISOString()}] ${line}`)
  }
  bootLogs = bootLogs.slice(-120)
  sendBootState()
}

function updateBoot(partial) {
  bootState = { ...bootState, ...partial }
  sendBootState()
}

function sendBootState() {
  if (!mainWindow || mainWindow.isDestroyed()) return
  mainWindow.webContents.send('shaggy:boot', { ...bootState, logs: bootLogs.slice(-60) })
}

function fileExists(p) {
  try { return fs.existsSync(p) } catch { return false }
}

function isShaggyRoot(root) {
  return Boolean(root && fileExists(path.join(root, 'shaggy_cli', 'main.py')) && fileExists(path.join(root, 'shaggy_cli', 'web_server.py')))
}

function resolveRepoRoot() {
  const candidates = [
    DEV_REPO_ROOT,
    path.resolve(__dirname, '../../..'),
    path.join(SHAGGY_HOME, 'shaggy-agent'),
    path.join(os.homedir(), '.shaggy', 'shaggy-agent')
  ].filter(Boolean)
  for (const candidate of candidates) {
    const resolved = path.resolve(candidate)
    if (isShaggyRoot(resolved)) return resolved
  }
  return null
}

function findPython(repoRoot) {
  const candidates = [
    path.join(repoRoot, '.venv', 'bin', 'python'),
    path.join(repoRoot, 'venv', 'bin', 'python'),
    path.join(SHAGGY_HOME, 'shaggy-agent', 'venv', 'bin', 'python'),
    '/opt/homebrew/bin/python3',
    '/usr/local/bin/python3',
    '/usr/bin/python3'
  ]
  for (const candidate of candidates) {
    if (fileExists(candidate)) return candidate
  }
  return 'python3'
}

function pickPort() {
  return new Promise((resolve, reject) => {
    let port = PORT_FLOOR
    const tryNext = () => {
      if (port > PORT_CEILING) {
        reject(new Error(`No free port found in ${PORT_FLOOR}-${PORT_CEILING}`))
        return
      }
      const server = net.createServer()
      server.once('error', () => {
        port += 1
        tryNext()
      })
      server.once('listening', () => {
        const chosen = port
        server.close(() => resolve(chosen))
      })
      server.listen(port, '127.0.0.1')
    }
    tryNext()
  })
}

function fetchStatus(baseUrl, token) {
  return new Promise((resolve, reject) => {
    const req = http.request(`${baseUrl}/api/status`, {
      method: 'GET',
      headers: token ? { 'X-Shaggy-Session-Token': token } : {}
    }, res => {
      let body = ''
      res.setEncoding('utf8')
      res.on('data', chunk => { body += chunk })
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) resolve(body)
        else reject(new Error(`HTTP ${res.statusCode}: ${body.slice(0, 200)}`))
      })
    })
    req.once('error', reject)
    req.setTimeout(1000, () => {
      req.destroy(new Error('status request timed out'))
    })
    req.end()
  })
}

async function waitForShaggy(baseUrl, token) {
  const start = Date.now()
  let lastError = null
  while (Date.now() - start < 45000) {
    try {
      await fetchStatus(baseUrl, token)
      return
    } catch (error) {
      lastError = error
      await new Promise(resolve => setTimeout(resolve, 500))
    }
  }
  throw new Error(`Shaggy backend did not become ready: ${lastError?.message || 'timeout'}`)
}

async function startShaggy() {
  if (connectionPromise) return connectionPromise
  connectionPromise = (async () => {
    if (DEV_BACKEND) {
      updateBoot({ phase: 'backend.remote', message: `Using backend ${DEV_BACKEND}`, progress: 70 })
      await waitForShaggy(DEV_BACKEND, '')
      return { baseUrl: DEV_BACKEND, token: '', mode: 'external' }
    }

    updateBoot({ phase: 'backend.resolve', message: 'Finding local Shaggy install', progress: 12, error: null })
    const repoRoot = resolveRepoRoot()
    if (!repoRoot) {
      throw new Error(`Could not find Shaggy source. Set SHAGGY_DESKTOP_REPO_ROOT or install Shaggy at ${path.join(SHAGGY_HOME, 'shaggy-agent')}.`)
    }

    const python = findPython(repoRoot)
    const port = await pickPort()
    const token = crypto.randomBytes(32).toString('base64url')
    const webDist = path.join(repoRoot, 'shaggy_cli', 'web_dist')
    const args = ['-m', 'shaggy_cli.main', 'dashboard', '--no-open', '--tui', '--host', '127.0.0.1', '--port', String(port)]
    if (fileExists(webDist)) args.push('--skip-build')

    updateBoot({ phase: 'backend.spawn', message: `Starting Shaggy backend on port ${port}`, progress: 48 })
    rememberLog(`repo=${repoRoot}`)
    rememberLog(`python=${python}`)
    rememberLog(`${python} ${args.join(' ')}`)

    backendProcess = spawn(python, args, {
      cwd: repoRoot,
      env: {
        ...process.env,
        SHAGGY_HOME,
        SHAGGY_DESKTOP: '1',
        SHAGGY_DASHBOARD_TUI: '1',
        SHAGGY_DASHBOARD_SESSION_TOKEN: token,
        PYTHONPATH: [repoRoot, process.env.PYTHONPATH].filter(Boolean).join(path.delimiter),
        ...(fileExists(webDist) ? { SHAGGY_WEB_DIST: webDist } : {})
      },
      stdio: ['ignore', 'pipe', 'pipe']
    })

    backendProcess.stdout.on('data', rememberLog)
    backendProcess.stderr.on('data', rememberLog)
    backendProcess.once('error', error => {
      rememberLog(`backend error: ${error.message}`)
      connectionPromise = null
    })
    backendProcess.once('exit', (code, signal) => {
      rememberLog(`backend exited: ${signal || code}`)
      backendProcess = null
      connectionPromise = null
      updateBoot({ phase: 'backend.exit', message: `Shaggy backend exited (${signal || code})`, error: `Backend exited (${signal || code})` })
    })

    const baseUrl = `http://127.0.0.1:${port}`
    updateBoot({ phase: 'backend.wait', message: 'Waiting for Shaggy backend', progress: 82 })
    await waitForShaggy(baseUrl, token)
    updateBoot({ phase: 'backend.ready', message: 'Shaggy backend ready', progress: 100, error: null })
    return { baseUrl, token, mode: 'local' }
  })().catch(error => {
    updateBoot({ phase: 'backend.error', message: error.message, error: error.message })
    connectionPromise = null
    throw error
  })
  return connectionPromise
}

function buildMenu() {
  return Menu.buildFromTemplate([
    ...(process.platform === 'darwin' ? [{ label: APP_NAME, submenu: [{ role: 'about' }, { type: 'separator' }, { role: 'quit' }] }] : []),
    { label: 'File', submenu: process.platform === 'darwin' ? [{ role: 'close' }] : [{ role: 'quit' }] },
    { label: 'Edit', submenu: [{ role: 'undo' }, { role: 'redo' }, { type: 'separator' }, { role: 'cut' }, { role: 'copy' }, { role: 'paste' }, { role: 'selectAll' }] },
    { label: 'View', submenu: [{ role: 'reload' }, { role: 'forceReload' }, { role: 'toggleDevTools' }, { type: 'separator' }, { role: 'togglefullscreen' }] }
  ])
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1220,
    height: 800,
    minWidth: 420,
    minHeight: 620,
    title: APP_NAME,
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    backgroundColor: '#f7f2df',
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      backgroundThrottling: false,
      preload: path.join(__dirname, 'preload.cjs')
    }
  })

  mainWindow.webContents.setWindowOpenHandler(details => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  mainWindow.loadFile(path.join(__dirname, '..', 'src', 'boot.html'))
  mainWindow.webContents.once('did-finish-load', () => {
    sendBootState()
    startShaggy()
      .then(({ baseUrl, token }) => {
        const target = `${baseUrl}/chat${token ? `?token=${encodeURIComponent(token)}` : ''}`
        return mainWindow.loadURL(target)
      })
      .catch(error => rememberLog(error.stack || error.message))
  })
}

app.whenReady().then(() => {
  Menu.setApplicationMenu(buildMenu())
  createWindow()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})

app.on('before-quit', () => {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill('SIGTERM')
  }
})
