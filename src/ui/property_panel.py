"""
Property panel component for the Drawing Package.

This module provides a panel for editing properties of selected drawing elements.
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
    QPushButton, QColorDialog, QComboBox, QFormLayout,
    QLineEdit, QGroupBox, QDoubleSpinBox, QCheckBox,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

logger = logging.getLogger(__name__)

class PropertyPanel(QWidget):
    """
    Property panel for viewing and editing properties of selected elements.
    
    This panel displays relevant properties based on the type of selected element
    and allows the user to modify those properties.
    """
    
    # Signal emitted when a property has been changed by the user
    property_changed = pyqtSignal(str, object)
    
    # Signal emitted when an element is selected from the list
    element_selected_from_list = pyqtSignal(object)
    
    def __init__(self, parent=None):
        """Initialize the property panel."""
        super().__init__(parent)
        
        # Set up the main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Create a title label
        self.title_label = QLabel("Properties")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.main_layout.addWidget(self.title_label)
        
        # Create a list of elements
        self.elements_group = QGroupBox("Elements")
        self.elements_group_layout = QVBoxLayout(self.elements_group)
        
        # Create the list widget
        self.elements_list = QListWidget()
        self.elements_list.setMaximumHeight(150)  # Limit height
        self.elements_list.itemClicked.connect(self._on_element_selected_from_list)
        self.elements_group_layout.addWidget(self.elements_list)
        
        # Add button to refresh the list
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self._on_refresh_list_clicked)
        self.elements_group_layout.addWidget(self.refresh_button)
        
        self.main_layout.addWidget(self.elements_group)
        
        # Create a form layout for property controls
        self.form_layout = QFormLayout()
        self.form_layout.setVerticalSpacing(8)
        self.form_layout.setHorizontalSpacing(15)
        
        # Group box for appearance properties
        self.appearance_group = QGroupBox("Appearance")
        self.appearance_layout = QFormLayout(self.appearance_group)
        
        # Color selection
        self.color_preview = QWidget()
        self.color_preview.setFixedSize(30, 20)
        self.color_preview.setAutoFillBackground(True)
        self.color_button = QPushButton("Choose...")
        self.color_button.clicked.connect(self._on_color_button_clicked)
        
        color_layout = QHBoxLayout()
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.addWidget(self.color_preview)
        color_layout.addWidget(self.color_button)
        
        self.appearance_layout.addRow(QLabel("Color:"), color_layout)
        
        # Line thickness control
        self.thickness_spinbox = QSpinBox()
        self.thickness_spinbox.setRange(1, 20)
        self.thickness_spinbox.setValue(1)
        self.thickness_spinbox.valueChanged.connect(
            lambda value: self.property_changed.emit("line_thickness", value)
        )
        self.appearance_layout.addRow(QLabel("Thickness:"), self.thickness_spinbox)
        
        # Line style dropdown
        self.line_style_combo = QComboBox()
        self.line_style_combo.addItems(["Solid", "Dashed", "Dotted"])
        self.line_style_combo.currentTextChanged.connect(
            lambda text: self.property_changed.emit("line_style", text)
        )
        self.appearance_layout.addRow(QLabel("Style:"), self.line_style_combo)
        
        self.main_layout.addWidget(self.appearance_group)
        
        # Group box for geometry properties
        self.geometry_group = QGroupBox("Geometry")
        self.geometry_layout = QFormLayout(self.geometry_group)
        
        # Position controls
        self.x_spinbox = QDoubleSpinBox()
        self.x_spinbox.setRange(0, 10000)
        self.x_spinbox.setDecimals(1)
        self.x_spinbox.valueChanged.connect(
            lambda value: self.property_changed.emit("x", value)
        )
        self.geometry_layout.addRow(QLabel("X:"), self.x_spinbox)
        
        self.y_spinbox = QDoubleSpinBox()
        self.y_spinbox.setRange(0, 10000)
        self.y_spinbox.setDecimals(1)
        self.y_spinbox.valueChanged.connect(
            lambda value: self.property_changed.emit("y", value)
        )
        self.geometry_layout.addRow(QLabel("Y:"), self.y_spinbox)
        
        # Size controls
        self.width_spinbox = QDoubleSpinBox()
        self.width_spinbox.setRange(1, 10000)
        self.width_spinbox.setDecimals(1)
        self.width_spinbox.valueChanged.connect(
            lambda value: self.property_changed.emit("width", value)
        )
        self.geometry_layout.addRow(QLabel("Width:"), self.width_spinbox)
        
        self.height_spinbox = QDoubleSpinBox()
        self.height_spinbox.setRange(1, 10000)
        self.height_spinbox.setDecimals(1)
        self.height_spinbox.valueChanged.connect(
            lambda value: self.property_changed.emit("height", value)
        )
        self.geometry_layout.addRow(QLabel("Height:"), self.height_spinbox)
        
        self.main_layout.addWidget(self.geometry_group)
        
        # Group box for text properties (initially hidden)
        self.text_group = QGroupBox("Text")
        self.text_layout = QFormLayout(self.text_group)
        
        self.text_edit = QLineEdit()
        self.text_edit.textChanged.connect(
            lambda text: self.property_changed.emit("text", text)
        )
        self.text_layout.addRow(QLabel("Content:"), self.text_edit)
        
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(6, 72)
        self.font_size_spinbox.setValue(12)
        self.font_size_spinbox.valueChanged.connect(
            lambda value: self.property_changed.emit("font_size", value)
        )
        self.text_layout.addRow(QLabel("Font Size:"), self.font_size_spinbox)
        
        self.main_layout.addWidget(self.text_group)
        self.text_group.setVisible(False)  # Hide initially
        
        # Add spacer to push everything to the top
        self.main_layout.addStretch(1)
        
        # Store current element type and reference
        self.current_element = None
        self.current_element_type = None
        
        # Dictionary to store elements by index in the list
        self.element_items = {}
        
        # Set initial state to show no selection
        self.set_no_selection()
        
        logger.info("Property panel initialized")
    
    def _on_element_selected_from_list(self, item):
        """Handle element selection from the list."""
        # Get the item's row to use as index
        row = self.elements_list.row(item)
        element = self.element_items.get(row)
        if element:
            self.element_selected_from_list.emit(element)
    
    def _on_refresh_list_clicked(self):
        """Refresh the elements list."""
        # This will trigger a refresh from the app
        self.element_selected_from_list.emit(None)
        
    def update_elements_list(self, elements):
        """Update the list of elements displayed in the panel."""
        self.elements_list.clear()
        self.element_items = {}
        
        for i, element in enumerate(elements):
            element_type = type(element).__name__
            item_text = f"{i+1}: {element_type}"
            item = QListWidgetItem(item_text)
            
            # If this is the currently selected element, highlight it
            if element == self.current_element:
                item.setBackground(QColor(220, 230, 255))
                
            self.elements_list.addItem(item)
            # Use the row number as the key instead of the item itself
            self.element_items[i] = element
            
    def _on_color_button_clicked(self):
        """Open a color dialog when the color button is clicked."""
        # Get the current color from the preview widget
        palette = self.color_preview.palette()
        current_color = palette.color(self.color_preview.backgroundRole())
        
        # Open the color dialog
        color = QColorDialog.getColor(current_color, self, "Select Color")
        
        if color.isValid():
            self._update_color_preview(color)
            self.property_changed.emit("color", color)
    
    def _update_color_preview(self, color):
        """Update the color preview widget with the given color."""
        palette = self.color_preview.palette()
        palette.setColor(self.color_preview.backgroundRole(), color)
        self.color_preview.setPalette(palette)
    
    def update_from_element(self, element):
        """Update the property panel based on the selected element."""
        if not element:
            self.set_no_selection()
            return
        
        # Store reference to the current element
        self.current_element = element
        element_type = type(element).__name__
        self.current_element_type = element_type
        
        # Update list selection if this element is in our list
        self._highlight_current_element_in_list()
        
        # Enable the panel and update the title
        self.setEnabled(True)
        self.title_label.setText(f"{element_type} Properties")
        
        # Temporarily block signals to prevent triggering updates while setting values
        self._block_signals(True)
        
        # Update common properties
        if hasattr(element, "pen"):
            # Check if pen is a method or property
            if callable(element.pen):
                # It's a method - call it to get the pen
                pen = element.pen()
                self._update_color_preview(pen.color())
                self.thickness_spinbox.setValue(int(pen.width()))
            else:
                # It's a property - access directly
                self._update_color_preview(element.pen.color())
                self.thickness_spinbox.setValue(int(element.pen.width()))
        
        # Update geometry properties
        if hasattr(element, "boundingRect"):
            rect = element.boundingRect()
            self.x_spinbox.setValue(element.x() + rect.x())
            self.y_spinbox.setValue(element.y() + rect.y())
            self.width_spinbox.setValue(rect.width())
            self.height_spinbox.setValue(rect.height())
        
        # Show/hide specific property groups based on element type
        if "Text" in element_type:
            self.text_group.setVisible(True)
            
            # Handle text content - could be property or method
            if hasattr(element, "text"):
                if callable(element.text):
                    self.text_edit.setText(element.text())
                else:
                    self.text_edit.setText(element.text)
            
            # Handle font - could be property or method
            if hasattr(element, "font"):
                if callable(element.font):
                    self.font_size_spinbox.setValue(element.font().pointSize())
                else:
                    self.font_size_spinbox.setValue(element.font.pointSize())
        else:
            self.text_group.setVisible(False)
        
        # Restore signal handling
        self._block_signals(False)
    
    def _highlight_current_element_in_list(self):
        """Highlight the currently selected element in the list."""
        # Find the item that corresponds to the current element
        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            element = self.element_items.get(i)
            
            if element == self.current_element:
                item.setBackground(QColor(220, 230, 255))
            else:
                item.setBackground(Qt.GlobalColor.white)
    
    def set_no_selection(self):
        """Set the panel to show that no element is selected."""
        self.current_element = None
        self.current_element_type = None
        self.title_label.setText("No Selection")
        self.setEnabled(False)
        self.text_group.setVisible(False)
        
        # Clear highlight in the elements list
        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            item.setBackground(Qt.GlobalColor.white)
    
    def _block_signals(self, block):
        """Block or unblock signals for all input widgets."""
        for widget in [
            self.thickness_spinbox, self.line_style_combo,
            self.x_spinbox, self.y_spinbox,
            self.width_spinbox, self.height_spinbox,
            self.text_edit, self.font_size_spinbox
        ]:
            widget.blockSignals(block)
