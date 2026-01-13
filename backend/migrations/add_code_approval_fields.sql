-- Migration: add_code_approval_fields
-- Adds approval tracking fields to code_generation_sessions table
-- Used to track when code is approved, who approved it, and the Git commit info

ALTER TABLE code_generation_sessions 
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS approved_by UUID REFERENCES auth.users(id),
ADD COLUMN IF NOT EXISTS commit_sha VARCHAR(40),
ADD COLUMN IF NOT EXISTS commit_url TEXT;

-- Add index for querying approved sessions
CREATE INDEX IF NOT EXISTS idx_code_sessions_approved 
ON code_generation_sessions(approved_at) 
WHERE approved_at IS NOT NULL;
