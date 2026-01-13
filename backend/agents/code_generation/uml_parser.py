"""
UML Parser Agent

Parses PlantUML diagrams into structured Python objects for code generation.
Uses regex-based parsing with LLM fallback for complex cases.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

from services.llm_service import LLMService
from models.generated_code import (
    ParsedClass,
    ParsedAttribute,
    ParsedMethod,
    ParsedParameter,
    ParsedRelationship,
    ParsedUMLResult,
    Visibility,
    RelationshipType,
)


class UMLParserAgent:
    """
    Parses PlantUML class diagrams into structured format.
    Primary: Regex-based parsing (fast, predictable)
    Fallback: LLM-based parsing for complex/malformed UML
    """

    def __init__(self):
        self.llm = LLMService()

    async def parse(self, plantuml_code: str) -> ParsedUMLResult:
        """
        Parse PlantUML code into structured format.

        Args:
            plantuml_code: PlantUML diagram code

        Returns:
            ParsedUMLResult with classes and relationships
        """
        if not plantuml_code or not plantuml_code.strip():
            return ParsedUMLResult(
                parse_success=False,
                parse_errors=["Empty PlantUML code provided"]
            )

        try:
            # Try regex parsing first
            classes = self._parse_classes(plantuml_code)
            relationships = self._parse_relationships(plantuml_code)

            # If regex parsing yields nothing, try LLM fallback
            if not classes and self.groq_enabled:
                return await self._parse_with_llm(plantuml_code)

            return ParsedUMLResult(
                classes=classes,
                relationships=relationships,
                raw_plantuml=plantuml_code,
                parse_success=True
            )

        except Exception as e:
            return ParsedUMLResult(
                raw_plantuml=plantuml_code,
                parse_success=False,
                parse_errors=[str(e)]
            )

    def _parse_classes(self, plantuml_code: str) -> List[ParsedClass]:
        """Parse class definitions from PlantUML."""
        classes = []

        # Pattern to match class definitions
        # Handles: class ClassName { ... } and abstract class ClassName { ... }
        class_pattern = r'(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?\s*\{([^}]*)\}'
        
        matches = re.finditer(class_pattern, plantuml_code, re.MULTILINE | re.DOTALL)

        for match in matches:
            class_name = match.group(1)
            parent_class = match.group(2)
            interfaces = match.group(3)
            body = match.group(4)

            is_abstract = 'abstract class' in match.group(0)

            # Parse interfaces
            interface_list = []
            if interfaces:
                interface_list = [i.strip() for i in interfaces.split(',')]

            # Parse attributes and methods from body
            attributes = self._parse_attributes(body)
            methods = self._parse_methods(body)

            classes.append(ParsedClass(
                name=class_name,
                attributes=attributes,
                methods=methods,
                is_abstract=is_abstract,
                parent_class=parent_class,
                interfaces=interface_list
            ))

        # Also handle simple class declarations without body
        simple_class_pattern = r'class\s+(\w+)\s*(?:\n|$)'
        simple_matches = re.finditer(simple_class_pattern, plantuml_code)
        existing_names = {c.name for c in classes}

        for match in simple_matches:
            class_name = match.group(1)
            if class_name not in existing_names:
                classes.append(ParsedClass(name=class_name))

        return classes

    def _parse_attributes(self, class_body: str) -> List[ParsedAttribute]:
        """Parse attributes from class body."""
        attributes = []

        # Pattern: visibility name : type
        # Handles: -id: UUID, +name: String, #count: int
        attr_pattern = r'([+\-#])(\w+)\s*:\s*(\w+(?:\[.*?\])?)'
        
        for match in re.finditer(attr_pattern, class_body):
            visibility_char = match.group(1)
            name = match.group(2)
            attr_type = match.group(3)

            visibility = self._parse_visibility(visibility_char)

            attributes.append(ParsedAttribute(
                name=name,
                type=attr_type,
                visibility=visibility
            ))

        return attributes

    def _parse_methods(self, class_body: str) -> List[ParsedMethod]:
        """Parse methods from class body."""
        methods = []

        # Pattern: visibility name(params): returnType
        # Handles: +login(): Boolean, -validate(input: String): void
        method_pattern = r'([+\-#])(\w+)\s*\(([^)]*)\)\s*(?::\s*(\w+))?'
        
        for match in re.finditer(method_pattern, class_body):
            visibility_char = match.group(1)
            name = match.group(2)
            params_str = match.group(3)
            return_type = match.group(4) or "None"

            visibility = self._parse_visibility(visibility_char)
            parameters = self._parse_parameters(params_str)

            methods.append(ParsedMethod(
                name=name,
                parameters=parameters,
                return_type=return_type,
                visibility=visibility
            ))

        return methods

    def _parse_parameters(self, params_str: str) -> List[ParsedParameter]:
        """Parse method parameters."""
        parameters = []

        if not params_str or not params_str.strip():
            return parameters

        # Split by comma and parse each parameter
        param_pattern = r'(\w+)\s*(?::\s*(\w+))?'
        
        for part in params_str.split(','):
            match = re.match(param_pattern, part.strip())
            if match:
                name = match.group(1)
                param_type = match.group(2) or "Any"
                parameters.append(ParsedParameter(name=name, type=param_type))

        return parameters

    def _parse_relationships(self, plantuml_code: str) -> List[ParsedRelationship]:
        """Parse relationships between classes."""
        relationships = []

        # Patterns for different relationship types
        relationship_patterns = [
            # Composition: A *-- B or A *--> B
            (r'(\w+)\s*\*--?\s*(?:"([^"]+)")?\s*(\w+)', RelationshipType.COMPOSITION),
            # Aggregation: A o-- B
            (r'(\w+)\s*o--?\s*(?:"([^"]+)")?\s*(\w+)', RelationshipType.AGGREGATION),
            # Inheritance: A --|> B or A <|-- B
            (r'(\w+)\s*--\|>\s*(\w+)', RelationshipType.INHERITANCE),
            (r'(\w+)\s*<\|--\s*(\w+)', RelationshipType.INHERITANCE),
            # Association: A --> B or A -- B
            (r'(\w+)\s*(?:"([^"]+)")?\s*-->\s*(?:"([^"]+)")?\s*(\w+)(?:\s*:\s*(.+))?', RelationshipType.ASSOCIATION),
            (r'(\w+)\s*(?:"([^"]+)")?\s*--\s*(?:"([^"]+)")?\s*(\w+)(?:\s*:\s*(.+))?', RelationshipType.ASSOCIATION),
        ]

        for pattern, rel_type in relationship_patterns:
            for match in re.finditer(pattern, plantuml_code):
                groups = match.groups()
                
                if rel_type == RelationshipType.INHERITANCE:
                    # Inheritance has simpler format
                    source, target = groups[0], groups[1]
                    relationships.append(ParsedRelationship(
                        source=source,
                        target=target,
                        relationship_type=rel_type
                    ))
                elif rel_type in [RelationshipType.COMPOSITION, RelationshipType.AGGREGATION]:
                    source = groups[0]
                    label = groups[1] if len(groups) > 1 else None
                    target = groups[2] if len(groups) > 2 else groups[1]
                    relationships.append(ParsedRelationship(
                        source=source,
                        target=target,
                        relationship_type=rel_type,
                        label=label
                    ))
                else:
                    # Association with possible multiplicities
                    source = groups[0]
                    source_mult = groups[1] if len(groups) > 1 and groups[1] else "1"
                    target_mult = groups[2] if len(groups) > 2 and groups[2] else "*"
                    target = groups[3] if len(groups) > 3 else groups[1]
                    label = groups[4] if len(groups) > 4 else None
                    
                    relationships.append(ParsedRelationship(
                        source=source,
                        target=target,
                        relationship_type=rel_type,
                        source_multiplicity=source_mult,
                        target_multiplicity=target_mult,
                        label=label
                    ))

        # Remove duplicates
        seen = set()
        unique_relationships = []
        for rel in relationships:
            key = (rel.source, rel.target, rel.relationship_type)
            if key not in seen:
                seen.add(key)
                unique_relationships.append(rel)

        return unique_relationships

    def _parse_visibility(self, char: str) -> Visibility:
        """Convert visibility character to enum."""
        mapping = {
            '+': Visibility.PUBLIC,
            '-': Visibility.PRIVATE,
            '#': Visibility.PROTECTED
        }
        return mapping.get(char, Visibility.PUBLIC)

    async def _parse_with_llm(self, plantuml_code: str) -> ParsedUMLResult:
        """Fallback: Parse using LLM for complex/malformed UML."""
        if not self.llm:
            return ParsedUMLResult(
                raw_plantuml=plantuml_code,
                parse_success=False,
                parse_errors=["LLM service not available"]
            )

        prompt = f"""Parse the following PlantUML class diagram and extract all classes, their attributes, methods, and relationships.

