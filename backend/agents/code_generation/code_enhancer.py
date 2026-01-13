"""
Code Enhancer Agent

Uses LLM to enhance generated code skeletons with business logic derived from user stories.
"""

from __future__ import annotations

import os
import logging
from typing import Optional, Dict, Any

from services.llm_service import LLMService

from models.generated_code import CodeGenerationContext, FileType

logger = logging.getLogger(__name__)


class CodeEnhancerAgent:
    """
    Enhances code skeletons with business logic using LLM.
    """

    def __init__(self):
        self.llm = LLMService()

    async def enhance_code(
        self,
        code: str,
        context: CodeGenerationContext,
        file_type: FileType,
        class_name: str
    ) -> str:
        """
        Enhance the generated code with business logic.

        Args:
            code: The skeleton code generated from templates
            context: The full generation context (stories, requirements)
            file_type: Type of file (model, api, service)
            class_name: Name of the class being generated

        Returns:
            Enhanced code with implemented TODOs
        """
        if not self.llm:
            return code

        # Only enhance specific file types that need business logic
        if file_type not in [FileType.SERVICE, FileType.API, FileType.MODEL]:
            return code

        prompt = self._build_enhancement_prompt(code, context, file_type, class_name)
        
        try:
            # Use centralized LLM service for better fallback and rate limiting
            response = await self.llm.complete(prompt, max_tokens=4000)
            enhanced_code = response["text"].strip()
            
            # Strip markdown code blocks if present
            if enhanced_code.startswith("```"):
                import re
                enhanced_code = re.sub(r'```(?:python)?\n?', '', enhanced_code)
                enhanced_code = enhanced_code.rstrip('`')
            
            return enhanced_code

        except Exception as e:
            logger.error(f"Error enhancing code for {class_name}: {e}")
            return code

    def _build_enhancement_prompt(
        self,
        code: str,
        context: CodeGenerationContext,
        file_type: FileType,
        class_name: str
    ) -> str:
        """Build the prompt for code enhancement."""
        
        # Gather relevant context
        related_stories = []
        if context.user_stories:
            for story in context.user_stories:
                # Simple keyword matching to find relevant stories
                if class_name.lower() in f"{story.title} {story.story}".lower():
                    related_stories.append(story)
        
        stories_text = ""
        if related_stories:
            stories_text = "RELEVANT USER STORIES:\n"
            for s in related_stories:
                stories_text += f"- {s.title}: {s.story}\n"
                if s.acceptance_criteria:
                    stories_text += "  Acceptance Criteria:\n"
                    for ac in s.acceptance_criteria:
                        stories_text += f"    * {ac}\n"

        if not stories_text and context.requirement_text:
            stories_text = f"REQUIREMENTS:\n{context.requirement_text[:1000]}..."

        prompt = f"""
You are completing a Python file. The file is currently a skeleton with TODOs.
Your task is to implement the missing logic based on the requirements.

CONTEXT:
File Type: {file_type.value}
Class Name: {class_name}

{stories_text}

CURRENT CODE SKELETON:
```python
{code}
```

INSTRUCTIONS:
1. Return the COMPLETE, valid Python file.
2. Implement the methods where you see 'TODO'.
3. Use the user stories/acceptance criteria to guide the logic.
4. Keep the existing structure, imports, and docstrings.
5. Add necessary error handling (try/except) and logging.
6. Do NOT add explanation text, just the code.

Generations:
"""
        return prompt
