# InteGrow Phase 1: Requirements Analyzer Module
## Product Requirements Document (PRD)

**Version:** 1.1 (API-Based LLMs)  
**Date:** October 2025  
**Project:** InteGrow AI-SES Suite  
**Phase:** Phase 1 - Requirements Analyzer  
**Duration:** 3-4 weeks  
**Prerequisites:** Phase 0 completed ✅ (Auth, Project Creation, GitHub Integration)  
**Team:** Muskan Tariq, Amna Hassan, Shuja-uddin  
**Supervisor:** Dr. Muhammad Bilal, Ms. Fatima Gillani

---

## 1. Executive Summary

Phase 1 introduces the **Requirements Analyzer**, the first AI-powered module in InteGrow. This module transforms natural language requirements into structured, validated, and ethically-audited specifications using a multi-agent AI system powered by **free/affordable API-based LLMs**. It provides an interactive chat interface (similar to Cursor) for iterative refinement, ensuring requirements are clear, complete, and unbiased.

**Key Objectives:**
- Build multi-agent AI system using LangGraph for requirements analysis
- Integrate API-based LLMs (Groq, Gemini) instead of local models - **NO HEAVY DOWNLOADS**
- Implement Parser, Ambiguity Detector, Completeness Checker, and Ethics Auditor agents
- Create WebSocket-based chat interface for real-time refinement
- Enable export of structured requirements (JSON/YAML)
- Auto-commit refined requirements to GitHub repository

**Why API-Based LLMs?**
- ✅ **No Heavy Downloads**: No need for 10GB+ local models
- ✅ **Works on 8GB RAM**: Any modern laptop can run it
- ✅ **Free Tier Available**: Groq (14,400 req/day), Gemini (1,500 req/day)
- ✅ **Faster Development**: Start coding immediately
- ✅ **Only ~$12/month** for 100 users in production vs $150-400 for local GPU server

---

## 2. Goals & Success Metrics

### Primary Goals
1. **Automated Analysis**: Parse and analyze requirements with 90%+ accuracy
2. **Ambiguity Detection**: Flag vague terms (e.g., "fast", "secure", "user-friendly") with 85%+ recall
3. **Completeness Checking**: Identify missing edge cases and constraints
4. **Ethics Auditing**: Detect bias and privacy issues in requirements
5. **Interactive Refinement**: Enable chat-based iteration like Cursor IDE
6. **GitHub Integration**: Automatically commit approved requirements

### Success Metrics
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Requirement Parsing Accuracy | >90% | Manual review of entity extraction |
| Ambiguity Detection Recall | >85% | Test dataset with known ambiguous terms |
| Completeness Check Coverage | >80% | Comparison with manual checklist |
| Ethics Issue Detection | 100% of known issues | Test with biased requirement samples |
| Chat Response Time | <3 seconds | WebSocket latency measurement |
| User Satisfaction (Refinement) | >4/5 | Post-interaction survey |
| Auto-commit Success Rate | 100% | Successful commits / total attempts |
| API Uptime | >99% | Monitoring dashboard |
| API Cost (Dev Phase) | $0/month | Track free tier usage |

---

## 3. Problem Statement

### Current Challenges
1. **Manual Requirements Analysis**: Developers spend hours manually reviewing requirements for ambiguities
2. **Inconsistent Quality**: Requirements quality varies significantly between projects
3. **Hidden Biases**: Ethical issues in requirements often go undetected until production
4. **No Standardization**: Requirements are written in free-form text without structure
5. **Poor Traceability**: Difficult to track requirement changes and versions
6. **Fragmented Tools**: Separate tools for writing, analyzing, and versioning requirements
7. **Heavy Infrastructure**: Local LLM solutions require expensive GPU servers

### Solution Approach
InteGrow's Requirements Analyzer unifies these concerns by:
- Using **lightweight API-based AI agents** to automatically analyze requirements as they're written
- Providing real-time feedback on ambiguities, completeness, and ethics
- Enabling iterative refinement through conversational interface
- Generating structured output (user stories, acceptance criteria)
- Automatically versioning requirements in Git
- **Running on any laptop** without GPU requirements

---

## 4. User Stories

### 4.1 As a Product Manager
```
Story: Writing Initial Requirements
As a product manager,
I want to write requirements in natural language,
So that I can quickly capture ideas without worrying about formal structure.

Acceptance Criteria:
✓ I can access "Requirements" tab from project dashboard
✓ I see a rich text editor (Monaco Editor)
✓ I can type or paste requirements in plain English
✓ I can save draft requirements
✓ The system auto-saves every 30 seconds
✓ I see a character/word count
✓ I can switch between dark/light mode
✓ The app works on my 8GB RAM laptop without installing large models
```

### 4.2 As a Product Manager (Getting AI Analysis)
```
Story: Analyzing Requirements for Issues
As a product manager,
I want AI to analyze my requirements and highlight issues,
So that I can fix problems before development starts.

Acceptance Criteria:
✓ I can click "Analyze Requirements" button
✓ I see a loading state while AI processes (progress indicator)
✓ Analysis completes in <15 seconds (using fast Groq API)
✓ I see color-coded inline annotations:
  - Yellow: Ambiguous terms
  - Orange: Missing completeness
  - Red: Ethical concerns
✓ I can hover over annotations to see detailed explanations
✓ I see a summary panel with:
  - Total issues found
  - Breakdown by category
  - Severity scores
✓ I can filter annotations by type
✓ The analysis works even without local GPU
```

### 4.3 As a Product Manager (Refining via Chat)
```
Story: Interactive Refinement
As a product manager,
I want to chat with AI to refine my requirements,
So that I can iteratively improve quality like using Cursor IDE.

Acceptance Criteria:
✓ I see a chat sidebar next to the editor
✓ I can ask questions like:
  - "How can I make this requirement clearer?"
  - "What edge cases am I missing?"
  - "Is this requirement biased?"
✓ AI responds in <3 seconds (using Groq's fast API)
✓ AI provides specific, actionable suggestions
✓ I can click "Apply Suggestion" to update the requirement
✓ Chat history is preserved during the session
✓ I can start a new chat to reset context
✓ Chat supports markdown formatting in responses
✓ Streaming responses feel natural (like ChatGPT)
```

### 4.4 As a Product Manager (Exporting Structured Output)
```
Story: Generating User Stories
As a product manager,
I want to export requirements as structured user stories,
So that developers can easily implement them.

Acceptance Criteria:
✓ I can click "Generate User Stories"
✓ AI converts requirements into:
  - User story format: "As a [user], I want [goal], so that [benefit]"
  - Acceptance criteria (Given-When-Then)
  - Priority labels (High/Medium/Low)
✓ I can review generated stories
✓ I can edit individual stories
✓ I can export as:
  - JSON (for API integration)
  - YAML (for configuration)
  - Markdown (for documentation)
  - CSV (for spreadsheet tools)
✓ Export includes all metadata (priority, status, tags)
```

### 4.5 As a Product Manager (Version Control)
```
Story: Committing Requirements to GitHub
As a product manager,
I want approved requirements automatically committed to GitHub,
So that changes are tracked and the team stays in sync.

Acceptance Criteria:
✓ I can click "Approve Requirements"
✓ A confirmation modal appears with:
  - Summary of changes
  - Commit message preview (editable)
  - Target branch (default: main)
✓ On approval, InteGrow Agent commits to GitHub:
  - File: .integrow/requirements/requirements_v{X}.yaml
  - Commit message: "✅ Requirements v{X} approved by {user}"
  - Author: InteGrow Agent
✓ I receive confirmation with GitHub commit link
✓ Requirements version increments automatically
✓ Previous versions remain accessible
```

### 4.6 As a Developer
```
Story: Viewing Approved Requirements
As a developer,
I want to view approved requirements in the project,
So that I can implement features accurately.

Acceptance Criteria:
✓ I can access "Requirements" tab
✓ I see latest approved version by default
✓ I can switch between versions using dropdown
✓ I see a diff view comparing versions
✓ Each requirement shows:
  - User story format
  - Acceptance criteria
  - Priority and status
  - Analysis results (ambiguity score, completeness score)
✓ I can filter by priority/status
✓ I can search requirements
```

