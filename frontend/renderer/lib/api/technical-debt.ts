import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface DebtIssue {
    id: string;
    session_id: string;
    file_path: string;
    issue_type: string; // 'complexity', 'duplication', 'dependency', 'smell', 'architecture', 'documentation'
    category: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    title: string;
    description: string;
    line_start?: number;
    line_end?: number;
    code_snippet?: string;
    suggested_fix?: string;
    estimated_hours: number;
    created_at: string;
}

export interface DebtSession {
    id: string;
    project_id: string;
    version: number;
    overall_score: number;
    complexity_score: number;
    duplication_score: number;
    dependency_score: number;
    summary: string;
    total_issues: number;
    critical_issues: number;
    estimated_hours: number;
    status: string;
    github_exported?: boolean;
    github_commit_sha?: string;
    github_exported_at?: string;
    created_at: string;
    debt_issues?: DebtIssue[];
}

export interface AnalyzeRequest {
    project_id: string;
    include_tests: boolean;
    max_depth: number;
    specific_files?: string[];
}

export const technicalDebtApi = {
    async analyzeProject(request: AnalyzeRequest, token: string): Promise<{ status: string; session_id: string; overall_score: number; total_issues: number }> {
        const response = await axios.post(`${API_URL}/api/debt/analyze`, request, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    },

    async getProjectSessions(projectId: string, token: string): Promise<DebtSession[]> {
        const response = await axios.get(`${API_URL}/api/debt/project/${projectId}`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    },

    async getSessionDetails(sessionId: string, token: string): Promise<DebtSession> {
        const response = await axios.get(`${API_URL}/api/debt/session/${sessionId}`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    },

    async deleteSession(sessionId: string, token: string): Promise<{ status: string }> {
        const response = await axios.delete(`${API_URL}/api/debt/session/${sessionId}`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    },

    async exportSessionToGitHub(sessionId: string, token: string): Promise<{ github_path: string; commit_sha: string; issues_exported: number }> {
        const response = await axios.post(`${API_URL}/api/debt/session/${sessionId}/export-github`, {}, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    },
};
