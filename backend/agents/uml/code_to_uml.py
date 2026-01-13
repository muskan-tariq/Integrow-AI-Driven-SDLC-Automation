"""
Code to UML Agent

Converts structural architecture data (extracted from code) into valid PlantUML diagrams.
Ensures consistent styling, layout logic, and relationship handling.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional

from models.uml_diagram import DiagramAnalysisMetadata, EntityInfo, RelationshipInfo

logger = logging.getLogger(__name__)


class CodeToUMLAgent:
    """
    Agent responsible for generating PlantUML code from discovered architecture.
    """

    def generate(self, metadata: DiagramAnalysisMetadata) -> str:
        """
        Generate PlantUML code from architecture metadata.

        Args:
            metadata: The discovered architecture metadata

        Returns:
            String containing the full PlantUML diagram code
        """
        lines = [
            "@startuml",
            "!theme plain",
            "hide empty members",
            "skinparam classAttributeIconSize 0",
            ""
        ]

        # 1. Add Entities (Classes)
        for entity_id, entity in metadata.entities.items():
            lines.append(f"class {entity.name} {{")
            
            # Attributes
            for attr in entity.attributes:
                lines.append(f"  + {attr}")
            
            if entity.attributes and entity.methods:
                lines.append("  --")

            # Methods
            for method in entity.methods:
                lines.append(f"  + {method}()")
            
            lines.append("}")
            lines.append("")

        # 2. Add Relationships
        for rel in metadata.relationships:
            arrow = "--"
            if rel.relationship_type == "inheritance":
                arrow = "--|>"
            elif rel.relationship_type == "composition":
                arrow = "*--"
            elif rel.relationship_type == "aggregation":
                arrow = "o--"
            elif rel.relationship_type == "association":
                arrow = "-->"
            elif rel.relationship_type == "dependency":
                arrow = "..>"
            
            # Basic validation to ensure entities exist or strictly defined
            # PlantUML is forgiving, so we can just output the relationship
            lines.append(f"{rel.target} {arrow} {rel.source} : {rel.description or ''}")

        lines.append("@enduml")
        
        return "\n".join(lines)
