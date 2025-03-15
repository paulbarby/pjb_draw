"""
Main window component for the Drawing Package UI.

This file contains the MainWindow class which serves as a container for all UI elements
and manages communication between different components.
"""
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    """Main window for the Drawing Package application."""
    
    def __init__(self, parent=None):
        """Initialize the main window."""
        super().__init__(parent)
        # The constructor will be implemented with necessary components
        # This is a placeholder for reconstruction purposes
        
        # Flag for hit area visualization
        self.show_hit_areas = False
    
    def toggle_hit_areas(self):
        """Toggle the visualization of hit areas for debugging."""
        self.show_hit_areas = not self.show_hit_areas
        
        # Update the canvas to show/hide hit areas
        if hasattr(self, 'canvas'):
            self.canvas.set_debug_hit_areas(self.show_hit_areas)
            self.canvas.viewport().update()
            
            status = "enabled" if self.show_hit_areas else "disabled"
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(f"Hit area visualization {status}")
    
    def _show_selection_help(self):
        """Show help about selection methods."""
        QMessageBox.information(
            self,
            "Selection Methods",
            """
            <h2>Element Selection Methods</h2>
            
            <h3>Single-click Selection</h3>
            <p>Click on elements to select them:</p>
            <ul>
                <li><b>Lines:</b> Click within 2 pixels of the line's path</li>
                <li><b>Circles:</b> Click near the circle's edge (within 2 pixels)</li>
                <li><b>Rectangles:</b> Click near the rectangle's edge (within 2 pixels)</li>
                <li><b>Text:</b> Click anywhere within the text's bounding box</li>
                <li><b>Images:</b> Click anywhere within the image</li>
            </ul>
            
            <h3>Area Selection</h3>
            <p>Click and drag with the selection tool to select multiple elements.</p>
            
            <h3>Selection Shortcuts</h3>
            <ul>
                <li><b>Ctrl+Click:</b> Add to or toggle selection</li>
                <li><b>Ctrl+A:</b> Select all elements</li>
                <li><b>Shift+Click:</b> Pan the canvas</li>
                <li><b>Ctrl+H:</b> Toggle hit area visualization (debug)</li>
            </ul>
            
            <h3>Selection Tips</h3>
            <ul>
                <li>For precise line selection, try to click directly on the line</li>
                <li>For circles and rectangles, click on the edge rather than the center</li>
                <li>If you're having difficulty selecting an element, try using the debug hit area visualization (Ctrl+H)</li>
                <li>You can also use the "Select All" option and then deselect elements you don't need</li>
            </ul>
            """
        ) 