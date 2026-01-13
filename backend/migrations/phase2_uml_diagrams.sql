-- ============================================
-- Phase 2: UML Class Diagram Generation
-- Migration: Create uml_diagrams table
-- ============================================

-- Create uml_diagrams table
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

-- Enable Row Level Security
ALTER TABLE uml_diagrams ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can view their own diagrams
CREATE POLICY "Users can view their own diagrams"
    ON uml_diagrams FOR SELECT
    USING (auth.uid() = user_id);

-- RLS Policy: Users can create diagrams for their projects
CREATE POLICY "Users can create diagrams for their projects"
    ON uml_diagrams FOR INSERT
    WITH CHECK (
        auth.uid() = user_id AND
        EXISTS (
            SELECT 1 FROM projects 
            WHERE id = project_id AND user_id = auth.uid()
        )
    );

-- RLS Policy: Users can update their own diagrams
CREATE POLICY "Users can update their own diagrams"
    ON uml_diagrams FOR UPDATE
    USING (auth.uid() = user_id);

-- RLS Policy: Users can delete their own diagrams
CREATE POLICY "Users can delete their own diagrams"
    ON uml_diagrams FOR DELETE
    USING (auth.uid() = user_id);

-- Indexes for performance
CREATE INDEX idx_uml_diagrams_requirement ON uml_diagrams(requirement_id);
CREATE INDEX idx_uml_diagrams_project ON uml_diagrams(project_id);
CREATE INDEX idx_uml_diagrams_user ON uml_diagrams(user_id);
CREATE INDEX idx_uml_diagrams_created ON uml_diagrams(created_at DESC);
CREATE INDEX idx_uml_diagrams_type ON uml_diagrams(diagram_type);

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_uml_diagrams_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER trigger_update_uml_diagrams_updated_at
    BEFORE UPDATE ON uml_diagrams
    FOR EACH ROW
    EXECUTE FUNCTION update_uml_diagrams_updated_at();

-- Comments for documentation
COMMENT ON TABLE uml_diagrams IS 'Stores UML class diagrams generated from user stories';
COMMENT ON COLUMN uml_diagrams.requirement_id IS 'Foreign key to requirements table';
COMMENT ON COLUMN uml_diagrams.diagram_type IS 'Type of UML diagram (class, sequence, use_case, etc.)';
COMMENT ON COLUMN uml_diagrams.plantuml_code IS 'PlantUML source code for the diagram';
COMMENT ON COLUMN uml_diagrams.rendered_svg IS 'Cached SVG rendering of the diagram';
COMMENT ON COLUMN uml_diagrams.analysis_metadata IS 'Metadata from diagram analysis (entities, relationships, etc.)';
COMMENT ON COLUMN uml_diagrams.version IS 'Version number for diagram history';
