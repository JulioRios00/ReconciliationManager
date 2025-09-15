# Testing Guide for ReconciliationManager

## Overview
This guide explains how to set up and run unit tests for the ReconciliationManager project.

## Test Structure
```
src/tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_reconciliation_service.py    # Service layer tests
├── test_reconciliation_repository.py # Repository layer tests
└── test_models.py           # Model tests
```

## Prerequisites

### 1. Install Dependencies
Make sure all testing dependencies are installed:
```bash
pip install -r requirements.txt
```

### 2. Required Packages
The project already includes the necessary testing packages:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `coverage` - Code coverage

## Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest src/tests/test_reconciliation_service.py

# Run specific test class
pytest src/tests/test_reconciliation_service.py::TestReconciliationService

# Run specific test method
pytest src/tests/test_reconciliation_service.py::TestReconciliationService::test_parse_date_valid_date_string
```

### Coverage Reports
```bash
# Generate coverage report
pytest --cov=src

# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View HTML report in browser
open htmlcov/index.html
```

### Test Markers
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Test Categories

### 1. Unit Tests (`@pytest.mark.unit`)
- Test individual functions/methods in isolation
- Mock all external dependencies (database, APIs, etc.)
- Focus on business logic

### 2. Integration Tests (`@pytest.mark.integration`)
- Test interactions between components
- May use test database
- Slower than unit tests

### 3. Slow Tests (`@pytest.mark.slow`)
- Tests that take longer to run
- Can be skipped in CI for faster feedback

## Key Testing Concepts

### Fixtures
Shared test data and setup code:
```python
@pytest.fixture
def mock_db_session():
    """Mock database session for testing"""
    return Mock(spec=Session)

@pytest.fixture
def reconciliation_service(mock_db_session):
    """Create service with mocked dependencies"""
    return ReconciliationService(mock_db_session)
```

### Mocking Strategy
1. **Database Layer**: Mock SQLAlchemy sessions and queries
2. **External APIs**: Mock HTTP requests and responses
3. **File System**: Mock file operations
4. **Time-dependent code**: Mock datetime functions

### Test Data
Use realistic but minimal test data:
```python
@pytest.fixture
def sample_air_record():
    """Sample air company invoice record"""
    record = Mock()
    record.Supplier = "Test Airlines"
    record.FlightDate = date(2023, 1, 15)
    record.Qty = 100
    return record
```

## Best Practices

### 1. Test Naming
- Use descriptive names: `test_get_all_reconciliation_data_success`
- Follow pattern: `test_<method_name>_<scenario>_<expected_result>`

### 2. Test Isolation
- Each test should be independent
- Use fixtures for setup/teardown
- Don't rely on test execution order

### 3. Mocking
- Mock external dependencies
- Verify mock interactions when necessary
- Use `spec` parameter for better error messages

### 4. Assertions
- Test one thing per test method
- Use descriptive assertion messages
- Test both success and failure scenarios

### 5. Coverage Goals
- Aim for 80%+ code coverage
- Focus on critical business logic
- Don't test generated code (ORM models)

## Example Test Patterns

### Testing Service Methods
```python
def test_get_all_reconciliation_data_success(self, reconciliation_service, mock_reconciliation_repository):
    # Arrange
    mock_record = Mock()
    mock_record.serialize.return_value = {"id": 1}
    mock_reconciliation_repository.get_all.return_value = [mock_record]

    # Act
    result = reconciliation_service.get_all_reconciliation_data()

    # Assert
    assert "data" in result
    assert len(result["data"]) == 1
    mock_reconciliation_repository.get_all.assert_called_once()
```

### Testing Exception Handling
```python
def test_get_all_reconciliation_data_exception(self, reconciliation_service, mock_reconciliation_repository):
    # Arrange
    mock_reconciliation_repository.get_all.side_effect = Exception("Database error")

    # Act
    result = reconciliation_service.get_all_reconciliation_data()

    # Assert
    assert "message" in result
    assert "error" in result
    assert result[1] == 501
```

### Testing Utility Functions
```python
def test_safe_int_valid_value(self, reconciliation_service):
    result = reconciliation_service._safe_int("42")
    assert result == 42

def test_safe_int_invalid_value(self, reconciliation_service):
    result = reconciliation_service._safe_int("invalid")
    assert result == 0
```

## CI/CD Integration

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
        python-version: '3.9'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest --cov=src --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure PYTHONPATH includes src directory
2. **Mock Errors**: Use `spec` parameter for better mocking
3. **Database Errors**: Always mock database operations in unit tests
4. **Coverage Issues**: Exclude test files and generated code

### Running Tests in IDE
- VS Code: Install Python extension, configure test settings
- PyCharm: Configure pytest as test runner
- Set working directory to project root

## Next Steps
1. Run the existing tests: `pytest`
2. Add more test cases for uncovered code
3. Set up pre-commit hooks for test execution
4. Configure CI/CD pipeline
5. Add performance tests for critical paths

## Resources
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)
- [Testing in Python](https://realpython.com/python-testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#testing)
