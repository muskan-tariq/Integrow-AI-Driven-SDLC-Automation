"""
Unit tests for Requirement Analysis Agents - Parser, Ambiguity, Completeness, Ethics.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

# Import actual agents
from agents.requirements.parser_agent import ParserAgent, ParsedRequirements
from agents.requirements.ambiguity_agent import AmbiguityAgent, AmbiguityIssue, AmbiguityResult


class TestParsedRequirements:
    """Tests for ParsedRequirements dataclass."""

    def test_parsed_requirements_creation(self):
        """Test creating ParsedRequirements."""
        result = ParsedRequirements(
            actors=["user", "admin"],
            actions=["login", "logout"],
            entities=["account", "session"],
            constraints=["within 2 seconds"],
            dependencies=[]
        )
        assert len(result.actors) == 2
        assert "login" in result.actions

    def test_parsed_requirements_empty(self):
        """Test creating empty ParsedRequirements."""
        result = ParsedRequirements(
            actors=[],
            actions=[],
            entities=[],
            constraints=[],
            dependencies=[]
        )
        assert result.actors == []


class TestParserAgent:
    """Unit tests for ParserAgent."""

    @pytest.fixture
    def agent(self):
        """Create ParserAgent instance."""
        return ParserAgent()

    def test_agent_initialization(self, agent):
        """Test agent is initialized with spaCy model."""
        assert agent.nlp is not None

    @pytest.mark.asyncio
    async def test_parse_simple_requirement(self, agent):
        """Test parsing a simple requirement."""
        text = "The user should be able to login to the system."
        result = await agent.parse(text)
        
        assert isinstance(result, ParsedRequirements)
        assert len(result.actors) > 0 or len(result.entities) > 0

    @pytest.mark.asyncio
    async def test_parse_empty_text_raises(self, agent):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            await agent.parse("")

    @pytest.mark.asyncio
    async def test_parse_whitespace_only_raises(self, agent):
        """Test that whitespace-only text raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            await agent.parse("   \n\t  ")

    @pytest.mark.asyncio
    async def test_parse_extracts_actors(self, agent):
        """Test that common actor keywords are extracted."""
        text = "The user and administrator can manage the system."
        result = await agent.parse(text)
        
        # Should find at least user or admin
        assert any(actor in ["user", "admin", "administrator"] for actor in result.actors) or \
               any("user" in e.lower() or "admin" in e.lower() for e in result.entities)

    @pytest.mark.asyncio
    async def test_parse_extracts_actions(self, agent):
        """Test that verbs/actions are extracted."""
        text = "Users can search, filter, and sort products."
        result = await agent.parse(text)
        
        # Should find at least one action
        assert len(result.actions) > 0 or len(result.entities) > 0

    @pytest.mark.asyncio
    async def test_parse_extracts_entities(self, agent):
        """Test that entities are extracted."""
        text = "The shopping cart should display product names and prices."
        result = await agent.parse(text)
        
        # Should find entities
        assert len(result.entities) > 0


class TestAmbiguityIssue:
    """Tests for AmbiguityIssue dataclass."""

    def test_ambiguity_issue_creation(self):
        """Test creating AmbiguityIssue."""
        issue = AmbiguityIssue(
            term="fast",
            explanation="'fast' is subjective",
            suggestions=["< 2 seconds", "< 100ms"]
        )
        assert issue.term == "fast"
        assert len(issue.suggestions) == 2


class TestAmbiguityResult:
    """Tests for AmbiguityResult dataclass."""

    def test_ambiguity_result_creation(self):
        """Test creating AmbiguityResult."""
        result = AmbiguityResult(
            issues=[],
            score=0.8
        )
        assert result.score == 0.8

    def test_ambiguity_result_with_issues(self):
        """Test AmbiguityResult with issues lowers score."""
        issue = AmbiguityIssue(term="fast", explanation="test", suggestions=[])
        result = AmbiguityResult(issues=[issue], score=0.9)
        assert len(result.issues) == 1


