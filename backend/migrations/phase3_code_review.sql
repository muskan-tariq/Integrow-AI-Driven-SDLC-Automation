-- Migration: Phase 3 Code Review
-- Description: Create tables for storing code reviews and issues.

-- Create table for code reviews
CREATE TABLE IF NOT EXISTS code_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed')),
    score INTEGER DEFAULT 0,
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create table for review issues
CREATE TABLE IF NOT EXISTS review_issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID REFERENCES code_reviews(id) ON DELETE CASCADE,
    line_number INTEGER,
    issue_type TEXT, -- bug, security, style, performance, logic
    severity TEXT, -- critical, high, medium, low
    description TEXT NOT NULL,
    suggested_fix TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE code_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE review_issues ENABLE ROW LEVEL SECURITY;

-- RLS Policies for code_reviews
CREATE POLICY "Users can view reviews for their projects"
    ON code_reviews FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = code_reviews.project_id
            AND projects.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create reviews for their projects"
    ON code_reviews FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = code_reviews.project_id
            AND projects.user_id = auth.uid()
        )
    );

-- RLS Policies for review_issues
CREATE POLICY "Users can view issues for their reviews"
    ON review_issues FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM code_reviews
            JOIN projects ON projects.id = code_reviews.project_id
            WHERE code_reviews.id = review_issues.review_id
            AND projects.user_id = auth.uid()
        )
    );

-- Trigger for updated_at
CREATE TRIGGER update_code_reviews_updated_at
    BEFORE UPDATE ON code_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
