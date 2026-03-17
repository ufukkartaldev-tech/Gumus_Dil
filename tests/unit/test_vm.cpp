#include <gtest/gtest.h>
#include "../../src/compiler/vm/vm.h"
#include "../../src/compiler/vm/chunk.h"
#include "../../src/compiler/vm/compiler.h"
#include "../../src/compiler/lexer/tokenizer.h"
#include "../../src/compiler/parser/parser.h"

#include <gtest/gtest.h>
#include "../../src/compiler/vm/vm.h"
#include "../../src/compiler/vm/chunk.h"
#include "../../src/compiler/vm/compiler.h"
#include "../../src/compiler/vm/memory_pool.h"
#include "../../src/compiler/lexer/tokenizer.h"
#include "../../src/compiler/parser/parser.h"
#include <chrono>

// Forward declarations
extern bool gumus_debug;

class GumusException : public std::exception {
public:
    GumusException(const std::string& msg) : message(msg) {}
    const char* what() const noexcept override { return message.c_str(); }
private:
    std::string message;
};

class MemoryArena {
public:
    // Simplified memory arena for tests
};

class VMTest : public ::testing::Test {
protected:
    std::unique_ptr<VM> vm;
    std::unique_ptr<Chunk> chunk;
    
    void SetUp() override {
        vm = std::make_unique<VM>();
        chunk = std::make_unique<Chunk>();
        
        // Reset memory pools for clean tests
        MemoryStats::resetAll();
    }
    
    void TearDown() override {
        vm.reset();
        chunk.reset();
        
        // Print memory statistics if debug enabled
        if (gumus_debug) {
            MemoryStats::printReport();
        }
    }
    
    InterpretResult compileAndRun(const std::string& source) {
        try {
            Tokenizer tokenizer(source);
            auto tokens = tokenizer.tokenize();
            
            MemoryArena arena;
            Parser parser(tokens, arena);
            auto statements = parser.parse();
            
            Compiler compiler(OptimizationLevel::BASIC);
            *chunk = compiler.compile(statements);
            
            return vm->run(chunk.get());
        } catch (const GumusException& e) {
            return INTERPRET_COMPILE_ERROR;
        }
    }
};

