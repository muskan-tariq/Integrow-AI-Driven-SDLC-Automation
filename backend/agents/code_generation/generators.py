"""
Core Code Generators

Concrete implementations for generating Models, APIs, and Services.
Coordinates Template Engine and Code Enhancer.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from models.generated_code import (
    CodeGenerationContext,
    GeneratedFile,
    ParsedClass,
    FileType,
)
from agents.code_generation.template_engine import TemplateEngine
from agents.code_generation.code_enhancer import CodeEnhancerAgent

logger = logging.getLogger(__name__)


class CodeGenerator(ABC):
    """Abstract base class for code generators."""

    def __init__(self, template_engine: TemplateEngine, enhancer: CodeEnhancerAgent):
        self.template_engine = template_engine
        self.enhancer = enhancer

    @abstractmethod
    async def generate(self, parsed_class: ParsedClass, context: CodeGenerationContext) -> GeneratedFile:
        pass


class ModelGenerator(CodeGenerator):
    """Generates Pydantic data models."""

    async def generate(self, parsed_class: ParsedClass, context: CodeGenerationContext) -> GeneratedFile:
        # 1. Generate skeleton from template
        generated_file = self.template_engine.generate_model(parsed_class)
        
        # 2. Enhance with LLM (logic often less needed for models, but checking for validations)
        enhanced_content = await self.enhancer.enhance_code(
            code=generated_file.content,
            context=context,
            file_type=FileType.MODEL,
            class_name=parsed_class.name
        )
        
        generated_file.content = enhanced_content
        return generated_file


class APIGenerator(CodeGenerator):
    """Generates FastAPI routers."""

    async def generate(self, parsed_class: ParsedClass, context: CodeGenerationContext) -> GeneratedFile:
        # 1. Generate skeleton
        generated_file = self.template_engine.generate_api_router(parsed_class)
        
        # 2. Enhance with LLM
        enhanced_content = await self.enhancer.enhance_code(
            code=generated_file.content,
            context=context,
            file_type=FileType.API,
            class_name=parsed_class.name
        )
        
        generated_file.content = enhanced_content
        return generated_file


class ServiceGenerator(CodeGenerator):
    """Generates Service layer with business logic."""

    async def generate(self, parsed_class: ParsedClass, context: CodeGenerationContext) -> GeneratedFile:
        # 1. Generate skeleton
        generated_file = self.template_engine.generate_service(parsed_class)
        
        # 2. Enhance with LLM (Critical for service layer)
        enhanced_content = await self.enhancer.enhance_code(
            code=generated_file.content,
            context=context,
            file_type=FileType.SERVICE,
            class_name=parsed_class.name
        )
        
        generated_file.content = enhanced_content
        return generated_file
