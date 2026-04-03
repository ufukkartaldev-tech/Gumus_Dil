# -*- coding: utf-8 -*-
"""
GümüşHafıza Memory Models
Core data structures for memory visualization
"""

import time
from typing import List, Dict, Optional


class MemoryBlock3D:
    """
    3D Memory Block representation - The building blocks of memory visualization
    """
    def __init__(self, address: str, size: int, var_type: str, value: str, name: str):
        self.address = address
        self.size = size
        self.var_type = var_type
        self.value = value
        self.name = name
        
        # 3D positioning
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        
        # Visual properties
        self.color = self._get_type_color()
        
        # Behavioral properties
        self.connections: List[str] = []  # For pointer visualization
        self.access_count = 0
        self.last_access = time.time()
        
    def _get_type_color(self) -> str:
        """Get color based on variable type"""
        colors = {
            "int": "#3b82f6",      # Blue
            "uzun": "#2563eb",     # Dark blue
            "kısa": "#60a5fa",     # Light blue
            "float": "#10b981",    # Green  
            "ondalık": "#059669",  # Dark green
            "string": "#f59e0b",   # Amber
            "metin": "#d97706",    # Dark amber
            "bool": "#8b5cf6",     # Purple
            "doğru": "#7c3aed",    # Dark purple
            "yanlış": "#a855f7",   # Light purple
            "list": "#ec4899",     # Pink
            "liste": "#db2777",    # Dark pink
            "map": "#f97316",      # Orange
            "harita": "#ea580c",   # Dark orange
            "dict": "#fb923c",     # Light orange
            "class": "#a855f7",    # Violet
            "sınıf": "#9333ea",    # Dark violet
            "object": "#c084fc",   # Light violet
            "nesne": "#a78bfa",    # Medium violet
            "pointer": "#06b6d4",  # Cyan
            "işaretçi": "#0891b2", # Dark cyan
            "ref": "#22d3ee",      # Light cyan
            "referans": "#0e7490", # Very dark cyan
            "null": "#6b7280",     # Gray
            "boş": "#4b5563",      # Dark gray
            "void": "#374151",     # Very dark gray
            "hiç": "#1f2937"       # Almost black
        }
        return colors.get(self.var_type.lower(), "#64748b")
        
    def add_connection(self, target_address: str):
        """Add pointer connection to another memory block"""
        if target_address not in self.connections:
            self.connections.append(target_address)
            
    def remove_connection(self, target_address: str):
        """Remove pointer connection"""
        if target_address in self.connections:
            self.connections.remove(target_address)
            
    def access(self):
        """Record memory access for heat mapping"""
        self.access_count += 1
        self.last_access = time.time()
        
    def get_heat_factor(self) -> float:
        """Calculate heat factor for visualization (0.0 to 1.0)"""
        return min(self.access_count / 10.0, 1.0)
        
    def is_hot(self) -> bool:
        """Check if this is a frequently accessed variable"""
        return self.access_count > 5
        
    def __repr__(self) -> str:
        return f"MemoryBlock3D({self.name}@{self.address}, {self.var_type}, {self.size}B)"


