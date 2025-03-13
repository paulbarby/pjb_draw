# Python-Based Drawing Package Specification

## Overview

This document outlines the specifications for a Python-based drawing package designed for marking up plans and images. The package will provide essential tools for adding annotations, lines, and other vector-based elements, with features tailored for plan and image markup. The UI will have a modern iOS-like look, support responsive resizing, and offer a seamless user experience.

## Features

### 1. **Core Functionality**

- **Image Loading**

  - Support for loading existing images (JPEG, PNG, BMP, SVG, PDF).
  - Drag-and-drop functionality for quick image loading.

- **Vector-Based Drawing Elements**
  - **Lines:** Straight-line drawing with adjustable thickness and color.
  - **Arrows:** Customizable arrowheads with attached notes.
  - **Text Annotations:** User-defined text with font size, color, and background options.
  - **Free Draw with Smoothing:** Hand-drawn lines with automatic smoothing for better readability.
  - **Circles and Shapes:** Ability to draw perfect circles, ellipses, and rectangles.
  - **Layers:** Support for multiple layers, enabling independent manipulation and flattening.

### 2. **Editing and Manipulation**

- **Multi-Step Undo/Redo**

  - Ability to undo and redo multiple drawing steps.

- **Vector Element Controls**

  - **Duplication:** Clone existing elements.
  - **Repositioning:** Drag elements to reposition.
  - **Resizing:** Adjust width and height while maintaining aspect ratio (if locked).
  - **Rotation:** Free rotation of vector elements.
  - **Alignment and Snapping:** Option to align elements and snap to guides.

- **Hotkeys for Precision Editing**
  - **Shift + Drag:** Lock vertical/horizontal movement.
  - **Ctrl + Scroll:** Zoom in/out.
  - **Arrow Keys:** Nudge elements in small increments.
  - **Ctrl + Z:** Undo last action.
  - **Ctrl + Y:** Redo last undone action.
  - **Ctrl + C:** Copy selected element.
  - **Ctrl + V:** Paste copied element.
  - **Ctrl + X:** Cut selected element.
  - **Delete:** Remove selected element.
  - **Ctrl + S:** Save project.
  - **Ctrl + O:** Open saved project.
  - **Ctrl + P:** Export or print annotated image.
  - **Ctrl + A:** Select all elements.
  - **Ctrl + D:** Deselect all elements.
  - **Space + Drag:** Pan the canvas.
  - **Mouse Wheel:** Scroll vertically.
  - **Shift + Mouse Wheel:** Scroll horizontally.

### 3. **Export and Saving**

- **Save and Load Markup Files**

  - Ability to save the drawing as a project file retaining vector layers.
  - Reopen saved projects for further edits.

- **Flattening Vectors to Bitmap**

  - Convert vector elements to raster images while preserving the background image.
  - Layer-specific flattening for finer control.

- **Export Options**
  - PNG, JPG: Save the markup image with adjustable resolution.
  - PDF: Export the annotated image as a high-resolution PDF.
  - SVG: Preserve vector elements in scalable vector format.

### 4. **User Interface**

- **Modern iOS-Inspired UI**

  - Clean and minimalist design with smooth animations.
  - Floating toolbar with customizable tools.
  - Responsive layout adapting to window resizing.
  - Dark and light mode support.

- **Workspace Customization**
  - Full-window mode for distraction-free markup.
  - Dockable tool panels for a flexible workspace.
  - Zooming and panning support for large images.

### 5. **Technical Requirements**

- **Programming Language:** Python
- **Frameworks & Libraries:**

  - PyQt or Tkinter for UI
  - PIL/Pillow for image processing
  - OpenCV for advanced image handling
  - NumPy for performance optimization
  - SVGwrite or Cairo for vector rendering

- **Operating System Compatibility:**
  - Windows
  - macOS
  - Linux

## Conclusion

This Python-based drawing package will provide an intuitive and efficient solution for marking up plans and images. With vector-based elements, undo/redo functionality, layer support, and modern UI design, it will serve as a powerful tool for professionals handling technical drawings and annotations.
