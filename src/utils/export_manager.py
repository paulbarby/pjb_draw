"""
Export management for the Drawing Package.

This module provides functionality for exporting the canvas
to various image formats like PNG, JPG, PDF, and SVG.
"""
import os
import logging
from typing import Optional, Dict, Any, Tuple
from enum import Enum

from PyQt6.QtCore import QRectF, Qt, QSizeF
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtSvg import QSvgGenerator
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import QGraphicsScene

logger = logging.getLogger(__name__)

class ExportFormat(Enum):
    """Supported export formats."""
    PNG = "png"
    JPG = "jpg"
    PDF = "pdf"
    SVG = "svg"

class ExportManager:
    """
    Manages exporting the canvas to different formats.
    
    This class provides methods to export the canvas content
    to various image formats with configurable options.
    """
    
    def __init__(self):
        """Initialize the export manager."""
        logger.info("Export manager initialized")
    
    def export_to_image(self, scene: QGraphicsScene, file_path: str, 
                       format: ExportFormat = ExportFormat.PNG, 
                       dpi: int = 300,
                       background_color: Optional[str] = None,
                       quality: int = 90,
                       export_area: Optional[QRectF] = None) -> bool:
        """
        Export the canvas to an image file.
        
        Args:
            scene: The QGraphicsScene to export
            file_path: Path to save the exported file
            format: The export format to use
            dpi: Resolution in dots per inch (used for PDF and raster formats)
            background_color: Optional background color (None for transparent where supported)
            quality: Image quality for JPG (0-100)
            export_area: Specific area to export (None for entire scene)
            
        Returns:
            True if export succeeded, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # If no export area is specified, use the scene bounding rect
            if export_area is None:
                export_area = scene.itemsBoundingRect()
                
                # If there are no items, use the scene rect
                if export_area.isEmpty():
                    export_area = scene.sceneRect()
            
            if format == ExportFormat.PDF:
                return self._export_to_pdf(scene, file_path, export_area, dpi, background_color)
            elif format == ExportFormat.SVG:
                return self._export_to_svg(scene, file_path, export_area, background_color)
            else:  # PNG, JPG
                return self._export_to_raster(scene, file_path, format.value, export_area, 
                                            dpi, background_color, quality)
                
        except Exception as e:
            logger.error(f"Error exporting to {file_path}: {str(e)}")
            return False
    
    def _export_to_raster(self, scene: QGraphicsScene, file_path: str, 
                         format_name: str, export_area: QRectF, dpi: int,
                         background_color: Optional[str], quality: int) -> bool:
        """
        Export the canvas to a raster image format (PNG or JPG).
        
        Args:
            scene: The QGraphicsScene to export
            file_path: Path to save the exported file
            format_name: The format name (png or jpg)
            export_area: Area to export
            dpi: Resolution in dots per inch
            background_color: Optional background color
            quality: Image quality for JPG (0-100)
            
        Returns:
            True if export succeeded, False otherwise
        """
        # Calculate pixel dimensions based on DPI
        inch_width = export_area.width() / 96  # Assuming screen is 96 DPI
        inch_height = export_area.height() / 96
        
        pixel_width = int(inch_width * dpi)
        pixel_height = int(inch_height * dpi)
        
        # Create image with appropriate size and format
        if format_name.lower() == "png":
            image = QImage(pixel_width, pixel_height, QImage.Format.Format_ARGB32)
            if background_color is None:
                image.fill(Qt.GlobalColor.transparent)
            else:
                image.fill(background_color)
        else:  # JPG doesn't support transparency
            image = QImage(pixel_width, pixel_height, QImage.Format.Format_RGB32)
            image.fill(background_color or Qt.GlobalColor.white)
        
        # Set up painter for the image
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Scale painter to fit the desired DPI
        scale_factor = dpi / 96  # Scale based on standard screen DPI
        painter.scale(scale_factor, scale_factor)
        
        # Render the scene to the image
        scene.render(painter, QRectF(0, 0, export_area.width(), export_area.height()), export_area)
        painter.end()
        
        # Save the image with appropriate format and quality
        save_params = [quality] if format_name.lower() == "jpg" else []
        success = image.save(file_path, format_name.upper(), *save_params)
        
        if success:
            logger.info(f"Exported to {format_name.upper()} file: {file_path}")
        else:
            logger.error(f"Failed to save {format_name.upper()} file: {file_path}")
        
        return success
    
    def _export_to_pdf(self, scene: QGraphicsScene, file_path: str, 
                      export_area: QRectF, dpi: int,
                      background_color: Optional[str]) -> bool:
        """
        Export the canvas to a PDF file.
        
        Args:
            scene: The QGraphicsScene to export
            file_path: Path to save the exported file
            export_area: Area to export
            dpi: Resolution in dots per inch
            background_color: Optional background color
            
        Returns:
            True if export succeeded, False otherwise
        """
        # Create PDF printer
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_path)
        printer.setResolution(dpi)
        
        # Set the page size to match the export area
        paper_size = QSizeF(export_area.width(), export_area.height())
        printer.setPageSize(QPrinter.PageSize.Custom)
        printer.setPageSizeMM(QSizeF(paper_size.width() * 0.2645, paper_size.height() * 0.2645))  # Convert to mm
        
        # Set up painter for the PDF
        painter = QPainter(printer)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # Fill background if specified
        if background_color:
            painter.fillRect(QRectF(0, 0, export_area.width(), export_area.height()), background_color)
        
        # Render the scene to the PDF
        scene.render(painter, QRectF(0, 0, export_area.width(), export_area.height()), export_area)
        painter.end()
        
        logger.info(f"Exported to PDF file: {file_path}")
        return True
    
    def _export_to_svg(self, scene: QGraphicsScene, file_path: str, 
                      export_area: QRectF,
                      background_color: Optional[str]) -> bool:
        """
        Export the canvas to an SVG file.
        
        Args:
            scene: The QGraphicsScene to export
            file_path: Path to save the exported file
            export_area: Area to export
            background_color: Optional background color
            
        Returns:
            True if export succeeded, False otherwise
        """
        # Create SVG generator
        generator = QSvgGenerator()
        generator.setFileName(file_path)
        generator.setSize(QSizeF(export_area.width(), export_area.height()).toSize())
        generator.setViewBox(QRectF(0, 0, export_area.width(), export_area.height()))
        generator.setTitle("Drawing Package Export")
        generator.setDescription("SVG created by Drawing Package")
        
        # Set up painter for the SVG
        painter = QPainter(generator)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # Fill background if specified
        if background_color:
            painter.fillRect(QRectF(0, 0, export_area.width(), export_area.height()), background_color)
        
        # Render the scene to the SVG
        scene.render(painter, QRectF(0, 0, export_area.width(), export_area.height()), export_area)
        painter.end()
        
        logger.info(f"Exported to SVG file: {file_path}")
        return True
        
    def get_supported_formats(self) -> Dict[str, str]:
        """
        Get a dictionary of supported export formats.
        
        Returns:
            Dictionary mapping format names to file extensions
        """
        return {
            "PNG": "*.png",
            "JPEG": "*.jpg *.jpeg",
            "PDF": "*.pdf",
            "SVG": "*.svg"
        } 