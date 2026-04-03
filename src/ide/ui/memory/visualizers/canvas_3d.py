# -*- coding: utf-8 -*-
"""
GümüşHafıza 3D Canvas
High-performance 3D memory visualization with incremental rendering
"""

import tkinter as tk
from tkinter import Canvas
import math
from typing import Dict, List, Tuple, Set
from ..memory_models import MemoryBlock3D, PerformanceMetrics


class MemoryCanvas3D(Canvas):
    """
    High-performance 3D-like memory visualization canvas with incremental updates
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="#0f172a", highlightthickness=0)
        
        # Memory block storage
        self.blocks: Dict[str, MemoryBlock3D] = {}
        self.stack_blocks: List[MemoryBlock3D] = []
        self.heap_blocks: List[MemoryBlock3D] = []
        
        # Performance optimization: Track what needs redrawing
        self.dirty_blocks: Set[str] = set()  # Blocks that need redrawing
        self.dirty_connections: Set[Tuple[str, str]] = set()  # Connections that need redrawing
        self.full_redraw_needed = True  # Force full redraw on first render
        
        # Canvas object tracking for incremental updates
        self.block_canvas_objects: Dict[str, List[int]] = {}  # address -> list of canvas object IDs
        self.connection_canvas_objects: Dict[Tuple[str, str], int] = {}  # (source, target) -> canvas object ID
        
        # 3D projection parameters
        self.camera_angle = 45.0
        self.camera_height = 0.5
        self.zoom = 1.0
        
        # Performance metrics
        self.metrics = PerformanceMetrics()
        
        # Animation state
        self.animation_running = False
        
        # Bind mouse events for interaction
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<MouseWheel>", self.on_zoom)
        
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        
    def project_3d(self, x: float, y: float, z: float) -> Tuple[float, float]:
        """Project 3D coordinates to 2D canvas using isometric projection"""
        # Simple isometric projection with camera controls
        angle_rad = math.radians(self.camera_angle)
        
        # Rotate around Y axis
        x_rot = x * math.cos(angle_rad) - z * math.sin(angle_rad)
        z_rot = x * math.sin(angle_rad) + z * math.cos(angle_rad)
        
        # Apply camera height and zoom
        y_adjusted = y + self.camera_height * z_rot
        
        # Project to 2D canvas coordinates
        canvas_x = (x_rot * 50 + self.winfo_width() / 2) * self.zoom
        canvas_y = (y_adjusted * 30 + z_rot * 20 + self.winfo_height() / 2) * self.zoom
        
        return canvas_x, canvas_y
        
    def add_memory_block(self, block: MemoryBlock3D, is_stack: bool = True):
        """Add a memory block to visualization with incremental update"""
        # Check if block already exists
        if block.address in self.blocks:
            old_block = self.blocks[block.address]
            # If value changed, mark for update
            if (old_block.value != block.value or 
                old_block.access_count != block.access_count or
                old_block.size != block.size):
                self.dirty_blocks.add(block.address)
        else:
            # New block
            self.dirty_blocks.add(block.address)
        
        self.blocks[block.address] = block
        
        # Position the block
        if is_stack:
            if block not in self.stack_blocks:
                block.x = 0
                block.y = len(self.stack_blocks)
                block.z = 0
                self.stack_blocks.append(block)
        else:
            if block not in self.heap_blocks:
                # Heap blocks arranged in a grid
                heap_count = len(self.heap_blocks)
                block.x = (heap_count % 8) - 4
                block.y = -(heap_count // 8) - 1
                block.z = 2
                self.heap_blocks.append(block)
                
        # Incremental redraw instead of full redraw
        self.incremental_redraw()
        
    def remove_memory_block(self, address: str):
        """Remove a memory block with incremental update"""
        if address in self.blocks:
            # Remove canvas objects for this block
            if address in self.block_canvas_objects:
                for obj_id in self.block_canvas_objects[address]:
                    self.delete(obj_id)
                del self.block_canvas_objects[address]
            
            block = self.blocks[address]
            
            # Remove from appropriate list and reposition
            if block in self.stack_blocks:
                self.stack_blocks.remove(block)
                # Reposition remaining stack blocks
                for i, stack_block in enumerate(self.stack_blocks):
                    if stack_block.y != i:
                        stack_block.y = i
                        self.dirty_blocks.add(stack_block.address)
                        
            elif block in self.heap_blocks:
                self.heap_blocks.remove(block)
                # Reposition remaining heap blocks
                for i, heap_block in enumerate(self.heap_blocks):
                    new_x = (i % 8) - 4
                    new_y = -(i // 8) - 1
                    if heap_block.x != new_x or heap_block.y != new_y:
                        heap_block.x = new_x
                        heap_block.y = new_y
                        self.dirty_blocks.add(heap_block.address)
                    
            del self.blocks[address]
            self.incremental_redraw()
            
    def incremental_redraw(self):
        """High-performance incremental redraw - only update changed elements"""
        # If camera moved or full redraw needed, do complete redraw
        if self.full_redraw_needed:
            self.full_redraw()
            return
            
        # Update only dirty blocks
        if self.dirty_blocks:
            blocks_updated = len(self.dirty_blocks)
            self.metrics.record_render(is_full_redraw=False, blocks_updated=blocks_updated)
            
            for address in self.dirty_blocks:
                if address in self.blocks:
                    self._update_single_block(self.blocks[address])
                    
            self.dirty_blocks.clear()
            
        # Update dirty connections
        if self.dirty_connections:
            self._update_connections()
            self.dirty_connections.clear()
            
    def _update_single_block(self, block: MemoryBlock3D):
        """Update a single memory block efficiently"""
        # Remove old canvas objects for this block
        if block.address in self.block_canvas_objects:
            for obj_id in self.block_canvas_objects[block.address]:
                self.delete(obj_id)
                
        # Redraw the block
        self.block_canvas_objects[block.address] = []
        self._draw_memory_block(block)
        
    def full_redraw(self):
        """Complete redraw - use only when necessary (camera changes, etc.)"""
        self.metrics.record_render(is_full_redraw=True)
        self.delete("all")
        
        # Clear tracking
        self.block_canvas_objects.clear()
        self.connection_canvas_objects.clear()
        
        # Draw coordinate system
        self._draw_axes()
        
        # Draw section labels
        self._draw_section_label("STACK", -200, 50, "#3b82f6")
        self._draw_section_label("HEAP", 200, 50, "#ec4899")
        
        # Draw all memory blocks (sorted by depth for proper rendering)
        all_blocks = sorted(self.blocks.values(), key=lambda b: b.z)
        for block in all_blocks:
            self.block_canvas_objects[block.address] = []
            self._draw_memory_block(block)
            
        # Draw pointer connections
        self._draw_connections()
        
        self.full_redraw_needed = False
        self.dirty_blocks.clear()
        self.dirty_connections.clear()
        
    def redraw(self):
        """Legacy method - now uses incremental redraw"""
        self.incremental_redraw()
        
    def _draw_axes(self):
        """Draw 3D coordinate axes for reference"""
        # X axis (red)
        x1, y1 = self.project_3d(-5, 0, 0)
        x2, y2 = self.project_3d(5, 0, 0)
        self.create_line(x1, y1, x2, y2, fill="#ef4444", width=2, tags="axis")
        
        # Y axis (green)
        x1, y1 = self.project_3d(0, -5, 0)
        x2, y2 = self.project_3d(0, 5, 0)
        self.create_line(x1, y1, x2, y2, fill="#22c55e", width=2, tags="axis")
        
        # Z axis (blue)
        x1, y1 = self.project_3d(0, 0, -5)
        x2, y2 = self.project_3d(0, 0, 5)
        self.create_line(x1, y1, x2, y2, fill="#3b82f6", width=2, tags="axis")
        
    def _draw_section_label(self, text: str, x: int, y: int, color: str):
        """Draw section labels for stack/heap regions"""
        self.create_text(x, y, text=text, fill=color, font=("Consolas", 14, "bold"))
        
    def _draw_memory_block(self, block: MemoryBlock3D):
        """Draw a single memory block in 3D with object tracking"""
        # Calculate heat color based on access frequency
        heat_factor = block.get_heat_factor()
        base_color = block.color
        
        # Convert hex to RGB
        r = int(base_color[1:3], 16) / 255.0
        g = int(base_color[3:5], 16) / 255.0
        b = int(base_color[5:7], 16) / 255.0
        
        # Add heat effect (more red = more accessed)
        r = min(r + heat_factor * 0.3, 1.0)
        
        # Convert back to hex
        heat_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        
        # Draw 3D cube and track canvas objects
        cube_objects = self._draw_cube(block.x, block.y, block.z, 0.8, heat_color, block)
        
        # Store canvas object IDs for this block
        if block.address not in self.block_canvas_objects:
            self.block_canvas_objects[block.address] = []
        self.block_canvas_objects[block.address].extend(cube_objects)
        
    def _draw_cube(self, x: float, y: float, z: float, size: float, color: str, block: MemoryBlock3D) -> List[int]:
        """Draw a 3D cube representing a memory block, return canvas object IDs"""
        canvas_objects = []
        
        # Define cube vertices
        vertices = [
            (x - size/2, y - size/2, z - size/2),  # 0: bottom-left-back
            (x + size/2, y - size/2, z - size/2),  # 1: bottom-right-back
            (x + size/2, y + size/2, z - size/2),  # 2: top-right-back
            (x - size/2, y + size/2, z - size/2),  # 3: top-left-back
            (x - size/2, y - size/2, z + size/2),  # 4: bottom-left-front
            (x + size/2, y - size/2, z + size/2),  # 5: bottom-right-front
            (x + size/2, y + size/2, z + size/2),  # 6: top-right-front
            (x - size/2, y + size/2, z + size/2),  # 7: top-left-front
        ]
        
        # Project vertices to 2D
        projected = [self.project_3d(vx, vy, vz) for vx, vy, vz in vertices]
        
        # Draw faces (back to front for proper depth)
        faces = [
            ([0, 1, 2, 3], 0.6),  # Back face (darker)
            ([4, 7, 6, 5], 1.0),  # Front face (brightest)
            ([0, 4, 5, 1], 0.8),  # Bottom face
            ([3, 2, 6, 7], 0.8),  # Top face
            ([0, 3, 7, 4], 0.7),  # Left face
            ([1, 5, 6, 2], 0.7),  # Right face
        ]
        
        for face_indices, brightness in faces:
            face_points = []
            for i in face_indices:
                face_points.extend(projected[i])
                
            # Adjust color brightness for 3D effect
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            r = int(r * brightness)
            g = int(g * brightness)
            b = int(b * brightness)
            
            face_color = f"#{r:02x}{g:02x}{b:02x}"
            
            obj_id = self.create_polygon(
                face_points,
                fill=face_color,
                outline="#ffffff",
                width=1,
                tags=f"block_{block.address}"
            )
            canvas_objects.append(obj_id)
            
        # Add text label
        center_x, center_y = self.project_3d(x, y + size/2 + 0.3, z)
        label_id = self.create_text(
            center_x, center_y,
            text=f"{block.name}\n{block.value[:10]}",
            fill="white",
            font=("Consolas", 8),
            tags=f"label_{block.address}"
        )
        canvas_objects.append(label_id)
        
        return canvas_objects
        
    def _update_connections(self):
        """Update pointer connections efficiently"""
        # Clear old connections
        for obj_id in self.connection_canvas_objects.values():
            self.delete(obj_id)
        self.connection_canvas_objects.clear()
        
        # Redraw all connections
        self._draw_connections()
        
    def _draw_connections(self):
        """Draw pointer connections between memory blocks"""
        for block in self.blocks.values():
            for target_addr in block.connections:
                if target_addr in self.blocks:
                    target = self.blocks[target_addr]
                    
                    # Draw arrow from source to target
                    x1, y1 = self.project_3d(block.x, block.y, block.z)
                    x2, y2 = self.project_3d(target.x, target.y, target.z)
                    
                    connection_key = (block.address, target_addr)
                    obj_id = self.create_line(
                        x1, y1, x2, y2,
                        fill="#06b6d4",
                        width=2,
                        arrow=tk.LAST,
                        arrowshape=(10, 12, 3),
                        tags="connection"
                    )
                    self.connection_canvas_objects[connection_key] = obj_id
                    
    def on_click(self, event):
        """Handle mouse click"""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        
    def on_drag(self, event):
        """Handle mouse drag for camera rotation with optimized redraw"""
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        
        self.camera_angle += dx * 0.5
        self.camera_height += dy * 0.01
        
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        
        # Camera changed - need full redraw
        self.full_redraw_needed = True
        self.full_redraw()
        
    def on_zoom(self, event):
        """Handle mouse wheel for zooming with optimized redraw"""
        if event.delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom *= 0.9
            
        self.zoom = max(0.1, min(self.zoom, 3.0))
        
        # Camera changed - need full redraw
        self.full_redraw_needed = True
        self.full_redraw()
        
    def animate_access(self, address: str):
        """Animate memory access with flash effect"""
        if address in self.blocks:
            block = self.blocks[address]
            block.access()
            
            # Flash effect
            original_color = block.color
            block.color = "#ffffff"
            self.dirty_blocks.add(address)
            self.incremental_redraw()
            
            def restore_color():
                block.color = original_color
                self.dirty_blocks.add(address)
                self.incremental_redraw()
                
            self.after(200, restore_color)
            
    def reset_view(self):
        """Reset camera to default position"""
        self.camera_angle = 45.0
        self.camera_height = 0.5
        self.zoom = 1.0
        self.full_redraw_needed = True
        self.full_redraw()
        
    def clear_all(self):
        """Clear all memory blocks and reset canvas"""
        self.blocks.clear()
        self.stack_blocks.clear()
        self.heap_blocks.clear()
        self.block_canvas_objects.clear()
        self.connection_canvas_objects.clear()
        self.dirty_blocks.clear()
        self.dirty_connections.clear()
        self.full_redraw_needed = True
        self.delete("all")
        
    def get_render_stats(self) -> dict:
        """Get rendering performance statistics"""
        return self.metrics.rendering_data.copy()
        
    def get_block_count(self) -> dict:
        """Get block count statistics"""
        return {
            "total_blocks": len(self.blocks),
            "stack_blocks": len(self.stack_blocks),
            "heap_blocks": len(self.heap_blocks),
            "hot_blocks": sum(1 for block in self.blocks.values() if block.is_hot())
        }