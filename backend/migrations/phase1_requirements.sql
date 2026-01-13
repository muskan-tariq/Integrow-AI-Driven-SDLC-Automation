-- Phase 1 Requirements Database Migration
-- Creates tables for requirements analysis, conversations, issues, and user stories

-- Requirements table
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

-- Create indexes for requirements table
CREATE INDEX IF NOT EXISTS idx_requirements_project_id ON requirements(project_id);
CREATE INDEX IF NOT EXISTS idx_requirements_status ON requirements(status);
CREATE INDEX IF NOT EXISTS idx_requirements_version ON requirements(project_id, version);
CREATE INDEX IF NOT EXISTS idx_requirements_created_by ON requirements(created_by);

-- Requirement conversations table (for chat state)
CREATE TABLE IF NOT EXISTS requirement_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID REFERENCES requirements(id) ON DELETE CASCADE,
    session_id TEXT UNIQUE NOT NULL,
    messages JSONB[] DEFAULT '{}',
    state JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for conversations table
CREATE INDEX IF NOT EXISTS idx_conversations_requirement_id ON requirement_conversations(requirement_id);
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON requirement_conversations(session_id);

-- Requirement issues table (for tracking analysis issues)
CREATE TABLE IF NOT EXISTS requirement_issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID REFERENCES requirements(id) ON DELETE CASCADE,
    issue_type TEXT CHECK (issue_type IN ('ambiguity', 'completeness', 'ethics')),
    severity TEXT CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    category TEXT,
    description TEXT NOT NULL,
    location_start INTEGER,
    location_end INTEGER,
    suggestions TEXT[],
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'ignored')),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for issues table
CREATE INDEX IF NOT EXISTS idx_issues_requirement_id ON requirement_issues(requirement_id);
CREATE INDEX IF NOT EXISTS idx_issues_status ON requirement_issues(status);
CREATE INDEX IF NOT EXISTS idx_issues_type ON requirement_issues(issue_type);
CREATE INDEX IF NOT EXISTS idx_issues_severity ON requirement_issues(severity);

-- User stories table (for generated user stories)
CREATE TABLE IF NOT EXISTS user_stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID REFERENCES requirements(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    story TEXT NOT NULL, -- "As a [user], I want [goal], so that [benefit]"
    acceptance_criteria TEXT[],
    priority TEXT CHECK (priority IN ('high', 'medium', 'low')),
    status TEXT DEFAULT 'backlog' CHECK (status IN ('backlog', 'in_progress', 'done')),
    story_points INTEGER,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for user stories table
CREATE INDEX IF NOT EXISTS idx_user_stories_requirement_id ON user_stories(requirement_id);
CREATE INDEX IF NOT EXISTS idx_user_stories_priority ON user_stories(priority);
CREATE INDEX IF NOT EXISTS idx_user_stories_status ON user_stories(status);

-- Row Level Security (RLS) Policies

-- Enable RLS on all tables
ALTER TABLE requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE requirement_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE requirement_issues ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_stories ENABLE ROW LEVEL SECURITY;

-- Requirements RLS policies
CREATE POLICY "Users can view requirements from their projects" ON requirements
    FOR SELECT USING (
        project_id IN (
            SELECT id FROM projects WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert requirements to their projects" ON requirements
    FOR INSERT WITH CHECK (
        project_id IN (
            SELECT id FROM projects WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update requirements in their projects" ON requirements
    FOR UPDATE USING (
        project_id IN (
            SELECT id FROM projects WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete requirements from their projects" ON requirements
    FOR DELETE USING (
        project_id IN (
            SELECT id FROM projects WHERE user_id = auth.uid()
        )
    );

-- Requirement conversations RLS policies
CREATE POLICY "Users can view conversations for their requirements" ON requirement_conversations
    FOR SELECT USING (
        requirement_id IN (
            SELECT id FROM requirements WHERE project_id IN (
                SELECT id FROM projects WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can insert conversations for their requirements" ON requirement_conversations
    FOR INSERT WITH CHECK (
        requirement_id IN (
            SELECT id FROM requirements WHERE project_id IN (
                SELECT id FROM projects WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can update conversations for their requirements" ON requirement_conversations
    FOR UPDATE USING (
        requirement_id IN (
            SELECT id FROM requirements WHERE project_id IN (
                SELECT id FROM projects WHERE user_id = auth.uid()
            )
        )
    );

-- Requirement issues RLS policies
CREATE POLICY "Users can view issues for their requirements" ON requirement_issues
    FOR SELECT USING (
        requirement_id IN (
            SELECT id FROM requirements WHERE project_id IN (
                SELECT id FROM projects WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can insert issues for their requirements" ON requirement_issues
    FOR INSERT WITH CHECK (
        requirement_id IN (
            SELECT id FROM requirements WHERE project_id IN (
                SELECT id FROM projects WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can update issues for their requirements" ON requirement_issues
    FOR UPDATE USING (
        requirement_id IN (
            SELECT id FROM requirements WHERE project_id IN (
                SELECT id FROM projects WHERE user_id = auth.uid()
            )
        )
    );

-- User stories RLS policies
CREATE POLICY "Users can view user stories for their requirements" ON user_stories
    FOR SELECT USING (
        requirement_id IN (
            SELECT id FROM requirements WHERE project_id IN (
                SELECT id FROM projects WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can insert user stories for their requirements" ON user_stories
    FOR INSERT WITH CHECK (
        requirement_id IN (
            SELECT id FROM requirements WHERE project_id IN (
                SELECT id FROM projects WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can update user stories for their requirements" ON user_stories
    FOR UPDATE USING (
        requirement_id IN (
            SELECT id FROM requirements WHERE project_id IN (
                SELECT id FROM projects WHERE user_id = auth.uid()
            )
        )
    );

-- Add comments for documentation
COMMENT ON TABLE requirements IS 'Stores requirement text and analysis results';
COMMENT ON TABLE requirement_conversations IS 'Stores chat conversation state for requirement refinement';
COMMENT ON TABLE requirement_issues IS 'Stores individual issues found during analysis (ambiguity, completeness, ethics)';
COMMENT ON TABLE user_stories IS 'Stores generated user stories from requirements';

COMMENT ON COLUMN requirements.parsed_entities IS 'JSON containing extracted actors, actions, entities, constraints';
COMMENT ON COLUMN requirements.ambiguity_analysis IS 'JSON containing ambiguity detection results';
COMMENT ON COLUMN requirements.completeness_analysis IS 'JSON containing completeness check results';
COMMENT ON COLUMN requirements.ethics_analysis IS 'JSON containing ethics audit results';
COMMENT ON COLUMN requirements.api_usage_log IS 'JSON tracking API usage for cost monitoring';
COMMENT ON COLUMN requirement_conversations.messages IS 'Array of chat messages in JSON format';
COMMENT ON COLUMN requirement_conversations.state IS 'JSON containing conversation state and context';
COMMENT ON COLUMN requirement_issues.suggestions IS 'Array of suggested improvements for the issue';
COMMENT ON COLUMN user_stories.story IS 'User story in "As a [user], I want [goal], so that [benefit]" format';
COMMENT ON COLUMN user_stories.acceptance_criteria IS 'Array of Given-When-Then acceptance criteria';
