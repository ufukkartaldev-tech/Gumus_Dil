# -*- coding: utf-8 -*-
import subprocess
import os
import sys
from pathlib import Path
from ..config import COMPILER_PATH, PROJECT_ROOT

class CompilerRunner:
    DLL_NOT_FOUND_ERROR = 3221225781 # 0xC0000135

    @staticmethod
    def is_compiler_viable():
        """Derleyicinin çalışabilir durumda olup olmadığını kontrol eder (DLL kontrolü)"""
        if not COMPILER_PATH.exists():
            return False
        try:
            # Sadece başlatıp hemen kapatmayı deneyelim
            res = subprocess.run(
                [str(COMPILER_PATH), "--help"], 
                capture_output=True, 
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
                timeout=2
            )
            # 0 dönmeli, yoksa bir sorun vardır (3221225781: DLL Missing, 3221225785: Entry Point Not Found)
            return res.returncode == 0
        except Exception:
            return False

    @staticmethod
    def start_interactive(source_file):
        """İnteraktif bir process başlatır ve Popen nesnesini döner"""
        creationflags = 0
        if sys.platform == 'win32':
            creationflags = subprocess.CREATE_NO_WINDOW

        # FALLBACK: Simülatör (Dosya yoksa VEYA çalışmıyorsa)
        if not CompilerRunner.is_compiler_viable():
            simulator_script = PROJECT_ROOT / "src" / "ide" / "core" / "run_simulator.py"
            process = subprocess.Popen(
                [sys.executable, str(simulator_script), str(source_file)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=0,
                creationflags=creationflags
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
            creationflags=creationflags
        )
        return process

    @staticmethod
    def start_with_memory(source_file):
        """Hafıza görselleştirme flag'i ile başlatır"""
        creationflags = 0
        if sys.platform == 'win32':
             creationflags = subprocess.CREATE_NO_WINDOW

        # FALLBACK: Simülatör
        if not CompilerRunner.is_compiler_viable():
            simulator_script = PROJECT_ROOT / "src" / "ide" / "core" / "run_simulator.py"
            # --dump-memory argumentini simülatör şimdilik yoksayacak veya ilerde ekleyebiliriz
            process = subprocess.Popen(
                [sys.executable, str(simulator_script), str(source_file)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=0,
                creationflags=creationflags
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
            creationflags=creationflags
        )
        return process

    @staticmethod
    def run(source_file):
        """Derleyiciyi çalıştırır ve sonucu (stdout, stderr, exit_code) döner"""
        creationflags = 0
        if sys.platform == 'win32':
             creationflags = subprocess.CREATE_NO_WINDOW
             
        # FALLBACK: Simülatör
        if not CompilerRunner.is_compiler_viable():
            simulator_script = PROJECT_ROOT / "src" / "ide" / "core" / "run_simulator.py"
            try:
                res = subprocess.run(
                    [sys.executable, str(simulator_script), str(source_file)],
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    creationflags=creationflags
                )
                return res.stdout, res.stderr, res.returncode
            except Exception as e:
                return None, f"Simülatör Hatasi: {e}\n", -1

        try:
            # Geriye uyumluluk için run metodu
            kwargs = {
                'capture_output': True,
                'text': True,
                'encoding': 'utf-8',
                'errors': 'replace',
                'creationflags': creationflags
            }
            
            res = subprocess.run(
                [str(COMPILER_PATH), str(source_file)],
                stdin=subprocess.DEVNULL, # Non-interactive mod
                **kwargs
            )
            return res.stdout, res.stderr, res.returncode
        except Exception as e:
            return None, f"Sistem Hatası: {e}\n", -1

    @staticmethod
    def get_ast_json(source_file):
        """AST'yi JSON olarak almak için derleyiciyi çalıştırır"""
        if not CompilerRunner.is_compiler_viable():
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
            # Windows için konsol penceresi açılmasını engelle
            kwargs = {
                'capture_output': True,
                'text': True,
                'encoding': 'utf-8',
                'errors': 'replace'
            }
            
            if sys.platform == 'win32':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            res = subprocess.run(
                [str(COMPILER_PATH), "--dump-ast", str(source_file)],
                **kwargs
            )
            return res.stdout, res.stderr, res.returncode
        except Exception as e:
            return None, str(e), -1

