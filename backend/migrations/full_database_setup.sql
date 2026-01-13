-- ========================================================
-- InteGrow Consolidated Database Setup
-- This script contains the base schema and all migrations.
-- Run this in your Supabase SQL Editor.
-- ========================================================

-- 1. BASE EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. BASE TABLES (from schema.sql)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    github_id TEXT UNIQUE NOT NULL,
    github_username TEXT NOT NULL,
    email TEXT,
    avatar_url TEXT,
    access_token_encrypted TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    local_path TEXT NOT NULL,
    github_repo_url TEXT NOT NULL,
    github_repo_id TEXT,
    default_branch TEXT DEFAULT 'main',
    visibility TEXT CHECK (visibility IN ('public', 'private')),
    template TEXT,
    agent_config JSONB DEFAULT '{"auto_commit": true, "commit_frequency": "milestone", "branch_strategy": "gitflow"}'::jsonb,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS project_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. PHASE 1: REQUIREMENTS (from phase1_requirements.sql)
CREATE TABLE IF NOT EXISTS requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,
    raw_text TEXT NOT NULL,
    parsed_entities JSONB,
    ambiguity_analysis JSONB,
    completeness_analysis JSONB,
    ethics_analysis JSONB,
    overall_quality_score FLOAT,
    api_usage_log JSONB DEFAULT '{"groq": 0, "gemini": 0, "openai": 0, "cached": 0}'::jsonb,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'analyzing', 'refining', 'approved', 'archived')),
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS requirement_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID REFERENCES requirements(id) ON DELETE CASCADE,
    session_id TEXT UNIQUE NOT NULL,
    messages JSONB[] DEFAULT '{}',
    state JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID REFERENCES requirements(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    story TEXT NOT NULL,
    acceptance_criteria TEXT[],
    priority TEXT CHECK (priority IN ('high', 'medium', 'low')),
    status TEXT DEFAULT 'backlog' CHECK (status IN ('backlog', 'in_progress', 'done')),
    story_points INTEGER,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. PHASE 2: UML (from phase2_uml_diagrams.sql)
CREATE TABLE IF NOT EXISTS uml_diagrams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID REFERENCES requirements(id) ON DELETE CASCADE,
    project_id UUID NOT NULL,
    user_id UUID NOT NULL,
    diagram_type VARCHAR(50) DEFAULT 'class',
    plantuml_code TEXT NOT NULL,
    rendered_svg TEXT,
    analysis_metadata JSONB DEFAULT '{}'::jsonb,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. CODE GENERATION (from add_code_generation_tables.sql)
DO $$ BEGIN
    CREATE TYPE generation_status AS ENUM ('pending', 'generating', 'completed', 'approved', 'rejected', 'committed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS code_generation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
    commit_sha TEXT,
    commit_url TEXT,
    approved_at TIMESTAMPTZ,
    approved_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS generated_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES code_generation_sessions(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    content TEXT NOT NULL,
    file_type TEXT NOT NULL,
    language TEXT DEFAULT 'python',
    dependencies JSONB DEFAULT '[]'::jsonb,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. AUDIT LOGS (Missing Table)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    action TEXT NOT NULL,
    resource_id TEXT,
    details JSONB,
    ip_address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. SHARED FUNCTIONS & TRIGGERS
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_requirements_updated_at ON requirements;
CREATE TRIGGER update_requirements_updated_at BEFORE UPDATE ON requirements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_code_generation_sessions_modtime ON code_generation_sessions;
CREATE TRIGGER update_code_generation_sessions_modtime BEFORE UPDATE ON code_generation_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 8. SECURITY (RLS)
-- (Simplified for initial setup - ensure users can only see their own data)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_stories ENABLE ROW LEVEL SECURITY;
ALTER TABLE uml_diagrams ENABLE ROW LEVEL SECURITY;
ALTER TABLE code_generation_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
