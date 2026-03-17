# -*- coding: utf-8 -*-
"""
Güvenli Subprocess Yöneticisi
Shell injection saldırılarını önleyen güvenli komut çalıştırma sistemi
"""

import subprocess
import shlex
import os
import sys
import re
import time
import threading
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union

class SecurityLevel:
    """Güvenlik seviyeleri"""
    UNTRUSTED = 0  # Hiçbir komuta izin verme
    LOW = 1        # Sadece güvenli komutlar
    MEDIUM = 2     # Sınırlı komut seti
    HIGH = 3       # Çoğu komuta izin ver
    SYSTEM = 4     # Tüm komutlara izin ver (dikkatli kullan!)

class SecureSubprocessManager:
    """Güvenli subprocess yöneticisi"""
    
    def __init__(self, security_level: int = SecurityLevel.LOW):
        self.security_level = security_level
        self.timeout = 30  # Varsayılan timeout (saniye)
        self.max_output_size = 1024 * 1024  # 1MB maksimum çıktı
        
        # Güvenli komutlar listesi (whitelist)
        self.safe_commands = {
            'git', 'python', 'python3', 'node', 'npm', 'yarn',
            'ls', 'dir', 'cat', 'type', 'echo', 'pwd', 'cd',
            'mkdir', 'rmdir', 'cp', 'copy', 'mv', 'move',
            'find', 'grep', 'head', 'tail', 'wc', 'sort'
        }
        
        # Tehlikeli komutlar (blacklist)
        self.dangerous_commands = {
            'rm', 'del', 'format', 'fdisk', 'mkfs', 'dd',
            'wget', 'curl', 'nc', 'netcat', 'telnet', 'ssh',
            'sudo', 'su', 'chmod', 'chown', 'passwd', 'useradd',
            'userdel', 'iptables', 'firewall', 'regedit', 'reg'
        }
        
        # Shell metacharacter'ları
        self.shell_metacharacters = {
            ';', '&', '|', '`', '$', '(', ')', '{', '}',
            '[', ']', '<', '>', '&&', '||', '>>', '<<'
        }
        
        # İzin verilen çalışma dizinleri
        self.allowed_directories = set()
        self.blocked_directories = {
            '/etc', '/bin', '/sbin', '/usr/bin', '/usr/sbin',
            'C:\\Windows', 'C:\\Program Files', 'C:\\System32'
        }
    
    def validate_command(self, command: str) -> Tuple[bool, str]:
        """Komutun güvenli olup olmadığını kontrol et"""
        
        if not command or not command.strip():
            return False, "Boş komut"
        
        # Temel güvenlik kontrolü
        if self.security_level == SecurityLevel.UNTRUSTED:
            return False, "Güvenlik seviyesi komut çalıştırmaya izin vermiyor"
        
        # Shell metacharacter kontrolü
        for meta in self.shell_metacharacters:
            if meta in command:
                return False, f"Tehlikeli shell karakteri tespit edildi: {meta}"
        
        # Komut adını çıkar
        command_parts = shlex.split(command)
        if not command_parts:
            return False, "Geçersiz komut formatı"
        
        base_command = Path(command_parts[0]).name.lower()
        
        # Tehlikeli komut kontrolü
        if base_command in self.dangerous_commands:
            if self.security_level < SecurityLevel.HIGH:
                return False, f"Tehlikeli komut tespit edildi: {base_command}"
        
        # Güvenli komut kontrolü (LOW seviyesinde)
        if self.security_level == SecurityLevel.LOW:
            if base_command not in self.safe_commands:
                return False, f"İzin verilmeyen komut: {base_command}"
        
        # Path traversal kontrolü
        if '../' in command or '..\\' in command:
            return False, "Path traversal saldırısı tespit edildi"
        
        # Injection pattern kontrolü
        injection_patterns = [
            r';\s*rm\s+', r';\s*del\s+', r'\|\s*nc\s+', r'\|\s*netcat\s+',
            r'`[^`]*`', r'\$\([^)]*\)', r'>\s*/dev/', r'>\s*CON',
            r'2>&1', r'>/dev/null', r'>NUL'
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Şüpheli injection pattern tespit edildi: {pattern}"
        
        return True, "Komut güvenli"
    
    def sanitize_arguments(self, args: List[str]) -> List[str]:
        """Argümanları temizle ve güvenli hale getir"""
        sanitized = []
        
        for arg in args:
            # Null byte kontrolü
            if '\x00' in arg:
                continue
            
            # Tehlikeli karakterleri kaldır
            cleaned = arg
            for meta in self.shell_metacharacters:
                cleaned = cleaned.replace(meta, '')
            
            # Path traversal temizle
            cleaned = cleaned.replace('../', '').replace('..\\', '')
            
            sanitized.append(cleaned)
        
        return sanitized
    
    def validate_working_directory(self, cwd: Optional[str]) -> Tuple[bool, str]:
        """Çalışma dizininin güvenli olup olmadığını kontrol et"""
        
        if not cwd:
            return True, "Çalışma dizini belirtilmemiş"
        
        cwd_path = Path(cwd).resolve()
        
        # Blocked directories kontrolü
        for blocked in self.blocked_directories:
            blocked_path = Path(blocked).resolve()
            try:
                cwd_path.relative_to(blocked_path)
                return False, f"Yasaklı dizin: {blocked}"
            except ValueError:
                continue
        
        # Allowed directories kontrolü (eğer tanımlanmışsa)
        if self.allowed_directories:
            allowed = False
            for allowed_dir in self.allowed_directories:
                allowed_path = Path(allowed_dir).resolve()
                try:
                    cwd_path.relative_to(allowed_path)
                    allowed = True
                    break
                except ValueError:
                    continue
            
            if not allowed:
                return False, "İzin verilmeyen dizin"
        
        return True, "Çalışma dizini güvenli"
    
    def execute_safe(self, command: str, args: Optional[List[str]] = None, 
                    cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> Dict:
        """Güvenli komut çalıştırma"""
        
        start_time = time.time()
        
        # Komut doğrulama
        is_valid, validation_error = self.validate_command(command)
        if not is_valid:
            return {
                'success': False,
                'error': f"Güvenlik hatası: {validation_error}",
                'stdout': '',
                'stderr': '',
                'returncode': -1,
                'execution_time': 0
            }
        
        # Çalışma dizini doğrulama
        if cwd:
            is_valid_cwd, cwd_error = self.validate_working_directory(cwd)
            if not is_valid_cwd:
                return {
                    'success': False,
                    'error': f"Dizin hatası: {cwd_error}",
                    'stdout': '',
                    'stderr': '',
                    'returncode': -1,
                    'execution_time': 0
                }
        
        # Argümanları temizle
        if args:
            args = self.sanitize_arguments(args)
        
        # Komut listesi oluştur
        if args:
            cmd_list = [command] + args
        else:
            cmd_list = shlex.split(command)
        
        try:
            # Güvenli environment oluştur
            safe_env = os.environ.copy()
            if env:
                # Sadece güvenli environment variable'ları ekle
                safe_env_keys = {'PATH', 'HOME', 'USER', 'TEMP', 'TMP'}
                for key, value in env.items():
                    if key in safe_env_keys and isinstance(value, str):
                        safe_env[key] = value
            
            # Subprocess çalıştır
            process = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,  # stdin'i kapat
                cwd=cwd,
                env=safe_env,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            # Timeout ile bekle
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                return {
                    'success': False,
                    'error': f"Komut timeout ({self.timeout}s) aşıldı",
                    'stdout': '',
                    'stderr': '',
                    'returncode': -1,
                    'execution_time': time.time() - start_time
                }
            
            # Çıktı boyutu kontrolü
            if len(stdout) > self.max_output_size:
                stdout = stdout[:self.max_output_size] + "\n[ÇIKTI KESİLDİ - BOYUT LİMİTİ]"
            
            if len(stderr) > self.max_output_size:
                stderr = stderr[:self.max_output_size] + "\n[HATA ÇIKTISI KESİLDİ - BOYUT LİMİTİ]"
            
            execution_time = time.time() - start_time
            
            return {
                'success': process.returncode == 0,
                'error': '' if process.returncode == 0 else f"Komut hata kodu: {process.returncode}",
                'stdout': stdout,
                'stderr': stderr,
                'returncode': process.returncode,
                'execution_time': execution_time
            }
            
        except FileNotFoundError:
            return {
                'success': False,
                'error': f"Komut bulunamadı: {command}",
                'stdout': '',
                'stderr': '',
                'returncode': -1,
                'execution_time': time.time() - start_time
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Beklenmeyen hata: {str(e)}",
                'stdout': '',
                'stderr': '',
                'returncode': -1,
                'execution_time': time.time() - start_time
            }
    
    def add_safe_command(self, command: str):
        """Güvenli komutlar listesine ekle"""
        self.safe_commands.add(command.lower())
    
    def add_dangerous_command(self, command: str):
        """Tehlikeli komutlar listesine ekle"""
        self.dangerous_commands.add(command.lower())
    
    def add_allowed_directory(self, directory: str):
        """İzin verilen dizinler listesine ekle"""
        self.allowed_directories.add(str(Path(directory).resolve()))
    
    def add_blocked_directory(self, directory: str):
        """Yasaklı dizinler listesine ekle"""
        self.blocked_directories.add(str(Path(directory).resolve()))
    
    def set_timeout(self, timeout: int):
        """Timeout süresini ayarla"""
        self.timeout = max(1, min(timeout, 300))  # 1-300 saniye arası
    
    def set_max_output_size(self, size: int):
        """Maksimum çıktı boyutunu ayarla"""
        self.max_output_size = max(1024, min(size, 10 * 1024 * 1024))  # 1KB - 10MB arası

# Global güvenli subprocess manager
_secure_manager = SecureSubprocessManager()

def execute_secure_command(command: str, args: Optional[List[str]] = None, 
                          cwd: Optional[str] = None, security_level: int = SecurityLevel.LOW) -> Dict:
    """Güvenli komut çalıştırma (global fonksiyon)"""
    global _secure_manager
    
    # Güvenlik seviyesini ayarla
    _secure_manager.security_level = security_level
    
    return _secure_manager.execute_safe(command, args, cwd)

def validate_command_security(command: str, security_level: int = SecurityLevel.LOW) -> Tuple[bool, str]:
    """Komutun güvenli olup olmadığını kontrol et (global fonksiyon)"""
    global _secure_manager
    
    # Güvenlik seviyesini ayarla
    _secure_manager.security_level = security_level
    
    return _secure_manager.validate_command(command)

# Güvenlik testi fonksiyonu
def test_security():
    """Güvenlik sistemini test et"""
    print("=== GÜMÜŞDİL GÜVENLİ SUBPROCESS TEST ===")
    
    test_commands = [
        "echo 'Merhaba Dünya'",  # Güvenli
        "ls -la",                # Güvenli
        "rm -rf /",             # Tehlikeli
        "echo test; rm file",   # Shell injection
        "cat ../../../etc/passwd",  # Path traversal
        "python --version",     # Güvenli
        "wget http://evil.com", # Tehlikeli
    ]
    
    for cmd in test_commands:
        is_safe, reason = validate_command_security(cmd, SecurityLevel.LOW)
        status = "✅ GÜVENLİ" if is_safe else "❌ TEHLİKELİ"
        print(f"{status}: {cmd}")
        if not is_safe:
            print(f"   Sebep: {reason}")
    
    print("=" * 45)

if __name__ == "__main__":
    test_security()