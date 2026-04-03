# -*- coding: utf-8 -*-
"""
GümüşHafıza Main Controller
The orchestrator that brings all memory visualization components together
"""

import customtkinter as ctk
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable

# Import our modular components
from .memory_models import MemoryBlock3D, PerformanceMetrics
from .memory_engine import MemoryDataProcessor, MemoryFilter, MemoryAnalyzer
from .visualizers.canvas_3d import MemoryCanvas3D
from .visualizers.memory_card import MemoryCard


class GumusHafizaMain(ctk.CTkFrame):
    """
    GümüşHafıza V3.0 - Main orchestrator for advanced memory visualization
    This class coordinates all components and manages the overall user experience
    """
    
    def __init__(self, parent, config, on_jump: Optional[Callable] = None):
        super().__init__(parent, fg_color="transparent")
        
        # Core configuration
        self.config = config
        self.on_jump = on_jump
        self.theme = config.THEMES[config.theme]
        
        # Core components
        self.data_processor = MemoryDataProcessor()
        self.memory_filter = MemoryFilter()
        self.memory_analyzer = MemoryAnalyzer()
        
        # Data storage
        self.history: List[dict] = []
        self.current_step = 0
        self.memory_cards: Dict[str, MemoryCard] = {}
        
        # View state
        self.view_mode = "cards"  # "cards" or "3d"
        
        # UI components (will be created in _setup_ui)
        self.content_notebook = None
        self.cards_scroll = None
        self.canvas_3d = None
        self.filter_entry = None
        self.type_filter = None
        self.sort_option = None
        self.timeline_slider = None
        self.step_label = None
        self.time_label = None
        self.status_badge = None
        self.perf_labels = {}
        self.perf_metrics = {}
        
        # Setup the user interface
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the main user interface - orchestrates all UI components"""
        
        # Top control panel
        self._create_control_panel()
        
        # Main content area with tabs
        self._create_content_area()
        
        # Setup individual views
        self._setup_cards_view()
        self._setup_3d_view()
        self._setup_performance_view()
        
    def _create_control_panel(self):
        """Create the top control panel with playback and tools"""
        top_panel = ctk.CTkFrame(
            self,
            fg_color=self.theme["sidebar_bg"],
            corner_radius=15,
            border_width=1,
            border_color=self.theme["border"]
        )
        top_panel.pack(fill="x", padx=10, pady=10)
        
        # Title and view toggle
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
        self._create_status_bar(top_panel)
        
        # Control bar with playback controls
        self._create_control_bar(top_panel)
        
    def _create_status_bar(self, parent):
        """Create status bar with performance indicators"""
        status_frame = ctk.CTkFrame(parent, fg_color="transparent")
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
        
        # Performance metrics chips
        perf_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        perf_frame.pack(side="right")
        
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
            
    def _create_control_bar(self, parent):
        """Create playback control bar"""
        control_bar = ctk.CTkFrame(parent, fg_color="transparent")
        control_bar.pack(fill="x", padx=15, pady=(0, 12))
        
        # Playback controls
        play_controls = ctk.CTkFrame(control_bar, fg_color=("gray85", "#2a2a2a"), corner_radius=10)
        play_controls.pack(side="left", padx=(0, 15))
        
        # Control buttons
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
        
        # Timeline
        self._create_timeline(control_bar)
        
        # Tools
        self._create_tools(control_bar)
        
    def _create_timeline(self, parent):
        """Create timeline controls"""
        timeline_frame = ctk.CTkFrame(parent, fg_color="transparent")
        timeline_frame.pack(side="left", fill="x", expand=True, padx=15)
        
        # Step info
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
        
        # Timeline slider
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
        
    def _create_tools(self, parent):
        """Create tools panel"""
        tools_frame = ctk.CTkFrame(parent, fg_color=("gray85", "#2a2a2a"), corner_radius=10)
        tools_frame.pack(side="right")
        
        tool_buttons = [
            ("📸", self.take_snapshot, "Take snapshot"),
            ("📊", self.show_performance_report, "Performance Report"),
            ("🗑️", self.clear_history, "Clear history")
        ]
        
        for icon, command, tooltip in tool_buttons:
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
            
    def _create_content_area(self):
        """Create main content area with tabs"""
        self.content_notebook = ctk.CTkTabview(
            self,
            corner_radius=15,
            border_width=1,
            segmented_button_fg_color=self.theme["sidebar_bg"],
            segmented_button_selected_color=self.theme["accent"]
        )
        self.content_notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Add tabs
        self.cards_tab = self.content_notebook.add("📋 Memory Cards")
        self.view_3d_tab = self.content_notebook.add("🎮 3D Visualization")
        self.perf_tab = self.content_notebook.add("📊 Performance")
        
    def _setup_cards_view(self):
        """Setup the memory cards view"""
        # Filter controls
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
        self.filter_entry.bind("<KeyRelease>", self._on_filter_change)
        
        # Type filter
        self.type_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All Types", "int", "string", "list", "class", "pointer"],
            width=120,
            command=self._on_filter_change
        )
        self.type_filter.pack(side="left", padx=(0, 10))
        
        # Sort options
        self.sort_option = ctk.CTkOptionMenu(
            filter_frame,
            values=["Name", "Type", "Size", "Access Count"],
            width=120,
            command=self._on_filter_change
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
        """Setup 3D visualization"""
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
            ("⚡", "Rendering Efficiency", "0%", "#8b5cf6"),
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
        
    # ============================================================
    # PUBLIC API - Main interface methods
    # ============================================================
    
    def update_memory(self, memory_json: str):
        """
        Main entry point for memory updates from GümüşDil runtime
        Orchestrates the entire update process
        """
        try:
            # Process the raw memory data
            processed_data = self.data_processor.process_memory_json(memory_json)
            
            if not processed_data:
                return
                
            # Add to history
            self.history.append(processed_data)
            
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
            
            # Update performance indicators
            self._update_performance_display()
            
        except Exception as e:
            print(f"❌ Memory update error: {e}")
            
    def step(self, direction: int):
        """Navigate through memory history"""
        new_step = self.current_step + direction
        new_step = max(0, min(new_step, len(self.history) - 1))
        
        if new_step != self.current_step:
            self.current_step = new_step
            self.timeline_slider.set(new_step)
            self._display_step(new_step)
            
    def toggle_play(self):
        """Toggle auto-play functionality"""
        # TODO: Implement auto-play with configurable speed
        pass
        
    def take_snapshot(self):
        """Take comprehensive snapshot of current state"""
        if self.current_step < 0 or not self.history:
            return
            
        try:
            current_data = self.history[self.current_step]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Get comprehensive performance summary
            perf_summary = self.data_processor.get_performance_summary()
            
            # Enhanced snapshot data
            snapshot = {
                "memory_state": current_data,
                "performance_summary": perf_summary,
                "step_info": {
                    "current_step": self.current_step,
                    "total_steps": len(self.history),
                    "timestamp": timestamp
                },
                "view_settings": {
                    "view_mode": self.view_mode,
                    "camera_angle": getattr(self.canvas_3d, 'camera_angle', 45),
                    "zoom": getattr(self.canvas_3d, 'zoom', 1.0)
                },
                "analysis": self._get_current_analysis()
            }
            
            filename = f"gumus_memory_snapshot_{timestamp}.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2, ensure_ascii=False)
                
            print(f"✅ Enhanced snapshot saved: {filename}")
            
        except Exception as e:
            print(f"❌ Snapshot error: {e}")
            
    def show_performance_report(self):
        """Show detailed performance report"""
        self.content_notebook.set("📊 Performance")
        
        # Update all performance metrics
        perf_summary = self.data_processor.get_performance_summary()
        
        if hasattr(self, 'perf_metrics'):
            memory_data = perf_summary.get("memory_performance", {})
            rendering_data = perf_summary.get("rendering_performance", {})
            efficiency_data = perf_summary.get("efficiency_metrics", {})
            
            self.perf_metrics["total_allocations"].configure(text=str(memory_data.get("total_allocations", 0)))
            self.perf_metrics["total_deallocations"].configure(text=str(memory_data.get("total_deallocations", 0)))
            self.perf_metrics["peak_memory_usage"].configure(text=f"{memory_data.get('peak_memory', 0)} B")
            self.perf_metrics["gc_cycles"].configure(text=str(memory_data.get("gc_cycles", 0)))
            self.perf_metrics["rendering_efficiency"].configure(text=f"{efficiency_data.get('rendering_efficiency', 0):.1f}%")
            
            # Calculate hot variables
            if self.history:
                current_vars = self.history[self.current_step].get("enhanced_variables", {})
                hot_count = sum(1 for var in current_vars.values() if var.get('access_count', 0) > 5)
                self.perf_metrics["hot_variables"].configure(text=str(hot_count))
                
        # Show 3D rendering performance
        if self.canvas_3d:
            render_stats = self.canvas_3d.get_render_stats()
            print("🎮 3D Rendering Performance:")
            print(f"  Total Renders: {render_stats.get('total_renders', 0)}")
            print(f"  Full Redraws: {render_stats.get('full_redraws', 0)}")
            print(f"  Incremental Updates: {render_stats.get('incremental_updates', 0)}")
            
    def clear_history(self):
        """Clear all history and reset state"""
        self.history.clear()
        self.current_step = 0
        
        # Reset data processor
        self.data_processor = MemoryDataProcessor()
        
        # Clear UI
        for card in self.memory_cards.values():
            card.destroy()
        self.memory_cards.clear()
        
        # Clear 3D view
        if self.canvas_3d:
            self.canvas_3d.clear_all()
        
        # Reset UI elements
        self.empty_state.pack(expand=True, pady=80)
        self.step_label.configure(text="Step: 0 / 0")
        self.time_label.configure(text="Time: 00:00.000")
        self.timeline_slider.configure(to=1)
        self.timeline_slider.set(0)
        
        # Reset status
        self.status_badge.configure(text="⚪ READY", fg_color="#6b7280")
        
        # Reset performance labels
        for label in self.perf_labels.values():
            label.configure(text="0")
            
    def reset(self):
        """Complete system reset"""
        self.clear_history()
        if self.canvas_3d:
            self.canvas_3d.reset_view()
            
        # Reset filters
        if self.filter_entry:
            self.filter_entry.delete(0, 'end')
        if self.type_filter:
            self.type_filter.set("All Types")
        if self.sort_option:
            self.sort_option.set("Name")
            
    # ============================================================
    # PRIVATE METHODS - Internal orchestration
    # ============================================================
    
    def _display_step(self, step_index: int):
        """Display a specific step - orchestrates all view updates"""
        if step_index < 0 or step_index >= len(self.history):
            return
            
        data = self.history[step_index]
        
        # Update step info
        self.step_label.configure(text=f"Step: {step_index + 1} / {len(self.history)}")
        
        # Update timestamp
        self._update_timestamp_display(data)
        
        # Hide empty state
        self.empty_state.pack_forget()
        
        # Update current view
        if self.view_mode == "cards":
            self._update_cards_view(data)
        elif self.view_mode == "3d":
            self._update_3d_view(data)
            
        # Jump to code line
        line_no = data.get("line", 0)
        if line_no > 0 and self.on_jump:
            self.on_jump(line_no)
            
    def _update_cards_view(self, data: dict):
        """Update the memory cards view"""
        # Clear existing cards
        for card in self.memory_cards.values():
            card.destroy()
        self.memory_cards.clear()
        
        # Get enhanced variables
        variables = data.get("enhanced_variables", {})
        
        # Apply filters using the memory filter engine
        filtered_vars = self.memory_filter.apply_filters(
            variables,
            search_term=self.filter_entry.get() if self.filter_entry else "",
            type_filter=self.type_filter.get() if self.type_filter else "All Types",
            sort_option=self.sort_option.get() if self.sort_option else "Name"
        )
        
        # Create cards using the memory card component
        for var_name, var_info in filtered_vars.items():
            card = MemoryCard(
                self.cards_scroll,
                var_name=var_name,
                var_value=var_info.get("value", "?"),
                var_type=var_info.get("type", "unknown"),
                address=var_info.get("address", "null"),
                size=var_info.get("size", 0),
                access_count=var_info.get("access_count", 0),
                theme=self.theme,
                on_breakpoint=self._on_card_breakpoint,
                on_watch=self._on_card_watch
            )
            card.pack(fill="x", padx=10, pady=5)
            self.memory_cards[var_name] = card
            
    def _update_3d_view(self, data: dict = None):
        """Update 3D visualization using the canvas component"""
        if not self.canvas_3d:
            return
            
        if data is None and self.current_step < len(self.history):
            data = self.history[self.current_step]
        elif data is None:
            return
            
        # Clear existing blocks
        self.canvas_3d.clear_all()
        
        # Get enhanced variables
        variables = data.get("enhanced_variables", {})
        
        # Add memory blocks to 3D canvas
        for var_name, var_info in variables.items():
            block = MemoryBlock3D(
                address=var_info.get("address", "null"),
                size=var_info.get("size", 8),
                var_type=var_info.get("type", "unknown"),
                value=var_info.get("value", "?"),
                name=var_name
            )
            
            # Set access count for heat mapping
            block.access_count = var_info.get("access_count", 0)
            
            # Use native type system to determine stack vs heap
            is_stack = var_info.get("is_stack", False)
            
            self.canvas_3d.add_memory_block(block, is_stack)
            
        # Add pointer connections
        for var_name, var_info in variables.items():
            if var_info.get("is_pointer", False):
                target_addr = var_info.get("points_to")
                if target_addr and var_info.get("address") in self.canvas_3d.blocks:
                    self.canvas_3d.blocks[var_info.get("address")].add_connection(target_addr)
                    
    def _update_performance_display(self):
        """Update performance indicators in the status bar"""
        perf_summary = self.data_processor.get_performance_summary()
        memory_data = perf_summary.get("memory_performance", {})
        
        if hasattr(self, 'perf_labels'):
            self.perf_labels["allocs"].configure(text=str(memory_data.get("total_allocations", 0)))
            self.perf_labels["deallocs"].configure(text=str(memory_data.get("total_deallocations", 0)))
            self.perf_labels["peak"].configure(text=f"{memory_data.get('peak_memory', 0)}B")
            
    def _update_timestamp_display(self, data: dict):
        """Update timestamp display"""
        if "timestamp" in data:
            timestamp = data["timestamp"]
            if hasattr(self, '_start_time'):
                elapsed = timestamp - self._start_time
                minutes = int(elapsed // 60)
                seconds = elapsed % 60
                self.time_label.configure(text=f"Time: {minutes:02d}:{seconds:06.3f}")
            else:
                self._start_time = timestamp
                
    def _get_current_analysis(self) -> dict:
        """Get analysis of current memory state"""
        if not self.history or self.current_step >= len(self.history):
            return {}
            
        current_data = self.history[self.current_step]
        variables = current_data.get("enhanced_variables", {})
        
        return self.memory_analyzer.analyze_memory_usage(variables)
        
    def _toggle_view_mode(self, value):
        """Toggle between cards and 3D view"""
        if "Cards" in value:
            self.view_mode = "cards"
            self.content_notebook.set("📋 Memory Cards")
        else:
            self.view_mode = "3d"
            self.content_notebook.set("🎮 3D Visualization")
            if self.current_step < len(self.history):
                self._update_3d_view(self.history[self.current_step])
                
    def _reset_3d_view(self):
        """Reset 3D view to default position"""
        if self.canvas_3d:
            self.canvas_3d.reset_view()
            
    def _on_slider_change(self, value):
        """Handle timeline slider changes"""
        step = int(value)
        if step != self.current_step:
            self.current_step = step
            self._display_step(step)
            
    def _on_filter_change(self, event=None):
        """Handle filter changes"""
        if self.current_step < len(self.history):
            self._update_cards_view(self.history[self.current_step])
            
    def _on_card_breakpoint(self, var_name: str, is_set: bool):
        """Handle breakpoint toggle on memory card"""
        print(f"Breakpoint {'set' if is_set else 'removed'} for variable: {var_name}")
        
    def _on_card_watch(self, var_name: str, is_watched: bool):
        """Handle watch toggle on memory card"""
        print(f"Variable {'watched' if is_watched else 'unwatched'}: {var_name}")


# Alias for backward compatibility
MemoryViewV3 = GumusHafizaMain