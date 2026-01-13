# UML Class Diagram Generation - Implementation Roadmap

## 🎯 Project Goal
Generate UML Class Diagrams from approved User Stories using AI (Groq/Gemini LLM) and PlantUML rendering.

## 🏗️ Architecture Decision
- **Diagram Type**: Class Diagram only (Phase 2 focus)
- **AI Provider**: Groq API (llama-3.3-70b-versatile) with Gemini fallback
- **Rendering Engine**: PlantUML (server-side + client-side)
- **Output Formats**: SVG, PNG, PlantUML code (editable)

---

## 📋 Implementation Phases

### **Phase 1: Backend Foundation** (Days 1-3)

#### Day 1: Agent & Service Setup ✅
- [x] **1.1** Create UML agents module structure
  ```
  backend/agents/uml/
  ├── __init__.py
  ├── diagram_analyzer.py
  └── class_diagram_agent.py
  ```

- [x] **1.2** Implement `DiagramAnalyzer`
  - Extract entities (nouns) from user stories
  - Identify relationships between entities
  - Extract methods (verbs/actions) from acceptance criteria
  - Map story elements to UML components

- [x] **1.3** Create `PlantUMLService`
  ```
  backend/services/plantuml_service.py
  ```
  - PlantUML code validation
  - SVG rendering via PlantUML server
  - PNG rendering (optional)
  - Local PlantUML jar integration (offline mode)

- [x] **1.4** Update package dependencies
  ```bash
  pip install plantuml httpx Pillow
  ```
  - [x] Tests created and passing (30/30 ✅)

#### Day 2: Database & Pydantic Models ✅
- [x] **2.1** Implement `ClassDiagramAgent` (DONE in Day 1)
  - Design LLM prompt for class diagram generation
  - Parse user stories + analysis results
  - Generate PlantUML syntax via Groq API
  - Validate generated PlantUML code
  - Handle LLM errors and retries

- [x] **2.2** Create prompt engineering template
  ```python
  """
  Given user stories, generate PlantUML class diagram including:
  - Classes with meaningful names
  - Attributes (from entities)
  - Methods (from actions/verbs)
  - Relationships (associations, compositions, inheritance)
  - Multiplicities (1, *, 0..1, etc.)
  """
  ```

- [x] **2.3** Add Gemini fallback mechanism
  - Try Groq first (faster, cheaper)
  - Fall back to Gemini if Groq fails
  - Return basic diagram if both fail

#### Day 3: Workflow & Database Migration ✅
- [x] **3.1** Create database migration
  ```sql
  -- migrations/phase2_uml_diagrams.sql
  CREATE TABLE uml_diagrams (
    id UUID PRIMARY KEY,
    requirement_id UUID REFERENCES requirements(id),
    project_id UUID,
    user_id UUID,
    diagram_type VARCHAR(50) DEFAULT 'class',
    plantuml_code TEXT NOT NULL,
    rendered_svg TEXT,
    metadata JSONB,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
  );
  ```

- [ ] **3.2** Run migration in Supabase SQL Editor (MANUAL STEP)

- [x] **3.3** Create `UMLWorkflow` orchestrator
  ```
  backend/workflows/uml_workflow.py
  ```
  - Coordinate DiagramAnalyzer → ClassDiagramAgent → PlantUMLService
  - Handle errors gracefully
  - Return structured result

- [x] **3.4** Add Pydantic models
  ```
  backend/models/uml_diagram.py
  ```
  - `UMLDiagramCreate`
  - `UMLDiagramResponse`
  - `DiagramAnalysisResult`
  - [x] Tests created and passing (9/9 ✅)

---

### **Phase 2: API Development** (Days 4-5)

#### Day 4: API Endpoints ✅
- [x] **4.1** Create UML router
  ```
  backend/api/uml_router.py
  ```

- [x] **4.2** Implement endpoints (6 total):

  **Generate Class Diagram** ✅
  ```python
  POST /api/projects/{project_id}/requirements/{req_id}/uml/generate
  ```

  **Get Diagram** ✅
  ```python
  GET /api/uml/{diagram_id}
  ```

  **Render Diagram** ✅
  ```python
  GET /api/uml/{diagram_id}/render?format=svg
  ```

  **Update Diagram Code** ✅
  ```python
  PUT /api/uml/{diagram_id}
  ```

  **List Diagrams for Requirement** ✅
  ```python
  GET /api/projects/{project_id}/requirements/{req_id}/uml
  ```

  **Delete Diagram** ✅
  ```python
  DELETE /api/uml/{diagram_id}
  ```

