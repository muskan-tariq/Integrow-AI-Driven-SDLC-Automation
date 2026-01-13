-- Migration: Add Code Generation Tables
-- Description: Create tables for storing code generation sessions and generated files.

-- Create enum for generation status
CREATE TYPE generation_status AS ENUM (
    'pending',
    'generating',
    'completed',
    'approved',
    'rejected',
    'committed'
);

-- Create table for code generation sessions
CREATE TABLE IF NOT EXISTS code_generation_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    requirement_id UUID REFERENCES requirements(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status generation_status DEFAULT 'pending',
    tech_stack JSONB DEFAULT '{}'::jsonb,
    generation_scope TEXT[] DEFAULT ARRAY[]::TEXT[],
    total_files INTEGER DEFAULT 0,
    total_lines INTEGER DEFAULT 0,
    generation_time FLOAT DEFAULT 0.0,
    api_used JSONB DEFAULT '{}'::jsonb,
    committed_sha TEXT,
    committed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updating updated_at timestamp
CREATE TRIGGER update_code_generation_sessions_modtime
    BEFORE UPDATE ON code_generation_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create table for generated files
CREATE TABLE IF NOT EXISTS generated_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES code_generation_sessions(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    content TEXT NOT NULL,
    file_type TEXT NOT NULL,
    language TEXT DEFAULT 'python',
    dependencies JSONB DEFAULT '[]'::jsonb,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_code_gen_sessions_project_id ON code_generation_sessions(project_id);
CREATE INDEX idx_code_gen_sessions_requirement_id ON code_generation_sessions(requirement_id);
CREATE INDEX idx_generated_files_session_id ON generated_files(session_id);

-- Enable Row Level Security (RLS)
ALTER TABLE code_generation_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_files ENABLE ROW LEVEL SECURITY;

-- RLS Policies for code_generation_sessions
CREATE POLICY "Users can view sessions for their projects"
    ON code_generation_sessions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = code_generation_sessions.project_id
            AND projects.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create sessions for their projects"
    ON code_generation_sessions FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = code_generation_sessions.project_id
            AND projects.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their sessions"
    ON code_generation_sessions FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = code_generation_sessions.project_id
            AND projects.user_id = auth.uid()
        )
    );

-- RLS Policies for generated_files
CREATE POLICY "Users can view files for their sessions"
    ON generated_files FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM code_generation_sessions
            JOIN projects ON projects.id = code_generation_sessions.project_id
            WHERE code_generation_sessions.id = generated_files.session_id
            AND projects.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert files for their sessions"
    ON generated_files FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM code_generation_sessions
            JOIN projects ON projects.id = code_generation_sessions.project_id
            WHERE code_generation_sessions.id = generated_files.session_id
            AND projects.user_id = auth.uid()
        )
    );
