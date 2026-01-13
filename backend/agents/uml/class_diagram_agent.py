"""
Class Diagram Agent

Generates PlantUML class diagrams from user stories using LLM (Groq/Gemini).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from .diagram_analyzer import DiagramAnalysisResult


@dataclass
class ClassDiagramResult:
    """Result of class diagram generation"""
    plantuml_code: str
    entities_count: int
    relationships_count: int
    api_used: str
    metadata: Dict[str, Any]


class ClassDiagramAgent:
    """
    Generates UML class diagrams from user stories using LLM.
    Uses LLMService for provider abstraction (Groq -> Gemini).
    """

    def __init__(self):
        from services.llm_service import LLMService
        self.llm = LLMService()

    async def generate(
        self,
        user_stories: List[Dict[str, Any]],
        analysis: DiagramAnalysisResult
    ) -> ClassDiagramResult:
        """
        Generate PlantUML class diagram from user stories and analysis.

        Args:
            user_stories: List of user story dicts
            analysis: Analysis result from DiagramAnalyzer

        Returns:
            ClassDiagramResult with PlantUML code
        """
        if not user_stories:
            return self._generate_empty_diagram()

        try:
            # Build prompt
            prompt = self._build_prompt(user_stories, analysis)
            
            # Generate using LLM Service
            # Increase token limit for large diagrams
            result = await self.llm.complete(prompt, max_tokens=2500)
            
            plantuml_code = result["text"].strip()
            plantuml_code = self._clean_plantuml_code(plantuml_code)
            
            return ClassDiagramResult(
                plantuml_code=plantuml_code,
                entities_count=len(analysis.entities),
                relationships_count=len(analysis.relationships),
                api_used=result.get("provider", "unknown"),
                metadata={"model": result.get("model", "unknown")}
            )

        except Exception as e:
            print(f"LLM generation failed: {e}. Falling back to basic diagram.")
            return self._generate_basic_diagram(analysis)  

    def _build_prompt(
        self,
        user_stories: List[Dict[str, Any]],
        analysis: DiagramAnalysisResult
    ) -> str:
        """Build the LLM prompt for class diagram generation"""

        # Format user stories
        stories_text = "\n\n".join([
            f"Story {i+1}: {story.get('story', '')}\n"
            f"Acceptance Criteria:\n" + 
            "\n".join([f"  - {ac}" for ac in story.get('acceptance_criteria', [])])
            for i, story in enumerate(user_stories)
        ])

        # Format identified entities
        entities_text = "\n".join([
            f"- {entity.name} (mentioned {entity.mentions} times)"
            for entity in analysis.entities.values()
        ])

        # Format actions
        actions_text = ", ".join(analysis.actions[:20])  # Limit to 20 actions

        prompt = f"""You are a UML expert. Generate a PlantUML class diagram from the following user stories.

USER STORIES:
{stories_text}

IDENTIFIED ENTITIES:
{entities_text}

IDENTIFIED ACTIONS:
{actions_text}

INSTRUCTIONS:
1. Create classes for each main entity (use the identified entities as a guide)
2. Add relevant attributes (data fields) - infer from the user stories
3. Add methods based on actions/verbs from acceptance criteria
4. Define relationships between classes:
   - Association (uses, has reference to) with "-->"
   - Composition (has, contains - strong ownership) with "*--"
   - Aggregation (contains - weak ownership) with "o--"
   - Inheritance (is-a) with "--|>"
5. Add multiplicities where appropriate (1, *, 0..1, 1..*)
6. Use meaningful class and method names in PascalCase
7. Use camelCase for attributes and methods
8. Keep the diagram clean and readable
9. Include visibility markers: + (public), - (private), # (protected)

OUTPUT FORMAT:
Return ONLY valid PlantUML code starting with @startuml and ending with @enduml.
Do NOT include explanations, markdown code blocks (```), or any text outside the PlantUML code.
Use proper PlantUML syntax for classes, attributes, methods, and relationships.

EXAMPLE OUTPUT:
@startuml
class User {{
  -id: UUID
  -username: String
  -email: String
  +login(): Boolean
  +logout(): void
  +updateProfile(): void
}}

class Project {{
  -id: UUID
  -name: String
  -description: String
  -createdAt: DateTime
  +create(): Project
  +update(): void
  +delete(): void
}}

User "1" -- "*" Project : owns >
@enduml

NOW GENERATE THE CLASS DIAGRAM:"""

        return prompt

    def _clean_plantuml_code(self, code: str) -> str:
        """Clean and validate PlantUML code from LLM response"""
        # Remove markdown code blocks if present
        code = code.replace("```plantuml", "").replace("```", "").strip()

        # Ensure it starts with @startuml
        if not code.startswith("@startuml"):
            code = "@startuml\n" + code

        # Ensure it ends with @enduml
        if not code.endswith("@enduml"):
            code = code + "\n@enduml"

        return code

    def _generate_basic_diagram(self, analysis: DiagramAnalysisResult) -> ClassDiagramResult:
        """Generate a basic diagram without LLM (fallback)"""
        lines = ["@startuml"]

        # Add classes
        for entity in analysis.entities.values():
            lines.append(f"\nclass {entity.name} {{")
            lines.append("  -id: UUID")
            
            # Add some basic methods
            if entity.methods:
                for method in list(entity.methods)[:3]:  # Limit to 3 methods
                    lines.append(f"  +{method}(): void")
            
            lines.append("}")

        # Add basic relationships
        for rel in analysis.relationships[:5]:  # Limit to 5 relationships
            if rel.relationship_type == "composition":
                lines.append(f"{rel.source} *-- {rel.target}")
            elif rel.relationship_type == "aggregation":
                lines.append(f"{rel.source} o-- {rel.target}")
            elif rel.relationship_type == "inheritance":
                lines.append(f"{rel.source} --|> {rel.target}")
            else:
                lines.append(f"{rel.source} -- {rel.target}")

        lines.append("@enduml")

        return ClassDiagramResult(
            plantuml_code="\n".join(lines),
            entities_count=len(analysis.entities),
            relationships_count=len(analysis.relationships),
            api_used="fallback",
            metadata={"message": "Generated without LLM"}
        )

    def _generate_empty_diagram(self) -> ClassDiagramResult:
        """Generate empty diagram when no user stories provided"""
        return ClassDiagramResult(
            plantuml_code="@startuml\nnote \"No user stories provided\" as N1\n@enduml",
            entities_count=0,
            relationships_count=0,
            api_used="none",
            metadata={"message": "No user stories provided"}
        )