- [x] **4.3** Add authentication & authorization
  - User must own the project
  - RLS policies for uml_diagrams table (completed in migration)

#### Day 5: Testing & Optimization ✅
- [x] **5.1** Write unit tests
  ```
  backend/tests/unit/test_diagram_analyzer.py (8 tests)
  backend/tests/unit/test_class_diagram_agent.py (8 tests)
  backend/tests/unit/test_plantuml_service.py (14 tests)
  backend/tests/unit/test_uml_workflow.py (9 tests)
  ```
  - ✅ All 39 tests passing

- [x] **5.2** API Integration verification
  - ✅ Server starts successfully with UML router
  - ✅ 6 endpoints registered and accessible
  - ✅ No import or initialization errors

- [x] **5.3** Test with sample user stories
  - ✅ Tested with 2-3 story samples (simple)
  - ✅ Tested with 5+ story samples (medium)
  - ✅ Complex scenarios with multiple entities

- [x] **5.4** Performance optimization
  - ✅ Async/await throughout workflow
  - ✅ SVG caching in database (rendered_svg column)
  - ✅ Efficient PlantUML encoding algorithm
  - ✅ Proper error handling and timeouts

---

## 🎉 **Backend Complete - Days 1-5** ✅

**Summary:**
- ✅ 4 Agent classes (DiagramAnalyzer, ClassDiagramAgent + workflow)
- ✅ 1 Service class (PlantUMLService)
- ✅ 6 API endpoints (REST)
- ✅ 1 Database table with RLS policies
- ✅ 4 Pydantic models
- ✅ 39 unit tests passing (100%)
- ✅ Coverage: 75-98% for UML modules

**Ready for Phase 3: Frontend Development** 🚀

---

### **Phase 3: Frontend Development** (Days 6-9)

#### Day 6: UML Page Setup ✅
- [x] **6.1** Create UML page route
  ```
  frontend/renderer/app/project/[id]/requirements/[reqId]/uml/page.tsx
  ```

- [x] **6.2** Install dependencies
  ```bash
  npm install @monaco-editor/react @radix-ui/react-toast class-variance-authority --legacy-peer-deps
  ```

- [x] **6.3** Create API client methods (integrated in page.tsx)
  ```typescript
  // Direct fetch API calls with:
  - generateClassDiagram(projectId, reqId, options)
  - getUMLDiagram(diagramId)
  - updateDiagramCode(diagramId, code)
  - renderDiagram(diagramId, format)
  ```

- [x] **6.4** Setup state management
  - Local state for diagram, loading, editing modes
  - Toast notifications for errors/success (shadcn/ui toast)
  - Navigation integration from User Stories List

#### Day 7: UI Components ✅
- [x] **7.1** Create `DiagramViewer` component
  ```tsx
  components/uml/DiagramViewer.tsx
  ```
  - Display SVG diagram
  - Zoom in/out controls (50-200%)
  - Reset zoom functionality
  - Fullscreen mode

- [x] **7.2** Create `PlantUMLEditor` component
  ```tsx
  components/uml/PlantUMLEditor.tsx
  ```
  - Monaco Editor with PlantUML syntax
  - Save/Cancel actions
  - Auto-focus on mount
  - Line numbers and minimap

- [x] **7.3** Create `DiagramControls` component (integrated in page.tsx)
  - Generate button (with loading state)
  - Edit/Preview toggle
  - Export options (SVG, PNG, Code)
  - Regenerate button
  - Back navigation

- [x] **7.4** Create `ExportDialog` component
  ```tsx
  components/uml/ExportDialog.tsx
  ```
  - Download SVG
  - Download PNG
  - Download PlantUML code (.puml)
  - Descriptive format options

#### Day 8: Main Page Implementation ✅
- [x] **8.1** Build UML page layout
  - Responsive grid layout with header and content sections
  - DiagramControls integrated in header
  - Conditional rendering: Loading → Error → Empty → Editor/Viewer

- [x] **8.2** Implement generation flow
  - Loading skeleton during generation
  - Toast notifications for success/errors
  - Auto-fetch and display diagram after generation
  - Graceful error handling with retry button

- [x] **8.3** Implement editing flow
  - Load PlantUML code into Monaco editor
  - Save functionality with Ctrl+S shortcut
  - Preview changes before saving
  - Cancel editing with Escape key

- [x] **8.4** Add navigation
  - Back button to requirements page
  - Breadcrumb in header
  - Link from User Stories List (UML button)

#### Day 9: Polish & UX ✅
- [x] **9.1** Add loading states
  - Skeleton loader for diagram (3-part layout)
  - Progress indicator for generation
  - Spinner for actions

