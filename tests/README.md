# Drawing Package Test Suite

This directory contains tests for the Drawing Package application.

## Testing Infrastructure

The project uses pytest for testing, with special considerations for PyQt GUI tests.

### Test Organization

Tests are organized by component:

- `tests/drawing/` - Tests for drawing elements and core functionality
- `tests/` - Main application tests, including integration tests and action handlers

### Test Categories

Tests are divided into categories:

- **Unit Tests**: Tests individual components in isolation
- **Integration Tests**: Tests interactions between components
- **UI Tests**: Tests that involve Qt GUI components and may be prone to race conditions

### Running Tests

#### Using the Custom Test Runner

The recommended way to run tests is using the custom test runner script:

```bash
# Run all tests (except UI tests)
python run_tests.py

# Run tests with verbose output
python run_tests.py -v

# Run a specific test module
python run_tests.py --module tests/test_action_handlers.py

# Include UI tests
python run_tests.py --include-ui

# Skip integration tests
python run_tests.py --skip-integration

# Adjust pause between test modules
python run_tests.py --pause 2.0
```

#### Using pytest directly

You can also run tests using pytest directly, but be aware of potential issues with UI tests:

```bash
# Run all tests, skipping UI tests
pytest --skip-ui-tests

# Run specific tests
pytest tests/test_action_handlers.py

# Run with verbose output
pytest -v tests/drawing/test_elements.py
```

### Custom Markers

The test suite defines custom markers to categorize tests:

- `@pytest.mark.ui_test`: Tests that interact with Qt UI components
- `@pytest.mark.slow`: Tests that are slow to execute
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.memory_intensive`: Tests that use a lot of memory

### Known Issues

1. **PyQt Memory Management**:

   - Tests involving Qt GUI components can cause crashes due to Qt's C++ memory management
   - The custom test runner helps mitigate this by running tests in isolation

2. **Race Conditions**:

   - Some tests may experience race conditions due to Qt's event loop
   - The test fixtures include workarounds like processing events before cleanup

3. **Order Dependency**:
   - Some tests may be sensitive to execution order
   - The test runner executes tests in a specific order to minimize issues

### Fixtures

The test suite includes several useful fixtures:

- `canvas`: A test Canvas instance with proper cleanup
- `scene`: A test QGraphicsScene
- Various element fixtures (rectangle_element, line_element, etc.)

## Contributing Tests

When adding new tests:

1. Add unit tests for any new functionality
2. Mark UI tests with `@pytest.mark.ui_test`
3. Use the existing fixtures whenever possible
4. Follow the established patterns for test cleanup
5. Verify that your tests run correctly with the test runner
