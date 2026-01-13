"""
UML Diagram Models

Pydantic models for UML diagram data validation and serialization.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field


class EntityInfo(BaseModel):
    """Information about an entity extracted from user stories"""
    name: str
    mentions: int = 0
    methods: List[str] = Field(default_factory=list)
    attributes: List[str] = Field(default_factory=list)


class RelationshipInfo(BaseModel):
    """Information about a relationship between entities"""
    source: str
    target: str
    relationship_type: str  # composition, aggregation, association, inheritance
    description: Optional[str] = None
    multiplicity: Optional[str] = None  # e.g., "1", "*", "0..1", "1..*"


class DiagramAnalysisMetadata(BaseModel):
    """Metadata from diagram analysis"""
    entities: Dict[str, EntityInfo] = Field(default_factory=dict)
    relationships: List[RelationshipInfo] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)
    total_stories: int = 0
    entities_found: int = 0
    relationships_found: int = 0
    api_used: Optional[str] = None  # groq, gemini, fallback


class UMLDiagramBase(BaseModel):
    """Base model for UML diagram"""
    diagram_type: str = Field(default="class", description="Type of UML diagram")
    plantuml_code: str = Field(..., description="PlantUML source code")
    analysis_metadata: Optional[DiagramAnalysisMetadata] = None


class UMLDiagramCreate(UMLDiagramBase):
    """Model for creating a new UML diagram"""
    requirement_id: UUID
    project_id: UUID
    user_id: UUID
    rendered_svg: Optional[str] = None
    version: int = Field(default=1)


class UMLDiagramUpdate(BaseModel):
    """Model for updating an existing UML diagram"""
    plantuml_code: Optional[str] = None
    rendered_svg: Optional[str] = None
    analysis_metadata: Optional[DiagramAnalysisMetadata] = None
    version: Optional[int] = None


class UMLDiagramResponse(UMLDiagramBase):
    """Model for UML diagram response"""
    id: UUID
    requirement_id: Optional[UUID] = None
    project_id: UUID
    user_id: UUID
    rendered_svg: Optional[str] = None
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UMLGenerationRequest(BaseModel):
    """Request model for generating UML diagram"""
    user_story_ids: Optional[List[UUID]] = Field(
        default=None,
        description="Optional list of user story IDs to include. If not provided, all stories will be used."
    )
    regenerate: bool = Field(
        default=False,
        description="Force regeneration even if cached diagram exists"
    )


class ApproveUMLRequest(BaseModel):
    """Request model for approving and pushing UML diagram"""
    diagram_id: UUID
    commit_message: str = Field(..., min_length=1, max_length=200)
    branch: str = Field(default="main")


class ApproveUMLResponse(BaseModel):
    """Response from UML diagram approval"""
    commit_sha: str = Field(..., description="Git commit SHA")
    commit_url: str = Field(..., description="GitHub commit URL")
    file_path: str = Field(..., description="Path to committed file")
    stories_count: int = Field(default=0, description="Dummy field for compatibility if needed")


class UMLGenerationResponse(BaseModel):
    """Response model for UML diagram generation"""
    id: UUID
    plantuml_code: str
    svg_url: str
    png_url: str
    analysis: DiagramAnalysisMetadata
    version: int
    created_at: datetime


class UMLDiagramListResponse(BaseModel):
    """Response model for listing UML diagrams"""
    diagrams: List[UMLDiagramResponse]
    total: int
    page: int = 1
    page_size: int = 10
