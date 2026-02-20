# -*- coding: utf-8 -*-
"""
GümüşIDE Debugger Manager
Breakpoint, Step-by-Step Execution, Variable Watch, Call Stack
"""

import subprocess
import threading
import time
from typing import Dict, List, Set, Callable, Optional, Any
from dataclasses import dataclass
from enum import Enum


class DebugState(Enum):
    """Debugger durumu"""
    IDLE = "idle"           # Çalışmıyor
    RUNNING = "running"     # Çalışıyor (breakpoint'e kadar)
    PAUSED = "paused"       # Breakpoint'te durdu
    STEPPING = "stepping"   # Adım adım ilerliyor
    FINISHED = "finished"   # Program bitti


class StepMode(Enum):
    """Adımlama modu"""
    OVER = "over"    # Step Over (F10)
    INTO = "into"    # Step Into (F11)
    OUT = "out"      # Step Out (Shift+F11)


@dataclass
class StackFrame:
    """Çağrı yığını frame'i"""
    function_name: str
    line_number: int
    file_path: str
    local_vars: Dict[str, Any]
    
    def __repr__(self):
        return f"{self.function_name}() at line {self.line_number}"


@dataclass
class Variable:
    """Değişken bilgisi"""
    name: str
    value: Any
    type_name: str
    scope: str  # "local" veya "global"
    changed: bool = False  # Son adımda değişti mi?
    
    def __repr__(self):
        return f"{self.name} = {self.value} ({self.type_name})"


