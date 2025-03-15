"""
Simple visual test for hit detection.

This script creates a window with various elements and visualizes the hit areas,
allowing for real-time testing of hit detection by moving the mouse.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QVBoxLayout, QWidget, QLabel, QCheckBox
)
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QPen, QColor, QBrush, QPainter

from src.drawing.elements.line_element import LineElement
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.text_element import TextElement
from src.utils.element_hit_detection import is_element_hit, debug_visualize_hit_areas

class HitTestView(QGraphicsView):
    """Graphics view for testing hit detection."""
    
    def __init__(self, parent=None):
        """Initialize the view."""
        super().__init__(parent)
        
        # Create the scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Set scene rectangle
        self.scene.setSceneRect(0, 0, 500, 400)
        
        # Set up the view
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        # Create elements for testing
        self.create_test_elements()
        
        # Latest hit element
        self.hit_element = None
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Flag to show hit areas
        self.show_hit_areas = True
    
    def create_test_elements(self):
        """Create various elements for testing hit detection."""
        # Create a line
        start_point = QPointF(50, 50)
        end_point = QPointF(200, 150)
        self.line = LineElement(start_point, end_point)
        self.line.setPen(QPen(QColor(255, 0, 0), 2))
        self.scene.addItem(self.line)
        
        # Create a rectangle
        self.rect = RectangleElement()
        self.rect._rect = QRectF(250, 50, 150, 100)
        self.rect.setPen(QPen(QColor(0, 255, 0), 2))
        self.rect.setBrush(QBrush(QColor(0, 255, 0, 50)))
        self.scene.addItem(self.rect)
        
        # Create a circle
        self.circle = CircleElement()
        self.circle.center = QPointF(125, 250)
        self.circle.radius = 50
        self.circle.setPen(QPen(QColor(0, 0, 255), 2))
        self.circle.setBrush(QBrush(QColor(0, 0, 255, 50)))
        self.scene.addItem(self.circle)
        
        # Create a text element
        text_content = "Test Text"
        position = QPointF(300, 250)
        self.text = TextElement(text_content, position)
        self.text.setFont(QApplication.font())
        self.scene.addItem(self.text)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events to check for hits."""
        super().mouseMoveEvent(event)
        
        # Convert view coordinates to scene coordinates
        scene_pos = self.mapToScene(event.position().toPoint())
        
        # Reset previous hit
        if self.hit_element:
            if isinstance(self.hit_element, LineElement):
                self.hit_element.setPen(QPen(QColor(255, 0, 0), 2))
            elif isinstance(self.hit_element, RectangleElement):
                self.hit_element.setPen(QPen(QColor(0, 255, 0), 2))
            elif isinstance(self.hit_element, CircleElement):
                self.hit_element.setPen(QPen(QColor(0, 0, 255), 2))
        
        self.hit_element = None
        
        # Check each element
        for element in [self.line, self.rect, self.circle, self.text]:
            if is_element_hit(element, scene_pos):
                self.hit_element = element
                # Highlight the hit element
                if isinstance(element, LineElement):
                    element.setPen(QPen(QColor(255, 128, 128), 3))
                elif isinstance(element, RectangleElement):
                    element.setPen(QPen(QColor(128, 255, 128), 3))
                elif isinstance(element, CircleElement):
                    element.setPen(QPen(QColor(128, 128, 255), 3))
                break
        
        # Update the view
        self.viewport().update()
    
    def paintEvent(self, event):
        """Custom paint event to show hit areas."""
        super().paintEvent(event)
        
        # If showing hit areas, draw them
        if self.show_hit_areas:
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Set the transform to match the view
            painter.setWorldTransform(self.transform())
            
            # Visualize hit areas
            debug_visualize_hit_areas(self.scene, painter)
            
            painter.end()
    
    def toggle_hit_areas(self, show):
        """Toggle showing hit areas."""
        self.show_hit_areas = show
        self.viewport().update()

class MainWindow(QMainWindow):
    """Main window for the hit test application."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.setWindowTitle("Hit Detection Test")
        self.resize(600, 500)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create the graphics view
        self.view = HitTestView()
        layout.addWidget(self.view)
        
        # Create status label
        self.status_label = QLabel("Move the mouse over elements to test hit detection")
        layout.addWidget(self.status_label)
        
        # Create checkbox for hit areas
        self.hit_areas_checkbox = QCheckBox("Show Hit Areas")
        self.hit_areas_checkbox.setChecked(True)
        self.hit_areas_checkbox.toggled.connect(self.view.toggle_hit_areas)
        layout.addWidget(self.hit_areas_checkbox)
        
        # Instructions label
        instructions = QLabel(
            "Red: Line Element - blue inside hit area<br>"
            "Green: Rectangle Element - hit on edges only<br>"
            "Blue: Circle Element - hit on edge only<br>"
            "Black: Text Element - hit anywhere in bounding box"
        )
        layout.addWidget(instructions)

def main():
    """Run the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 