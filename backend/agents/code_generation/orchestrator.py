"""
Code Generation Orchestrator

Main entry point for the code generation pipeline.
Coordinates context building, parsing, and execution of generators.
"""

from __future__ import annotations

import logging
import asyncio
from typing import List
from uuid import uuid4

from models.generated_code import (
    CodeGenerationRequest,
    CodeGenerationResult,
    CodeGenerationContext,
    GenerationStatus,
    GeneratedFile,
)
from agents.code_generation.context_builder import ContextBuilder
from agents.code_generation.template_engine import TemplateEngine
from agents.code_generation.code_enhancer import CodeEnhancerAgent
from agents.code_generation.generators import (
    ModelGenerator,
    APIGenerator,
    ServiceGenerator,
)

logger = logging.getLogger(__name__)


class CodeGenerationOrchestrator:
    """
    Orchestrates the entire code generation process.
    """

    def __init__(self):
        self.context_builder = ContextBuilder()
        self.template_engine = TemplateEngine()
        self.enhancer = CodeEnhancerAgent()
        
        # Initialize generators
        self.model_gen = ModelGenerator(self.template_engine, self.enhancer)
        self.api_gen = APIGenerator(self.template_engine, self.enhancer)
        self.service_gen = ServiceGenerator(self.template_engine, self.enhancer)

    async def generate_code(self, request: CodeGenerationRequest) -> CodeGenerationResult:
        """
        Execute the code generation pipeline.

        Args:
            request: The generation request

        Returns:
            CodeGenerationResult containing generated files
        """
        session_id = uuid4()
        start_time = asyncio.get_event_loop().time()
        
        result = CodeGenerationResult(
            session_id=session_id,
            requirement_id=request.requirement_id,
            status=GenerationStatus.GENERATING
        )

        try:
            # 1. Build Context
            logger.info(f"Building context for request {session_id}")
            context = await self.context_builder.build(
                project_id=str(request.project_id),
                requirement_id=str(request.requirement_id),
                uml_diagram_id=str(request.uml_diagram_id) if request.uml_diagram_id else None,
                tech_stack=request.tech_stack,
                generation_scope=request.generation_scope
            )

            if not context.parsed_uml or not context.parsed_uml.classes:
                result.status = GenerationStatus.REJECTED
                logger.error("No classes found in UML context")
                return result

            # 2. Generate Files
            logger.info(f"Generating code for {len(context.parsed_uml.classes)} classes")
            
            all_generation_tasks = []
            for parsed_class in context.parsed_uml.classes:
                # Add generators based on scope
                if "models" in request.generation_scope:
                    all_generation_tasks.append(self.model_gen.generate(parsed_class, context))
                
                if "api" in request.generation_scope:
                    all_generation_tasks.append(self.api_gen.generate(parsed_class, context))
                
                if "services" in request.generation_scope:
                    all_generation_tasks.append(self.service_gen.generate(parsed_class, context))

            # Execute ALL generation tasks in parallel across all classes
            if all_generation_tasks:
                generated_files = await asyncio.gather(*all_generation_tasks)
            else:
                generated_files = []

            # 3. Finalize Result
            end_time = asyncio.get_event_loop().time()
            
            result.files = generated_files
            result.total_files = len(generated_files)
            result.total_lines = sum(len(f.content.splitlines()) for f in generated_files)
            result.generation_time = end_time - start_time
            result.status = GenerationStatus.COMPLETED

            logger.info(f"Generation completed: {result.total_files} files generated")
            return result

        except Exception as e:
            logger.error(f"Code generation failed: {e}", exc_info=True)
            result.status = GenerationStatus.REJECTED
            return result
