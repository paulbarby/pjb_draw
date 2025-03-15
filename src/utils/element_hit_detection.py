"""
Element hit detection utilities for the Drawing Package.

This module provides specialized hit detection functions for different element types,
making selection more accurate, especially for thin elements like lines.
"""
import math
from PyQt6.QtCore import QPointF, QRectF, QLineF
from PyQt6.QtGui import QPen, QColor, QBrush
from src.drawing.elements import VectorElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.text_element import TextElement
from src.drawing.elements.image_element import ImageElement

# Tolerance for hit detection in scene coordinates
HIT_TOLERANCE = 2.0

def point_to_line_distance(point, line_start, line_end):
    """
    Calculate the distance from a point to a line segment.
    
    Args:
        point: The point to check (QPointF)
        line_start: Start point of the line (QPointF)
        line_end: End point of the line (QPointF)
        
    Returns:
        Float distance from point to line segment
    """
    # Convert to QLineF for easier calculations
    line = QLineF(line_start, line_end)
    
    # If line has zero length, return distance to the point
    if line.length() == 0:
        return QLineF(point, line_start).length()
    
    # Calculate the perpendicular distance
    # First, get the normalized direction vector of the line
    dx = line_end.x() - line_start.x()
    dy = line_end.y() - line_start.y()
    length = line.length()
    
    # Normalize
    dx /= length
    dy /= length
    
    # Calculate the perpendicular distance
    px = point.x() - line_start.x()
    py = point.y() - line_start.y()
    
    # Project the point onto the line
    proj = px * dx + py * dy
    
    # If projection is outside line segment, return distance to nearest endpoint
    if proj < 0:
        return QLineF(point, line_start).length()
    if proj > length:
        return QLineF(point, line_end).length()
    
    # Calculate perpendicular distance
    perp_x = line_start.x() + proj * dx
    perp_y = line_start.y() + proj * dy
    
    return QLineF(point, QPointF(perp_x, perp_y)).length()

def point_to_rect_edge_distance(point, rect):
    """
    Calculate the distance from a point to the nearest edge of a rectangle.
    
    Args:
        point: The point to check (QPointF)
        rect: The rectangle (QRectF)
        
    Returns:
        Float distance from point to nearest rectangle edge
    """
    # Check if point is inside the rectangle
    if rect.contains(point):
        # Calculate distance to each edge
        dist_left = point.x() - rect.left()
        dist_right = rect.right() - point.x()
        dist_top = point.y() - rect.top()
        dist_bottom = rect.bottom() - point.y()
        
        # Return the minimum distance
        return min(dist_left, dist_right, dist_top, dist_bottom)
    
    # If point is outside, calculate distance to nearest edge
    top_left = rect.topLeft()
    top_right = rect.topRight()
    bottom_left = rect.bottomLeft()
    bottom_right = rect.bottomRight()
    
    # Calculate distance to each edge
    dist_top = point_to_line_distance(point, top_left, top_right)
    dist_right = point_to_line_distance(point, top_right, bottom_right)
    dist_bottom = point_to_line_distance(point, bottom_left, bottom_right)
    dist_left = point_to_line_distance(point, top_left, bottom_left)
    
    # Return the minimum distance
    return min(dist_top, dist_right, dist_bottom, dist_left)

def point_to_circle_edge_distance(point, center, radius):
    """
    Calculate the distance from a point to the edge of a circle.
    
    Args:
        point: The point to check (QPointF)
        center: Center of the circle (QPointF)
        radius: Radius of the circle (float)
        
    Returns:
        Float distance from point to circle edge (negative if inside)
    """
    # Calculate the distance from point to center
    dist_to_center = QLineF(point, center).length()
    
    # Return the absolute difference between this distance and the radius
    return abs(dist_to_center - radius)

def is_line_hit(line_element, local_point):
    """
    Check if a line element is hit by checking for intersection within tolerance.
    Line elements are thin, so we check if the mouse is within +/- HIT_TOLERANCE pixels.
    
    Args:
        line_element: The LineElement to check
        local_point: The point in the element's local coordinates
        
    Returns:
        True if the line is hit, False otherwise
    """
    # Calculate perpendicular distance from point to line
    distance = point_to_line_distance(
        local_point, 
        line_element.start_point, 
        line_element.end_point
    )
    
    # Line is hit if distance is within tolerance (+/- 2 pixels)
    return distance <= HIT_TOLERANCE

