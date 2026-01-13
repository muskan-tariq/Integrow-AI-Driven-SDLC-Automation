import { contextBridge, ipcRenderer, IpcRendererEvent } from 'electron'

const handler = {
  send(channel: string, value: unknown) {
    ipcRenderer.send(channel, value)
  },
  on(channel: string, callback: (...args: unknown[]) => void) {
    const subscription = (_event: IpcRendererEvent, ...args: unknown[]) =>
      callback(...args)
    ipcRenderer.on(channel, subscription)

    return () => {
      ipcRenderer.removeListener(channel, subscription)
    }
  }
}

contextBridge.exposeInMainWorld('ipc', handler)

// Expose Electron APIs to renderer
contextBridge.exposeInMainWorld('electron', {
  // OAuth
  openGitHubOAuth: () => ipcRenderer.invoke('github-oauth'),
  exchangeCode: (code: string) => ipcRenderer.invoke('exchange-code', code),
  
  // Auth management
  getAuth: () => ipcRenderer.invoke('get-auth'),
  logout: () => ipcRenderer.invoke('logout'),
  checkAuth: () => ipcRenderer.invoke('check-auth'),
  
  // File system access
  openFolder: (folderPath: string) => ipcRenderer.invoke('open-folder', folderPath),
  openExternal: (url: string) => ipcRenderer.invoke('open-external', url),
  
  // Auth status listener
  onAuthCallback: (callback: (data: { code: string }) => void) => {
    ipcRenderer.on('auth-callback', (_event, data) => callback(data))
  },
  onAuthStatus: (callback: (data: { isAuthenticated: boolean }) => void) => {
    ipcRenderer.on('auth-status', (_event, data) => callback(data))
  },
})

export type IpcHandler = typeof handler
