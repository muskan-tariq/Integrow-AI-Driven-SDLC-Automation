"""
Context Builder

Assembles code generation context from UML diagrams and user stories.
Fetches data from Supabase and maps acceptance criteria to method implementations.
"""

from __future__ import annotations

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from models.generated_code import (
    CodeGenerationContext,
    ParsedUMLResult,
    UserStoryContext,
    TechStackConfig,
)

logger = logging.getLogger(__name__)


class ContextBuilder:
    """
    Builds the complete context for code generation.
    Combines UML diagrams, user stories, and project configuration.
    """

    def __init__(self, supabase_service=None):
        """
        Initialize the context builder.

        Args:
            supabase_service: Optional SupabaseService instance
        """
        self._supabase = supabase_service
        if self._supabase is None:
            try:
                from services.supabase_service import supabase_service
                self._supabase = supabase_service
            except ImportError:
                logger.warning("SupabaseService not available")

    async def build(
        self,
        project_id: str,
        requirement_id: str,
        uml_diagram_id: Optional[str] = None,
        tech_stack: Optional[TechStackConfig] = None,
        generation_scope: Optional[List[str]] = None
    ) -> CodeGenerationContext:
        """
        Build the complete code generation context.

        Args:
            project_id: Project UUID
            requirement_id: Requirement UUID
            uml_diagram_id: Optional specific UML diagram ID
            tech_stack: Technology stack configuration
            generation_scope: What to generate

        Returns:
            CodeGenerationContext with all assembled data
        """
        context = CodeGenerationContext(
            project_id=project_id,
            requirement_id=requirement_id,
            tech_stack=tech_stack or TechStackConfig(),
            generation_scope=generation_scope or ["models", "api", "services"]
        )

        try:
            # Fetch requirement text
            context.requirement_text = await self._fetch_requirement(requirement_id)

            # Fetch and parse UML diagram
            context.parsed_uml = await self._fetch_uml(project_id, uml_diagram_id)

            # Fetch user stories
            context.user_stories = await self._fetch_user_stories(requirement_id)

        except Exception as e:
            logger.error(f"Error building context: {e}")
            raise

        return context

    async def _fetch_requirement(self, requirement_id: str) -> str:
        """Fetch requirement text from database."""
        if not self._supabase:
            return ""

        try:
            response = self._supabase.client.table("requirements").select(
                "raw_text"
            ).eq("id", requirement_id).execute()

            if response.data:
                return response.data[0].get("raw_text", "")
        except Exception as e:
            logger.warning(f"Could not fetch requirement: {e}")

        return ""

    async def _fetch_uml(
        self,
        project_id: str,
        uml_diagram_id: Optional[str] = None
    ) -> Optional[ParsedUMLResult]:
        """Fetch UML diagram and parse it."""
        if not self._supabase:
            return None

        try:
            query = self._supabase.client.table("uml_diagrams").select(
                "id, diagram_type, plantuml_code"
            ).eq("project_id", project_id)

            if uml_diagram_id:
                query = query.eq("id", uml_diagram_id)
            else:
                # Get the most recent class diagram
                query = query.eq("diagram_type", "class").order(
                    "created_at", desc=True
                ).limit(1)

            response = query.execute()

            if response.data:
                plantuml_code = response.data[0].get("plantuml_code", "")
                
                # Parse the UML using UMLParserAgent
                from agents.code_generation.uml_parser import UMLParserAgent
                parser = UMLParserAgent()
                return await parser.parse(plantuml_code)

        except Exception as e:
            logger.warning(f"Could not fetch/parse UML: {e}")

        return None

    async def _fetch_user_stories(
        self,
        requirement_id: str
    ) -> List[UserStoryContext]:
        """Fetch user stories for the requirement."""
        if not self._supabase:
            return []

        try:
            response = self._supabase.client.table("user_stories").select(
                "id, title, story, acceptance_criteria, priority, tags"
            ).eq("requirement_id", requirement_id).execute()

            stories = []
            for row in response.data or []:
                # Parse acceptance criteria if it's a string
                criteria = row.get("acceptance_criteria", [])
                if isinstance(criteria, str):
                    criteria = [c.strip() for c in criteria.split("\n") if c.strip()]

                stories.append(UserStoryContext(
                    title=row.get("title", ""),
                    story=row.get("story", ""),
                    acceptance_criteria=criteria,
                    priority=row.get("priority", "medium"),
                    tags=row.get("tags", [])
                ))

            return stories

        except Exception as e:
            logger.warning(f"Could not fetch user stories: {e}")

        return []

    def map_criteria_to_methods(
        self,
        context: CodeGenerationContext
    ) -> Dict[str, List[str]]:
        """
        Map acceptance criteria to class methods.
        
        This helps the LLM understand what business logic to implement.

        Args:
            context: The code generation context

        Returns:
            Dict mapping class names to relevant acceptance criteria
        """
        mapping = {}

        if not context.parsed_uml or not context.user_stories:
            return mapping

        # Get all class names
        class_names = [cls.name.lower() for cls in context.parsed_uml.classes]

        # For each user story, find relevant classes based on keywords
        for story in context.user_stories:
            story_text = f"{story.title} {story.story}".lower()
            
            for cls in context.parsed_uml.classes:
                cls_name = cls.name.lower()
                
                # Check if class is mentioned in the story
                if cls_name in story_text:
                    if cls.name not in mapping:
                        mapping[cls.name] = []
                    
                    # Add all acceptance criteria from this story
                    mapping[cls.name].extend(story.acceptance_criteria)

        return mapping

    def build_enhanced_prompt_context(
        self,
        context: CodeGenerationContext
    ) -> str:
        """
        Build an enhanced prompt context for LLM code enhancement.

        Args:
            context: The code generation context

        Returns:
            Formatted string for LLM prompt
        """
        sections = []

        # Requirement
        if context.requirement_text:
            sections.append(f"## Original Requirement\n{context.requirement_text}")

        # User Stories
        if context.user_stories:
            stories_text = "\n".join([
                f"### {s.title}\n{s.story}\n**Acceptance Criteria:**\n" +
                "\n".join([f"- {c}" for c in s.acceptance_criteria])
                for s in context.user_stories
            ])
            sections.append(f"## User Stories\n{stories_text}")

        # Classes from UML
        if context.parsed_uml and context.parsed_uml.classes:
            classes_text = "\n".join([
                f"- **{cls.name}**: {len(cls.attributes)} attributes, {len(cls.methods)} methods"
                for cls in context.parsed_uml.classes
            ])
            sections.append(f"## Classes from UML\n{classes_text}")

        # Criteria mapping
        criteria_mapping = self.map_criteria_to_methods(context)
        if criteria_mapping:
            mapping_text = "\n".join([
                f"### {cls_name}\n" + "\n".join([f"- {c}" for c in criteria])
                for cls_name, criteria in criteria_mapping.items()
            ])
            sections.append(f"## Class-to-Criteria Mapping\n{mapping_text}")

        return "\n\n".join(sections)
