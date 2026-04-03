# -*- coding: utf-8 -*-
"""
GÜMÜŞHAFİZA V3.0 - Advanced Memory Visualizer
Real-time memory tracking with 3D visualization, heap/stack separation,
pointer tracking, and performance analytics
"""

import customtkinter as ctk
import tkinter as tk
import json
import math
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable, Tuple
from tkinter import Canvas
import colorsys


class MemoryBlock3D:
    """
    3D Memory Block representation for advanced visualization
    """
    def __init__(self, address: str, size: int, var_type: str, value: str, name: str):
        self.address = address
        self.size = size
        self.var_type = var_type
        self.value = value
        self.name = name
        self.x = 0
        self.y = 0
        self.z = 0
        self.color = self._get_type_color()
        self.connections = []  # For pointer visualization
        self.access_count = 0
        self.last_access = time.time()
        
    def _get_type_color(self) -> str:
        """Get color based on variable type"""
        colors = {
            "int": "#3b82f6",      # Blue
            "float": "#10b981",    # Green  
            "string": "#f59e0b",   # Amber
            "bool": "#8b5cf6",     # Purple
            "list": "#ec4899",     # Pink
            "map": "#f97316",      # Orange
            "class": "#a855f7",    # Violet
            "pointer": "#06b6d4",  # Cyan
            "null": "#6b7280"      # Gray
        }
        return colors.get(self.var_type.lower(), "#64748b")
        
    def add_connection(self, target_address: str):
        """Add pointer connection to another memory block"""
        if target_address not in self.connections:
            self.connections.append(target_address)
            
    def access(self):
        """Record memory access for heat mapping"""
        self.access_count += 1
        self.last_access = time.time()


