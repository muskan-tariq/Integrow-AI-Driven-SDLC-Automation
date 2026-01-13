"""
Template Engine

Jinja2-based template engine for code generation.
Renders parsed UML classes into code files using templates.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any, Optional, List

from jinja2 import Environment, FileSystemLoader, select_autoescape

from models.generated_code import (
    ParsedClass,
    GeneratedFile,
    FileType,
)


# Type mapping from UML types to Python types
UML_TO_PYTHON_TYPES = {
    # Primitives
    "string": "str",
    "String": "str",
    "int": "int",
    "Int": "int",
    "Integer": "int",
    "integer": "int",
    "float": "float",
    "Float": "float",
    "double": "float",
    "Double": "float",
    "boolean": "bool",
    "Boolean": "bool",
    "bool": "bool",
    "void": "None",
    "Void": "None",
    "none": "None",
    
    # Common types
    "UUID": "UUID",
    "uuid": "UUID",
    "Date": "datetime",
    "DateTime": "datetime",
    "date": "datetime",
    "datetime": "datetime",
    "Timestamp": "datetime",
    
    # Collections
    "List": "List",
    "Array": "List",
    "Set": "set",
    "Dict": "Dict",
    "Map": "Dict",
    "Optional": "Optional",
    
    # Any/Object
    "Object": "Any",
    "object": "Any",
    "any": "Any",
    "Any": "Any",
}


def python_type_filter(uml_type: str) -> str:
    """Convert UML type to Python type."""
    if not uml_type:
        return "Any"
    
    # Handle generic types like List[String]
    if "[" in uml_type:
        base_type = uml_type.split("[")[0]
        inner_type = uml_type.split("[")[1].rstrip("]")
        python_base = UML_TO_PYTHON_TYPES.get(base_type, base_type)
        python_inner = UML_TO_PYTHON_TYPES.get(inner_type, inner_type)
        return f"{python_base}[{python_inner}]"
    
    return UML_TO_PYTHON_TYPES.get(uml_type, uml_type)


class TemplateEngine:
    """
    Jinja2-based template engine for code generation.
    Renders parsed UML classes into code files.
    """

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the template engine.

        Args:
            templates_dir: Path to templates directory. Defaults to backend/templates/
        """
        if templates_dir is None:
            # Default to templates directory relative to this file
            templates_dir = str(Path(__file__).parent.parent.parent / "templates")
        
        self.templates_dir = Path(templates_dir)
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Add custom filters
        self.env.filters['python_type'] = python_type_filter
        self.env.filters['lower'] = str.lower
        self.env.filters['upper'] = str.upper

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Render a template with the given context.

        Args:
            template_name: Name of the template file (e.g., 'python/pydantic_model.py.jinja2')
            context: Template variables

        Returns:
            Rendered template content
        """
        template = self.env.get_template(template_name)
        return template.render(**context)

    def generate_model(self, parsed_class: ParsedClass) -> GeneratedFile:
        """
        Generate a Pydantic model from a parsed class.

        Args:
            parsed_class: The parsed class definition

        Returns:
            GeneratedFile with the generated model code
        """
        context = {
            "class_name": parsed_class.name,
            "attributes": parsed_class.attributes,
            "methods": parsed_class.methods,
            "description": parsed_class.description,
            "is_abstract": parsed_class.is_abstract,
            "parent_class": parsed_class.parent_class,
        }
        
        content = self.render_template("python/pydantic_model.py.jinja2", context)
        
        return GeneratedFile(
            file_path=f"models/{parsed_class.name.lower()}.py",
            content=content,
            file_type=FileType.MODEL,
            language="python",
            description=f"Pydantic model for {parsed_class.name}"
        )

    def generate_api_router(self, parsed_class: ParsedClass) -> GeneratedFile:
        """
        Generate a FastAPI router from a parsed class.

        Args:
            parsed_class: The parsed class definition

        Returns:
            GeneratedFile with the generated router code
        """
        context = {
            "class_name": parsed_class.name,
            "attributes": parsed_class.attributes,
            "methods": parsed_class.methods,
            "description": parsed_class.description,
        }
        
        content = self.render_template("python/fastapi_router.py.jinja2", context)
        
        return GeneratedFile(
            file_path=f"api/{parsed_class.name.lower()}_router.py",
            content=content,
            file_type=FileType.API,
            language="python",
            description=f"FastAPI router for {parsed_class.name}"
        )

    def generate_service(self, parsed_class: ParsedClass) -> GeneratedFile:
        """
        Generate a service layer from a parsed class.

        Args:
            parsed_class: The parsed class definition

        Returns:
            GeneratedFile with the generated service code
        """
        context = {
            "class_name": parsed_class.name,
            "attributes": parsed_class.attributes,
            "methods": parsed_class.methods,
            "description": parsed_class.description,
        }
        
        content = self.render_template("python/service.py.jinja2", context)
        
        return GeneratedFile(
            file_path=f"services/{parsed_class.name.lower()}_service.py",
            content=content,
            file_type=FileType.SERVICE,
            language="python",
            description=f"Service layer for {parsed_class.name}"
        )

    def generate_all_for_class(
        self,
        parsed_class: ParsedClass,
        scope: List[str] = None
    ) -> List[GeneratedFile]:
        """
        Generate all code files for a parsed class.

        Args:
            parsed_class: The parsed class definition
            scope: List of what to generate ('models', 'api', 'services')

        Returns:
            List of GeneratedFile objects
        """
        if scope is None:
            scope = ["models", "api", "services"]
        
        files = []
        
        if "models" in scope:
            files.append(self.generate_model(parsed_class))
        
        if "api" in scope:
            files.append(self.generate_api_router(parsed_class))
        
        if "services" in scope:
            files.append(self.generate_service(parsed_class))
        
        return files

    def list_available_templates(self) -> Dict[str, List[str]]:
        """List all available templates organized by language."""
        templates = {}
        
        for lang_dir in self.templates_dir.iterdir():
            if lang_dir.is_dir():
                templates[lang_dir.name] = [
                    f.name for f in lang_dir.iterdir() if f.suffix == '.jinja2'
                ]
        
        return templates
