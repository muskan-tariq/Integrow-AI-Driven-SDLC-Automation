import path from 'path'
import { app, ipcMain, BrowserWindow, shell, protocol } from 'electron'
import serve from 'electron-serve'
import { createWindow } from './helpers'
import { AuthService } from './services/auth-service'

const isProd = process.env.NODE_ENV === 'production'

// GitHub OAuth configuration
const GITHUB_CLIENT_ID = 'Ov23lizA5BZy7YziOsy7' // UPDATE THIS with your Client ID from GitHub
const BACKEND_URL = 'http://localhost:8000'
const REDIRECT_URI = `${BACKEND_URL}/api/auth/github/callback`

// Store the main window reference globally
let mainWindow: BrowserWindow | null = null

// Prevent multiple instances of the app
const gotTheLock = app.requestSingleInstanceLock()

if (!gotTheLock) {
  app.quit()
} else {
  app.on('second-instance', (event, commandLine, workingDirectory) => {
    // Someone tried to run a second instance, we should focus our window instead
    const windows = BrowserWindow.getAllWindows()
    if (windows.length > 0) {
      const mainWindow = windows[0]
      if (mainWindow.isMinimized()) mainWindow.restore()
      mainWindow.focus()
    }
  })

  if (isProd) {
    serve({ directory: 'app' })
  } else {
    app.setPath('userData', `${app.getPath('userData')} (development)`)
  }

  ; (async () => {
    await app.whenReady()

    // Register custom protocol for OAuth callback
    protocol.registerHttpProtocol('integrow', (request, callback) => {
      // Handle the OAuth callback
      const url = new URL(request.url)
      if (url.hostname === 'auth' && url.pathname === '/callback') {
        const code = url.searchParams.get('code')
        if (code && mainWindow) {
          // Send the code to the renderer process
          mainWindow.webContents.send('auth-callback', { code })
        }
      }
    })

    mainWindow = createWindow('main', {
      width: 1200,
      height: 800,
      webPreferences: {
        preload: path.join(__dirname, 'preload.js'),
        nodeIntegration: false,
        contextIsolation: true,
      }
    })

    if (isProd) {
      await mainWindow.loadURL('app://./')
    } else {
      const port = process.argv[2]

      await mainWindow.loadURL(`http://localhost:${port}/`)
      mainWindow.webContents.openDevTools()
    }

    // Check if user is already authenticated
    const isAuthenticated = AuthService.isAuthenticated()
    if (isAuthenticated && mainWindow) {
      mainWindow.webContents.send('auth-status', { isAuthenticated: true })
    }
  })()

  app.on('window-all-closed', () => {
    app.quit()
  })

  // GitHub OAuth IPC handler
  ipcMain.handle('github-oauth', async () => {
    const authUrl = `https://github.com/login/oauth/authorize?client_id=${GITHUB_CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scope=repo,user`

    // Create a new browser window for OAuth
    const authWindow = new BrowserWindow({
      width: 800,
      height: 600,
      show: true,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
      }
    })

    authWindow.loadURL(authUrl)

    // Listen for the callback URL
    authWindow.webContents.on('will-redirect', (event, url) => {
      handleCallback(url, authWindow)
    })

    authWindow.webContents.on('did-navigate', (event, url) => {
      handleCallback(url, authWindow)
    })

    function handleCallback(url: string, window: BrowserWindow) {
      const urlObj = new URL(url)

      console.log('🔍 Checking URL:', url);

      // Check if this is our callback URL
      if (urlObj.origin === BACKEND_URL && urlObj.pathname === '/api/auth/github/callback') {
        const code = urlObj.searchParams.get('code')

        console.log('✅ Callback URL matched! Code:', code);

        if (code && mainWindow) {
          // Send code to renderer
          console.log('📤 Sending code to renderer...');
          mainWindow.webContents.send('auth-callback', { code })

          // Close the auth window
          window.close()
        }
      }
    }

    return { success: true }
  })

  // Handle OAuth callback with code
  ipcMain.handle('exchange-code', async (event, code: string) => {
    try {
      console.log('🔄 Exchanging code:', code);
      // Exchange code for token by calling backend
      const response = await fetch(`${BACKEND_URL}/api/auth/github/callback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      })

      console.log('📡 Backend response status:', response.status);

      if (!response.ok) {
        const error = await response.json()
        console.error('❌ Backend error:', error);
        throw new Error(error.detail || 'Authentication failed')
      }

      const authData = await response.json()
      console.log('✅ Auth data received:', { ...authData, access_token: '***' });

      // Transform the response to match our interface
      // Backend returns: { access_token, user }
      // We need: { accessToken, user }
      const transformedData = {
        accessToken: authData.access_token,
        user: authData.user
      }

      console.log('💾 Storing auth data...');
      // Store authentication data securely
      try {
        AuthService.setAuth(transformedData)
        console.log('💾 Auth data stored successfully');
      } catch (storeError) {
        console.error('❌ Error storing auth data:', storeError);
        throw new Error('Failed to store authentication data: ' + (storeError instanceof Error ? storeError.message : 'Unknown error'))
      }

      return { success: true, data: transformedData }
    } catch (error) {
      console.error('❌ Code exchange error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  })

  // Get stored auth data
  ipcMain.handle('get-auth', async () => {
    const authData = AuthService.getAuthData()
    return authData
  })

  // Logout handler
  ipcMain.handle('logout', async () => {
    AuthService.clearAuth()
    return { success: true }
  })

  // Check auth status
  ipcMain.handle('check-auth', async () => {
    return { isAuthenticated: AuthService.isAuthenticated() }
  })

  // File system access - Open folder in file explorer
  ipcMain.handle('open-folder', async (event, folderPath: string) => {
    try {
      console.log('📂 Opening folder:', folderPath)
      await shell.openPath(folderPath)
      return { success: true }
    } catch (error) {
      console.error('❌ Error opening folder:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  })

  // Open URL in external browser
  ipcMain.handle('open-external', async (event, url: string) => {
    try {
      console.log('🌐 Opening URL:', url)
      await shell.openExternal(url)
      return { success: true }
    } catch (error) {
      console.error('❌ Error opening URL:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  })
}
