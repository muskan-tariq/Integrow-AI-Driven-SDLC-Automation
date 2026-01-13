"""
Pydantic models for requirements and analysis data
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ParsedEntities(BaseModel):
    """Parsed entities from requirement text"""
    actors: List[str] = Field(default_factory=list, description="Actors mentioned in the requirement")
    actions: List[str] = Field(default_factory=list, description="Actions/verbs in the requirement")
    entities: List[str] = Field(default_factory=list, description="Key entities/objects mentioned")
    constraints: List[str] = Field(default_factory=list, description="Constraints and limitations")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies on other requirements")


class AmbiguityIssue(BaseModel):
    """Individual ambiguity issue found"""
    term: str = Field(..., description="The ambiguous term")
    location: Dict[str, int] = Field(..., description="Start and end positions in text")
    severity: Literal["critical", "high", "medium", "low"] = Field(..., description="Issue severity")
    explanation: str = Field(..., description="Explanation of why it's ambiguous")
    suggestions: List[str] = Field(default_factory=list, description="Suggested improvements")


class AmbiguityAnalysis(BaseModel):
    """Ambiguity detection results"""
    issues: List[AmbiguityIssue] = Field(default_factory=list, description="List of ambiguous terms found")
    score: float = Field(..., ge=0.0, le=1.0, description="Ambiguity score (0=clear, 1=very ambiguous)")
    total_issues: int = Field(..., description="Total number of issues found")


class CompletenessIssue(BaseModel):
    """Individual completeness issue found"""
    category: str = Field(..., description="Category of missing item (error_handling, edge_cases, etc.)")
    description: str = Field(..., description="Description of what's missing")
    severity: Literal["critical", "high", "medium", "low"] = Field(..., description="Issue severity")
    suggestion: str = Field(..., description="Suggestion for improvement")


class CompletenessAnalysis(BaseModel):
    """Completeness check results"""
    missing_items: List[CompletenessIssue] = Field(default_factory=list, description="List of missing items")
    score: float = Field(..., ge=0.0, le=1.0, description="Completeness score (0=incomplete, 1=complete)")
    total_missing: int = Field(..., description="Total number of missing items")


class EthicsIssue(BaseModel):
    """Individual ethics issue found"""
    issue_type: Literal["bias", "privacy", "discrimination"] = Field(..., description="Type of ethics issue")
    category: str = Field(..., description="Category of the issue (gender, race, etc.)")
    location: Optional[Dict[str, int]] = Field(None, description="Location in text if applicable")
    description: str = Field(..., description="Description of the ethics issue")
    severity: Literal["critical", "high", "medium", "low"] = Field(..., description="Issue severity")
    recommendation: str = Field(..., description="Recommendation for fixing the issue")


class EthicsAnalysis(BaseModel):
    """Ethics audit results"""
    ethical_issues: List[EthicsIssue] = Field(default_factory=list, description="List of ethics issues found")
    score: float = Field(..., ge=0.0, le=1.0, description="Ethics score (0=unethical, 1=ethical)")
    total_issues: int = Field(..., description="Total number of ethics issues")


class APIUsageLog(BaseModel):
    """API usage tracking for cost monitoring"""
    groq: int = Field(default=0, description="Number of Groq API calls")
    gemini: int = Field(default=0, description="Number of Gemini API calls")
    openai: int = Field(default=0, description="Number of OpenAI API calls")
    cached: int = Field(default=0, description="Number of cached responses used")
    total_tokens: int = Field(default=0, description="Total tokens consumed")
    estimated_cost: float = Field(default=0.0, description="Estimated cost in USD")


class RequirementBase(BaseModel):
    """Base requirement model"""
    project_id: UUID = Field(..., description="ID of the project this requirement belongs to")
    raw_text: str = Field(..., min_length=1, max_length=50000, description="Raw requirement text")
    version: int = Field(default=1, ge=1, description="Version number of the requirement")


class RequirementCreate(RequirementBase):
    """Model for creating a new requirement"""
    pass


class RequirementUpdate(BaseModel):
    """Model for updating a requirement"""
    raw_text: Optional[str] = Field(None, min_length=1, max_length=50000)
    status: Optional[Literal["draft", "analyzing", "refining", "approved", "archived"]] = None


class Requirement(RequirementBase):
    """Full requirement model with analysis results"""
    id: UUID = Field(..., description="Unique identifier")
    parsed_entities: Optional[ParsedEntities] = Field(None, description="Parsed entities from text")
    ambiguity_analysis: Optional[AmbiguityAnalysis] = Field(None, description="Ambiguity detection results")
    completeness_analysis: Optional[CompletenessAnalysis] = Field(None, description="Completeness check results")
    ethics_analysis: Optional[EthicsAnalysis] = Field(None, description="Ethics audit results")
    overall_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall quality score")
    api_usage_log: APIUsageLog = Field(default_factory=APIUsageLog, description="API usage tracking")
    status: Literal["draft", "analyzing", "refining", "approved", "archived"] = Field(default="draft")
    created_by: Optional[UUID] = Field(None, description="User who created the requirement")
    approved_by: Optional[UUID] = Field(None, description="User who approved the requirement")
    approved_at: Optional[datetime] = Field(None, description="When the requirement was approved")
    created_at: datetime = Field(..., description="When the requirement was created")
    updated_at: datetime = Field(..., description="When the requirement was last updated")

    class Config:
        from_attributes = True


class RequirementSummary(BaseModel):
    """Summary model for requirement lists"""
    id: UUID
    project_id: UUID
    version: int
    raw_text: str = Field(..., max_length=200)  # Truncated for list view
    overall_quality_score: Optional[float]
    status: str
    created_at: datetime
    updated_at: datetime


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: Literal["user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    suggestions: Optional[List[str]] = Field(None, description="AI suggestions if applicable")


class ConversationState(BaseModel):
    """Conversation state for chat"""
    session_id: str = Field(..., description="Unique session identifier")
    requirement_id: UUID = Field(..., description="Associated requirement ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="Chat message history")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserStory(BaseModel):
    """Generated user story"""
    title: str = Field(..., description="User story title")
    story: str = Field(..., description="User story in 'As a [user], I want [goal], so that [benefit]' format")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Given-When-Then criteria")
    priority: Literal["high", "medium", "low"] = Field(default="medium", description="Story priority")
    story_points: Optional[int] = Field(None, ge=1, le=13, description="Story points estimation")
    tags: List[str] = Field(default_factory=list, description="Story tags")


class ExportRequest(BaseModel):
    """Request model for exporting requirements"""
    requirement_id: UUID = Field(..., description="ID of requirement to export")
    format: Literal["user_stories", "acceptance_criteria", "raw", "structured"] = Field(
        ..., description="Export format"
    )
    output_format: Literal["json", "yaml", "markdown", "csv"] = Field(
        default="json", description="Output file format"
    )
    include_analysis: bool = Field(default=True, description="Include analysis results in export")


class ExportResponse(BaseModel):
    """Response model for export requests"""
    format: str = Field(..., description="Export format used")
    content: str = Field(..., description="Exported content")
    download_url: Optional[str] = Field(None, description="URL to download the file")
    file_size: int = Field(..., description="Size of exported content in bytes")


class ApprovalRequest(BaseModel):
    """Request model for approving requirements"""
    requirement_id: UUID = Field(..., description="ID of requirement to approve")
    commit_message: str = Field(..., min_length=1, max_length=200, description="Git commit message")
    branch: str = Field(default="main", description="Target branch for commit")


class ApprovalResponse(BaseModel):
    """Response model for approval requests"""
    requirement_id: UUID = Field(..., description="ID of approved requirement")
    version: int = Field(..., description="New version number")
    commit_sha: str = Field(..., description="Git commit SHA")
    commit_url: str = Field(..., description="GitHub commit URL")
    file_path: str = Field(..., description="Path to committed file")


class AnalysisRequest(BaseModel):
    """Request model for analyzing requirements"""
    project_id: UUID = Field(..., description="ID of the project")
    text: str = Field(..., min_length=1, max_length=50000, description="Requirement text to analyze")


class AnalysisResponse(BaseModel):
    """Response model for analysis requests"""
    requirement_id: UUID = Field(..., description="ID of created requirement")
    session_id: str = Field(..., description="Session ID for chat")
    quality_score: int = Field(..., ge=0, le=100, description="Quality score (0-100)")
    total_issues: int = Field(..., ge=0, description="Total number of issues found")
    ambiguity_issues: List[Dict[str, Any]] = Field(default_factory=list, description="Ambiguity issues")
    completeness_issues: List[Dict[str, Any]] = Field(default_factory=list, description="Completeness issues")
    ethics_issues: List[Dict[str, Any]] = Field(default_factory=list, description="Ethics issues")
    parsed_entities: Dict[str, List[str]] = Field(default_factory=dict, description="Parsed entities")
    actors: List[str] = Field(default_factory=list, description="Actors mentioned in the requirement")
    actions: List[str] = Field(default_factory=list, description="Actions/verbs in the requirement")
    entities: List[str] = Field(default_factory=list, description="Key entities/objects mentioned")
    constraints: List[str] = Field(default_factory=list, description="Constraints and limitations")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies on other requirements")


class AmbiguityIssue(BaseModel):
    """Individual ambiguity issue found"""
    term: str = Field(..., description="The ambiguous term")
    location: Dict[str, int] = Field(..., description="Start and end positions in text")
    severity: Literal["critical", "high", "medium", "low"] = Field(..., description="Issue severity")
    explanation: str = Field(..., description="Explanation of why it's ambiguous")
    suggestions: List[str] = Field(default_factory=list, description="Suggested improvements")


class AmbiguityAnalysis(BaseModel):
    """Ambiguity detection results"""
    issues: List[AmbiguityIssue] = Field(default_factory=list, description="List of ambiguous terms found")
    score: float = Field(..., ge=0.0, le=1.0, description="Ambiguity score (0=clear, 1=very ambiguous)")
    total_issues: int = Field(..., description="Total number of issues found")


class CompletenessIssue(BaseModel):
    """Individual completeness issue found"""
    category: str = Field(..., description="Category of missing item (error_handling, edge_cases, etc.)")
    description: str = Field(..., description="Description of what's missing")
    severity: Literal["critical", "high", "medium", "low"] = Field(..., description="Issue severity")
    suggestion: str = Field(..., description="Suggestion for improvement")


class CompletenessAnalysis(BaseModel):
    """Completeness check results"""
    missing_items: List[CompletenessIssue] = Field(default_factory=list, description="List of missing items")
    score: float = Field(..., ge=0.0, le=1.0, description="Completeness score (0=incomplete, 1=complete)")
    total_missing: int = Field(..., description="Total number of missing items")


class EthicsIssue(BaseModel):
    """Individual ethics issue found"""
    issue_type: Literal["bias", "privacy", "discrimination"] = Field(..., description="Type of ethics issue")
    category: str = Field(..., description="Category of the issue (gender, race, etc.)")
    location: Optional[Dict[str, int]] = Field(None, description="Location in text if applicable")
    description: str = Field(..., description="Description of the ethics issue")
    severity: Literal["critical", "high", "medium", "low"] = Field(..., description="Issue severity")
    recommendation: str = Field(..., description="Recommendation for fixing the issue")


class EthicsAnalysis(BaseModel):
    """Ethics audit results"""
    ethical_issues: List[EthicsIssue] = Field(default_factory=list, description="List of ethics issues found")
    score: float = Field(..., ge=0.0, le=1.0, description="Ethics score (0=unethical, 1=ethical)")
    total_issues: int = Field(..., description="Total number of ethics issues")


class APIUsageLog(BaseModel):
    """API usage tracking for cost monitoring"""
    groq: int = Field(default=0, description="Number of Groq API calls")
    gemini: int = Field(default=0, description="Number of Gemini API calls")
    openai: int = Field(default=0, description="Number of OpenAI API calls")
    cached: int = Field(default=0, description="Number of cached responses used")
    total_tokens: int = Field(default=0, description="Total tokens consumed")
    estimated_cost: float = Field(default=0.0, description="Estimated cost in USD")


class RequirementBase(BaseModel):
    """Base requirement model"""
    project_id: UUID = Field(..., description="ID of the project this requirement belongs to")
    raw_text: str = Field(..., min_length=1, max_length=50000, description="Raw requirement text")
    version: int = Field(default=1, ge=1, description="Version number of the requirement")


class RequirementCreate(RequirementBase):
    """Model for creating a new requirement"""
    pass


class RequirementUpdate(BaseModel):
    """Model for updating a requirement"""
    raw_text: Optional[str] = Field(None, min_length=1, max_length=50000)
    status: Optional[Literal["draft", "analyzing", "refining", "approved", "archived"]] = None


class Requirement(RequirementBase):
    """Full requirement model with analysis results"""
    id: UUID = Field(..., description="Unique identifier")
    parsed_entities: Optional[ParsedEntities] = Field(None, description="Parsed entities from text")
    ambiguity_analysis: Optional[AmbiguityAnalysis] = Field(None, description="Ambiguity detection results")
    completeness_analysis: Optional[CompletenessAnalysis] = Field(None, description="Completeness check results")
    ethics_analysis: Optional[EthicsAnalysis] = Field(None, description="Ethics audit results")
    overall_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall quality score")
    api_usage_log: APIUsageLog = Field(default_factory=APIUsageLog, description="API usage tracking")
    status: Literal["draft", "analyzing", "refining", "approved", "archived"] = Field(default="draft")
    created_by: Optional[UUID] = Field(None, description="User who created the requirement")
    approved_by: Optional[UUID] = Field(None, description="User who approved the requirement")
    approved_at: Optional[datetime] = Field(None, description="When the requirement was approved")
    created_at: datetime = Field(..., description="When the requirement was created")
    updated_at: datetime = Field(..., description="When the requirement was last updated")

    class Config:
        from_attributes = True


class RequirementSummary(BaseModel):
    """Summary model for requirement lists"""
    id: UUID
    project_id: UUID
    version: int
    raw_text: str = Field(..., max_length=200)  # Truncated for list view
    overall_quality_score: Optional[float]
    status: str
    created_at: datetime
    updated_at: datetime


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: Literal["user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    suggestions: Optional[List[str]] = Field(None, description="AI suggestions if applicable")


class ConversationState(BaseModel):
    """Conversation state for chat"""
    session_id: str = Field(..., description="Unique session identifier")
    requirement_id: UUID = Field(..., description="Associated requirement ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="Chat message history")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserStory(BaseModel):
    """Generated user story"""
    title: str = Field(..., description="User story title")
    story: str = Field(..., description="User story in 'As a [user], I want [goal], so that [benefit]' format")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Given-When-Then criteria")
    priority: Literal["high", "medium", "low"] = Field(default="medium", description="Story priority")
    story_points: Optional[int] = Field(None, ge=1, le=13, description="Story points estimation")
    tags: List[str] = Field(default_factory=list, description="Story tags")


class ExportRequest(BaseModel):
    """Request model for exporting requirements"""
    requirement_id: UUID = Field(..., description="ID of requirement to export")
    format: Literal["user_stories", "acceptance_criteria", "raw", "structured"] = Field(
        ..., description="Export format"
    )
    output_format: Literal["json", "yaml", "markdown", "csv"] = Field(
        default="json", description="Output file format"
    )
    include_analysis: bool = Field(default=True, description="Include analysis results in export")


class ExportResponse(BaseModel):
    """Response model for export requests"""
    format: str = Field(..., description="Export format used")
    content: str = Field(..., description="Exported content")
    download_url: Optional[str] = Field(None, description="URL to download the file")
    file_size: int = Field(..., description="Size of exported content in bytes")


class ApprovalRequest(BaseModel):
    """Request model for approving requirements"""
    requirement_id: UUID = Field(..., description="ID of requirement to approve")
    commit_message: str = Field(..., min_length=1, max_length=200, description="Git commit message")
    branch: str = Field(default="main", description="Target branch for commit")


class ApprovalResponse(BaseModel):
    """Response model for approval requests"""
    requirement_id: UUID = Field(..., description="ID of approved requirement")
    version: int = Field(..., description="New version number")
    commit_sha: str = Field(..., description="Git commit SHA")
    commit_url: str = Field(..., description="GitHub commit URL")
    file_path: str = Field(..., description="Path to committed file")


class AnalysisRequest(BaseModel):
    """Request model for analyzing requirements"""
    project_id: UUID = Field(..., description="ID of the project")
    text: str = Field(..., min_length=1, max_length=50000, description="Requirement text to analyze")


class AnalysisResponse(BaseModel):
    """Response model for analysis requests"""
    requirement_id: UUID = Field(..., description="ID of created requirement")
    session_id: str = Field(..., description="Session ID for chat")
    quality_score: int = Field(..., ge=0, le=100, description="Quality score (0-100)")
    total_issues: int = Field(..., ge=0, description="Total number of issues found")
    ambiguity_issues: List[Dict[str, Any]] = Field(default_factory=list, description="Ambiguity issues")
    completeness_issues: List[Dict[str, Any]] = Field(default_factory=list, description="Completeness issues")
    ethics_issues: List[Dict[str, Any]] = Field(default_factory=list, description="Ethics issues")
    parsed_entities: Dict[str, List[str]] = Field(default_factory=dict, description="Parsed entities")
    parsed: Optional[ParsedEntities] = Field(None, description="Detailed parsed entities")
    analysis: Dict[str, Any] = Field(..., description="Analysis results")
    overall_quality_score: float = Field(..., ge=0.0, le=1.0, description="Overall quality score (0-1)")
    api_used: Dict[str, str] = Field(default_factory=dict, description="Which APIs were used for each analysis")
    processing_time: float = Field(..., description="Time taken for analysis in seconds")
    user_stories: List[UserStory] = Field(default_factory=list, description="Generated user stories")
