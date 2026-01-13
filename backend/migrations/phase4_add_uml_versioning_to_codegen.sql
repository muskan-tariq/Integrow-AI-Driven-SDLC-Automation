-- Migration: Add uml_diagram_id to code_generation_sessions
-- Description: Link code generation sessions to specific UML diagram versions.

ALTER TABLE code_generation_sessions
ADD COLUMN IF NOT EXISTS uml_diagram_id UUID REFERENCES uml_diagrams(id) ON DELETE SET NULL;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_code_gen_sessions_uml_diagram_id ON code_generation_sessions(uml_diagram_id);
