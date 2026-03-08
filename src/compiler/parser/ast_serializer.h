#ifndef GUMUS_AST_SERIALIZER_H
#define GUMUS_AST_SERIALIZER_H

#include "ast.h"
#include <sstream>
#include <string>
#include <vector>

class AstJsonSerializer : public ExprVisitor, public StmtVisitor {
public:
    std::string serialize(AstNode* node) {
        if (!node) return "null";
        ss.str(""); ss.clear();
        if (auto* expr = dynamic_cast<Expr*>(node)) expr->accept(*this);
        else if (auto* stmt = dynamic_cast<Stmt*>(node)) stmt->accept(*this);
        return ss.str();
    }

    std::string serialize(const std::vector<Stmt*>& statements) {
        ss.str(""); ss.clear();
        ss << "[";
        for (size_t i = 0; i < statements.size(); ++i) {
            statements[i]->accept(*this);
            if (i < statements.size() - 1) ss << ", ";
        }
        ss << "]";
        return ss.str();
    }

private:
    std::ostringstream ss;

    static std::string jsonEscape(const std::string& s) {
        std::string res = "";
        for (char c : s) {
            if (c == '"') res += "\\\"";
            else if (c == '\\') res += "\\\\";
            else if (c == '\n') res += "\\n";
            else if (c == '\r') res += "\\r";
            else if (c == '\t') res += "\\t";
            else res += c;
        }
        return res;
    }

    // --- Expr Visitors ---
    void visitLiteralExpr(LiteralExpr* expr) override {
        ss << "{ \"type\": \"Literal\", \"line\": " << expr->value.line 
           << ", \"value\": \"" << jsonEscape(expr->value.value) << "\", \"children\": [] }";
    }

    void visitBinaryExpr(BinaryExpr* expr) override {
        ss << "{ \"type\": \"BinaryExpr\", \"line\": " << expr->op.line 
           << ", \"value\": \"" << jsonEscape(expr->op.value) << "\", \"children\": [";
        expr->left->accept(*this);
        ss << ", ";
        expr->right->accept(*this);
        ss << "] }";
    }

    void visitVariableExpr(VariableExpr* expr) override {
        ss << "{ \"type\": \"Variable\", \"line\": " << expr->name.line 
           << ", \"value\": \"" << jsonEscape(expr->name.value) 
           << "\", \"distance\": " << expr->distance << ", \"children\": [] }";
    }

    void visitUnaryExpr(UnaryExpr* expr) override {
        ss << "{ \"type\": \"UnaryExpr\", \"line\": " << expr->op.line 
           << ", \"value\": \"" << jsonEscape(expr->op.value) << "\", \"children\": [";
        expr->right->accept(*this);
        ss << "] }";
    }

    void visitLogicalExpr(LogicalExpr* expr) override {
        ss << "{ \"type\": \"LogicalExpr\", \"line\": " << expr->op.line 
           << ", \"value\": \"" << jsonEscape(expr->op.value) << "\", \"children\": [";
        expr->left->accept(*this);
        ss << ", ";
        expr->right->accept(*this);
        ss << "] }";
    }

    void visitAssignExpr(AssignExpr* expr) override {
        ss << "{ \"type\": \"AssignExpr\", \"line\": " << expr->name.line 
           << ", \"value\": \"" << jsonEscape(expr->name.value) 
           << "\", \"distance\": " << expr->distance << ", \"children\": [";
        expr->value->accept(*this);
        ss << "] }";
    }

    void visitListExpr(ListExpr* expr) override {
        ss << "{ \"type\": \"ListExpr\", \"line\": 0, \"value\": \"[]\", \"children\": [";
        for (size_t i = 0; i < expr->elements.size(); ++i) {
            expr->elements[i]->accept(*this);
            if (i < expr->elements.size() - 1) ss << ", ";
        }
        ss << "] }";
    }

    void visitGetExpr(GetExpr* expr) override {
        ss << "{ \"type\": \"IndexGetExpr\", \"line\": " << expr->bracket.line 
           << ", \"value\": \"[]\", \"children\": [";
        expr->object->accept(*this);
        ss << ", ";
        expr->index->accept(*this);
        ss << "] }";
    }

