-- Phase 5: Technical Debt Analyzer Database Schema
-- Creates tables for tracking technical debt analysis sessions and detected issues

-- Enable UUID extension (should already be enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Debt Sessions Table
CREATE TABLE IF NOT EXISTS debt_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    overall_score INTEGER DEFAULT 0,
    complexity_score INTEGER DEFAULT 0,
    duplication_score INTEGER DEFAULT 0,
    dependency_score INTEGER DEFAULT 0,
    summary TEXT,
    total_issues INTEGER DEFAULT 0,
    critical_issues INTEGER DEFAULT 0,
    estimated_hours FLOAT DEFAULT 0,
    status TEXT DEFAULT 'completed' CHECK (status IN ('in_progress', 'completed', 'failed')),
    github_exported BOOLEAN DEFAULT FALSE,
    github_commit_sha TEXT,
    github_exported_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Debt Issues Table
CREATE TABLE IF NOT EXISTS debt_issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES debt_sessions(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    issue_type TEXT NOT NULL, -- 'complexity', 'duplication', 'dependency', 'smell', 'architecture', 'documentation'
    category TEXT NOT NULL, -- e.g., 'High Complexity', 'Duplicate Code', 'Outdated Dependency'
    severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    line_start INTEGER,
    line_end INTEGER,
    code_snippet TEXT,
    suggested_fix TEXT,
    estimated_hours FLOAT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_debt_sessions_project ON debt_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_debt_sessions_version ON debt_sessions(project_id, version);
CREATE INDEX IF NOT EXISTS idx_debt_sessions_created ON debt_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_debt_issues_session ON debt_issues(session_id);
CREATE INDEX IF NOT EXISTS idx_debt_issues_severity ON debt_issues(severity);
CREATE INDEX IF NOT EXISTS idx_debt_issues_type ON debt_issues(issue_type);

-- Enable Row Level Security
ALTER TABLE debt_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE debt_issues ENABLE ROW LEVEL SECURITY;

-- RLS Policies for debt_sessions
CREATE POLICY "Users can view debt sessions for their projects"
    ON debt_sessions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = debt_sessions.project_id
            AND projects.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create debt sessions for their projects"
    ON debt_sessions FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = debt_sessions.project_id
            AND projects.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update debt sessions for their projects"
    ON debt_sessions FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = debt_sessions.project_id
            AND projects.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete debt sessions for their projects"
    ON debt_sessions FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = debt_sessions.project_id
            AND projects.user_id = auth.uid()
        )
    );

-- RLS Policies for debt_issues
CREATE POLICY "Users can view debt issues for their sessions"
    ON debt_issues FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM debt_sessions
            JOIN projects ON projects.id = debt_sessions.project_id
            WHERE debt_sessions.id = debt_issues.session_id
            AND projects.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create debt issues for their sessions"
    ON debt_issues FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM debt_sessions
            JOIN projects ON projects.id = debt_sessions.project_id
            WHERE debt_sessions.id = debt_issues.session_id
            AND projects.user_id = auth.uid()
        )
    );

-- Comments for documentation
COMMENT ON TABLE debt_sessions IS 'Stores technical debt analysis sessions with overall metrics';
COMMENT ON TABLE debt_issues IS 'Stores individual technical debt issues detected during analysis';
COMMENT ON COLUMN debt_sessions.overall_score IS 'Overall technical debt score (0-100, higher is better)';
COMMENT ON COLUMN debt_sessions.estimated_hours IS 'Estimated hours to resolve all issues in this session';
COMMENT ON COLUMN debt_issues.issue_type IS 'Type of debt: complexity, duplication, dependency, smell, architecture, documentation';
COMMENT ON COLUMN debt_issues.estimated_hours IS 'Estimated hours to resolve this specific issue';
