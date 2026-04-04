# -*- coding: utf-8 -*-
import json
import re
import time

class OutputParser:
    """Kod çıktısı parsing ve analiz modülü"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.memory_buffer = []
        self.last_ui_update_time = 0
        self.ui_update_interval = 0.05  # 50ms
        
    def parse_output_line(self, line):
        """Tek satır çıktıyı parse eder ve uygun UI bileşenine yönlendirir"""
        line = line.strip()
        if not line:
            return
            
        # Memory JSON parsing
        if self._is_memory_json(line):
            self._handle_memory_json(line)
            return
            
        # Canvas komutları
        if line.startswith("CANVAS:"):
            self._handle_canvas_command(line)
            return
            
        # Trace komutları  
        if line.startswith("TRACE:"):
            self._handle_trace_command(line)
            return
            
        # Profiler komutları
        if line.startswith("PROFILER:"):
            self._handle_profiler_command(line)
            return
            
        # Normal terminal çıktısı
        self._handle_terminal_output(line)
        
    def _is_memory_json(self, line):
        """Satırın memory JSON formatında olup olmadığını kontrol eder"""
        return (line.startswith('{"type":"memory"') or 
                line.startswith('{"type":"variable"') or
                line.startswith('{"type":"function_call"') or
                line.startswith('{"type":"function_return"'))
                
    def _handle_memory_json(self, line):
        """Memory JSON verilerini işler"""
        try:
            data = json.loads(line)
            self.memory_buffer.append(data)
            
            # UI throttling
            current_time = time.time()
            if current_time - self.last_ui_update_time > self.ui_update_interval:
                self._update_memory_ui()
                self.last_ui_update_time = current_time
                
        except json.JSONDecodeError:
            pass  # Geçersiz JSON, görmezden gel
            
    def _handle_canvas_command(self, line):
        """Canvas komutlarını işler"""
        command = line[7:]  # "CANVAS:" kısmını çıkar
        
        if hasattr(self.main_window, 'sidebar') and hasattr(self.main_window.sidebar, 'canvas_panel'):
            canvas_panel = self.main_window.sidebar.canvas_panel
            if hasattr(canvas_panel, 'process_command'):
                canvas_panel.process_command(command)
                
    def _handle_trace_command(self, line):
        """Trace komutlarını işler"""
        trace_data = line[6:]  # "TRACE:" kısmını çıkar
        
        if hasattr(self.main_window, 'sidebar') and hasattr(self.main_window.sidebar, 'trace_panel'):
            trace_panel = self.main_window.sidebar.trace_panel
            if hasattr(trace_panel, 'add_trace'):
                trace_panel.add_trace(trace_data)
                
    def _handle_profiler_command(self, line):
        """Profiler komutlarını işler"""
        profiler_data = line[9:]  # "PROFILER:" kısmını çıkar
        
        if hasattr(self.main_window, 'sidebar') and hasattr(self.main_window.sidebar, 'profiler_panel'):
            profiler_panel = self.main_window.sidebar.profiler_panel
            if hasattr(profiler_panel, 'update_data'):
                profiler_panel.update_data(profiler_data)
                
    def _handle_terminal_output(self, line):
        """Normal terminal çıktısını işler"""
        if hasattr(self.main_window, 'terminal'):
            self.main_window.terminal.write_text(line + "\n")
            
    def _update_memory_ui(self):
        """Memory UI'ını günceller"""
        if not self.memory_buffer:
            return
            
        if hasattr(self.main_window, 'sidebar') and hasattr(self.main_window.sidebar, 'memory_panel'):
            memory_panel = self.main_window.sidebar.memory_panel
            
            for data in self.memory_buffer:
                if hasattr(memory_panel, 'process_memory_data'):
                    memory_panel.process_memory_data(data)
                    
        self.memory_buffer.clear()
        
    def clear_buffers(self):
        """Tüm buffer'ları temizler"""
        self.memory_buffer.clear()
        self.last_ui_update_time = 0