#pragma once
#include "interpreter.h"

namespace gumus {
namespace compiler {
namespace interpreter {

/**
 * Statement execution functionality separated from main interpreter
 * Handles: function statements, class statements, block statements, control flow
 */
class StatementExecutor {
private:
    Interpreter* interpreter;
    
public:
    explicit StatementExecutor(Interpreter* interp) : interpreter(interp) {}
    
    // Statement visitors
    std::shared_ptr<Value> visitFunctionStmt(FunctionStmt* stmt);
    std::shared_ptr<Value> visitClassStmt(ClassStmt* stmt);
    std::shared_ptr<Value> visitBlockStmt(BlockStmt* stmt);
    std::shared_ptr<Value> visitVarStmt(VarStmt* stmt);
    std::shared_ptr<Value> visitModuleStmt(ModuleStmt* stmt);
    
    // Control flow statements
    std::shared_ptr<Value> visitIfStmt(IfStmt* stmt);
    std::shared_ptr<Value> visitWhileStmt(WhileStmt* stmt);
    std::shared_ptr<Value> visitForStmt(ForStmt* stmt);
    std::shared_ptr<Value> visitTryStmt(TryStmt* stmt);
    std::shared_ptr<Value> visitReturnStmt(ReturnStmt* stmt);
    std::shared_ptr<Value> visitBreakStmt(BreakStmt* stmt);
    std::shared_ptr<Value> visitContinueStmt(ContinueStmt* stmt);
    std::shared_ptr<Value> visitPrintStmt(PrintStmt* stmt);
    std::shared_ptr<Value> visitExpressionStmt(ExpressionStmt* stmt);
    
private:
    // Helper methods
    void defineFunction(const std::string& name, std::shared_ptr<GumusFunction> function);
    void defineClass(const std::string& name, std::shared_ptr<GumusClass> klass);
    void defineVariable(const std::string& name, std::shared_ptr<Value> value);
};

} // namespace interpreter
} // namespace compiler  
} // namespace gumus