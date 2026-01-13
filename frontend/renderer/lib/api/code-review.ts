import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ReviewIssue {
    id?: string;
    line_number?: number;
    issue_type: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    description: string;
    suggested_fix?: string;
}

export interface CodeReviewReport {
    id: string;
    session_id?: string;
    file_path: string;
    score: number;
    version: number;
    summary: string;
    issues: ReviewIssue[];
    created_at: string;
    github_exported?: boolean;
    github_commit_sha?: string;
    github_exported_at?: string;
}

export interface ReviewSession {
    id: string;
    project_id: string;
    version: number;
    score: number;
    summary: string;
    created_at: string;
    code_reviews?: CodeReviewReport[];
    github_exported?: boolean;
    github_commit_sha?: string;
    github_exported_at?: string;
}

export interface AnalyzeRequest {
    project_id: string;
    file_paths: string[];
}

export const codeReviewApi = {
    async analyzeFiles(request: AnalyzeRequest, token: string): Promise<{ status: string; session_id: string; results: CodeReviewReport[] }> {
        const response = await axios.post(`${API_URL}/api/review/analyze`, request, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    },

    async getProjectSessions(projectId: string, token: string): Promise<ReviewSession[]> {
        const response = await axios.get(`${API_URL}/api/review/project/${projectId}`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    },

    async getSessionDetails(sessionId: string, token: string): Promise<ReviewSession> {
        const response = await axios.get(`${API_URL}/api/review/session/${sessionId}`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    },

    async deleteReviewSession(sessionId: string, token: string): Promise<{ status: string }> {
        const response = await axios.delete(`${API_URL}/api/review/session/${sessionId}`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    },

    async exportReviewToGitHub(reviewId: string, token: string): Promise<{ github_path: string; commit_sha: string }> {
        const response = await axios.post(`${API_URL}/api/review/${reviewId}/export-github`, {}, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    },

    async exportSessionToGitHub(sessionId: string, token: string): Promise<{ github_path: string; commit_sha: string; files_exported: number }> {
        const response = await axios.post(`${API_URL}/api/review/session/${sessionId}/export-github`, {}, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    },
};
