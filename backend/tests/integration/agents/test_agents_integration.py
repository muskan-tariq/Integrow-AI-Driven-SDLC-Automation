"""
Integration tests for Agents - testing how they work together without external APIs.
"""
import pytest
import dataclasses
from unittest.mock import AsyncMock, MagicMock, patch

# Import agents
from agents.requirements.parser_agent import ParserAgent
from agents.requirements.ambiguity_agent import AmbiguityAgent, AmbiguityResult
from agents.requirements.completeness_agent import CompletenessAgent, CompletenessResult
from agents.requirements.ethics_agent import EthicsAgent, EthicsResult
from agents.uml.diagram_analyzer import DiagramAnalyzer, DiagramAnalysisResult
from agents.uml.class_diagram_agent import ClassDiagramAgent, ClassDiagramResult


class TestRequirementsAgentsIntegration:
    """Integration tests for requirements analysis agents workflow."""

    @pytest.fixture
    def parser_agent(self):
        return ParserAgent()

    @pytest.fixture
    def ambiguity_agent(self):
        with patch.dict('os.environ', {'GROQ_API_KEY': '', 'DEVELOPMENT_MODE': 'true'}, clear=False):
            return AmbiguityAgent()

    @pytest.fixture
    def completeness_agent(self):
        with patch.dict('os.environ', {'GEMINI_API_KEY': '', 'DEVELOPMENT_MODE': 'true'}, clear=False):
            return CompletenessAgent()
            
    @pytest.fixture
    def ethics_agent(self):
        return EthicsAgent()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_analysis_workflow_integration(
        self, parser_agent, ambiguity_agent, completeness_agent, ethics_agent
    ):
        """
        Test the sequential flow of data between agents:
        Parser -> (Parsed Data) -> Ambiguity/Completeness/Ethics
        """
        # 1. Input Requirement
        requirement_text = "The User should be able to login quickly via the system."
        
        # 2. Run Parser Agent
        # parse is async
        parsed_result = await parser_agent.parse(requirement_text)
        
        # Verify Parser Output
        assert parsed_result is not None
        # It's a dataclass, so use attribute access
        assert hasattr(parsed_result, "actors")
        # "User" should be identified as an actor
        assert "User" in parsed_result.actors or "user" in parsed_result.actors

        # 3. Pass Parsed Data to Other Agents
        
        # Ambiguity Check: method is 'detect', not 'check'
        ambiguity_result = await ambiguity_agent.detect(requirement_text)
        assert isinstance(ambiguity_result, AmbiguityResult)
        # "quickly" should be flagged as ambiguous by the heuristic fallback
        assert any("quickly" in issue.term.lower() for issue in ambiguity_result.issues)

        # Completeness Check (needs parsed entities as dict)
        # Convert dataclass to dict for compatibility if agent expects dict
        parsed_dict = dataclasses.asdict(parsed_result)
        completeness_result = await completeness_agent.check(requirement_text, parsed_dict)
        assert isinstance(completeness_result, CompletenessResult)
        
        # Ethics Check: method is 'audit'
        ethics_result = await ethics_agent.audit(requirement_text)
        assert isinstance(ethics_result, EthicsResult)
        
        # 4. Verify Overall Data Compatibility
        assert completeness_result.completeness_score >= 0.0


class TestUMLAgentsIntegration:
    """Integration tests for UML generation workflow."""
    
    @pytest.fixture
    def diagram_analyzer(self):
        return DiagramAnalyzer()
        
    @pytest.fixture
    def class_diagram_agent(self):
        with patch.dict('os.environ', {'GROQ_API_KEY': '', 'GEMINI_API_KEY': ''}, clear=False):
            return ClassDiagramAgent()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_uml_generation_pipeline(self, diagram_analyzer, class_diagram_agent):
        """
        Test flow: User Stories -> DiagramAnalyzer -> ClassDiagramAgent
        """
        # 1. Input User Stories
        user_stories = [
            {
                "story": "As a Customer, I want to view Products so that I can buy them.",
                "acceptance_criteria": ["Customer can see list", "Customer can click details"]
            },
            {
                "story": "As a Customer, I want to add Products to my Cart.",
                "acceptance_criteria": ["Cart updates total"]
            }
        ]
        
        # 2. Analyze User Stories (DiagramAnalyzer)
        analysis_result = await diagram_analyzer.analyze(user_stories)
        
        # Verify Analysis
        assert isinstance(analysis_result, DiagramAnalysisResult)
        assert "Customer" in analysis_result.entities
        assert "Product" in analysis_result.entities
        
        # 3. Generate Diagram Code (ClassDiagramAgent)
        # Using the analysis result from step 2
        diagram_result = await class_diagram_agent.generate(user_stories, analysis_result)
        
        # Verify Diagram Generation
        assert isinstance(diagram_result, ClassDiagramResult)
        assert "@startuml" in diagram_result.plantuml_code
        
        # Verify that entities found by analyzer are present in the final diagram code (even in basic fallback)
        assert "Customer" in diagram_result.plantuml_code
        assert "Product" in diagram_result.plantuml_code


