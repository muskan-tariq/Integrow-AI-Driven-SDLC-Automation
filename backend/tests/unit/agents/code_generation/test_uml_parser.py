"""
Tests for UML Parser Agent
"""

import pytest
from agents.code_generation.uml_parser import UMLParserAgent, ParsedUMLResult
from models.generated_code import Visibility, RelationshipType

@pytest.fixture
def parser():
    return UMLParserAgent()

class TestUMLParser:
    
    @pytest.mark.asyncio
    async def test_parse_simple_class(self, parser):
        uml = """
        class User {
            -id: UUID
            +username: String
            +email: String
            +login(): Boolean
        }
        """
        result = await parser.parse(uml)
        
        assert result.parse_success
        assert len(result.classes) == 1
        
        user_class = result.classes[0]
        assert user_class.name == "User"
        assert len(user_class.attributes) == 3
        assert len(user_class.methods) == 1
        
        # Check attributes
        assert user_class.attributes[0].name == "id"
        assert user_class.attributes[0].visibility == Visibility.PRIVATE
        assert user_class.attributes[1].name == "username"
        assert user_class.attributes[1].visibility == Visibility.PUBLIC
        
        # Check method
        assert user_class.methods[0].name == "login"
        assert user_class.methods[0].return_type == "Boolean"

    @pytest.mark.asyncio
    async def test_parse_relationships(self, parser):
        uml = """
        class User {
            +id: UUID
        }
        
        class Project {
            +id: UUID
        }
        
        User "1" --> "*" Project : creates
        """
        result = await parser.parse(uml)
        
        assert result.parse_success
        assert len(result.classes) == 2
        assert len(result.relationships) == 1
        
        rel = result.relationships[0]
        assert rel.source == "User"
        assert rel.target == "Project"
        assert rel.relationship_type == RelationshipType.ASSOCIATION
        assert rel.source_multiplicity == "1"
        assert rel.target_multiplicity == "*"
        assert rel.label == "creates"

    @pytest.mark.asyncio
    async def test_parse_inheritance(self, parser):
        uml = """
        class Animal {}
        class Dog extends Animal {}
        """
        result = await parser.parse(uml)
        
        assert len(result.classes) == 2
        dog_class = next(c for c in result.classes if c.name == "Dog")
        assert dog_class.parent_class == "Animal"
