const { contextBridge, ipcRenderer, webUtils } = require('electron')

contextBridge.exposeInMainWorld('shaggyDesktop', {
  getConnection: profile => ipcRenderer.invoke('shaggy:connection', profile),
  revalidateConnection: () => ipcRenderer.invoke('shaggy:connection:revalidate'),
  touchBackend: profile => ipcRenderer.invoke('shaggy:backend:touch', profile),
  getGatewayWsUrl: profile => ipcRenderer.invoke('shaggy:gateway:ws-url', profile),
  openSessionWindow: sessionId => ipcRenderer.invoke('shaggy:window:openSession', sessionId),
  getBootProgress: () => ipcRenderer.invoke('shaggy:boot-progress:get'),
  getConnectionConfig: profile => ipcRenderer.invoke('shaggy:connection-config:get', profile),
  saveConnectionConfig: payload => ipcRenderer.invoke('shaggy:connection-config:save', payload),
  applyConnectionConfig: payload => ipcRenderer.invoke('shaggy:connection-config:apply', payload),
  testConnectionConfig: payload => ipcRenderer.invoke('shaggy:connection-config:test', payload),
  probeConnectionConfig: remoteUrl => ipcRenderer.invoke('shaggy:connection-config:probe', remoteUrl),
  oauthLoginConnectionConfig: remoteUrl => ipcRenderer.invoke('shaggy:connection-config:oauth-login', remoteUrl),
  oauthLogoutConnectionConfig: remoteUrl => ipcRenderer.invoke('shaggy:connection-config:oauth-logout', remoteUrl),
  profile: {
    get: () => ipcRenderer.invoke('shaggy:profile:get'),
    set: name => ipcRenderer.invoke('shaggy:profile:set', name)
  },
  api: request => ipcRenderer.invoke('shaggy:api', request),
  notify: payload => ipcRenderer.invoke('shaggy:notify', payload),
  requestMicrophoneAccess: () => ipcRenderer.invoke('shaggy:requestMicrophoneAccess'),
  readFileDataUrl: filePath => ipcRenderer.invoke('shaggy:readFileDataUrl', filePath),
  readFileText: filePath => ipcRenderer.invoke('shaggy:readFileText', filePath),
  selectPaths: options => ipcRenderer.invoke('shaggy:selectPaths', options),
  writeClipboard: text => ipcRenderer.invoke('shaggy:writeClipboard', text),
  saveImageFromUrl: url => ipcRenderer.invoke('shaggy:saveImageFromUrl', url),
  saveImageBuffer: (data, ext) => ipcRenderer.invoke('shaggy:saveImageBuffer', { data, ext }),
  saveClipboardImage: () => ipcRenderer.invoke('shaggy:saveClipboardImage'),
  getPathForFile: file => {
    try {
      return webUtils.getPathForFile(file) || ''
    } catch {
      return ''
    }
  },
  normalizePreviewTarget: (target, baseDir) => ipcRenderer.invoke('shaggy:normalizePreviewTarget', target, baseDir),
  watchPreviewFile: url => ipcRenderer.invoke('shaggy:watchPreviewFile', url),
  stopPreviewFileWatch: id => ipcRenderer.invoke('shaggy:stopPreviewFileWatch', id),
  setTitleBarTheme: payload => ipcRenderer.send('shaggy:titlebar-theme', payload),
  setPreviewShortcutActive: active => ipcRenderer.send('shaggy:previewShortcutActive', Boolean(active)),
  openExternal: url => ipcRenderer.invoke('shaggy:openExternal', url),
  fetchLinkTitle: url => ipcRenderer.invoke('shaggy:fetchLinkTitle', url),
  sanitizeWorkspaceCwd: cwd => ipcRenderer.invoke('shaggy:workspace:sanitize', cwd),
  settings: {
    getDefaultProjectDir: () => ipcRenderer.invoke('shaggy:setting:defaultProjectDir:get'),
    setDefaultProjectDir: dir => ipcRenderer.invoke('shaggy:setting:defaultProjectDir:set', dir),
    pickDefaultProjectDir: () => ipcRenderer.invoke('shaggy:setting:defaultProjectDir:pick')
  },
  revealLogs: () => ipcRenderer.invoke('shaggy:logs:reveal'),
  getRecentLogs: () => ipcRenderer.invoke('shaggy:logs:recent'),
  readDir: dirPath => ipcRenderer.invoke('shaggy:fs:readDir', dirPath),
  gitRoot: startPath => ipcRenderer.invoke('shaggy:fs:gitRoot', startPath),
  terminal: {
    dispose: id => ipcRenderer.invoke('shaggy:terminal:dispose', id),
    resize: (id, size) => ipcRenderer.invoke('shaggy:terminal:resize', id, size),
    start: options => ipcRenderer.invoke('shaggy:terminal:start', options),
    write: (id, data) => ipcRenderer.invoke('shaggy:terminal:write', id, data),
    onData: (id, callback) => {
      const channel = `shaggy:terminal:${id}:data`
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on(channel, listener)
      return () => ipcRenderer.removeListener(channel, listener)
    },
    onExit: (id, callback) => {
      const channel = `shaggy:terminal:${id}:exit`
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on(channel, listener)
      return () => ipcRenderer.removeListener(channel, listener)
    }
  },
  onClosePreviewRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('shaggy:close-preview-requested', listener)
    return () => ipcRenderer.removeListener('shaggy:close-preview-requested', listener)
  },
  onOpenUpdatesRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('shaggy:open-updates', listener)
    return () => ipcRenderer.removeListener('shaggy:open-updates', listener)
  },
  onDeepLink: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('shaggy:deep-link', listener)
    return () => ipcRenderer.removeListener('shaggy:deep-link', listener)
  },
  signalDeepLinkReady: () => ipcRenderer.invoke('shaggy:deep-link-ready'),
  onWindowStateChanged: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('shaggy:window-state-changed', listener)
    return () => ipcRenderer.removeListener('shaggy:window-state-changed', listener)
  },
  onPreviewFileChanged: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('shaggy:preview-file-changed', listener)
    return () => ipcRenderer.removeListener('shaggy:preview-file-changed', listener)
  },
  onBackendExit: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('shaggy:backend-exit', listener)
    return () => ipcRenderer.removeListener('shaggy:backend-exit', listener)
  },
  onPowerResume: callback => {
    const listener = () => callback()
    ipcRenderer.on('shaggy:power-resume', listener)
    return () => ipcRenderer.removeListener('shaggy:power-resume', listener)
  },
  onBootProgress: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('shaggy:boot-progress', listener)
    return () => ipcRenderer.removeListener('shaggy:boot-progress', listener)
  },
  // First-launch bootstrap progress -- emitted by the install.ps1 stage
  // runner in main.cjs (apps/desktop/electron/bootstrap-runner.cjs).
  // Renderer's install overlay subscribes to live events and queries the
  // current snapshot via getBootstrapState() to recover after a devtools
  // reload mid-bootstrap.
  getBootstrapState: () => ipcRenderer.invoke('shaggy:bootstrap:get'),
  resetBootstrap: () => ipcRenderer.invoke('shaggy:bootstrap:reset'),
  repairBootstrap: () => ipcRenderer.invoke('shaggy:bootstrap:repair'),
  cancelBootstrap: () => ipcRenderer.invoke('shaggy:bootstrap:cancel'),
  onBootstrapEvent: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('shaggy:bootstrap:event', listener)
    return () => ipcRenderer.removeListener('shaggy:bootstrap:event', listener)
  },
  getVersion: () => ipcRenderer.invoke('shaggy:version'),
  uninstall: {
    summary: () => ipcRenderer.invoke('shaggy:uninstall:summary'),
    run: mode => ipcRenderer.invoke('shaggy:uninstall:run', { mode })
  },
  updates: {
    check: () => ipcRenderer.invoke('shaggy:updates:check'),
    apply: opts => ipcRenderer.invoke('shaggy:updates:apply', opts),
    getBranch: () => ipcRenderer.invoke('shaggy:updates:branch:get'),
    setBranch: name => ipcRenderer.invoke('shaggy:updates:branch:set', name),
    onProgress: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('shaggy:updates:progress', listener)
      return () => ipcRenderer.removeListener('shaggy:updates:progress', listener)
    }
  },
  themes: {
    fetchMarketplace: id => ipcRenderer.invoke('shaggy:vscode-theme:fetch', id),
    searchMarketplace: query => ipcRenderer.invoke('shaggy:vscode-theme:search', query)
  }
})
