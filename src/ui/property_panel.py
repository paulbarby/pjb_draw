"""
Property panel component for the Drawing Package.

This module provides a panel for editing properties of selected drawing elements.
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
    QPushButton, QColorDialog, QComboBox, QFormLayout,
    QLineEdit, QGroupBox, QDoubleSpinBox, QCheckBox,
    QListWidget, QListWidgetItem, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette

logger = logging.getLogger(__name__)

class ColorFrame(QFrame):
    """A simple frame that displays a solid color."""
    
    def __init__(self, color=None, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.setLineWidth(1)
        self.setMinimumSize(30, 20)
        self.setMaximumSize(30, 20)
        self._color = color or QColor(0, 0, 0)
        self.setStyleSheet(f"background-color: {self._color.name()};")
        
    def set_color(self, color):
        """Set the color of the frame."""
        self._color = color
        self.setStyleSheet(f"background-color: {self._color.name()};")
        self.update()
        
    def get_color(self):
        """Get the current color of the frame."""
        return self._color

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
        
        # Apply size policy for better responsive behavior
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        # Create a title label
        self.title_label = QLabel("Properties")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.main_layout.addWidget(self.title_label)
        
        # Create a list of elements
        self.elements_group = QGroupBox("Elements")
        self.elements_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.elements_group_layout = QVBoxLayout(self.elements_group)
        
        # Create the list widget
        self.elements_list = QListWidget()
        self.elements_list.setMaximumHeight(150)  # Limit height
        self.elements_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
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
        self.appearance_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.appearance_layout = QFormLayout(self.appearance_group)
        
        # Color selection - use ColorFrame instead of QWidget
        self.color_preview = ColorFrame(QColor(0, 0, 0))
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
        self.geometry_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.geometry_layout = QFormLayout(self.geometry_group)
        
        # Position controls - updated range to support negative values
        self.x_spinbox = QDoubleSpinBox()
        self.x_spinbox.setRange(-10000, 10000)  # Allow negative coordinates
        self.x_spinbox.setDecimals(1)
        self.x_spinbox.valueChanged.connect(
            lambda value: self._on_spinbox_value_changed("visual_x", value, self.x_spinbox)
        )
        self.geometry_layout.addRow(QLabel("X:"), self.x_spinbox)
        
        self.y_spinbox = QDoubleSpinBox()
        self.y_spinbox.setRange(-10000, 10000)  # Allow negative coordinates
        self.y_spinbox.setDecimals(1)
        self.y_spinbox.valueChanged.connect(
            lambda value: self._on_spinbox_value_changed("visual_y", value, self.y_spinbox)
        )
        self.geometry_layout.addRow(QLabel("Y:"), self.y_spinbox)
        
        # Size controls
        self.width_spinbox = QDoubleSpinBox()
        self.width_spinbox.setRange(1, 10000)
        self.width_spinbox.setDecimals(1)
        self.width_spinbox.valueChanged.connect(
            lambda value: self._on_spinbox_value_changed("width", value, self.width_spinbox)
        )
        self.geometry_layout.addRow(QLabel("Width:"), self.width_spinbox)
        
        self.height_spinbox = QDoubleSpinBox()
        self.height_spinbox.setRange(1, 10000)
        self.height_spinbox.setDecimals(1)
        self.height_spinbox.valueChanged.connect(
            lambda value: self._on_spinbox_value_changed("height", value, self.height_spinbox)
        )
        self.geometry_layout.addRow(QLabel("Height:"), self.height_spinbox)
        
        self.main_layout.addWidget(self.geometry_group)
        
        # Group box for text properties (initially hidden)
        self.text_group = QGroupBox("Text")
        self.text_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
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
        
        # Add stretch to push content to top when resizing
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
        """Handle refresh list button click."""
        if hasattr(self, 'on_refresh_list'):
            self.on_refresh_list()
            
    def _on_color_button_clicked(self):
        """Handle color button click to open color picker."""
        if not self.current_element and not hasattr(self, 'multiple_elements'):
            return
            
        # Get current color
        current_color = self.color_preview.get_color()
        
        # Open color dialog
        color = QColorDialog.getColor(current_color, self, "Select Color")
        
        # If user canceled, color.isValid() will be False
        if color.isValid():
            # Update color preview
            self._update_color_preview(color)
            
            # Emit property changed signal
            self.property_changed.emit("color", color)
            
    def _update_color_preview(self, color):
        """Update the color preview widget."""
        self.color_preview.set_color(color)
    
    def _block_signals(self, block):
        """
        Block or unblock signals for all interactive widgets.
        
        Args:
            block: True to block signals, False to unblock
        """
        widgets = [
            self.thickness_spinbox,
            self.line_style_combo,
            self.x_spinbox,
            self.y_spinbox,
            self.width_spinbox,
            self.height_spinbox,
            self.text_edit,
            self.font_size_spinbox,
            self.color_button
        ]
        
        for widget in widgets:
            widget.blockSignals(block)
    
    def set_no_selection(self):
        """Set the panel state when no elements are selected."""
        self.setEnabled(False)
        self.title_label.setText("No Selection")
        self._block_signals(True)
        
        # Clear element-specific fields
        self.x_spinbox.setValue(0)
        self.y_spinbox.setValue(0)
        self.width_spinbox.setValue(100)
        self.height_spinbox.setValue(100)
        self.thickness_spinbox.setValue(1)
        self.line_style_combo.setCurrentIndex(0)
        self._update_color_preview(QColor(0, 0, 0))
        
        # Hide text properties
        self.text_group.setVisible(False)
        
        # Clear element reference
        self.current_element = None
        self.current_element_type = None
        
        # Clear multiple elements flag
        if hasattr(self, 'multiple_elements'):
            del self.multiple_elements
            
        self._block_signals(False)
    
    def update_from_element(self, element):
        """
        Update the property panel to reflect the properties of the given element.
        
        Args:
            element: The element to display properties for
        """
        if not element:
            # If no element is provided, disable the panel
            if hasattr(self, 'multiple_elements') and self.multiple_elements:
                return  # Keep showing the multi-selection panel
            else:
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
        
        # Get all properties from the element
        properties = element.get_properties()
        
        # Update color and line thickness if available
        if "color" in properties:
            self._update_color_preview(properties["color"])
        
        if "line_thickness" in properties:
            self.thickness_spinbox.setValue(int(properties["line_thickness"]))
            
        # Update line style if available
        if "line_style" in properties:
            style = properties["line_style"]
            index = self.line_style_combo.findText(style)
            if index >= 0:
                self.line_style_combo.setCurrentIndex(index)
        
        # Update position properties - use visual position
        visual_x, visual_y = element.get_visual_position()
        self.x_spinbox.setValue(visual_x)
        self.y_spinbox.setValue(visual_y)
        
        # Update width and height if supported
        if element.supports_property("width"):
            self.width_spinbox.setValue(element.get_property_value("width"))
            self.width_spinbox.setEnabled(True)
        else:
            self.width_spinbox.setEnabled(False)
            
        if element.supports_property("height"):
            self.height_spinbox.setValue(element.get_property_value("height"))
            self.height_spinbox.setEnabled(True)
        else:
            self.height_spinbox.setEnabled(False)
        
        # Handle text-specific properties
        if element.supports_property("text"):
            self.text_group.setVisible(True)
            self.text_edit.setText(element.get_property_value("text"))
            
            if element.supports_property("font_size"):
                self.font_size_spinbox.setValue(element.get_property_value("font_size"))
                self.font_size_spinbox.setEnabled(True)
            else:
                self.font_size_spinbox.setEnabled(False)
        else:
            self.text_group.setVisible(False)
            
        # Restore signal handling
        self._block_signals(False)
        logger.debug(f"Updated property panel for {element_type}")
    
    def _highlight_current_element_in_list(self):
        """Highlight the current element in the list if it exists."""
        # Reset selection
        self.elements_list.clearSelection()
        
        # Find the element in our list and select it
        for row, element in self.element_items.items():
            if element == self.current_element:
                item = self.elements_list.item(row)
                if item:
                    item.setSelected(True)
                    self.elements_list.scrollToItem(item)
                break
    
    def set_elements_list(self, elements):
        """
        Set the list of available elements.
        
        Args:
            elements: List of elements to display
        """
        # Clear existing items
        self.elements_list.clear()
        self.element_items.clear()
        
        # Add elements to the list
        for i, element in enumerate(elements):
            element_type = type(element).__name__
            element_text = f"{element_type} {i+1}"
            
            item = QListWidgetItem(element_text)
            self.elements_list.addItem(item)
            
            # Store reference to the element by index
            self.element_items[i] = element
        
        # Highlight current element if it's in the list
        self._highlight_current_element_in_list()
        
        # Update the property panel with the first element
        if elements and len(elements) > 0:
            self.update_from_element(elements[0])
    
    def resizeEvent(self, event):
        """Handle resize events for the property panel."""
        super().resizeEvent(event)
        
        # Get current width
        width = event.size().width()
        
        # Adjust layout based on available width
        if width < 200:
            # For very narrow panels, use compact layout
            for i in range(self.appearance_layout.rowCount()):
                label_item = self.appearance_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
                if label_item and label_item.widget():
                    label_item.widget().setWordWrap(True)
            
            # Set labels above fields for all form layouts
            self.appearance_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
            if hasattr(self, 'geometry_layout'):
                self.geometry_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
            if hasattr(self, 'text_layout'):
                self.text_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        else:
            # For wider panels, use standard side-by-side layout
            for i in range(self.appearance_layout.rowCount()):
                label_item = self.appearance_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
                if label_item and label_item.widget():
                    label_item.widget().setWordWrap(False)
            
            # Set labels beside fields for all form layouts
            self.appearance_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
            if hasattr(self, 'geometry_layout'):
                self.geometry_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
            if hasattr(self, 'text_layout'):
                self.text_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)

    def update_from_multiple_elements(self, elements):
        """
        Update the property panel for multiple selected elements.
        Shows only common properties that can be edited for all elements.
        
        Args:
            elements: List of selected elements
        """
        if not elements:
            self.set_no_selection()
            return
            
        # Set multi-selection flag
        self.multiple_elements = True
        
        # Clear current element reference
        self.current_element = None
        self.current_element_type = "Multiple"
        
        # Enable the panel and update the title
        self.setEnabled(True)
        self.title_label.setText(f"Multiple Elements ({len(elements)})")
        
        # Temporarily block signals
        self._block_signals(True)
        
        # Find common properties
        common_properties = self._get_common_properties(elements)
        
        # Update appearance properties if common
        if "color" in common_properties:
            # Use the color of the first element
            self._update_color_preview(elements[0].get_property_value("color"))
            self.color_button.setEnabled(True)
        else:
            # Disable color button if not common
            self.color_button.setEnabled(False)
            
        if "line_thickness" in common_properties:
            # Use the thickness of the first element
            self.thickness_spinbox.setValue(int(elements[0].get_property_value("line_thickness")))
            self.thickness_spinbox.setEnabled(True)
        else:
            self.thickness_spinbox.setEnabled(False)
            
        if "line_style" in common_properties:
            # Use the style of the first element
            style = elements[0].get_property_value("line_style")
            index = self.line_style_combo.findText(style)
            if index >= 0:
                self.line_style_combo.setCurrentIndex(index)
            self.line_style_combo.setEnabled(True)
        else:
            self.line_style_combo.setEnabled(False)
            
        # Disable geometry properties for multi-selection
        self.x_spinbox.setEnabled(False)
        self.y_spinbox.setEnabled(False)
        self.width_spinbox.setEnabled(False)
        self.height_spinbox.setEnabled(False)
        
        # Hide text properties for multi-selection
        self.text_group.setVisible(False)
        
        # Hide radius property for multi-selection
        if hasattr(self, 'radius_spinbox'):
            self.radius_label.setVisible(False)
            self.radius_spinbox.setVisible(False)
            
        # Restore signal handling
        self._block_signals(False)
        
    def _get_common_properties(self, elements):
        """
        Get properties that are common to all elements in the list.
        
        Args:
            elements: List of elements to check
            
        Returns:
            Set of property names common to all elements
        """
        if not elements:
            return set()
            
        # Start with all properties of the first element
        first_element = elements[0]
        common_properties = set(first_element.get_properties().keys())
        
        # Intersect with properties of all other elements
        for element in elements[1:]:
            element_properties = set(element.get_properties().keys())
            common_properties = common_properties.intersection(element_properties)
            
        return common_properties

    def _on_spinbox_value_changed(self, property_name, value, spinbox):
        """
        Handle spinbox value changes, only emitting signals when the value actually changes.
        This prevents feedback loops when updating the UI.
        """
        if not self.current_element:
            return
            
        # Get the current value from the element
        current_value = self.current_element.get_property_value(property_name)
        
        # Only emit if the value has actually changed
        # Use a small epsilon for float comparison
        if abs(current_value - value) > 0.0001:
            self.property_changed.emit(property_name, value)
