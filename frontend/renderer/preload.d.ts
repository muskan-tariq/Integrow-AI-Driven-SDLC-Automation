import { IpcHandler } from '../main/preload'

declare global {
  interface Window {
    ipc: IpcHandler
    electron: {
      // OAuth
      openGitHubOAuth: () => Promise<{ success: boolean }>
      exchangeCode: (code: string) => Promise<{
        success: boolean
        data?: {
          access_token: string
          user: {
            id: string
            github_username: string
            github_id: number
            email: string | null
            avatar_url: string | null
          }
        }
        error?: string
      }>
      
      // Auth management
      getAuth: () => Promise<{
        accessToken: string
        user: {
          id: string
          github_username: string
          github_id: number
          email: string | null
          avatar_url: string | null
        }
      } | null>
      logout: () => Promise<{ success: boolean }>
      checkAuth: () => Promise<{ isAuthenticated: boolean }>
      
      // File system access
      openFolder: (folderPath: string) => Promise<{ success: boolean; error?: string }>
      openExternal: (url: string) => Promise<{ success: boolean; error?: string }>
      
      // Event listeners
      onAuthCallback: (callback: (data: { code: string }) => void) => void
      onAuthStatus: (callback: (data: { isAuthenticated: boolean }) => void) => void
    }
  }
}

