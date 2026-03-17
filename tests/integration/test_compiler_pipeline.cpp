#include <gtest/gtest.h>
#include "../../src/compiler/lexer/tokenizer.h"
#include "../../src/compiler/parser/parser.h"
#include "../../src/compiler/interpreter/interpreter.h"
#include "../../src/compiler/vm/compiler.h"
#include "../../src/compiler/vm/vm.h"
#include "../../src/compiler/semantic/resolver.h"
#include <sstream>

class CompilerPipelineTest : public ::testing::Test {
protected:
    std::unique_ptr<Interpreter> interpreter;
    std::unique_ptr<VM> vm;
    std::ostringstream output;
    
    void SetUp() override {
        interpreter = std::make_unique<Interpreter>();
        vm = std::make_unique<VM>();
        interpreter->setOutputStream(&output);
    }
    
    void TearDown() override {
        interpreter.reset();
        vm.reset();
    }
    
    std::string runInterpreter(const std::string& source) {
        output.str("");
        output.clear();
        
        try {
            // Full pipeline: Tokenizer -> Parser -> Resolver -> Interpreter
            Tokenizer tokenizer(source);
            auto tokens = tokenizer.tokenize();
            
            Parser parser(tokens, interpreter->astArena);
            auto statements = parser.parse();
            
            Resolver resolver(*interpreter);
            resolver.resolve(statements);
            
            for (auto stmt : statements) {
                interpreter->execute(stmt);
            }
        } catch (const GumusException& e) {
            return "ERROR: " + std::string(e.what());
        }
        
        return output.str();
    }
    
    InterpretResult runVM(const std::string& source) {
        try {
            // Full pipeline: Tokenizer -> Parser -> Compiler -> VM
            Tokenizer tokenizer(source);
            auto tokens = tokenizer.tokenize();
            
            MemoryArena arena;
            Parser parser(tokens, arena);
            auto statements = parser.parse();
            
            Compiler compiler;
            auto chunk = compiler.compile(statements);
            
            return vm->run(&chunk);
        } catch (const GumusException& e) {
            return INTERPRET_COMPILE_ERROR;
        }
    }
};

// 🧪 Complete Program Execution Testi
TEST_F(CompilerPipelineTest, CompleteProgramExecution) {
    std::string program = R"(
        // Fibonacci hesaplama programı
        fonksiyon fibonacci(n) {
            eğer (n <= 1) {
                dön n
            } değilse {
                dön fibonacci(n - 1) + fibonacci(n - 2)
            }
        }
        
        değişken i = 0
        döngü (i <= 10) {
            yazdır("F(" + i + ") = " + fibonacci(i))
            i = i + 1
        }
    )";
    
    std::string result = runInterpreter(program);
    
    // Check that fibonacci sequence is calculated correctly
    EXPECT_TRUE(result.find("F(0) = 0") != std::string::npos);
    EXPECT_TRUE(result.find("F(1) = 1") != std::string::npos);
    EXPECT_TRUE(result.find("F(5) = 5") != std::string::npos);
    EXPECT_TRUE(result.find("F(10) = 55") != std::string::npos);
}

// 🧪 Interpreter vs VM Consistency Testi
TEST_F(CompilerPipelineTest, InterpreterVMConsistency) {
    std::string program = R"(
        değişken x = 10
        değişken y = 20
        değişken sonuc = (x + y) * 2 - x
        yazdır(sonuc)
    )";
    
    std::string interpreterResult = runInterpreter(program);
    InterpretResult vmResult = runVM(program);
    
    // Both should execute successfully
    EXPECT_FALSE(interpreterResult.find("ERROR") != std::string::npos);
    EXPECT_EQ(vmResult, INTERPRET_OK);
    
    // Result should be 50: (10 + 20) * 2 - 10 = 60 - 10 = 50
    EXPECT_TRUE(interpreterResult.find("50") != std::string::npos);
}

// 🧪 Complex Control Flow Testi
TEST_F(CompilerPipelineTest, ComplexControlFlow) {
    std::string program = R"(
        fonksiyon isPrime(n) {
            eğer (n < 2) {
                dön yanlış
            }
            
            değişken i = 2
            döngü (i * i <= n) {
                eğer (n % i == 0) {
                    dön yanlış
                }
                i = i + 1
            }
            
            dön doğru
        }
        
        değişken count = 0
        değişken num = 2
        
        döngü (count < 5) {
            eğer (isPrime(num)) {
                yazdır("Prime: " + num)
                count = count + 1
            }
            num = num + 1
        }
    )";
    
    std::string result = runInterpreter(program);
    
    // Should find first 5 primes: 2, 3, 5, 7, 11
    EXPECT_TRUE(result.find("Prime: 2") != std::string::npos);
    EXPECT_TRUE(result.find("Prime: 3") != std::string::npos);
    EXPECT_TRUE(result.find("Prime: 5") != std::string::npos);
    EXPECT_TRUE(result.find("Prime: 7") != std::string::npos);
    EXPECT_TRUE(result.find("Prime: 11") != std::string::npos);
}

