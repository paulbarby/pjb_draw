"""
Main application class for the Drawing Package.
"""
import sys
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QFileDialog, QMessageBox, QHBoxLayout, QToolBar,
    QPushButton, QLabel, QSizePolicy, QMenu, QToolButton,
    QStatusBar, QDockWidget, QInputDialog, QSplitter
)
from PyQt6.QtCore import Qt, QMimeData, QSize, QSettings, QRectF, QTimer, QPoint
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QAction, QIcon, QColor, QPixmap

from src.ui.canvas import Canvas
from src.ui.property_panel import PropertyPanel
from src.utils.image_handler import ImageHandler
from src.utils.tool_manager import ToolType, ToolManager
from src.utils.history_manager import HistoryManager, HistoryAction, ActionType
from src.utils.project_manager import ProjectManager
from src.utils.export_manager import ExportManager, ExportFormat
from src.utils.element_factory import ElementFactory
from src.utils.theme_manager import ThemeManager
from src.ui.menus.menu_factory import MenuFactory

# Configure logging
# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Set up handlers
log_file_path = os.path.join(logs_dir, "drawing_app.log")
file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=1024 * 1024 * 5,  # 5MB max file size
    backupCount=5,  # Keep 5 backup files
    encoding='utf-8'
)
console_handler = logging.StreamHandler()

# Configure format for both handlers
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Set different log levels for handlers
file_handler.setLevel(logging.INFO)  # Detailed logging to file
console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger(__name__)
logger.info(f"Logging to file: {log_file_path}")

