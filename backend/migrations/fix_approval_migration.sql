-- Fix for "Key (approved_by) is not present in table users" error
-- This removes the strict foreign key constraint to allow storing the user ID 
-- even if the public.users table sync is delayed or permission denied.

ALTER TABLE code_generation_sessions 
DROP CONSTRAINT IF EXISTS code_generation_sessions_approved_by_fkey;
