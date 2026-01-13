"""
Tests for Template Engine
"""

import pytest
from agents.code_generation.template_engine import TemplateEngine
from models.generated_code import ParsedClass, ParsedAttribute, ParsedMethod, Visibility

@pytest.fixture
def engine():
    return TemplateEngine()

@pytest.fixture
def simple_class():
    return ParsedClass(
        name="Product",
        attributes=[
            ParsedAttribute(name="id", type="UUID", visibility=Visibility.PRIVATE),
            ParsedAttribute(name="name", type="String", visibility=Visibility.PUBLIC),
            ParsedAttribute(name="price", type="float", visibility=Visibility.PUBLIC)
        ],
        methods=[
            ParsedMethod(name="calculate_tax", return_type="float", visibility=Visibility.PUBLIC)
        ]
    )

class TestTemplateEngine:
    
    def test_generate_pydantic_model(self, engine, simple_class):
        generated = engine.generate_model(simple_class)
        
        assert generated.file_path == "models/product.py"
        assert "class Product(BaseModel):" in generated.content
        assert "id: UUID" in generated.content
        assert "name: str" in generated.content
        assert "price: float" in generated.content
        assert "def calculate_tax(self)" in generated.content

    def test_generate_fastapi_router(self, engine, simple_class):
        generated = engine.generate_api_router(simple_class)
        
        assert generated.file_path == "api/product_router.py"
        assert 'router = APIRouter(prefix="/api/products"' in generated.content
        assert "@router.get(" in generated.content
        assert "@router.post(" in generated.content
        
    def test_generate_service(self, engine, simple_class):
        generated = engine.generate_service(simple_class)
        
        assert generated.file_path == "services/product_service.py"
        assert "class ProductService:" in generated.content
        assert "async def get_all(self)" in generated.content
        assert "async def create(self" in generated.content
