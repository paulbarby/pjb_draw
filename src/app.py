"""
Main application class for the Drawing Package.
"""
import sys
import logging
import os
from logging.handlers import RotatingFileHandler

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QFileDialog, QMessageBox, QHBoxLayout, QToolBar,
    QPushButton, QLabel, QSizePolicy, QMenu, QToolButton,
    QStatusBar, QDockWidget
)
from PyQt6.QtCore import Qt, QMimeData, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QAction, QIcon, QColor

from src.ui.canvas import Canvas
from src.ui.property_panel import PropertyPanel
from src.utils.image_handler import ImageHandler
from src.utils.tool_manager import ToolType, ToolManager
from src.utils.history_manager import HistoryManager, HistoryAction, ActionType
from src.utils.project_manager import ProjectManager
from src.utils.export_manager import ExportManager, ExportFormat
from src.utils.element_factory import ElementFactory

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
        
        # Set up the main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Initialize utility managers first
        self.history_manager = HistoryManager()
        self.project_manager = ProjectManager()
        self.export_manager = ExportManager()
        self.element_factory = ElementFactory()
        
        # Create image handler
        self.image_handler = ImageHandler()
        
        # Create tool manager
        self.tool_manager = ToolManager()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create and add the canvas
        self.canvas = Canvas(parent=self, history_manager=self.history_manager)
        self.canvas.tool_manager = self.tool_manager
        self.layout.addWidget(self.canvas)
        
        # Connect canvas signals
        self.canvas.status_message.connect(self._update_status)
        self.canvas.element_created.connect(self._on_element_created)
        self.canvas.element_selected.connect(self._on_element_selected)
        self.canvas.element_changed.connect(self._on_element_changed)
        
        # Create property panel in a dock widget
        self.property_panel = PropertyPanel()
        self.property_panel.property_changed.connect(self._on_property_changed)
        self.property_panel.element_selected_from_list.connect(self._on_element_selected_from_list)
        
        # Create dock widget for property panel
        self.property_dock = QDockWidget("Properties", self)
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
        
        logger.info("Application initialized")
    
    def create_tools_toolbar(self):
        """Create the tools toolbar."""
        # Main toolbar
        self.toolbar = QToolBar("Drawing Tools")
        self.toolbar.setMovable(True)  # Allow toolbar to be moved
        self.toolbar.setFloatable(True)  # Allow toolbar to be detached as floating window
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        
        # Drawing tools group
        self.toolbar.addWidget(self.create_label("Drawing:"))
        
        # Add SELECT tool first
        select_action = self.create_tool_action("Select", "select", "Select and edit elements (S)")
        select_action.setShortcut("S")
        select_action.setChecked(True)  # Select tool is checked by default
        
        line_action = self.create_tool_action("Line", "line", "Draw lines (L)")
        line_action.setShortcut("L")
        rect_action = self.create_tool_action("Rectangle", "rectangle", "Draw rectangles (R)")
        rect_action.setShortcut("R")
        circle_action = self.create_tool_action("Circle", "circle", "Draw circles (C)")
        circle_action.setShortcut("C")
        text_action = self.create_tool_action("Text", "text", "Add text annotations (T)")
        text_action.setShortcut("T")
        
        self.toolbar.addSeparator()
        
        # File operations group
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
        action = QAction(QIcon(f"icons/{tool_type}.png"), name, self)
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
        from src.utils.tool_manager import ToolType
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
                
        # Update the current tool in tool manager
        self.tool_manager.set_tool(tool_type)
        self.status_bar.showMessage(f"Selected {tool_type.value} tool")
    
    def _on_element_selected(self, element):
        """Handle element selection."""
        logger.info(f"Element selected: {element}")
        self.status_bar.showMessage(f"Selected {type(element).__name__}")
        
        # Update property panel with selected element
        self.property_panel.update_from_element(element)
        
    def _on_element_created(self, element):
        """Handle element creation."""
        logger.info(f"Element created: {element}")
        self.status_bar.showMessage(f"Created {type(element).__name__}")
        
        # Update property panel with the newly created element
        self.property_panel.update_from_element(element)
        
        # Refresh elements list
        self._refresh_elements_list()
        
    def _on_element_changed(self, element):
        """Handle element modification."""
        logger.info(f"Element modified: {element}")
        self.status_bar.showMessage(f"Modified {type(element).__name__}")
        
        # Update property panel if the modified element is selected
        if self.property_panel.current_element == element:
            self.property_panel.update_from_element(element)
            
        # Refresh elements list to update any displayed properties
        self._refresh_elements_list()
    
    def _on_property_changed(self, property_name, value):
        """Handle property changes from the property panel."""
        element = self.property_panel.current_element
        if not element:
            return
            
        logger.info(f"Changing property '{property_name}' to '{value}' for {type(element).__name__}")
        
        # Track whether the element was modified
        modified = False
        
        # Apply the property change to the element
        if property_name == "color" and hasattr(element, "pen"):
            # Try both method and property approaches to ensure compatibility
            try:
                if callable(element.pen):
                    pen = element.pen()
                    pen.setColor(value)
                    element.setPen(pen)
                else:
                    element.color = value  # Using property accessor
                modified = True
            except Exception as e:
                logger.error(f"Error setting color: {e}")
        
        elif property_name == "line_thickness" and hasattr(element, "pen"):
            try:
                if callable(element.pen):
                    pen = element.pen()
                    pen.setWidth(value)
                    element.setPen(pen)
                else:
                    element.thickness = value  # Using property accessor
                modified = True
            except Exception as e:
                logger.error(f"Error setting line thickness: {e}")
            
        elif property_name == "x" and hasattr(element, "setX"):
            try:
                # Adjust for the position within the element's bounding rect
                if hasattr(element, "boundingRect"):
                    element.setX(value - element.boundingRect().x())
                else:
                    element.setX(value)
                modified = True
            except Exception as e:
                logger.error(f"Error setting x position: {e}")
                
        elif property_name == "y" and hasattr(element, "setY"):
            try:
                if hasattr(element, "boundingRect"):
                    element.setY(value - element.boundingRect().y())
                else:
                    element.setY(value)
                modified = True
            except Exception as e:
                logger.error(f"Error setting y position: {e}")
                
        elif property_name == "width" and hasattr(element, "setRect"):
            try:
                # For direct rect access
                if hasattr(element, "rect"):
                    if callable(element.rect):
                        rect = element.rect()
                        rect.setWidth(value)
                        element.setRect(rect)
                    else:
                        # Using property
                        rect = element.rect
                        rect.setWidth(value)
                        element.rect = rect
                modified = True
            except Exception as e:
                logger.error(f"Error setting width: {e}")
            
        elif property_name == "height" and hasattr(element, "setRect"):
            try:
                # For direct rect access
                if hasattr(element, "rect"):
                    if callable(element.rect):
                        rect = element.rect()
                        rect.setHeight(value)
                        element.setRect(rect)
                    else:
                        # Using property
                        rect = element.rect
                        rect.setHeight(value)
                        element.rect = rect
                modified = True
            except Exception as e:
                logger.error(f"Error setting height: {e}")
            
        elif property_name == "text" and hasattr(element, "setText"):
            try:
                element.setText(value)
                modified = True
            except Exception as e:
                logger.error(f"Error setting text: {e}")
            
        elif property_name == "font_size" and hasattr(element, "font"):
            try:
                if callable(element.font):
                    font = element.font()
                    font.setPointSize(value)
                    element.setFont(font)
                else:
                    # Using direct property
                    font = element.font
                    font.setPointSize(value)
                    element.font = font
                modified = True
            except Exception as e:
                logger.error(f"Error setting font size: {e}")
                
        # Notify that the element was changed if modifications were made
        if modified:
            element.update()  # Force element to redraw itself
            self.canvas.element_changed.emit(element)
            self.canvas.viewport().update()  # Force canvas update
    
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
    
    def closeEvent(self, event):
        """Handle application close events."""
        logger.info("Application closing")
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
        """
        Load an image from file and set it as the canvas background.
        
        Args:
            file_path: Path to the image file to load
        """
        if not self.image_handler.load_image(file_path):
            QMessageBox.warning(
                self, 
                "Image Load Error", 
                f"Failed to load image: {file_path}"
            )
            return
            
        # Get pixmap from the image handler
        pixmap = self.image_handler.get_pixmap()
        if not pixmap or pixmap.isNull():
            QMessageBox.warning(
                self, 
                "Image Load Error", 
                "Failed to convert image to a displayable format."
            )
            return
            
        # Set the pixmap as the canvas background
        if hasattr(self, 'canvas') and self.canvas:
            if self.canvas.set_background_image(pixmap):
                self.status_bar.showMessage(f"Loaded image: {file_path}")
                
                # Record in history manager if available
                if self.history_manager:
                    # Store previous background for undo
                    prev_background = self.canvas.get_background_image()
                    
                    def undo_set_background():
                        self.canvas.set_background_image(prev_background)
                        
                    def redo_set_background():
                        self.canvas.set_background_image(pixmap)
                        
                    action = HistoryAction(
                        ActionType.SET_BACKGROUND,
                        undo_set_background,
                        redo_set_background,
                        "Set background image"
                    )
                    
                    self.history_manager.add_action(action)
            else:
                self.status_bar.showMessage(f"Failed to set image as background")
        else:
            self.status_bar.showMessage(f"Canvas not available to display image")
    
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
            self._load_from_file(file_path)
    
    def _load_from_file(self, file_path: str):
        """Load a project from a file."""
        if not hasattr(self, 'canvas') or not self.canvas:
            QMessageBox.warning(self, "Open Error", "No canvas to load into.")
            return
            
        # Load project using project manager
        project_data = self.project_manager.load_project(file_path, self.element_factory)
        
        if project_data:
            # Clear current canvas
            self.canvas.clear_canvas()
            
            # Set background image if available
            if project_data["background_image"]:
                self.canvas.set_background_image(project_data["background_image"])
            
            # Add elements to canvas
            for element in project_data["elements"]:
                self.canvas.scene.addItem(element)
            
            # Apply metadata if available
            metadata = project_data.get("metadata", {})
            canvas_size = metadata.get("canvas_size", {})
            if canvas_size:
                self.canvas.scene.setSceneRect(0, 0, 
                                             canvas_size.get("width", 2000),
                                             canvas_size.get("height", 2000))
            
            # Clear history as we're loading a new project
            self.history_manager.clear()
            
            # Refresh elements list
            self._refresh_elements_list()
            
            self.statusBar().showMessage(f"Project loaded from {file_path}")
        else:
            QMessageBox.warning(self, "Open Error", "Failed to load the project.")
    
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
        """Save the project to a file."""
        if hasattr(self, 'canvas') and self.canvas:
            # Get all elements from the canvas
            elements = self.canvas.get_all_elements()
            
            # Get background image if any
            background_image = self.canvas.get_background_image()
            
            # Additional metadata
            metadata = {
                "canvas_size": {
                    "width": self.canvas.scene.width(),
                    "height": self.canvas.scene.height()
                }
            }
            
            # Save using project manager
            if self.project_manager.save_project(file_path, elements, background_image, metadata):
                self.statusBar().showMessage(f"Project saved to {file_path}")
            else:
                QMessageBox.warning(self, "Save Error", "Failed to save the project.")
        else:
            QMessageBox.warning(self, "Save Error", "No canvas to save.")
    
    def export_image(self):
        """Export the canvas as an image."""
        if not hasattr(self, 'canvas') or not self.canvas:
            QMessageBox.warning(self, "Export Error", "No canvas to export.")
            return
        
        # Create dialog for export options
        file_filter = ";;".join([
            "PNG Files (*.png)",
            "JPEG Files (*.jpg *.jpeg)",
            "PDF Files (*.pdf)",
            "SVG Files (*.svg)"
        ])
        
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Image",
            "",
            file_filter
        )
        
        if not file_path:
            return
            
        # Determine format based on selected filter or file extension
        format_map = {
            "PNG Files (*.png)": ExportFormat.PNG,
            "JPEG Files (*.jpg *.jpeg)": ExportFormat.JPG,
            "PDF Files (*.pdf)": ExportFormat.PDF,
            "SVG Files (*.svg)": ExportFormat.SVG
        }
        
        export_format = None
        
        # Check selected filter first
        if selected_filter in format_map:
            export_format = format_map[selected_filter]
        
        # If not determined by filter, check file extension
        if not export_format:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.png':
                export_format = ExportFormat.PNG
            elif ext in ('.jpg', '.jpeg'):
                export_format = ExportFormat.JPG
            elif ext == '.pdf':
                export_format = ExportFormat.PDF
            elif ext == '.svg':
                export_format = ExportFormat.SVG
            else:
                # Default to PNG if unknown
                export_format = ExportFormat.PNG
                file_path += '.png'
        
        # Ensure file has the correct extension
        expected_ext = f".{export_format.value}"
        if not file_path.lower().endswith(expected_ext):
            file_path += expected_ext
        
        # Export using the export manager
        if self.export_manager.export_to_image(self.canvas.scene, file_path, export_format):
            self.statusBar().showMessage(f"Exported to {file_path}")
        else:
            QMessageBox.warning(self, "Export Error", "Failed to export the image.")
    
    def zoom_in(self):
        """Zoom in the canvas."""
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.scale(1.2, 1.2)
        self.status_bar.showMessage("Zoomed in")
    
    def zoom_out(self):
        """Zoom out the canvas."""
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.scale(0.8, 0.8)
        self.status_bar.showMessage("Zoomed out")
    
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
        self.action_undo.setEnabled(can_undo)
        self.action_redo.setEnabled(can_redo)
        
        # Update status bar with descriptions if available
        if can_undo:
            undo_desc = self.history_manager.get_undo_description()
            if undo_desc:
                self.action_undo.setStatusTip(f"Undo: {undo_desc}")
        else:
            self.action_undo.setStatusTip("Undo")
            
        if can_redo:
            redo_desc = self.history_manager.get_redo_description()
            if redo_desc:
                self.action_redo.setStatusTip(f"Redo: {redo_desc}")
        else:
            self.action_redo.setStatusTip("Redo")

    def _update_status(self, message):
        """Update the status bar message."""
        self.status_bar.showMessage(message)
    
    def _on_element_selected_from_list(self, element):
        """Handle when user selects an element from the property panel list."""
        if element is None:
            # This is a request to refresh the list
            self._refresh_elements_list()
            return
            
        # Select the element on the canvas
        self.canvas.scene.clearSelection()
        element.setSelected(True)
        self.canvas.element_selected.emit(element)
        
        # Update property panel
        self.property_panel.update_from_element(element)
        
        # Update status bar
        self.status_bar.showMessage(f"Selected {type(element).__name__}")
    
    def _refresh_elements_list(self):
        """Refresh the elements list in the property panel."""
        if hasattr(self, 'canvas') and self.canvas:
            # Get all elements from the canvas
            elements = self.canvas.get_all_elements()
            
            # Update the property panel's elements list
            self.property_panel.update_elements_list(elements)

    def create_menu_bar(self):
        """Create the application menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # New Project
        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Create a new project")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        # Open Project
        open_project_action = QAction("&Open Project...", self)
        open_project_action.setShortcut("Ctrl+O")
        open_project_action.setStatusTip("Open an existing project")
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)
        
        # Open Image
        open_image_action = QAction("Open &Image...", self)
        open_image_action.setShortcut("Ctrl+I")
        open_image_action.setStatusTip("Open an image as background")
        open_image_action.triggered.connect(self.open_image)
        file_menu.addAction(open_image_action)
        
        file_menu.addSeparator()
        
        # Save
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Save the current project")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        # Save As
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.setStatusTip("Save the current project with a new name")
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Export
        export_action = QAction("&Export Image...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setStatusTip("Export the canvas as an image")
        export_action.triggered.connect(self.export_image)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        
        # Undo
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setStatusTip("Undo the last action")
        undo_action.triggered.connect(self.undo_action)
        edit_menu.addAction(undo_action)
        
        # Redo
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.setStatusTip("Redo the previously undone action")
        redo_action.triggered.connect(self.redo_action)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        # Clear Canvas
        clear_action = QAction("&Clear Canvas", self)
        clear_action.setShortcut("Ctrl+Shift+C")
        clear_action.setStatusTip("Clear all elements from the canvas")
        clear_action.triggered.connect(self.clear_canvas)
        edit_menu.addAction(clear_action)
        
        # View menu
        view_menu = menu_bar.addMenu("&View")
        
        # Zoom In
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.setStatusTip("Zoom in on the canvas")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        # Zoom Out
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.setStatusTip("Zoom out on the canvas")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        view_menu.addSeparator()
        
        # Clear Background
        clear_bg_action = QAction("Clear &Background", self)
        clear_bg_action.setStatusTip("Remove the background image")
        clear_bg_action.triggered.connect(self.clear_background)
        view_menu.addAction(clear_bg_action)

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

    def clear_background(self):
        """Remove the background image from the canvas."""
        if hasattr(self, 'canvas') and self.canvas:
            # Store previous background for undo
            prev_background = self.canvas.get_background_image()
            
            # Clear the background
            success = self.canvas.set_background_image(None)
            
            if success:
                self.status_bar.showMessage("Background image cleared")
                
                # Record in history manager if available
                if self.history_manager and prev_background:
                    def undo_clear_background():
                        self.canvas.set_background_image(prev_background)
                        
                    def redo_clear_background():
                        self.canvas.set_background_image(None)
                        
                    action = HistoryAction(
                        ActionType.SET_BACKGROUND,
                        undo_clear_background,
                        redo_clear_background,
                        "Clear background image"
                    )
                    
                    self.history_manager.add_action(action)
            else:
                self.status_bar.showMessage("No background image to clear")
