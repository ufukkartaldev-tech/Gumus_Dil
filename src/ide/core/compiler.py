# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import time
from pathlib import Path
from ..config import COMPILER_PATH, PROJECT_ROOT
from .secure_subprocess import SecureSubprocessManager, SecurityLevel, SecurityError

class CompilerRunner:
    DLL_NOT_FOUND_ERROR = 3221225781 # 0xC0000135

    def __init__(self):
        # Initialize secure subprocess manager with enhanced stability
        self.secure_manager = SecureSubprocessManager(SecurityLevel.MEDIUM)
        # Add compiler and Python as safe commands
        self.secure_manager.add_safe_command("python")
        self.secure_manager.add_safe_command("python3")
        self.secure_manager.add_safe_command(str(COMPILER_PATH.name))
        # Set timeout for compiler operations with retry logic
        self.secure_manager.set_timeout(45)  # Increased to 45 seconds for stability
        
        # Enhanced error tracking
        self.error_count = 0
        self.last_error_time = None
        self.max_consecutive_errors = 3
        self.fallback_mode = False

    def is_compiler_viable(self):
        """Derleyicinin çalışabilir durumda olup olmadığını kontrol eder (DLL kontrolü)"""
        if not COMPILER_PATH.exists():
            return False
        try:
            # Use secure subprocess for compiler check with retry logic
            for attempt in range(3):  # 3 attempts for stability
                result = self.secure_manager.execute_safe(
                    str(COMPILER_PATH), 
                    ["--help"],
                    cwd=str(PROJECT_ROOT)
                )
                if result['success'] and result['returncode'] == 0:
                    self.error_count = 0  # Reset error count on success
                    self.fallback_mode = False
                    return True
                
                if attempt < 2:  # Don't sleep on last attempt
                    time.sleep(1)  # Wait 1 second between attempts
                    
            self._handle_compiler_error("Compiler viability check failed after 3 attempts")
            return False
        except Exception as e:
            self._handle_compiler_error(f"Exception during compiler check: {e}")
            return False

    def start_interactive(self, source_file):
        """İnteraktif bir process başlatır ve Popen nesnesini döner"""
        # Validate source file path
        if not self.secure_manager.validate_working_directory(str(Path(source_file).parent))[0]:
            raise SecurityError(f"Güvensiz kaynak dosya yolu: {source_file}")

        # FALLBACK: Simülatör (Dosya yoksa VEYA çalışmıyorsa)
        if not self.is_compiler_viable():
            simulator_script = PROJECT_ROOT / "src" / "ide" / "core" / "run_simulator.py"

            # Validate simulator script exists and is safe
            if not simulator_script.exists():
                raise FileNotFoundError(f"Simülatör bulunamadı: {simulator_script}")

            # Use secure subprocess for simulator
            return self.secure_manager.execute_interactive(
                sys.executable,
                [str(simulator_script), str(source_file)],
                cwd=str(PROJECT_ROOT)
            )

        # Use secure subprocess for compiler
        return self.secure_manager.execute_interactive(
            str(COMPILER_PATH),
            [str(source_file)],
            cwd=str(PROJECT_ROOT)
        )


    def start_with_memory(self, source_file):
        """Hafıza görselleştirme flag'i ile başlatır"""
        # Validate source file path
        if not self.secure_manager.validate_working_directory(str(Path(source_file).parent))[0]:
            raise SecurityError(f"Güvensiz kaynak dosya yolu: {source_file}")

        # FALLBACK: Simülatör
        if not self.is_compiler_viable():
            simulator_script = PROJECT_ROOT / "src" / "ide" / "core" / "run_simulator.py"
            
            if not simulator_script.exists():
                raise FileNotFoundError(f"Simülatör bulunamadı: {simulator_script}")
                
            # Use secure subprocess for simulator with trace
            return self.secure_manager.execute_interactive(
                sys.executable,
                [str(simulator_script), "--trace", str(source_file)],
                cwd=str(PROJECT_ROOT)
            )

        # Use secure subprocess for compiler with memory dump
        return self.secure_manager.execute_interactive(
            str(COMPILER_PATH),
            ["--dump-memory", str(source_file)],
            cwd=str(PROJECT_ROOT)
        )

    def run(self, source_file):
        """Derleyiciyi çalıştırır ve sonucu (stdout, stderr, exit_code) döner"""
        # Validate source file path
        if not self.secure_manager.validate_working_directory(str(Path(source_file).parent))[0]:
            return None, f"Güvenlik Hatası: Güvensiz kaynak dosya yolu: {source_file}", -1
            
        # Check if we should use fallback mode
        if self.fallback_mode or not self.is_compiler_viable():
            return self._run_with_simulator(source_file)
        
        # Try compiler with enhanced error handling
        try:
            result = self._run_with_compiler(source_file)
            if result[2] == 0:  # Success
                self.error_count = 0
                return result
            else:
                # Handle compiler error
                self._handle_compiler_error(f"Compiler returned error code: {result[2]}")
                return self._run_with_simulator(source_file)
                
        except Exception as e:
            self._handle_compiler_error(f"Compiler execution exception: {e}")
            return self._run_with_simulator(source_file)
    
    def _run_with_compiler(self, source_file):
        """Run with the actual compiler"""
        result = self.secure_manager.execute_safe(
            str(COMPILER_PATH),
            [str(source_file)],
            cwd=str(PROJECT_ROOT)
        )
        
        if result['success']:
            return result['stdout'], result['stderr'], result['returncode']
        else:
            raise Exception(f"Derleyici Hatası: {result['error']}")
    
    def _run_with_simulator(self, source_file):
        """Run with the Python simulator as fallback"""
        simulator_script = PROJECT_ROOT / "src" / "ide" / "core" / "run_simulator.py"
        
        if not simulator_script.exists():
            return None, f"Simülatör bulunamadı: {simulator_script}", -1
            
        try:
            result = self.secure_manager.execute_safe(
                sys.executable,
                [str(simulator_script), str(source_file)],
                cwd=str(PROJECT_ROOT)
            )
            
            if result['success']:
                return result['stdout'], result['stderr'], result['returncode']
            else:
                return None, f"Simülatör Hatası: {result['error']}", result['returncode']
                
        except Exception as e:
            return None, f"Simülatör Güvenlik Hatası: {e}", -1
    
    def _handle_compiler_error(self, error_msg):
        """Handle compiler errors with fallback logic"""
        import time
        
        self.error_count += 1
        self.last_error_time = time.time()
        
        print(f"[COMPILER ERROR] {error_msg} (Error count: {self.error_count})")
        
        # Switch to fallback mode if too many consecutive errors
        if self.error_count >= self.max_consecutive_errors:
            self.fallback_mode = True
            print("[COMPILER] Switching to fallback mode due to repeated errors")

    def get_ast_json(self, source_file):
        """AST'yi JSON olarak almak için derleyiciyi çalıştırır"""
        # Validate source file path
        if not self.secure_manager.validate_working_directory(str(Path(source_file).parent))[0]:
            return None, f"Güvenlik Hatası: Güvensiz kaynak dosya yolu: {source_file}", -1
            
        if not self.is_compiler_viable():
            # FALLBACK: Python tabanlı parser'ı kullan
            try:
                from .tokenizer import GumusTokenizer
                from .parser import GumusParser
                import json
                
                with open(source_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                tokenizer = GumusTokenizer(code)
                tokens = tokenizer.tokenize()
                parser = GumusParser(tokens)
                ast = parser.parse()
                
                return json.dumps(ast.to_json(), indent=2, ensure_ascii=False), "", 0
            except Exception as e:
                return None, f"HATA: Derleyici eksik ve simülasyon parser'ı başarısız oldu: {e}", -1
            
        try:
            # Use secure subprocess for AST generation
            result = self.secure_manager.execute_safe(
                str(COMPILER_PATH),
                ["--dump-ast", str(source_file)],
                cwd=str(PROJECT_ROOT)
            )
            
            if result['success']:
                return result['stdout'], result['stderr'], result['returncode']
            else:
                return None, f"AST Hatası: {result['error']}", result['returncode']
                
        except Exception as e:
            return None, f"Güvenlik Hatası: {e}", -1

# Güvenlik exception'ı artık secure_subprocess.py'den import ediliyor

