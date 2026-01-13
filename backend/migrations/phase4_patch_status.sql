-- Migration Patch: Add status column to review_sessions
-- Run this if you already applied phase4_review_sessions.sql before the update.

ALTER TABLE review_sessions ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'completed';