- [x] **9.2** Error handling
  - Network errors with retry
  - LLM generation failures with descriptive messages
  - 404 handling (no diagrams)
  - User-friendly error messages

- [x] **9.3** Add empty states
  - No diagram generated yet (with CTA)
  - Clear call-to-action buttons
  - Helpful messages

- [x] **9.4** Responsive design
  - Mobile-friendly viewer
  - Zoom/pan controls
  - Touch-friendly buttons

- [x] **9.5** Add help & documentation
  - Tooltip with keyboard shortcuts (Ctrl+S, Ctrl+E, Esc)
  - Help icon in header
  - Pan instructions in viewer

---

## 🎉 **Phase 3 Complete - Days 6-9** ✅

**Summary:**
- ✅ 4 Feature components (Page, DiagramViewer, PlantUMLEditor, ExportDialog)
- ✅ 5 UI system components (Toast, Skeleton, Tooltip, Toaster, use-toast)
- ✅ Navigation integration from User Stories
- ✅ Keyboard shortcuts (Ctrl+S, Ctrl+E, Esc)
- ✅ Pan & zoom functionality
- ✅ Export to SVG/PNG/PlantUML
- ✅ Error handling & loading states
- ✅ Zero TypeScript errors
- ✅ 1,161 lines of production code

**Total Frontend Development**: 75% Complete (9/12 days)

**Ready for Phase 4: Integration & Refinement** 🚀

---

### **Phase 4: Integration & Refinement** (Days 10-12)

#### Day 10: Workflow Integration
- [ ] **10.1** Add UML generation trigger
  - Button on Requirements Analyzer page
  - Auto-generate after user story approval (optional)
  - Batch generation for multiple requirements

- [ ] **10.2** Link diagrams to user stories
  - Highlight which stories contributed to each class
  - Click class to see related stories
  - Traceability matrix

- [ ] **10.3** Add versioning
  - Save each regeneration as new version
  - Version history viewer
  - Compare versions side-by-side
  - Restore previous version

#### Day 11: Prompt Engineering & Quality
- [ ] **11.1** Improve prompt engineering
  - Test with various user story complexities
  - Add domain-specific templates
  - Handle edge cases (no clear entities, too many classes)

- [ ] **11.2** Add quality checks
  - Validate PlantUML syntax before saving
  - Check for common mistakes (missing relationships, isolated classes)
  - Automated validation feedback

- [ ] **11.3** Optimization & Polish
  - Performance tuning for large diagrams
  - Caching improvements
  - UI/UX refinements

#### Day 12: Testing & Documentation
- [ ] **12.1** End-to-end testing
  - Create requirement → Generate stories → Generate UML
  - Edit diagram → Save → Export
  - Multiple users, projects, requirements

- [ ] **12.2** Performance testing
  - Large diagrams (20+ classes)
  - Concurrent generation requests
  - Response time optimization

- [ ] **12.3** Update documentation
  - User guide for UML generation
  - API documentation
  - Architecture diagram
  - Update README.md

- [ ] **12.4** Create demo video
  - Record UML generation workflow
  - Show editing capabilities
  - Export examples

---

## 🔧 Technical Implementation Details

### **Prompt Engineering for Class Diagrams**

```python
CLASS_DIAGRAM_PROMPT = """
You are a UML expert. Generate a PlantUML class diagram from the following user stories.

USER STORIES:
{user_stories}

IDENTIFIED ENTITIES:
{entities}

IDENTIFIED ACTIONS:
{actions}

INSTRUCTIONS:
1. Create classes for each main entity
2. Add relevant attributes (data fields)
3. Add methods based on actions/verbs
4. Define relationships:
   - Association (uses, has reference to)
   - Composition (has, contains - strong ownership)
   - Aggregation (contains - weak ownership)
   - Inheritance (is-a)
5. Add multiplicities (1, *, 0..1, 1..*)
6. Use meaningful class and method names
7. Follow UML naming conventions
8. Keep the diagram clean and readable

OUTPUT FORMAT:
Return ONLY valid PlantUML code starting with @startuml and ending with @enduml.
Do NOT include explanations, markdown, or code blocks.

EXAMPLE OUTPUT:
@startuml
class User {{
  -id: UUID
  -username: String
  -email: String
  +login(): Boolean
  +logout(): void
}}

class Project {{
  -id: UUID
  -name: String
  -description: String
  +create(): Project
  +update(): void
}}

User "1" -- "*" Project : owns >
@enduml
"""
```

### **PlantUML Rendering Options**

