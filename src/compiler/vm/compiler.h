#ifndef COMPILER_H
#define COMPILER_H

#include <vector>
#include <map>
#include <string>
#include <stack>
#include "../parser/ast.h"
#include "chunk.h"
#include "op_code.h"
#include "../interpreter/value.h"

// 🎯 Compiler optimization levels
enum class OptimizationLevel {
    NONE,       // No optimizations
    BASIC,      // Basic optimizations (constant folding, dead code elimination)
    ADVANCED,   // Advanced optimizations (loop unrolling, inlining)
    AGGRESSIVE  // Aggressive optimizations (may increase compile time)
};

// 📊 Compilation statistics
struct CompilerStats {
    size_t instructionsGenerated = 0;
    size_t constantsGenerated = 0;
    size_t optimizationsApplied = 0;
    double compilationTime = 0.0;
    size_t bytecodeSize = 0;
};

class Compiler : public ExprVisitor, public StmtVisitor {
public:
    Compiler(OptimizationLevel level = OptimizationLevel::BASIC);
    ~Compiler();
    
    Chunk compile(const std::vector<Stmt*>& statements);
    
    // 📊 Statistics and debugging
    CompilerStats getStats() const { return stats; }
    void setOptimizationLevel(OptimizationLevel level) { optimizationLevel = level; }
    void enableDebugInfo(bool enable) { debugInfo = enable; }

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
    std::map<std::string, int> globalsMap;
    std::stack<int> breakJumps;
    std::stack<int> continueJumps;
    
    // 🎯 Optimization settings
    OptimizationLevel optimizationLevel;
    bool debugInfo;
    CompilerStats stats;
    
    // 🔧 Code generation helpers
    int getGlobalIndex(const std::string& name);
    void emitByte(uint8_t byte, int line = 0);
    void emitBytes(uint8_t byte1, uint8_t byte2, int line = 0);
    void emitConstant(Value value, int line = 0);
    int emitJump(uint8_t instruction, int line = 0);
    void patchJump(int offset);
    void emitLoop(int loopStart, int line = 0);
    
    // 🎯 Optimization methods
    void optimizeChunk();
    void constantFolding();
    void deadCodeElimination();
    void peepholeOptimization();
    
    // 📊 Statistics tracking
    void trackInstruction();
    void trackConstant();
    void trackOptimization();
};

#endif // COMPILER_H
