from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ReviewIssue(BaseModel):
    id: Optional[UUID] = None
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    issue_type: str # bug, security, style, performance, clean_code
    severity: str # critical, high, medium, low
    description: str
    suggested_fix: Optional[str] = None

class CodeReviewReport(BaseModel):
    id: UUID
    session_id: Optional[UUID] = None
    project_id: UUID
    file_path: str
    status: str
    score: int # 0-100
    version: int = 1
    summary: str
    issues: List[ReviewIssue]
    created_at: datetime
    updated_at: datetime

class ReviewSession(BaseModel):
    id: UUID
    project_id: UUID
    version: int
    score: int
    summary: Optional[str] = None
    created_at: datetime
    reports: Optional[List[CodeReviewReport]] = None

class ReviewRequest(BaseModel):
    project_id: UUID
    file_paths: List[str] # List of relative paths or directory path
    content: Optional[str] = None # Optional, only used for single-file editor preview