def is_rectangle_hit(rect_element, local_point):
    """
    Check if a rectangle element is hit by checking edge proximity.
    We look for intersection with the rectangle edge, not the interior.
    
    Args:
        rect_element: The RectangleElement to check
        local_point: The point in the element's local coordinates
        
    Returns:
        True if the rectangle edge is hit, False otherwise
    """
    # Get the rectangle in element's local coordinates
    rect = rect_element._rect
    
    # Calculate distance to nearest edge
    dist_left = abs(local_point.x() - rect.left())
    dist_right = abs(rect.right() - local_point.x())
    dist_top = abs(local_point.y() - rect.top())
    dist_bottom = abs(rect.bottom() - local_point.y())
    
    # Find the minimum distance to any edge
    min_distance = min(dist_left, dist_right, dist_top, dist_bottom)
    
    # Check if we're inside the rectangle
    is_inside = rect.contains(local_point)
    
    # Hit if:
    # 1. We're inside and close to an edge, or
    # 2. We're outside but very close to an edge
    if is_inside:
        return min_distance <= HIT_TOLERANCE
    else:
        # When outside, use point_to_rect_edge_distance for more accurate detection
        distance = point_to_rect_edge_distance(local_point, rect)
        return distance <= HIT_TOLERANCE

def is_circle_hit(circle_element, local_point):
    """
    Check if a circle element is hit by checking edge proximity.
    We look for intersection with the circle edge, not the interior.
    
    Args:
        circle_element: The CircleElement to check
        local_point: The point in the element's local coordinates
        
    Returns:
        True if the circle edge is hit, False otherwise
    """
    # Get the center and radius
    center = circle_element.center
    radius = circle_element.radius
    
    # Calculate distance from point to circle center
    dist_to_center = QLineF(local_point, center).length()
    
    # Calculate distance from point to circle edge
    edge_distance = abs(dist_to_center - radius)
    
    # Circle edge is hit if distance is within tolerance
    return edge_distance <= HIT_TOLERANCE

def is_text_hit(text_element, local_point):
    """
    Check if a text element is hit.
    
    For text elements, we check if the point is within the text's bounding rectangle.
    
    Args:
        text_element: The TextElement to check
        local_point: The point in the element's local coordinates
        
    Returns:
        True if the text is hit, False otherwise
    """
    try:
        # Try to get the bounding rectangle using fontMetrics
        font_metrics = text_element.fontMetrics()
        text_content = text_element.text
        if callable(text_content):
            text_content = text_content()
        text_rect = font_metrics.boundingRect(text_content)
        text_rect.moveTopLeft(QPointF(text_element.position.x(), text_element.position.y() - font_metrics.ascent()))
    except (AttributeError, TypeError):
        # Fallback: use a simple rectangle around the position
        # Get text content, handling both property and method cases
        try:
            text_content = text_element.text
            if callable(text_content):
                text_content = text_content()
        except (AttributeError, TypeError):
            # If we can't get the text, use a default size
            text_content = "Text"
            
        text_width = len(text_content) * 10  # Approximate width based on text length
        text_height = 20  # Approximate height
        
        # Get position, handling both property and method cases
        try:
            position = text_element.position
            if callable(position):
                position = position()
        except (AttributeError, TypeError):
            # If we can't get the position, use (0,0)
            position = QPointF(0, 0)
            
        text_rect = QRectF(
            position.x(), 
            position.y() - text_height, 
            text_width, 
            text_height
        )
    
    # Point is inside the text's bounding rectangle
    return text_rect.contains(local_point)

def is_image_hit(image_element, local_point):
    """
    Check if an image element is hit.
    
    Args:
        image_element: The ImageElement to check
        local_point: The point in the element's local coordinates
        
    Returns:
        True if the image is hit, False otherwise
    """
    # Get the rectangle in element's local coordinates
    rect = image_element.rect
    
    # Check if point is within rectangle
    return rect.contains(local_point)

def is_element_hit(element, scene_point):
    """
    Check if an element is hit by a point in scene coordinates.
    
    This function uses specialized hit detection for different element types:
    - For lines: Uses perpendicular distance to the line (within +/- 2 pixels)
    - For rectangles: Checks proximity to the nearest edge
    - For circles: Checks proximity to the circle edge
    - For text: Checks if the point is within the bounding rectangle
    - For other elements: Falls back to default detection
    
    Args:
        element: The element to check
        scene_point: The point in scene coordinates
        
    Returns:
        True if the element is hit, False otherwise
    """
    # Convert scene point to element's local coordinates
    local_point = element.mapFromScene(scene_point)
    
    # Use specialized hit detection based on element type
    if isinstance(element, LineElement):
        return is_line_hit(element, local_point)
    
    elif isinstance(element, RectangleElement):
        return is_rectangle_hit(element, local_point)
    
    elif isinstance(element, CircleElement):
        return is_circle_hit(element, local_point)
    
    elif isinstance(element, TextElement):
        return is_text_hit(element, local_point)
    
    elif isinstance(element, ImageElement):
        return is_image_hit(element, local_point)
    
    # Default case - use the element's boundingRect
    return element.boundingRect().contains(local_point)

