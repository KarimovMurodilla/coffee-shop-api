# Testing Guide

This document describes how to run and write tests for the Coffee Shop API project.

## Test Structure

The test suite is organized into three levels following the testing pyramid:

```
tests/
├── unit/                   # Unit tests (fast, isolated)
│   ├── test_entities.py   # Domain entity tests
│   └── test_use_cases.py  # Use case tests
├── integration/            # Integration tests (with database)
│   ├── test_repositories.py
│   └── test_services.py
└── e2e/                    # End-to-end tests (full API)
    └── test_api.py
```

### Test Types

1. **Unit Tests** (`tests/unit/`)
   - Test individual components in isolation
   - No external dependencies (database, network, etc.)
   - Use mocks and stubs
   - Very fast execution
   - Example: Testing User entity methods

2. **Integration Tests** (`tests/integration/`)
   - Test interaction between components
   - Use real database (in-memory SQLite)
   - Test repository and service implementations
   - Slower than unit tests
   - Example: Testing SQLAlchemy repository operations

3. **End-to-End Tests** (`tests/e2e/`)
   - Test complete user flows through HTTP API
   - Test full request/response cycle
   - Most comprehensive but slowest
   - Example: Testing signup → login → access protected resource

## Installation

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

Or with Docker:

```bash
docker-compose exec api pip install -r requirements-test.txt
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Types

```bash
# Unit tests only (fast)
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# End-to-end tests only
pytest tests/e2e/
```

### Run Specific Test File

```bash
pytest tests/unit/test_entities.py
```

### Run Specific Test Class or Function

```bash
# Run specific class
pytest tests/unit/test_entities.py::TestUser

# Run specific test function
pytest tests/unit/test_entities.py::TestUser::test_user_creation
```

### Run Tests with Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Open HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Run Tests in Docker

```bash
# Run all tests
docker-compose exec api pytest

# Run with coverage
docker-compose exec api pytest --cov=app --cov-report=term

# Run specific test type
docker-compose exec api pytest tests/unit/
```

### Run Tests with Verbose Output

```bash
# More detailed output
pytest -v

# Even more detailed with print statements
pytest -vv -s

# Show local variables on failure
pytest -vv -l
```

### Run Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4
```

## Test Markers

Tests are marked with custom markers for categorization:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only e2e tests
pytest -m e2e

# Run all except slow tests
pytest -m "not slow"
```

## Writing Tests

### Unit Test Example

```python
import pytest
from app.domain.entities import User, UserRole

class TestUser:
    def test_user_creation(self):
        """Test creating a user entity."""
        user = User(
            id=1,
            email="test@example.com",
            hashed_password="hashed",
            first_name="John",
            last_name="Doe",
            role=UserRole.USER,
            is_verified=False,
            verification_code="code123",
            verification_code_expires_at=datetime.utcnow() + timedelta(hours=48),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        assert user.id == 1
        assert user.email == "test@example.com"
```

### Integration Test Example

```python
import pytest
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

@pytest.mark.asyncio
async def test_create_user(user_repository):
    """Test creating a user in database."""
    user = await user_repository.create(sample_user)
    
    assert user.id is not None
    assert user.email == sample_user.email
```

### End-to-End Test Example

```python
import pytest

@pytest.mark.asyncio
async def test_signup_flow(client):
    """Test user signup flow."""
    response = await client.post(
        "/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
```

## Test Fixtures

Common fixtures are defined in `tests/conftest.py`:

```python
@pytest.fixture
def sample_user():
    """Create sample user entity."""
    return User(...)

@pytest.fixture
async def client():
    """Create test HTTP client."""
    async with AsyncClient(app=app) as ac:
        yield ac
```

## Continuous Integration

Tests can be run automatically in CI/CD pipelines:

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Test Coverage Goals

Target coverage levels:
- **Overall**: > 80%
- **Domain Layer**: > 95% (critical business logic)
- **Application Layer**: > 90% (use cases)
- **Infrastructure Layer**: > 70% (external dependencies)
- **API Layer**: > 80% (endpoints)

Check current coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

## Best Practices

### 1. Test Naming

Use descriptive names that explain what is being tested:

```python
# Good
def test_user_can_verify_with_valid_code()

# Bad
def test_verify()
```

### 2. Test Structure (AAA Pattern)

Follow Arrange-Act-Assert pattern:

```python
def test_example():
    # Arrange: Set up test data
    user = create_user()
    
    # Act: Execute the code being tested
    result = user.verify("code123")
    
    # Assert: Verify the results
    assert result is True
```

### 3. One Assertion Per Test

Focus each test on one specific behavior:

```python
# Good
def test_user_is_verified_after_verification():
    user.verify()
    assert user.is_verified is True

def test_verification_code_is_cleared_after_verification():
    user.verify()
    assert user.verification_code is None

# Avoid multiple unrelated assertions
```

### 4. Use Fixtures for Common Setup

```python
@pytest.fixture
def verified_user():
    user = create_user()
    user.verify()
    return user

def test_verified_user_behavior(verified_user):
    assert verified_user.is_verified is True
```

### 5. Mock External Dependencies

```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_signup_sends_email(mock_email_service):
    mock_email_service.send_verification_email = AsyncMock()
    
    await signup_use_case.execute(request)
    
    mock_email_service.send_verification_email.assert_called_once()
```

### 6. Test Edge Cases

```python
def test_verify_with_expired_code()
def test_verify_with_invalid_code()
def test_verify_with_empty_code()
def test_verify_already_verified_user()
```

### 7. Use Parameterized Tests

```python
@pytest.mark.parametrize("password,expected", [
    ("short", False),
    ("Valid123!", True),
    ("", False),
    ("12345678", True),
])
def test_password_validation(password, expected):
    result = validate_password(password)
    assert result == expected
```

## Debugging Tests

### Run Single Test with Print Statements

```bash
pytest tests/unit/test_entities.py::TestUser::test_user_creation -s
```

### Use pytest Debugger

```bash
# Add breakpoint in test
def test_something():
    import pdb; pdb.set_trace()
    # or
    breakpoint()

# Run pytest
pytest --pdb
```

### View Full Error Traceback

```bash
pytest --tb=long
```

## Performance Testing

For performance testing, use `pytest-benchmark`:

```python
def test_password_hashing_performance(benchmark):
    password_service = BcryptPasswordService()
    
    result = benchmark(password_service.hash_password, "password123")
    
    assert result is not None
```

## Test Database

Integration and E2E tests use an in-memory SQLite database that is created and destroyed for each test session:

```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

This ensures:
- Tests are isolated
- Fast execution
- No cleanup needed
- No conflicts with production database

## Common Issues

### 1. Async Tests Not Running

Make sure to:
- Install `pytest-asyncio`
- Mark async tests with `@pytest.mark.asyncio`
- Set `asyncio_mode = auto` in `pytest.ini`

### 2. Database Connection Errors

- Check that test database is properly configured
- Ensure fixtures are properly awaited
- Verify database is created before tests run

### 3. Import Errors

- Ensure project root is in Python path
- Check `conftest.py` configuration
- Verify all `__init__.py` files exist

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## Quick Reference

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific type
pytest tests/unit/

# Run with markers
pytest -m unit

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Show print output
pytest -s

# Parallel execution
pytest -n 4
```
