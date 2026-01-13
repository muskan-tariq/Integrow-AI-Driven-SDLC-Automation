"""
UML Workflow Orchestrator

Coordinates the UML diagram generation process:
1. Fetch user stories
2. Analyze stories for entities/relationships (DiagramAnalyzer)
3. Generate PlantUML code (ClassDiagramAgent)
4. Render diagram (PlantUMLService)
5. Save to database
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from agents.uml import DiagramAnalyzer, ClassDiagramAgent, DiagramAnalysisResult, ClassDiagramResult
from agents.uml.architecture_discovery import ArchitectureDiscoveryAgent
from agents.uml.code_to_uml import CodeToUMLAgent
from services.plantuml_service import PlantUMLService
from models.uml_diagram import (
    DiagramAnalysisMetadata,
    EntityInfo as EntityInfoModel,
    RelationshipInfo as RelationshipInfoModel,
)

logger = logging.getLogger(__name__)


class UMLWorkflow:
    """Orchestrates UML diagram generation workflow"""

    def __init__(self):
        self.analyzer = DiagramAnalyzer()
        self.class_agent = ClassDiagramAgent()
        self.plantuml_service = PlantUMLService()
        self.discovery_agent = ArchitectureDiscoveryAgent()
        self.code_to_uml_agent = CodeToUMLAgent()

    async def generate_class_diagram(
        self,
        user_stories: List[Dict[str, Any]],
        requirement_id: UUID,
        project_id: UUID,
    ) -> Dict[str, Any]:
        """
        Generate a class diagram from user stories.

        Args:
            user_stories: List of user story dictionaries with 'story' and 'acceptance_criteria'
            requirement_id: UUID of the requirement
            project_id: UUID of the project

        Returns:
            Dictionary containing:
            - plantuml_code: PlantUML source code
            - rendered_svg: SVG rendering of the diagram
            - analysis: Analysis metadata
            - entities_count: Number of classes/entities found
            - relationships_count: Number of relationships found

        Raises:
            ValueError: If user stories are empty or invalid
            RuntimeError: If diagram generation or rendering fails
        """
        try:
            # Step 1: Validate input
            if not user_stories:
                raise ValueError("No user stories provided for diagram generation")

            logger.info(
                f"Starting class diagram generation for requirement {requirement_id} "
                f"with {len(user_stories)} user stories"
            )

            # Step 2: Analyze user stories
            logger.info("Analyzing user stories for entities and relationships...")
            analysis_result: DiagramAnalysisResult = await self.analyzer.analyze(user_stories)

            logger.info(
                f"Analysis complete: {len(analysis_result.entities)} entities, "
                f"{len(analysis_result.relationships)} relationships, "
                f"{len(analysis_result.actions)} actions"
            )

            # Step 3: Generate PlantUML code
            logger.info("Generating PlantUML code using AI...")
            diagram_result: ClassDiagramResult = await self.class_agent.generate(
                user_stories, analysis_result
            )

            logger.info(
                f"PlantUML code generated successfully using {diagram_result.api_used} API"
            )

            # Step 4: Validate PlantUML syntax
            is_valid, error = self.plantuml_service.validate_syntax(diagram_result.plantuml_code)
            if not is_valid:
                logger.warning(f"Generated PlantUML has syntax issues: {error}")
                # Continue anyway - PlantUML server might still render it

            # Step 5: Render diagram to SVG
            logger.info("Rendering diagram to SVG...")
            rendered_svg = await self.plantuml_service.render_svg(diagram_result.plantuml_code)
            
            logger.info(f"SVG rendering complete.")

            # Step 6: Parse actual relationships from PlantUML code
            actual_relationships = self._parse_plantuml_relationships(diagram_result.plantuml_code)
            logger.info(f"Parsed {len(actual_relationships)} relationships from PlantUML code")

            # Step 7: Prepare metadata with actual counts from PlantUML
            # This handles converting dataclasses to Pydantic models
            analysis_metadata = self._prepare_metadata(
                analysis_result, 
                diagram_result,
                actual_relationships=actual_relationships
            )

            # Step 8: Return result
            # Note: analysis_metadata is a Pydantic model, so model_dump() works
            result = {
                "plantuml_code": diagram_result.plantuml_code,
                "rendered_svg": rendered_svg.decode("utf-8") if isinstance(rendered_svg, bytes) else rendered_svg,
                "analysis": analysis_metadata.model_dump(),
                "entities_count": diagram_result.entities_count,
                "relationships_count": len(actual_relationships),
                "requirement_id": str(requirement_id),
                "project_id": str(project_id),
            }

            logger.info("Class diagram generation completed successfully")
            return result

        except Exception as e:
            logger.error(f"Class diagram generation failed: {e}")
            raise RuntimeError(f"Failed to generate class diagram: {e}")

    async def sync_from_code(
        self,
        project_path: str,
    ) -> Dict[str, Any]:
        """
        Generate UML diagram directly from code structure.

        Args:
            project_path: Path to the project codebase

        Returns:
            Dictionary with diagram data
        """
        try:
            logger.info(f"Syncing UML from code at {project_path}")
            
            # 1. Discover Architecture
            metadata = await self.discovery_agent.discover(project_path)
            
            if not metadata.entities:
                 raise ValueError("No classes or entities found in the codebase.")

            # 2. Convert to PlantUML
            plantuml_code = self.code_to_uml_agent.generate(metadata)
            
            # 3. Validate
            is_valid, error = self.plantuml_service.validate_syntax(plantuml_code)
            if not is_valid:
                 logger.warning(f"Generated PlantUML from code has syntax issues: {error}")

            # 4. Render
            rendered_svg = await self.plantuml_service.render_svg(plantuml_code)
            
            return {
                "plantuml_code": plantuml_code,
                "rendered_svg": rendered_svg.decode('utf-8') if isinstance(rendered_svg, bytes) else rendered_svg,
                "analysis": metadata.model_dump(),
                "entities_count": metadata.entities_found,
                "relationships_count": metadata.relationships_found,
            }
            
        except Exception as e:
            logger.error(f"Sync from code failed: {e}")
            raise RuntimeError(f"Failed to sync from code: {e}")

    def _parse_plantuml_relationships(self, plantuml_code: str) -> List[RelationshipInfoModel]:
        """
        Parse relationships from PlantUML code.
        
        Detects relationship patterns like:
        - A "1" -- "1" B : label
        - A --> B
        - A <|-- B (inheritance)
        - A *-- B (composition)
        - A o-- B (aggregation)
        
        Args:
            plantuml_code: PlantUML source code
            
        Returns:
            List of RelationshipInfoModel objects
        """
        import re
        
        relationships = []
        
        # Relationship patterns in PlantUML
        patterns = [
            # Association with multiplicities: A "1" -- "*" B : label
            r'(\w+)\s+"([^"]+)"\s+(--|\<--|\-\-\>|\<\|\-\-|\*\-\-|o\-\-)\s+"([^"]+)"\s+(\w+)\s*:\s*(.+)',
            # Association without multiplicities: A -- B : label
            r'(\w+)\s+(--|\<--|\-\-\>|\<\|\-\-|\*\-\-|o\-\-)\s+(\w+)\s*:\s*(.+)',
            # Association without label: A -- B
            r'(\w+)\s+(--|\<--|\-\-\>|\<\|\-\-|\*\-\-|o\-\-)\s+(\w+)\s*$',
        ]
        
        # Relationship type mapping
        rel_type_map = {
            '--': 'association',
            '-->': 'association',
            '<--': 'association',
            '<|--': 'inheritance',
            '*--': 'composition',
            'o--': 'aggregation',
        }
        
        for line in plantuml_code.split('\n'):
            line = line.strip()
            
            # Try pattern with multiplicities
            match = re.match(patterns[0], line)
            if match:
                source, mult1, rel_symbol, mult2, target, label = match.groups()
                relationships.append(RelationshipInfoModel(
                    source=source,
                    target=target,
                    relationship_type=rel_type_map.get(rel_symbol, 'association'),
                    description=label.strip(),
                    multiplicity=f"{mult1}..{mult2}"
                ))
                continue
            
            # Try pattern without multiplicities but with label
            match = re.match(patterns[1], line)
            if match:
                source, rel_symbol, target, label = match.groups()
                relationships.append(RelationshipInfoModel(
                    source=source,
                    target=target,
                    relationship_type=rel_type_map.get(rel_symbol, 'association'),
                    description=label.strip(),
                    multiplicity=None
                ))
                continue
            
            # Try pattern without label
            match = re.match(patterns[2], line)
            if match:
                source, rel_symbol, target = match.groups()
                relationships.append(RelationshipInfoModel(
                    source=source,
                    target=target,
                    relationship_type=rel_type_map.get(rel_symbol, 'association'),
                    description=None,
                    multiplicity=None
                ))
        
        return relationships

    def _prepare_metadata(
        self,
        analysis_result: DiagramAnalysisResult,
        diagram_result: ClassDiagramResult,
        actual_relationships: List[RelationshipInfoModel] = None,
    ) -> DiagramAnalysisMetadata:
        """
        Prepare analysis metadata for database storage.

        Args:
            analysis_result: Result from DiagramAnalyzer
            diagram_result: Result from ClassDiagramAgent
            actual_relationships: Relationships parsed from final PlantUML code (optional)

        Returns:
            DiagramAnalysisMetadata object
        """
        # Convert EntityInfo objects to Pydantic models
        entities_dict = {}
        for name, entity in analysis_result.entities.items():
            entities_dict[name] = EntityInfoModel(
                name=entity.name,
                mentions=entity.mentions,
                methods=list(entity.methods),
                attributes=list(entity.attributes),
            )

        # Use actual relationships from PlantUML if provided, otherwise use analysis results
        if actual_relationships:
            relationships_list = actual_relationships
            relationships_count = len(actual_relationships)
        else:
            # Convert RelationshipInfo objects to Pydantic models
            relationships_list = []
            for rel in analysis_result.relationships:
                relationships_list.append(
                    RelationshipInfoModel(
                        source=rel.source,
                        target=rel.target,
                        relationship_type=rel.relationship_type,
                        description=rel.description,
                        multiplicity=getattr(rel, "multiplicity", None),
                    )
                )
            relationships_count = len(analysis_result.relationships)

        return DiagramAnalysisMetadata(
            entities=entities_dict,
            relationships=relationships_list,
            actions=analysis_result.actions,
            total_stories=analysis_result.metadata.get("total_stories", 0),
            entities_found=len(analysis_result.entities),
            relationships_found=relationships_count,
            api_used=diagram_result.api_used,
        )

    async def regenerate_diagram(
        self,
        plantuml_code: str,
    ) -> bytes:
        """
        Regenerate diagram rendering from PlantUML code.

        Args:
            plantuml_code: PlantUML source code

        Returns:
            SVG rendering as bytes

        Raises:
            ValueError: If PlantUML syntax is invalid
            RuntimeError: If rendering fails
        """
        try:
            logger.info("Regenerating diagram from PlantUML code...")

            # Validate syntax
            is_valid, error = self.plantuml_service.validate_syntax(plantuml_code)
            if not is_valid:
                raise ValueError(f"Invalid PlantUML syntax: {error}")

            # Render to SVG
            rendered_svg = await self.plantuml_service.render_svg(plantuml_code)

            logger.info("Diagram regenerated successfully")
            return rendered_svg

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error regenerating diagram: {e}", exc_info=True)
            raise RuntimeError(f"Failed to regenerate diagram: {str(e)}")

    async def export_diagram(
        self,
        plantuml_code: str,
        format: str = "svg",
    ) -> bytes:
        """
        Export diagram in specified format.

        Args:
            plantuml_code: PlantUML source code
            format: Output format ('svg' or 'png')

        Returns:
            Diagram rendering as bytes

        Raises:
            ValueError: If format is unsupported or syntax is invalid
            RuntimeError: If export fails
        """
        try:
            logger.info(f"Exporting diagram as {format.upper()}...")

            # Validate syntax
            is_valid, error = self.plantuml_service.validate_syntax(plantuml_code)
            if not is_valid:
                raise ValueError(f"Invalid PlantUML syntax: {error}")

            # Render in requested format
            if format.lower() == "svg":
                result = await self.plantuml_service.render_svg(plantuml_code)
            elif format.lower() == "png":
                result = await self.plantuml_service.render_png(plantuml_code)
            else:
                raise ValueError(f"Unsupported format: {format}. Use 'svg' or 'png'.")

            logger.info(f"Diagram exported as {format.upper()} successfully")
            return result

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error exporting diagram: {e}", exc_info=True)
            raise RuntimeError(f"Failed to export diagram: {str(e)}")