class DrawingApp(QMainWindow):
    """Main application window for the Drawing Package."""
    
    def __init__(self):
        """Initialize the application window."""
        super().__init__()
        
        self.setWindowTitle("Drawing Package")
        self.setMinimumSize(800, 600)
        
        # Initialize settings
        self.settings = QSettings("DrawingPackage", "DrawingApp")
        
        # Initialize theme manager early
        self.theme_manager = ThemeManager(self)
        
        # Set up the main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Initialize utility managers first
        self.history_manager = HistoryManager()
        self.project_manager = ProjectManager()
        self.export_manager = ExportManager()
        self.element_factory = ElementFactory()
        
        # Create image handler
        self.image_handler = ImageHandler()
        
        # Create tool manager
        self.tool_manager = ToolManager()
        
        # Create and add the canvas
        self.canvas = Canvas(parent=self, history_manager=self.history_manager)
        self.canvas.tool_manager = self.tool_manager
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.canvas)
        
        # Connect canvas signals
        self.canvas.status_message.connect(self._update_status)
        self.canvas.element_created.connect(self._on_element_created)
        self.canvas.element_selected.connect(self._on_element_selected)
        self.canvas.element_changed.connect(self._on_element_changed)
        
        # Initialize menu factory and create menu bar
        self.menu_factory = MenuFactory(self)
        self.setMenuBar(self.menu_factory.create_menu_bar())
        
        # Create property panel in a dock widget
        self.property_panel = PropertyPanel()
        self.property_panel.property_changed.connect(self._on_property_changed)
        self.property_panel.element_selected_from_list.connect(self._on_element_selected_from_list)
        
        # Create dock widget for property panel
        self.property_dock = QDockWidget("Properties", self)
        self.property_dock.setObjectName("PropertiesDockWidget")  # Add object name for state saving
        self.property_dock.setWidget(self.property_panel)
        self.property_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.property_dock.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea | 
            Qt.DockWidgetArea.LeftDockWidgetArea
        )
        
        # Add the dock widget to the right side
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.property_dock)
        
        # Set up status bar
        self.status_bar = self.statusBar()
        
        # Create toolbar
        self.create_tools_toolbar()
        
        # Set initial status message AFTER creating tools
        # This ensures it won't be overwritten by tool selection
        self.status_bar.showMessage("Ready")
        
        # Enable drag-and-drop
        self.setAcceptDrops(True)
        
        # Connect history manager to update UI
        self.history_manager.register_action_listener(self._update_history_actions)
        
        # Initialize the elements list in the property panel
        self._refresh_elements_list()
        
        # Apply theme using theme manager
        self.theme_manager.apply_theme()
        
        # Restore window state and geometry if available
        if self.settings.contains("window_geometry"):
            self.restoreGeometry(self.settings.value("window_geometry"))
        if self.settings.contains("window_state"):
            self.restoreState(self.settings.value("window_state"))
        
        # Set default autosave interval if not set
        if not self.settings.contains("autosave_interval"):
            self.settings.setValue("autosave_interval", 300)  # 5 minutes default
        
        logger.info("Application initialized")
    
    def create_tools_toolbar(self):
        """Create the tools toolbar."""
        # Main toolbar
        self.toolbar = QToolBar("Drawing Tools")
        self.toolbar.setObjectName("DrawingToolsToolBar")  # Add object name for state saving
        self.toolbar.setMovable(True)  # Allow toolbar to be moved
        self.toolbar.setFloatable(True)  # Allow toolbar to be detached as floating window
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        
        # Drawing tools group
        self.toolbar.addWidget(self.create_label("Drawing:"))
        
        # Add SELECT tool first
        select_action = self.create_tool_action("Select", ToolType.SELECT, "Select and edit elements (S)")
        select_action.setShortcut("S")
        select_action.setChecked(True)  # Select tool is checked by default
        
        # Add other drawing tools
        line_action = self.create_tool_action("Line", ToolType.LINE, "Draw lines (L)")
        line_action.setShortcut("L")
        rect_action = self.create_tool_action("Rectangle", ToolType.RECTANGLE, "Draw rectangles (R)")
        rect_action.setShortcut("R")
        circle_action = self.create_tool_action("Circle", ToolType.CIRCLE, "Draw circles (C)")
        circle_action.setShortcut("C")
        text_action = self.create_tool_action("Text", ToolType.TEXT, "Add text annotations (T)")
        text_action.setShortcut("T")
        
        # Initialize tool state
        self.select_tool(ToolType.SELECT)
        
        # File operations group
        self.toolbar.addSeparator()
        
        self.toolbar.addWidget(self.create_label("File:"))
        self.action_open = QAction(QIcon("icons/open.png"), "Open", self)
        self.action_open.setToolTip("Open an image (Ctrl+O)")
        self.action_open.setShortcut("Ctrl+O")
        self.action_open.triggered.connect(self.open_project)
        self.toolbar.addAction(self.action_open)
        
        self.action_save = QAction(QIcon("icons/save.png"), "Save", self)
        self.action_save.setToolTip("Save project (Ctrl+S)")
        self.action_save.setShortcut("Ctrl+S")
        self.action_save.triggered.connect(self.save_project)
        self.toolbar.addAction(self.action_save)
        
        self.action_export = QAction(QIcon("icons/export.png"), "Export", self)
        self.action_export.setToolTip("Export as image (Ctrl+E)")
        self.action_export.setShortcut("Ctrl+E") 
        self.action_export.triggered.connect(self.export_image)
        self.toolbar.addAction(self.action_export)
        
        self.toolbar.addSeparator()
        
        # Canvas operations
        self.toolbar.addWidget(self.create_label("Canvas:"))
        self.action_clear = QAction(QIcon("icons/clear.png"), "Clear Canvas", self)
        self.action_clear.setToolTip("Clear all drawings (Ctrl+Delete)")
        self.action_clear.setShortcut("Ctrl+Delete")
        self.action_clear.triggered.connect(self.clear_canvas)
        self.toolbar.addAction(self.action_clear)
        
        self.action_zoom_in = QAction(QIcon("icons/zoom_in.png"), "Zoom In", self)
        self.action_zoom_in.setToolTip("Zoom in (Ctrl++)")
        self.action_zoom_in.setShortcut("Ctrl++")
        self.action_zoom_in.triggered.connect(self.zoom_in)
        self.toolbar.addAction(self.action_zoom_in)
        
        self.action_zoom_out = QAction(QIcon("icons/zoom_out.png"), "Zoom Out", self)
        self.action_zoom_out.setToolTip("Zoom out (Ctrl+-)")
        self.action_zoom_out.setShortcut("Ctrl+-")
        self.action_zoom_out.triggered.connect(self.zoom_out)
        self.toolbar.addAction(self.action_zoom_out)
        
        self.toolbar.addSeparator()
        
        # Edit operations
        self.toolbar.addWidget(self.create_label("Edit:"))
        self.action_undo = QAction(QIcon("icons/undo.png"), "Undo", self)
        self.action_undo.setToolTip("Undo last action (Ctrl+Z)")
        self.action_undo.setShortcut("Ctrl+Z")
        self.action_undo.triggered.connect(self.undo_action)
        self.toolbar.addAction(self.action_undo)
        
        self.action_redo = QAction(QIcon("icons/redo.png"), "Redo", self)
        self.action_redo.setToolTip("Redo last undone action (Ctrl+Y)")
        self.action_redo.setShortcut("Ctrl+Y")
        self.action_redo.triggered.connect(self.redo_action)
        self.toolbar.addAction(self.action_redo)

    def create_label(self, text):
        """Create a label for the toolbar."""
        label = QLabel(text)
        label.setStyleSheet("margin-left: 10px; font-weight: bold;")
        return label

    def create_tool_action(self, name, tool_type, tooltip=None):
        """Create a tool action for the toolbar."""
        # Convert string to ToolType enum
        if isinstance(tool_type, str):
            tool_type = ToolType(tool_type)
            
        action = QAction(QIcon(f"icons/{tool_type.value}.png"), name, self)
        if tooltip:
            action.setToolTip(tooltip)
        action.setCheckable(True)
        action.setData(tool_type)
        action.triggered.connect(lambda checked, t=tool_type: self.select_tool(t))
        self.toolbar.addAction(action)
        return action

    def select_tool(self, tool_type):
        """
        Select a drawing tool.
        
        Args:
            tool_type: The tool type to select (string or ToolType)
        """
        # Convert string to ToolType enum if needed
        if isinstance(tool_type, str):
            try:
                # Convert string to enum value (e.g., "line" to ToolType.LINE)
                tool_type = ToolType(tool_type)
            except ValueError:
                # If conversion fails, log an error and default to SELECT
                logger.error(f"Invalid tool type: {tool_type}, defaulting to SELECT")
                tool_type = ToolType.SELECT
        
        # Uncheck all tool actions and check only the selected one
        for action in self.toolbar.actions():
            if action.isCheckable():
                # Get the action's tool type
                action_tool_type = action.data()
                if action_tool_type:
                    # Convert to ToolType enum if it's a string
                    if isinstance(action_tool_type, str):
                        try:
                            action_tool_type = ToolType(action_tool_type)
                        except ValueError:
                            continue
                    
                    # Set checked state based on whether this is the selected tool
                    action.setChecked(action_tool_type == tool_type)
                
        # Update the current tool in tool manager and canvas
        self.tool_manager.set_tool(tool_type)
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.set_tool(tool_type)
        self.status_bar.showMessage(f"Selected {tool_type.value} tool")
    
    def _on_element_selected(self, element):
        """Handle element selection."""
        # If element is None, it could be either no selection or multi-selection
        if element is None:
            # Check if there are multiple elements selected
            selected_elements = self.canvas.selection_manager.current_selection
            count = len(selected_elements)
            
            if count == 0:
                logger.info("No elements selected")
                self.status_bar.showMessage("No selection")
                self.property_panel.update_from_element(None)
            else:
                logger.info(f"Multiple elements selected: {count}")
                self.status_bar.showMessage(f"Selected {count} elements")
                # Update property panel with multiple elements
                self.property_panel.update_from_multiple_elements(selected_elements)
        else:
            logger.info(f"Element selected: {element}")
            self.status_bar.showMessage(f"Selected {type(element).__name__}")
            # Update property panel with single element
            self.property_panel.update_from_element(element)
        
    def _on_element_created(self, element):
        """Handle element creation."""
        logger.info(f"Element created: {element}")
        self.status_bar.showMessage(f"Created {type(element).__name__}")
        
        # Update property panel with the newly created element
        self.property_panel.update_from_element(element)
        
        # Refresh elements list
        self._refresh_elements_list()
        
        # Update project data for autosave
        self._update_project_data_for_autosave()
        
    def _on_element_changed(self, element):
        """Handle element modification."""
        logger.info(f"Element modified: {element}")
        self.status_bar.showMessage(f"Modified {type(element).__name__}")
        
        # Update property panel if the modified element is selected
        if self.property_panel.current_element == element:
            self.property_panel.update_from_element(element)
            
        # Refresh elements list to update any displayed properties
        self._refresh_elements_list()
        
        # Update project data for autosave
        self._update_project_data_for_autosave()
    
    def _on_property_changed(self, property_name, value, element=None):
        """Handle property changes from the property panel."""
        # If no element is provided, use the current element
        if element is None:
            element = self.property_panel.current_element
            
        if not element:
            logger.warning("No element selected for property change")
            return
            
        # Check if the element supports this property
        if not element.supports_property(property_name):
            logger.warning(f"Element {type(element).__name__} does not support property {property_name}")
            return
            
        # Begin a property change action group
        self.history_manager.begin_action_group(f"Change {property_name}")
        
        # try:
        # Store old property value for undo
        old_value = element.get_property_value(property_name)
        
        # Create undo/redo functions
        def undo_property_change():
            try:
                element.set_property_value(property_name, old_value)
                self.canvas.update()
                # For position changes, notify the scene that item has moved
                if property_name in ["x", "y", "visual_x", "visual_y", "global_x", "global_y", "local_x", "local_y"]:
                    element.update()
                    element.prepareGeometryChange()
                    # Update handles if available
                    if hasattr(element, "update_handles"):
                        element.update_handles()
            except Exception as e:
                logger.error(f"Error undoing property change: {str(e)}")
        
        def redo_property_change():
            try:
                element.set_property_value(property_name, value)
                self.canvas.update()
                # For position changes, notify the scene that item has moved
                if property_name in ["x", "y", "visual_x", "visual_y", "global_x", "global_y", "local_x", "local_y"]:
                    element.update()
                    element.prepareGeometryChange()
                    # Update handles if available
                    if hasattr(element, "update_handles"):
                        element.update_handles()
            except Exception as e:
                logger.error(f"Error redoing property change: {str(e)}")
        
        # Create history action
        action = HistoryAction(
            ActionType.CHANGE_PROPERTY,
            undo_property_change,
            redo_property_change,
            f"Change {property_name} to {value}",
            {
                "property": property_name,
                "old_value": str(old_value),
                "new_value": str(value),
                "element_type": type(element).__name__
            }
        )
        
        # Add to history
        self.history_manager.add_action(action)
        
        # Apply the change
        # try:
        element.set_property_value(property_name, value)
        # except Exception as e:
        #    logger.error(f"Error setting property '{property_name}' to '{value}': {str(e)}")
        #     raise
        
        # End the action group
        self.history_manager.end_action_group()
        
        # Update the canvas
        self.canvas.viewport().update()
        
        # For position changes, ensure the scene is properly notified
        if property_name in ["x", "y", "visual_x", "visual_y", "global_x", "global_y", "local_x", "local_y"]:
            element.update()
            element.prepareGeometryChange()
            # Update handles if available
            if hasattr(element, "update_handles"):
                element.update_handles()
        
        # Emit changed signal for canvas
        self.canvas.element_changed.emit(element)
        
        # Log the change
        logger.info(f"Changing property '{property_name}' to '{value}' for {type(element).__name__}")
            
        #except Exception as e:
        # Log the error
        #    logger.error(f"Error setting property '{property_name}' to '{value}': {str(e)}")
        #    QMessageBox.warning(self, "Error", f"Could not set property: {str(e)}")
            
            # End the action group (will be empty if the change failed)
        #    self.history_manager.end_action_group()
    
    def _apply_property_to_multiple(self, elements, property_name, value):
        """
        Apply a property change to multiple elements.
        
        Args:
            elements: List of elements to modify
            property_name: Name of the property to change
            value: New value for the property
        """
        if not elements:
            return
            
        # Begin a property change action group
        self.history_manager.begin_action_group(f"Change {property_name} for multiple elements")
        
        # Store old values for undo
        old_values = {}
        for element in elements:
            if element.supports_property(property_name):
                old_values[element] = element.get_property_value(property_name)
        
        # Create undo function
        def undo_multi_property_change():
            try:
                for element, old_value in old_values.items():
                    element.set_property_value(property_name, old_value)
                    # For position changes, notify the scene that item has moved
                    if property_name in ["x", "y", "visual_x", "visual_y", "global_x", "global_y", "local_x", "local_y"]:
                        element.update()
                        element.prepareGeometryChange()
                        # Update handles if available
                        if hasattr(element, "update_handles"):
                            element.update_handles()
                self.canvas.update()
            except Exception as e:
                logger.error(f"Error undoing multi-property change: {str(e)}")
        
        def redo_multi_property_change():
            try:
                for element in old_values.keys():
                    element.set_property_value(property_name, value)
                    # For position changes, notify the scene that item has moved
                    if property_name in ["x", "y", "visual_x", "visual_y", "global_x", "global_y", "local_x", "local_y"]:
                        element.update()
                        element.prepareGeometryChange()
                        # Update handles if available
                        if hasattr(element, "update_handles"):
                            element.update_handles()
                self.canvas.update()
            except Exception as e:
                logger.error(f"Error redoing multi-property change: {str(e)}")
        
        # Create history action
        action = HistoryAction(
            ActionType.CHANGE_PROPERTY,
            undo_multi_property_change,
            redo_multi_property_change,
            f"Change {property_name} to {value} for {len(old_values)} elements",
            {
                "property": property_name,
                "new_value": str(value),
                "element_count": len(old_values)
            }
        )
        
        # Add to history
        self.history_manager.add_action(action)
        
        # Apply the changes
        for element in old_values.keys():
            element.set_property_value(property_name, value)
            # For position changes, ensure the scene is properly notified
            if property_name in ["x", "y", "visual_x", "visual_y", "global_x", "global_y", "local_x", "local_y"]:
                element.update()
                element.prepareGeometryChange()
                # Update handles if available
                if hasattr(element, "update_handles"):
                    element.update_handles()
        
        # End the action group
        self.history_manager.end_action_group()
        
        # Update the canvas
        self.canvas.viewport().update()
        
        # Log the change
        logger.info(f"Changed property '{property_name}' to '{value}' for {len(old_values)} elements")
    
    def _create_tool_action(self, name, tool_id):
        """Create a tool action for the toolbar."""
        action = QAction(name, self)
        action.setCheckable(True)
        action.setToolTip(f"{name} tool")
        action.setData(tool_id)
        action.triggered.connect(self._on_tool_selected)
        self.toolbar.addAction(action)
        return action
    
    def _on_tool_selected(self):
        """Handle tool selection."""
        sender = self.sender()
        if sender.isChecked():
            # Uncheck other tool actions
            for action in self.toolbar.actions():
                if action.isCheckable() and action != sender:
                    action.setChecked(False)
            
            # Set the active tool
            tool_id = sender.data()
            self.canvas.set_tool(tool_id)
    
    @property
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return bool(self.history_manager.can_undo())

    @property
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return bool(self.history_manager.can_redo())

    def closeEvent(self, event):
        """Handle application close event."""
        # Disable autosave
        self.project_manager.enable_autosave(False)
        
        # Ask user to save if there are unsaved changes
        if self.canvas.is_dirty():
            reply = QMessageBox.question(
                self, 
                'Close Drawing Package',
                'You have unsaved changes. Would you like to save before closing?',
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_project()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            
        # Save window state and geometry
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())
        
        # Save theme preference
        self.settings.setValue("dark_theme", self.theme_manager.is_dark_theme)
        
        # Save other settings
        self.settings.sync()
        
        # Accept the close event
        event.accept()
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events for drag-and-drop."""
        # Check if the drag contains image data or urls
        if event.mimeData().hasUrls():
            # Check if at least one URL is a supported image file
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if self.image_handler.is_supported_format(file_path):
                    event.acceptProposedAction()
                    self.status_bar.showMessage(f"Drop to load image: {file_path}")
                    return
                    
        event.ignore()
        
    def dropEvent(self, event: QDropEvent):
        """Handle drop events for drag-and-drop."""
        if event.mimeData().hasUrls():
            # Get the first supported image URL
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if self.image_handler.is_supported_format(file_path):
                    self._load_image(file_path)
                    event.acceptProposedAction()
                    return
                    
        event.ignore()
        
    def _load_image(self, file_path: str):
        """Load an image from file."""
        try:
            # Use the image handler to load the image
            if self.image_handler.load_image(file_path):
                pixmap = self.image_handler.get_pixmap()
                
                # Set the image as the canvas background
                self.canvas.set_background(pixmap, file_path)
                
                # Add to recent files
                self.add_to_recent_files(file_path)
                
                # Create a special history action for setting background
                self.history_manager.add_action(
                    HistoryAction(
                        action_type=ActionType.SET_BACKGROUND,
                        description=f"Set background to {os.path.basename(file_path)}",
                        data={
                            "pixmap": pixmap,
                            "file_path": file_path
                        },
                        undo_function=self._create_undo_set_background(),
                        redo_function=self._create_redo_set_background(pixmap, file_path)
                    )
                )
                
                self._update_status(f"Loaded image: {file_path}")
                return True
            else:
                QMessageBox.warning(self, "Error", f"Could not load image: {file_path}")
                return False
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            return False

    def open_project(self):
        """Open a project file."""
        file_filter = f"Drawing Package Files (*{self.project_manager.FILE_EXTENSION})"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            file_filter
        )
        
        if file_path:
            # Check for autosave
            autosave_path = self.project_manager.check_for_autosave(file_path)
            if autosave_path:
                # Ask user if they want to recover from autosave
                recover = QMessageBox.question(
                    self,
                    "Recover Project",
                    f"An autosave file for this project exists. Would you like to recover from the autosave?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if recover == QMessageBox.StandardButton.Yes:
                    # Load from autosave
                    self._load_from_file(autosave_path)
                    self._update_status(f"Project recovered from autosave: {autosave_path}")
                    return
            
            # Load normal file
            self._load_from_file(file_path)
    
    def _load_from_file(self, file_path: str):
        """Load a project from file."""
        try:
            # Load the project file
            project_data = self.project_manager.load(file_path)
            if not project_data:
                QMessageBox.warning(self, "Error", f"Could not load project from {file_path}")
                return False
            
            # Get elements data
            elements_data = project_data.get("elements", [])
            
            # Clear canvas
            self.canvas.clear_all()
            
            # Clear history
            self.history_manager.clear()
            
            # Begin a complex operation for loading all elements
            self.history_manager.begin_action_group("Load project")
            
            # Load elements
            for element_data in elements_data:
                try:
                    # Create the element
                    element_type = element_data.get("type")
                    element = self.element_factory.create_element(element_type, element_data)
                    
                    # Add to canvas
                    self.canvas.add_element(element)
                except Exception as e:
                    logger.error(f"Error deserializing element: {str(e)}")
            
            # Set background if available
            background_data = project_data.get("background")
            if background_data and "file_path" in background_data:
                file_path = background_data["file_path"]
                if os.path.exists(file_path):
                    pixmap = self.image_handler.load_image(file_path)
                    if pixmap:
                        self.canvas.set_background(pixmap, file_path)
            
            # End the complex operation
            self.history_manager.end_action_group()
            
            # Add to recent files
            self.add_to_recent_files(file_path)
            
            # Enable autosave
            self._enable_autosave()
            
            self._update_status(f"Project loaded from {file_path}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            logger.error(f"Error loading project: {str(e)}")
            return False
    
    def clear_canvas(self):
        """Clear all elements from the canvas."""
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.clear_canvas()
        self.status_bar.showMessage("Canvas cleared")
        
        # Update property panel to show no selection
        self.property_panel.set_no_selection()
        
        # Refresh elements list
        self._refresh_elements_list()

    def save_project(self):
        """Save the current project."""
        if not self.project_manager.get_current_file_path():
            self.save_project_as()
            return
            
        file_path = self.project_manager.get_current_file_path()
        self._save_to_file(file_path)
    
    def save_project_as(self):
        """Save the current project with a new filename."""
        file_filter = f"Drawing Package Files (*{self.project_manager.FILE_EXTENSION})"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project",
            "",
            file_filter
        )
        
        if file_path:
            # Ensure the file has the correct extension
            if not file_path.endswith(self.project_manager.FILE_EXTENSION):
                file_path += self.project_manager.FILE_EXTENSION
                
            self._save_to_file(file_path)
    
    def _save_to_file(self, file_path: str):
        """Save the project to file."""
        try:
            # Get all elements from canvas
            elements = self.canvas.get_all_elements()
            
            # Serialize elements
            elements_data = []
            for element in elements:
                try:
                    element_data = element.to_dict()
                    elements_data.append(element_data)
                except Exception as e:
                    logger.error(f"Error serializing element: {str(e)}")
            
            # Get background data if exists
            background_data = None
            if self.canvas.has_background():
                background_data = {
                    "file_path": self.canvas.background_path
                }
            
            # Get history data
            history_data = self.history_manager.serialize_history() if self.history_manager else None
            
            # Create project data
            project_data = {
                "elements": elements_data,
                "background": background_data,
                "history": history_data
            }
            
            # Save to file
            if self.project_manager.save(file_path, project_data):
                # Add to recent files
                self.add_to_recent_files(file_path)
                
                # Enable autosave
                self._enable_autosave()
                
                # Update project data in project manager
                self.project_manager.update_project_data(project_data)
                
                self._update_status(f"Project saved to {file_path}")
                return True
            else:
                QMessageBox.warning(self, "Error", f"Could not save project to {file_path}")
                return False
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            logger.error(f"Error saving project: {str(e)}")
            return False
    
    def export_image(self, export_format=None):
        """
        Export the canvas as an image.
        
        Args:
            export_format: Optional export format (PNG, JPG, PDF, SVG)
        """
        if export_format is None:
            export_format = ExportFormat.PNG
            
        # Default file extension and filter based on format
        if export_format == ExportFormat.PNG:
            default_ext = "png"
            file_filter = "PNG Image (*.png)"
        elif export_format == ExportFormat.JPG:
            default_ext = "jpg"
            file_filter = "JPEG Image (*.jpg *.jpeg)"
        elif export_format == ExportFormat.PDF:
            default_ext = "pdf"
            file_filter = "PDF Document (*.pdf)"
        elif export_format == ExportFormat.SVG:
            default_ext = "svg"
            file_filter = "SVG Image (*.svg)"
        else:
            # Default to PNG
            default_ext = "png"
            file_filter = "PNG Image (*.png)"
            export_format = ExportFormat.PNG
            
        # Get the save path from the user
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Image",
            os.path.expanduser(f"~/untitled.{default_ext}"),
            file_filter
        )
        
        if not file_path:
            return  # User cancelled
            
        # Export the image
        try:
            if self.export_manager.export(self.canvas, file_path, export_format):
                self._update_status(f"Image exported to {file_path}")
            else:
                QMessageBox.warning(
                    self,
                    "Export Error",
                    f"Failed to export image to {file_path}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred during export: {str(e)}"
            )
    
    def zoom_in(self):
        """Zoom in on the canvas."""
        self.canvas.zoom_in()
        self.status_bar.showMessage(f"Zoom level: {self.canvas.get_zoom_level():.0%}")

    def zoom_out(self):
        """Zoom out on the canvas."""
        self.canvas.zoom_out()
        self.status_bar.showMessage(f"Zoom level: {self.canvas.get_zoom_level():.0%}")

    def reset_zoom(self):
        """Reset zoom to 100%."""
        self.canvas.reset_zoom()
        self.status_bar.showMessage("Zoom level: 100%")

    def clear_background(self):
        """Clear the canvas background."""
        self.canvas.clear_background()
        self.status_bar.showMessage("Background cleared")

    def toggle_properties_panel(self):
        """Toggle the visibility of the properties panel."""
        if self.property_dock.isVisible():
            self.property_dock.hide()
            self.status_bar.showMessage("Properties panel hidden")
        else:
            self.property_dock.show()
            self.status_bar.showMessage("Properties panel shown")

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.theme_manager.toggle_theme()
        theme = "dark" if self.theme_manager.is_dark_theme else "light"
        self.status_bar.showMessage(f"Switched to {theme} mode")

    def apply_theme(self):
        """Apply the current theme to the application."""
        self.theme_manager.apply_theme()

    def set_line_color(self):
        """Set the line color of the selected elements."""
        selected_elements = self.canvas.selection_manager.get_selected_elements()
        if not selected_elements:
            return
        
        # TODO: Show color picker dialog
        self.status_bar.showMessage("Line color picker not implemented yet")

    def set_fill_color(self):
        """Set the fill color of the selected elements."""
        selected_elements = self.canvas.selection_manager.get_selected_elements()
        if not selected_elements:
            return
        
        # TODO: Show color picker dialog
        self.status_bar.showMessage("Fill color picker not implemented yet")

    def set_line_thickness(self, thickness):
        """Set the line thickness of the selected elements.
        
        Args:
            thickness (int): The new line thickness in pixels
        """
        selected_elements = self.canvas.selection_manager.get_selected_elements()
        if not selected_elements:
            return
        
        # Record the action for undo/redo
        old_thicknesses = {element: element.line_thickness for element in selected_elements}
        
        def undo_thickness_change():
            for element, old_thickness in old_thicknesses.items():
                element.line_thickness = old_thickness
            self.canvas.viewport().update()
        
        def redo_thickness_change():
            for element in selected_elements:
                element.line_thickness = thickness
            self.canvas.viewport().update()
        
        self.history_manager.add_action(
            HistoryAction(
                f"Set Line Thickness to {thickness}px",
                undo_thickness_change,
                redo_thickness_change,
                ActionType.PROPERTY_CHANGE
            )
        )
        
        # Perform the change
        redo_thickness_change()
        self.status_bar.showMessage(f"Set line thickness to {thickness}px")

    def rotate_selected_elements(self):
        """Rotate the selected elements."""
        selected_elements = self.canvas.selection_manager.get_selected_elements()
        if not selected_elements:
            return
        
        # TODO: Show rotation dialog
        self.status_bar.showMessage("Rotation dialog not implemented yet")

    def scale_selected_elements(self):
        """Scale the selected elements."""
        selected_elements = self.canvas.selection_manager.get_selected_elements()
        if not selected_elements:
            return
        
        # TODO: Show scale dialog
        self.status_bar.showMessage("Scale dialog not implemented yet")

    def flip_horizontal(self):
        """Flip the selected elements horizontally."""
        selected_elements = self.canvas.selection_manager.get_selected_elements()
        if not selected_elements:
            return
        
        # TODO: Implement horizontal flip
        self.status_bar.showMessage("Horizontal flip not implemented yet")

    def flip_vertical(self):
        """Flip the selected elements vertically."""
        selected_elements = self.canvas.selection_manager.get_selected_elements()
        if not selected_elements:
            return
        
        # TODO: Implement vertical flip
        self.status_bar.showMessage("Vertical flip not implemented yet")

    def bring_to_front(self):
        """Bring the selected elements to the front."""
        selected_elements = self.canvas.selection_manager.get_selected_elements()
        if not selected_elements:
            return
        
        # Record the action for undo/redo
        old_z_values = {element: element.zValue() for element in selected_elements}
        max_z = self.canvas.get_max_z_value()
        
        def undo_z_change():
            for element, old_z in old_z_values.items():
                element.setZValue(old_z)
            self.canvas.viewport().update()
        
        def redo_z_change():
            for i, element in enumerate(selected_elements):
                element.setZValue(max_z + 1 + i)
            self.canvas.viewport().update()
        
        self.history_manager.add_action(
            HistoryAction(
                "Bring to Front",
                undo_z_change,
                redo_z_change,
                ActionType.Z_ORDER
            )
        )
        
        # Perform the change
        redo_z_change()
        self.status_bar.showMessage("Brought elements to front")

    def send_to_back(self):
        """Send the selected elements to the back."""
        selected_elements = self.canvas.selection_manager.get_selected_elements()
        if not selected_elements:
            return
        
        # Record the action for undo/redo
        old_z_values = {element: element.zValue() for element in selected_elements}
        min_z = self.canvas.get_min_z_value()
        
        def undo_z_change():
            for element, old_z in old_z_values.items():
                element.setZValue(old_z)
            self.canvas.viewport().update()
        
        def redo_z_change():
            for i, element in enumerate(selected_elements):
                element.setZValue(min_z - 1 - i)
            self.canvas.viewport().update()
        
        self.history_manager.add_action(
            HistoryAction(
                "Send to Back",
                undo_z_change,
                redo_z_change,
                ActionType.Z_ORDER
            )
        )
        
        # Perform the change
        redo_z_change()
        self.status_bar.showMessage("Sent elements to back")

    def bring_forward(self):
        """Bring the selected elements forward by one level."""
        selected_elements = self.canvas.selection_manager.get_selected_elements()
        if not selected_elements:
            return
        
        # Record the action for undo/redo
        old_z_values = {element: element.zValue() for element in selected_elements}
        
        def undo_z_change():
            for element, old_z in old_z_values.items():
                element.setZValue(old_z)
            self.canvas.viewport().update()
        
        def redo_z_change():
            for element in selected_elements:
                element.setZValue(element.zValue() + 1)
            self.canvas.viewport().update()
        
        self.history_manager.add_action(
            HistoryAction(
                "Bring Forward",
                undo_z_change,
                redo_z_change,
                ActionType.Z_ORDER
            )
        )
        
        # Perform the change
        redo_z_change()
        self.status_bar.showMessage("Brought elements forward")

    def send_backward(self):
        """Send the selected elements backward by one level."""
        selected_elements = self.canvas.selection_manager.get_selected_elements()
        if not selected_elements:
            return
        
        # Record the action for undo/redo
        old_z_values = {element: element.zValue() for element in selected_elements}
        
        def undo_z_change():
            for element, old_z in old_z_values.items():
                element.setZValue(old_z)
            self.canvas.viewport().update()
        
        def redo_z_change():
            for element in selected_elements:
                element.setZValue(element.zValue() - 1)
            self.canvas.viewport().update()
        
        self.history_manager.add_action(
            HistoryAction(
                "Send Backward",
                undo_z_change,
                redo_z_change,
                ActionType.Z_ORDER
            )
        )
        
        # Perform the change
        redo_z_change()
        self.status_bar.showMessage("Sent elements backward")

    def show_user_guide(self):
        """Show the user guide."""
        # TODO: Implement user guide dialog
        self.status_bar.showMessage("User guide not implemented yet")

    def show_shortcuts(self):
        """Show the keyboard shortcuts dialog."""
        # TODO: Implement keyboard shortcuts dialog
        self.status_bar.showMessage("Keyboard shortcuts dialog not implemented yet")

    def show_about_dialog(self):
        """Show the about dialog."""
        # TODO: Implement about dialog
        self.status_bar.showMessage("About dialog not implemented yet")

    def undo_action(self):
        """Undo the last action."""
        action = self.history_manager.undo()
        if action:
            self.statusBar().showMessage(f"Undid: {action.description}")
        else:
            self.statusBar().showMessage("Nothing to undo")
    
    def redo_action(self):
        """Redo the last undone action."""
        action = self.history_manager.redo()
        if action:
            self.statusBar().showMessage(f"Redid: {action.description}")
        else:
            self.statusBar().showMessage("Nothing to redo")
            
    def new_project(self):
        """Create a new project."""
        if hasattr(self, 'canvas') and self.canvas:
            # Clear the canvas
            self.canvas.clear_canvas()
            
            # Reset project file path
            self.project_manager.current_file_path = None
            
            # Clear history
            self.history_manager.clear()
            
            self.statusBar().showMessage("New project created")
    
    def _update_history_actions(self, can_undo: bool, can_redo: bool):
        """Update the enabled state of undo/redo actions."""
        # Update menu states through the menu factory
        self.menu_factory.update_menu_states()
    
    def _update_status(self, message):
        """Update the status bar message."""
        self.statusBar().showMessage(message)
    
    def _on_element_selected_from_list(self, element):
        """Handle element selection from the elements list."""
        if element:
            self.canvas.selection_manager.select_elements([element])
            self.canvas.viewport().update()

    def _refresh_elements_list(self):
        """Refresh the elements list in the property panel."""
        if hasattr(self, 'canvas') and self.canvas:
            elements = self.canvas.get_all_elements()
            if hasattr(self, 'property_panel'):
                self.property_panel.set_elements_list(elements)

    def update_recent_files_menu(self):
        """Update the recent files menu with the current list of recent files."""
        self.menu_factory.update_recent_files_menu()

    def add_to_recent_files(self, file_path):
        """Add a file path to the recent files list."""
        recent_files = self.get_recent_files()
        
        # Remove if already exists (to move it to the top)
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to the beginning of the list
        recent_files.insert(0, file_path)
        
        # Keep only the last 10 files
        recent_files = recent_files[:10]
        
        # Save to settings
        self.settings.setValue("recent_files", recent_files)
        
        # Update the menu
        self.update_recent_files_menu()

    def get_recent_files(self) -> List[str]:
        """Get the list of recent files from settings."""
        recent_files = self.settings.value("recent_files", [])
        if recent_files is None:
            recent_files = []
        # Filter out files that no longer exist
        recent_files = [f for f in recent_files if os.path.exists(f)]
        # Update settings with filtered list
        self.settings.setValue("recent_files", recent_files)
        return recent_files

    def open_recent_file(self, file_path):
        """Open a file from the recent files list.
        
        Args:
            file_path (str): Path to the file to open
        """
        if not os.path.exists(file_path):
            # File no longer exists
            QMessageBox.warning(
                self,
                "File Not Found",
                f"The file {file_path} no longer exists."
            )
            self.remove_from_recent_files(file_path)
            return
        
        self._load_from_file(file_path)

    def remove_from_recent_files(self, file_path):
        """Remove a file from the recent files list.
        
        Args:
            file_path (str): Path to the file to remove
        """
        recent_files = self.settings.value("recent_files", [], str)
        if file_path in recent_files:
            recent_files.remove(file_path)
            self.settings.setValue("recent_files", recent_files)
            self.update_recent_files_menu()

    def clear_recent_files(self):
        """Clear the list of recent files."""
        self.settings.setValue("recent_files", [])
        self.update_recent_files_menu()

    def not_implemented(self):
        """Show a message for features that are not yet implemented."""
        QMessageBox.information(
            self,
            "Not Implemented",
            "This feature is not yet implemented."
        )

    def _enable_autosave(self, enabled=True):
        """Enable autosave functionality."""
        # Get autosave interval setting
        interval = self.settings.value("autosave_interval", 300, int)
        
        # Enable autosave in project manager
        self.project_manager.enable_autosave(enabled, interval)
        
        if enabled:
            logger.info(f"Autosave enabled with {interval} second interval")
        else:
            logger.info("Autosave disabled")

    def _update_project_data_for_autosave(self):
        """Update project data in the project manager for autosave."""
        if not self.project_manager.get_current_file_path():
            # No current project, nothing to update
            return
        
        # Get all elements from canvas
        elements = self.canvas.get_all_elements()
        
        # Serialize elements
        elements_data = []
        for element in elements:
            try:
                element_data = element.to_dict()
                elements_data.append(element_data)
            except Exception as e:
                logger.error(f"Error serializing element: {str(e)}")
        
        # Get background data if exists
        background_data = None
        if self.canvas.has_background():
            background_data = {
                "file_path": self.canvas.background_path
            }
        
        # Create project data
        project_data = {
            "elements": elements_data,
            "background": background_data
        }
        
        # Update project data in project manager
        self.project_manager.update_project_data(project_data)

    def _set_autosave_interval(self, interval_seconds):
        """Set the autosave interval."""
        self.settings.setValue("autosave_interval", interval_seconds)
        
        # Update the interval in the project manager if autosave is enabled
        if self.project_manager._autosave_enabled:
            self.project_manager.enable_autosave(True, interval_seconds)
        
        self._update_status(f"Autosave interval set to {interval_seconds // 60} minutes")

    def _clear_history(self):
        """Clear the undo/redo history."""
        if self.history_manager:
            self.history_manager.clear()
            self.statusBar().showMessage("History cleared")
            
    def _show_history_panel(self):
        """Show the history panel dialog."""
        # For now, just show a message box with the summary
        if self.history_manager:
            history = self.history_manager.get_history_summary(20)
            if not history:
                QMessageBox.information(self, "History", "No actions in history.")
                return
                
            history_text = "Recent Actions:\n\n"
            for i, action in enumerate(history):
                status = "Can Undo" if action["can_undo"] else "Can Redo"
                history_text += f"{i+1}. {action['description']} ({status})\n"
                
            QMessageBox.information(self, "History", history_text)
        else:
            QMessageBox.information(self, "History", "History manager not available.")

    def _save_selection_with_dialog(self):
        """Save the current selection with a user-provided name."""
        if not self.canvas.selection_manager.has_selection():
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select one or more elements to save."
            )
            return
        
        name, ok = QInputDialog.getText(
            self,
            "Save Selection",
            "Enter a name for this selection:"
        )
        
        if ok and name:
            if self.canvas.selection_manager.save_selection(name):
                self._update_status(f"Selection saved as '{name}'")
                # Update the named selections menu in the menu factory
                self.menu_factory.builders['edit'].update_named_selections_menu()
            else:
                QMessageBox.warning(
                    self,
                    "Save Failed",
                    f"Could not save selection as '{name}'"
                )

    def _restore_named_selection(self, name):
        """Restore a named selection."""
        if self.canvas.selection_manager.restore_selection(name):
            self._update_status(f"Selection '{name}' restored")
        else:
            self._update_status(f"Could not restore selection '{name}'")

    def _delete_named_selection(self, name):
        """Delete a named selection."""
        if self.canvas.selection_manager.delete_named_group(name):
            self._update_status(f"Selection '{name}' deleted")
            # Update the named selections menu in the menu factory
            self.menu_factory.builders['edit'].update_named_selections_menu()
        else:
            self._update_status(f"Could not delete selection '{name}'")

    def toggle_toolbar(self):
        """Toggle the visibility of the toolbar."""
        if hasattr(self, 'toolbar') and self.toolbar:
            self.toolbar.setVisible(not self.toolbar.isVisible())
            self.status_bar.showMessage(f"Toolbar {'shown' if self.toolbar.isVisible() else 'hidden'}")
    
    def toggle_property_panel(self):
        """Toggle the visibility of the property panel."""
        if hasattr(self, 'property_dock') and self.property_dock:
            self.property_dock.setVisible(not self.property_dock.isVisible())
            self.status_bar.showMessage(f"Property panel {'shown' if self.property_dock.isVisible() else 'hidden'}")

    def keyPressEvent(self, event):
        """Handle key press events."""
        # Check for debug keys
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_H:
                # Toggle hit areas debug visualization with Ctrl+H
                self.toggle_hit_area_visualization()
                event.accept()
                return
            
        # Pass to parent for default handling
        super().keyPressEvent(event)

    def toggle_hit_area_visualization(self):
        """Toggle the visualization of hit areas for elements."""
        self.canvas.toggle_hit_area_visualization()
        
        # Update status bar
        if self.canvas.show_hit_areas:
            self.status_bar.showMessage("Hit area visualization enabled")
        else:
            self.status_bar.showMessage("Hit area visualization disabled")

    def cut_selected_elements(self):
        """Cut the selected elements to the clipboard."""
        self.copy_selected_elements()
        self.delete_selected_elements()

    def copy_selected_elements(self):
        """Copy the selected elements to the clipboard."""
        selected_elements = self.canvas.selection_manager.get_selected_elements()
        if not selected_elements:
            return
        
        # TODO: Implement copying elements to clipboard
        self.status_bar.showMessage("Copy not implemented yet")

    def paste_elements(self):
        """Paste elements from the clipboard."""
        # TODO: Implement pasting elements from clipboard
        self.status_bar.showMessage("Paste not implemented yet")

    def delete_selected_elements(self):
        """Delete the selected elements."""
        selected_elements = self.canvas.selection_manager.get_selected_elements()
        if not selected_elements:
            return
        
        # Record the action for undo/redo
        def undo_delete():
            for element in selected_elements:
                self.canvas.add_element(element)
            self.canvas.selection_manager.select_elements(selected_elements)
            self._refresh_elements_list()
        
        def redo_delete():
            for element in selected_elements:
                self.canvas.remove_element(element)
            self._refresh_elements_list()
        
        self.history_manager.add_action(
            HistoryAction(
                "Delete Elements",
                undo_delete,
                redo_delete,
                ActionType.DELETE
            )
        )
        
        # Perform the deletion
        redo_delete()
        self.status_bar.showMessage(f"Deleted {len(selected_elements)} element(s)")

    def open_image(self):
        """Open an image file and set it as the canvas background."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Open Image")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        # Get supported formats as filter string
        filters = self.image_handler.get_supported_formats_filter()
        file_dialog.setNameFilter(filters)
        
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                self._load_image(file_path)
