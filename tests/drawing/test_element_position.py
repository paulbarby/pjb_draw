import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import QPointF
from src.drawing.elements import VectorElement
from src.drawing.elements.rectangle_element import RectangleElement

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Element Position Test")
        self.setGeometry(100, 100, 500, 300)
        
        # Main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Status label
        self.status_label = QLabel("Position test")
        layout.addWidget(self.status_label)
        
        # Test buttons
        test_rect_button = QPushButton("Test Rectangle Position")
        test_rect_button.clicked.connect(self.test_rectangle_position)
        layout.addWidget(test_rect_button)
        
        test_direct_button = QPushButton("Test Direct setX/setY")
        test_direct_button.clicked.connect(self.test_direct_position)
        layout.addWidget(test_direct_button)
        
        self.setCentralWidget(main_widget)
    
    def test_rectangle_position(self):
        """Test rectangle position changing through property methods."""
        # Create a rectangle element
        rect = RectangleElement()
        
        # Print initial position
        self.status_label.setText(f"Initial position: x={rect.x()}, y={rect.y()}")
        print(f"Initial position: x={rect.x()}, y={rect.y()}")
        
        # Try changing position through property methods
        print("Attempting to set x=100, y=200 via property methods")
        rect.set_property_value("x", 100)
        rect.set_property_value("y", 200)
        
        # Print new position
        print(f"New position: x={rect.x()}, y={rect.y()}")
        self.status_label.setText(f"New position: x={rect.x()}, y={rect.y()}")
    
    def test_direct_position(self):
        """Test direct position setting."""
        # Create a rectangle element
        rect = RectangleElement()
        
        # Print initial position
        self.status_label.setText(f"Initial position: x={rect.x()}, y={rect.y()}")
        print(f"Initial position: x={rect.x()}, y={rect.y()}")
        
        # Try changing position directly
        print("Attempting to set x=100, y=200 via direct methods")
        rect.setX(100)
        rect.setY(200)
        
        # Print new position
        print(f"New position: x={rect.x()}, y={rect.y()}")
        self.status_label.setText(f"New position: x={rect.x()}, y={rect.y()}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec()) 