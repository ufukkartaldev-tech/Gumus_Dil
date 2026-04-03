# -*- coding: utf-8 -*-
"""
GümüşHafıza Memory Visualization System
Modular, high-performance memory visualization for GümüşDil
"""

# Main orchestrator - the public interface
from .gumus_hafiza_main import GumusHafizaMain, MemoryViewV3

# Core data models
from .memory_models import MemoryBlock3D, GumusDilTypeSystem, PerformanceMetrics

# Business logic engine
from .memory_engine import MemoryDataProcessor, MemoryFilter, MemoryAnalyzer

# Visualization components
from .visualizers.canvas_3d import MemoryCanvas3D
from .visualizers.memory_card import MemoryCard

__all__ = [
    # Main interface
    'GumusHafizaMain',
    'MemoryViewV3',  # Backward compatibility
    
    # Core models
    'MemoryBlock3D',
    'GumusDilTypeSystem', 
    'PerformanceMetrics',
    
    # Engine components
    'MemoryDataProcessor',
    'MemoryFilter',
    'MemoryAnalyzer',
    
    # Visualizers
    'MemoryCanvas3D',
    'MemoryCard'
]

# Version info
__version__ = "3.0.0"
__author__ = "GümüşDil Team"
__description__ = "Advanced memory visualization system with 3D rendering and performance analytics"