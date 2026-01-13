-- Migration: Phase 3 Add Versioning and Deletion
-- Description: Add version column to code_reviews and RLS policy for deletion.

-- Add version column to code_reviews
ALTER TABLE code_reviews ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;

-- Add RLS policy for deletion if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'code_reviews' 
        AND policyname = 'Users can delete reviews for their projects'
    ) THEN
        CREATE POLICY "Users can delete reviews for their projects"
            ON code_reviews FOR DELETE
            USING (
                EXISTS (
                    SELECT 1 FROM projects
                    WHERE projects.id = code_reviews.project_id
                    AND projects.user_id = auth.uid()
                )
            );
    END IF;
END $$;
