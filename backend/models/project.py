from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import re

class ProjectVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"

class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"

class ProjectTemplate(str, Enum):
    BLANK = "blank"
    WEB_APP = "web-app"
    MOBILE_APP = "mobile-app"
    API = "api"

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    visibility: ProjectVisibility = ProjectVisibility.PRIVATE
    template: ProjectTemplate = ProjectTemplate.BLANK

    @validator('name')
    def validate_project_name(cls, v):
        # Only allow alphanumeric characters and hyphens
        if not re.match(r'^[a-zA-Z0-9-]+$', v):
            raise ValueError('Project name can only contain alphanumeric characters and hyphens')
        if v.startswith('-') or v.endswith('-'):
            raise ValueError('Project name cannot start or end with a hyphen')
        return v

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    visibility: Optional[ProjectVisibility] = None
    status: Optional[ProjectStatus] = None

class Project(ProjectBase):
    """Full project model for internal use"""
    id: str
    user_id: str
    local_path: str
    github_repo_url: str
    github_repo_id: Optional[str] = None
    github_username: str
    repo_name: str
    default_branch: str = "main"
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectResponse(ProjectBase):
    id: str
    user_id: str
    local_path: str
    github_repo_url: str
    github_repo_id: Optional[str] = None
    github_username: str
    repo_name: str
    default_branch: str = "main"
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    local_path: str
    github_repo_url: str
    visibility: ProjectVisibility
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectCreateResponse(BaseModel):
    project_id: str
    name: str
    local_path: str
    github_url: str
    branches: List[str]
    created_at: datetime

class ProjectActivity(BaseModel):
    activity_type: str
    description: str
    metadata: Optional[Dict[str, Any]] = None

class ProjectActivityCreate(BaseModel):
    project_id: str
    activity_type: str
    description: str
    metadata: Optional[Dict[str, Any]] = None