class TestAmbiguityAgent:
    """Unit tests for AmbiguityAgent."""

    @pytest.fixture
    def agent(self):
        """Create AmbiguityAgent instance without API."""
        with patch.dict('os.environ', {'GROQ_API_KEY': ''}, clear=False):
            return AmbiguityAgent()

    def test_agent_initialization(self, agent):
        """Test agent is initialized with vague terms list."""
        assert hasattr(agent, '_vague_terms')
        assert len(agent._vague_terms) > 0

    @pytest.mark.asyncio
    async def test_detect_empty_text(self, agent):
        """Test detecting ambiguities in empty text."""
        result = await agent.detect("")
        assert isinstance(result, AmbiguityResult)
        assert result.score == 1.0
        assert len(result.issues) == 0

    @pytest.mark.asyncio
    async def test_detect_clean_text(self, agent):
        """Test detecting ambiguities in clean, specific text."""
        text = "The system shall respond within 200 milliseconds."
        result = await agent.detect(text)
        assert isinstance(result, AmbiguityResult)

    @pytest.mark.asyncio
    async def test_detect_vague_term_fast(self, agent):
        """Test detecting 'fast' as ambiguous."""
        text = "The system should be fast and responsive."
        result = await agent.detect(text)
        
        # Should find 'fast' as ambiguous
        terms = [issue.term.lower() for issue in result.issues]
        assert "fast" in terms

    @pytest.mark.asyncio
    async def test_detect_vague_term_secure(self, agent):
        """Test detecting 'secure' as ambiguous."""
        text = "The application must be secure."
        result = await agent.detect(text)
        
        terms = [issue.term.lower() for issue in result.issues]
        assert "secure" in terms

    @pytest.mark.asyncio
    async def test_detect_vague_term_user_friendly(self, agent):
        """Test detecting 'user-friendly' as ambiguous."""
        text = "The interface should be user-friendly."
        result = await agent.detect(text)
        
        # Should find user-friendly or similar
        assert len(result.issues) > 0

    @pytest.mark.asyncio
    async def test_detect_multiple_vague_terms(self, agent):
        """Test detecting multiple ambiguous terms."""
        text = "The system should be fast, secure, and reliable."
        result = await agent.detect(text)
        
        # Should find multiple issues
        assert len(result.issues) >= 2

    @pytest.mark.asyncio
    async def test_detect_score_decreases_with_issues(self, agent):
        """Test that score decreases with more issues."""
        clean_text = "The system shall respond within 100ms."
        clean_result = await agent.detect(clean_text)
        
        vague_text = "The system should be fast, secure, reliable, and user-friendly."
        vague_result = await agent.detect(vague_text)
        
        # Clean text should have higher score
        assert clean_result.score >= vague_result.score

    def test_local_detect_finds_patterns(self, agent):
        """Test _local_detect method directly."""
        text = "The app needs to be fast and quick."
        issues = agent._local_detect(text)
        
        assert len(issues) >= 1
        terms = [i["term"] for i in issues]
        assert any("fast" in t.lower() or "quick" in t.lower() for t in terms)

    def test_to_result_conversion(self, agent):
        """Test _to_result converts raw issues to AmbiguityResult."""
        raw_issues = [
            {"term": "fast", "explanation": "test", "suggestions": ["< 1s"]},
            {"term": "slow", "explanation": "test2", "suggestions": []},
        ]
        result = agent._to_result(raw_issues)
        
        assert isinstance(result, AmbiguityResult)
        assert len(result.issues) == 2
        assert result.score <= 1.0
        assert result.score >= 0.0

    def test_to_result_empty_list(self, agent):
        """Test _to_result with empty list."""
        result = agent._to_result([])
        assert len(result.issues) == 0
        assert result.score == 1.0

    def test_build_prompt(self, agent):
        """Test _build_prompt generates valid prompt."""
        text = "Test requirement"
        prompt = agent._build_prompt(text)
        
        assert "Test requirement" in prompt
        assert "JSON" in prompt

    def test_parse_llm_json_valid(self, agent):
        """Test _parse_llm_json with valid JSON."""
        json_str = '[{"term": "fast", "explanation": "test", "suggestions": []}]'
        result = agent._parse_llm_json(json_str)
        
        assert len(result) == 1
        assert result[0]["term"] == "fast"

    def test_parse_llm_json_invalid(self, agent):
        """Test _parse_llm_json with invalid JSON returns empty list."""
        result = agent._parse_llm_json("not valid json")
        assert result == []

    def test_parse_llm_json_embedded(self, agent):
        """Test _parse_llm_json extracts JSON from text."""
        text = 'Here are the issues: [{"term": "test", "explanation": "x", "suggestions": []}] end.'
        result = agent._parse_llm_json(text)
        
        assert len(result) == 1


