"""
Story Refinement Agent - Refines user stories based on user feedback using Groq API
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class UserStory:
    """User story structure"""
    title: str
    story: str
    acceptance_criteria: List[str]
    priority: str
    story_points: Optional[int]
    tags: List[str]


@dataclass
class RefinementResult:
    """Result of story refinement"""
    refined_stories: List[UserStory]
    changes_made: List[str]
    explanation: str


class StoryRefinementAgent:
    """
    Refines user stories based on user feedback using Groq API.
    Maintains conversation context for iterative refinement.
    """

    def __init__(self) -> None:
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        self.groq_enabled = os.getenv("GROQ_API_KEY") is not None
        self._client = None
        if self.groq_enabled:
            try:
                from groq import Groq
                self._client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            except Exception:
                self.groq_enabled = False

    async def refine_stories(
        self,
        current_stories: List[Dict[str, Any]],
        refinement_request: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> RefinementResult:
        """
        Refine a list of user stories based on user's refinement request.

        Args:
            current_stories: List of current story states
            refinement_request: What the user wants to change
            conversation_history: Previous messages in this refinement session

        Returns:
            RefinementResult with refined stories list, changes made, and explanation
        """
        if not self.groq_enabled or self._client is None:
            return self._generate_fallback_refinement(current_stories, refinement_request)

        try:
            prompt = self._build_refinement_prompt(
                current_stories, refinement_request, conversation_history or []
            )

            # Increase tokens for batch processing
            response = self._client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2500,
            )

            content = response.choices[0].message.content
            return self._parse_refinement_response(content, current_stories)

        except Exception as e:
            # Fallback on API errors
            return self._generate_fallback_refinement(current_stories, refinement_request)

    def _build_refinement_prompt(
        self,
        current_stories: List[Dict[str, Any]],
        refinement_request: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Build the refinement prompt for Groq API."""
        
        # Format current stories
        stories_text = ""
        for idx, story in enumerate(current_stories):
            # Safe access to fields
            title = story.get('title', 'Untitled')
            story_text = story.get('story', '')
            priority = story.get('priority', 'medium')
            points = story.get('story_points', 'Not estimated')
            tags = ', '.join(story.get('tags', []) or [])
            criteria = story.get('acceptance_criteria', []) or []
            
            stories_text += f"""
---
**Story {idx + 1}:**
Title: {title}
User Story: {story_text}
Priority: {priority}
Story Points: {points}
Tags: {tags}
Acceptance Criteria:
{chr(10).join(f"- {c}" for c in criteria)}
"""

        # Format conversation history if any
        history_text = ""
        if conversation_history:
            history_text = "\n**Previous Conversation:**\n"
            for msg in conversation_history[-3:]:  # Last 3 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_text += f"{role.capitalize()}: {content}\n"

        prompt = f"""You are an expert Agile coach and business analyst helping refine user stories.

**Stories to Refine:**
{stories_text}

{history_text}

**User's Refinement Request:**
{refinement_request}

**Instructions:**
1. Apply the user's request to ALL provided stories appropriately.
2. Maintain proper standard user story format ("As a... I want... So that...").
3. Ensure acceptance criteria are testable (Given-When-Then).
4. Be consistent across all stories.
5. Identify manual/custom stories and treat them with equal care.

**Output Format:**
Respond with a JSON object containing:
- "refined_stories": Array of updated story objects. Order MUST match input. Each object must have: {{ title, story, acceptance_criteria (array), priority, story_points, tags (array) }}
- "changes_made": Array of strings describing specific changes applied.
- "explanation": Brief text summary of what you did.

**Example JSON Response:**
```json
{{
  "refined_stories": [
    {{
      "title": "Login",
      "story": "As a user...",
      "acceptance_criteria": ["Given...", "When..."],
      "priority": "high",
      "story_points": 3,
      "tags": ["auth"]
    }}
  ],
  "changes_made": ["Updated priority to High", "Added security criteria"],
  "explanation": "I updated the priority and added criteria as requested."
}}
```

Perform the refinement now:"""

        return prompt

    def _parse_refinement_response(
        self, content: str, original_stories: List[Dict[str, Any]]
    ) -> RefinementResult:
        """Parse the LLM response and extract refinement result."""
        try:
            # Try to parse as direct JSON
            data = json.loads(content)
            return self._convert_to_refinement_result(data, len(original_stories))
        except Exception:
            pass

        # Try to extract JSON from code blocks
        import re
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return self._convert_to_refinement_result(data, len(original_stories))
            except Exception:
                pass

        # Try to find any JSON object
        obj_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content, re.DOTALL)
        if obj_match:
            try:
                data = json.loads(obj_match.group(0))
                return self._convert_to_refinement_result(data, len(original_stories))
            except Exception:
                pass

        # Fallback: no changes
        return self._generate_fallback_refinement(original_stories, "Failed to parse AI response")

    def _convert_to_refinement_result(self, data: Dict[str, Any], expected_count: int) -> RefinementResult:
        """Convert parsed JSON to RefinementResult object."""
        refined_list_data = data.get("refined_stories", [])
        
        refined_stories = []
        for item in refined_list_data:
            story = UserStory(
                title=str(item.get("title", "Untitled")),
                story=str(item.get("story", "")),
                acceptance_criteria=item.get("acceptance_criteria", []),
                priority=str(item.get("priority", "medium")).lower(),
                story_points=item.get("story_points"),
                tags=item.get("tags", [])
            )
            # Basic validation
            if story.priority not in ["high", "medium", "low"]:
                story.priority = "medium"
            if story.story_points is not None:
                story.story_points = max(1, min(13, int(story.story_points)))
                
            refined_stories.append(story)
            
        # If count mismatch, return strict valid ones or fallback (for now just return what we got)
        # Ideally we should map them back to originals, but for batch this assumes order preservation.

        return RefinementResult(
            refined_stories=refined_stories,
            changes_made=data.get("changes_made", []),
            explanation=data.get("explanation", "Stories refined successfully.")
        )

    def _generate_fallback_refinement(
        self, current_stories: List[Dict[str, Any]], refinement_request: str
    ) -> RefinementResult:
        """Generate a simple fallback refinement when API is unavailable."""
        refined = []
        for s in current_stories:
            refined.append(UserStory(
                title=s.get("title", ""),
                story=s.get("story", ""),
                acceptance_criteria=s.get("acceptance_criteria", []),
                priority=s.get("priority", "medium"),
                story_points=s.get("story_points"),
                tags=s.get("tags", [])
            ))
            
        return RefinementResult(
            refined_stories=refined,
            changes_made=[],
            explanation=f"AI refinement unavailable. Please manually edit: {refinement_request}"
        )
