"""
Main entry point for the drawing application.
"""

import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gui.app_window import ApplicationWindow

def main():
    """Main function to start the application."""
    app = ApplicationWindow()
    app.run()

if __name__ == "__main__":
    main()