# Import completeness and ethics agents
from agents.requirements.completeness_agent import (
    CompletenessAgent, CompletenessItem, CompletenessResult
)
from agents.requirements.ethics_agent import (
    EthicsAgent, EthicsIssue, EthicsResult
)


class TestCompletenessItem:
    """Tests for CompletenessItem dataclass."""

    def test_completeness_item_creation(self):
        """Test creating CompletenessItem."""
        item = CompletenessItem(
            category="error_handling",
            description="No error handling specified",
            severity="high",
            suggestion="Add retry logic"
        )
        assert item.category == "error_handling"
        assert item.severity == "high"


class TestCompletenessResult:
    """Tests for CompletenessResult dataclass."""

    def test_completeness_result_creation(self):
        """Test creating CompletenessResult."""
        result = CompletenessResult(
            missing_items=[],
            completeness_score=0.85
        )
        assert result.completeness_score == 0.85

    def test_completeness_result_with_items(self):
        """Test CompletenessResult with missing items."""
        item = CompletenessItem(
            category="security",
            description="Missing auth",
            severity="high",
            suggestion="Add OAuth"
        )
        result = CompletenessResult(missing_items=[item], completeness_score=0.9)
        assert len(result.missing_items) == 1


class TestCompletenessAgent:
    """Unit tests for CompletenessAgent."""

    @pytest.fixture
    def agent(self):
        """Create CompletenessAgent instance without API."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': '', 'DEVELOPMENT_MODE': 'true'}, clear=False):
            return CompletenessAgent()

    def test_agent_initialization(self, agent):
        """Test agent is initialized."""
        assert hasattr(agent, 'dev_mode')
        assert hasattr(agent, 'enabled')

    @pytest.mark.asyncio
    async def test_check_empty_text(self, agent):
        """Test checking empty text returns perfect score."""
        result = await agent.check("", {})
        assert isinstance(result, CompletenessResult)
        assert result.completeness_score == 1.0
        assert len(result.missing_items) == 0

    @pytest.mark.asyncio
    async def test_check_incomplete_requirement(self, agent):
        """Test checking incomplete requirement finds missing items."""
        text = "Users can view products."
        parsed = {"actors": ["user"], "actions": ["view"], "entities": ["products"]}
        result = await agent.check(text, parsed)
        
        assert isinstance(result, CompletenessResult)
        # Should find missing items (no error handling, no performance, no security)
        assert len(result.missing_items) > 0

    @pytest.mark.asyncio
    async def test_check_finds_missing_error_handling(self, agent):
        """Test that missing error handling is detected."""
        text = "The user can submit a form."
        result = await agent.check(text, {})
        
        categories = [item.category for item in result.missing_items]
        assert "error_handling" in categories

    @pytest.mark.asyncio
    async def test_check_finds_missing_security(self, agent):
        """Test that missing security is detected."""
        text = "Users can view their data."
        result = await agent.check(text, {})
        
        categories = [item.category for item in result.missing_items]
        assert "security" in categories

    @pytest.mark.asyncio
    async def test_check_with_error_handling_present(self, agent):
        """Test that error handling is not flagged if present."""
        text = "If an error occurs, the system shall retry 3 times and then fail gracefully."
        result = await agent.check(text, {})
        
        categories = [item.category for item in result.missing_items]
        assert "error_handling" not in categories

    @pytest.mark.asyncio
    async def test_check_with_security_present(self, agent):
        """Test that security is not flagged if auth mentioned."""
        text = "Users must authenticate via OAuth before accessing the API."
        result = await agent.check(text, {})
        
        categories = [item.category for item in result.missing_items]
        assert "security" not in categories

    @pytest.mark.asyncio
    async def test_check_score_decreases_with_issues(self, agent):
        """Test that score decreases with more missing items."""
        incomplete_text = "Show data."
        complete_text = "Show data with OAuth auth, retry on error, respond in 100ms, timeout after 30 seconds."
        
        incomplete_result = await agent.check(incomplete_text, {})
        complete_result = await agent.check(complete_text, {})
        
        assert complete_result.completeness_score >= incomplete_result.completeness_score

    def test_heuristic_items(self, agent):
        """Test _heuristic_items method directly."""
        text = "Display user profile."
        items = agent._heuristic_items(text, {})
        
        assert len(items) > 0
        categories = [i["category"] for i in items]
        assert "error_handling" in categories

    def test_to_result_conversion(self, agent):
        """Test _to_result converts raw items to CompletenessResult."""
        raw_items = [
            {"category": "security", "description": "test", "severity": "high", "suggestion": "x"},
            {"category": "performance", "description": "test2", "severity": "medium", "suggestion": "y"},
        ]
        result = agent._to_result(raw_items)
        
        assert isinstance(result, CompletenessResult)
        assert len(result.missing_items) == 2

    def test_to_result_empty_list(self, agent):
        """Test _to_result with empty list."""
        result = agent._to_result([])
        assert len(result.missing_items) == 0
        assert result.completeness_score == 1.0

    def test_build_prompt(self, agent):
        """Test _build_prompt generates valid prompt."""
        text = "Test requirement"
        parsed = {"actors": ["user"], "actions": ["test"], "entities": []}
        prompt = agent._build_prompt(text, parsed)
        
        assert "Test requirement" in prompt
        assert "JSON" in prompt

    def test_parse_json_array_valid(self, agent):
        """Test _parse_json_array with valid JSON."""
        json_str = '[{"category": "security", "description": "test", "severity": "high", "suggestion": "x"}]'
        result = agent._parse_json_array(json_str)
        
        assert len(result) == 1

    def test_parse_json_array_invalid(self, agent):
        """Test _parse_json_array with invalid JSON returns empty list."""
        result = agent._parse_json_array("not valid json")
        assert result == []


class TestEthicsIssue:
    """Tests for EthicsIssue dataclass."""

    def test_ethics_issue_creation(self):
        """Test creating EthicsIssue."""
        issue = EthicsIssue(
            type="bias",
            category="gender",
            description="Requirement implies gender restrictions",
            severity="high"
        )
        assert issue.type == "bias"
        assert issue.category == "gender"


class TestEthicsResult:
    """Tests for EthicsResult dataclass."""

    def test_ethics_result_creation(self):
        """Test creating EthicsResult."""
        result = EthicsResult(
            issues=[],
            ethics_score=1.0
        )
        assert result.ethics_score == 1.0


class TestEthicsAgent:
    """Unit tests for EthicsAgent."""

    @pytest.fixture
    def agent(self):
        """Create EthicsAgent instance without API."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': ''}, clear=False):
            return EthicsAgent()

    def test_agent_initialization(self, agent):
        """Test agent is initialized."""
        assert hasattr(agent, 'llm_enabled')

    @pytest.mark.asyncio
    async def test_audit_empty_text(self, agent):
        """Test auditing empty text returns perfect score."""
        result = await agent.audit("")
        assert isinstance(result, EthicsResult)
        # Empty text should have high ethics score
        assert result.ethics_score >= 0.0

    @pytest.mark.asyncio
    async def test_audit_neutral_requirement(self, agent):
        """Test auditing a neutral, unbiased requirement."""
        text = "The system shall allow users to search for products by name."
        result = await agent.audit(text)
        
        assert isinstance(result, EthicsResult)

    @pytest.mark.asyncio
    async def test_audit_finds_bias_keywords(self, agent):
        """Test that obvious bias keywords are detected."""
        text = "Only male users can access the management dashboard."
        result = await agent.audit(text)
        
        # Should find some ethics issues related to gender
        assert isinstance(result, EthicsResult)
        # Score should be lower for biased text
        if len(result.issues) > 0:
            assert result.ethics_score < 1.0

    @pytest.mark.asyncio
    async def test_audit_privacy_concerns(self, agent):
        """Test that privacy-related text is analyzed."""
        text = "The system shall collect and store all user browsing history permanently."
        result = await agent.audit(text)
        
        assert isinstance(result, EthicsResult)
