# -*- coding: utf-8 -*-
"""
GümüşHafıza Memory Engine
Core business logic for memory data processing, filtering, and analysis
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from .memory_models import GumusDilTypeSystem, PerformanceMetrics


class MemoryDataProcessor:
    """
    Core engine for processing memory data from GümüşDil runtime
    """
    
    def __init__(self):
        self.performance_metrics = PerformanceMetrics()
        self._last_var_count = 0
        self._start_time = None
        
    def process_memory_json(self, memory_json: str) -> Dict[str, Any]:
        """
        Process raw memory JSON from GümüşDil runtime
        Returns structured memory data with enhanced information
        """
        try:
            raw_data = json.loads(memory_json)
            
            # Add timestamp
            raw_data["timestamp"] = time.time()
            
            # Process and enhance the data
            processed_data = self._enhance_memory_data(raw_data)
            
            # Update performance metrics
            self._update_performance_metrics(processed_data)
            
            return processed_data
            
        except Exception as e:
            print(f"❌ Memory JSON processing error: {e}")
            return {}
            
    def _enhance_memory_data(self, raw_data: Dict) -> Dict[str, Any]:
        """
        Enhance raw memory data with type system information
        """
        enhanced_data = raw_data.copy()
        
        # Collect and enhance variables
        variables = self._collect_variables(raw_data)
        enhanced_variables = {}
        
        for name, info in variables.items():
            var_type = info.get("type", "unknown")
            var_value = info.get("value", "")
            
            # Use GümüşDil native type system for accurate sizing
            accurate_size = GumusDilTypeSystem.get_type_size(var_type, var_value)
            type_category = GumusDilTypeSystem.get_type_category(var_type)
            
            # Enhanced variable info with native type data
            enhanced_info = {
                "value": var_value,
                "type": var_type,
                "address": info.get("address", f"0x{hash(name) & 0xFFFFFF:06x}"),
                "size": accurate_size,
                "access_count": info.get("access_count", 0),
                "scope_depth": info.get("scope_depth", 0),
                "points_to": info.get("points_to"),
                "type_category": type_category,
                "is_stack": type_category == "stack",
                "memory_region": "stack" if type_category == "stack" else "heap",
                "is_pointer": GumusDilTypeSystem.is_pointer_type(var_type),
                "heat_level": self._calculate_heat_level(info.get("access_count", 0))
            }
            enhanced_variables[name] = enhanced_info
            
        enhanced_data["enhanced_variables"] = enhanced_variables
        return enhanced_data
        
    def _collect_variables(self, scope_data: Dict, depth: int = 0) -> Dict[str, Any]:
        """
        Recursively collect variables from all scopes
        """
        variables = {}
        
        def traverse(scope, current_depth=0):
            if not scope:
                return
                
            # Current scope variables
            for name, info in scope.get("variables", {}).items():
                # Add scope depth information
                var_info = info.copy()
                var_info["scope_depth"] = current_depth
                variables[name] = var_info
                
            # Traverse parent scope
            traverse(scope.get("parent"), current_depth + 1)
            
        traverse(scope_data, depth)
        return variables
        
    def _calculate_heat_level(self, access_count: int) -> str:
        """Calculate heat level based on access count"""
        if access_count > 10:
            return "hot"
        elif access_count > 5:
            return "warm"
        elif access_count > 0:
            return "cool"
        else:
            return "cold"
            
    def _update_performance_metrics(self, data: Dict):
        """Update performance tracking metrics"""
        variables = data.get("enhanced_variables", {})
        current_count = len(variables)
        
        # Track allocations/deallocations
        if hasattr(self, '_last_var_count'):
            if current_count > self._last_var_count:
                diff = current_count - self._last_var_count
                for _ in range(diff):
                    self.performance_metrics.record_allocation(8)  # Average size
            elif current_count < self._last_var_count:
                diff = self._last_var_count - current_count
                for _ in range(diff):
                    self.performance_metrics.record_deallocation(8)
                    
        self._last_var_count = current_count
        
        # Calculate total memory usage
        total_size = sum(var.get("size", 8) for var in variables.values())
        self.performance_metrics.memory_data["current_memory"] = total_size
        self.performance_metrics.memory_data["peak_memory"] = max(
            self.performance_metrics.memory_data["peak_memory"], 
            total_size
        )
        
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        return self.performance_metrics.get_summary()


class MemoryFilter:
    """
    Advanced filtering and searching for memory variables
    """
    
    @staticmethod
    def apply_filters(variables: Dict[str, Any], 
                     search_term: str = "", 
                     type_filter: str = "All Types",
                     sort_option: str = "Name",
                     heat_filter: str = "All") -> Dict[str, Any]:
        """
        Apply comprehensive filtering to memory variables
        """
        filtered = {}
        
        # Search filter
        for name, info in variables.items():
            if search_term and search_term.lower() not in name.lower():
                continue
                
            # Type filter
            if type_filter != "All Types" and info.get("type", "").lower() != type_filter.lower():
                continue
                
            # Heat filter
            if heat_filter != "All":
                heat_level = info.get("heat_level", "cold")
                if heat_filter.lower() != heat_level:
                    continue
                    
            filtered[name] = info
            
        # Apply sorting
        return MemoryFilter._sort_variables(filtered, sort_option)
        
    @staticmethod
    def _sort_variables(variables: Dict[str, Any], sort_option: str) -> Dict[str, Any]:
        """Sort variables based on the specified option"""
        if sort_option == "Name":
            return dict(sorted(variables.items()))
        elif sort_option == "Type":
            return dict(sorted(variables.items(), key=lambda x: x[1].get("type", "")))
        elif sort_option == "Size":
            return dict(sorted(variables.items(), key=lambda x: x[1].get("size", 0), reverse=True))
        elif sort_option == "Access Count":
            return dict(sorted(variables.items(), key=lambda x: x[1].get("access_count", 0), reverse=True))
        elif sort_option == "Address":
            return dict(sorted(variables.items(), key=lambda x: x[1].get("address", "")))
        elif sort_option == "Scope Depth":
            return dict(sorted(variables.items(), key=lambda x: x[1].get("scope_depth", 0)))
        else:
            return variables
            
    @staticmethod
    def search_by_pattern(variables: Dict[str, Any], pattern: str) -> Dict[str, Any]:
        """Search variables using regex pattern"""
        import re
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            return {name: info for name, info in variables.items() 
                   if regex.search(name) or regex.search(str(info.get("value", "")))}
        except re.error:
            # Fallback to simple string search
            return {name: info for name, info in variables.items() 
                   if pattern.lower() in name.lower() or pattern.lower() in str(info.get("value", "")).lower()}
            
    @staticmethod
    def get_hot_variables(variables: Dict[str, Any], threshold: int = 5) -> Dict[str, Any]:
        """Get frequently accessed (hot) variables"""
        return {name: info for name, info in variables.items() 
               if info.get("access_count", 0) > threshold}
               
    @staticmethod
    def get_large_variables(variables: Dict[str, Any], size_threshold: int = 100) -> Dict[str, Any]:
        """Get variables larger than specified size"""
        return {name: info for name, info in variables.items() 
               if info.get("size", 0) > size_threshold}
               
    @staticmethod
    def get_pointer_variables(variables: Dict[str, Any]) -> Dict[str, Any]:
        """Get all pointer/reference variables"""
        return {name: info for name, info in variables.items() 
               if info.get("is_pointer", False)}


class MemoryAnalyzer:
    """
    Advanced analysis and insights for memory usage patterns
    """
    
    @staticmethod
    def analyze_memory_usage(variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive memory usage analysis
        """
        if not variables:
            return {}
            
        # Basic statistics
        total_variables = len(variables)
        total_size = sum(var.get("size", 0) for var in variables.values())
        
        # Type distribution
        type_distribution = {}
        for var in variables.values():
            var_type = var.get("type", "unknown")
            type_distribution[var_type] = type_distribution.get(var_type, 0) + 1
            
        # Memory region distribution
        stack_vars = [v for v in variables.values() if v.get("is_stack", False)]
        heap_vars = [v for v in variables.values() if not v.get("is_stack", True)]
        
        stack_size = sum(var.get("size", 0) for var in stack_vars)
        heap_size = sum(var.get("size", 0) for var in heap_vars)
        
        # Access pattern analysis
        hot_vars = [v for v in variables.values() if v.get("access_count", 0) > 5]
        cold_vars = [v for v in variables.values() if v.get("access_count", 0) == 0]
        
        # Scope analysis
        scope_distribution = {}
        for var in variables.values():
            depth = var.get("scope_depth", 0)
            scope_distribution[depth] = scope_distribution.get(depth, 0) + 1
            
        return {
            "basic_stats": {
                "total_variables": total_variables,
                "total_size": total_size,
                "average_size": total_size / max(total_variables, 1)
            },
            "type_distribution": type_distribution,
            "memory_regions": {
                "stack": {"count": len(stack_vars), "size": stack_size},
                "heap": {"count": len(heap_vars), "size": heap_size}
            },
            "access_patterns": {
                "hot_variables": len(hot_vars),
                "cold_variables": len(cold_vars),
                "access_ratio": len(hot_vars) / max(total_variables, 1)
            },
            "scope_distribution": scope_distribution,
            "largest_variables": sorted(
                [(name, var.get("size", 0)) for name, var in variables.items()],
                key=lambda x: x[1], reverse=True
            )[:5],
            "most_accessed": sorted(
                [(name, var.get("access_count", 0)) for name, var in variables.items()],
                key=lambda x: x[1], reverse=True
            )[:5]
        }
        
    @staticmethod
    def detect_memory_leaks(history: List[Dict]) -> List[Dict]:
        """
        Detect potential memory leaks from history
        """
        if len(history) < 10:
            return []
            
        leaks = []
        
        # Analyze memory growth over time
        memory_sizes = []
        for step in history[-10:]:  # Last 10 steps
            variables = step.get("enhanced_variables", {})
            total_size = sum(var.get("size", 0) for var in variables.values())
            memory_sizes.append(total_size)
            
        # Check for consistent growth
        if len(memory_sizes) >= 5:
            growth_trend = all(memory_sizes[i] <= memory_sizes[i+1] for i in range(len(memory_sizes)-1))
            if growth_trend and memory_sizes[-1] > memory_sizes[0] * 1.5:
                leaks.append({
                    "type": "consistent_growth",
                    "description": "Memory usage consistently growing",
                    "growth_factor": memory_sizes[-1] / max(memory_sizes[0], 1)
                })
                
        return leaks
        
    @staticmethod
    def suggest_optimizations(analysis: Dict) -> List[str]:
        """
        Suggest memory optimizations based on analysis
        """
        suggestions = []
        
        # Check stack/heap ratio
        stack_size = analysis.get("memory_regions", {}).get("stack", {}).get("size", 0)
        heap_size = analysis.get("memory_regions", {}).get("heap", {}).get("size", 0)
        
        if heap_size > stack_size * 3:
            suggestions.append("Consider using more stack-allocated variables for better performance")
            
        # Check access patterns
        access_ratio = analysis.get("access_patterns", {}).get("access_ratio", 0)
        if access_ratio < 0.1:
            suggestions.append("Many variables are never accessed - consider removing unused variables")
            
        # Check large variables
        largest_vars = analysis.get("largest_variables", [])
        if largest_vars and largest_vars[0][1] > 1000:
            suggestions.append(f"Variable '{largest_vars[0][0]}' is very large ({largest_vars[0][1]}B) - consider optimization")
            
        return suggestions