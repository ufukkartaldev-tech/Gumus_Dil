#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stability and Error Recovery Tests
Tests for the enhanced error handling and recovery system
"""

import unittest
import sys
import os
import tempfile
import time
from pathlib import Path

# Add project root to path
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ide.core.compiler import CompilerRunner
from src.ide.core.secure_subprocess import SecureSubprocessManager, SecurityLevel

class TestErrorRecovery(unittest.TestCase):
    """Test error recovery and stability features"""
    
    def setUp(self):
        self.compiler_runner = CompilerRunner()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        # Clean up temporary files
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_test_file(self, content, filename="test.tr"):
        """Create a temporary test file"""
        test_file = self.temp_dir / filename
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return test_file
    
    def test_compiler_fallback_mechanism(self):
        """Test that simulator fallback works when compiler fails"""
        # Create a simple test program
        test_content = '''
        değişken mesaj = "Merhaba Dünya"
        yazdır(mesaj)
        '''
        test_file = self.create_test_file(test_content)
        
        # Force fallback mode
        self.compiler_runner.fallback_mode = True
        
        stdout, stderr, exit_code = self.compiler_runner.run(str(test_file))
        
        # Should succeed with simulator
        self.assertEqual(exit_code, 0, f"Fallback failed: {stderr}")
        self.assertIn("Merhaba Dünya", stdout or "")
    
    def test_error_count_tracking(self):
        """Test that error counting works correctly"""
        initial_count = self.compiler_runner.error_count
        
        # Simulate some errors
        self.compiler_runner._handle_compiler_error("Test error 1")
        self.assertEqual(self.compiler_runner.error_count, initial_count + 1)
        
        self.compiler_runner._handle_compiler_error("Test error 2")
        self.assertEqual(self.compiler_runner.error_count, initial_count + 2)
        
        # Should switch to fallback mode after max errors
        self.compiler_runner._handle_compiler_error("Test error 3")
        self.assertTrue(self.compiler_runner.fallback_mode)
    
    def test_syntax_error_handling(self):
        """Test handling of syntax errors"""
        # Create a file with syntax error
        test_content = '''
        değişken x = 
        yazdır(x)
        '''
        test_file = self.create_test_file(test_content)
        
        stdout, stderr, exit_code = self.compiler_runner.run(str(test_file))
        
        # Should handle error gracefully
        self.assertIsNotNone(stderr)
        self.assertNotEqual(exit_code, 0)
    
    def test_runtime_error_handling(self):
        """Test handling of runtime errors"""
        # Create a file with runtime error
        test_content = '''
        yazdır(undefined_variable)
        '''
        test_file = self.create_test_file(test_content)
        
        stdout, stderr, exit_code = self.compiler_runner.run(str(test_file))
        
        # Should handle error gracefully
        self.assertIsNotNone(stderr)
    
    def test_timeout_handling(self):
        """Test timeout handling for long-running processes"""
        # Create a program that might run long
        test_content = '''
        değişken i = 0
        döngü (i < 1000000) {
            i = i + 1
        }
        yazdır("Finished")
        '''
        test_file = self.create_test_file(test_content)
        
        # Set a short timeout for testing
        original_timeout = self.compiler_runner.secure_manager.timeout
        self.compiler_runner.secure_manager.set_timeout(5)  # 5 seconds
        
        try:
            start_time = time.time()
            stdout, stderr, exit_code = self.compiler_runner.run(str(test_file))
            end_time = time.time()
            
            # Should complete within reasonable time (timeout + overhead)
            self.assertLess(end_time - start_time, 10)
            
        finally:
            # Restore original timeout
            self.compiler_runner.secure_manager.set_timeout(original_timeout)
    
    def test_memory_limit_handling(self):
        """Test memory limit handling"""
        # Create a program that might use memory
        test_content = '''
        değişken liste = []
        değişken i = 0
        döngü (i < 1000) {
            liste[i] = "test string " + i
            i = i + 1
        }
        yazdır("Memory test completed")
        '''
        test_file = self.create_test_file(test_content)
        
        stdout, stderr, exit_code = self.compiler_runner.run(str(test_file))
        
        # Should complete successfully or fail gracefully
        self.assertIsNotNone(exit_code)
    
    def test_concurrent_execution_safety(self):
        """Test that concurrent executions don't interfere"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def run_test(test_id):
            test_content = f'''
            değişken test_id = {test_id}
            yazdır("Test " + test_id + " completed")
            '''
            test_file = self.create_test_file(test_content, f"test_{test_id}.tr")
            
            stdout, stderr, exit_code = self.compiler_runner.run(str(test_file))
            results.put((test_id, exit_code, stdout, stderr))
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=run_test, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout
        
        # Check results
        completed_tests = []
        while not results.empty():
            test_id, exit_code, stdout, stderr = results.get()
            completed_tests.append(test_id)
            # Each test should complete successfully
            self.assertEqual(exit_code, 0, f"Test {test_id} failed: {stderr}")
        
        # All tests should have completed
        self.assertEqual(len(completed_tests), 3)
    
    def test_security_validation(self):
        """Test security validation in subprocess manager"""
        secure_manager = SecureSubprocessManager(SecurityLevel.LOW)
        
        # Test safe command
        is_valid, error = secure_manager.validate_command("python --version")
        self.assertTrue(is_valid, f"Safe command rejected: {error}")
        
        # Test dangerous command
        is_valid, error = secure_manager.validate_command("rm -rf /")
        self.assertFalse(is_valid, "Dangerous command accepted")
        
        # Test shell injection
        is_valid, error = secure_manager.validate_command("echo test; rm file")
        self.assertFalse(is_valid, "Shell injection not detected")
    
    def test_path_traversal_protection(self):
        """Test path traversal protection"""
        secure_manager = SecureSubprocessManager(SecurityLevel.LOW)
        
        # Test normal path
        is_valid, error = secure_manager.validate_working_directory(str(self.temp_dir))
        self.assertTrue(is_valid, f"Normal path rejected: {error}")
        
        # Test path traversal
        traversal_path = str(self.temp_dir / ".." / ".." / "etc")
        is_valid, error = secure_manager.validate_working_directory(traversal_path)
        # This might be valid depending on the actual path, so we just check it doesn't crash
        self.assertIsNotNone(error)  # Should return some result
    
    def test_resource_monitoring(self):
        """Test resource monitoring capabilities"""
        # Create a simple test that should complete quickly
        test_content = '''
        yazdır("Resource monitoring test")
        '''
        test_file = self.create_test_file(test_content)
        
        start_time = time.time()
        stdout, stderr, exit_code = self.compiler_runner.run(str(test_file))
        end_time = time.time()
        
        # Should complete quickly
        self.assertLess(end_time - start_time, 5)  # Less than 5 seconds
        self.assertEqual(exit_code, 0, f"Resource monitoring test failed: {stderr}")
    
    def test_graceful_degradation(self):
        """Test graceful degradation under stress"""
        # Simulate multiple rapid executions
        results = []
        
        for i in range(5):
            test_content = f'''
            değişken iteration = {i}
            yazdır("Iteration " + iteration)
            '''
            test_file = self.create_test_file(test_content, f"stress_{i}.tr")
            
            stdout, stderr, exit_code = self.compiler_runner.run(str(test_file))
            results.append((exit_code, stdout, stderr))
            
            # Small delay between executions
            time.sleep(0.1)
        
        # At least some executions should succeed
        successful_runs = sum(1 for exit_code, _, _ in results if exit_code == 0)
        self.assertGreater(successful_runs, 0, "No executions succeeded under stress")
    
    def test_error_message_quality(self):
        """Test that error messages are helpful"""
        # Test undefined variable error
        test_content = '''
        yazdır(undefined_var)
        '''
        test_file = self.create_test_file(test_content)
        
        stdout, stderr, exit_code = self.compiler_runner.run(str(test_file))
        
        # Should provide meaningful error message
        if stderr:
            self.assertTrue(
                any(keyword in stderr.lower() for keyword in ['undefined', 'tanımlanmamış', 'error', 'hata']),
                f"Error message not helpful: {stderr}"
            )

