"""
Main entry point for the Drawing Package application.
"""
import sys
import logging
from PyQt6.QtWidgets import QApplication

from src.app import DrawingApp

if __name__ == "__main__":
    logging.info("Starting Drawing Package application")
    
    app = QApplication(sys.argv)
    window = DrawingApp()
    window.show()
    
    sys.exit(app.exec())
