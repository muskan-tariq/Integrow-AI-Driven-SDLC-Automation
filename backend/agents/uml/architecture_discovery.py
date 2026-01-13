"""
Architecture Discovery Agent

Scans codebase to extract architectural elements and relationships.
Primary: AST-based parsing for Python (and simple regex for others).
Secondary: LLM-based analysis for complex relationships and summarization.
"""

from __future__ import annotations

import ast
import os
import logging
from typing import List, Dict, Any, Optional

from models.uml_diagram import (
    DiagramAnalysisMetadata,
    EntityInfo,
    RelationshipInfo,
)
from services.llm_service import LLMService

logger = logging.getLogger(__name__)


class ArchitectureDiscoveryAgent:
    """
    Agent responsible for discovering architecture from existing code.
    """

    def __init__(self):
        self.llm = LLMService()

    async def discover(self, project_path: str, exclusions: List[str] = None) -> DiagramAnalysisMetadata:
        """
        Scan the project path and discover architecture.

        Args:
            project_path: Absolute path to the project root
            exclusions: List of directories/files to exclude

        Returns:
            DiagramAnalysisMetadata containing entities and relationships
        """
        if not os.path.exists(project_path):
            raise ValueError(f"Project path does not exist: {project_path}")

        exclusions = exclusions or [".git", "__pycache__", "venv", "node_modules", "dist", "build", ".idea", ".vscode"]
        
        entities: Dict[str, EntityInfo] = {}
        relationships: List[RelationshipInfo] = []
        
        # 1. AST Scanning (Python only for now)
        python_files = self._find_python_files(project_path, exclusions)
        
        for file_path in python_files:
            try:
                file_entities, file_relationships = self._parse_file_ast(file_path)
                entities.update(file_entities)
                relationships.extend(file_relationships)
            except Exception as e:
                logger.warning(f"Failed to parse {file_path}: {e}")

        # 2. Relationship Refinement (Connect imports/inheritance)
        # This is basic; a full implementation would use the LLM to understand logical coupling
        
        return DiagramAnalysisMetadata(
            entities=entities,
            relationships=relationships,
            entities_found=len(entities),
            relationships_found=len(relationships),
            actions=["discovered_from_code"],
            api_used="ast_parser"
        )

    def _find_python_files(self, root_path: str, exclusions: List[str]) -> List[str]:
        """Recursively find python files."""
        py_files = []
        for root, dirs, files in os.walk(root_path):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclusions]
            
            for file in files:
                if file.endswith(".py"):
                    py_files.append(os.path.join(root, file))
        return py_files

    def _parse_file_ast(self, file_path: str) -> tuple[Dict[str, EntityInfo], List[RelationshipInfo]]:
        """Parse a single Python file using AST."""
        entities = {}
        relationships = []
        
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=file_path)
            except SyntaxError:
                return {}, []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                attributes = [] # Attributes are harder to extract reliably without type hints parsing
                
                # Basic Attribute Extraction (fields in __init__)
                for subnode in node.body:
                    if isinstance(subnode, ast.FunctionDef) and subnode.name == "__init__":
                        for stmt in subnode.body:
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                                        attributes.append(target.attr)
                            elif isinstance(stmt, ast.AnnAssign):
                                if isinstance(stmt.target, ast.Attribute) and isinstance(stmt.target.value, ast.Name) and stmt.target.value.id == "self":
                                    attributes.append(stmt.target.attr)

                entities[class_name] = EntityInfo(
                    name=class_name,
                    methods=methods,
                    attributes=list(set(attributes)), # Unique attributes
                    mentions=1
                )

                # Inheritance
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        relationships.append(RelationshipInfo(
                            source=class_name,
                            target=base.id,
                            relationship_type="inheritance",
                            description=f"inherits from {base.id}"
                        ))

        return entities, relationships
