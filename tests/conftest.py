"""
Global test configuration and fixtures.
"""
import pytest
import sys
import os
import time

# Add a custom option to skip UI tests
def pytest_addoption(parser):
    parser.addoption(
        "--skip-ui-tests",
        action="store_true",
        default=False,
        help="Skip tests that interact with the UI",
    )

# Skip UI tests if the option is enabled
def pytest_configure(config):
    config.addinivalue_line("markers", "ui_test: mark test as UI test")

def pytest_collection_modifyitems(config, items):
    if config.getoption("--skip-ui-tests"):
        skip_ui = pytest.mark.skip(reason="UI tests skipped with --skip-ui-tests option")
        for item in items:
            # Skip tests in test_canvas.py and test_app.py modules
            if "test_canvas.py" in item.nodeid or "test_app.py" in item.nodeid:
                item.add_marker(skip_ui)
                
            # Also skip any test explicitly marked as UI test
            if "ui_test" in item.keywords:
                item.add_marker(skip_ui)

# Fixture that runs between each test to ensure proper Qt cleanup
@pytest.fixture(autouse=True, scope="function")
def qt_cleanup(request):
    """Auto-use fixture to clean up Qt resources between tests."""
    yield
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.processEvents()
            time.sleep(0.05)  # Small delay to let Qt process events
            app.processEvents()
    except Exception:
        pass

# Cleanup Qt resources after all tests
@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Clean up Qt resources after all tests are done."""
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.closeAllWindows()
            app.processEvents()
            time.sleep(0.1)  # Give Qt time to process events
            app.processEvents()
    except Exception:
        pass 