class MemoryCanvas3D(Canvas):
    """
    3D-like memory visualization canvas with stack/heap separation
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="#0f172a", highlightthickness=0)
        
        self.blocks: Dict[str, MemoryBlock3D] = {}
        self.stack_blocks = []
        self.heap_blocks = []
        self.animation_running = False
        
        # 3D projection parameters
        self.camera_angle = 45
        self.camera_height = 0.5
        self.zoom = 1.0
        
        # Bind mouse events for interaction
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<MouseWheel>", self.on_zoom)
        
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        
    def project_3d(self, x: float, y: float, z: float) -> Tuple[float, float]:
        """Project 3D coordinates to 2D canvas"""
        # Simple isometric projection
        angle_rad = math.radians(self.camera_angle)
        
        # Rotate around Y axis
        x_rot = x * math.cos(angle_rad) - z * math.sin(angle_rad)
        z_rot = x * math.sin(angle_rad) + z * math.cos(angle_rad)
        
        # Project to 2D
        canvas_x = (x_rot * 50 + self.winfo_width() / 2) * self.zoom
        canvas_y = (y * 30 + z_rot * 20 + self.winfo_height() / 2) * self.zoom
        
        return canvas_x, canvas_y
        
    def add_memory_block(self, block: MemoryBlock3D, is_stack: bool = True):
        """Add a memory block to visualization"""
        self.blocks[block.address] = block
        
        if is_stack:
            block.x = 0
            block.y = len(self.stack_blocks)
            block.z = 0
            self.stack_blocks.append(block)
        else:
            # Heap blocks arranged in a grid
            heap_count = len(self.heap_blocks)
            block.x = (heap_count % 8) - 4
            block.y = -(heap_count // 8) - 1
            block.z = 2
            self.heap_blocks.append(block)
            
        self.redraw()
        
    def remove_memory_block(self, address: str):
        """Remove a memory block"""
        if address in self.blocks:
            block = self.blocks[address]
            if block in self.stack_blocks:
                self.stack_blocks.remove(block)
                # Reposition remaining stack blocks
                for i, stack_block in enumerate(self.stack_blocks):
                    stack_block.y = i
            elif block in self.heap_blocks:
                self.heap_blocks.remove(block)
                # Reposition remaining heap blocks
                for i, heap_block in enumerate(self.heap_blocks):
                    heap_block.x = (i % 8) - 4
                    heap_block.y = -(i // 8) - 1
                    
            del self.blocks[address]
            self.redraw()
            
    def redraw(self):
        """Redraw the entire memory visualization"""
        self.delete("all")
        
        # Draw coordinate system
        self._draw_axes()
        
        # Draw stack section
        self._draw_section_label("STACK", -200, 50, "#3b82f6")
        
        # Draw heap section  
        self._draw_section_label("HEAP", 200, 50, "#ec4899")
        
        # Draw memory blocks
        all_blocks = sorted(self.blocks.values(), key=lambda b: b.z)
        for block in all_blocks:
            self._draw_memory_block(block)
            
        # Draw pointer connections
        self._draw_connections()
        
    def _draw_axes(self):
        """Draw 3D coordinate axes"""
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
        """Draw section labels"""
        self.create_text(x, y, text=text, fill=color, font=("Consolas", 14, "bold"))
        
    def _draw_memory_block(self, block: MemoryBlock3D):
        """Draw a single memory block in 3D"""
        # Calculate heat color based on access frequency
        heat_factor = min(block.access_count / 10.0, 1.0)
        base_color = block.color
        
        # Convert hex to RGB
        r = int(base_color[1:3], 16) / 255.0
        g = int(base_color[3:5], 16) / 255.0
        b = int(base_color[5:7], 16) / 255.0
        
        # Add heat effect (more red = more accessed)
        r = min(r + heat_factor * 0.3, 1.0)
        
        # Convert back to hex
        heat_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        
        # Draw 3D cube
        self._draw_cube(block.x, block.y, block.z, 0.8, heat_color, block)
        
    def _draw_cube(self, x: float, y: float, z: float, size: float, color: str, block: MemoryBlock3D):
        """Draw a 3D cube representing a memory block"""
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
                
            # Adjust color brightness
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            r = int(r * brightness)
            g = int(g * brightness)
            b = int(b * brightness)
            
            face_color = f"#{r:02x}{g:02x}{b:02x}"
            
            self.create_polygon(
                face_points,
                fill=face_color,
                outline="#ffffff",
                width=1,
                tags=f"block_{block.address}"
            )
            
        # Add text label
        center_x, center_y = self.project_3d(x, y + size/2 + 0.3, z)
        self.create_text(
            center_x, center_y,
            text=f"{block.name}\n{block.value[:10]}",
            fill="white",
            font=("Consolas", 8),
            tags=f"label_{block.address}"
        )
        
    def _draw_connections(self):
        """Draw pointer connections between memory blocks"""
        for block in self.blocks.values():
            for target_addr in block.connections:
                if target_addr in self.blocks:
                    target = self.blocks[target_addr]
                    
                    # Draw arrow from source to target
                    x1, y1 = self.project_3d(block.x, block.y, block.z)
                    x2, y2 = self.project_3d(target.x, target.y, target.z)
                    
                    self.create_line(
                        x1, y1, x2, y2,
                        fill="#06b6d4",
                        width=2,
                        arrow=tk.LAST,
                        arrowshape=(10, 12, 3),
                        tags="connection"
                    )
                    
    def on_click(self, event):
        """Handle mouse click"""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        
    def on_drag(self, event):
        """Handle mouse drag for camera rotation"""
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        
        self.camera_angle += dx * 0.5
        self.camera_height += dy * 0.01
        
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        
        self.redraw()
        
    def on_zoom(self, event):
        """Handle mouse wheel for zooming"""
        if event.delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom *= 0.9
            
        self.zoom = max(0.1, min(self.zoom, 3.0))
        self.redraw()
        
    def animate_access(self, address: str):
        """Animate memory access"""
        if address in self.blocks:
            block = self.blocks[address]
            block.access()
            
            # Flash effect
            original_color = block.color
            block.color = "#ffffff"
            self.redraw()
            
            def restore_color():
                block.color = original_color
                self.redraw()
                
            self.after(200, restore_color)


class MemoryCard(ctk.CTkFrame):
    """
    Enhanced memory card with performance metrics and interaction
    """
    def __init__(self, parent, var_name: str, var_value: str, var_type: str, 
                 address: str, theme: dict, size: int = 0, access_count: int = 0, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.var_name = var_name
        self.var_value = var_value
        self.var_type = var_type
        self.address = address
        self.theme = theme
        self.size = size
        self.access_count = access_count
        self.is_watched = False
        self.is_breakpoint = False
        
        # Enhanced type colors with gradients
        type_colors = {
            "int": "#3b82f6",      # Blue
            "float": "#10b981",    # Green
            "string": "#f59e0b",   # Amber
            "bool": "#8b5cf6",     # Purple
            "list": "#ec4899",     # Pink
            "map": "#f97316",      # Orange
            "class": "#a855f7",    # Violet
            "pointer": "#06b6d4",  # Cyan
            "null": "#6b7280"      # Gray
        }
        
        self.accent_color = type_colors.get(var_type.lower(), "#64748b")
        
        # Performance-based border color
        if access_count > 10:
            border_color = "#ef4444"  # Red for hot variables
        elif access_count > 5:
            border_color = "#f59e0b"  # Orange for warm variables
        else:
            border_color = self.accent_color
        
        # Main card container with enhanced styling
        self.configure(
            fg_color=("gray90", "#1a1a1a"),
            corner_radius=15,
            border_width=2,
            border_color=border_color
        )
        
        # Header with enhanced info
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(12, 8))
        
        # Left side: Variable info
        left_info = ctk.CTkFrame(header, fg_color="transparent")
        left_info.pack(side="left", fill="x", expand=True)
        
        # Variable name with type icon
        type_icons = {
            "int": "🔢", "float": "📊", "string": "📝", "bool": "✅",
            "list": "📋", "map": "🗂️", "class": "🏗️", "pointer": "➡️", "null": "⭕"
        }
        icon = type_icons.get(var_type.lower(), "❓")
        
        name_label = ctk.CTkLabel(
            left_info,
            text=f"{icon} {var_name}",
            font=("Segoe UI", 15, "bold"),
            text_color=self.accent_color,
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        # Size and access info
        info_text = f"Size: {size}B"
        if access_count > 0:
            info_text += f" • Accessed: {access_count}x"
            
        info_label = ctk.CTkLabel(
            left_info,
            text=info_text,
            font=("Consolas", 9),
            text_color=self.theme["comment"],
            anchor="w"
        )
        info_label.pack(anchor="w")
        
        # Right side: Type badge and controls
        right_controls = ctk.CTkFrame(header, fg_color="transparent")
        right_controls.pack(side="right")
        
        # Performance indicator
        if access_count > 0:
            perf_color = "#ef4444" if access_count > 10 else "#f59e0b" if access_count > 5 else "#22c55e"
            perf_badge = ctk.CTkLabel(
                right_controls,
                text="🔥" if access_count > 10 else "🌡️" if access_count > 5 else "❄️",
                font=("Segoe UI", 12),
                fg_color=perf_color,
                corner_radius=8,
                padx=6,
                pady=2
            )
            perf_badge.pack(side="right", padx=(5, 0))
        
        # Type badge
        type_badge = ctk.CTkLabel(
            right_controls,
            text=var_type.upper(),
            font=("Consolas", 9, "bold"),
            text_color="white",
            fg_color=self.accent_color,
            corner_radius=8,
            padx=10,
            pady=3
        )
        type_badge.pack(side="right", padx=(5, 0))
        
        # Value display with syntax highlighting
        value_frame = ctk.CTkFrame(self, fg_color=("gray85", "#252525"), corner_radius=10)
        value_frame.pack(fill="x", padx=12, pady=(0, 8))
        
        # Format value based on type
        formatted_value = self._format_value(var_value, var_type)
        if len(formatted_value) > 60:
            formatted_value = formatted_value[:57] + "..."
            
        value_label = ctk.CTkLabel(
            value_frame,
            text=formatted_value,
            font=("Consolas", 14, "bold"),
            text_color=("gray10", "gray90"),
            wraplength=300,
            justify="left"
        )
        value_label.pack(padx=12, pady=8)
        
        # Footer with address and controls
        footer = ctk.CTkFrame(self, fg_color=("gray80", "#2a2a2a"), corner_radius=8)
        footer.pack(fill="x", padx=10, pady=(0, 10))
        
        # Address with copy button
        addr_frame = ctk.CTkFrame(footer, fg_color="transparent")
        addr_frame.pack(side="left", padx=8, pady=6)
        
        ctk.CTkLabel(
            addr_frame,
            text=f"📍 {address}",
            font=("Consolas", 9),
            text_color=self.theme["comment"]
        ).pack(side="left")
        
        # Control buttons
        controls = ctk.CTkFrame(footer, fg_color="transparent")
        controls.pack(side="right", padx=8, pady=6)
        
        # Breakpoint button
        self.breakpoint_btn = ctk.CTkButton(
            controls,
            text="🔴",
            width=28,
            height=24,
            font=("Segoe UI", 12),
            fg_color="transparent",
            hover_color=("gray70", "#333333"),
            command=self.toggle_breakpoint
        )
        self.breakpoint_btn.pack(side="right", padx=2)
        
        # Watch button
        self.watch_btn = ctk.CTkButton(
            controls,
            text="☆",
            width=28,
            height=24,
            font=("Segoe UI", 14),
            fg_color="transparent",
            hover_color=("gray70", "#333333"),
            command=self.toggle_watch
        )
        self.watch_btn.pack(side="right", padx=2)
        
        # Hover effects
        self.bind("<Enter>", self._on_hover_enter)
        self.bind("<Leave>", self._on_hover_leave)
        
    def _format_value(self, value: str, var_type: str) -> str:
        """Format value with syntax highlighting"""
        if var_type == "string":
            return f'"{value}"'
        elif var_type == "bool":
            return "doğru" if value.lower() in ["true", "1", "doğru"] else "yanlış"
        elif var_type == "null":
            return "boş"
        elif var_type == "list":
            return f"[{value}]" if not value.startswith("[") else value
        elif var_type == "map":
            return f"{{{value}}}" if not value.startswith("{") else value
        return value
        
    def toggle_watch(self):
        """Toggle watch status"""
        self.is_watched = not self.is_watched
        if self.is_watched:
            self.watch_btn.configure(text="⭐", fg_color=self.accent_color)
            self.configure(border_width=3)
        else:
            self.watch_btn.configure(text="☆", fg_color="transparent")
            self.configure(border_width=2)
            
    def toggle_breakpoint(self):
        """Toggle breakpoint status"""
        self.is_breakpoint = not self.is_breakpoint
        if self.is_breakpoint:
            self.breakpoint_btn.configure(text="🛑", fg_color="#ef4444")
        else:
            self.breakpoint_btn.configure(text="🔴", fg_color="transparent")
            
    def update_value(self, new_value: str, new_access_count: int = 0):
        """Update value with animation"""
        self.var_value = new_value
        self.access_count = new_access_count
        self._flash_update()
        
    def _flash_update(self):
        """Flash animation for value changes"""
        original_border = self.cget("border_color")
        self.configure(border_color="#00ff00", border_width=4)
        self.after(400, lambda: self.configure(border_color=original_border, border_width=2))
        
    def _on_hover_enter(self, event):
        """Enhanced hover effect"""
        self.configure(border_width=3)
        
    def _on_hover_leave(self, event):
        """Restore normal state"""
        if not self.is_watched:
            self.configure(border_width=2)


class MemoryViewV3(ctk.CTkFrame):
    """
    GümüşHafıza V3.0 - Advanced Memory Visualizer with 3D view
    """
    def __init__(self, parent, config, on_jump: Optional[Callable] = None, 
                 on_ask_ai: Optional[Callable] = None):
        super().__init__(parent, fg_color="transparent")
        
        self.config = config
        self.on_jump = on_jump
        self.on_ask_ai = on_ask_ai
        self.theme = config.THEMES[config.theme]
        
        # Data structures
        self.history: List[dict] = []
        self.current_step = 0
        self.memory_cards: Dict[str, MemoryCard] = {}
        self.performance_data = {
            "total_allocations": 0,
            "total_deallocations": 0,
            "peak_memory": 0,
            "current_memory": 0,
            "gc_cycles": 0
        }
        
        # View mode: "cards" or "3d"
        self.view_mode = "cards"
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the enhanced UI with 3D visualization"""
        
        # ============================================================
        # TOP PANEL: Enhanced Controls and Performance Dashboard
        # ============================================================
        top_panel = ctk.CTkFrame(
            self,
            fg_color=self.theme["sidebar_bg"],
            corner_radius=15,
            border_width=1,
            border_color=self.theme["border"]
        )
        top_panel.pack(fill="x", padx=10, pady=10)
        
        # Title with view mode toggle
        title_frame = ctk.CTkFrame(top_panel, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(12, 8))
        
        ctk.CTkLabel(
            title_frame,
            text="🧠 GÜMÜŞHAFİZA V3.0",
            font=("Segoe UI", 20, "bold"),
            text_color=self.theme["accent"]
        ).pack(side="left")
        
        # View mode toggle
        view_toggle = ctk.CTkSegmentedButton(
            title_frame,
            values=["📋 Cards", "🎮 3D View"],
            command=self._toggle_view_mode,
            font=("Segoe UI", 11, "bold")
        )
        view_toggle.set("📋 Cards")
        view_toggle.pack(side="right", padx=(10, 0))
        
        # Status and performance indicators
        status_frame = ctk.CTkFrame(top_panel, fg_color="transparent")
        status_frame.pack(fill="x", padx=15, pady=(0, 8))
        
        # Status badge
        self.status_badge = ctk.CTkLabel(
            status_frame,
            text="⚪ READY",
            font=("Segoe UI", 10, "bold"),
            text_color="white",
            fg_color="#6b7280",
            corner_radius=12,
            padx=12,
            pady=4
        )
        self.status_badge.pack(side="left")
        
        # Performance metrics
        perf_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        perf_frame.pack(side="right")
        
        self.perf_labels = {}
        metrics = [("🚀", "Allocs", "0"), ("🗑️", "Deallocs", "0"), ("📈", "Peak", "0KB")]
        
        for icon, label, value in metrics:
            metric_chip = ctk.CTkFrame(perf_frame, fg_color=("gray85", "#2a2a2a"), corner_radius=8)
            metric_chip.pack(side="left", padx=2)
            
            ctk.CTkLabel(metric_chip, text=icon, font=("Segoe UI", 12)).pack(side="left", padx=(6, 2))
            
            value_label = ctk.CTkLabel(
                metric_chip, 
                text=value, 
                font=("Consolas", 10, "bold"),
                text_color=self.theme["accent"]
            )
            value_label.pack(side="left", padx=(0, 6))
            
            self.perf_labels[label.lower()] = value_label
        
        # Enhanced control bar
        control_bar = ctk.CTkFrame(top_panel, fg_color="transparent")
        control_bar.pack(fill="x", padx=15, pady=(0, 12))
        
        # Playback controls
        play_controls = ctk.CTkFrame(control_bar, fg_color=("gray85", "#2a2a2a"), corner_radius=10)
        play_controls.pack(side="left", padx=(0, 15))
        
        # Control buttons with enhanced styling
        buttons = [
            ("⏮", lambda: self.step(-10), "Skip back 10"),
            ("⏪", lambda: self.step(-1), "Previous step"),
            ("▶", self.toggle_play, "Play/Pause"),
            ("⏩", lambda: self.step(1), "Next step"),
            ("⏭", lambda: self.step(10), "Skip forward 10")
        ]
        
        for icon, command, tooltip in buttons:
            btn = ctk.CTkButton(
                play_controls,
                text=icon,
                width=40,
                height=35,
                font=("Segoe UI", 16),
                fg_color="transparent" if icon != "▶" else self.theme["accent"],
                hover_color=("gray75", "#333333"),
                command=command
            )
            btn.pack(side="left", padx=3, pady=6)
            
            if icon == "▶":
                self.play_btn = btn
        
        # Timeline with enhanced info
        timeline_frame = ctk.CTkFrame(control_bar, fg_color="transparent")
        timeline_frame.pack(side="left", fill="x", expand=True, padx=15)
        
        # Step info with timestamp
        step_info = ctk.CTkFrame(timeline_frame, fg_color="transparent")
        step_info.pack(fill="x")
        
        self.step_label = ctk.CTkLabel(
            step_info,
            text="Step: 0 / 0",
            font=("Consolas", 12, "bold"),
            text_color=self.theme["fg"],
            anchor="w"
        )
        self.step_label.pack(side="left")
        
        self.time_label = ctk.CTkLabel(
            step_info,
            text="Time: 00:00.000",
            font=("Consolas", 10),
            text_color=self.theme["comment"],
            anchor="e"
        )
        self.time_label.pack(side="right")
        
        # Enhanced timeline slider
        self.timeline_slider = ctk.CTkSlider(
            timeline_frame,
            from_=0,
            to=1,
            width=400,
            height=20,
            button_color=self.theme["accent"],
            button_hover_color=self.theme["select_bg"],
            progress_color=self.theme["accent"],
            command=self._on_slider_change
        )
        self.timeline_slider.set(0)
        self.timeline_slider.pack(fill="x", pady=(5, 0))
        
        # Advanced tools
        tools_frame = ctk.CTkFrame(control_bar, fg_color=("gray85", "#2a2a2a"), corner_radius=10)
        tools_frame.pack(side="right")
        
        tool_buttons = [
            ("📸", self.take_snapshot, "Take snapshot"),
            ("🤖", self.ask_ai_analysis, "AI Analysis"),
            ("📊", self.show_performance_report, "Performance Report"),
            ("🗑️", self.clear_history, "Clear history")
        ]
        
        for icon, command, tooltip in tool_buttons:
            if icon == "🤖" and not self.on_ask_ai:
                continue
                
            btn = ctk.CTkButton(
                tools_frame,
                text=icon,
                width=40,
                height=35,
                font=("Segoe UI", 16),
                fg_color="transparent",
                hover_color=("gray75", "#333333"),
                command=command
            )
            btn.pack(side="left", padx=3, pady=6)
        
        # ============================================================
        # MAIN CONTENT: Tabbed view for Cards and 3D visualization
        # ============================================================
        self.content_notebook = ctk.CTkTabview(
            self,
            corner_radius=15,
            border_width=1,
            segmented_button_fg_color=self.theme["sidebar_bg"],
            segmented_button_selected_color=self.theme["accent"]
        )
        self.content_notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Cards view tab
        self.cards_tab = self.content_notebook.add("📋 Memory Cards")
        self._setup_cards_view()
        
        # 3D view tab
        self.view_3d_tab = self.content_notebook.add("🎮 3D Visualization")
        self._setup_3d_view()
        
        # Performance tab
        self.perf_tab = self.content_notebook.add("📊 Performance")
        self._setup_performance_view()
        
    def _setup_cards_view(self):
        """Setup the enhanced cards view"""
        # Filter and search bar
        filter_frame = ctk.CTkFrame(self.cards_tab, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            filter_frame,
            text="🔍 Filter:",
            font=("Segoe UI", 12, "bold")
        ).pack(side="left", padx=(0, 10))
        
        self.filter_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Search variables...",
            width=200
        )
        self.filter_entry.pack(side="left", padx=(0, 10))
        
        # Type filter
        self.type_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All Types", "int", "string", "list", "class", "pointer"],
            width=120
        )
        self.type_filter.pack(side="left", padx=(0, 10))
        
        # Sort options
        self.sort_option = ctk.CTkOptionMenu(
            filter_frame,
            values=["Name", "Type", "Size", "Access Count"],
            width=120
        )
        self.sort_option.pack(side="left")
        
        # Cards container
        self.cards_scroll = ctk.CTkScrollableFrame(
            self.cards_tab,
            fg_color=self.theme["editor_bg"],
            corner_radius=12
        )
        self.cards_scroll.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Empty state
        self._setup_empty_state()
        
    def _setup_3d_view(self):
        """Setup the 3D memory visualization"""
        # 3D controls
        controls_3d = ctk.CTkFrame(self.view_3d_tab, fg_color="transparent", height=60)
        controls_3d.pack(fill="x", padx=10, pady=10)
        controls_3d.pack_propagate(False)
        
        ctk.CTkLabel(
            controls_3d,
            text="🎮 3D Memory Layout - Drag to rotate, scroll to zoom",
            font=("Segoe UI", 14, "bold"),
            text_color=self.theme["accent"]
        ).pack(side="left", pady=20)
        
        # Reset view button
        ctk.CTkButton(
            controls_3d,
            text="🔄 Reset View",
            width=100,
            command=self._reset_3d_view
        ).pack(side="right", pady=15, padx=10)
        
        # 3D Canvas
        self.canvas_3d = MemoryCanvas3D(
            self.view_3d_tab,
            width=800,
            height=600
        )
        self.canvas_3d.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
    def _setup_performance_view(self):
        """Setup performance analytics view"""
        # Performance metrics dashboard
        metrics_frame = ctk.CTkFrame(self.perf_tab, fg_color=self.theme["sidebar_bg"], corner_radius=12)
        metrics_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            metrics_frame,
            text="📊 Memory Performance Analytics",
            font=("Segoe UI", 16, "bold"),
            text_color=self.theme["accent"]
        ).pack(pady=15)
        
        # Metrics grid
        metrics_grid = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        metrics_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        self.perf_metrics = {}
        metrics_data = [
            ("🚀", "Total Allocations", "0", "#3b82f6"),
            ("🗑️", "Total Deallocations", "0", "#ef4444"),
            ("📈", "Peak Memory Usage", "0 KB", "#10b981"),
            ("🔄", "GC Cycles", "0", "#f59e0b"),
            ("⚡", "Avg Access Time", "0 μs", "#8b5cf6"),
            ("🌡️", "Hot Variables", "0", "#ec4899")
        ]
        
        for i, (icon, label, value, color) in enumerate(metrics_data):
            metric_card = ctk.CTkFrame(metrics_grid, fg_color=("gray85", "#252525"), corner_radius=10)
            metric_card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="ew")
            
            ctk.CTkLabel(metric_card, text=icon, font=("Segoe UI", 24)).pack(pady=(10, 5))
            
            value_label = ctk.CTkLabel(
                metric_card,
                text=value,
                font=("Consolas", 18, "bold"),
                text_color=color
            )
            value_label.pack()
            
            ctk.CTkLabel(
                metric_card,
                text=label,
                font=("Segoe UI", 10),
                text_color=self.theme["comment"]
            ).pack(pady=(0, 10))
            
            self.perf_metrics[label.lower().replace(" ", "_")] = value_label
            
        # Configure grid weights
        for i in range(3):
            metrics_grid.columnconfigure(i, weight=1)
        
    def _setup_empty_state(self):
        """Setup empty state message"""
        self.empty_state = ctk.CTkFrame(self.cards_scroll, fg_color="transparent")
        self.empty_state.pack(expand=True, pady=80)
        
        ctk.CTkLabel(
            self.empty_state,
            text="🎯",
            font=("Segoe UI", 64)
        ).pack()
        
        ctk.CTkLabel(
            self.empty_state,
            text="No Memory Data",
            font=("Segoe UI", 18, "bold"),
            text_color=self.theme["comment"]
        ).pack(pady=(15, 8))
        
        ctk.CTkLabel(
            self.empty_state,
            text="Run your GümüşDil code to see real-time memory visualization",
            font=("Segoe UI", 12),
            text_color=self.theme["comment"]
        ).pack()
        
    def _toggle_view_mode(self, value):
        """Toggle between cards and 3D view"""
        if "Cards" in value:
            self.view_mode = "cards"
            self.content_notebook.set("📋 Memory Cards")
        else:
            self.view_mode = "3d"
            self.content_notebook.set("🎮 3D Visualization")
            self._update_3d_view()
            
    def _reset_3d_view(self):
        """Reset 3D view to default position"""
        self.canvas_3d.camera_angle = 45
        self.canvas_3d.camera_height = 0.5
        self.canvas_3d.zoom = 1.0
        self.canvas_3d.redraw()
        
    def update_memory(self, memory_json: str):
        """Enhanced memory update with performance tracking"""
        try:
            data = json.loads(memory_json)
            
            # Add timestamp
            data["timestamp"] = time.time()
            
            # Track performance metrics
            self._update_performance_metrics(data)
            
            self.history.append(data)
            
            # Update timeline
            total_steps = len(self.history)
            if total_steps > 0:
                self.timeline_slider.configure(to=total_steps - 1)
                
                # Auto-advance if at the end
                if self.current_step == total_steps - 2 or self.current_step == 0:
                    self.current_step = total_steps - 1
                    self.timeline_slider.set(self.current_step)
                    self._display_step(self.current_step)
                    
            # Update status
            self.status_badge.configure(
                text="🟢 RUNNING",
                fg_color="#22c55e"
            )
            
        except Exception as e:
            print(f"❌ Memory update error: {e}")
            
    def _update_performance_metrics(self, data: dict):
        """Update performance tracking"""
        # Count allocations/deallocations
        variables = self._collect_variables(data)
        current_count = len(variables)
        
        if hasattr(self, '_last_var_count'):
            if current_count > self._last_var_count:
                self.performance_data["total_allocations"] += current_count - self._last_var_count
            elif current_count < self._last_var_count:
                self.performance_data["total_deallocations"] += self._last_var_count - current_count
                
        self._last_var_count = current_count
        
        # Calculate memory usage (estimated)
        total_size = sum(var.get("size", 8) for var in variables.values())
        self.performance_data["current_memory"] = total_size
        self.performance_data["peak_memory"] = max(self.performance_data["peak_memory"], total_size)
        
        # Update performance labels
        if hasattr(self, 'perf_labels'):
            self.perf_labels["allocs"].configure(text=str(self.performance_data["total_allocations"]))
            self.perf_labels["deallocs"].configure(text=str(self.performance_data["total_deallocations"]))
            self.perf_labels["peak"].configure(text=f"{self.performance_data['peak_memory']}B")
            
    def _display_step(self, step_index: int):
        """Enhanced step display with 3D sync"""
        if step_index < 0 or step_index >= len(self.history):
            return
            
        data = self.history[step_index]
        
        # Update step info
        self.step_label.configure(text=f"Step: {step_index + 1} / {len(self.history)}")
        
        # Update timestamp
        if "timestamp" in data:
            timestamp = data["timestamp"]
            if hasattr(self, '_start_time'):
                elapsed = timestamp - self._start_time
                minutes = int(elapsed // 60)
                seconds = elapsed % 60
                self.time_label.configure(text=f"Time: {minutes:02d}:{seconds:06.3f}")
            else:
                self._start_time = timestamp
                
        # Hide empty state
        self.empty_state.pack_forget()
        
        # Update cards view
        self._update_cards_view(data)
        
        # Update 3D view if active
        if self.view_mode == "3d":
            self._update_3d_view(data)
            
        # Jump to code line
        line_no = data.get("line", 0)
        if line_no > 0 and self.on_jump:
            self.on_jump(line_no)
            
    def _update_cards_view(self, data: dict):
        """Update the cards view"""
        # Clear existing cards
        for card in self.memory_cards.values():
            card.destroy()
        self.memory_cards.clear()
        
        # Collect variables
        variables = self._collect_variables(data)
        
        # Apply filters
        filtered_vars = self._apply_filters(variables)
        
        # Create cards
        for var_name, var_info in filtered_vars.items():
            card = MemoryCard(
                self.cards_scroll,
                var_name=var_name,
                var_value=var_info.get("value", "?"),
                var_type=var_info.get("type", "unknown"),
                address=var_info.get("address", "null"),
                size=var_info.get("size", 0),
                access_count=var_info.get("access_count", 0),
                theme=self.theme
            )
            card.pack(fill="x", padx=10, pady=5)
            self.memory_cards[var_name] = card
            
    def _update_3d_view(self, data: dict = None):
        """Update 3D visualization"""
        if data is None and self.current_step < len(self.history):
            data = self.history[self.current_step]
        elif data is None:
            return
            
        # Clear existing blocks
        self.canvas_3d.blocks.clear()
        self.canvas_3d.stack_blocks.clear()
        self.canvas_3d.heap_blocks.clear()
        
        # Add memory blocks
        variables = self._collect_variables(data)
        
        for var_name, var_info in variables.items():
            block = MemoryBlock3D(
                address=var_info.get("address", "null"),
                size=var_info.get("size", 8),
                var_type=var_info.get("type", "unknown"),
                value=var_info.get("value", "?"),
                name=var_name
            )
            
            # Determine if stack or heap based on type
            is_stack = var_info.get("type", "").lower() in ["int", "float", "bool"]
            
            self.canvas_3d.add_memory_block(block, is_stack)
            
        # Add pointer connections
        for var_name, var_info in variables.items():
            if var_info.get("type", "").lower() == "pointer":
                target_addr = var_info.get("points_to")
                if target_addr and var_info.get("address") in self.canvas_3d.blocks:
                    self.canvas_3d.blocks[var_info.get("address")].add_connection(target_addr)
                    
        self.canvas_3d.redraw()
        
    def _apply_filters(self, variables: dict) -> dict:
        """Apply search and type filters"""
        filtered = {}
        
        search_term = self.filter_entry.get().lower() if hasattr(self, 'filter_entry') else ""
        type_filter = self.type_filter.get() if hasattr(self, 'type_filter') else "All Types"
        
        for name, info in variables.items():
            # Search filter
            if search_term and search_term not in name.lower():
                continue
                
            # Type filter
            if type_filter != "All Types" and info.get("type", "").lower() != type_filter.lower():
                continue
                
            filtered[name] = info
            
        # Sort results
        sort_by = self.sort_option.get() if hasattr(self, 'sort_option') else "Name"
        
        if sort_by == "Name":
            filtered = dict(sorted(filtered.items()))
        elif sort_by == "Type":
            filtered = dict(sorted(filtered.items(), key=lambda x: x[1].get("type", "")))
        elif sort_by == "Size":
            filtered = dict(sorted(filtered.items(), key=lambda x: x[1].get("size", 0), reverse=True))
        elif sort_by == "Access Count":
            filtered = dict(sorted(filtered.items(), key=lambda x: x[1].get("access_count", 0), reverse=True))
            
        return filtered
        
    def _collect_variables(self, scope_data: dict) -> dict:
        """Collect variables from all scopes with enhanced info"""
        variables = {}
        
        def traverse(scope, depth=0):
            if not scope:
                return
                
            # Current scope variables
            for name, info in scope.get("variables", {}).items():
                # Enhanced variable info
                enhanced_info = {
                    "value": info.get("value", "?"),
                    "type": info.get("type", "unknown"),
                    "address": info.get("address", f"0x{hash(name) & 0xFFFFFF:06x}"),
                    "size": info.get("size", self._estimate_size(info.get("type", ""), info.get("value", ""))),
                    "access_count": info.get("access_count", 0),
                    "scope_depth": depth,
                    "points_to": info.get("points_to")  # For pointers
                }
                variables[name] = enhanced_info
                
            # Traverse parent scope
            traverse(scope.get("parent"), depth + 1)
            
        traverse(scope_data)
        return variables
        
    def _estimate_size(self, var_type: str, value: str) -> int:
        """Estimate variable size in bytes"""
        size_map = {
            "int": 4,
            "float": 8,
            "bool": 1,
            "string": len(str(value)) + 1,
            "list": len(str(value)) * 4,  # Rough estimate
            "map": len(str(value)) * 8,   # Rough estimate
            "class": 16,
            "pointer": 8,
            "null": 0
        }
        return size_map.get(var_type.lower(), 8)
        
    def step(self, direction: int):
        """Enhanced step navigation"""
        new_step = self.current_step + direction
        new_step = max(0, min(new_step, len(self.history) - 1))
        
        if new_step != self.current_step:
            self.current_step = new_step
            self.timeline_slider.set(new_step)
            self._display_step(new_step)
            
    def toggle_play(self):
        """Auto-play functionality"""
        # TODO: Implement auto-play with configurable speed
        pass
        
    def _on_slider_change(self, value):
        """Timeline slider change handler"""
        step = int(value)
        if step != self.current_step:
            self.current_step = step
            self._display_step(step)
            
    def take_snapshot(self):
        """Enhanced snapshot with performance data"""
        if self.current_step < 0 or not self.history:
            return
            
        try:
            current_data = self.history[self.current_step]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Enhanced snapshot data
            snapshot = {
                "memory_state": current_data,
                "performance_metrics": self.performance_data.copy(),
                "step_info": {
                    "current_step": self.current_step,
                    "total_steps": len(self.history),
                    "timestamp": timestamp
                },
                "view_settings": {
                    "view_mode": self.view_mode,
                    "camera_angle": getattr(self.canvas_3d, 'camera_angle', 45),
                    "zoom": getattr(self.canvas_3d, 'zoom', 1.0)
                }
            }
            
            filename = f"gumus_memory_snapshot_{timestamp}.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2, ensure_ascii=False)
                
            print(f"✅ Enhanced snapshot saved: {filename}")
            
        except Exception as e:
            print(f"❌ Snapshot error: {e}")
            
    def ask_ai_analysis(self):
        """Enhanced AI analysis with performance context"""
        if not self.on_ask_ai or not self.history:
            return
            
        # Prepare comprehensive analysis context
        variables = self._collect_variables(self.history[self.current_step])
        
        # Performance summary
        perf_summary = f"""
Performance Metrics:
- Total Allocations: {self.performance_data['total_allocations']}
- Total Deallocations: {self.performance_data['total_deallocations']}
- Peak Memory: {self.performance_data['peak_memory']} bytes
- Current Memory: {self.performance_data['current_memory']} bytes
"""
        
        # Variable summary
        var_summary = f"Step {self.current_step + 1}: {len(variables)} active variables\n"
        
        # Hot variables (most accessed)
        hot_vars = sorted(variables.items(), key=lambda x: x[1].get('access_count', 0), reverse=True)[:5]
        if hot_vars:
            var_summary += "\nMost Accessed Variables:\n"
            for name, info in hot_vars:
                var_summary += f"- {name}: {info.get('value', '?')} (accessed {info.get('access_count', 0)}x)\n"
        
        query = f"""Analyze this GümüşDil memory state:

{perf_summary}

{var_summary}

Please provide insights about:
1. Memory usage patterns
2. Potential optimizations
3. Variable lifecycle analysis
4. Performance bottlenecks
"""
        
        self.on_ask_ai(query)
        
    def show_performance_report(self):
        """Show detailed performance report"""
        self.content_notebook.set("📊 Performance")
        
        # Update performance metrics display
        if hasattr(self, 'perf_metrics'):
            self.perf_metrics["total_allocations"].configure(text=str(self.performance_data["total_allocations"]))
            self.perf_metrics["total_deallocations"].configure(text=str(self.performance_data["total_deallocations"]))
            self.perf_metrics["peak_memory_usage"].configure(text=f"{self.performance_data['peak_memory']} B")
            self.perf_metrics["gc_cycles"].configure(text=str(self.performance_data["gc_cycles"]))
            
            # Calculate derived metrics
            if self.history:
                avg_vars = sum(len(self._collect_variables(step)) for step in self.history) / len(self.history)
                hot_vars = sum(1 for step in self.history for var in self._collect_variables(step).values() 
                              if var.get('access_count', 0) > 5)
                
                self.perf_metrics["avg_access_time"].configure(text=f"{avg_vars:.1f}")
                self.perf_metrics["hot_variables"].configure(text=str(hot_vars))
        
    def clear_history(self):
        """Enhanced clear with performance reset"""
        self.history.clear()
        self.current_step = 0
        
        # Reset performance data
        self.performance_data = {
            "total_allocations": 0,
            "total_deallocations": 0,
            "peak_memory": 0,
            "current_memory": 0,
            "gc_cycles": 0
        }
        
        # Clear UI
        for card in self.memory_cards.values():
            card.destroy()
        self.memory_cards.clear()
        
        # Clear 3D view
        self.canvas_3d.blocks.clear()
        self.canvas_3d.stack_blocks.clear()
        self.canvas_3d.heap_blocks.clear()
        self.canvas_3d.redraw()
        
        # Reset UI elements
        self.empty_state.pack(expand=True, pady=80)
        self.step_label.configure(text="Step: 0 / 0")
        self.time_label.configure(text="Time: 00:00.000")
        self.timeline_slider.configure(to=1)
        self.timeline_slider.set(0)
        
        # Reset status
        self.status_badge.configure(text="⚪ READY", fg_color="#6b7280")
        
        # Reset performance labels
        if hasattr(self, 'perf_labels'):
            for label in self.perf_labels.values():
                label.configure(text="0")
                
    def reset(self):
        """Complete system reset"""
        self.clear_history()
        self._reset_3d_view()
        
        # Reset filters
        if hasattr(self, 'filter_entry'):
            self.filter_entry.delete(0, 'end')
        if hasattr(self, 'type_filter'):
            self.type_filter.set("All Types")
        if hasattr(self, 'sort_option'):
            self.sort_option.set("Name")


# Alias for backward compatibility
MemoryViewV2 = MemoryViewV3