// 🧪 String Processing Testi
TEST_F(CompilerPipelineTest, StringProcessing) {
    std::string program = R"(
        fonksiyon reverseString(str) {
            değişken result = ""
            değişken i = str.length() - 1
            
            döngü (i >= 0) {
                result = result + str[i]
                i = i - 1
            }
            
            dön result
        }
        
        değişken text = "Merhaba"
        değişken reversed = reverseString(text)
        yazdır("Original: " + text)
        yazdır("Reversed: " + reversed)
    )";
    
    std::string result = runInterpreter(program);
    
    EXPECT_TRUE(result.find("Original: Merhaba") != std::string::npos);
    EXPECT_TRUE(result.find("Reversed: abahreM") != std::string::npos);
}

// 🧪 Nested Function Calls Testi
TEST_F(CompilerPipelineTest, NestedFunctionCalls) {
    std::string program = R"(
        fonksiyon add(a, b) {
            dön a + b
        }
        
        fonksiyon multiply(a, b) {
            dön a * b
        }
        
        fonksiyon calculate(x, y, z) {
            dön multiply(add(x, y), z)
        }
        
        değişken result = calculate(5, 3, 2)
        yazdır("Result: " + result)
    )";
    
    std::string result = runInterpreter(program);
    
    // (5 + 3) * 2 = 16
    EXPECT_TRUE(result.find("Result: 16") != std::string::npos);
}

// 🧪 Error Recovery Testi
TEST_F(CompilerPipelineTest, ErrorRecovery) {
    // Syntax error
    std::string syntaxError = "değişken x = ";
    std::string result = runInterpreter(syntaxError);
    EXPECT_TRUE(result.find("ERROR") != std::string::npos);
    
    // Runtime error
    std::string runtimeError = "yazdır(undefined_variable)";
    result = runInterpreter(runtimeError);
    EXPECT_TRUE(result.find("ERROR") != std::string::npos);
    
    // Type error
    std::string typeError = R"(
        değişken x = "string"
        yazdır(x + 5)
    )";
    result = runInterpreter(typeError);
    // Should handle string + number concatenation
    EXPECT_TRUE(result.find("string5") != std::string::npos || result.find("ERROR") != std::string::npos);
}

// 🧪 Memory Management Integration Testi
TEST_F(CompilerPipelineTest, MemoryManagementIntegration) {
    std::string program = R"(
        fonksiyon createLargeObject() {
            değişken obj = {}
            değişken i = 0
            
            döngü (i < 100) {
                obj["key" + i] = "value" + i
                i = i + 1
            }
            
            dön obj
        }
        
        değişken objects = []
        değişken i = 0
        
        döngü (i < 10) {
            objects[i] = createLargeObject()
            i = i + 1
        }
        
        yazdır("Created " + objects.length() + " objects")
    )";
    
    std::string result = runInterpreter(program);
    
    // Should complete without memory issues
    EXPECT_TRUE(result.find("Created 10 objects") != std::string::npos);
}

// 🧪 Scope Resolution Testi
TEST_F(CompilerPipelineTest, ScopeResolution) {
    std::string program = R"(
        değişken global = "global_value"
        
        fonksiyon outer() {
            değişken outer_var = "outer_value"
            
            fonksiyon inner() {
                değişken inner_var = "inner_value"
                yazdır("Inner: " + inner_var)
                yazdır("Outer: " + outer_var)
                yazdır("Global: " + global)
            }
            
            inner()
            yazdır("From outer: " + outer_var)
        }
        
        outer()
        yazdır("From global: " + global)
    )";
    
    std::string result = runInterpreter(program);
    
    EXPECT_TRUE(result.find("Inner: inner_value") != std::string::npos);
    EXPECT_TRUE(result.find("Outer: outer_value") != std::string::npos);
    EXPECT_TRUE(result.find("Global: global_value") != std::string::npos);
    EXPECT_TRUE(result.find("From outer: outer_value") != std::string::npos);
    EXPECT_TRUE(result.find("From global: global_value") != std::string::npos);
}

// 🧪 Performance Stress Testi
TEST_F(CompilerPipelineTest, PerformanceStressTest) {
    std::string program = R"(
        fonksiyon heavyComputation(n) {
            değişken result = 0
            değişken i = 0
            
            döngü (i < n) {
                değişken j = 0
                döngü (j < 100) {
                    result = result + (i * j)
                    j = j + 1
                }
                i = i + 1
            }
            
            dön result
        }
        
        değişken start = getCurrentTime()
        değişken result = heavyComputation(50)
        değişken end = getCurrentTime()
        
        yazdır("Result: " + result)
        yazdır("Time: " + (end - start) + "ms")
    )";
    
    // This test should complete within reasonable time
    auto start = std::chrono::high_resolution_clock::now();
    std::string result = runInterpreter(program);
    auto end = std::chrono::high_resolution_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    // Should complete within 5 seconds
    EXPECT_LT(duration.count(), 5000);
    EXPECT_TRUE(result.find("Result:") != std::string::npos);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}