```python
# Option 1: Public PlantUML Server (Simple, requires internet)
PLANTUML_SERVER = "http://www.plantuml.com/plantuml/svg/"

# Option 2: Local PlantUML JAR (Offline, requires Java)
PLANTUML_JAR = "/path/to/plantuml.jar"

# Option 3: Docker Container (Isolated, consistent)
PLANTUML_DOCKER = "plantuml/plantuml-server"
```

### **Database Schema Details**

```sql
-- RLS Policies
ALTER TABLE uml_diagrams ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own diagrams"
  ON uml_diagrams FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create diagrams for their projects"
  ON uml_diagrams FOR INSERT
  WITH CHECK (
    auth.uid() = user_id AND
    EXISTS (
      SELECT 1 FROM projects 
      WHERE id = project_id AND user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update their own diagrams"
  ON uml_diagrams FOR UPDATE
  USING (auth.uid() = user_id);

-- Indexes for performance
CREATE INDEX idx_uml_diagrams_requirement ON uml_diagrams(requirement_id);
CREATE INDEX idx_uml_diagrams_project ON uml_diagrams(project_id);
CREATE INDEX idx_uml_diagrams_created ON uml_diagrams(created_at DESC);
```

---

## 🎯 Success Criteria

### **Functional Requirements**
- ✅ Generate class diagram from user stories with >80% accuracy
- ✅ Render PlantUML to SVG within 3 seconds
- ✅ Allow manual editing of PlantUML code
- ✅ Export diagram as SVG, PNG, and code
- ✅ Version history for diagrams
- ✅ Mobile-responsive viewer

### **Technical Requirements**
- ✅ LLM generation success rate >90%
- ✅ PlantUML validation before saving
- ✅ Graceful fallback if Groq fails
- ✅ Cached rendering for repeat views
- ✅ Unit test coverage >80%
- ✅ API response time <2s (p95)

### **User Experience**
- ✅ Clear loading states during generation
- ✅ Helpful error messages
- ✅ Intuitive edit/preview toggle
- ✅ One-click export functionality
- ✅ Responsive design on all devices

---

## 📦 Deliverables

### **Backend**
- [ ] `agents/uml/` module with 2 agents
- [ ] `services/plantuml_service.py`
- [ ] `workflows/uml_workflow.py`
- [ ] `api/uml_router.py` with 5 endpoints
- [ ] `models/uml_diagram.py`
- [ ] Database migration script
- [ ] 15+ unit tests
- [ ] 5+ integration tests

### **Frontend**
- [ ] UML page at `/project/[id]/requirements/[reqId]/uml`
- [ ] 4 new components (Viewer, Editor, Controls, Export)
- [ ] API integration with React Query
- [ ] Export functionality (SVG, PNG, Code)
- [ ] Responsive design
- [ ] Loading/error states

### **Documentation**
- [ ] API documentation (Swagger)
- [ ] User guide with screenshots
- [ ] Architecture diagram
- [ ] Updated README.md
- [ ] Demo video

---

## 🚀 Quick Start Commands

### Backend
```bash
# Install dependencies
cd backend
.\integrow_env\Scripts\activate
pip install plantuml httpx Pillow

# Run migration
# Copy contents of migrations/phase2_uml_diagrams.sql to Supabase SQL Editor

# Run server
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Run tests
pytest tests/unit/test_class_diagram_agent.py -v
pytest tests/integration/test_uml_router.py -v
```

### Frontend
```bash
# Install dependencies
cd frontend
npm install plantuml-encoder react-svg @tanstack/react-query

# Run dev server
npm run electron:dev
```

---

## 📝 Notes & Considerations

### **AI Prompt Optimization**
- Test prompts with various story complexities
- Include examples in prompt for better results
- Use temperature=0.2 for consistent diagrams
- Add validation rules in prompt

### **PlantUML Limitations**
- Complex diagrams may be hard to read
- Manual layout adjustments might be needed
- SVG rendering can be slow for huge diagrams

### **Scalability**
- Cache rendered SVGs in database
- Consider CDN for serving static diagrams
- Implement pagination for diagram lists
- Rate limit LLM calls per user

### **Future Enhancements** (Post-Phase 2)
- Sequence diagrams
- Use case diagrams
- Activity diagrams
- Real-time collaborative editing
- AI-powered layout optimization
- Export to Draw.io format

---

**Estimated Timeline**: 12 working days  
**Priority**: High  
**Dependencies**: Requirements module (completed ✅)  
**Next Phase**: Sequence Diagram Generation (Phase 3)

---

*Last Updated: December 3, 2025*
