"""
Tests for the drawing application.
"""

import unittest
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gui.app_window import ApplicationWindow

class TestApplicationWindow(unittest.TestCase):
    """Test cases for ApplicationWindow class."""
    
    def test_creation(self):
        """Test that the application window can be created."""
        # This is a simple test to ensure the class can be instantiated
        # In a real test, you would use a mock framework or test toolkit
        try:
            # We don't actually run the app, just test instantiation
            app = ApplicationWindow()
            created = True
        except Exception as e:
            created = False
            print(f"Error: {e}")
        
        self.assertTrue(created)

if __name__ == "__main__":
    unittest.main()
