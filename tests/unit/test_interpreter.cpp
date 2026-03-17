#include <gtest/gtest.h>
#include "../../src/compiler/interpreter/interpreter.h"
#include "../../src/compiler/parser/parser.h"
#include "../../src/compiler/lexer/tokenizer.h"
#include <sstream>

class InterpreterTest : public ::testing::Test {
protected:
    std::unique_ptr<Interpreter> interpreter;
    std::ostringstream output;
    
    void SetUp() override {
        interpreter = std::make_unique<Interpreter>();
        // Redirect output for testing
        interpreter->setOutputStream(&output);
    }
    
    void TearDown() override {
        interpreter.reset();
    }
    
    std::string execute(const std::string& source) {
        output.str("");
        output.clear();
        
        try {
            Tokenizer tokenizer(source);
            auto tokens = tokenizer.tokenize();
            Parser parser(tokens, interpreter->astArena);
            auto statements = parser.parse();
            
            for (auto stmt : statements) {
                interpreter->execute(stmt);
            }
        } catch (const GumusException& e) {
            return "ERROR: " + std::string(e.what());
        }
        
        return output.str();
    }
};

// 🧪 Basit Değişken Testi
TEST_F(InterpreterTest, SimpleVariable) {
    std::string result = execute(R"(
        değişken x = 42
        yazdır(x)
    )");
    
    EXPECT_EQ(result, "42\n");
}

// 🧪 Aritmetik İşlemler Testi
TEST_F(InterpreterTest, ArithmeticOperations) {
    std::string result = execute(R"(
        değişken a = 10
        değişken b = 5
        yazdır(a + b)
        yazdır(a - b)
        yazdır(a * b)
        yazdır(a / b)
    )");
    
    EXPECT_EQ(result, "15\n5\n50\n2\n");
}

// 🧪 String İşlemleri Testi
TEST_F(InterpreterTest, StringOperations) {
    std::string result = execute(R"(
        değişken isim = "Dünya"
        yazdır("Merhaba " + isim + "!")
    )");
    
    EXPECT_EQ(result, "Merhaba Dünya!\n");
}

// 🧪 If-Else Testi
TEST_F(InterpreterTest, IfElseLogic) {
    std::string result = execute(R"(
        değişken x = 10
        eğer (x > 5) {
            yazdır("büyük")
        } değilse {
            yazdır("küçük")
        }
    )");
    
    EXPECT_EQ(result, "büyük\n");
}

// 🧪 Döngü Testi
TEST_F(InterpreterTest, WhileLoop) {
    std::string result = execute(R"(
        değişken i = 0
        döngü (i < 3) {
            yazdır(i)
            i = i + 1
        }
    )");
    
    EXPECT_EQ(result, "0\n1\n2\n");
}

// 🧪 Fonksiyon Tanımlama ve Çağırma Testi
TEST_F(InterpreterTest, FunctionDefinitionAndCall) {
    std::string result = execute(R"(
        fonksiyon topla(a, b) {
            dön a + b
        }
        
        değişken sonuc = topla(5, 3)
        yazdır(sonuc)
    )");
    
    EXPECT_EQ(result, "8\n");
}

// 🧪 Recursive Function Testi
TEST_F(InterpreterTest, RecursiveFunction) {
    std::string result = execute(R"(
        fonksiyon faktöriyel(n) {
            eğer (n <= 1) {
                dön 1
            } değilse {
                dön n * faktöriyel(n - 1)
            }
        }
        
        yazdır(faktöriyel(5))
    )");
    
    EXPECT_EQ(result, "120\n");
}

// 🧪 Scope Testi
TEST_F(InterpreterTest, VariableScope) {
    std::string result = execute(R"(
        değişken x = "global"
        
        fonksiyon test() {
            değişken x = "local"
            yazdır(x)
        }
        
        test()
        yazdır(x)
    )");
    
    EXPECT_EQ(result, "local\nglobal\n");
}

// 🧪 Boolean Logic Testi
TEST_F(InterpreterTest, BooleanLogic) {
    std::string result = execute(R"(
        değişken a = doğru
        değişken b = yanlış
        
        yazdır(a ve b)
        yazdır(a veya b)
        yazdır(değil a)
    )");
    
    EXPECT_EQ(result, "yanlış\ndoğru\nyanlış\n");
}

// 🧪 Comparison Operations Testi
TEST_F(InterpreterTest, ComparisonOperations) {
    std::string result = execute(R"(
        değişken x = 10
        değişken y = 5
        
        yazdır(x > y)
        yazdır(x < y)
        yazdır(x == y)
        yazdır(x != y)
        yazdır(x >= y)
        yazdır(x <= y)
    )");
    
    EXPECT_EQ(result, "doğru\nyanlış\nyanlış\ndoğru\ndoğru\nyanlış\n");
}

// 🧪 Error Handling Testi
TEST_F(InterpreterTest, RuntimeErrors) {
    // Division by zero
    std::string result = execute("yazdır(10 / 0)");
    EXPECT_TRUE(result.find("ERROR") != std::string::npos);
    
    // Undefined variable
    result = execute("yazdır(undefined_var)");
    EXPECT_TRUE(result.find("ERROR") != std::string::npos);
    
    // Wrong number of arguments
    result = execute(R"(
        fonksiyon test(a, b) { dön a + b }
        yazdır(test(1))
    )");
    EXPECT_TRUE(result.find("ERROR") != std::string::npos);
}

// 🧪 Complex Expression Testi
TEST_F(InterpreterTest, ComplexExpressions) {
    std::string result = execute(R"(
        değişken x = 2
        değişken y = 3
        değişken z = 4
        
        değişken sonuc = (x + y) * z - (x * y)
        yazdır(sonuc)
    )");
    
    EXPECT_EQ(result, "14\n"); // (2+3)*4 - (2*3) = 20 - 6 = 14
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}