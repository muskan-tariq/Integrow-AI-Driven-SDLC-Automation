from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class UserStory:
    title: str
    story: str
    acceptance_criteria: List[str]
    priority: str  # high, medium, low
    story_points: Optional[int]
    tags: List[str]


@dataclass
class UserStoryResult:
    user_stories: List[UserStory]
    total_stories: int


class UserStoryAgent:
    """
    Generates user stories from requirements using Groq API.
    Takes the requirement text and analysis findings to create comprehensive,
    structured user stories with acceptance criteria.
    """

    def __init__(self) -> None:
        # Load environment variables from .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # dotenv not available, rely on system env vars
        
        self.groq_enabled = os.getenv("GROQ_API_KEY") is not None
        self._client = None
        if self.groq_enabled:
            try:
                from groq import Groq  # type: ignore

                self._client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            except Exception:
                self.groq_enabled = False

    async def generate(
        self,
        requirement_text: str,
        parsed_entities: Dict[str, Any],
        analysis_findings: Dict[str, Any],
    ) -> UserStoryResult:
        """
        Generate user stories from requirement text and analysis findings.

        Args:
            requirement_text: The original requirement text
            parsed_entities: Parsed entities (actors, actions, entities)
            analysis_findings: Analysis results (ambiguity, completeness, ethics)

        Returns:
            UserStoryResult with generated user stories
        """
        if not requirement_text or not requirement_text.strip():
            return UserStoryResult(user_stories=[], total_stories=0)

        if not self.groq_enabled or self._client is None:
            # Fallback: generate basic user story from requirement
            return self._generate_fallback_story(requirement_text, parsed_entities)

        try:
            prompt = self._build_prompt(requirement_text, parsed_entities, analysis_findings)
            response = self._client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000,
            )
            content = response.choices[0].message.content
            stories = self._parse_llm_response(content)
            return UserStoryResult(user_stories=stories, total_stories=len(stories))
        except Exception as e:
            # Fallback on API errors
            return self._generate_fallback_story(requirement_text, parsed_entities)

    def _build_prompt(
        self,
        requirement_text: str,
        parsed_entities: Dict[str, Any],
        analysis_findings: Dict[str, Any],
    ) -> str:
        """Build detailed prompt for Groq API with all context."""
        
        # Extract key information
        actors = parsed_entities.get("actors", [])
        actions = parsed_entities.get("actions", [])
        entities = parsed_entities.get("entities", [])
        
        ambiguity_issues = analysis_findings.get("ambiguity", {}).get("issues", [])
        completeness_gaps = analysis_findings.get("completeness", {}).get("missing", [])
        ethics_concerns = analysis_findings.get("ethics", {}).get("issues", [])

        prompt = f"""You are a professional business analyst and agile coach. Generate comprehensive user stories from the following requirement.

**REQUIREMENT:**
{requirement_text}

**CONTEXT FROM ANALYSIS:**

Identified Actors: {', '.join(actors) if actors else 'None identified'}
Identified Actions: {', '.join(actions) if actions else 'None identified'}
Identified Entities: {', '.join(entities) if entities else 'None identified'}

Ambiguity Issues Found: {len(ambiguity_issues)}
"""
        if ambiguity_issues:
            prompt += "\nAmbiguous terms to clarify:\n"
            for issue in ambiguity_issues[:3]:  # Limit to top 3
                term = issue.get("term", "")
                explanation = issue.get("explanation", "")
                prompt += f"  - {term}: {explanation}\n"

        if completeness_gaps:
            prompt += f"\nCompleteness Gaps Found: {len(completeness_gaps)}\n"
            prompt += "Missing aspects to address:\n"
            for gap in completeness_gaps[:3]:  # Limit to top 3
                category = gap.get("category", "")
                description = gap.get("description", "")
                prompt += f"  - {category}: {description}\n"

        if ethics_concerns:
            prompt += f"\nEthics Concerns Found: {len(ethics_concerns)}\n"
            prompt += "Ensure stories address these concerns appropriately.\n"

        prompt += """
**INSTRUCTIONS:**

Generate 2-5 user stories that:
1. Use the standard format: "As a [user/role], I want [goal], so that [benefit]"
2. Include specific, testable acceptance criteria in Given-When-Then format
3. Address any ambiguities with concrete, measurable requirements
4. Fill in completeness gaps with necessary error handling, security, and performance criteria
5. Ensure stories are inclusive and ethical
6. Assign appropriate priority (high/medium/low) based on business value
7. Estimate story points (1-13, Fibonacci scale) based on complexity

**OUTPUT FORMAT:**

Respond ONLY with a JSON array of objects. Each object must have:
- title: Short descriptive title
- story: User story in standard format
- acceptance_criteria: Array of strings in Given-When-Then format
- priority: "high" | "medium" | "low"
- story_points: Integer (1-13)
- tags: Array of relevant tags (e.g., ["authentication", "security"])

**EXAMPLE:**
```json
[
  {
    "title": "User Login Authentication",
    "story": "As a user, I want to login with my email and password, so that I can access my personalized account securely.",
    "acceptance_criteria": [
      "Given I am on the login page, When I enter valid credentials, Then I should be logged in within 2 seconds",
      "Given I enter invalid credentials, When I attempt to login, Then I should see a clear error message",
      "Given I have entered wrong password 3 times, When I try again, Then my account should be temporarily locked"
    ],
    "priority": "high",
    "story_points": 5,
    "tags": ["authentication", "security"]
  }
]
```

Generate the user stories now:"""

        return prompt

    def _parse_llm_response(self, content: str) -> List[UserStory]:
        """Parse LLM response and extract user stories."""
        try:
            # Try to parse as direct JSON
            data = json.loads(content)
            if isinstance(data, list):
                return self._convert_to_user_stories(data)
        except Exception:
            pass

        # Try to extract JSON array from markdown code blocks
        json_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                if isinstance(data, list):
                    return self._convert_to_user_stories(data)
            except Exception:
                pass

        # Try to find any JSON array in the content
        array_match = re.search(r"\[[\s\S]*\]", content)
        if array_match:
            try:
                data = json.loads(array_match.group(0))
                if isinstance(data, list):
                    return self._convert_to_user_stories(data)
            except Exception:
                pass

        # No valid JSON found
        return []

    def _convert_to_user_stories(self, data: List[Dict[str, Any]]) -> List[UserStory]:
        """Convert parsed JSON data to UserStory objects."""
        stories = []
        for item in data:
            try:
                story = UserStory(
                    title=str(item.get("title", "Untitled Story")),
                    story=str(item.get("story", "")),
                    acceptance_criteria=item.get("acceptance_criteria", []),
                    priority=str(item.get("priority", "medium")).lower(),
                    story_points=item.get("story_points"),
                    tags=item.get("tags", []),
                )
                # Validate priority
                if story.priority not in ["high", "medium", "low"]:
                    story.priority = "medium"
                # Validate story points
                if story.story_points is not None:
                    story.story_points = max(1, min(13, int(story.story_points)))
                stories.append(story)
            except Exception:
                # Skip invalid stories
                continue
        return stories

    def _generate_fallback_story(
        self, requirement_text: str, parsed_entities: Dict[str, Any]
    ) -> UserStoryResult:
        """Generate a basic user story when Groq API is unavailable."""
        actors = parsed_entities.get("actors", [])
        actions = parsed_entities.get("actions", [])

        # Determine primary actor
        actor = actors[0] if actors else "user"
        
        # Create basic story
        story = UserStory(
            title="Requirement Implementation",
            story=f"As a {actor}, I want to {requirement_text[:100]}..., so that I can fulfill the requirement.",
            acceptance_criteria=[
                "Given the system is ready, When the user performs the action, Then the requirement should be fulfilled",
                "Given invalid input, When the user tries to proceed, Then appropriate error messages should be shown",
            ],
            priority="medium",
            story_points=5,
            tags=["requirement"],
        )

        return UserStoryResult(user_stories=[story], total_stories=1)
