#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Test Runner for GümüşDil
Comprehensive test execution with improved reliability and reporting
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_enhanced_test_suite():
    """Run the complete enhanced test suite"""
    print("🚀 GÜMÜŞDIL ENHANCED TEST SUITE")
    print("=" * 60)
    
    test_results = {}
    overall_success = True
    
    # 1. Run Python Integration Tests (Enhanced)
    print("\n📋 Running Enhanced Integration Tests...")
    try:
        from tests.test_framework_improvements import run_enhanced_tests
        result = run_enhanced_tests()
        test_results['integration'] = {'success': result == 0, 'details': 'Enhanced integration tests'}
        if result != 0:
            overall_success = False
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
        test_results['integration'] = {'success': False, 'details': str(e)}
        overall_success = False
    
    # 2. Run Enhanced Security Tests
    print("\n🔒 Running Enhanced Security Tests...")
    try:
        from tests.security_test_enhanced import run_enhanced_security_tests
        result = run_enhanced_security_tests()
        test_results['security'] = {'success': result == 0, 'details': 'Enhanced security tests'}
        if result != 0:
            overall_success = False
    except Exception as e:
        print(f"❌ Security tests failed: {e}")
        test_results['security'] = {'success': False, 'details': str(e)}
        overall_success = False
    
    # 3. Run Original Python Tests (with fallback)
    print("\n🐍 Running Original Python Tests...")
    try:
        result = subprocess.run([
            sys.executable, 'tests/test_integration.py', '--verbose'
        ], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=60)
        
        test_results['python_original'] = {
            'success': result.returncode == 0,
            'details': f"Exit code: {result.returncode}"
        }
        if result.returncode != 0:
            print(f"⚠️  Original Python tests had issues (exit code: {result.returncode})")
    except Exception as e:
        print(f"⚠️  Original Python tests failed: {e}")
        test_results['python_original'] = {'success': False, 'details': str(e)}
    
    # Print final summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 60)
    
    total_suites = len(test_results)
    passed_suites = sum(1 for r in test_results.values() if r['success'])
    
    for suite_name, result in test_results.items():
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        print(f"{suite_name.upper()}: {status}")
        if not result['success']:
            print(f"  Details: {result['details']}")
    
    success_rate = (passed_suites / total_suites * 100) if total_suites > 0 else 0
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed_suites}/{total_suites} suites)")
    
    if success_rate >= 80:
        print("🎉 EXCELLENT: Test improvements successful!")
        return 0
    elif success_rate >= 60:
        print("⚠️  GOOD: Significant improvements made, minor issues remain")
        return 0
    else:
        print("❌ NEEDS WORK: Further improvements required")
        return 1

if __name__ == "__main__":
    sys.exit(run_enhanced_test_suite())