### 4.7 As an AI Agent
```
Story: Multi-Agent Requirements Analysis
As the Requirements Analyzer agent system,
I need to coordinate multiple specialized agents,
So that comprehensive analysis is performed efficiently.

Acceptance Criteria:
✓ I can orchestrate 5 agents via LangGraph:
  1. Parser Agent (local spaCy + HuggingFace API)
  2. Ambiguity Detector (Groq API - LLaMA 3.3 70B)
  3. Completeness Checker (Gemini API)
  4. Ethics Auditor (local AIF360 + OpenAI fallback)
  5. Orchestrator (coordinates all agents)
✓ I can run Parser Agent first (sequential)
✓ I can run Detection agents in parallel (concurrent)
✓ I can aggregate results from all agents
✓ I can maintain conversation state in Redis
✓ I can resume conversations after interruption
✓ I can handle API failures gracefully (automatic fallback)
✓ I can log all agent interactions for debugging
✓ I can cache common responses to save API costs
```

---

## 5. Functional Requirements

### 5.1 Backend - AI Agent System

#### 5.1.1 LangGraph Orchestration
**FR-B-001**: Multi-Agent Workflow
- Framework: LangGraph (from LangChain)
- Workflow Pattern: Sequential + Parallel execution
- State Management: Redis for conversation memory
- Error Handling: Retry logic with exponential backoff + API fallback
- Logging: Structured logs for each agent action
- **API Integration**: Groq, Gemini, HuggingFace, OpenAI (fallback)

**FR-B-002**: State Graph Definition
```python
# Workflow Structure
StateGraph:
  - parser_node: Parse raw text → extract entities (local spaCy + HF API)
  - ambiguity_node: Detect vague terms (Groq API - parallel)
  - completeness_node: Check missing constraints (Gemini API - parallel)
  - ethics_node: Audit for bias/privacy issues (local + OpenAI fallback - parallel)
  - aggregator_node: Combine results → final analysis
  - chat_handler_node: Handle user feedback → loop back (Groq streaming)
```

#### 5.1.2 Parser Agent
**FR-B-003**: Entity Extraction Agent
- **Purpose**: Extract structured information from natural language
- **Tools**:
  - spaCy 3.7+ with `en_core_web_sm` model (50MB, runs locally)
  - HuggingFace Inference API for BERT (`dslim/bert-base-NER`)
- **Input**: Raw requirement text
- **Output**:
  ```json
  {
    "actors": ["user", "admin", "system"],
    "actions": ["login", "register", "authenticate"],
    "entities": ["account", "password", "session"],
    "constraints": ["max 3 failed attempts", "timeout 30 minutes"],
    "dependencies": ["requires email verification"]
  }
  ```
- **Performance**: Process 1000 words in <2 seconds
- **Cost**: FREE (local spaCy + free HF API)

**FR-B-004**: Parser Implementation
```python
# agents/parser_agent.py
import spacy
from transformers import pipeline

class ParserAgent:
    def __init__(self):
        # Local lightweight model (50MB)
        self.nlp = spacy.load("en_core_web_sm")
        
        # HuggingFace API (free)
        self.ner_pipeline = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )
    
    async def parse(self, text: str) -> ParsedRequirements:
        # Step 1: spaCy for basic extraction (local, instant)
        doc = self.nlp(text)
        actors = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        
        # Step 2: HuggingFace for advanced NER (API, free)
        entities = self.ner_pipeline(text)
        
        # Step 3: Extract actions from verbs
        actions = [token.lemma_ for token in doc if token.pos_ == "VERB"]
        
        return ParsedRequirements(
            actors=actors,
            actions=actions,
            entities=entities,
            constraints=self._extract_constraints(doc)
        )
```

#### 5.1.3 Ambiguity Detector Agent
**FR-B-005**: Ambiguity Detection Agent
- **Purpose**: Flag vague, unclear, or ambiguous terms
- **Model**: Groq API with LLaMA 3.3 70B (500+ tokens/sec, 14,400 req/day free)
- **Technique**: Few-shot prompting with examples
- **Input**: Parsed requirements + raw text
- **Output**:
  ```json
  {
    "ambiguous_terms": [
      {
        "term": "fast response time",
        "location": { "start": 45, "end": 63 },
        "severity": "high",
        "explanation": "'fast' is subjective. Specify: <100ms, <1s, or <5s?",
        "suggestions": ["response time <100ms", "response time <1 second"]
      }
    ],
    "ambiguity_score": 0.65
  }
  ```
- **Cost**: FREE (under 14,400 req/day limit)

**FR-B-006**: Ambiguity Implementation
```python
# agents/ambiguity_agent.py
from groq import Groq
import os

class AmbiguityAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
    async def detect(self, text: str):
        prompt = f"""You are a requirements analyst. Identify ambiguous terms.

Examples of ambiguous terms:
- "fast" → needs timing (e.g., <100ms)
- "secure" → needs measures (e.g., TLS 1.3)
- "user-friendly" → subjective, needs criteria

Requirement: {text}

Output JSON only:
[{{"term": "...", "explanation": "...", "suggestions": ["..."]}}]
"""
        
        response = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        
        return self._parse_response(response.choices[0].message.content)
```

#### 5.1.4 Completeness Checker Agent
**FR-B-007**: Completeness Analysis Agent
- **Purpose**: Identify missing edge cases, error handling, constraints
- **Model**: Google Gemini 2.5 Flash API (free tier, fast)
- **Technique**: Template-based checking + LLM reasoning
- **Input**: Parsed requirements
- **Output**:
  ```json
  {
    "missing_items": [
      {
        "category": "error_handling",
        "description": "No handling specified for login failure",
        "severity": "high",
        "suggestion": "Specify behavior after 3 failed login attempts"
      },
      {
        "category": "edge_cases",
        "description": "No behavior defined for expired sessions",
        "severity": "medium",
        "suggestion": "Define session timeout duration and renewal policy"
      }
    ],
    "completeness_score": 0.72
  }
  ```
- **Cost**: FREE (under 1,500 req/day limit)

**FR-B-008**: Completeness Implementation
```python
# agents/completeness_agent.py
import google.generativeai as genai

class CompletenessAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    async def check(self, text: str, parsed_entities: dict):
        prompt = f"""Analyze requirement completeness.

Requirement: {text}
Parsed: actors={parsed_entities['actors']}, actions={parsed_entities['actions']}

Check for missing:
1. Error handling - What happens when things fail?
2. Edge cases - Boundary conditions?
3. Performance - Response time requirements?
4. Security - Authentication, authorization?

Output JSON only:
[{{"category": "...", "description": "...", "severity": "high|medium|low", "suggestion": "..."}}]
"""
        
        response = self.model.generate_content(prompt)
        return self._parse_response(response.text)
```

#### 5.1.5 Ethics Auditor Agent
**FR-B-009**: Ethics & Bias Detection Agent
- **Purpose**: Detect bias, discrimination, privacy violations
- **Tools**:
  - Local pattern matching (regex) for protected attributes
  - IBM AIF360 (local, free)
  - Microsoft Fairlearn (local, free)
  - OpenAI GPT-4o-mini API (fallback, $5 free credits)
- **Input**: Requirement text
- **Output**:
  ```json
  {
    "ethical_issues": [
      {
        "type": "bias",
        "category": "gender",
        "location": { "start": 120, "end": 135 },
        "description": "Requirement mentions gender-specific language",
        "severity": "critical",
        "recommendation": "Use gender-neutral terms"
      },
      {
        "type": "privacy",
        "category": "data_collection",
        "description": "No mention of user consent for data collection",
        "severity": "high",
        "recommendation": "Add explicit consent mechanism"
      }
    ],
    "ethics_score": 0.45
  }
  ```
- **Cost**: FREE (pattern matching + local AIF360, API only for complex cases)

**FR-B-010**: Ethics Implementation
```python
# agents/ethics_agent.py
from aif360.datasets import BinaryLabelDataset
import re

class EthicsAgent:
    def __init__(self):
        self.protected_attributes = [
            "gender", "race", "ethnicity", "age", "religion",
            "sexual orientation", "disability", "nationality"
        ]
        self.privacy_keywords = [
            "personal data", "tracking", "biometric", "location"
        ]
        # Optional OpenAI for nuanced analysis
        self.llm_enabled = os.getenv("OPENAI_API_KEY") is not None
    
    async def audit(self, text: str):
        issues = []
        
        # Local pattern matching (fast, free)
        for attr in self.protected_attributes:
            if re.search(rf'\b{attr}\b', text, re.IGNORECASE):
                issues.append({
                    "type": "bias",
                    "category": attr,
                    "description": f"Mentions protected attribute: {attr}",
                    "severity": "high"
                })
        
        # Privacy checks
        for keyword in self.privacy_keywords:
            if keyword in text.lower():
                issues.append({
                    "type": "privacy",
                    "description": f"Mentions: {keyword}",
                    "severity": "medium"
                })
        
        # Optional: LLM for complex validation
        if self.llm_enabled and len(issues) > 0:
            issues = await self._llm_validate(text, issues)
        
        return issues
```

