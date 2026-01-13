-- Migration: Phase 4 Review Sessions
-- Description: Add review_sessions table for grouping multi-file reviews.

-- Create review_sessions table
CREATE TABLE IF NOT EXISTS review_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    score INTEGER DEFAULT 0,
    status TEXT DEFAULT 'completed',
    summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add session_id to code_reviews
ALTER TABLE code_reviews ADD COLUMN IF NOT EXISTS session_id UUID REFERENCES review_sessions(id) ON DELETE CASCADE;

-- Enable RLS on review_sessions
ALTER TABLE review_sessions ENABLE ROW LEVEL SECURITY;

-- Add RLS policies for review_sessions
CREATE POLICY "Users can view sessions for their projects"
    ON review_sessions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = review_sessions.project_id
            AND projects.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create sessions for their projects"
    ON review_sessions FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = review_sessions.project_id
            AND projects.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete sessions for their projects"
    ON review_sessions FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = review_sessions.project_id
            AND projects.user_id = auth.uid()
        )
    );

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_review_sessions_project_id ON review_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_code_reviews_session_id ON code_reviews(session_id);
