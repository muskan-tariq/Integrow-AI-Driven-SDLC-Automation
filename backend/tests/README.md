# InteGrow Backend Tests

Comprehensive test suite organized by test type and module.

## Test Structure

```
tests/
├── unit/                        # Fast, isolated tests (no external deps)
│   ├── agents/                  # Agent unit tests
│   │   ├── test_requirements_agents.py
│   │   ├── test_uml_agents.py
│   │   └── test_git_agents.py
│   ├── api/                     # Router unit tests
│   │   └── test_routers.py
│   ├── services/                # Service unit tests
│   │   └── test_services.py
│   └── models/                  # Model validation tests
│       └── test_models.py
├── integration/                 # Tests requiring external services
│   ├── agents/                  # Agent integration tests
│   │   └── test_agents_integration.py
│   ├── api/                     # API integration tests
│   │   └── test_api_integration.py
│   └── services/                # Service integration tests
│       └── test_services_integration.py
├── fixtures/                    # Shared test fixtures
├── conftest.py                  # Pytest configuration & fixtures
└── README.md                    # This file
```

## Quick Start

```powershell
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run only unit tests (fast)
pytest tests/unit -v

# Run only integration tests
pytest tests/integration -v

# Run tests for specific module
pytest tests/unit/agents -v
pytest tests/unit/api -v
pytest tests/unit/services -v
pytest tests/unit/models -v

# Run with verbose output
pytest -v

# Stop on first failure
pytest -x

# Run tests by marker
pytest -m unit           # Only unit tests
pytest -m integration    # Only integration tests
```

## Coverage Reports

### Terminal Coverage Report
```powershell
pytest --cov=. --cov-report=term-missing
```

### HTML Coverage Report (Interactive)
```powershell
# Generate HTML report
pytest --cov=. --cov-report=html

# Open in browser
start htmlcov\index.html
```

The HTML report provides an interactive view where you can:
- See overall coverage percentage
- Click on any file to view line-by-line coverage
- Identify untested code paths (highlighted in red)

### Combined Terminal + HTML Report
```powershell
pytest --cov=. --cov-report=html --cov-report=term -v 2>&1 | Select-Object -Last 50
```
This generates both HTML and terminal reports, showing the last 50 lines of output for a quick coverage summary.

## Test Categories

### Unit Tests (`tests/unit/`)
Fast, isolated tests with no external dependencies:
- **agents/**: Parser, Ambiguity, Completeness, Ethics, UML, Git agents
- **api/**: Auth, Project, Requirements, UML routers
- **services/**: Encryption, PlantUML, LLM services
- **models/**: Pydantic model validation

### Integration Tests (`tests/integration/`)
Tests requiring external services (database, APIs):
- **agents/**: End-to-end agent workflows
- **api/**: Full API endpoint testing
- **services/**: Supabase, WebSocket, external API integration

## Writing New Tests

1. **Unit tests**: Add to `tests/unit/<module>/`
2. **Integration tests**: Add to `tests/integration/<module>/`
3. Use appropriate markers: `@pytest.mark.unit` or `@pytest.mark.integration`
4. Follow naming convention: `test_<functionality>.py`
