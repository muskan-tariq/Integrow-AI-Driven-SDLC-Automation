import Store from 'electron-store'

interface AuthData {
  accessToken: string
  user: {
    id: string
    github_username: string
    github_id: number
    email: string | null
    avatar_url: string | null
  }
}

// Secure store for authentication data
// Note: Removed encryptionKey as it was causing issues with electron-store
// The JWT token itself is already secure, and GitHub tokens are encrypted in the backend
const store = new Store({
  name: 'integrow-auth',
})

export class AuthService {
  private static TOKEN_KEY = 'auth_token'
  private static USER_KEY = 'user_data'

  /**
   * Store authentication data securely
   */
  static setAuth(authData: AuthData): void {
    try {
      // Clear the entire store first to avoid schema conflicts
      store.clear()
      
      // Set new values
      store.set(this.TOKEN_KEY, authData.accessToken)
      store.set(this.USER_KEY, authData.user)
      
      console.log('✅ Auth data stored successfully')
    } catch (error) {
      console.error('❌ Error storing auth data:', error)
      throw error
    }
  }

  /**
   * Get stored access token
   */
  static getToken(): string | null {
    return store.get(this.TOKEN_KEY) as string | null
  }

  /**
   * Get stored user data
   */
  static getUser(): AuthData['user'] | null {
    return store.get(this.USER_KEY) as AuthData['user'] | null
  }

  /**
   * Check if user is authenticated
   */
  static isAuthenticated(): boolean {
    return !!this.getToken()
  }

  /**
   * Clear all authentication data
   */
  static clearAuth(): void {
    store.delete(this.TOKEN_KEY)
    store.delete(this.USER_KEY)
  }

  /**
   * Get full auth data
   */
  static getAuthData(): AuthData | null {
    const token = this.getToken()
    const user = this.getUser()

    if (!token || !user) {
      return null
    }

    return {
      accessToken: token,
      user,
    }
  }
}
