# -*- coding: utf-8 -*-
"""
GümüşHafıza Memory Card
Enhanced memory card UI component with performance metrics and interaction
"""

import customtkinter as ctk
from typing import Dict, Optional, Callable


class MemoryCard(ctk.CTkFrame):
    """
    Enhanced memory card with performance metrics and interaction
    """
    def __init__(self, parent, var_name: str, var_value: str, var_type: str, 
                 address: str, theme: dict, size: int = 0, access_count: int = 0, 
                 on_breakpoint: Optional[Callable] = None, 
                 on_watch: Optional[Callable] = None, **kwargs):
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
        
        # Callbacks
        self.on_breakpoint = on_breakpoint
        self.on_watch = on_watch
        
        # Enhanced type colors with Turkish support
        self.accent_color = self._get_type_color()
        
        # Performance-based border color
        border_color = self._get_performance_border_color()
        
        # Main card container with enhanced styling
        self.configure(
            fg_color=("gray90", "#1a1a1a"),
            corner_radius=15,
            border_width=2,
            border_color=border_color
        )
        
        self._setup_ui()
        
    def _get_type_color(self) -> str:
        """Get color based on variable type with Turkish support"""
        type_colors = {
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
            "boş": "#4b5563"       # Dark gray
        }
        
        return type_colors.get(self.var_type.lower(), "#64748b")
        
    def _get_performance_border_color(self) -> str:
        """Get border color based on performance metrics"""
        if self.access_count > 10:
            return "#ef4444"  # Red for hot variables
        elif self.access_count > 5:
            return "#f59e0b"  # Orange for warm variables
        else:
            return self.accent_color
            
    def _get_type_icon(self) -> str:
        """Get icon based on variable type"""
        type_icons = {
            "int": "🔢", "uzun": "🔢", "kısa": "🔢",
            "float": "📊", "ondalık": "📊",
            "string": "📝", "metin": "📝",
            "bool": "✅", "doğru": "✅", "yanlış": "❌",
            "list": "📋", "liste": "📋",
            "map": "🗂️", "harita": "🗂️", "dict": "🗂️",
            "class": "🏗️", "sınıf": "🏗️",
            "object": "📦", "nesne": "📦",
            "pointer": "➡️", "işaretçi": "➡️",
            "ref": "🔗", "referans": "🔗",
            "null": "⭕", "boş": "⭕"
        }
        return type_icons.get(self.var_type.lower(), "❓")
        
    def _setup_ui(self):
        """Setup the card UI components"""
        # Header with enhanced info
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(12, 8))
        
        # Left side: Variable info
        left_info = ctk.CTkFrame(header, fg_color="transparent")
        left_info.pack(side="left", fill="x", expand=True)
        
        # Variable name with type icon
        icon = self._get_type_icon()
        
        name_label = ctk.CTkLabel(
            left_info,
            text=f"{icon} {self.var_name}",
            font=("Segoe UI", 15, "bold"),
            text_color=self.accent_color,
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        # Size and access info
        info_text = f"Size: {self.size}B"
        if self.access_count > 0:
            info_text += f" • Accessed: {self.access_count}x"
            
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
        if self.access_count > 0:
            perf_icon, perf_color = self._get_performance_indicator()
            perf_badge = ctk.CTkLabel(
                right_controls,
                text=perf_icon,
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
            text=self.var_type.upper(),
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
        formatted_value = self._format_value(self.var_value, self.var_type)
        if len(formatted_value) > 60:
            formatted_value = formatted_value[:57] + "..."
            
        self.value_label = ctk.CTkLabel(
            value_frame,
            text=formatted_value,
            font=("Consolas", 14, "bold"),
            text_color=("gray10", "gray90"),
            wraplength=300,
            justify="left"
        )
        self.value_label.pack(padx=12, pady=8)
        
        # Footer with address and controls
        footer = ctk.CTkFrame(self, fg_color=("gray80", "#2a2a2a"), corner_radius=8)
        footer.pack(fill="x", padx=10, pady=(0, 10))
        
        # Address with copy functionality
        addr_frame = ctk.CTkFrame(footer, fg_color="transparent")
        addr_frame.pack(side="left", padx=8, pady=6)
        
        self.addr_label = ctk.CTkLabel(
            addr_frame,
            text=f"📍 {self.address}",
            font=("Consolas", 9),
            text_color=self.theme["comment"]
        )
        self.addr_label.pack(side="left")
        
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
        
    def _get_performance_indicator(self) -> tuple:
        """Get performance indicator icon and color"""
        if self.access_count > 10:
            return "🔥", "#ef4444"  # Hot
        elif self.access_count > 5:
            return "🌡️", "#f59e0b"  # Warm
        else:
            return "❄️", "#22c55e"  # Cool
            
    def _format_value(self, value: str, var_type: str) -> str:
        """Format value with syntax highlighting"""
        if var_type.lower() in ["string", "metin"]:
            return f'"{value}"'
        elif var_type.lower() in ["bool", "doğru", "yanlış"]:
            if value.lower() in ["true", "1", "doğru"]:
                return "doğru"
            else:
                return "yanlış"
        elif var_type.lower() in ["null", "boş"]:
            return "boş"
        elif var_type.lower() in ["list", "liste"]:
            return f"[{value}]" if not value.startswith("[") else value
        elif var_type.lower() in ["map", "harita", "dict"]:
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
            
        # Notify callback
        if self.on_watch:
            self.on_watch(self.var_name, self.is_watched)
            
    def toggle_breakpoint(self):
        """Toggle breakpoint status"""
        self.is_breakpoint = not self.is_breakpoint
        if self.is_breakpoint:
            self.breakpoint_btn.configure(text="🛑", fg_color="#ef4444")
        else:
            self.breakpoint_btn.configure(text="🔴", fg_color="transparent")
            
        # Notify callback
        if self.on_breakpoint:
            self.on_breakpoint(self.var_name, self.is_breakpoint)
            
    def update_value(self, new_value: str, new_access_count: int = 0):
        """Update value with animation"""
        self.var_value = new_value
        self.access_count = new_access_count
        
        # Update display
        formatted_value = self._format_value(new_value, self.var_type)
        if len(formatted_value) > 60:
            formatted_value = formatted_value[:57] + "..."
        self.value_label.configure(text=formatted_value)
        
        # Update performance indicator
        self._update_performance_display()
        
        # Flash animation
        self._flash_update()
        
    def _update_performance_display(self):
        """Update performance-related display elements"""
        # Update border color based on new access count
        border_color = self._get_performance_border_color()
        self.configure(border_color=border_color)
        
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
            
    def set_theme(self, theme: dict):
        """Update theme colors"""
        self.theme = theme
        # Refresh UI elements with new theme
        # This would update colors based on new theme
        
    def get_card_info(self) -> dict:
        """Get comprehensive card information"""
        return {
            "name": self.var_name,
            "value": self.var_value,
            "type": self.var_type,
            "address": self.address,
            "size": self.size,
            "access_count": self.access_count,
            "is_watched": self.is_watched,
            "is_breakpoint": self.is_breakpoint,
            "accent_color": self.accent_color
        }