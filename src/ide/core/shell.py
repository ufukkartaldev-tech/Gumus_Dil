# -*- coding: utf-8 -*-
import sys
import io
import traceback
from .transpiler import GumusToPythonTranspiler
from .secure_subprocess import SecureSubprocessManager, SecurityLevel

class GumusShell:
    """GümüşDil Etkileşimli Kabuk (REPL)"""
    
    def __init__(self, output_callback=None):
        self.transpiler = GumusToPythonTranspiler()
        self.locals = {}
        self.output_callback = output_callback or print
        self.buffer = []
        self.brace_count = 0
        
        # Initialize secure subprocess manager for shell commands
        self.secure_manager = SecureSubprocessManager(SecurityLevel.LOW)
        self.secure_manager.set_timeout(10)  # 10 seconds for shell commands
        
        # Standart kütüphaneyi içeri alalım
        import math, random, time
        self.locals['math'] = math
        self.locals['random'] = random
        self.locals['time'] = time
        self.locals['doğru'] = True
        self.locals['yanlış'] = False
        self.locals['yok'] = None
        
        # Built-in mapping helpers
        self.locals['metin'] = str
        self.locals['sayı'] = int
        self.locals['uzunluk'] = len
        
        # Add secure command execution function
        self.locals['güvenli_komut'] = self._secure_command_wrapper

    def _secure_command_wrapper(self, command, args=None):
        """Güvenli komut çalıştırma wrapper'ı"""
        try:
            result = self.secure_manager.execute_safe(command, args or [])
            if result['success']:
                return {
                    'çıktı': result['stdout'],
                    'hata': result['stderr'],
                    'başarılı': True,
                    'kod': result['returncode']
                }
            else:
                return {
                    'çıktı': '',
                    'hata': result['error'],
                    'başarılı': False,
                    'kod': result['returncode']
                }
        except Exception as e:
            return {
                'çıktı': '',
                'hata': f"Güvenlik hatası: {str(e)}",
                'başarılı': False,
                'kod': -1
            }

    def execute_line(self, line):
        """Tek bir satırı veya blok parçasını işler"""
        line = line.strip()
        
        if line == "sıfırla":
            self.reset()
            return "GÜMÜŞ > "
            
        if line == "temizle":
            if hasattr(self, 'terminal_clear_callback'):
                self.terminal_clear_callback()
            return "GÜMÜŞ > "

        if not line and not self.buffer:
            return
            
        # Blok kontrolü
        self.buffer.append(line)
        self.brace_count += line.count('{')
        self.brace_count -= line.count('}')
        
        if self.brace_count > 0:
            # Blok henüz tamamlanmadı, devam et
            return "... "
            
        # Blok tamamlandı veya normal satır, çalıştır
        full_code = "\n".join(self.buffer)
        self.buffer = []
        self.brace_count = 0
        
        try:
            # Security check for potentially dangerous code patterns
            if self._contains_dangerous_patterns(full_code):
                self.output_callback("🔴 Güvenlik Uyarısı: Tehlikeli kod kalıbı tespit edildi!\n")
                return ">>> "
            
            # 1. GümüşDil -> Python
            py_code = self.transpiler.transpile(full_code)
            
            # Eğer hata mesajıyla döndüyse (transpiler hata verirse # ile başlar genelde ama kontrol edelim)
            if py_code.startswith("# HATA"):
                self.output_callback(f"🔴 Tercüme Hatası: {py_code.splitlines()[1]}\n")
                return ">>> "

            # 2. Python kodunu çalıştır ve çıktıyı yakala
            output = io.StringIO()
            sys.stdout = output
            
            try:
                # exec() kullanarak değişkenleri sakla. 
                # Eğer tek bir ifadeyse (değişken olmayan), sonucunu yazdırabiliriz.
                # Ancak transpile edilmiş kod genelde statement'lardan oluşur.
                exec(py_code, {"__builtins__": __builtins__}, self.locals)
            except Exception as e:
                sys.stdout = sys.__stdout__
                self.output_callback(f"🔴 Çalıştırma Hatası: {str(e)}\n")
                return ">>> "
            finally:
                sys.stdout = sys.__stdout__
            
            # Çıktıyı yazdır
            res_text = output.getvalue()
            if res_text:
                self.output_callback(res_text)
                
        except Exception as e:
            self.output_callback(f"🔴 Beklenmeyen Hata: {str(e)}\n")
            # traceback.print_exc()
            
        return ">>> "

    def _contains_dangerous_patterns(self, code):
        """Tehlikeli kod kalıplarını kontrol et"""
        dangerous_patterns = [
            'import os', 'import subprocess', 'import sys',
            'exec(', 'eval(', '__import__',
            'open(', 'file(', 'input(',
            'raw_input(', 'compile(',
            'globals()', 'locals()', 'vars()',
            'delattr(', 'setattr(', 'getattr(',
            'hasattr(', 'dir(', 'help(',
            'reload(', 'execfile('
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in code_lower:
                return True
        return False

    def reset(self):
        self.variables = {}
        self.buffer = []
        self.brace_count = 0
        self.output_callback("🧹 GümüşShell sıfırlandı.\n")

