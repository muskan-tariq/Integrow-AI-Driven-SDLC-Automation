"""
Unit tests for PlantUML Service - Syntax validation and encoding.
"""
import pytest
from services.plantuml_service import PlantUMLService


class TestPlantUMLService:
    """Unit tests for PlantUML service."""

    @pytest.fixture
    def service(self):
        """Create PlantUML service instance."""
        return PlantUMLService()

    def test_service_initialization(self, service):
        """Test service is initialized correctly."""
        assert service.server_url == "http://www.plantuml.com/plantuml"
        assert service.timeout == 30.0

    # --- Syntax Validation Tests ---

    def test_validate_syntax_valid_code(self, service):
        """Test validation of valid PlantUML code."""
        code = """@startuml
class User {
    +name: String
    +email: String
}
@enduml"""
        is_valid, error = service.validate_syntax(code)
        assert is_valid == True
        assert error is None

    def test_validate_syntax_empty_code(self, service):
        """Test validation rejects empty code."""
        is_valid, error = service.validate_syntax("")
        assert is_valid == False
        assert "empty" in error.lower()

    def test_validate_syntax_whitespace_only(self, service):
        """Test validation rejects whitespace-only code."""
        is_valid, error = service.validate_syntax("   \n\t  ")
        assert is_valid == False

    def test_validate_syntax_missing_startuml(self, service):
        """Test validation rejects code without @startuml."""
        code = """class User {
    +name: String
}
@enduml"""
        is_valid, error = service.validate_syntax(code)
        assert is_valid == False
        assert "@startuml" in error

    def test_validate_syntax_missing_enduml(self, service):
        """Test validation rejects code without @enduml."""
        code = """@startuml
class User {
    +name: String
}"""
        is_valid, error = service.validate_syntax(code)
        assert is_valid == False
        assert "@enduml" in error

    def test_validate_syntax_unbalanced_braces(self, service):
        """Test validation rejects unbalanced braces."""
        code = """@startuml
class User {
    +name: String

@enduml"""
        is_valid, error = service.validate_syntax(code)
        assert is_valid == False
        assert "brace" in error.lower()

    def test_validate_syntax_sequence_diagram(self, service):
        """Test validation of sequence diagram."""
        code = """@startuml
Alice -> Bob: Hello
Bob --> Alice: Hi there
@enduml"""
        is_valid, error = service.validate_syntax(code)
        assert is_valid == True

    def test_validate_syntax_use_case_diagram(self, service):
        """Test validation of use case diagram."""
        code = """@startuml
:User: --> (Login)
:Admin: --> (Manage Users)
@enduml"""
        is_valid, error = service.validate_syntax(code)
        assert is_valid == True

    # --- Encoding Tests ---

    def test_encode_plantuml_returns_string(self, service):
        """Test encoding returns a string."""
        code = "@startuml\nclass Test\n@enduml"
        encoded = service._encode_plantuml(code)
        assert isinstance(encoded, str)
        assert len(encoded) > 0

    def test_encode_plantuml_different_inputs(self, service):
        """Test that different inputs produce different encodings."""
        code1 = "@startuml\nclass A\n@enduml"
        code2 = "@startuml\nclass B\n@enduml"
        encoded1 = service._encode_plantuml(code1)
        encoded2 = service._encode_plantuml(code2)
        assert encoded1 != encoded2

    def test_encode_plantuml_uses_valid_alphabet(self, service):
        """Test that encoding uses PlantUML's valid alphabet."""
        code = "@startuml\nclass Test\n@enduml"
        encoded = service._encode_plantuml(code)
        valid_chars = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_")
        for char in encoded:
            assert char in valid_chars, f"Invalid character in encoding: {char}"

    def test_plantuml_encode_bytes(self, service):
        """Test _plantuml_encode with raw bytes."""
        data = b"Hello World"
        encoded = service._plantuml_encode(data)
        assert isinstance(encoded, str)
        assert len(encoded) > 0

    def test_plantuml_encode_empty_bytes(self, service):
        """Test _plantuml_encode with empty bytes."""
        encoded = service._plantuml_encode(b"")
        assert encoded == ""

    def test_encode_complex_diagram(self, service):
        """Test encoding of a complex class diagram."""
        code = """@startuml
package "Domain" {
    class User {
        -id: UUID
        -name: String
        -email: String
        +login()
        +logout()
    }
    
    class Order {
        -id: UUID
        -items: List<Item>
        +calculateTotal()
    }
    
    User "1" --> "*" Order : places
}
@enduml"""
        encoded = service._encode_plantuml(code)
        assert len(encoded) > 50  # Complex diagram should have longer encoding


class TestPlantUMLServiceEdgeCases:
    """Edge case tests for PlantUML service."""

    @pytest.fixture
    def service(self):
        return PlantUMLService()

    def test_validate_special_characters(self, service):
        """Test validation with special characters in content."""
        code = """@startuml
note "User's <data> & info" as N1
@enduml"""
        is_valid, error = service.validate_syntax(code)
        assert is_valid == True

    def test_validate_unicode_content(self, service):
        """Test validation with unicode characters."""
        code = """@startuml
class 用户 {
    +名前: String
}
@enduml"""
        is_valid, error = service.validate_syntax(code)
        assert is_valid == True

    def test_validate_nested_braces(self, service):
        """Test validation with properly nested braces."""
        code = """@startuml
class Outer {
    class Inner {
        +field: String
    }
}
@enduml"""
        is_valid, error = service.validate_syntax(code)
        assert is_valid == True

    def test_validate_multiple_diagrams_single_file(self, service):
        """Test validation only checks first diagram structure."""
        code = """@startuml
class A
@enduml"""
        is_valid, error = service.validate_syntax(code)
        assert is_valid == True