#### 5.1.6 Orchestrator Agent
**FR-B-011**: Workflow Coordination
- **Purpose**: Manage agent execution and state transitions
- **Responsibilities**:
  - Route requests to appropriate agents
  - Aggregate results from parallel agents
  - Manage conversation state in Redis
  - Handle API failures (automatic fallback: Groq → Gemini → OpenAI)
  - Implement caching to minimize API costs
  - Decide when analysis is complete
  - Trigger auto-commit when approved

**FR-B-012**: State Management (Redis)
```python
# Conversation State Structure
{
  "session_id": "uuid",
  "project_id": "uuid",
  "requirement_id": "uuid",
  "raw_text": "original requirement text",
  "parsed_data": {...},
  "analysis_results": {
    "ambiguity": {...},
    "completeness": {...},
    "ethics": {...}
  },
  "chat_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "api_usage": {
    "groq_requests": 150,
    "gemini_requests": 50,
    "cached_responses": 30
  },
  "iteration": 3,
  "status": "refining",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

**FR-B-013**: API Fallback & Caching Service
```python
# services/llm_service.py
from groq import Groq
import google.generativeai as genai
from openai import OpenAI
import hashlib

class LLMService:
    def __init__(self):
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.gemini = genai.GenerativeModel('gemini-2.5-flash')
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        self.providers = ["groq", "gemini", "openai"]
        self.current_provider = 0
        
        # Redis for caching
        self.cache = redis.Redis.from_url(os.getenv("REDIS_URL"))
    
    async def complete(self, prompt: str, max_tokens: int = 1000):
        """Try providers in order with automatic fallback + caching"""
        
        # Check cache first
        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        cached = self.cache.get(f"llm:{cache_key}")
        if cached:
            return json.loads(cached)
        
        # Try each provider
        for attempt in range(len(self.providers)):
            provider = self.providers[self.current_provider]
            
            try:
                if provider == "groq":
                    result = await self._groq_complete(prompt, max_tokens)
                elif provider == "gemini":
                    result = await self._gemini_complete(prompt, max_tokens)
                elif provider == "openai":
                    result = await self._openai_complete(prompt, max_tokens)
                
                # Cache for 24 hours
                self.cache.setex(f"llm:{cache_key}", 86400, json.dumps(result))
                return result
                
            except Exception as e:
                logger.warning(f"{provider} failed: {e}, trying next provider")
                self.current_provider = (self.current_provider + 1) % len(self.providers)
                continue
        
        raise Exception("All LLM providers failed")
```

### 5.2 Backend - API Endpoints

#### 5.2.1 Requirements Management
**FR-B-014**: POST /api/requirements/analyze
```json
Request:
POST /api/requirements/analyze
Authorization: Bearer {jwt}
Content-Type: application/json

{
  "project_id": "uuid",
  "text": "User should be able to login with email and password. System must be secure and fast."
}

Response (200):
{
  "requirement_id": "uuid",
  "session_id": "uuid",
  "parsed": {
    "actors": ["user", "system"],
    "actions": ["login"],
    "entities": ["email", "password"]
  },
  "analysis": {
    "ambiguity": {
      "score": 0.65,
      "issues": [...]
    },
    "completeness": {
      "score": 0.72,
      "missing": [...]
    },
    "ethics": {
      "score": 0.90,
      "issues": []
    }
  },
  "overall_quality_score": 0.76,
  "api_used": {
    "parser": "local_spacy",
    "ambiguity": "groq",
    "completeness": "gemini",
    "ethics": "local"
  }
}

Error (400):
{
  "detail": "Requirement text cannot be empty"
}
```

**FR-B-015**: WS /api/requirements/chat/{session_id}
```
Purpose: Real-time chat for requirement refinement with streaming responses

WebSocket URL:
wss://localhost:8000/api/requirements/chat/{session_id}?token={jwt}

Client → Server:
{
  "type": "message",
  "content": "How can I make this clearer?"
}

Server → Client (streaming):
{"type": "chunk", "content": "To make"}
{"type": "chunk", "content": " the login"}
{"type": "chunk", "content": " requirement"}
{"type": "chunk", "content": " clearer,"}
...
{"type": "complete", "suggestions": [...], "updated_analysis": {...}}

API Used: Groq (for streaming speed)
```

**FR-B-016**: POST /api/requirements/apply-suggestion
```json
Request:
POST /api/requirements/apply-suggestion
Authorization: Bearer {jwt}

{
  "session_id": "uuid",
  "suggestion_id": "uuid",
  "approved": true
}

Response (200):
{
  "requirement_id": "uuid",
  "updated_text": "...",
  "new_analysis": {...}
}
```

**FR-B-017**: POST /api/requirements/export
```json
Request:
POST /api/requirements/export
Authorization: Bearer {jwt}

{
  "requirement_id": "uuid",
  "format": "user_stories",
  "output_format": "yaml"
}

Response (200):
{
  "format": "yaml",
  "content": "---\nuser_stories:\n  - story: As a user...\n",
  "download_url": "https://..."
}

Supported formats:
- "user_stories": Generate user story format
- "acceptance_criteria": Generate Given-When-Then
- "raw": Export as-is
- "structured": Export parsed JSON

Output formats:
- "json", "yaml", "markdown", "csv"

API Used: Groq (for user story generation)
```

**FR-B-018**: POST /api/requirements/approve
```json
Request:
POST /api/requirements/approve
Authorization: Bearer {jwt}

{
  "requirement_id": "uuid",
  "commit_message": "Requirements for authentication module",
  "branch": "main"
}

Response (200):
{
  "requirement_id": "uuid",
  "version": 2,
  "commit_sha": "abc123",
  "commit_url": "https://github.com/user/repo/commit/abc123",
  "file_path": ".integrow/requirements/requirements_v2.yaml"
}
```

**FR-B-019**: GET /api/requirements/{requirement_id}/history
```json
Request:
GET /api/requirements/{requirement_id}/history