def debug_visualize_hit_areas(scene, painter):
    """
    Visualize hit detection areas for elements in the scene.
    
    This is a debug utility that draws the hit areas for each element.
    
    Args:
        scene: The QGraphicsScene containing elements
        painter: The QPainter to draw with
    """
    # Set up drawing style
    hit_pen = QPen(QColor(255, 0, 0, 128), 1)
    hit_brush = QBrush(QColor(255, 0, 0, 64))
    
    # Draw hit areas for each element
    for item in scene.items():
        if not isinstance(item, VectorElement):
            continue
            
        # Draw based on element type
        if isinstance(item, LineElement):
            # Draw a thickened line representing the hit area
            line_pen = QPen(QColor(255, 0, 0, 128), HIT_TOLERANCE * 2)
            painter.setPen(line_pen)
            scene_start = item.mapToScene(item.start_point)
            scene_end = item.mapToScene(item.end_point)
            painter.drawLine(scene_start, scene_end)
            
        elif isinstance(item, RectangleElement):
            # Draw an expanded rectangle border showing the hit area
            painter.setPen(hit_pen)
            painter.setBrush(QBrush())  # No fill
            
            # Inner rectangle (inner hit boundary)
            inner_rect = item.mapRectToScene(item._rect).adjusted(
                HIT_TOLERANCE, HIT_TOLERANCE, 
                -HIT_TOLERANCE, -HIT_TOLERANCE
            )
            
            # Outer rectangle (outer hit boundary)
            outer_rect = item.mapRectToScene(item._rect).adjusted(
                -HIT_TOLERANCE, -HIT_TOLERANCE, 
                HIT_TOLERANCE, HIT_TOLERANCE
            )
            
            # Draw both to show the hit area
            painter.drawRect(inner_rect)
            painter.drawRect(outer_rect)
            
        elif isinstance(item, CircleElement):
            # Draw a ring around the circle showing the hit area
            painter.setPen(hit_pen)
            painter.setBrush(QBrush())  # No fill
            scene_center = item.mapToScene(item.center)
            
            # Inner and outer circles showing hit boundaries
            painter.drawEllipse(
                scene_center, 
                item.radius - HIT_TOLERANCE, 
                item.radius - HIT_TOLERANCE
            )
            painter.drawEllipse(
                scene_center, 
                item.radius + HIT_TOLERANCE, 
                item.radius + HIT_TOLERANCE
            )
            
        elif isinstance(item, TextElement):
            # Draw the text bounding box
            painter.setPen(hit_pen)
            painter.setBrush(hit_brush)
            
            try:
                # Try to get the bounding rectangle using fontMetrics
                font_metrics = item.fontMetrics()
                text_content = item.text
                if callable(text_content):
                    text_content = text_content()
                text_rect = font_metrics.boundingRect(text_content)
                text_rect.moveTopLeft(QPointF(item.position.x(), item.position.y() - font_metrics.ascent()))
            except (AttributeError, TypeError):
                # Fallback: use a simple rectangle around the position
                # Get text content, handling both property and method cases
                try:
                    text_content = item.text
                    if callable(text_content):
                        text_content = text_content()
                except (AttributeError, TypeError):
                    # If we can't get the text, use a default size
                    text_content = "Text"
                    
                text_width = len(text_content) * 10  # Approximate width based on text length
                text_height = 20  # Approximate height
                
                # Get position, handling both property and method cases
                try:
                    position = item.position
                    if callable(position):
                        position = position()
                except (AttributeError, TypeError):
                    # If we can't get the position, use (0,0)
                    position = QPointF(0, 0)
                    
                text_rect = QRectF(
                    position.x(), 
                    position.y() - text_height, 
                    text_width, 
                    text_height
                )
            
            scene_rect = item.mapRectToScene(text_rect)
            painter.drawRect(scene_rect)
        
        elif isinstance(item, ImageElement):
            # Draw the image bounding box
            painter.setPen(hit_pen)
            painter.setBrush(QBrush())  # No fill
            scene_rect = item.mapRectToScene(item.rect)
            painter.drawRect(scene_rect)

def test_hit_detection(element, test_points):
    """
    Test hit detection for an element with multiple test points.
    
    Args:
        element: The element to test
        test_points: List of (QPointF, expected_result) tuples in scene coordinates
        
    Returns:
        (passed, failed) counts
    """
    passed = 0
    failed = 0
    
    for point, expected in test_points:
        result = is_element_hit(element, point)
        if result == expected:
            passed += 1
            print(f"PASS: Point {point.x():.1f},{point.y():.1f} - {'Hit' if result else 'Miss'}")
        else:
            failed += 1
            print(f"FAIL: Point {point.x():.1f},{point.y():.1f} - Expected {'Hit' if expected else 'Miss'}, got {'Hit' if result else 'Miss'}")
    
    return passed, failed 