#ifndef COMPILER_H
#define COMPILER_H

#include <vector>
#include "../parser/ast.h"
#include "chunk.h"
#include "op_code.h"

class Compiler : public ExprVisitor, public StmtVisitor {
public:
    Compiler();
    Chunk* compile(const std::vector<Stmt*>& statements);

    // StmtVisitor
    void visitExpressionStmt(ExpressionStmt* stmt) override;
    void visitPrintStmt(PrintStmt* stmt) override;
    void visitBlockStmt(BlockStmt* stmt) override;
    void visitIfStmt(IfStmt* stmt) override;
    void visitWhileStmt(WhileStmt* stmt) override;
    void visitBreakStmt(BreakStmt* stmt) override;
    void visitContinueStmt(ContinueStmt* stmt) override;
    void visitForStmt(ForStmt* stmt) override;
    void visitFunctionStmt(FunctionStmt* stmt) override;
    void visitReturnStmt(ReturnStmt* stmt) override;
    void visitVarStmt(VarStmt* stmt) override;
    void visitClassStmt(ClassStmt* stmt) override;
    void visitTryCatchStmt(TryCatchStmt* stmt) override;
    void visitModuleStmt(ModuleStmt* stmt) override;

    // ExprVisitor
    void visitLiteralExpr(LiteralExpr* expr) override;
    void visitBinaryExpr(BinaryExpr* expr) override;
    void visitUnaryExpr(UnaryExpr* expr) override;
    void visitLogicalExpr(LogicalExpr* expr) override;
    void visitVariableExpr(VariableExpr* expr) override;
    void visitAssignExpr(AssignExpr* expr) override;
    void visitCallExpr(CallExpr* expr) override;
    void visitGetExpr(GetExpr* expr) override;
    void visitSetExpr(SetExpr* expr) override;
    void visitThisExpr(ThisExpr* expr) override;
    void visitSuperExpr(SuperExpr* expr) override;
    void visitScopeResolutionExpr(ScopeResolutionExpr* expr) override;
    void visitListExpr(ListExpr* expr) override;
    void visitMapExpr(MapExpr* expr) override;
    void visitPropertyExpr(PropertyExpr* expr) override;
    void visitIndexSetExpr(IndexSetExpr* expr) override;

private:
    Chunk* currentChunk;
    void emitByte(uint8_t byte, int line);
    void emitBytes(uint8_t byte1, uint8_t byte2, int line);
    void emitConstant(Value value, int line);
    int emitJump(uint8_t instruction, int line);
    void patchJump(int offset);
};

#endif // COMPILER_H
