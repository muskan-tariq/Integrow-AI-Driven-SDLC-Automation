"""
Tests for Core Generators and Orchestrator
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from models.generated_code import (
    ParsedClass, ParsedAttribute, ParsedMethod, Visibility,
    CodeGenerationContext, CodeGenerationRequest, FileType
)
from agents.code_generation.generators import ModelGenerator, APIGenerator, ServiceGenerator
from agents.code_generation.orchestrator import CodeGenerationOrchestrator

@pytest.fixture
def mock_template_engine():
    engine = MagicMock()
    engine.generate_model.return_value = MagicMock(content="class TestModel:", file_path="model.py", file_type=FileType.MODEL)
    engine.generate_api_router.return_value = MagicMock(content="router = APIRouter()", file_path="router.py", file_type=FileType.API)
    engine.generate_service.return_value = MagicMock(content="class TestService:", file_path="service.py", file_type=FileType.SERVICE)
    return engine

@pytest.fixture
def mock_enhancer():
    enhancer = AsyncMock()
    enhancer.enhance_code.return_value = "# Enhanced Code"
    return enhancer

@pytest.fixture
def simple_class():
    return ParsedClass(
        name="Test",
        attributes=[],
        methods=[]
    )

@pytest.fixture
def context():
    return CodeGenerationContext(project_id="p1", requirement_id="r1")

class TestGenerators:
    
    @pytest.mark.asyncio
    async def test_model_generator(self, mock_template_engine, mock_enhancer, simple_class, context):
        generator = ModelGenerator(mock_template_engine, mock_enhancer)
        result = await generator.generate(simple_class, context)
        
        assert result.content == "# Enhanced Code"
        mock_template_engine.generate_model.assert_called_once()
        mock_enhancer.enhance_code.assert_called_once()

    @pytest.mark.asyncio
    async def test_api_generator(self, mock_template_engine, mock_enhancer, simple_class, context):
        generator = APIGenerator(mock_template_engine, mock_enhancer)
        result = await generator.generate(simple_class, context)
        
        assert result.content == "# Enhanced Code"
        mock_template_engine.generate_api_router.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_service_generator(self, mock_template_engine, mock_enhancer, simple_class, context):
        generator = ServiceGenerator(mock_template_engine, mock_enhancer)
        result = await generator.generate(simple_class, context)
        
        assert result.content == "# Enhanced Code"
        mock_template_engine.generate_service.assert_called_once()

class TestOrchestrator:

    @pytest.mark.asyncio
    async def test_orchestrator_flow(self):
        orchestrator = CodeGenerationOrchestrator()
        
        # Mock dependencies
        orchestrator.context_builder.build = AsyncMock()
        context = CodeGenerationContext(
            project_id="p1", 
            requirement_id="r1"
        )
        # Manually set parsed_uml
        from models.generated_code import ParsedUMLResult
        context.parsed_uml = ParsedUMLResult(
            classes=[ParsedClass(name="User")], 
            parse_success=True
        )
        orchestrator.context_builder.build.return_value = context
        
        # Mock generators
        orchestrator.model_gen.generate = AsyncMock(return_value=MagicMock(content="model code"))
        orchestrator.api_gen.generate = AsyncMock(return_value=MagicMock(content="api code"))
        orchestrator.service_gen.generate = AsyncMock(return_value=MagicMock(content="service code"))
        
        request = CodeGenerationRequest(
            project_id=uuid4(),
            requirement_id=uuid4(),
            generation_scope=["models", "api"]
        )
        
        result = await orchestrator.generate_code(request)
        
        assert result.total_files == 2
        orchestrator.model_gen.generate.assert_called_once()
        orchestrator.api_gen.generate.assert_called_once()
        orchestrator.service_gen.generate.assert_not_called()
