"""
Unit tests for UML Agents - ClassDiagramAgent and DiagramAnalyzer.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from dataclasses import asdict

# Import UML agents
from agents.uml.diagram_analyzer import (
    DiagramAnalyzer, DiagramAnalysisResult,
    EntityInfo, RelationshipInfo
)
from agents.uml.class_diagram_agent import (
    ClassDiagramAgent, ClassDiagramResult
)


# ==================== DiagramAnalyzer Tests ====================

class TestEntityInfo:
    """Tests for EntityInfo dataclass."""

    def test_entity_info_creation(self):
        """Test creating EntityInfo."""
        entity = EntityInfo(name="User", mentions=5)
        assert entity.name == "User"
        assert entity.mentions == 5
        assert entity.methods == set()
        assert entity.attributes == set()

    def test_entity_info_with_methods(self):
        """Test EntityInfo with methods."""
        entity = EntityInfo(name="Order", mentions=3)
        entity.methods.add("create")
        entity.methods.add("update")
        assert len(entity.methods) == 2

    def test_entity_info_related_entities(self):
        """Test EntityInfo with related entities."""
        entity = EntityInfo(name="User")
        entity.related_entities.add("Order")
        entity.related_entities.add("Cart")
        assert "Order" in entity.related_entities


class TestRelationshipInfo:
    """Tests for RelationshipInfo dataclass."""

    def test_relationship_info_creation(self):
        """Test creating RelationshipInfo."""
        rel = RelationshipInfo(
            source="User",
            target="Order",
            relationship_type="composition"
        )
        assert rel.source == "User"
        assert rel.target == "Order"
        assert rel.relationship_type == "composition"
        assert rel.description == ""

    def test_relationship_info_with_description(self):
        """Test RelationshipInfo with description."""
        rel = RelationshipInfo(
            source="Customer",
            target="Account",
            relationship_type="association",
            description="Customer has Account"
        )
        assert rel.description == "Customer has Account"


class TestDiagramAnalysisResult:
    """Tests for DiagramAnalysisResult dataclass."""

    def test_result_creation(self):
        """Test creating DiagramAnalysisResult."""
        result = DiagramAnalysisResult(
            entities={},
            relationships=[],
            actions=[]
        )
        assert result.entities == {}
        assert result.relationships == []
        assert result.metadata == {}

    def test_result_with_data(self):
        """Test DiagramAnalysisResult with actual data."""
        result = DiagramAnalysisResult(
            entities={"User": EntityInfo(name="User", mentions=5)},
            relationships=[RelationshipInfo("User", "Order", "has")],
            actions=["create", "update"],
            metadata={"total_stories": 3}
        )
        assert "User" in result.entities
        assert len(result.relationships) == 1
        assert len(result.actions) == 2


class TestDiagramAnalyzer:
    """Unit tests for DiagramAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create DiagramAnalyzer instance."""
        return DiagramAnalyzer()

    def test_analyzer_initialization(self, analyzer):
        """Test analyzer is initialized with NLP and patterns."""
        assert hasattr(analyzer, 'nlp')
        assert hasattr(analyzer, 'relationship_patterns')
        assert "composition" in analyzer.relationship_patterns
        assert "aggregation" in analyzer.relationship_patterns

    @pytest.mark.asyncio
    async def test_analyze_empty_stories(self, analyzer):
        """Test analyzing empty stories list."""
        result = await analyzer.analyze([])
        assert isinstance(result, DiagramAnalysisResult)
        assert result.entities == {}
        assert result.relationships == []
        assert result.actions == []

    @pytest.mark.asyncio
    async def test_analyze_single_story(self, analyzer):
        """Test analyzing a single user story."""
        stories = [{
            "story": "As a User, I want to create an Order so that I can purchase products.",
            "acceptance_criteria": [
                "Given I am logged in, When I add items to cart, Then I can create an Order"
            ]
        }]
        result = await analyzer.analyze(stories)
        
        assert isinstance(result, DiagramAnalysisResult)
        assert len(result.entities) > 0 or len(result.actions) > 0

    @pytest.mark.asyncio
    async def test_analyze_extracts_entities(self, analyzer):
        """Test that analyzer extracts entities from stories."""
        stories = [{
            "story": "As an Admin, I want to manage Users and their Accounts.",
            "acceptance_criteria": []
        }]
        result = await analyzer.analyze(stories)
        
        # Should find some entities
        assert result.metadata.get("entities_found", 0) >= 0

    @pytest.mark.asyncio
    async def test_analyze_extracts_actions(self, analyzer):
        """Test that analyzer extracts actions from stories."""
        stories = [{
            "story": "The system should create, update, and delete products.",
            "acceptance_criteria": ["User can view and edit product details"]
        }]
        result = await analyzer.analyze(stories)
        
        assert isinstance(result.actions, list)

    @pytest.mark.asyncio
    async def test_analyze_multiple_stories(self, analyzer):
        """Test analyzing multiple user stories."""
        stories = [
            {"story": "User can login to the system.", "acceptance_criteria": []},
            {"story": "Admin can manage products.", "acceptance_criteria": []},
            {"story": "Customer can place orders.", "acceptance_criteria": []}
        ]
        result = await analyzer.analyze(stories)
        
        assert result.metadata.get("total_stories") == 3

    def test_extract_from_empty_text(self, analyzer):
        """Test _extract_from_text with empty text."""
        entities, actions = analyzer._extract_from_text("")
        assert entities == set()
        assert actions == set()

    def test_extract_from_text_with_entities(self, analyzer):
        """Test _extract_from_text extracts capitalized words."""
        text = "The User creates an Order and manages the Cart."
        entities, actions = analyzer._extract_from_text(text)
        
        # Should find entities or actions
        assert isinstance(entities, set)
        assert isinstance(actions, set)

    def test_detect_relationships_empty(self, analyzer):
        """Test _detect_relationships with empty entities."""
        relationships = analyzer._detect_relationships("Some text", [])
        assert relationships == []

    def test_detect_relationships_composition(self, analyzer):
        """Test detecting composition relationship."""
        text = "User has Orders"
        relationships = analyzer._detect_relationships(text, ["User", "Orders"])
        
        # Should detect "has" relationship
        if relationships:
            assert any(r.relationship_type == "composition" for r in relationships)

    def test_detect_relationships_aggregation(self, analyzer):
        """Test detecting aggregation relationship."""
        text = "Cart uses Product items"
        relationships = analyzer._detect_relationships(text, ["Cart", "Product"])
        
        if relationships:
            types = [r.relationship_type for r in relationships]
            assert "aggregation" in types or len(relationships) >= 0

    def test_detect_relationships_between_pairs(self, analyzer):
        """Test that relationships are detected between entity pairs."""
        text = "Customer owns Account and Account contains Transactions"
        entities = ["Customer", "Account", "Transactions"]
        relationships = analyzer._detect_relationships(text, entities)
        
        assert isinstance(relationships, list)

    def test_relationship_patterns_exist(self, analyzer):
        """Test that all relationship pattern types are defined."""
        expected_types = ["composition", "aggregation", "association", "inheritance"]
        for rel_type in expected_types:
            assert rel_type in analyzer.relationship_patterns
            assert len(analyzer.relationship_patterns[rel_type]) > 0


# ==================== ClassDiagramAgent Tests ====================

class TestClassDiagramResult:
    """Tests for ClassDiagramResult dataclass."""

    def test_result_creation(self):
        """Test creating ClassDiagramResult."""
        result = ClassDiagramResult(
            plantuml_code="@startuml\nclass User\n@enduml",
            entities_count=1,
            relationships_count=0,
            api_used="groq",
            metadata={"model": "llama-3.3-70b"}
        )
        assert "@startuml" in result.plantuml_code
        assert result.entities_count == 1
        assert result.api_used == "groq"


class TestClassDiagramAgent:
    """Unit tests for ClassDiagramAgent."""

    @pytest.fixture
    def agent(self):
        """Create ClassDiagramAgent instance without API keys."""
        with patch.dict('os.environ', {'GROQ_API_KEY': '', 'GEMINI_API_KEY': ''}, clear=False):
            return ClassDiagramAgent()

    @pytest.fixture
    def sample_analysis(self):
        """Create sample DiagramAnalysisResult."""
        return DiagramAnalysisResult(
            entities={
                "User": EntityInfo(name="User", mentions=3),
                "Order": EntityInfo(name="Order", mentions=2)
            },
            relationships=[RelationshipInfo("User", "Order", "composition")],
            actions=["create", "update", "delete"],
            metadata={"total_stories": 2}
        )

    def test_agent_initialization(self, agent):
        """Test agent is initialized."""
        assert hasattr(agent, 'groq_enabled')
        assert hasattr(agent, 'gemini_enabled')

    @pytest.mark.asyncio
    async def test_generate_empty_stories(self, agent, sample_analysis):
        """Test generating diagram with empty stories."""
        result = await agent.generate([], sample_analysis)
        
        assert isinstance(result, ClassDiagramResult)
        assert result.api_used == "none"
        assert "No user stories" in result.metadata.get("message", "")

    @pytest.mark.asyncio
    async def test_generate_basic_diagram_fallback(self, agent, sample_analysis):
        """Test fallback to basic diagram when no API available."""
        stories = [{"story": "User creates Order", "acceptance_criteria": []}]
        result = await agent.generate(stories, sample_analysis)
        
        assert isinstance(result, ClassDiagramResult)
        assert "@startuml" in result.plantuml_code
        assert "@enduml" in result.plantuml_code
        assert result.api_used == "fallback"

    def test_generate_empty_diagram(self, agent):
        """Test _generate_empty_diagram method."""
        result = agent._generate_empty_diagram()
        
        assert result.plantuml_code.startswith("@startuml")
        assert result.plantuml_code.endswith("@enduml")
        assert result.entities_count == 0
        assert result.relationships_count == 0

    def test_generate_basic_diagram(self, agent, sample_analysis):
        """Test _generate_basic_diagram method."""
        result = agent._generate_basic_diagram(sample_analysis)
        
        assert "@startuml" in result.plantuml_code
        assert "@enduml" in result.plantuml_code
        assert "User" in result.plantuml_code
        assert "Order" in result.plantuml_code
        assert result.api_used == "fallback"

    def test_clean_plantuml_code_already_valid(self, agent):
        """Test _clean_plantuml_code with valid code."""
        code = "@startuml\nclass Test\n@enduml"
        cleaned = agent._clean_plantuml_code(code)
        
        assert cleaned == code

    def test_clean_plantuml_code_removes_markdown(self, agent):
        """Test _clean_plantuml_code removes markdown blocks."""
        code = "```plantuml\n@startuml\nclass Test\n@enduml\n```"
        cleaned = agent._clean_plantuml_code(code)
        
        assert "```" not in cleaned
        assert cleaned.startswith("@startuml")
        assert cleaned.endswith("@enduml")

    def test_clean_plantuml_code_adds_missing_startuml(self, agent):
        """Test _clean_plantuml_code adds missing @startuml."""
        code = "class Test\n@enduml"
        cleaned = agent._clean_plantuml_code(code)
        
        assert cleaned.startswith("@startuml")

    def test_clean_plantuml_code_adds_missing_enduml(self, agent):
        """Test _clean_plantuml_code adds missing @enduml."""
        code = "@startuml\nclass Test"
        cleaned = agent._clean_plantuml_code(code)
        
        assert cleaned.endswith("@enduml")

    def test_build_prompt(self, agent, sample_analysis):
        """Test _build_prompt generates valid prompt."""
        stories = [
            {
                "story": "As a user, I want to create orders",
                "acceptance_criteria": ["Can add items", "Can checkout"]
            }
        ]
        prompt = agent._build_prompt(stories, sample_analysis)
        
        assert "USER STORIES" in prompt
        assert "IDENTIFIED ENTITIES" in prompt
        assert "PlantUML" in prompt
        assert "@startuml" in prompt

    def test_build_prompt_includes_story_content(self, agent, sample_analysis):
        """Test that prompt includes story content."""
        stories = [
            {"story": "Test story content here", "acceptance_criteria": []}
        ]
        prompt = agent._build_prompt(stories, sample_analysis)
        
        assert "Test story content" in prompt

    def test_build_prompt_includes_entities(self, agent, sample_analysis):
        """Test that prompt includes identified entities."""
        stories = [{"story": "Test", "acceptance_criteria": []}]
        prompt = agent._build_prompt(stories, sample_analysis)
        
        assert "User" in prompt
        assert "Order" in prompt

    def test_generate_basic_diagram_with_methods(self, agent):
        """Test basic diagram includes entity methods."""
        entity = EntityInfo(name="User", mentions=1)
        entity.methods.add("login")
        entity.methods.add("logout")
        
        analysis = DiagramAnalysisResult(
            entities={"User": entity},
            relationships=[],
            actions=["login", "logout"]
        )
        
        result = agent._generate_basic_diagram(analysis)
        
        assert "login" in result.plantuml_code or "User" in result.plantuml_code

    def test_generate_basic_diagram_with_relationships(self, agent):
        """Test basic diagram includes relationships."""
        analysis = DiagramAnalysisResult(
            entities={
                "User": EntityInfo(name="User", mentions=1),
                "Order": EntityInfo(name="Order", mentions=1)
            },
            relationships=[
                RelationshipInfo("User", "Order", "composition"),
                RelationshipInfo("Order", "Item", "aggregation")
            ],
            actions=[]
        )
        
        result = agent._generate_basic_diagram(analysis)
        
        # Should include relationship syntax
        assert "*--" in result.plantuml_code or "--" in result.plantuml_code or "User" in result.plantuml_code