    void visitPropertyExpr(PropertyExpr* expr) override {
        ss << "{ \"type\": \"PropertyExpr\", \"line\": " << expr->name.line 
           << ", \"value\": \".\" + \"" << jsonEscape(expr->name.value) << "\", \"children\": [";
        expr->object->accept(*this);
        ss << "] }";
    }

    void visitSetExpr(SetExpr* expr) override {
        ss << "{ \"type\": \"SetExpr\", \"line\": " << expr->name.line 
           << ", \"value\": \"" << jsonEscape(expr->name.value) << "\", \"children\": [";
        expr->object->accept(*this);
        ss << ", ";
        expr->value->accept(*this);
        ss << "] }";
    }

    void visitIndexSetExpr(IndexSetExpr* expr) override {
        ss << "{ \"type\": \"IndexSetExpr\", \"line\": " << expr->bracket.line 
           << ", \"value\": \"[]=\", \"children\": [";
        expr->object->accept(*this);
        ss << ", ";
        expr->index->accept(*this);
        ss << ", ";
        expr->value->accept(*this);
        ss << "] }";
    }

    void visitThisExpr(ThisExpr* expr) override {
        ss << "{ \"type\": \"ThisExpr\", \"line\": " << expr->keyword.line 
           << ", \"value\": \"oz\", \"distance\": " << expr->distance << ", \"children\": [] }";
    }

    void visitSuperExpr(SuperExpr* expr) override {
        ss << "{ \"type\": \"SuperExpr\", \"line\": " << expr->keyword.line 
           << ", \"value\": \"ata." << jsonEscape(expr->method.value) << "\", \"distance\": " 
           << expr->distance << ", \"children\": [] }";
    }

    void visitCallExpr(CallExpr* expr) override {
        ss << "{ \"type\": \"CallExpr\", \"line\": " << expr->paren.line 
           << ", \"value\": \"()\", \"children\": [";
        expr->callee->accept(*this);
        for (const auto& arg : expr->arguments) {
            ss << ", ";
            arg->accept(*this);
        }
        ss << "] }";
    }

    void visitScopeResolutionExpr(ScopeResolutionExpr* expr) override {
        ss << "{ \"type\": \"ScopeExpr\", \"line\": " << expr->moduleName.line 
           << ", \"value\": \"" << jsonEscape(expr->moduleName.value) << "::" 
           << jsonEscape(expr->name.value) << "\", \"children\": [] }";
    }

    void visitMapExpr(MapExpr* expr) override {
        ss << "{ \"type\": \"MapExpr\", \"line\": 0, \"value\": \"{}\", \"children\": [";
        for (size_t i = 0; i < expr->keys.size(); ++i) {
            ss << "{ \"type\": \"Pair\", \"children\": [";
            expr->keys[i]->accept(*this);
            ss << ", ";
            expr->values[i]->accept(*this);
            ss << "] }";
            if (i < expr->keys.size() - 1) ss << ", ";
        }
        ss << "] }";
    }

    // --- Stmt Visitors ---
    void visitExpressionStmt(ExpressionStmt* stmt) override {
        ss << "{ \"type\": \"ExpressionStmt\", \"line\": 0, \"value\": \"\", \"children\": [";
        stmt->expression->accept(*this);
        ss << "] }";
    }

    void visitPrintStmt(PrintStmt* stmt) override {
        ss << "{ \"type\": \"PrintStmt\", \"line\": 0, \"value\": \"yazdir\", \"children\": [";
        stmt->expression->accept(*this);
        ss << "] }";
    }

    void visitBlockStmt(BlockStmt* stmt) override {
        ss << "{ \"type\": \"BlockStmt\", \"line\": 0, \"value\": \"{}\", \"children\": [";
        for (size_t i = 0; i < stmt->statements.size(); ++i) {
            stmt->statements[i]->accept(*this);
            if (i < stmt->statements.size() - 1) ss << ", ";
        }
        ss << "] }";
    }

