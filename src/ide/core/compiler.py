# -*- coding: utf-8 -*-
import subprocess
import os
import sys
from pathlib import Path
from ..config import COMPILER_PATH, PROJECT_ROOT
from .secure_subprocess import SecureSubprocessManager, SecurityLevel

class CompilerRunner:
    DLL_NOT_FOUND_ERROR = 3221225781 # 0xC0000135

    def __init__(self):
        # Initialize secure subprocess manager
        self.secure_manager = SecureSubprocessManager(SecurityLevel.MEDIUM)
        # Add compiler and Python as safe commands
        self.secure_manager.add_safe_command("python")
        self.secure_manager.add_safe_command("python3")
        self.secure_manager.add_safe_command(str(COMPILER_PATH.name))
        # Set timeout for compiler operations
        self.secure_manager.set_timeout(30)  # 30 seconds for compilation

    def is_compiler_viable(self):
        """Derleyicinin çalışabilir durumda olup olmadığını kontrol eder (DLL kontrolü)"""
        if not COMPILER_PATH.exists():
            return False
        try:
            # Use secure subprocess for compiler check
            result = self.secure_manager.execute_safe(
                str(COMPILER_PATH), 
                ["--help"],
                cwd=str(PROJECT_ROOT)
            )
            return result['success'] and result['returncode'] == 0
        except Exception:
            return False

    def start_interactive(self, source_file):
        """İnteraktif bir process başlatır ve Popen nesnesini döner"""
        # Validate source file path
        if not self.secure_manager.validate_working_directory(str(Path(source_file).parent))[0]:
            raise SecurityError(f"Güvensiz kaynak dosya yolu: {source_file}")
            
        creationflags = 0
        if sys.platform == 'win32':
            creationflags = subprocess.CREATE_NO_WINDOW

        # FALLBACK: Simülatör (Dosya yoksa VEYA çalışmıyorsa)
        if not self.is_compiler_viable():
            simulator_script = PROJECT_ROOT / "src" / "ide" / "core" / "run_simulator.py"
            
            # Validate simulator script exists and is safe
            if not simulator_script.exists():
                raise FileNotFoundError(f"Simülatör bulunamadı: {simulator_script}")
                
            process = subprocess.Popen(
                [sys.executable, str(simulator_script), str(source_file)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=0,
                creationflags=creationflags,
                cwd=str(PROJECT_ROOT)  # Secure working directory
            )
            return process

        process = subprocess.Popen(
            [str(COMPILER_PATH), str(source_file)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=0, # Unbuffered
            creationflags=creationflags,
            cwd=str(PROJECT_ROOT)  # Secure working directory
        )
        return process

    def start_with_memory(self, source_file):
        """Hafıza görselleştirme flag'i ile başlatır"""
        # Validate source file path
        if not self.secure_manager.validate_working_directory(str(Path(source_file).parent))[0]:
            raise SecurityError(f"Güvensiz kaynak dosya yolu: {source_file}")
            
        creationflags = 0
        if sys.platform == 'win32':
             creationflags = subprocess.CREATE_NO_WINDOW

        # FALLBACK: Simülatör
        if not self.is_compiler_viable():
            simulator_script = PROJECT_ROOT / "src" / "ide" / "core" / "run_simulator.py"
            
            if not simulator_script.exists():
                raise FileNotFoundError(f"Simülatör bulunamadı: {simulator_script}")
                
            # --trace argumentini simülatöre geç (Görsel izleme için)
            process = subprocess.Popen(
                [sys.executable, str(simulator_script), "--trace", str(source_file)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=0,
                creationflags=creationflags,
                cwd=str(PROJECT_ROOT)  # Secure working directory
            )
            return process

        process = subprocess.Popen(
            [str(COMPILER_PATH), "--dump-memory", str(source_file)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=0,
            creationflags=creationflags,
            cwd=str(PROJECT_ROOT)  # Secure working directory
        )
        return process

    def run(self, source_file):
        """Derleyiciyi çalıştırır ve sonucu (stdout, stderr, exit_code) döner"""
        # Validate source file path
        if not self.secure_manager.validate_working_directory(str(Path(source_file).parent))[0]:
            return None, f"Güvenlik Hatası: Güvensiz kaynak dosya yolu: {source_file}", -1
            
        # FALLBACK: Simülatör
        if not self.is_compiler_viable():
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

        try:
            # Use secure subprocess for compiler execution
            result = self.secure_manager.execute_safe(
                str(COMPILER_PATH),
                [str(source_file)],
                cwd=str(PROJECT_ROOT)
            )
            
            if result['success']:
                return result['stdout'], result['stderr'], result['returncode']
            else:
                return None, f"Derleyici Hatası: {result['error']}", result['returncode']
                
        except Exception as e:
            return None, f"Güvenlik Hatası: {e}", -1

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

# Security exception class
class SecurityError(Exception):
    """Güvenlik ihlali exception'ı"""
    pass

