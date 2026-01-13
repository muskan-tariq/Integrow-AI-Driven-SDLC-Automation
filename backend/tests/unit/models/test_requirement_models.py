"""
Unit tests for Requirement Models - Analysis, Issues, Export, Chat models.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime
from uuid import uuid4

# Import actual requirement models
from models.requirement import (
    ParsedEntities,
    AmbiguityIssue, AmbiguityAnalysis,
    CompletenessIssue, CompletenessAnalysis,
    EthicsIssue, EthicsAnalysis,
    APIUsageLog,
    RequirementBase, RequirementCreate, RequirementUpdate, Requirement,
    RequirementSummary,
    ChatMessage, ConversationState,
    UserStory,
    ExportRequest, ExportResponse,
    ApprovalRequest, ApprovalResponse,
    AnalysisRequest, AnalysisResponse
)


class TestParsedEntities:
    """Unit tests for ParsedEntities model."""

    def test_parsed_entities_default_values(self):
        """Test that ParsedEntities has correct default empty lists."""
        entities = ParsedEntities()
        assert entities.actors == []
        assert entities.actions == []
        assert entities.entities == []
        assert entities.constraints == []
        assert entities.dependencies == []

    def test_parsed_entities_with_values(self):
        """Test ParsedEntities with actual values."""
        entities = ParsedEntities(
            actors=["user", "admin"],
            actions=["login", "logout"],
            entities=["account", "session"],
            constraints=["within 2 seconds"],
            dependencies=["REQ-001"]
        )
        assert len(entities.actors) == 2
        assert "user" in entities.actors


class TestAmbiguityModels:
    """Unit tests for Ambiguity-related models."""

    def test_ambiguity_issue_valid(self):
        """Test valid AmbiguityIssue creation."""
        issue = AmbiguityIssue(
            term="fast",
            location={"start": 10, "end": 14},
            severity="high",
            explanation="'fast' is subjective and unmeasurable",
            suggestions=["< 2 seconds", "< 100ms response time"]
        )
        assert issue.term == "fast"
        assert issue.severity == "high"

    def test_ambiguity_issue_severity_validation(self):
        """Test that severity must be valid literal."""
        with pytest.raises(ValidationError):
            AmbiguityIssue(
                term="test",
                location={"start": 0, "end": 4},
                severity="invalid",  # Invalid severity
                explanation="test"
            )

    def test_ambiguity_analysis_valid(self):
        """Test valid AmbiguityAnalysis creation."""
        analysis = AmbiguityAnalysis(
            issues=[],
            score=0.3,
            total_issues=0
        )
        assert analysis.score == 0.3

    def test_ambiguity_analysis_score_validation(self):
        """Test that score must be between 0 and 1."""
        with pytest.raises(ValidationError):
            AmbiguityAnalysis(issues=[], score=1.5, total_issues=0)


class TestCompletenessModels:
    """Unit tests for Completeness-related models."""

    def test_completeness_issue_valid(self):
        """Test valid CompletenessIssue creation."""
        issue = CompletenessIssue(
            category="error_handling",
            description="Missing error handling for network failures",
            severity="high",
            suggestion="Add retry logic with exponential backoff"
        )
        assert issue.category == "error_handling"

    def test_completeness_analysis_valid(self):
        """Test valid CompletenessAnalysis creation."""
        analysis = CompletenessAnalysis(
            missing_items=[],
            score=0.8,
            total_missing=0
        )
        assert analysis.score == 0.8


class TestEthicsModels:
    """Unit tests for Ethics-related models."""

    def test_ethics_issue_valid(self):
        """Test valid EthicsIssue creation."""
        issue = EthicsIssue(
            issue_type="privacy",
            category="data_collection",
            description="Requirement implies collecting sensitive user data",
            severity="high",
            recommendation="Add explicit data handling policies"
        )
        assert issue.issue_type == "privacy"

    def test_ethics_issue_type_validation(self):
        """Test that issue_type must be valid literal."""
        with pytest.raises(ValidationError):
            EthicsIssue(
                issue_type="invalid_type",
                category="test",
                description="test",
                severity="low",
                recommendation="test"
            )

    def test_ethics_analysis_valid(self):
        """Test valid EthicsAnalysis creation."""
        analysis = EthicsAnalysis(
            ethical_issues=[],
            score=0.95,
            total_issues=0
        )
        assert analysis.score == 0.95


class TestAPIUsageLog:
    """Unit tests for APIUsageLog model."""

    def test_api_usage_log_defaults(self):
        """Test APIUsageLog default values."""
        log = APIUsageLog()
        assert log.groq == 0
        assert log.gemini == 0
        assert log.openai == 0
        assert log.cached == 0
        assert log.total_tokens == 0
        assert log.estimated_cost == 0.0

    def test_api_usage_log_with_values(self):
        """Test APIUsageLog with actual values."""
        log = APIUsageLog(
            groq=5,
            gemini=3,
            total_tokens=1500,
            estimated_cost=0.05
        )
        assert log.groq == 5
        assert log.total_tokens == 1500


class TestRequirementModels:
    """Unit tests for Requirement CRUD models."""

    def test_requirement_base_valid(self):
        """Test valid RequirementBase creation."""
        req = RequirementBase(
            project_id=uuid4(),
            raw_text="The system shall allow users to login."
        )
        assert req.version == 1
        assert len(req.raw_text) > 0

    def test_requirement_base_text_min_length(self):
        """Test that raw_text has minimum length."""
        with pytest.raises(ValidationError):
            RequirementBase(project_id=uuid4(), raw_text="")

    def test_requirement_create_valid(self):
        """Test valid RequirementCreate creation."""
        req = RequirementCreate(
            project_id=uuid4(),
            raw_text="Users can search products by name."
        )
        assert req.version == 1

    def test_requirement_update_all_optional(self):
        """Test that RequirementUpdate fields are optional."""
        update = RequirementUpdate()
        assert update.raw_text is None
        assert update.status is None

    def test_requirement_update_with_status(self):
        """Test RequirementUpdate with status."""
        update = RequirementUpdate(status="approved")
        assert update.status == "approved"

    def test_requirement_summary_valid(self):
        """Test valid RequirementSummary creation."""
        now = datetime.now()
        summary = RequirementSummary(
            id=uuid4(),
            project_id=uuid4(),
            version=1,
            raw_text="Short description...",
            overall_quality_score=0.75,
            status="draft",
            created_at=now,
            updated_at=now
        )
        assert summary.version == 1


class TestChatModels:
    """Unit tests for Chat-related models."""

    def test_chat_message_user(self):
        """Test user chat message."""
        msg = ChatMessage(
            role="user",
            content="What are the ambiguities in my requirement?"
        )
        assert msg.role == "user"
        assert msg.timestamp is not None

    def test_chat_message_assistant(self):
        """Test assistant chat message with suggestions."""
        msg = ChatMessage(
            role="assistant",
            content="I found 3 ambiguous terms...",
            suggestions=["Use specific metrics", "Define user roles"]
        )
        assert msg.role == "assistant"
        assert len(msg.suggestions) == 2

    def test_conversation_state_valid(self):
        """Test valid ConversationState creation."""
        state = ConversationState(
            session_id="session-123",
            requirement_id=uuid4(),
            messages=[]
        )
        assert state.session_id == "session-123"


class TestUserStory:
    """Unit tests for UserStory model."""

    def test_user_story_valid(self):
        """Test valid UserStory creation."""
        story = UserStory(
            title="User Login",
            story="As a user, I want to login, so that I can access my dashboard.",
            acceptance_criteria=[
                "Given valid credentials, when I login, then I see dashboard",
                "Given invalid credentials, when I login, then I see error"
            ],
            priority="high",
            story_points=3,
            tags=["auth", "security"]
        )
        assert story.priority == "high"
        assert story.story_points == 3

    def test_user_story_defaults(self):
        """Test UserStory default values."""
        story = UserStory(
            title="Test Story",
            story="As a tester, I want to test, so that I verify functionality."
        )
        assert story.priority == "medium"
        assert story.story_points is None
        assert story.tags == []

    def test_user_story_points_validation(self):
        """Test that story_points must be 1-13 (Fibonacci-like)."""
        with pytest.raises(ValidationError):
            UserStory(
                title="Test",
                story="Test story",
                story_points=15  # Invalid: > 13
            )


class TestExportModels:
    """Unit tests for Export-related models."""

    def test_export_request_valid(self):
        """Test valid ExportRequest creation."""
        request = ExportRequest(
            requirement_id=uuid4(),
            format="user_stories",
            output_format="markdown"
        )
        assert request.format == "user_stories"
        assert request.include_analysis == True  # Default

    def test_export_response_valid(self):
        """Test valid ExportResponse creation."""
        response = ExportResponse(
            format="markdown",
            content="# Requirements\n\n...",
            file_size=256
        )
        assert response.file_size == 256


class TestApprovalModels:
    """Unit tests for Approval-related models."""

    def test_approval_request_valid(self):
        """Test valid ApprovalRequest creation."""
        request = ApprovalRequest(
            requirement_id=uuid4(),
            commit_message="Add user login requirement"
        )
        assert request.branch == "main"  # Default

    def test_approval_request_custom_branch(self):
        """Test ApprovalRequest with custom branch."""
        request = ApprovalRequest(
            requirement_id=uuid4(),
            commit_message="Feature: Add search",
            branch="feature/search"
        )
        assert request.branch == "feature/search"

    def test_approval_response_valid(self):
        """Test valid ApprovalResponse creation."""
        response = ApprovalResponse(
            requirement_id=uuid4(),
            version=2,
            commit_sha="abc123def456",
            commit_url="https://github.com/user/repo/commit/abc123",
            file_path="requirements/REQ-001.yaml"
        )
        assert response.version == 2


class TestAnalysisModels:
    """Unit tests for Analysis request/response models."""

    def test_analysis_request_valid(self):
        """Test valid AnalysisRequest creation."""
        request = AnalysisRequest(
            project_id=uuid4(),
            text="The system should be fast and user-friendly."
        )
        assert len(request.text) > 0

    def test_analysis_request_text_min_length(self):
        """Test that analysis text has minimum length."""
        with pytest.raises(ValidationError):
            AnalysisRequest(project_id=uuid4(), text="")
