"""
File-related actions and enums.
"""
from enum import Enum, auto

class ExportFormat(Enum):
    """Supported export formats."""
    PNG = auto()
    JPG = auto()
    PDF = auto()
    SVG = auto() 