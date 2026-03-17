#include <gtest/gtest.h>
#include "../../src/compiler/vm/vm.h"
#include "../../src/compiler/vm/chunk.h"
#include "../../src/compiler/vm/compiler.h"
#include "../../src/compiler/lexer/tokenizer.h"
#include "../../src/compiler/parser/parser.h"

class VMTest : public ::testing::Test {
protected:
    std::unique_ptr<VM> vm;
    std::unique_ptr<Chunk> chunk;
    
    void SetUp() override {
        vm = std::make_unique<VM>();
        chunk = std::make_unique<Chunk>();
    }
    
    void TearDown() override {
        vm.reset();
        chunk.reset();
    }
    
    InterpretResult compileAndRun(const std::string& source) {
        try {
            Tokenizer tokenizer(source);
            auto tokens = tokenizer.tokenize();
            
            MemoryArena arena;
            Parser parser(tokens, arena);
            auto statements = parser.parse();
            
            Compiler compiler;
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