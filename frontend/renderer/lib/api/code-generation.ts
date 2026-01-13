import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface TechStackConfig {
  backend: string;
  database: string;
  frontend: string;
  orm: string;
}

export interface GeneratedFile {
  file_path: string;
  content: string;
  file_type: 'model' | 'api' | 'service' | 'component' | 'test' | 'migration';
  language: string;
  dependencies: string[];
  description?: string;
}

export interface CodeGenerationResult {
  session_id: string;
  requirement_id: string;
  files: GeneratedFile[];
  total_files: number;
  total_lines: number;
  generation_time: number;
  status: 'pending' | 'generating' | 'completed' | 'approved' | 'rejected' | 'committed';
  api_used: Record<string, string>;
}

export interface CodeGenerationRequest {
  project_id: string;
  requirement_id: string;
  tech_stack?: TechStackConfig;
  include_tests?: boolean;
  include_migrations?: boolean;
  generation_scope?: string[];
}

export interface ApproveCodeRequest {
  session_id: string;
  commit_message?: string;
  branch?: string;
  target_directory?: string;
}

export interface ApproveCodeResponse {
  commit_sha: string;
  commit_url: string;
  files_committed: number;
  branch: string;
}

export const codeGenerationApi = {
  async generateCode(request: CodeGenerationRequest, token: string): Promise<CodeGenerationResult> {
    const response = await axios.post(`${API_URL}/api/code-generation/generate`, request, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  async getSession(sessionId: string, token: string): Promise<CodeGenerationResult> {
    const response = await axios.get(`${API_URL}/api/code-generation/sessions/${sessionId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  async getLatestForRequirement(requirementId: string, token: string): Promise<CodeGenerationResult | null> {
    try {
      const response = await axios.get(`${API_URL}/api/code-generation/requirement/${requirementId}/latest`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    } catch (error: any) {
      if (error.response && error.response.status === 404) {
        return null;
      }
      throw error;
    }
  },

  async approveCode(request: ApproveCodeRequest, token: string): Promise<ApproveCodeResponse> {
    const response = await axios.post(`${API_URL}/api/code-generation/approve`, request, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  async compareSession(sessionId: string, token: string): Promise<ComparisonResult> {
    const response = await axios.get(`${API_URL}/api/code-generation/sessions/${sessionId}/compare`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  async applySession(sessionId: string, request: ApproveCodeRequest, token: string): Promise<ApproveCodeResponse> {
    // This uses the apply endpoint which is semantically 'merge and commit'
    const response = await axios.post(`${API_URL}/api/code-generation/sessions/${sessionId}/apply`, request, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },
};

export interface FileDiff {
  file_path: string;
  change_type: 'create' | 'modify' | 'delete' | 'identical';
  old_content?: string;
  new_content?: string;
  diff_stat: string;
}

export interface ComparisonResult {
  session_id: string;
  project_id: string;
  diffs: FileDiff[];
  total_changes: number;
  can_apply_automatically: boolean;
}

