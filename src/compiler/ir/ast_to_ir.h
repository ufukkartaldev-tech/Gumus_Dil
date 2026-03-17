#ifndef AST_TO_IR_H
#define AST_TO_IR_H

#include "ir_instruction.h"
#include "../parser/ast.h"
#include <unordered_map>
#include <stack>

// 🔄 AST to IR Converter
class ASTToIRConverter {
private:
    IRModule* module;
    IRFunction* currentFunction;
    IRBuilder builder;
    
    // Symbol table for variable tracking
    std::unordered_map<std::string, std::string> variableMap;
    
    // Control flow stack for break/continue
    struct LoopContext {
        std::string breakLabel;
        std::string continueLabel;
    };
    std::stack<LoopContext> loopStack;
    
    // Function context
    struct FunctionContext {
        std::string name;
        std::string returnLabel;
        std::string returnVariable;
    };
    std::stack<FunctionContext> functionStack;
    
    int labelCounter = 0;
    int tempCounter = 0;
    
public:
    ASTToIRConverter(IRModule* mod) : module(mod) {}
    
    // Main conversion entry points
    void convertProgram(const std::vector<Stmt*>& statements);
    void convertFunction(FunctionStmt* funcStmt);
    
    // Statement conversion
    void convertStatement(Stmt* stmt);
    void convertExpressionStmt(ExpressionStmt* stmt);
    void convertVarStmt(VarStmt* stmt);
    void convertIfStmt(IfStmt* stmt);
    void convertWhileStmt(WhileStmt* stmt);
    void convertForStmt(ForStmt* stmt);
    void convertReturnStmt(ReturnStmt* stmt);
    void convertBlockStmt(BlockStmt* stmt);
    
    // Expression conversion (returns the IR value/variable name)
    std::string convertExpression(Expr* expr);
    std::string convertBinaryExpr(BinaryExpr* expr);
    std::string convertUnaryExpr(UnaryExpr* expr);
    std::string convertLiteralExpr(LiteralExpr* expr);
    std::string convertVariableExpr(VariableExpr* expr);
    std::string convertAssignExpr(AssignExpr* expr);
    std::string convertCallExpr(CallExpr* expr);
    std::string convertGroupingExpr(GroupingExpr* expr);
    std::string convertLogicalExpr(LogicalExpr* expr);
    
    // Utility functions
    std::string generateTempName();
    std::string generateLabel(const std::string& prefix = "L");
    void declareVariable(const std::string& name, const std::string& irName);
    std::string getVariableIR(const std::string& name);
    
    // Type conversion helpers
    IRValue convertLiteralValue(const Value& value);
    IROpcode getBinaryOpcode(TokenType op);
    IROpcode getUnaryOpcode(TokenType op);
    IROpcode getComparisonOpcode(TokenType op);
};

// 🎯 IR Generation Context
class IRGenerationContext {
public:
    IRModule* module;
    std::unordered_map<std::string, IRFunction*> functions;
    std::unordered_map<std::string, std::string> globalVariables;
    
    IRGenerationContext(IRModule* mod) : module(mod) {}
    
    void registerFunction(const std::string& name, IRFunction* func);
    IRFunction* getFunction(const std::string& name);
    void registerGlobalVariable(const std::string& name, const std::string& irName);
    std::string getGlobalVariable(const std::string& name);
};

// 🚀 High-level conversion function
std::unique_ptr<IRModule> convertASTToIR(const std::vector<Stmt*>& statements, const std::string& moduleName = "main");

#endif // AST_TO_IR_H