"""
Unit tests for User Stories Router - Model validation tests.
"""
import pytest
from datetime import datetime
import uuid

# Import modules under test
from api.user_stories_router import (
    RefineStoryRequest, RefineStoryResponse, 
    ApproveStoriesRequest, ApproveStoriesResponse,
    UserStoryWithContext
)
from models.user import UserProfile


class TestUserStoryModels:
    """Tests for user story Pydantic models."""

    def test_refine_story_request_valid(self):
        """Test creating valid refinement request."""
        request = RefineStoryRequest(
            story_id="story-123",
            stories=[{"title": "As a user, I want to login"}],
            refinement_request="Make the acceptance criteria more specific"
        )
        assert request.story_id == "story-123"
        assert len(request.stories) == 1

    def test_refine_story_request_with_history(self):
        """Test refinement request with conversation history."""
        request = RefineStoryRequest(
            story_id="story-123",
            stories=[{"title": "User story"}],
            refinement_request="Add more detail",
            conversation_history=[
                {"role": "user", "content": "Previous request"},
                {"role": "assistant", "content": "Previous response"}
            ]
        )
        assert len(request.conversation_history) == 2

    def test_refine_story_request_requires_refinement(self):
        """Test that refinement_request is required and non-empty."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            RefineStoryRequest(
                story_id="story-123",
                stories=[{"title": "Story"}],
                refinement_request=""  # Empty string not allowed
            )

    def test_approve_stories_request_valid(self):
        """Test creating valid approval request."""
        from models.requirement import UserStory
        
        # Create mock user stories
        stories = [
            UserStory(
                id=str(uuid.uuid4()),
                title="Login Feature",
                story="As a user, I want to login",
                acceptance_criteria=["Given valid credentials, When I click login, Then I am authenticated"],
                priority="high"
            )
        ]
        
        request = ApproveStoriesRequest(
            requirement_id=uuid.uuid4(),
            user_stories=stories,
            commit_message="Add login user stories"
        )
        assert request.branch == "main"  # Default value

    def test_approve_stories_request_custom_branch(self):
        """Test approval request with custom branch."""
        from models.requirement import UserStory
        
        stories = [
            UserStory(
                id=str(uuid.uuid4()),
                title="Feature",
                story="As a user...",
                acceptance_criteria=["Criteria 1"],
                priority="medium"
            )
        ]
        
        request = ApproveStoriesRequest(
            requirement_id=uuid.uuid4(),
            user_stories=stories,
            commit_message="Feature commit",
            branch="develop"
        )
        assert request.branch == "develop"

    def test_user_story_with_context_creation(self):
        """Test creating UserStoryWithContext."""
        story = UserStoryWithContext(
            id=str(uuid.uuid4()),
            requirement_id=str(uuid.uuid4()),
            title="Login Feature",
            story="As a user, I want to login",
            acceptance_criteria=["Criteria 1", "Criteria 2"],
            priority="high",
            story_points=5,
            tags=["auth", "security"]
        )
        assert story.title == "Login Feature"
        assert story.story_points == 5
        assert len(story.tags) == 2

    def test_user_story_with_context_defaults(self):
        """Test UserStoryWithContext default values."""
        story = UserStoryWithContext(
            id=str(uuid.uuid4()),
            requirement_id=str(uuid.uuid4()),
            title="Feature",
            story="As a user...",
            acceptance_criteria=[],
            priority="medium"
        )
        assert story.story_points is None
        assert story.tags == []

    def test_refine_story_response_model(self):
        """Test RefineStoryResponse model structure."""
        from models.requirement import UserStory
        
        refined_stories = [
            UserStory(
                id=str(uuid.uuid4()),
                title="Login Feature",
                story="As a user, I want to login",
                acceptance_criteria=["Given valid credentials", "Then I am authenticated"],
                priority="high"
            )
        ]
        
        response = RefineStoryResponse(
            refined_stories=refined_stories,
            changes_made=["Added Gherkin-style criteria"],
            explanation="Improved acceptance criteria"
        )
        
        assert len(response.refined_stories) == 1
        assert len(response.changes_made) == 1
        assert response.explanation == "Improved acceptance criteria"

    def test_approve_stories_response_model(self):
        """Test ApproveStoriesResponse model structure."""
        response = ApproveStoriesResponse(
            commit_sha="abc123def456",
            commit_url="https://github.com/user/repo/commit/abc123",
            file_path=".integrow/user-stories/requirement-001.md",
            stories_count=5
        )
        assert response.commit_sha == "abc123def456"
        assert response.stories_count == 5

    def test_refine_story_request_multiple_stories(self):
        """Test refinement request with multiple stories."""
        request = RefineStoryRequest(
            story_id="batch-123",
            stories=[
                {"title": "Story 1"},
                {"title": "Story 2"},
                {"title": "Story 3"}
            ],
            refinement_request="Add acceptance criteria to all"
        )
        assert len(request.stories) == 3

    def test_user_story_priorities(self):
        """Test user story priority values."""
        for priority in ["high", "medium", "low"]:
            story = UserStoryWithContext(
                id=str(uuid.uuid4()),
                requirement_id=str(uuid.uuid4()),
                title="Test",
                story="As a user...",
                acceptance_criteria=[],
                priority=priority
            )
            assert story.priority == priority
