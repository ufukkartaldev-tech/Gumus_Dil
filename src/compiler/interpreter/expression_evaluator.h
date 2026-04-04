#pragma once
#include "interpreter.h"

namespace gumus {
namespace compiler {
namespace interpreter {

/**
 * Expression evaluation functionality separated from main interpreter
 * Handles: binary expressions, call expressions, property access, literals
 */
class ExpressionEvaluator {
private:
    Interpreter* interpreter;
    
public:
    explicit ExpressionEvaluator(Interpreter* interp) : interpreter(interp) {}
    
    // Expression visitors
    std::shared_ptr<Value> visitBinaryExpr(BinaryExpr* expr);
    std::shared_ptr<Value> visitUnaryExpr(UnaryExpr* expr);
    std::shared_ptr<Value> visitCallExpr(CallExpr* expr);
    std::shared_ptr<Value> visitGetExpr(GetExpr* expr);
    std::shared_ptr<Value> visitSetExpr(SetExpr* expr);
    std::shared_ptr<Value> visitAssignExpr(AssignExpr* expr);
    std::shared_ptr<Value> visitVariableExpr(VariableExpr* expr);
    std::shared_ptr<Value> visitLiteralExpr(LiteralExpr* expr);
    std::shared_ptr<Value> visitGroupingExpr(GroupingExpr* expr);
    std::shared_ptr<Value> visitLogicalExpr(LogicalExpr* expr);
    std::shared_ptr<Value> visitThisExpr(ThisExpr* expr);
    std::shared_ptr<Value> visitSuperExpr(SuperExpr* expr);
    std::shared_ptr<Value> visitArrayExpr(ArrayExpr* expr);
    std::shared_ptr<Value> visitObjectExpr(ObjectExpr* expr);
    std::shared_ptr<Value> visitIndexExpr(IndexExpr* expr);
    std::shared_ptr<Value> visitLambdaExpr(LambdaExpr* expr);
    
private:
    // Helper methods
    std::shared_ptr<Value> evaluateBinaryOperation(TokenType operator_, 
                                                  std::shared_ptr<Value> left, 
                                                  std::shared_ptr<Value> right);
    std::shared_ptr<Value> evaluateUnaryOperation(TokenType operator_, 
                                                 std::shared_ptr<Value> operand);
    std::shared_ptr<Value> callFunction(std::shared_ptr<Value> callee, 
                                       const std::vector<std::shared_ptr<Value>>& arguments);
    bool isTruthy(std::shared_ptr<Value> value);
    bool isEqual(std::shared_ptr<Value> a, std::shared_ptr<Value> b);
};

} // namespace interpreter
} // namespace compiler  
} // namespace gumus