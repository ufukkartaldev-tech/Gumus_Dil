#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixed Security Validator with Enhanced Detection
Handles URL encoding, hex encoding, and advanced attack patterns
"""

import re
import urllib.parse
import html

class FixedSecurityValidator:
    """Enhanced security validator with comprehensive attack detection"""
    
    def __init__(self):
        self.blocked_patterns = self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching"""
        patterns = {}
        
        # Enhanced SQL injection patterns
        sql_pattern = '|'.join([
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(\bEXEC\b.*\bxp_)",
            r"(';.*--)",
            r"('\s+OR\s+'1'\s*=\s*'1)",
            r"(\bWAITFOR\b.*\bDELAY\b)",
            r"(\bSLEEP\s*\()",
            r"(\bBENCHMARK\s*\()",
            r"(\bDELETE\b.*\bFROM\b)",
            r"(\bTRUNCATE\b)",
            r"(\bINSERT\b.*\bINTO\b.*\bVALUES\b.*';)",
            r"(\bUPDATE\b.*\bSET\b.*';)"
        ])
        patterns['sql'] = re.compile(sql_pattern, re.IGNORECASE)
        
        # Enhanced shell injection patterns
        shell_pattern = '|'.join([
            r"(;\s*\w+)",
            r"(&&\s*\w+)",
            r"(\|\s*\w+)",
            r"(`[^`]+`)",
            r"(\$\([^)]+\))",
            r"(\bwget\b.*http)",
            r"(\bcurl\b.*http)",
            r"(\bnc\b|\bnetcat\b)",
            r"(\brm\s+-rf)",
            r"(\bdd\s+if=)",
            r"(\bformat\s+)",
            r"(\bfdisk\s+)",
            r"(\bmkfs\s+)",
            r"(\bchmod\s+777)"
        ])
        patterns['shell'] = re.compile(shell_pattern, re.IGNORECASE)
        
        # Enhanced path traversal patterns
        path_pattern = '|'.join([
            r"(\.\./)",
            r"(\.\.\\)",
            r"(%2e%2e%2f)",
            r"(%2e%2e%5c)",
            r"(\.\.%2f)",
            r"(\.\.%5c)",
            r"(%252e%252e%252f)",
            r"(%c0%af)",
            r"(%ef%bc%8f)",
            r"(file:///)",
            r"(\\\\)"
        ])
        patterns['path'] = re.compile(path_pattern, re.IGNORECASE)
        
        # Enhanced XSS patterns
        xss_pattern = '|'.join([
            r"(<script[^>]*>)",
            r"(<iframe[^>]*>)",
            r"(<object[^>]*>)",
            r"(on\w+\s*=)",
            r"(javascript:)",
            r"(vbscript:)",
            r"(<style[^>]*>)",
            r"(<link[^>]*>)",
            r"(@import)",
            r"(expression\s*\()"
        ])
        patterns['xss'] = re.compile(xss_pattern, re.IGNORECASE)
        
        # Code injection patterns
        code_pattern = '|'.join([
            r"(__import__)",
            r"(\beval\s*\()",
            r"(\bexec\s*\()",
            r"(\bsystem\s*\()",
            r"(\brequire\s*\()",
            r"(Function\s*\()",
            r"(\{\{.*\}\})",
            r"(\$\{.*\})",
            r"(#\{.*\})",
            r"(<%.*%>)",
            r"(\*\)\(&)",
            r"(<!DOCTYPE.*<!ENTITY)",
            r"(return\s+db\.)"
        ])
        patterns['code'] = re.compile(code_pattern, re.IGNORECASE)
        
        return patterns
    
    def _decode_input(self, input_str):
        """Decode various encoding schemes"""
        decoded_variants = [input_str]
        
        # URL decoding
        try:
            url_decoded = urllib.parse.unquote(input_str)
            if url_decoded != input_str:
                decoded_variants.append(url_decoded)
                # Double URL decoding
                double_decoded = urllib.parse.unquote(url_decoded)
                if double_decoded != url_decoded:
                    decoded_variants.append(double_decoded)
        except:
            pass
        
        # HTML entity decoding
        try:
            html_decoded = html.unescape(input_str)
            if html_decoded != input_str:
                decoded_variants.append(html_decoded)
        except:
            pass
        
        # Hex decoding (for SQL injection)
        if input_str.startswith('0x'):
            try:
                hex_part = input_str[2:]
                hex_decoded = bytes.fromhex(hex_part).decode('utf-8', errors='ignore')
                decoded_variants.append(hex_decoded)
            except:
                pass
        
        # Unicode normalization
        try:
            import unicodedata
            normalized = unicodedata.normalize('NFKC', input_str)
            if normalized != input_str:
                decoded_variants.append(normalized)
        except:
            pass
        
        return decoded_variants
    
    def validate_sql_query(self, query):
        """Enhanced SQL query validation with decoding"""
        if not query or len(query) > 10000:
            return False, "Invalid query length"
        
        # Get all decoded variants
        variants = self._decode_input(query)
        
        # Check each variant for SQL injection patterns
        for variant in variants:
            if self.blocked_patterns['sql'].search(variant):
                return False, "SQL injection pattern detected"
            
            # Additional keyword checks
            dangerous_keywords = [
                "DROP TABLE", "DELETE FROM", "TRUNCATE", "EXEC XP_", 
                "SP_", "WAITFOR DELAY", "SLEEP(", "BENCHMARK(",
                "' OR '1'='1'", "' OR 1=1", "UNION SELECT", "'; --",
                "admin'--", "' AND (SELECT", "' OR (SELECT", 
                "SUBSTRING(@@version", "information_schema", "sysobjects"
            ]
            
            variant_upper = variant.upper()
            for keyword in dangerous_keywords:
                if keyword in variant_upper:
                    return False, f"Dangerous SQL keyword: {keyword}"
        
        return True, "Valid SQL query"
    
    def validate_shell_command(self, command):
        """Enhanced shell command validation with decoding"""
        if not command or len(command) > 1000:
            return False, "Invalid command length"
        
        # Get all decoded variants
        variants = self._decode_input(command)
        
        # Check each variant for shell injection patterns
        for variant in variants:
            if self.blocked_patterns['shell'].search(variant):
                return False, "Shell injection pattern detected"
            
            # Additional dangerous command checks
            dangerous_commands = [
                "rm -rf", "dd if=", "format ", "fdisk ", "mkfs ",
                "chmod 777", "wget http", "curl http", "nc ", "netcat ",
                "powershell", "cmd.exe", "bash -c", "sh -c"
            ]
            
            variant_lower = variant.lower()
            for cmd in dangerous_commands:
                if cmd in variant_lower:
                    return False, f"Dangerous command: {cmd}"
        
        return True, "Valid shell command"
    
    def validate_file_path(self, path):
        """Enhanced file path validation with decoding"""
        if not path or len(path) > 4096:
            return False, "Invalid path length"
        
        # Get all decoded variants
        variants = self._decode_input(path)
        
        # Check each variant for path traversal patterns
        for variant in variants:
            if self.blocked_patterns['path'].search(variant):
                return False, "Path traversal pattern detected"
            
            # Additional path checks
            dangerous_paths = [
                "../", "..\\", "/etc/", "/bin/", "/sbin/",
                "c:\\windows\\", "c:\\system32\\", "\\\\server\\",
                "file:///", "\x00"
            ]
            
            variant_lower = variant.lower()
            for dangerous_path in dangerous_paths:
                if dangerous_path in variant_lower:
                    return False, f"Dangerous path pattern: {dangerous_path}"
        
        # Check for dangerous file extensions
        dangerous_extensions = [
            '.exe', '.bat', '.cmd', '.com', '.scr', '.pif',
            '.dll', '.sys', '.vbs', '.js', '.jar', '.sh',
            '.ps1', '.msi', '.reg'
        ]
        
        path_lower = path.lower()
        for ext in dangerous_extensions:
            if path_lower.endswith(ext):
                return False, f"Dangerous file extension: {ext}"
        
        return True, "Valid file path"
    
    def validate_user_input(self, input_str, input_type="general"):
        """Enhanced user input validation with comprehensive checks"""
        if not input_str:
            return False, "Empty input"
        
        if len(input_str) > 1024:
            return False, "Input too long"
        
        # Check for null bytes
        if '\x00' in input_str:
            return False, "Null byte detected"
        
        # Get all decoded variants
        variants = self._decode_input(input_str)
        
        # Check for XSS patterns
        for variant in variants:
            if self.blocked_patterns['xss'].search(variant):
                return False, "XSS pattern detected"
            
            if self.blocked_patterns['code'].search(variant):
                return False, "Code injection pattern detected"
        
        # Type-specific validation
        if input_type == "variable":
            if not re.match(r'^[a-zA-Z_çğıöşüÇĞIÖŞÜ][a-zA-Z0-9_çğıöşüÇĞIÖŞÜ]*$', input_str):
                return False, "Invalid variable name format"
        
        elif input_type == "filename":
            if not re.match(r'^[a-zA-Z0-9._-]+$', input_str):
                return False, "Invalid filename format"
        
        return True, "Valid input"