    void visitIfStmt(IfStmt* stmt) override {
        ss << "{ \"type\": \"IfStmt\", \"line\": 0, \"value\": \"eger\", \"children\": [";
        stmt->condition->accept(*this);
        ss << ", ";
        stmt->thenBranch->accept(*this);
        if (stmt->elseBranch) {
            ss << ", ";
            stmt->elseBranch->accept(*this);
        }
        ss << "] }";
    }

    void visitWhileStmt(WhileStmt* stmt) override {
        ss << "{ \"type\": \"WhileStmt\", \"line\": 0, \"value\": \"dongu\", \"children\": [";
        stmt->condition->accept(*this);
        ss << ", ";
        stmt->body->accept(*this);
        ss << "] }";
    }

    void visitBreakStmt(BreakStmt* stmt) override {
        ss << "{ \"type\": \"BreakStmt\", \"line\": " << stmt->keyword.line << ", \"value\": \"kir\", \"children\": [] }";
    }

    void visitContinueStmt(ContinueStmt* stmt) override {
        ss << "{ \"type\": \"ContinueStmt\", \"line\": " << stmt->keyword.line << ", \"value\": \"devam\", \"children\": [] }";
    }

    void visitTryCatchStmt(TryCatchStmt* stmt) override {
        ss << "{ \"type\": \"TryCatchStmt\", \"line\": 0, \"value\": \"deneme\", \"children\": [";
        stmt->tryBlock->accept(*this);
        ss << ", ";
        stmt->catchBlock->accept(*this);
        ss << "] }";
    }

    void visitFunctionStmt(FunctionStmt* stmt) override {
        ss << "{ \"type\": \"FunctionStmt\", \"line\": " << stmt->name.line 
           << ", \"value\": \"" << jsonEscape(stmt->name.value) << "\", \"children\": [";
        ss << "{ \"type\": \"BlockStmt\", \"line\": " << stmt->name.line << ", \"value\": \"body\", \"children\": [";
        for (size_t i = 0; i < stmt->body.size(); ++i) {
            stmt->body[i]->accept(*this);
            if (i < stmt->body.size() - 1) ss << ", ";
        }
        ss << "] }] }";
    }

    void visitClassStmt(ClassStmt* stmt) override {
        ss << "{ \"type\": \"ClassStmt\", \"line\": " << stmt->name.line 
           << ", \"value\": \"" << jsonEscape(stmt->name.value) << "\", \"children\": [";
        bool first = true;
        if (stmt->superclass) { stmt->superclass->accept(*this); first = false; }
        for (const auto& m : stmt->methods) {
            if (!first) ss << ", ";
            m->accept(*this);
            first = false;
        }
        ss << "] }";
    }

    void visitVarStmt(VarStmt* stmt) override {
        ss << "{ \"type\": \"VarStmt\", \"line\": " << stmt->name.line 
           << ", \"value\": \"" << jsonEscape(stmt->name.value) << "\", \"children\": [";
        if (stmt->initializer) stmt->initializer->accept(*this);
        ss << "] }";
    }

    void visitReturnStmt(ReturnStmt* stmt) override {
        ss << "{ \"type\": \"ReturnStmt\", \"line\": " << stmt->keyword.line 
           << ", \"value\": \"don\", \"children\": [";
        if (stmt->value) stmt->value->accept(*this);
        ss << "] }";
    }

    void visitModuleStmt(ModuleStmt* stmt) override {
        ss << "{ \"type\": \"ModuleStmt\", \"line\": " << stmt->name.line 
           << ", \"value\": \"" << jsonEscape(stmt->name.value) << "\", \"children\": [";
        for (size_t i = 0; i < stmt->statements.size(); ++i) {
            stmt->statements[i]->accept(*this);
            if (i < stmt->statements.size() - 1) ss << ", ";
        }
        ss << "] }";
    }

