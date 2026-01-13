from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class DebtAnalysisRequest(BaseModel):
    project_id: UUID
    include_tests: bool = True
    max_depth: int = 10  # Maximum directory depth to analyze
    specific_files: Optional[List[str]] = None  # Optional list of specific files to analyze


class DebtIssue(BaseModel):
    id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    file_path: str
    issue_type: str  # 'complexity', 'duplication', 'dependency', 'smell', 'architecture', 'documentation'
    category: str  # e.g., 'High Complexity', 'Duplicate Code'
    severity: str  # 'critical', 'high', 'medium', 'low'
    title: str
    description: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    code_snippet: Optional[str] = None
    suggested_fix: Optional[str] = None
    estimated_hours: float = 0.0
    created_at: Optional[datetime] = None


class DebtSession(BaseModel):
    id: UUID
    project_id: UUID
    version: int
    overall_score: int
    complexity_score: int
    duplication_score: int
    dependency_score: int
    summary: Optional[str] = None
    total_issues: int
    critical_issues: int
    estimated_hours: float
    status: str = 'completed'
    github_exported: Optional[bool] = False
    github_commit_sha: Optional[str] = None
    github_exported_at: Optional[datetime] = None
    created_at: datetime
    issues: Optional[List[DebtIssue]] = None


class DebtAnalysisResponse(BaseModel):
    status: str
    session_id: UUID
    version: int
    overall_score: int
    total_issues: int
    critical_issues: int
    estimated_hours: float
    issues: List[DebtIssue]
