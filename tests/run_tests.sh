#!/bin/bash

# GümüşDil C++ Compiler Tests Runner
# Bu script tüm C++ derleyici testlerini çalıştırır

echo "🧪 GümüşDil C++ Compiler Tests"
echo "================================"

# Test dizinine git
cd "$(dirname "$0")"

# Build directory oluştur
mkdir -p build
cd build

echo "📦 Building tests..."
cmake ..
if [ $? -ne 0 ]; then
    echo "❌ CMake configuration failed!"
    exit 1
fi

make -j$(nproc)
if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo ""
echo "🚀 Running tests..."
echo "==================="

# Test sonuçları
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test fonksiyonu
run_test() {
    local test_name=$1
    local test_executable=$2
    
    echo ""
    echo "🧪 Running $test_name..."
    echo "------------------------"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if ./$test_executable; then
        echo "✅ $test_name PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo "❌ $test_name FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Unit Tests
echo ""
echo "📋 UNIT TESTS"
echo "============="

run_test "Tokenizer Tests" "test_tokenizer"
run_test "Parser Tests" "test_parser"
run_test "Interpreter Tests" "test_interpreter"
run_test "Garbage Collector Tests" "test_garbage_collector"
run_test "VM Tests" "test_vm"

# Integration Tests
echo ""
echo "🔗 INTEGRATION TESTS"
echo "==================="

run_test "Compiler Pipeline Tests" "test_compiler_pipeline"
run_test "IDE-Compiler Integration Tests" "test_ide_compiler_integration"

# Sonuçları göster
echo ""
echo "📊 TEST RESULTS"
echo "==============="
echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo "🎉 ALL TESTS PASSED!"
    echo "The GümüşDil C++ compiler is ready for production."
    exit 0
else
    echo ""
    echo "💥 SOME TESTS FAILED!"
    echo "Please fix the failing tests before proceeding."
    exit 1
fi