PlantUML Code:
```plantuml
{plantuml_code}
```

Return a JSON object with this structure:
{{
  "classes": [
    {{
      "name": "ClassName",
      "attributes": [{{"name": "attr", "type": "String", "visibility": "private"}}],
      "methods": [{{"name": "method", "parameters": [{{"name": "param", "type": "String"}}], "return_type": "void", "visibility": "public"}}],
      "is_abstract": false,
      "parent_class": null
    }}
  ],
  "relationships": [
    {{
      "source": "ClassA",
      "target": "ClassB",
      "relationship_type": "association",
      "label": "owns"
    }}
  ]
}}

Return ONLY valid JSON, no markdown or explanations.
"""

        try:
            response = await self.llm.complete(prompt, max_tokens=2000)
            
            import json
            content = response["text"].strip()
            
            # Try to extract JSON from response
            if content.startswith("```"):
                content = re.sub(r'```(?:json)?\n?', '', content)
                content = content.rstrip('`')
            
            data = json.loads(content)

            # Convert to ParsedUMLResult
            classes = []
            for cls_data in data.get("classes", []):
                attributes = [
                    ParsedAttribute(
                        name=a.get("name", ""),
                        type=a.get("type", "Any"),
                        visibility=Visibility(a.get("visibility", "private"))
                    )
                    for a in cls_data.get("attributes", [])
                ]
                methods = [
                    ParsedMethod(
                        name=m.get("name", ""),
                        parameters=[
                            ParsedParameter(name=p.get("name", ""), type=p.get("type", "Any"))
                            for p in m.get("parameters", [])
                        ],
                        return_type=m.get("return_type", "None"),
                        visibility=Visibility(m.get("visibility", "public"))
                    )
                    for m in cls_data.get("methods", [])
                ]
                classes.append(ParsedClass(
                    name=cls_data.get("name", ""),
                    attributes=attributes,
                    methods=methods,
                    is_abstract=cls_data.get("is_abstract", False),
                    parent_class=cls_data.get("parent_class")
                ))

            relationships = [
                ParsedRelationship(
                    source=r.get("source", ""),
                    target=r.get("target", ""),
                    relationship_type=RelationshipType(r.get("relationship_type", "association")),
                    label=r.get("label")
                )
                for r in data.get("relationships", [])
            ]

            return ParsedUMLResult(
                classes=classes,
                relationships=relationships,
                raw_plantuml=plantuml_code,
                parse_success=True
            )

        except Exception as e:
            return ParsedUMLResult(
                raw_plantuml=plantuml_code,
                parse_success=False,
                parse_errors=[f"LLM parsing failed: {str(e)}"]
            )
