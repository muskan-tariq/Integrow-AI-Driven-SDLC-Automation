"""
Generated Code Models

Pydantic models for the code generation feature.
Handles UML parsing results, generation requests/responses, and file storage.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================
# Enums
# ============================================

class Visibility(str, Enum):
    """Visibility modifier for class members."""
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"


class RelationshipType(str, Enum):
    """UML relationship types."""
    ASSOCIATION = "association"
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"
    INHERITANCE = "inheritance"
    DEPENDENCY = "dependency"


class FileType(str, Enum):
    """Type of generated file."""
    MODEL = "model"
    API = "api"
    SERVICE = "service"
    COMPONENT = "component"
    TEST = "test"
    MIGRATION = "migration"


class GenerationStatus(str, Enum):
    """Status of a code generation session."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMMITTED = "committed"


# ============================================
# Parsed UML Models
# ============================================

class ParsedAttribute(BaseModel):
    """Represents a class attribute parsed from UML."""
    name: str
    type: str = "Any"
    visibility: Visibility = Visibility.PRIVATE
    default_value: Optional[str] = None
    is_optional: bool = False


class ParsedParameter(BaseModel):
    """Represents a method parameter."""
    name: str
    type: str = "Any"
    default_value: Optional[str] = None


class ParsedMethod(BaseModel):
    """Represents a class method parsed from UML."""
    name: str
    parameters: List[ParsedParameter] = Field(default_factory=list)
    return_type: str = "None"
    visibility: Visibility = Visibility.PUBLIC
    is_async: bool = False
    description: Optional[str] = None


class ParsedRelationship(BaseModel):
    """Represents a relationship between classes."""
    source: str
    target: str
    relationship_type: RelationshipType
    source_multiplicity: str = "1"
    target_multiplicity: str = "1"
    label: Optional[str] = None


class ParsedClass(BaseModel):
    """Represents a class parsed from UML diagram."""
    name: str
    attributes: List[ParsedAttribute] = Field(default_factory=list)
    methods: List[ParsedMethod] = Field(default_factory=list)
    is_abstract: bool = False
    parent_class: Optional[str] = None
    interfaces: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class ParsedUMLResult(BaseModel):
    """Complete result of parsing a PlantUML diagram."""
    classes: List[ParsedClass] = Field(default_factory=list)
    relationships: List[ParsedRelationship] = Field(default_factory=list)
    raw_plantuml: str = ""
    parse_success: bool = True
    parse_errors: List[str] = Field(default_factory=list)


# ============================================
# Tech Stack Configuration
# ============================================

class TechStackConfig(BaseModel):
    """Configuration for the target technology stack."""
    backend: str = Field(
        default="python-fastapi",
        description="Backend framework: python-fastapi, python-django, nodejs-express"
    )
    database: str = Field(
        default="postgresql",
        description="Database: postgresql, mysql, mongodb, sqlite"
    )
    frontend: str = Field(
        default="react-typescript",
        description="Frontend: react-typescript, vue-typescript, nextjs"
    )
    orm: str = Field(
        default="sqlalchemy",
        description="ORM: sqlalchemy, prisma, mongoose, typeorm"
    )


# ============================================
# Code Generation Request/Response
# ============================================

class GeneratedFile(BaseModel):
    """Represents a single generated file."""
    file_path: str = Field(..., description="Relative path for the file")
    content: str = Field(..., description="File content")
    file_type: FileType
    language: str = Field(default="python", description="Programming language")
    dependencies: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class CodeGenerationRequest(BaseModel):
    """Request to generate code from UML/user stories."""
    project_id: UUID
    requirement_id: UUID
    uml_diagram_id: Optional[UUID] = None
    tech_stack: TechStackConfig = Field(default_factory=TechStackConfig)
    include_tests: bool = True
    include_migrations: bool = True
    generation_scope: List[str] = Field(
        default=["models", "api", "services"],
        description="What to generate: models, api, services, frontend, tests"
    )


class CodeGenerationResult(BaseModel):
    """Result of code generation."""
    session_id: UUID
    requirement_id: UUID
    files: List[GeneratedFile] = Field(default_factory=list)
    total_files: int = 0
    total_lines: int = 0
    generation_time: float = 0.0
    status: GenerationStatus = GenerationStatus.PENDING
    api_used: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# Context Models
# ============================================

class UserStoryContext(BaseModel):
    """User story data for context building."""
    title: str
    story: str
    acceptance_criteria: List[str] = Field(default_factory=list)
    priority: str = "medium"
    tags: List[str] = Field(default_factory=list)


class CodeGenerationContext(BaseModel):
    """Complete context for code generation."""
    project_id: str
    requirement_id: str
    requirement_text: str = ""
    
    # From UML
    parsed_uml: Optional[ParsedUMLResult] = None
    uml_diagram_id: Optional[str] = None
    
    # From User Stories
    user_stories: List[UserStoryContext] = Field(default_factory=list)
    
    # Configuration
    tech_stack: TechStackConfig = Field(default_factory=TechStackConfig)
    generation_scope: List[str] = Field(default_factory=list)
    
    # Optional: existing code for consistency (RAG)
    existing_code_context: Optional[str] = None


# ============================================
# Database Session Model
# ============================================

class CodeGenerationSession(BaseModel):
    """Database model for storing code generation sessions."""
    id: Optional[UUID] = None
    project_id: UUID
    requirement_id: UUID
    uml_diagram_id: Optional[UUID] = None
    user_id: UUID
    status: GenerationStatus = GenerationStatus.PENDING
    tech_stack: TechStackConfig = Field(default_factory=TechStackConfig)
    generation_scope: List[str] = Field(default_factory=list)
    total_files: int = 0
    total_lines: int = 0
    generation_time: float = 0.0
    api_used: Dict[str, str] = Field(default_factory=dict)
    committed_sha: Optional[str] = None
    committed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None
    commit_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# Approval Request/Response
# ============================================

class ApproveCodeRequest(BaseModel):
    """Request to approve and commit generated code."""
    session_id: UUID
    commit_message: str = Field(
        default="feat: add generated code",
        description="Git commit message"
    )
    branch: str = Field(default="main", description="Target branch")
    target_directory: str = Field(
        default="src",
        description="Directory in repo where files will be placed"
    )


class ApproveCodeResponse(BaseModel):
    """Response after approving and committing code."""
    commit_sha: str
    commit_url: str
    files_committed: int
    branch: str


# ============================================
# Diff & Comparison Models
# ============================================

class ChangeType(str, Enum):
    """Type of change in a file."""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    IDENTICAL = "identical"


class FileDiff(BaseModel):
    """Represents the difference between generated and local file."""
    file_path: str
    change_type: ChangeType
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    diff_stat: str = "+0 -0"  # Simple stat like "+10 -2"


class ComparisonResult(BaseModel):
    """Result of comparing a generation session against local codebase."""
    session_id: UUID
    project_id: UUID
    diffs: List[FileDiff] = Field(default_factory=list)
    total_changes: int = 0
    can_apply_automatically: bool = True

