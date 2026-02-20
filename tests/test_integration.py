import os
import unittest
import sys

# Set up paths
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
sys.path.insert(0, PROJECT_ROOT)

from src.ide.core.compiler import CompilerRunner

class TestGumusIntegration(unittest.TestCase):
    def setUp(self):
        self.original_cwd = os.getcwd()
        os.chdir(PROJECT_ROOT)

    def tearDown(self):
        os.chdir(self.original_cwd)

    def run_script(self, filename):
        script_path = os.path.join(TEST_DIR, filename)
        # Use CompilerRunner which handles fallback
        stdout, stderr, returncode = CompilerRunner.run(script_path)
        
        # Mock result object for compatibility with existing tests
        class Result:
            def __init__(self, o, e, c):
                self.stdout = o
                self.stderr = e
                self.returncode = c
        
        return Result(stdout, stderr, returncode)

    def test_basit_test(self):
        # Create a simple test file if not exists
        test_file = os.path.join(TEST_DIR, "basit_test.tr")
        if not os.path.exists(test_file):
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write('yazdır("GÜMÜŞDIL TEST PROGRAMI")')
                
        result = self.run_script("basit_test.tr")
        self.assertEqual(result.returncode, 0, f"basit_test.tr failed. Stderr: {result.stderr}")
        self.assertIn("GÜMÜŞDIL TEST PROGRAMI", result.stdout)

    def test_bulk_files(self):
        """Runs all .tr files in tests/ folder and checks for crashes (nonzero exit), excluding known error tests."""
        files = [f for f in os.listdir(TEST_DIR) if f.endswith(".tr")]
        
        for f in files:
            # Skip tests designed to fail or torture tests that might hang/fail
            if "hata" in f or "error" in f or "kaos" in f or "worst_case" in f:
                continue
            
            with self.subTest(file=f):
                print(f"Testing {f}...")
                result = self.run_script(f)
                if result.returncode != 0:
                    print(f"FAILED: {f}")
                    print(f"STDOUT: {result.stdout[:200]}..." if result.stdout else "No Output")
                    print(f"STDERR: {result.stderr}")
                
                self.assertEqual(result.returncode, 0, f"{f} failed with exit code {result.returncode}")

if __name__ == '__main__':
    unittest.main()