    void visitForStmt(ForStmt* stmt) override {
        ss << "{ \"type\": \"ForStmt\", \"line\": " << stmt->keyword.line << ", \"value\": \"dongu\", \"children\": [";
        bool first = true;
        if (stmt->initializer) { stmt->initializer->accept(*this); first = false; }
        if (stmt->condition) { if (!first) ss << ", "; stmt->condition->accept(*this); first = false; }
        if (stmt->increment) { if (!first) ss << ", "; stmt->increment->accept(*this); first = false; }
        if (stmt->body) { if (!first) ss << ", "; stmt->body->accept(*this); }
        ss << "] }";
    }
};

class AstStringifier : public ExprVisitor, public StmtVisitor {
public:
    std::string stringify(AstNode* node) {
        if (!node) return "null";
        ss.str(""); ss.clear();
        if (auto* expr = dynamic_cast<Expr*>(node)) expr->accept(*this);
        else if (auto* stmt = dynamic_cast<Stmt*>(node)) stmt->accept(*this);
        return ss.str();
    }

private:
    std::ostringstream ss;

    void visitLiteralExpr(LiteralExpr* expr) override { ss << "Literal(" << expr->value.value << ")"; }
    void visitBinaryExpr(BinaryExpr* expr) override { 
        ss << "Binary(";
        expr->left->accept(*this);
        ss << " " << expr->op.value << " ";
        expr->right->accept(*this);
        ss << ")";
    }
    void visitVariableExpr(VariableExpr* expr) override { ss << "Var(" << expr->name.value << ")"; }
    void visitUnaryExpr(UnaryExpr* expr) override { 
        ss << "Unary(" << expr->op.value << " ";
        expr->right->accept(*this);
        ss << ")";
    }
    void visitLogicalExpr(LogicalExpr* expr) override { 
        ss << "Logical(";
        expr->left->accept(*this);
        ss << " " << expr->op.value << " ";
        expr->right->accept(*this);
        ss << ")";
    }
    void visitAssignExpr(AssignExpr* expr) override { 
        ss << "Assign(" << expr->name.value << " = ";
        expr->value->accept(*this);
        ss << ")";
    }
    void visitListExpr(ListExpr*) override { ss << "List"; }
    void visitGetExpr(GetExpr*) override { ss << "Get"; }
    void visitIndexSetExpr(IndexSetExpr*) override { ss << "IndexSet"; }
    void visitPropertyExpr(PropertyExpr*) override { ss << "Prop"; }
    void visitSetExpr(SetExpr*) override { ss << "Set"; }
    void visitThisExpr(ThisExpr*) override { ss << "oz"; }
    void visitSuperExpr(SuperExpr*) override { ss << "ata"; }
    void visitCallExpr(CallExpr*) override { ss << "Call"; }
    void visitScopeResolutionExpr(ScopeResolutionExpr*) override { ss << "Scope"; }
    void visitMapExpr(MapExpr*) override { ss << "Map"; }

    void visitExpressionStmt(ExpressionStmt* stmt) override { 
        ss << "ExprStmt(";
        stmt->expression->accept(*this);
        ss << ")";
    }
    void visitPrintStmt(PrintStmt* stmt) override { 
        ss << "Print(";
        stmt->expression->accept(*this);
        ss << ")";
    }
    void visitBlockStmt(BlockStmt*) override { ss << "Block"; }
    void visitIfStmt(IfStmt*) override { ss << "If"; }
    void visitWhileStmt(WhileStmt*) override { ss << "While"; }
    void visitBreakStmt(BreakStmt*) override { ss << "Break"; }
    void visitContinueStmt(ContinueStmt*) override { ss << "Continue"; }
    void visitTryCatchStmt(TryCatchStmt*) override { ss << "TryCatch"; }
    void visitFunctionStmt(FunctionStmt*) override { ss << "Function"; }
    void visitClassStmt(ClassStmt*) override { ss << "Class"; }
    void visitVarStmt(VarStmt*) override { ss << "Var"; }
    void visitReturnStmt(ReturnStmt*) override { ss << "Return"; }
    void visitModuleStmt(ModuleStmt*) override { ss << "Module"; }
    void visitForStmt(ForStmt*) override { ss << "For"; }
};

#endif
