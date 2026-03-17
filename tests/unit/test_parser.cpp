#include <gtest/gtest.h>
#include "../../src/compiler/parser/parser.h"
#include "../../src/compiler/lexer/tokenizer.h"
#include "../../src/compiler/interpreter/memory_arena.h"
#include <memory>

class ParserTest : public ::testing::Test {
protected:
    std::unique_ptr<MemoryArena> arena;
    
    void SetUp() override {
        arena = std::make_unique<MemoryArena>();
    }
    
    void TearDown() override {
        arena.reset();
    }
    
    std::vector<Stmt*> parse(const std::string& source) {
        Tokenizer tokenizer(source);
        auto tokens = tokenizer.tokenize();
        Parser parser(tokens, *arena);
        return parser.parse();
    }
};

// 🧪 Değişken Tanımlama Testi
TEST_F(ParserTest, VariableDeclaration) {
    auto statements = parse("değişken x = 42");
    
    ASSERT_EQ(statements.size(), 1);
    
    auto varStmt = dynamic_cast<VarStmt*>(statements[0]);
    ASSERT_NE(varStmt, nullptr);
    EXPECT_EQ(varStmt->name.value, "x");
    
    auto literal = dynamic_cast<LiteralExpr*>(varStmt->initializer);
    ASSERT_NE(literal, nullptr);
    EXPECT_EQ(std::get<int>(literal->value), 42);
}

// 🧪 Fonksiyon Tanımlama Testi
TEST_F(ParserTest, FunctionDeclaration) {
    auto statements = parse(R"(
        fonksiyon topla(a, b) {
            dön a + b
        }
    )");
    
    ASSERT_EQ(statements.size(), 1);
    
    auto funcStmt = dynamic_cast<FunctionStmt*>(statements[0]);
    ASSERT_NE(funcStmt, nullptr);
    EXPECT_EQ(funcStmt->name.value, "topla");
    EXPECT_EQ(funcStmt->params.size(), 2);
    EXPECT_EQ(funcStmt->params[0].value, "a");
    EXPECT_EQ(funcStmt->params[1].value, "b");
}

// 🧪 If-Else Testi
TEST_F(ParserTest, IfElseStatement) {
    auto statements = parse(R"(
        eğer (x > 5) {
            yazdır("büyük")
        } değilse {
            yazdır("küçük")
        }
    )");
    
    ASSERT_EQ(statements.size(), 1);
    
    auto ifStmt = dynamic_cast<IfStmt*>(statements[0]);
    ASSERT_NE(ifStmt, nullptr);
    ASSERT_NE(ifStmt->condition, nullptr);
    ASSERT_NE(ifStmt->thenBranch, nullptr);
    ASSERT_NE(ifStmt->elseBranch, nullptr);
}

// 🧪 Döngü Testi
TEST_F(ParserTest, WhileLoop) {
    auto statements = parse(R"(
        döngü (i < 10) {
            yazdır(i)
            i = i + 1
        }
    )");
    
    ASSERT_EQ(statements.size(), 1);
    
    auto whileStmt = dynamic_cast<WhileStmt*>(statements[0]);
    ASSERT_NE(whileStmt, nullptr);
    ASSERT_NE(whileStmt->condition, nullptr);
    ASSERT_NE(whileStmt->body, nullptr);
}

// 🧪 Binary Expression Testi
TEST_F(ParserTest, BinaryExpressions) {
    auto statements = parse("değişken sonuc = (a + b) * (c - d)");
    
    ASSERT_EQ(statements.size(), 1);
    
    auto varStmt = dynamic_cast<VarStmt*>(statements[0]);
    ASSERT_NE(varStmt, nullptr);
    
    auto binaryExpr = dynamic_cast<BinaryExpr*>(varStmt->initializer);
    ASSERT_NE(binaryExpr, nullptr);
    EXPECT_EQ(binaryExpr->op.type, TokenType::MULTIPLY);
}

// 🧪 Hata Durumları Testi
TEST_F(ParserTest, SyntaxErrors) {
    EXPECT_THROW(parse("değişken = 42"), GumusException); // Missing name
    EXPECT_THROW(parse("eğer x > 5 { }"), GumusException); // Missing parentheses
    EXPECT_THROW(parse("fonksiyon { }"), GumusException); // Missing name
}

// 🧪 Nested Expressions Testi
TEST_F(ParserTest, NestedExpressions) {
    auto statements = parse("değişken x = ((a + b) * c) / (d - e)");
    
    ASSERT_EQ(statements.size(), 1);
    
    auto varStmt = dynamic_cast<VarStmt*>(statements[0]);
    ASSERT_NE(varStmt, nullptr);
    
    // Check that it's a binary expression (division)
    auto divExpr = dynamic_cast<BinaryExpr*>(varStmt->initializer);
    ASSERT_NE(divExpr, nullptr);
    EXPECT_EQ(divExpr->op.type, TokenType::DIVIDE);
}

// 🧪 Function Call Testi
TEST_F(ParserTest, FunctionCall) {
    auto statements = parse("sonuc = topla(5, 10)");
    
    ASSERT_EQ(statements.size(), 1);
    
    auto exprStmt = dynamic_cast<ExpressionStmt*>(statements[0]);
    ASSERT_NE(exprStmt, nullptr);
    
    auto assignExpr = dynamic_cast<AssignExpr*>(exprStmt->expression);
    ASSERT_NE(assignExpr, nullptr);
    
    auto callExpr = dynamic_cast<CallExpr*>(assignExpr->value);
    ASSERT_NE(callExpr, nullptr);
    EXPECT_EQ(callExpr->arguments.size(), 2);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}