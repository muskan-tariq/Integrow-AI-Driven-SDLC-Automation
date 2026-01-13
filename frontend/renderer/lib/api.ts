const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface User {
  id: string
  github_username: string
  github_id: number
  email: string | null
  avatar_url: string | null
  created_at: string
}

interface Project {
  id: string
  name: string
  description: string | null
  github_repo_url: string
  local_path: string
  visibility: 'public' | 'private'
  template: string
  status: 'active' | 'archived'
  created_at: string
  updated_at: string
}

interface CreateProjectInput {
  name: string
  description?: string
  visibility: 'public' | 'private'
  template: string
}

class APIClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  setToken(token: string) {
    this.token = token
  }

  clearToken() {
    this.token = null
  }

  getToken(): string | null {
    return this.token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: 'An unknown error occurred',
      }))
      const errorWithStatus: any = new Error(error.detail || `HTTP ${response.status}`)
      errorWithStatus.status = response.status
      throw errorWithStatus
    }

    return response.json()
  }

  // Auth endpoints
  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/auth/me')
  }

  async logout(): Promise<{ status: string }> {
    return this.request('/api/auth/logout', { method: 'POST' })
  }

  // Project endpoints
  async getProjects(params?: {
    limit?: number
    offset?: number
    sort?: string
    order?: 'asc' | 'desc'
  }): Promise<{ projects: Project[]; total: number; limit: number; offset: number }> {
    const searchParams = new URLSearchParams()
    if (params?.limit) searchParams.set('limit', params.limit.toString())
    if (params?.offset) searchParams.set('offset', params.offset.toString())
    if (params?.sort) searchParams.set('sort', params.sort)
    if (params?.order) searchParams.set('order', params.order)

    const query = searchParams.toString()
    return this.request(`/api/projects${query ? `?${query}` : ''}`)
  }

  async getProject(projectId: string): Promise<Project> {
    return this.request<Project>(`/api/projects/${projectId}`)
  }

  async createProject(data: CreateProjectInput): Promise<Project> {
    return this.request<Project>('/api/projects/create', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateProject(
    projectId: string,
    data: Partial<CreateProjectInput>
  ): Promise<Project> {
    return this.request<Project>(`/api/projects/${projectId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteProject(projectId: string): Promise<{ status: string }> {
    return this.request(`/api/projects/${projectId}`, {
      method: 'DELETE',
    })
  }

  async getProjectFiles(projectId: string): Promise<{ files: any[] }> {
    return this.request(`/api/projects/${projectId}/files`)
  }

  // Health check
  async healthCheck(): Promise<{ status: string; database: string }> {
    return this.request('/health')
  }
}

export const api = new APIClient(API_BASE_URL)
export type { User, Project, CreateProjectInput }