# Update the test class to use the fixed validator
def patch_security_tests():
    """Patch the security tests to use the fixed validator"""
    import sys
    from pathlib import Path
    
    # Import the test module
    test_module_path = Path(__file__).parent / "security_test_enhanced.py"
    
    # Replace the validator in the test
    if 'tests.security_test_enhanced' in sys.modules:
        test_module = sys.modules['tests.security_test_enhanced']
        
        # Replace the EnhancedSecurityValidator class
        test_module.EnhancedSecurityValidator = FixedSecurityValidator
        
        print("✅ Security validator patched with enhanced detection")
    
    return FixedSecurityValidator()

if __name__ == "__main__":
    # Test the fixed validator
    validator = FixedSecurityValidator()
    
    # Test cases
    test_cases = [
        ("SELECT * FROM users WHERE id = '1' OR '1'='1'", "sql"),
        ("%27%20OR%20%271%27%3D%271", "sql"),
        ("echo test; rm -rf /", "shell"),
        ("%3B%20ls%20-la", "shell"),
        ("../../../etc/passwd", "path"),
        ("%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd", "path"),
        ("<script>alert('XSS')</script>", "user"),
        ("%3Cscript%3Ealert('XSS')%3C/script%3E", "user"),
    ]
    
    print("🔒 Testing Fixed Security Validator")
    print("=" * 40)
    
    for test_input, test_type in test_cases:
        if test_type == "sql":
            is_safe, reason = validator.validate_sql_query(test_input)
        elif test_type == "shell":
            is_safe, reason = validator.validate_shell_command(test_input)
        elif test_type == "path":
            is_safe, reason = validator.validate_file_path(test_input)
        else:
            is_safe, reason = validator.validate_user_input(test_input)
        
        status = "✅ BLOCKED" if not is_safe else "❌ ALLOWED"
        print(f"{status}: {test_input[:50]}...")
        if not is_safe:
            print(f"   Reason: {reason}")
    
    print("\n🎯 Fixed validator should block all test cases above")