// 🧪 Basit Aritmetik Testi
TEST_F(VMTest, SimpleArithmetic) {
    // Test: 2 + 3 * 4
    chunk->writeConstant(Value(2), 1);
    chunk->writeConstant(Value(3), 1);
    chunk->writeConstant(Value(4), 1);
    chunk->write(OP_MULTIPLY, 1);
    chunk->write(OP_ADD, 1);
    chunk->write(OP_RETURN, 1);
    
    InterpretResult result = vm->run(chunk.get());
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Stack Operations Testi
TEST_F(VMTest, StackOperations) {
    // Push values and pop them
    chunk->writeConstant(Value(42), 1);
    chunk->writeConstant(Value(24), 1);
    chunk->write(OP_POP, 1);  // Pop 24
    chunk->write(OP_RETURN, 1); // Return 42
    
    InterpretResult result = vm->run(chunk.get());
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Variable Operations Testi
TEST_F(VMTest, VariableOperations) {
    InterpretResult result = compileAndRun(R"(
        değişken x = 42
        x
    )");
    
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Function Call Testi
TEST_F(VMTest, FunctionCall) {
    InterpretResult result = compileAndRun(R"(
        fonksiyon topla(a, b) {
            dön a + b
        }
        
        topla(5, 3)
    )");
    
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Control Flow Testi
TEST_F(VMTest, ControlFlow) {
    InterpretResult result = compileAndRun(R"(
        değişken x = 10
        eğer (x > 5) {
            x = x * 2
        }
        x
    )");
    
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Loop Execution Testi
TEST_F(VMTest, LoopExecution) {
    InterpretResult result = compileAndRun(R"(
        değişken i = 0
        değişken toplam = 0
        
        döngü (i < 5) {
            toplam = toplam + i
            i = i + 1
        }
        
        toplam
    )");
    
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 String Operations Testi
TEST_F(VMTest, StringOperations) {
    InterpretResult result = compileAndRun(R"(
        değişken isim = "Dünya"
        değişken mesaj = "Merhaba " + isim
        mesaj
    )");
    
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Boolean Logic Testi
TEST_F(VMTest, BooleanLogic) {
    InterpretResult result = compileAndRun(R"(
        değişken a = doğru
        değişken b = yanlış
        değişken sonuc = a ve (değil b)
        sonuc
    )");
    
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Comparison Operations Testi
TEST_F(VMTest, ComparisonOperations) {
    InterpretResult result = compileAndRun(R"(
        değişken x = 10
        değişken y = 5
        değişken büyük = x > y
        değişken eşit = x == y
        büyük ve (değil eşit)
    )");
    
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Nested Function Calls Testi
TEST_F(VMTest, NestedFunctionCalls) {
    InterpretResult result = compileAndRun(R"(
        fonksiyon çarp(a, b) {
            dön a * b
        }
        
        fonksiyon kare(x) {
            dön çarp(x, x)
        }
        
        kare(5)
    )");
    
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Recursive Function Testi
TEST_F(VMTest, RecursiveFunction) {
    InterpretResult result = compileAndRun(R"(
        fonksiyon faktöriyel(n) {
            eğer (n <= 1) {
                dön 1
            } değilse {
                dön n * faktöriyel(n - 1)
            }
        }
        
        faktöriyel(5)
    )");
    
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Error Handling Testi
TEST_F(VMTest, RuntimeErrors) {
    // Division by zero
    InterpretResult result = compileAndRun("10 / 0");
    EXPECT_EQ(result, INTERPRET_RUNTIME_ERROR);
    
    // Undefined variable
    result = compileAndRun("undefined_var");
    EXPECT_EQ(result, INTERPRET_RUNTIME_ERROR);
}

// 🧪 Complex Expression Testi
TEST_F(VMTest, ComplexExpressions) {
    InterpretResult result = compileAndRun(R"(
        değişken a = 2
        değişken b = 3
        değişken c = 4
        
        // (a + b) * c - a * b + c / 2
        (a + b) * c - a * b + c / 2
    )");
    
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Memory Management Testi
TEST_F(VMTest, MemoryManagement) {
    // Create many objects to test GC integration
    InterpretResult result = compileAndRun(R"(
        fonksiyon createObjects() {
            değişken liste = []
            değişken i = 0
            
            döngü (i < 100) {
                liste[i] = "object_" + i
                i = i + 1
            }
            
            dön liste
        }
        
        createObjects()
    )");
    
    EXPECT_EQ(result, INTERPRET_OK);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
// 🎯 Performance and Memory Tests
TEST_F(VMTest, PerformanceTest) {
    auto start = std::chrono::high_resolution_clock::now();
    
    InterpretResult result = compileAndRun(R"(
        değişken toplam = 0
        değişken i = 0
        
        döngü (i < 1000) {
            toplam = toplam + i
            i = i + 1
        }
        
        toplam
    )");
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    EXPECT_EQ(result, INTERPRET_OK);
    
    // Performance should be reasonable (less than 10ms for 1000 iterations)
    EXPECT_LT(duration.count(), 10000);
    
    if (gumus_debug) {
        std::cout << "Performance test completed in " << duration.count() << " microseconds\n";
        
        auto stats = vm->getStats();
        std::cout << "VM Stats:\n";
        std::cout << "  Instructions executed: " << stats.instructionCount << "\n";
        std::cout << "  Stack size: " << stats.stackSize << "\n";
        std::cout << "  Memory usage: " << stats.memoryUsage << " bytes\n";
    }
}

// 🧪 Memory Pool Integration Test
TEST_F(VMTest, MemoryPoolIntegration) {
    size_t initialMemory = MemoryStats::getTotalMemoryUsage();
    
    InterpretResult result = compileAndRun(R"(
        değişken liste = []
        değişken i = 0
        
        döngü (i < 100) {
            liste[i] = "test_string_" + i
            i = i + 1
        }
        
        liste
    )");
    
    EXPECT_EQ(result, INTERPRET_OK);
    
    size_t finalMemory = MemoryStats::getTotalMemoryUsage();
    EXPECT_GT(finalMemory, initialMemory); // Memory should have increased
    
    if (gumus_debug) {
        std::cout << "Memory usage increased by " << (finalMemory - initialMemory) << " bytes\n";
    }
}

// 🎯 Stack Overflow Protection Test
TEST_F(VMTest, StackOverflowProtection) {
    InterpretResult result = compileAndRun(R"(
        fonksiyon sonsuzRekürsif() {
            sonsuzRekürsif()
        }
        
        sonsuzRekürsif()
    )");
    
    EXPECT_EQ(result, INTERPRET_RUNTIME_ERROR);
}

// 🧪 Bytecode Optimization Test
TEST_F(VMTest, BytecodeOptimization) {
    // Test that chunk optimization works
    chunk->write(OP_CONSTANT, 1);
    chunk->write(0, 1);
    chunk->write(OP_POP, 1);
    chunk->write(OP_POP, 1); // Redundant POP
    chunk->write(OP_NOP, 1); // Should be removed
    chunk->write(OP_RETURN, 1);
    
    size_t originalSize = chunk->code.size();
    chunk->optimize();
    size_t optimizedSize = chunk->code.size();
    
    EXPECT_LT(optimizedSize, originalSize);
    
    if (gumus_debug) {
        std::cout << "Bytecode optimized from " << originalSize 
                  << " to " << optimizedSize << " instructions\n";
    }
}