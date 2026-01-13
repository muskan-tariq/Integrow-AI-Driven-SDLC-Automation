"""
Unit tests for UML Diagram Models.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime
from uuid import uuid4

# Import actual UML models
from models.uml_diagram import (
    EntityInfo, RelationshipInfo, DiagramAnalysisMetadata,
    UMLDiagramBase, UMLDiagramCreate, UMLDiagramUpdate,
    UMLDiagramResponse, UMLGenerationRequest, UMLGenerationResponse,
    UMLDiagramListResponse
)


class TestEntityInfo:
    """Tests for EntityInfo model."""

    def test_entity_info_creation(self):
        """Test creating EntityInfo."""
        entity = EntityInfo(
            name="User",
            mentions=5,
            methods=["login", "logout"],
            attributes=["name", "email"]
        )
        assert entity.name == "User"
        assert entity.mentions == 5
        assert len(entity.methods) == 2

    def test_entity_info_defaults(self):
        """Test EntityInfo default values."""
        entity = EntityInfo(name="Product")
        assert entity.mentions == 0
        assert entity.methods == []
        assert entity.attributes == []


class TestRelationshipInfo:
    """Tests for RelationshipInfo model."""

    def test_relationship_info_creation(self):
        """Test creating RelationshipInfo."""
        rel = RelationshipInfo(
            source="User",
            target="Order",
            relationship_type="association",
            description="User places Order",
            multiplicity="1..*"
        )
        assert rel.source == "User"
        assert rel.target == "Order"
        assert rel.relationship_type == "association"

    def test_relationship_info_required_fields(self):
        """Test that source, target, and type are required."""
        with pytest.raises(ValidationError):
            RelationshipInfo(source="User")


class TestDiagramAnalysisMetadata:
    """Tests for DiagramAnalysisMetadata model."""

    def test_metadata_creation(self):
        """Test creating DiagramAnalysisMetadata."""
        metadata = DiagramAnalysisMetadata(
            entities={"User": EntityInfo(name="User")},
            relationships=[],
            actions=["login", "search"],
            total_stories=5,
            entities_found=3,
            relationships_found=2,
            api_used="groq"
        )
        assert metadata.total_stories == 5
        assert metadata.api_used == "groq"

    def test_metadata_defaults(self):
        """Test DiagramAnalysisMetadata default values."""
        metadata = DiagramAnalysisMetadata()
        assert metadata.entities == {}
        assert metadata.relationships == []
        assert metadata.actions == []
        assert metadata.total_stories == 0


class TestUMLDiagramBase:
    """Tests for UMLDiagramBase model."""

    def test_diagram_base_creation(self):
        """Test creating UMLDiagramBase."""
        diagram = UMLDiagramBase(
            diagram_type="class",
            plantuml_code="@startuml\nclass User\n@enduml"
        )
        assert diagram.diagram_type == "class"
        assert "@startuml" in diagram.plantuml_code

    def test_diagram_base_requires_plantuml_code(self):
        """Test that plantuml_code is required."""
        with pytest.raises(ValidationError):
            UMLDiagramBase(diagram_type="class")

    def test_diagram_base_default_type(self):
        """Test default diagram type."""
        diagram = UMLDiagramBase(plantuml_code="@startuml\n@enduml")
        assert diagram.diagram_type == "class"


class TestUMLDiagramCreate:
    """Tests for UMLDiagramCreate model."""

    def test_diagram_create_valid(self):
        """Test valid UMLDiagramCreate."""
        diagram = UMLDiagramCreate(
            requirement_id=uuid4(),
            project_id=uuid4(),
            user_id=uuid4(),
            plantuml_code="@startuml\nclass User\n@enduml"
        )
        assert diagram.version == 1

    def test_diagram_create_with_svg(self):
        """Test UMLDiagramCreate with rendered SVG."""
        diagram = UMLDiagramCreate(
            requirement_id=uuid4(),
            project_id=uuid4(),
            user_id=uuid4(),
            plantuml_code="@startuml\n@enduml",
            rendered_svg="<svg>...</svg>",
            version=2
        )
        assert diagram.rendered_svg is not None
        assert diagram.version == 2


class TestUMLDiagramUpdate:
    """Tests for UMLDiagramUpdate model."""

    def test_diagram_update_all_optional(self):
        """Test that all update fields are optional."""
        update = UMLDiagramUpdate()
        assert update.plantuml_code is None
        assert update.rendered_svg is None
        assert update.version is None

    def test_diagram_update_partial(self):
        """Test partial update."""
        update = UMLDiagramUpdate(plantuml_code="@startuml\nclass Test\n@enduml")
        assert update.plantuml_code is not None


class TestUMLDiagramResponse:
    """Tests for UMLDiagramResponse model."""

    def test_diagram_response_valid(self):
        """Test valid UMLDiagramResponse."""
        now = datetime.now()
        response = UMLDiagramResponse(
            id=uuid4(),
            requirement_id=uuid4(),
            project_id=uuid4(),
            user_id=uuid4(),
            plantuml_code="@startuml\nclass User\n@enduml",
            version=1,
            created_at=now,
            updated_at=now
        )
        assert response.version == 1


class TestUMLGenerationRequest:
    """Tests for UMLGenerationRequest model."""

    def test_generation_request_defaults(self):
        """Test default values."""
        request = UMLGenerationRequest()
        assert request.user_story_ids is None
        assert request.regenerate == False

    def test_generation_request_with_stories(self):
        """Test with story IDs."""
        request = UMLGenerationRequest(
            user_story_ids=[uuid4(), uuid4()],
            regenerate=True
        )
        assert len(request.user_story_ids) == 2
        assert request.regenerate == True


class TestUMLGenerationResponse:
    """Tests for UMLGenerationResponse model."""

    def test_generation_response_valid(self):
        """Test valid UMLGenerationResponse."""
        now = datetime.now()
        response = UMLGenerationResponse(
            id=uuid4(),
            plantuml_code="@startuml\nclass User\n@enduml",
            svg_url="https://example.com/diagram.svg",
            png_url="https://example.com/diagram.png",
            analysis=DiagramAnalysisMetadata(),
            version=1,
            created_at=now
        )
        assert response.svg_url.endswith(".svg")


class TestUMLDiagramListResponse:
    """Tests for UMLDiagramListResponse model."""

    def test_list_response_empty(self):
        """Test empty list response."""
        response = UMLDiagramListResponse(
            diagrams=[],
            total=0
        )
        assert len(response.diagrams) == 0
        assert response.page == 1
        assert response.page_size == 10

    def test_list_response_with_diagrams(self):
        """Test list response with diagrams."""
        now = datetime.now()
        diagram = UMLDiagramResponse(
            id=uuid4(),
            requirement_id=uuid4(),
            project_id=uuid4(),
            user_id=uuid4(),
            plantuml_code="@startuml\n@enduml",
            version=1,
            created_at=now,
            updated_at=now
        )
        response = UMLDiagramListResponse(
            diagrams=[diagram],
            total=1,
            page=1,
            page_size=10
        )
        assert len(response.diagrams) == 1
        assert response.total == 1
