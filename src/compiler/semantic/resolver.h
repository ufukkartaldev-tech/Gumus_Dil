#ifndef GUMUS_RESOLVER_H
#define GUMUS_RESOLVER_H

#include <vector>
#include <string>
#include <unordered_map>
#include <memory>
#include "../parser/ast.h"

class Interpreter;

enum class FunctionType {
    NONE,
    FUNCTION,
    INITIALIZER,
    METHOD
};

enum class ClassType {
    NONE,
    CLASS,
    SUBCLASS
};

class Resolver : public ExprVisitor, public StmtVisitor {
public:
    Resolver(Interpreter& interpreter);
    void resolve(const std::vector<std::shared_ptr<Stmt>>& statements);

private:
    Interpreter& interpreter;
    std::vector<std::unordered_map<std::string, bool>> scopes;
    FunctionType currentFunction = FunctionType::NONE;
    ClassType currentClass = ClassType::NONE;

    void resolve(std::shared_ptr<Stmt> stmt);
    void resolve(std::shared_ptr<Expr> expr);
    void resolveLocal(Expr* expr, const Token& name);
    void resolveFunction(FunctionStmt* function, FunctionType type);
    
    void beginScope();
    void endScope();
    void declare(const Token& name);
    void define(const Token& name);

    // Stmt Visitors
    void visitBlockStmt(BlockStmt* stmt) override;
    void visitVarStmt(VarStmt* stmt) override;
    void visitFunctionStmt(FunctionStmt* stmt) override;
    void visitExpressionStmt(ExpressionStmt* stmt) override;
    void visitIfStmt(IfStmt* stmt) override;
    void visitPrintStmt(PrintStmt* stmt) override;
    void visitReturnStmt(ReturnStmt* stmt) override;
    void visitWhileStmt(WhileStmt* stmt) override;
    void visitForStmt(ForStmt* stmt) override;
    void visitBreakStmt(BreakStmt* stmt) override;
    void visitContinueStmt(ContinueStmt* stmt) override;
    void visitClassStmt(ClassStmt* stmt) override;
    void visitTryCatchStmt(TryCatchStmt* stmt) override;
    void visitModuleStmt(ModuleStmt* stmt) override;

    // Expr Visitors
    void visitVariableExpr(VariableExpr* expr) override;
    void visitAssignExpr(AssignExpr* expr) override;
    void visitBinaryExpr(BinaryExpr* expr) override;
    void visitCallExpr(CallExpr* expr) override;
    void visitLiteralExpr(LiteralExpr* expr) override;
    void visitLogicalExpr(LogicalExpr* expr) override;
    void visitUnaryExpr(UnaryExpr* expr) override;
    void visitListExpr(ListExpr* expr) override;
    void visitGetExpr(GetExpr* expr) override;
    void visitSetExpr(SetExpr* expr) override;
    void visitThisExpr(ThisExpr* expr) override;
    void visitSuperExpr(SuperExpr* expr) override;
    void visitPropertyExpr(PropertyExpr* expr) override;
    void visitIndexSetExpr(IndexSetExpr* expr) override;
    void visitScopeResolutionExpr(ScopeResolutionExpr* expr) override;
    void visitMapExpr(MapExpr* expr) override;
};

#endif
