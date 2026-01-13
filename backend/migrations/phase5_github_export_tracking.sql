-- Migration: Add GitHub Export Tracking to Review Sessions
-- Adds fields to track GitHub export status for both sessions and individual reviews

-- Add GitHub export fields to review_sessions
ALTER TABLE review_sessions ADD COLUMN IF NOT EXISTS github_exported BOOLEAN DEFAULT FALSE;
ALTER TABLE review_sessions ADD COLUMN IF NOT EXISTS github_commit_sha TEXT;
ALTER TABLE review_sessions ADD COLUMN IF NOT EXISTS github_exported_at TIMESTAMPTZ;

-- Add GitHub export fields to code_reviews (for individual file exports)
ALTER TABLE code_reviews ADD COLUMN IF NOT EXISTS github_exported BOOLEAN DEFAULT FALSE;
ALTER TABLE code_reviews ADD COLUMN IF NOT EXISTS github_commit_sha TEXT;
ALTER TABLE code_reviews ADD COLUMN IF NOT EXISTS github_exported_at TIMESTAMPTZ;

-- Create index for faster queries on exported status
CREATE INDEX IF NOT EXISTS idx_review_sessions_github_exported ON review_sessions(github_exported);
CREATE INDEX IF NOT EXISTS idx_code_reviews_github_exported ON code_reviews(github_exported);