class DebuggerManager:
    """
    GümüşIDE Debugger Yöneticisi
    
    Özellikler:
    - Breakpoint yönetimi
    - Step-by-step execution
    - Variable watching
    - Call stack tracking
    """
    
    def __init__(self, compiler_path: str = "gumus.exe"):
        self.compiler_path = compiler_path
        
        # Breakpoints
        self.breakpoints: Set[int] = set()  # Satır numaraları
        
        # Execution State
        self.state = DebugState.IDLE
        self.current_line: Optional[int] = None
        self.current_file: Optional[str] = None
        
        # Call Stack
        self.call_stack: List[StackFrame] = []
        
        # Variables
        self.variables: Dict[str, Variable] = {}
        self.watched_vars: Set[str] = set()  # Kullanıcının takip ettiği değişkenler
        
        # Callbacks
        self.on_state_change: Optional[Callable[[DebugState], None]] = None
        self.on_line_change: Optional[Callable[[int], None]] = None
        self.on_variable_change: Optional[Callable[[str, Variable], None]] = None
        self.on_stack_change: Optional[Callable[[List[StackFrame]], None]] = None
        
        # Execution Control
        self.process: Optional[subprocess.Popen] = None
        self.execution_thread: Optional[threading.Thread] = None
        self.step_mode: Optional[StepMode] = None
        self.execution_speed: float = 1.0  # 1x normal hız
        
    # ==================== Breakpoint Management ====================
    
    def add_breakpoint(self, line: int):
        """Breakpoint ekle"""
        self.breakpoints.add(line)
        
    def remove_breakpoint(self, line: int):
        """Breakpoint kaldır"""
        self.breakpoints.discard(line)
        
    def toggle_breakpoint(self, line: int):
        """Breakpoint ekle/kaldır"""
        if line in self.breakpoints:
            self.remove_breakpoint(line)
        else:
            self.add_breakpoint(line)
            
    def clear_all_breakpoints(self):
        """Tüm breakpoint'leri temizle"""
        self.breakpoints.clear()
        
    def has_breakpoint(self, line: int) -> bool:
        """Satırda breakpoint var mı?"""
        return line in self.breakpoints
    
    # ==================== Execution Control ====================
    
    def start_debug(self, file_path: str):
        """Debug modunda programı başlat"""
        self.current_file = file_path
        self._set_state(DebugState.RUNNING)
        
        # Simüle edilmiş çalıştırma (gerçek implementasyon compiler'a debug flag eklemeli)
        self.execution_thread = threading.Thread(target=self._run_debug_loop, args=(file_path,))
        self.execution_thread.daemon = True
        self.execution_thread.start()
        
    def pause(self):
        """Çalışmayı duraklat"""
        if self.state == DebugState.RUNNING:
            self._set_state(DebugState.PAUSED)
            
    def continue_execution(self):
        """Sonraki breakpoint'e kadar devam et (F5)"""
        if self.state == DebugState.PAUSED:
            self._set_state(DebugState.RUNNING)
            self.step_mode = None
            
    def step_over(self):
        """Mevcut satırı çalıştır, sonraki satıra geç (F10)"""
        if self.state == DebugState.PAUSED:
            self._set_state(DebugState.STEPPING)
            self.step_mode = StepMode.OVER
            
    def step_into(self):
        """Fonksiyon çağrısına gir (F11)"""
        if self.state == DebugState.PAUSED:
            self._set_state(DebugState.STEPPING)
            self.step_mode = StepMode.INTO
            
    def step_out(self):
        """Mevcut fonksiyondan çık (Shift+F11)"""
        if self.state == DebugState.PAUSED:
            self._set_state(DebugState.STEPPING)
            self.step_mode = StepMode.OUT
            
    def stop(self):
        """Debug'ı durdur"""
        if self.process:
            self.process.terminate()
        self._set_state(DebugState.IDLE)
        self.current_line = None
        self.call_stack.clear()
        self.variables.clear()
        
    def set_speed(self, speed: float):
        """Çalıştırma hızını ayarla (0.5x, 1x, 2x, vb.)"""
        self.execution_speed = max(0.1, min(10.0, speed))
    
    # ==================== Variable Management ====================
    
    def add_watch(self, var_name: str):
        """Değişkeni takip listesine ekle"""
        self.watched_vars.add(var_name)
        
    def remove_watch(self, var_name: str):
        """Değişkeni takip listesinden çıkar"""
        self.watched_vars.discard(var_name)
        
    def update_variable(self, var_name: str, new_value: Any):
        """Değişken değerini güncelle (runtime'da değiştir)"""
        if var_name in self.variables:
            old_var = self.variables[var_name]
            new_var = Variable(
                name=var_name,
                value=new_value,
                type_name=type(new_value).__name__,
                scope=old_var.scope,
                changed=True
            )
            self.variables[var_name] = new_var
            
            if self.on_variable_change:
                self.on_variable_change(var_name, new_var)
    
    def get_watched_variables(self) -> List[Variable]:
        """Takip edilen değişkenleri getir"""
        return [self.variables[name] for name in self.watched_vars if name in self.variables]
    
    def get_all_variables(self) -> List[Variable]:
        """Tüm değişkenleri getir"""
        return list(self.variables.values())
    
    # ==================== Call Stack Management ====================
    
    def get_call_stack(self) -> List[StackFrame]:
        """Çağrı yığınını getir"""
        return self.call_stack.copy()
    
    def get_current_frame(self) -> Optional[StackFrame]:
        """Mevcut stack frame'i getir"""
        return self.call_stack[-1] if self.call_stack else None
    
    # ==================== Internal Methods ====================
    
    def _set_state(self, new_state: DebugState):
        """Durum değiştir ve callback'i tetikle"""
        self.state = new_state
        if self.on_state_change:
            self.on_state_change(new_state)
            
    def _set_current_line(self, line: int):
        """Mevcut satırı değiştir ve callback'i tetikle"""
        self.current_line = line
        if self.on_line_change:
            self.on_line_change(line)
            
    def _run_debug_loop(self, file_path: str):
        """
        Gerçek debug döngüsü (gumus.exe ile haberleşir)
        """
        import json
        import os
        
        # Absolute path kullan
        if not os.path.exists(self.compiler_path):
             # Default path fallback
             self.compiler_path = os.path.join(os.getcwd(), "src", "compiler", "gumus.exe")
             
        if not os.path.exists(self.compiler_path):
             print(f"Compiler bulunamadi: {self.compiler_path}")
             self._set_state(DebugState.FINISHED)
             return

        try:
            # Process'i başlat (--debug modu ile)
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            self.process = subprocess.Popen(
                [self.compiler_path, "--debug", file_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                startupinfo=startupinfo,
                encoding='utf-8' # UTF-8 önemli
            )
            
            self._set_state(DebugState.RUNNING)
            
            while self.process.poll() is None:
                # Stdout oku
                line = self.process.stdout.readline()
                if not line:
                    break
                    
                line = line.strip()
                
                # Debug EVENT yakala
                if line.startswith("__DEBUG_EVENT__"):
                    try:
                        data = json.loads(line.replace("__DEBUG_EVENT__", ""))
                        if "line" in data:
                            self._set_current_line(data["line"])
                            
                            # Her satırda duruyor, state'i PAUSED yap
                            self._set_state(DebugState.PAUSED)
                            
                            # Değişkenleri iste
                            if self.process and self.process.stdin:
                                self.process.stdin.write("VARS\n")
                                self.process.stdin.flush()
                                
                    except Exception as e:
                        print(f"JSON Parse Error: {e}")
                        
                # Debug DATA yakala (Variables)
                elif line.startswith("__DEBUG_DATA__"):
                    try:
                        json_str = line.replace("__DEBUG_DATA__", "")
                        # Bazen boş gelebilir {}
                        if json_str.strip() == "null" or not json_str.strip():
                            continue
                            
                        env_data = json.loads(json_str)
                        self._parse_variables(env_data)
                        
                    except Exception as e:
                        print(f"Var Parse Error: {e}")
                        
                # Komut bekleme mantığı (PAUSED durumunda)
                while self.state == DebugState.PAUSED and self.process.poll() is None:
                    # Kullanıcı arayüzünden komut bekliyoruz
                    if self.step_mode == StepMode.OVER:
                        if self.process.stdin:
                            self.process.stdin.write("STEP_OVER\n")
                            self.process.stdin.flush()
                        self.step_mode = None
                        self._set_state(DebugState.RUNNING)
                        break
                        
                    elif self.step_mode == StepMode.INTO: # Şimdilik aynı
                         if self.process.stdin:
                            self.process.stdin.write("STEP_OVER\n")
                            self.process.stdin.flush()
                         self.step_mode = None
                         self._set_state(DebugState.RUNNING)
                         break
                         
                    elif self.state == DebugState.RUNNING: # Continue basıldıysa
                        if self.process.stdin:
                            self.process.stdin.write("CONTINUE\n")
                            self.process.stdin.flush()
                        break
                    
                    time.sleep(0.05)
                    
        except Exception as e:
            print(f"Debug hatasi: {e}")
        finally:
            self.stop()
            self._set_state(DebugState.FINISHED)

    def _parse_variables(self, env_data):
        """Environment JSON'dan değişkenleri güncelle"""
        if not isinstance(env_data, dict): return
        
        # Rekürsif olarak tüm scope'ları gezebiliriz, şimdilik sadece mevcut scope
        if "variables" in env_data:
            for name, val_data in env_data["variables"].items():
                # Value formatı: {"type": "...", "value": ...}
                val = val_data.get("value", "")
                typ = val_data.get("type", "unknown")
                
                # Update logic
                self.update_variable(name, val)
                
                # Yeni değişken ekle
                if name not in self.variables:
                     self.variables[name] = Variable(name, val, typ, "local")
                     
            # Callback
            if self.on_variable_change:
                # Toplu güncelleme bildirimi yapılabilir ama şimdilik tek tek
                pass