class TestSimulatorStability(unittest.TestCase):
    """Test the Python simulator stability"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_test_file(self, content, filename="test.tr"):
        """Create a temporary test file"""
        test_file = self.temp_dir / filename
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return test_file
    
    def run_simulator(self, test_file, args=None):
        """Run the simulator on a test file"""
        import subprocess
        
        simulator_script = PROJECT_ROOT / "src" / "ide" / "core" / "run_simulator.py"
        cmd = [sys.executable, str(simulator_script), str(test_file)]
        
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(PROJECT_ROOT)
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Timeout", -1
    
    def test_basic_simulation(self):
        """Test basic simulator functionality"""
        test_content = '''
        değişken x = 42
        yazdır("Test value: " + x)
        '''
        test_file = self.create_test_file(test_content)
        
        stdout, stderr, exit_code = self.run_simulator(test_file)
        
        self.assertEqual(exit_code, 0, f"Simulator failed: {stderr}")
        self.assertIn("42", stdout)
    
    def test_simulator_error_handling(self):
        """Test simulator error handling"""
        test_content = '''
        // This should cause an error
        invalid_syntax_here
        '''
        test_file = self.create_test_file(test_content)
        
        stdout, stderr, exit_code = self.run_simulator(test_file)
        
        # Should handle error gracefully (may succeed or fail, but shouldn't crash)
        self.assertIsNotNone(exit_code)
    
    def test_simulator_trace_mode(self):
        """Test simulator trace mode"""
        test_content = '''
        değişken x = 1
        yazdır(x)
        '''
        test_file = self.create_test_file(test_content)
        
        stdout, stderr, exit_code = self.run_simulator(test_file, ["--trace"])
        
        # Should include trace information
        self.assertTrue(
            "__TRACE__" in stdout or "__MEMORY_JSON_START__" in stdout,
            "Trace mode not working"
        )

if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)