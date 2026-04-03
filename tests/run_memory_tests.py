#!/usr/bin/env python3
"""
🧪 GümüşDil Memory Management Test Runner
Comprehensive test suite for bytecode generator, VM, and garbage collector
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def run_command(self, cmd, timeout=60):
        """Run a command with timeout and capture output"""
        try:
            print(f"🚀 Running: {' '.join(cmd)}")
            start_time = time.time()
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=Path(__file__).parent
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration': duration
            }
        except subprocess.TimeoutExpired:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': f'Test timed out after {timeout} seconds',
                'duration': timeout
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'duration': 0
            }
    
    def build_tests(self):
        """Build all test executables"""
        print("🔨 Building test executables...")
        
        # Create build directory
        build_dir = Path("build")
        build_dir.mkdir(exist_ok=True)
        
        # Configure with CMake
        cmake_cmd = [
            "cmake", 
            "-S", ".", 
            "-B", "build",
            "-DCMAKE_BUILD_TYPE=Debug"
        ]
        
        result = self.run_command(cmake_cmd)
        if result['returncode'] != 0:
            print(f"❌ CMake configuration failed:")
            print(result['stderr'])
            return False
        
        # Build
        build_cmd = ["cmake", "--build", "build", "--parallel"]
        result = self.run_command(build_cmd)
        
        if result['returncode'] != 0:
            print(f"❌ Build failed:")
            print(result['stderr'])
            return False
        
        print("✅ Build completed successfully")
        return True
    
    def run_test_suite(self, test_name, executable_path):
        """Run a specific test suite"""
        print(f"\n📋 Running {test_name}...")
        
        if not os.path.exists(executable_path):
            print(f"❌ Test executable not found: {executable_path}")
            self.test_results[test_name] = {
                'status': 'FAILED',
                'reason': 'Executable not found',
                'duration': 0
            }
            self.failed_tests += 1
            return False
        
        result = self.run_command([executable_path, "--gtest_output=json:test_results.json"])
        
        # Parse results
        success = result['returncode'] == 0
        
        self.test_results[test_name] = {
            'status': 'PASSED' if success else 'FAILED',
            'duration': result['duration'],
            'stdout': result['stdout'],
            'stderr': result['stderr']
        }
        
        if success:
            print(f"✅ {test_name} passed ({result['duration']:.2f}s)")
            self.passed_tests += 1
        else:
            print(f"❌ {test_name} failed ({result['duration']:.2f}s)")
            print(f"Error: {result['stderr']}")
            self.failed_tests += 1
        
        self.total_tests += 1
        return success
    
    def run_all_tests(self):
        """Run all memory management tests"""
        print("🧪 Starting GümüşDil Memory Management Tests")
        print("=" * 60)
        
        # Build tests first
        if not self.build_tests():
            print("❌ Build failed, cannot run tests")
            return False
        
        # Test suites to run
        test_suites = [
            ("Garbage Collector Tests", "build/test_garbage_collector"),
            ("Bytecode Generator Tests", "build/test_bytecode_generator"),
            ("VM Enhanced Tests", "build/test_vm_enhanced"),
            ("Memory Management Tests", "build/test_memory_management"),
            ("Performance Benchmarks", "build/test_performance_benchmarks")
        ]
        
        # Run each test suite
        for test_name, executable in test_suites:
            self.run_test_suite(test_name, executable)
        
        # Print summary
        self.print_summary()
        
        return self.failed_tests == 0
    
    def run_quick_tests(self):
        """Run only essential tests for quick validation"""
        print("⚡ Running Quick Memory Tests")
        print("=" * 40)
        
        if not self.build_tests():
            return False
        
        quick_tests = [
            ("GC Basic Tests", "build/test_garbage_collector", "--gtest_filter=*Basic*"),
            ("VM Basic Tests", "build/test_vm_enhanced", "--gtest_filter=*Basic*"),
        ]
        
        for test_name, executable, filter_arg in quick_tests:
            if os.path.exists(executable):
                result = self.run_command([executable, filter_arg])
                success = result['returncode'] == 0
                
                if success:
                    print(f"✅ {test_name} passed")
                    self.passed_tests += 1
                else:
                    print(f"❌ {test_name} failed")
                    self.failed_tests += 1
                
                self.total_tests += 1
        
        self.print_summary()
        return self.failed_tests == 0
    
    def run_performance_only(self):
        """Run only performance benchmarks"""
        print("🚀 Running Performance Benchmarks Only")
        print("=" * 45)
        
        if not self.build_tests():
            return False
        
        return self.run_test_suite("Performance Benchmarks", "build/test_performance_benchmarks")
    
    def run_memory_leak_check(self):
        """Run memory leak detection with Valgrind (Linux only)"""
        print("🔍 Running Memory Leak Detection")
        print("=" * 40)
        
        if sys.platform != "linux":
            print("⚠️ Memory leak detection only available on Linux")
            return True
        
        # Check if Valgrind is available
        try:
            subprocess.run(["valgrind", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ Valgrind not found, skipping memory leak detection")
            return True
        
        if not self.build_tests():
            return False
        
        valgrind_cmd = [
            "valgrind",
            "--tool=memcheck",
            "--leak-check=full",
            "--show-leak-kinds=all",
            "--track-origins=yes",
            "--error-exitcode=1",
            "build/test_memory_management"
        ]
        
        result = self.run_command(valgrind_cmd, timeout=300)  # 5 minute timeout
        
        if result['returncode'] == 0:
            print("✅ No memory leaks detected")
            return True
        else:
            print("❌ Memory leaks detected:")
            print(result['stderr'])
            return False
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        
        if self.failed_tests == 0:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️ {self.failed_tests} test(s) failed")
        
        # Print individual test results
        print("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result['status'] == 'PASSED' else "❌"
            print(f"  {status_icon} {test_name}: {result['status']} ({result['duration']:.2f}s)")
    
    def save_results(self, filename="test_results.json"):
        """Save test results to JSON file"""
        results = {
            'summary': {
                'total_tests': self.total_tests,
                'passed_tests': self.passed_tests,
                'failed_tests': self.failed_tests,
                'success_rate': (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
            },
            'test_results': self.test_results,
            'timestamp': time.time()
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Results saved to {filename}")

def main():
    """Main entry point"""
    runner = TestRunner()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "quick":
            success = runner.run_quick_tests()
        elif mode == "performance":
            success = runner.run_performance_only()
        elif mode == "leak-check":
            success = runner.run_memory_leak_check()
        elif mode == "all":
            success = runner.run_all_tests()
        else:
            print(f"Unknown mode: {mode}")
            print("Available modes: quick, performance, leak-check, all")
            sys.exit(1)
    else:
        success = runner.run_all_tests()
    
    # Save results
    runner.save_results()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()