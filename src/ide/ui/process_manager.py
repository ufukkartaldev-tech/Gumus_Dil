# -*- coding: utf-8 -*-
import subprocess
import threading
import os
import signal
import time

class ProcessManager:
    """Process lifecycle yönetimi"""
    
    def __init__(self, main_window, config):
        self.main_window = main_window
        self.config = config
        self.process = None
        self.is_running = False
        
    def start_process(self, run_file):
        """Yeni process başlatır"""
        if self.is_running:
            self.stop_process()
            
        try:
            # Compiler path
            compiler_path = self.config.get_compiler_path()
            if not os.path.exists(compiler_path):
                raise FileNotFoundError(f"Compiler bulunamadı: {compiler_path}")
                
            # Process başlat
            self.process = subprocess.Popen(
                [compiler_path, str(run_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            self.is_running = True
            return True
            
        except Exception as e:
            self._handle_process_error(f"Process başlatma hatası: {e}")
            return False
            
    def stop_process(self):
        """Çalışan process'i durdurur"""
        if not self.process or not self.is_running:
            return
            
        try:
            if os.name == 'nt':
                # Windows
                self.process.send_signal(signal.CTRL_BREAK_EVENT)
                time.sleep(0.1)
                if self.process.poll() is None:
                    self.process.terminate()
                    time.sleep(0.1)
                    if self.process.poll() is None:
                        self.process.kill()
            else:
                # Unix/Linux
                self.process.terminate()
                time.sleep(0.1)
                if self.process.poll() is None:
                    self.process.kill()
                    
        except Exception as e:
            print(f"Process durdurma hatası: {e}")
        finally:
            self.process = None
            self.is_running = False
            
    def send_input(self, text):
        """Process'e input gönderir"""
        if not self.process or not self.is_running:
            return False
            
        try:
            self.process.stdin.write(text + '\n')
            self.process.stdin.flush()
            return True
        except Exception as e:
            self._handle_process_error(f"Input gönderme hatası: {e}")
            return False
            
    def read_output(self):
        """Process çıktısını okur (non-blocking)"""
        if not self.process or not self.is_running:
            return None
            
        try:
            # Process bitmiş mi kontrol et
            if self.process.poll() is not None:
                self.is_running = False
                return None
                
            # Çıktı oku
            line = self.process.stdout.readline()
            if line:
                return line.rstrip('\n\r')
            else:
                return None
                
        except Exception as e:
            self._handle_process_error(f"Çıktı okuma hatası: {e}")
            return None
            
    def is_process_running(self):
        """Process'in çalışıp çalışmadığını kontrol eder"""
        if not self.process:
            return False
            
        if self.process.poll() is not None:
            self.is_running = False
            
        return self.is_running
        
    def get_process_info(self):
        """Process bilgilerini döner"""
        if not self.process:
            return None
            
        return {
            'pid': self.process.pid,
            'returncode': self.process.returncode,
            'is_running': self.is_running
        }
        
    def _handle_process_error(self, error_message):
        """Process hatalarını işler"""
        print(f"ProcessManager Error: {error_message}")
        
        if hasattr(self.main_window, 'terminal'):
            self.main_window.terminal.write_text(f"⚠️ {error_message}\n")
            
        self.is_running = False
        
    def cleanup(self):
        """Temizlik işlemleri"""
        if self.is_running:
            self.stop_process()