const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('shaggyDesktop', {
  onBoot: callback => {
    const handler = (_event, state) => callback(state)
    ipcRenderer.on('shaggy:boot', handler)
    return () => ipcRenderer.removeListener('shaggy:boot', handler)
  }
})