Response (200):
{
  "requirement_id": "uuid",
  "versions": [
    {
      "version": 2,
      "status": "approved",
      "quality_score": 0.92,
      "approved_by": "uuid",
      "approved_at": "2025-10-10T12:00:00Z",
      "commit_sha": "abc123"
    },
    {
      "version": 1,
      "status": "draft",
      "quality_score": 0.76,
      "created_at": "2025-10-09T10:00:00Z"
    }
  ]
}
```

### 5.3 Backend - Database Schema (Supabase)

#### 5.3.1 Requirements Table
**FR-D-001**: requirements table
```sql
CREATE TABLE requirements (
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

CREATE INDEX idx_requirements_project_id ON requirements(project_id);
CREATE INDEX idx_requirements_status ON requirements(status);
CREATE INDEX idx_requirements_version ON requirements(project_id, version);
```

#### 5.3.2 Requirement Conversations Table
**FR-D-002**: requirement_conversations table
```sql
CREATE TABLE requirement_conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  requirement_id UUID REFERENCES requirements(id) ON DELETE CASCADE,
  session_id TEXT UNIQUE NOT NULL,
  messages JSONB[] DEFAULT '{}',
  state JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conversations_requirement_id ON requirement_conversations(requirement_id);
CREATE INDEX idx_conversations_session_id ON requirement_conversations(session_id);
```

#### 5.3.3 Requirement Issues Table
**FR-D-003**: requirement_issues table
```sql
CREATE TABLE requirement_issues (
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

CREATE INDEX idx_issues_requirement_id ON requirement_issues(requirement_id);
CREATE INDEX idx_issues_status ON requirement_issues(status);
```

#### 5.3.4 User Stories Table
**FR-D-004**: user_stories table
```sql
CREATE TABLE user_stories (
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

CREATE INDEX idx_user_stories_requirement_id ON user_stories(requirement_id);
CREATE INDEX idx_user_stories_priority ON user_stories(priority);
CREATE INDEX idx_user_stories_status ON user_stories(status);
```

### 5.4 Frontend - UI Components

#### 5.4.1 Requirements Editor
**FR-F-001**: Monaco Editor Integration
- Component: RequirementsEditor.tsx
- Features:
  - Syntax: Plain text mode
  - Theme: Dark/Light mode support
  - Auto-save: Every 30 seconds
  - Word count: Real-time display
  - Inline annotations: Color-coded highlights
  - Keyboard shortcuts:
    - Cmd/Ctrl+S: Save
    - Cmd/Ctrl+Enter: Analyze
    - Cmd/Ctrl+/: Toggle chat
- State management: React Query for auto-save

**FR-F-002**: Annotation System
```typescript
interface Annotation {
  id: string;
  type: 'ambiguity' | 'completeness' | 'ethics';
  severity: 'critical' | 'high' | 'medium' | 'low';
  range: { start: number; end: number };
  message: string;
  suggestions: string[];
}

// Visual representation:
// - Yellow underline: ambiguity
// - Orange underline: completeness
// - Red underline: ethics
// - Hover: Show tooltip with details
```

#### 5.4.2 Analysis Panel
**FR-F-003**: Analysis Results Display
- Component: AnalysisPanel.tsx
- Layout: Right sidebar (400px wide, collapsible)
- Sections:
  1. **Overview Card**:
     - Overall quality score (0-100)
     - Score breakdown (ambiguity, completeness, ethics)
     - Progress bar visualization
     - API usage indicator (shows which APIs were used)
  2. **Issues List**:
     - Filterable by type/severity
     - Sortable by severity
     - Click to jump to location in editor
  3. **Quick Actions**:
     - "Start Refining" (opens chat)
     - "Export as User Stories"
     - "Approve Requirements"

#### 5.4.3 Chat Interface
**FR-F-004**: Interactive Chat Sidebar
- Component: ChatSidebar.tsx
- Layout: Right sidebar (replaces analysis panel)
- Features:
  - Message history (scrollable)
  - Typing indicator while AI responds
  - Markdown rendering in AI responses
  - Code blocks with syntax highlighting
  - "Apply Suggestion" buttons inline
  - "Copy" button for messages
  - "Start New Chat" to reset context
  - **Streaming responses** (powered by Groq)
- WebSocket connection for real-time streaming
- Auto-scroll to latest message

**FR-F-005**: Chat Message Component
```typescript
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  suggestions?: Suggestion[];
  timestamp: string;
  streaming?: boolean; // For partial responses
}

interface Suggestion {
  id: string;
  type: 'replacement' | 'addition';
  original?: string;
  suggested: string;
  applied: boolean;
}
```

#### 5.4.4 Export Modal
**FR-F-006**: Export Options Dialog
- Component: ExportModal.tsx
- Options:
  - Format: User Stories / Acceptance Criteria / Raw / Structured
  - Output: JSON / YAML / Markdown / CSV
  - Include: Analysis results (checkbox)
  - Preview: Show generated output before download
- Actions: Download / Copy to Clipboard / Cancel

#### 5.4.5 Approval Flow
**FR-F-007**: Requirements Approval Modal
- Component: ApprovalModal.tsx
- Display:
  - Quality score summary
  - Resolved vs open issues count
  - Warning if quality score <80%
- Inputs:
  - Commit message (editable)
  - Target branch (dropdown: main, develop)
- Preview:
  - Show file structure that will be committed
  - Show commit message
- Actions: Approve & Commit / Cancel

### 5.5 API Configuration & Setup

#### 5.5.1 API Keys Setup Guide
**FR-AI-001**: Getting Free API Keys

**Groq (Primary - Fastest)**
1. Go to: https://console.groq.com/
2. Sign up with Google/GitHub
3. Navigate to "API Keys"
4. Create API Key
5. Copy → Add to `.env` as `GROQ_API_KEY`
- **Free Tier**: 14,400 requests/day, 500 tokens/second
- **Models**: LLaMA 3.3 70B, Mixtral 8x7B

**Google Gemini (Secondary)**
1. Go to: https://makersuite.google.com/
2. Sign in with Google
3. Click "Get API Key"
4. Create new project
5. Copy → Add to `.env` as `GEMINI_API_KEY`
- **Free Tier**: 1,500 requests/day, 1M tokens/month
- **Model**: Gemini 2.5 Flash API (free tier, fast)

**HuggingFace (Optional - NER)**
1. Go to: https://huggingface.co/
2. Sign up
3. Settings → Access Tokens
4. Create "Read" token
5. Copy → Add to `.env` as `HUGGINGFACE_API_KEY`
- **Free Tier**: Unlimited (rate limited)

**OpenAI (Backup Only)**
1. Go to: https://platform.openai.com/
2. Sign up and add payment method
3. Get $5 free credits
4. Create API key
5. Copy → Add to `.env` as `OPENAI_API_KEY`
- **Free Credits**: $5 (covers ~33K requests)
- **Model**: GPT-4o-mini

#### 5.5.2 Environment Variables
```env
# .env.example (Phase 1 additions)

# Phase 0 variables (existing)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
REDIS_URL=redis://localhost:6379
GITHUB_TOKEN=ghp_xxx
JWT_SECRET=your_secret_key

# Phase 1: LLM API Keys
# Groq (Primary - FASTEST, 14,400 req/day free)
GROQ_API_KEY=gsk_xxx
# Get from: https://console.groq.com/keys

# Google Gemini (Secondary - 1500 req/day free)
GEMINI_API_KEY=AIzaSy_xxx
# Get from: https://makersuite.google.com/app/apikey

# HuggingFace (Optional - Free inference)
HUGGINGFACE_API_KEY=hf_xxx
# Get from: https://huggingface.co/settings/tokens

# OpenAI (Backup only - $5 free credits)
OPENAI_API_KEY=sk-xxx
# Get from: https://platform.openai.com/api-keys

# Feature Flags
USE_LOCAL_SPACY=true
ENABLE_CACHE=true
CACHE_TTL_HOURS=24
DEVELOPMENT_MODE=false  # Set to true for mock data
```

#### 5.5.3 Local Models (Lightweight Only)
```bash
# Install lightweight spaCy model (50MB instead of 500MB)
python -m spacy download en_core_web_sm

# NO Ollama needed!
# NO GPU drivers needed!
# Total download: ~500MB vs 10GB+ for local LLMs
```

---

## 6. Non-Functional Requirements

### 6.1 Performance
**NFR-P-001**: Analysis Speed
- Parser Agent: <2 seconds for 1000 words (local spaCy)
- Ambiguity Detection: <5 seconds (Groq API - 500 tok/sec)
- Completeness Check: <5 seconds (Gemini API)
- Ethics Audit: <3 seconds (local pattern matching)
- Total analysis time: <15 seconds for typical requirements (500 words)

**NFR-P-002**: Chat Response Time
- Initial response: <3 seconds (95th percentile) using Groq
- Streaming responses: First token <1 second
- Subsequent messages: <2 seconds (with context)

**NFR-P-003**: UI Responsiveness
- Editor typing lag: <50ms
- Annotation rendering: <200ms
- Auto-save: <1 second

**NFR-P-004**: API Caching
- Cache hit rate: >40% for similar requirements
- Cache storage: Redis with 24-hour TTL
- Reduces API costs by ~50%

### 6.2 Scalability
**NFR-S-001**: Concurrent Analysis
- Support 10 concurrent analyses per instance
- Queue additional requests using Celery
- Horizontal scaling: Add more backend instances
- API rate limiting handled automatically with fallback

**NFR-S-002**: API Usage Management
- Track API usage per user/project
- Alert when approaching free tier limits
- Automatic fallback: Groq → Gemini → OpenAI
- Smart caching to minimize API calls

**NFR-S-003**: Database Performance
- Supabase connection pooling (min 5, max 20 connections)
- Redis for caching frequent queries and API responses
- Index all foreign keys and frequently queried fields

### 6.3 Reliability
**NFR-R-001**: Error Handling
- All agent failures retry 3 times with exponential backoff
- API failures trigger automatic fallback to next provider
- Partial results returned if one agent fails (graceful degradation)
- User notified of any agent failures with actionable error messages

**NFR-R-002**: Data Persistence
- Auto-save draft requirements every 30 seconds
- Conversation state persists in Redis (24-hour TTL)
- All approved requirements backed up to GitHub
- API responses cached for 24 hours

**NFR-R-003**: Availability
- Backend uptime: 99.5%
- API provider redundancy (3 providers available)
- WebSocket reconnection logic in frontend
- Graceful degradation if all APIs fail

### 6.4 Security
**NFR-SE-001**: Data Privacy
- Requirements data encrypted at rest in Supabase
- WebSocket connections use WSS (encrypted)
- API keys stored securely (never exposed to frontend)
- No requirements data logged by API providers

**NFR-SE-002**: Access Control
- Users can only access their project's requirements
- Supabase RLS policies enforce project-level isolation
- API endpoints validate project ownership

**NFR-SE-003**: Input Validation
- Sanitize all user inputs to prevent injection
- Max requirement size: 50,000 characters
- Rate limiting: 100 analysis requests per hour per user

### 6.5 Cost Management
**NFR-CM-001**: API Cost Tracking
- Log all API calls (provider, tokens used, cost)
- Dashboard showing API usage and estimated costs
- Alert when 80% of free tier consumed
- Weekly usage reports for administrators

**NFR-CM-002**: Free Tier Optimization
- Target: $0/month during development
- Target: <$15/month for 100 active users in production
- Implement aggressive caching (24-hour TTL)
- Use local models where possible (Parser, Ethics)

### 6.6 Usability
**NFR-U-001**: Learning Curve
- First-time users complete analysis in <5 minutes
- Inline tooltips explain all features
- Sample requirements provided for testing
- No need to understand LLM configuration

**NFR-U-002**: Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation for all features
- Screen reader compatible
- High contrast mode available

**NFR-U-003**: Internationalization (Future)
- UI supports English (Phase 1)
- Architecture ready for i18n (use i18next)
- LLM prompts parameterized for future translation

---

## 7. Technical Architecture

### 7.1 System Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (Next.js/Electron)                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Requirements Tab                                     │   │
│  │  ┌──────────────────┐  ┌───────────────────────┐    │   │
│  │  │  Monaco Editor   │  │   Analysis Panel      │    │   │
│  │  │  - Auto-save     │  │   - Quality Score     │    │   │
│  │  │  - Annotations   │  │   - Issues List       │    │   │
│  │  │  - Word Count    │  │   - API Usage         │    │   │
│  │  └──────────────────┘  └───────────────────────┘    │   │
│  │                                                       │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │   Chat Sidebar (WebSocket - Groq Streaming)  │   │   │
│  │  │   - Message History                          │   │   │
│  │  │   - Streaming Responses (500 tok/s)         │   │   │
│  │  │   - Apply Suggestions                        │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                    HTTP/REST + WebSocket
                          │
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Routers                                         │   │
│  │  ┌────────────────┐  ┌──────────────────────────┐   │   │
│  │  │  Requirements  │  │    WebSocket Handler     │   │   │
│  │  │    Router      │  │   (Chat Streaming)       │   │   │
│  │  └────────────────┘  └──────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LangGraph Agent System                              │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │          Orchestrator Agent                  │   │   │
│  │  │  - API Fallback (Groq→Gemini→OpenAI)       │   │   │
│  │  │  - Response Caching (Redis)                 │   │   │
│  │  │  - Usage Tracking                           │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  │                                                       │   │
│  │  ┌───────────────┐  ┌──────────────────────────┐    │   │
│  │  │ Parser Agent  │  │   Ambiguity Detector     │    │   │
│  │  │ (Local spaCy  │  │   (Groq API - LLaMA 3.3) │    │   │
│  │  │  + HF API)    │  │   FREE: 14,400 req/day   │    │   │
│  │  └───────────────┘  └──────────────────────────┘    │   │
│  │                                                       │   │
│  │  ┌───────────────┐  ┌──────────────────────────┐    │   │
│  │  │ Completeness  │  │   Ethics Auditor         │    │   │
│  │  │ Checker       │  │   (Local AIF360          │    │   │
│  │  │ (Gemini API)  │  │    + OpenAI fallback)    │    │   │
│  │  │ FREE: 1,500/d │  │                          │    │   │
│  │  └───────────────┘  └──────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         │              │              │              │
    ┌────────┐    ┌─────────┐    ┌─────────┐   ┌──────────┐
    │Supabase│    │  Groq   │    │  Redis  │   │  GitHub  │
    │   DB   │    │ Gemini  │    │ (Cache) │   │   API    │
    │        │    │ OpenAI  │    │         │   │          │
    └────────┘    └─────────┘    └─────────┘   └──────────┘
```

### 7.2 Data Flow: Requirements Analysis
```
1. User types requirement in Monaco Editor
2. User clicks "Analyze Requirements"
3. Frontend → Backend: POST /api/requirements/analyze
4. Backend validates input
5. Backend → Supabase: Save draft requirement
6. Backend checks Redis cache (save API costs)
   ├─ Cache HIT → Return cached analysis (0 API calls)
   └─ Cache MISS → Continue to agents
7. Backend initiates LangGraph workflow:
   
   Step 1: Parser Agent (Sequential, Local + Free API)
   ├─→ spaCy (local): Extract entities (FREE, instant)
   ├─→ HuggingFace API: Advanced NER (FREE)
   └─→ Output: Parsed entities JSON
   
   Step 2-4: Parallel Agent Execution
   ┌─→ Ambiguity Detector (Groq API)
   │   ├─→ Try Groq LLaMA 3.3 70B (FREE, 500 tok/s)
   │   ├─→ Fallback: Gemini if rate limit
   │   └─→ Identify vague terms
   │
   ├─→ Completeness Checker (Gemini API)
   │   ├─→ Try Gemini 2.5 Flash (FREE, fast)
   │   ├─→ Fallback: Groq if rate limit
   │   └─→ Find missing items
   │
   └─→ Ethics Auditor (Local + API fallback)
       ├─→ Local regex patterns (FREE, instant)
       ├─→ Local AIF360 (FREE)
       └─→ Fallback: OpenAI for complex cases
   
   Step 5: Aggregator Agent
   └─→ Combine results → Calculate quality score

8. Backend → Redis: Cache analysis (24h TTL)
9. Backend → Supabase: Update requirement with analysis + API usage log
10. Backend → Frontend: Return analysis results + API providers used
11. Frontend renders annotations in editor
12. Frontend displays issues in analysis panel
13. Frontend shows API usage indicator (e.g., "Powered by Groq + Gemini")
```

### 7.3 Data Flow: Chat Refinement (Streaming)
```
1. User types message in chat: "How can I improve this?"
2. Frontend → Backend: WebSocket message
3. Backend retrieves conversation state from Redis
4. Backend checks cache for similar questions
   ├─ Cache HIT → Return cached response instantly
   └─ Cache MISS → Generate new response
5. Backend constructs LLM prompt:
   - System: "You are a requirements analyst..."
   - Context: Current requirement text
   - Context: Analysis results
   - History: Previous chat messages (last 4)
   - User message: "How can I improve this?"
6. Backend → Groq API: Stream completion request (LLaMA 3.3 70B)
7. Groq streams response tokens (500+ tokens/second)
8. Backend → Frontend: Stream tokens via WebSocket in real-time
   {"type": "chunk", "content": "To make"}
   {"type": "chunk", "content": " the login"}
   {"type": "chunk", "content": " requirement"}
   ...
9. Frontend displays streaming response in chat (like ChatGPT)
10. When complete:
    - Backend extracts suggestions from response
    - Backend → Redis: Cache conversation + response
    - If Groq fails → Fallback to Gemini → OpenAI
11. User clicks "Apply Suggestion"
12. Frontend updates editor content
13. Repeat analysis flow (with cache check)
```

### 7.4 API Cost Optimization Flow
```
┌─────────────────────────────────────────────┐
│         Request Arrives                      │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│   Step 1: Check Redis Cache                 │
│   - Hash requirement text                   │
│   - Lookup in Redis (TTL: 24h)             │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
    Cache HIT             Cache MISS
        │                       │
        ▼                       ▼
┌───────────────┐    ┌──────────────────────┐
│ Return Cached │    │ Proceed to Agents    │
│ 💰 Cost: $0   │    │                      │
└───────────────┘    └──────────────────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │ Step 2: Choose API       │
                │ - Try Groq first (fastest)│
                │ - Track usage counters   │
                └──────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
             SUCCESS    RATE LIMIT      ERROR
                │             │             │
                ▼             ▼             ▼
        ┌────────────┐ ┌────────────┐ ┌────────────┐
        │ Use Result │ │  Fallback  │ │  Fallback  │
        │ Cache it   │ │  to Gemini │ │  to OpenAI │
        └────────────┘ └────────────┘ └────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Log API Usage:   │
                    │ - Provider used  │
                    │ - Tokens consumed│
                    │ - Estimated cost │
                    └──────────────────┘
```

---

## 8. Dependencies & Prerequisites

### 8.1 Python Packages (Updated - Much Lighter!)
```txt
# requirements.txt (Phase 1 additions)

# Existing Phase 0 dependencies
fastapi==0.110.0
uvicorn[standard]==0.27.0
pydantic==2.6.0
pydantic-settings==2.1.0
supabase==2.3.0
redis==5.0.1

# LangChain (lighter without Ollama)
langchain==0.1.7
langgraph==0.0.25
langchain-openai==0.0.5
langchain-groq==0.1.0
langchain-google-genai==1.0.0

# NLP (lightweight local models)
spacy==3.7.2  # Will use small model (50MB)
transformers==4.37.2
torch==2.2.0  # Only for HuggingFace inference

# API Clients
groq==0.4.2
google-generativeai==0.3.2
openai==1.12.0

# Ethics (local)
aif360==0.5.0
fairlearn==0.10.0

# Utils
python-multipart==0.0.9
python-jose[cryptography]==3.3.0
httpx==0.26.0
websockets==12.0
pytest==8.0.0
pytest-asyncio==0.23.4
pytest-cov==4.1.0
black==24.1.1
ruff==0.2.1
```

### 8.2 Frontend Packages (Phase 1 additions)
```json
// package.json (Phase 1 additions to existing Phase 0)
{
  "dependencies": {
    // Existing Phase 0 dependencies
    "next": "15.0.3",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "typescript": "5.3.3",
    
    // Phase 1: Requirements Editor
    "@monaco-editor/react": "4.6.0",
    "@tanstack/react-query": "5.17.19",
    "axios": "1.6.5",
    "socket.io-client": "4.6.1",
    "zustand": "4.5.0",
    
    // Existing shadcn/ui components
    "@radix-ui/react-dialog": "1.0.5",
    "@radix-ui/react-select": "2.0.0",
    "@radix-ui/react-tooltip": "1.0.7",
    
    // Phase 1: Additional UI
    "react-markdown": "9.0.1",
    "remark-gfm": "4.0.0",
    "lucide-react": "0.312.0"
  },
  "devDependencies": {
    "@playwright/test": "1.41.0",
    "@testing-library/react": "14.1.2",
    "@testing-library/jest-dom": "6.2.0",
    "jest": "29.7.0"
  }
}
```

### 8.3 Hardware Requirements (Much Lighter!)

**Development Environment:**
- **CPU**: 2+ cores (any modern laptop)
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 5GB free space (vs 50GB for local LLMs)
- **GPU**: NOT REQUIRED ✅
- **Internet**: Required (but with caching, minimal impact)

**Production Environment:**
- **CPU**: 4+ cores per instance
- **RAM**: 16GB per instance
- **Storage**: 10GB
- **GPU**: NOT REQUIRED ✅
- **Network**: Stable internet connection (1 Mbps minimum)

**Cost Comparison:**
| | Local LLMs | API-Based |
|---|---|---|
| Initial Setup | $0 | $0 |
| Hardware | $150-400/mo GPU rental | $0 |
| Dev Phase | $0 API | $0 API (free tiers) |
| Prod (100 users) | $150-400/mo | $12/mo |
| **Total Savings** | - | **92% cheaper**

def test_gemini():
    """Test Gemini API connection"""
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Say 'test'")
        print("✅ Gemini API: Connected")
        print(f"   Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Gemini API: Failed - {e}")
        return False

if __name__ == "__main__":
    print("\n🔍 Testing API Connections...\n")
    groq_ok = test_groq()
    gemini_ok = test_gemini()
    
    if groq_ok and gemini_ok:
        print("\n✅ All APIs configured correctly!")
    else:
        print("\n⚠️  Some APIs failed. Check your keys.")
```

Run the test:
```bash
python tests/test_apis.py
```

---

## 10. Development Milestones

### Week 1: AI Agent Foundation
**Days 1-2: Setup & Parser Agent**
- [x] Install Phase 1 dependencies
- [x] Get free API keys (Groq, Gemini)
- [x] Test API connections
- [x] Download spaCy small model (50MB)
- [x] Create backend/agents/ directory structure
- [x] Implement ParserAgent class with spaCy
- [x] Integrate HuggingFace API for NER
- [x] Write unit tests for parser
- [x] Test entity extraction accuracy (target: >90%)

**Days 3-5: Detection Agents**
- [x] Implement AmbiguityAgent with Groq API
- [x] Create prompt templates for ambiguity detection
- [x] Test Groq streaming responses
- [x] Implement CompletenessAgent with Gemini API
- [x] Create completeness checklist templates
- [x] Implement EthicsAgent (local patterns + AIF360)
- [x] Write unit tests for all agents
- [x] Test detection accuracy on sample requirements

### Week 2: LangGraph Orchestration & API
**Days 6-8: Workflow Implementation**
- [x] Setup LangGraph state graph
- [x] Implement orchestrator agent
- [x] Setup Redis for conversation state
- [x] Implement parallel agent execution
- [x] Add API fallback logic (Groq → Gemini → OpenAI)
- [x] Implement response caching in Redis
- [x] Test workflow end-to-end
- [x] Add error handling and retries

**Days 9-10: REST API & Database**
- [x] Create Supabase tables (requirements, conversations, issues, user_stories)
- [x] Implement POST /api/requirements/analyze
- [x] Implement GET /api/requirements/{id}
- [x] Implement POST /api/requirements/export
- [x] Implement POST /api/requirements/approve
- [x] Add API usage logging
- [x] Write API integration tests
- [x] Test with Postman/Thunder Client

### Week 3: WebSocket Chat & Frontend
**Days 11-13: WebSocket Chat**
- [ ] Implement WebSocket handler in FastAPI
- [ ] Integrate Groq streaming API
- [ ] Implement suggestion extraction
- [ ] Test chat conversation flow
- [ ] Add conversation state management in Redis
- [ ] Test WebSocket reconnection logic
- [ ] Add chat history persistence

**Days 14-15: Frontend - Editor**
- [ ] Setup Monaco Editor component in Next.js
- [ ] Implement auto-save functionality
- [ ] Add word count display
- [ ] Implement annotation rendering system
- [ ] Add keyboard shortcuts (Ctrl+S, Ctrl+Enter)
- [ ] Style editor UI with Tailwind
- [ ] Test editor performance

### Week 4: Integration & Polish
**Days 16-18: Frontend - Panels**
- [ ] Build Analysis Panel component
- [ ] Add quality score visualization
- [ ] Build Chat Sidebar component
- [ ] Implement streaming message display
- [ ] Add "Apply Suggestion" buttons
- [ ] Implement Export Modal with preview
- [ ] Implement Approval Modal with GitHub commit
- [ ] Connect all components to backend API
- [ ] Add loading states and error handling

**Days 19-21: GitHub Integration & Testing**
- [ ] Implement auto-commit functionality
- [ ] Test GitHub Agent integration (.integrow/requirements/)
- [ ] Write E2E tests with Playwright
- [ ] Perform load testing (100 concurrent analyses)
- [ ] Test API fallback scenarios
- [ ] Monitor API usage and costs
- [ ] Fix bugs and optimize performance
- [ ] Document API endpoints (Swagger)
- [ ] Create user guide and video tutorial
- [ ] Prepare demo for Phase 1 review

---

## 11. Testing Strategy

### 11.1 Unit Tests

#### Backend Agent Tests
```python
# tests/test_parser_agent.py
import pytest
from agents.parser_agent import ParserAgent

@pytest.mark.asyncio
async def test_parser_extracts_actors():
    agent = ParserAgent()
    text = "User shall login with email and password"
    result = await agent.parse(text)
    
    assert "user" in result.actors
    assert "login" in result.actions
    assert "email" in result.entities
    assert "password" in result.entities

@pytest.mark.asyncio
async def test_parser_handles_empty_text():
    agent = ParserAgent()
    with pytest.raises(ValueError):
        await agent.parse("")
```

```python
# tests/test_ambiguity_agent.py
import pytest
from agents.ambiguity_agent import AmbiguityAgent

@pytest.mark.asyncio
async def test_detects_vague_terms():
    agent = AmbiguityAgent()
    text = "System must be fast and secure"
    result = await agent.detect_ambiguity(text)
    
    assert len(result.issues) >= 2
    assert any("fast" in issue.term.lower() for issue in result.issues)
    assert any("secure" in issue.term.lower() for issue in result.issues)
    assert result.score < 0.7  # Low score = high ambiguity

@pytest.mark.asyncio
async def test_api_fallback():
    """Test automatic fallback if Groq fails"""
    agent = AmbiguityAgent()
    # Simulate Groq failure by using invalid key
    agent.groq_client.api_key = "invalid"
    
    result = await agent.detect_ambiguity("System must be fast")
    # Should fallback to Gemini and still return results
    assert result is not None
```

#### API Cost Testing
```python
# tests/test_api_costs.py
import pytest
from services.llm_service import LLMService

@pytest.mark.asyncio
async def test_caching_reduces_costs():
    service = LLMService()
    
    # First call - hits API
    result1 = await service.complete("Test prompt", max_tokens=100)
    api_calls_1 = service.get_api_call_count()
    
    # Second call - should hit cache
    result2 = await service.complete("Test prompt", max_tokens=100)
    api_calls_2 = service.get_api_call_count()
    
    assert result1 == result2
    assert api_calls_2 == api_calls_1  # No additional API call
```

### 11.2 Integration Tests

```python
# tests/test_analysis_flow.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_end_to_end_analysis(client: AsyncClient, auth_token: str):
    # Step 1: Create requirement
    response = await client.post(
        "/api/requirements/analyze",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "project_id": "test-project-id",
            "text": "User should login fast"
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Step 2: Verify analysis results
    assert "requirement_id" in data
    assert data["analysis"]["ambiguity"]["score"] < 0.7
    assert len(data["analysis"]["ambiguity"]["issues"]) > 0
    
    # Step 3: Verify API usage logged
    assert "api_used" in data
    assert data["api_used"]["ambiguity"] in ["groq", "gemini"]
    
    # Step 4: Export as user stories
    export_response = await client.post(
        "/api/requirements/export",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "requirement_id": data["requirement_id"],
            "format": "user_stories",
            "output_format": "json"
        }
    )
    assert export_response.status_code == 200
```

### 11.3 E2E Tests (Playwright)

```typescript
// e2e/requirements-flow.spec.ts
import { test, expect } from '@playwright/test';

test('complete requirements analysis flow', async ({ page }) => {
  // Login (from Phase 0)
  await page.goto('http://localhost:8888');
  // Assume already logged in from Phase 0
  
  // Navigate to project
  await page.click('text=My Test Project');
  await page.click('text=Requirements');
  
  // Enter requirement
  await page.fill('.monaco-editor', 'User should login quickly');
  await page.click('button:has-text("Analyze")');
  
  // Wait for analysis
  await page.waitForSelector('.analysis-panel');
  
  // Verify annotations appear
  const ambiguityAnnotation = await page.locator('.annotation-ambiguity');
  await expect(ambiguityAnnotation).toBeVisible();
  
  // Verify API usage indicator
  await expect(page.locator('text=/Powered by (Groq|Gemini)/')).toBeVisible();
  
  // Open chat
  await page.click('button:has-text("Refine in Chat")');
  
  // Send chat message
  await page.fill('textarea[placeholder="Ask for improvements"]', 
    'How can I make this clearer?');
  await page.press('textarea', 'Enter');
  
  // Verify streaming response
  await page.waitForSelector('.chat-message.assistant');
  const response = await page.locator('.chat-message.assistant').first();
  await expect(response).toContainText('specify');
  
  // Apply suggestion
  await page.click('button:has-text("Apply Suggestion")');
  
  // Verify editor updated
  const editorContent = await page.locator('.monaco-editor').textContent();
  expect(editorContent).not.toContain('quickly');
  expect(editorContent).toMatch(/<\d+ms|<\d+ second/); // Specific timing
});
```

### 11.4 Performance Tests

```python
# tests/test_performance.py
import pytest
import time
from agents.parser_agent import ParserAgent

@pytest.mark.performance
async def test_parser_performance():
    agent = ParserAgent()
    text = "User " * 200  # 1000-word requirement
    
    start = time.time()
    await agent.parse(text)
    duration = time.time() - start
    
    assert duration < 2.0  # Must complete in <2 seconds

@pytest.mark.performance
async def test_api_response_time():
    """Test Groq API response time"""
    from groq import Groq
    
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    start = time.time()
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": "Test"}],
        max_tokens=100
    )
    duration = time.time() - start
    
    assert duration < 3.0  # Groq is fast!

@pytest.mark.performance
async def test_concurrent_analyses():
    # Simulate 10 concurrent analysis requests
    import asyncio
    
    async def analyze():
        # ... analysis logic ...
        pass
    
    start = time.time()
    await asyncio.gather(*[analyze() for _ in range(10)])
    duration = time.time() - start
    
    assert duration < 30.0  # 10 analyses in <30 seconds
```

---

## 12. Cost Analysis & Monitoring

### 12.1 Expected API Usage (Development Phase)

| Activity | Daily Count | Groq | Gemini | Cost |
|----------|-------------|------|--------|------|
| Testing | 50 analyses | 50 | 50 | $0 (free) |
| Development | 100 chats | 100 | 0 | $0 (free) |
| Demo/Review | 20 analyses | 20 | 20 | $0 (free) |
| **Total** | **170** | **170** | **70** | **$0** |

**Free Tier Status**: Under limits (Groq: 14,400/day, Gemini: 1,500/day)

### 12.2 Expected API Usage (Production - 100 Users)

| Activity | Monthly Count | Groq | Gemini | Est. Cost |
|----------|---------------|------|--------|-----------|
| Requirements Analysis | 5,000 | 5,000 | 5,000 | ~$7.50 |
| Chat Refinements | 10,000 | 10,000 | 0 | ~$5.00 |
| Export Generation | 2,000 | 2,000 | 0 | ~$1.00 |
| **Total** | **17,000** | **17,000** | **5,000** | **~$13.50** |

**With 40% Cache Hit Rate**: ~$8.10/month

### 12.3 API Usage Dashboard

```python
# models/api_usage.py
from pydantic import BaseModel

class APIUsageStats(BaseModel):
    groq_requests: int
    gemini_requests: int
    openai_requests: int
    cached_responses: int
    total_tokens_used: int
    estimated_cost: float
    
    def cache_hit_rate(self) -> float:
        total = sum([self.groq_requests, self.gemini_requests, 
                     self.openai_requests, self.cached_responses])
        return (self.cached_responses / total * 100) if total > 0 else 0

# Endpoint to track usage
@router.get("/api/usage/stats")
async def get_usage_stats(
    project_id: str,
    user: User = Depends(get_current_user)
):
    """Get API usage statistics for a project"""
    stats = await get_project_api_usage(project_id)
    return {
        "groq": stats.groq_requests,
        "gemini": stats.gemini_requests,
        "cached": stats.cached_responses,
        "cache_hit_rate": f"{stats.cache_hit_rate():.1f}%",
        "estimated_cost": f"${stats.estimated_cost:.2f}",
        "free_tier_status": "OK" if stats.groq_requests < 14000 else "APPROACHING LIMIT"
    }
```

---

## 13. Success Criteria

### 13.1 Quantitative Metrics
- ✅ **Parsing Accuracy**: >90% of entities correctly extracted
- ✅ **Ambiguity Detection**: >85% of vague terms flagged
- ✅ **Completeness Coverage**: >80% of missing items identified
- ✅ **Ethics Detection**: 100% of known biases caught
- ✅ **Response Time**: <15 seconds for full analysis
- ✅ **Chat Latency**: <3 seconds for responses
- ✅ **API Uptime**: >99.5%
- ✅ **Unit Test Coverage**: >70%
- ✅ **E2E Test Pass Rate**: 100%
- ✅ **API Cost (Dev)**: $0/month
- ✅ **API Cost (Prod, 100 users)**: <$15/month
- ✅ **Cache Hit Rate**: >40%

### 13.2 Qualitative Criteria
- ✅ Users can complete analysis without documentation
- ✅ AI suggestions are actionable and specific
- ✅ Chat interface feels natural (like Cursor IDE)
- ✅ Streaming responses are smooth (no lag)
- ✅ Annotations don't interfere with editing
- ✅ Export formats are usable by developers
- ✅ GitHub commits are professional and traceable
- ✅ Works on 8GB RAM laptops without slowdown
- ✅ No GPU required
- ✅ API failures handled gracefully with fallback

### 13.3 Acceptance Checklist
- [ ] All API endpoints implemented and tested
- [ ] All AI agents functional with acceptable accuracy
- [ ] API fallback mechanism working (Groq → Gemini → OpenAI)
- [ ] Response caching implemented (>40% hit rate)
- [ ] Frontend components polished and responsive
- [ ] WebSocket chat working with streaming
- [ ] Auto-save and version control working
- [ ] Export functionality generates correct formats
- [ ] GitHub integration commits successfully
- [ ] API usage tracking and cost monitoring working
- [ ] Documentation complete (API docs, user guide)
- [ ] Performance benchmarks met
- [ ] Security audit passed (input validation, RLS policies)
- [ ] Free tier limits not exceeded during development
- [ ] Production cost estimate confirmed (<$15/month for 100 users)

---

## 14. Risk Management

### 14.1 Technical Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|-------------------|
| **API Rate Limits** | Medium | High | Implement automatic fallback, aggressive caching, monitor usage |
| **API Service Downtime** | Low | Medium | 3-provider redundancy (Groq → Gemini → OpenAI) |
| **LLM Accuracy Issues** | Medium | High | Use ensemble approach, allow manual override, improve prompts |
| **Performance Degradation** | Low | Medium | Implement caching, optimize prompts, use faster APIs (Groq) |
| **WebSocket Connection Drops** | Medium | Low | Implement reconnection logic, persist state in Redis |
| **Parsing Inaccuracy** | Medium | Medium | Provide manual editing, improve training data, user feedback loop |
| **Cache Inconsistency** | Low | Low | 24-hour TTL, manual cache invalidation option |

### 14.2 User Experience Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|-------------------|
| **Analysis Too Slow** | Low | High | Use Groq (500 tok/s), show progress, allow cancellation |
| **Too Many False Positives** | High | Medium | Implement confidence thresholds, allow users to dismiss |
| **Unclear AI Suggestions** | Medium | High | Improve prompt engineering, add examples, test with users |
| **Chat Context Loss** | Low | Medium | Persist state in Redis with 24-hour TTL |
| **Overwhelming UI** | Medium | Medium | Progressive disclosure, tooltips, onboarding tutorial |
| **Streaming Lag** | Low | Low | Groq streams at 500 tok/s, very smooth |

### 14.3 Cost Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|-------------------|
| **Exceeded Free Tier** | Low | Medium | Usage alerts at 80%, cache aggressively, rate limit users |
| **Unexpected API Costs** | Low | High | Daily cost monitoring, hard limits ($20/month max) |
| **Cache Memory Usage** | Low | Low | Redis 24-hour TTL, max 10K cached entries |

---

## 15. Documentation Deliverables

### 15.1 Technical Documentation
1. **API Reference**
   - OpenAPI/Swagger specification at `/docs`
   - Request/response examples with API usage info
   - Error codes and handling
   - Rate limiting details
   - WebSocket protocol documentation

2. **Agent Architecture Guide**
   - LangGraph workflow diagrams
   - Agent responsibilities
   - Prompt templates (with optimization tips)
   - State management
   - API fallback logic

3. **Deployment Guide**
   - API key setup instructions (5-minute guide)
   - Environment variables
   - Docker Compose configuration (optional)
   - Monitoring setup

4. **Database Schema**
   - Supabase table definitions
   - Relationships and indexes
   - RLS policies
   - Sample queries
   - Migration scripts

### 15.2 User Documentation
1. **User Guide**
   - Getting started tutorial (< 5 min)
   - Feature overview with screenshots
   - Best practices for writing requirements
   - Interpreting analysis results
   - Using the chat interface
   - Exporting and approving requirements
   - Understanding API usage indicators

2. **Video Tutorials**
   - 2-minute: Quick start (write → analyze → export)
   - 5-minute: Deep dive into chat refinement
   - 3-minute: Understanding analysis results
   - 1-minute: How we keep costs low with API fallback

3. **FAQ**
   - Common issues and solutions
   - Tips for improving requirement quality
   - Troubleshooting AI responses
   - "What if I hit API rate limits?"
   - "Why do I see 'Powered by Groq' sometimes?"

---

## 16. Future Enhancements (Post Phase 1)

### 16.1 Short-term (Phase 1.5)
- **Collaboration Features**: Multi-user editing, comments, mentions
- **Requirements Templates**: Pre-built templates for common use cases
- **Custom Checklists**: Team-specific completeness criteria
- **Requirement Prioritization**: AI-suggested priority based on impact/effort
- **Requirement Dependencies**: Visual graph of relationships
- **Offline Mode**: Cache last analysis, work without internet

### 16.2 Medium-term (Phase 2+)
- **Integration with UML Module**: Auto-generate UML from requirements
- **Traceability Matrix**: Link requirements to code, tests, UML
- **Change Impact Analysis**: Predict affected code/tests
- **Requirements Diffing**: Visual diff between versions
- **Natural Language Search**: Semantic search across requirements
- **Local LLM Option**: For users with GPU (privacy-focused)

### 16.3 Long-term (Phase 3+)
- **Multi-language Support**: Non-English requirements
- **Voice Input**: Speak requirements instead of typing
- **Requirements from Mockups**: Extract from UI designs
- **Stakeholder Portal**: Non-technical review/comment interface
- **Requirements Testing**: Generate test cases directly

---

## 17. Appendix

### 17.1 Glossary
- **Ambiguity**: Vague or subjective terms lacking specific criteria
- **Completeness**: Coverage of all necessary aspects (error handling, edge cases, etc.)
- **Ethics Audit**: Detection of bias, discrimination, or privacy violations
- **Entity**: Key object mentioned in requirements (user, password, session)
- **Actor**: Person or system performing actions
- **Constraint**: Limitation or rule that must be satisfied
- **User Story**: Requirement in "As a [user], I want [goal], so that [benefit]" format
- **Acceptance Criteria**: Testable conditions for requirement satisfaction (Given-When-Then)
- **API Fallback**: Automatic switch to alternate API when primary fails
- **Cache Hit Rate**: Percentage of requests served from cache vs API
- **Streaming Response**: Real-time token-by-token output (like ChatGPT)

### 17.2 API Providers Comparison

| Feature | Groq | Gemini | OpenAI |
|---------|------|--------|--------|
| Free Tier | 14,400 req/day | 1,500 req/day | $5 credit |
| Speed | ⚡ 500 tok/s | 🚀 Fast | 🐢 Medium |
| Model | LLaMA 3.3 70B | Gemini 2.5 Flash | GPT-4o-mini |
| Best For | Chat, Ambiguity | Completeness | Fallback |
| Cost (Paid) | $0.05-0.10/1M | $0.075/1M | $0.15/1M |

### 17.3 References
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Groq API Documentation](https://console.groq.com/docs)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [spaCy Documentation](https://spacy.io/usage)
- [IBM AIF360](https://aif360.mybluemix.net/)
- [Supabase Documentation](https://supabase.com/docs)

### 17.4 Contact & Support
- **Project Lead**: Dr. Muhammad Bilal (bilal@nu.edu.pk)
- **Co-Supervisor**: Ms. Fatima Gillani (fatima.gillani@nu.edu.pk)
- **Team**: Muskan Tariq, Amna Hassan, Shuja-uddin
- **Repository**: https://github.com/integrow/integrow
- **Issues**: https://github.com/integrow/integrow/issues

---

## 18. Phase 1 Completion Checklist

### ✅ Week 1: AI Agent Foundation
- [ ] All API keys obtained and tested
- [ ] spaCy small model downloaded (50MB)
- [ ] Parser Agent implemented and tested
- [ ] Ambiguity Agent with Groq implemented
- [ ] Completeness Agent with Gemini implemented
- [ ] Ethics Agent with local patterns implemented
- [ ] Unit tests passing (>70% coverage)

### ✅ Week 2: LangGraph & API
- [ ] LangGraph state graph configured
- [ ] Orchestrator with API fallback working
- [ ] Redis caching implemented (>40% hit rate)
- [ ] Supabase tables created and tested
- [ ] All REST endpoints implemented
- [ ] API integration tests passing

### ✅ Week 3: WebSocket & Frontend
- [ ] WebSocket handler with streaming implemented
- [ ] Groq streaming integration working
- [ ] Monaco Editor integrated
- [ ] Auto-save functionality working
- [ ] Annotation system rendering correctly

### ✅ Week 4: Integration & Polish
- [ ] Analysis Panel complete
- [ ] Chat Sidebar with streaming complete
- [ ] Export Modal with preview working
- [ ] Approval Modal with GitHub commit working
- [ ] E2E tests passing
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] Demo prepared

---

**Document Version**: 1.1 (API-Based)  
**Last Updated**: October 2025  
**Status**: Ready for Development  
**Approved By**: Dr. Muhammad Bilal, Ms. Fatima Gillani  
**API Strategy**: Free-tier LLMs (Groq + Gemini) with automatic fallback  
**Target Cost**: $0 in development, <$15/month for 100 users in production 🎯# InteGrow Phase 1: Requirements Analyzer Module