class GumusDilTypeSystem:
    """
    Interface to GümüşDil's native type system for accurate size calculation
    """
    
    @staticmethod
    def get_type_size(var_type: str, value: str = "", compiler_context=None) -> int:
        """
        Get accurate type size from GümüşDil compiler's type system
        Falls back to estimates if compiler context unavailable
        """
        
        # Try to get from compiler context first
        if compiler_context and hasattr(compiler_context, 'get_type_size'):
            try:
                return compiler_context.get_type_size(var_type, value)
            except:
                pass  # Fall back to estimates
        
        # GümüşDil native type sizes (based on C++ backend)
        native_sizes = {
            # Primitive types (from C++ implementation)
            "int": 4,           # 32-bit integer
            "uzun": 8,          # 64-bit long
            "kısa": 2,          # 16-bit short  
            "float": 8,         # 64-bit double precision
            "ondalık": 8,       # Same as float
            "bool": 1,          # Boolean
            "doğru": 1,         # Boolean true
            "yanlış": 1,        # Boolean false
            "char": 1,          # Single character
            "karakter": 1,      # Turkish char
            
            # Complex types
            "string": GumusDilTypeSystem._calculate_string_size(value),
            "metin": GumusDilTypeSystem._calculate_string_size(value),
            "list": GumusDilTypeSystem._calculate_list_size(value),
            "liste": GumusDilTypeSystem._calculate_list_size(value),
            "map": GumusDilTypeSystem._calculate_map_size(value),
            "harita": GumusDilTypeSystem._calculate_map_size(value),
            "dict": GumusDilTypeSystem._calculate_map_size(value),
            
            # Object types
            "class": 16,        # Base object overhead
            "sınıf": 16,        # Turkish class
            "object": 16,       # Object overhead
            "nesne": 16,        # Turkish object
            
            # Pointer types
            "pointer": 8,       # 64-bit pointer
            "işaretçi": 8,      # Turkish pointer
            "ref": 8,           # Reference
            "referans": 8,      # Turkish reference
            
            # Special types
            "null": 0,          # Null pointer
            "boş": 0,           # Turkish null
            "void": 0,          # Void type
            "hiç": 0,           # Turkish void
        }
        
        # Get size with fallback
        return native_sizes.get(var_type.lower(), 8)  # Default 8 bytes
    
    @staticmethod
    def _calculate_string_size(value: str) -> int:
        """Calculate string size including UTF-8 encoding and null terminator"""
        if not value:
            return 1  # Just null terminator
        
        # UTF-8 encoding can use 1-4 bytes per character
        # Turkish characters (ğ, ü, ş, ı, ö, ç) use 2 bytes in UTF-8
        utf8_size = 0
        for char in value:
            if ord(char) < 128:
                utf8_size += 1  # ASCII
            elif ord(char) < 2048:
                utf8_size += 2  # Turkish chars, most Unicode
            elif ord(char) < 65536:
                utf8_size += 3  # Most Unicode
            else:
                utf8_size += 4  # Rare Unicode
                
        return utf8_size + 1 + 8  # +1 for null terminator, +8 for string object overhead
    
    @staticmethod
    def _calculate_list_size(value: str) -> int:
        """Calculate list size based on estimated element count"""
        if not value or value in ["[]", "boş"]:
            return 24  # Empty list overhead (vector in C++)
        
        # Estimate element count from string representation
        element_count = value.count(',') + 1 if ',' in value else 1
        
        # List overhead + (element_count * average_element_size)
        return 24 + (element_count * 8)  # 8 bytes per element pointer
    
    @staticmethod
    def _calculate_map_size(value: str) -> int:
        """Calculate map/dictionary size based on key-value pairs"""
        if not value or value in ["{}", "boş"]:
            return 48  # Empty map overhead (std::unordered_map in C++)
        
        # Estimate key-value pair count
        pair_count = value.count(':') if ':' in value else 1
        
        # Map overhead + (pair_count * (key_size + value_size + node_overhead))
        return 48 + (pair_count * 32)  # 32 bytes per key-value pair average
    
    @staticmethod
    def get_type_category(var_type: str) -> str:
        """Get type category for visualization grouping"""
        categories = {
            # Stack types (primitive)
            "stack": ["int", "uzun", "kısa", "float", "ondalık", "bool", 
                     "doğru", "yanlış", "char", "karakter"],
            
            # Heap types (complex)
            "heap": ["string", "metin", "list", "liste", "map", "harita", 
                    "dict", "class", "sınıf", "object", "nesne"],
            
            # Pointer types
            "pointer": ["pointer", "işaretçi", "ref", "referans"],
            
            # Special types
            "special": ["null", "boş", "void", "hiç"]
        }
        
        var_type_lower = var_type.lower()
        for category, types in categories.items():
            if var_type_lower in types:
                return category
        
        return "heap"  # Default to heap for unknown types
    
    @staticmethod
    def is_stack_type(var_type: str) -> bool:
        """Check if type should be allocated on stack"""
        return GumusDilTypeSystem.get_type_category(var_type) == "stack"
    
    @staticmethod
    def is_pointer_type(var_type: str) -> bool:
        """Check if type is a pointer/reference"""
        return GumusDilTypeSystem.get_type_category(var_type) == "pointer"


class PerformanceMetrics:
    """
    Performance tracking for memory visualization
    """
    def __init__(self):
        self.memory_data = {
            "total_allocations": 0,
            "total_deallocations": 0,
            "peak_memory": 0,
            "current_memory": 0,
            "gc_cycles": 0
        }
        
        self.rendering_data = {
            "total_renders": 0,
            "full_redraws": 0,
            "incremental_updates": 0,
            "blocks_updated": 0
        }
        
    def record_allocation(self, size: int):
        """Record memory allocation"""
        self.memory_data["total_allocations"] += 1
        self.memory_data["current_memory"] += size
        self.memory_data["peak_memory"] = max(
            self.memory_data["peak_memory"], 
            self.memory_data["current_memory"]
        )
        
    def record_deallocation(self, size: int):
        """Record memory deallocation"""
        self.memory_data["total_deallocations"] += 1
        self.memory_data["current_memory"] = max(0, self.memory_data["current_memory"] - size)
        
    def record_gc_cycle(self):
        """Record garbage collection cycle"""
        self.memory_data["gc_cycles"] += 1
        
    def record_render(self, is_full_redraw: bool = False, blocks_updated: int = 0):
        """Record rendering operation"""
        self.rendering_data["total_renders"] += 1
        
        if is_full_redraw:
            self.rendering_data["full_redraws"] += 1
        else:
            self.rendering_data["incremental_updates"] += 1
            self.rendering_data["blocks_updated"] += blocks_updated
            
    def get_efficiency_percentage(self) -> float:
        """Calculate rendering efficiency percentage"""
        total = self.rendering_data["total_renders"]
        if total == 0:
            return 100.0
        
        incremental = self.rendering_data["incremental_updates"]
        return (incremental / total) * 100.0
        
    def get_memory_efficiency(self) -> float:
        """Calculate memory usage efficiency"""
        peak = self.memory_data["peak_memory"]
        if peak == 0:
            return 100.0
            
        current = self.memory_data["current_memory"]
        return (current / peak) * 100.0
        
    def reset(self):
        """Reset all metrics"""
        self.memory_data = {
            "total_allocations": 0,
            "total_deallocations": 0,
            "peak_memory": 0,
            "current_memory": 0,
            "gc_cycles": 0
        }
        
        self.rendering_data = {
            "total_renders": 0,
            "full_redraws": 0,
            "incremental_updates": 0,
            "blocks_updated": 0
        }
        
    def get_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        return {
            "memory_performance": self.memory_data.copy(),
            "rendering_performance": self.rendering_data.copy(),
            "efficiency_metrics": {
                "rendering_efficiency": self.get_efficiency_percentage(),
                "memory_efficiency": self.get_memory_efficiency()
            }
        }