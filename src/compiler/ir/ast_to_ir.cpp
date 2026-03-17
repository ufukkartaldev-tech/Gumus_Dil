#include "ast_to_ir.h"
#include "../interpreter/value.h"
#include <iostream>

// 🔄 AST to IR Converter Implementation

void ASTToIRConverter::convertProgram(const std::vector<Stmt*>& statements) {
    // Create main function
    currentFunction = module->createFunction("main");
    builder.setCurrentFunction(currentFunction);
    
    // Create entry block
    auto entryBlock = currentFunction->createBlock("entry");
    builder.setInsertPoint(entryBlock);
    
    // Convert all statements
    for (auto stmt : statements) {
        convertStatement(stmt);
    }
    
    // Add return if not present
    if (!entryBlock->isTerminated()) {
        builder.createReturn(IRValue{0});
    }
}

void ASTToIRConverter::convertFunction(FunctionStmt* funcStmt) {
    // Create IR function
    auto irFunc = module->createFunction(funcStmt->name.value);
    
    // Add parameters
    for (const auto& param : funcStmt->params) {
        irFunc->addParameter(param.value);
    }
    
    // Set current function context
    auto prevFunction = currentFunction;
    currentFunction = irFunc;
    builder.setCurrentFunction(irFunc);
    
    // Create entry block
    auto entryBlock = irFunc->createBlock("entry");
    builder.setInsertPoint(entryBlock);
    
    // Create return label and variable
    std::string returnLabel = generateLabel("return");
    std::string returnVar = generateTempName();
    
    FunctionContext funcContext;
    funcContext.name = funcStmt->name.value;
    funcContext.returnLabel = returnLabel;
    funcContext.returnVariable = returnVar;
    functionStack.push(funcContext);
    
    // Declare parameters as local variables
    for (const auto& param : funcStmt->params) {
        std::string paramIR = generateTempName();
        declareVariable(param.value, paramIR);
        // Parameters are loaded from function arguments
        builder.createLoad(param.value, paramIR);
    }
    
    // Convert function body
    for (auto stmt : funcStmt->body) {
        convertStatement(stmt);
    }
    
    // Create return block if not already terminated
    if (!entryBlock->isTerminated()) {
        builder.createJump(returnLabel);
    }
    
    // Create return block
    auto returnBlock = irFunc->createBlock(returnLabel);
    builder.setInsertPoint(returnBlock);
    builder.createReturn(IRValue{returnVar});
    
    // Restore previous function context
    functionStack.pop();
    currentFunction = prevFunction;
    if (prevFunction) {
        builder.setCurrentFunction(prevFunction);
    }
}

void ASTToIRConverter::convertStatement(Stmt* stmt) {
    if (auto exprStmt = dynamic_cast<ExpressionStmt*>(stmt)) {
        convertExpressionStmt(exprStmt);
    } else if (auto varStmt = dynamic_cast<VarStmt*>(stmt)) {
        convertVarStmt(varStmt);
    } else if (auto ifStmt = dynamic_cast<IfStmt*>(stmt)) {
        convertIfStmt(ifStmt);
    } else if (auto whileStmt = dynamic_cast<WhileStmt*>(stmt)) {
        convertWhileStmt(whileStmt);
    } else if (auto forStmt = dynamic_cast<ForStmt*>(stmt)) {
        convertForStmt(forStmt);
    } else if (auto returnStmt = dynamic_cast<ReturnStmt*>(stmt)) {
        convertReturnStmt(returnStmt);
    } else if (auto blockStmt = dynamic_cast<BlockStmt*>(stmt)) {
        convertBlockStmt(blockStmt);
    } else if (auto funcStmt = dynamic_cast<FunctionStmt*>(stmt)) {
        convertFunction(funcStmt);
    }
}

void ASTToIRConverter::convertExpressionStmt(ExpressionStmt* stmt) {
    convertExpression(stmt->expression);
}

void ASTToIRConverter::convertVarStmt(VarStmt* stmt) {
    std::string varName = stmt->name.value;
    std::string irVarName = generateTempName();
    
    // Declare variable
    declareVariable(varName, irVarName);
    
    // Initialize if initializer present
    if (stmt->initializer) {
        std::string initValue = convertExpression(stmt->initializer);
        builder.createStore(IRValue{initValue}, irVarName);
    } else {
        // Default initialization
        builder.createStore(IRValue{0}, irVarName);
    }
}

void ASTToIRConverter::convertIfStmt(IfStmt* stmt) {
    std::string thenLabel = generateLabel("then");
    std::string elseLabel = generateLabel("else");
    std::string endLabel = generateLabel("endif");
    
    // Convert condition
    std::string condition = convertExpression(stmt->condition);
    
    // Conditional jump
    if (stmt->elseBranch) {
        builder.createCondJump(IRValue{condition}, thenLabel, elseLabel);
    } else {
        builder.createCondJump(IRValue{condition}, thenLabel, endLabel);
    }
    
    // Then branch
    auto thenBlock = currentFunction->createBlock(thenLabel);
    builder.setInsertPoint(thenBlock);
    convertStatement(stmt->thenBranch);
    if (!thenBlock->isTerminated()) {
        builder.createJump(endLabel);
    }
    
    // Else branch (if present)
    if (stmt->elseBranch) {
        auto elseBlock = currentFunction->createBlock(elseLabel);
        builder.setInsertPoint(elseBlock);
        convertStatement(stmt->elseBranch);
        if (!elseBlock->isTerminated()) {
            builder.createJump(endLabel);
        }
    }
    
    // End block
    auto endBlock = currentFunction->createBlock(endLabel);
    builder.setInsertPoint(endBlock);
}

void ASTToIRConverter::convertWhileStmt(WhileStmt* stmt) {
    std::string condLabel = generateLabel("while_cond");
    std::string bodyLabel = generateLabel("while_body");
    std::string endLabel = generateLabel("while_end");
    
    // Push loop context for break/continue
    LoopContext loopCtx;
    loopCtx.breakLabel = endLabel;
    loopCtx.continueLabel = condLabel;
    loopStack.push(loopCtx);
    
    // Jump to condition
    builder.createJump(condLabel);
    
    // Condition block
    auto condBlock = currentFunction->createBlock(condLabel);
    builder.setInsertPoint(condBlock);
    std::string condition = convertExpression(stmt->condition);
    builder.createCondJump(IRValue{condition}, bodyLabel, endLabel);
    
    // Body block
    auto bodyBlock = currentFunction->createBlock(bodyLabel);
    builder.setInsertPoint(bodyBlock);
    convertStatement(stmt->body);
    if (!bodyBlock->isTerminated()) {
        builder.createJump(condLabel);
    }
    
    // End block
    auto endBlock = currentFunction->createBlock(endLabel);
    builder.setInsertPoint(endBlock);
    
    // Pop loop context
    loopStack.pop();
}

void ASTToIRConverter::convertForStmt(ForStmt* stmt) {
    // For loop: for (init; condition; increment) body
    // Converted to: init; while (condition) { body; increment; }
    
    std::string condLabel = generateLabel("for_cond");
    std::string bodyLabel = generateLabel("for_body");
    std::string incrLabel = generateLabel("for_incr");
    std::string endLabel = generateLabel("for_end");
    
    // Push loop context
    LoopContext loopCtx;
    loopCtx.breakLabel = endLabel;
    loopCtx.continueLabel = incrLabel;
    loopStack.push(loopCtx);
    
    // Initializer
    if (stmt->initializer) {
        convertStatement(stmt->initializer);
    }
    
    // Jump to condition
    builder.createJump(condLabel);
    
    // Condition block
    auto condBlock = currentFunction->createBlock(condLabel);
    builder.setInsertPoint(condBlock);
    if (stmt->condition) {
        std::string condition = convertExpression(stmt->condition);
        builder.createCondJump(IRValue{condition}, bodyLabel, endLabel);
    } else {
        // Infinite loop if no condition
        builder.createJump(bodyLabel);
    }
    
    // Body block
    auto bodyBlock = currentFunction->createBlock(bodyLabel);
    builder.setInsertPoint(bodyBlock);
    convertStatement(stmt->body);
    if (!bodyBlock->isTerminated()) {
        builder.createJump(incrLabel);
    }
    
    // Increment block
    auto incrBlock = currentFunction->createBlock(incrLabel);
    builder.setInsertPoint(incrBlock);
    if (stmt->increment) {
        convertExpression(stmt->increment);
    }
    builder.createJump(condLabel);
    
    // End block
    auto endBlock = currentFunction->createBlock(endLabel);
    builder.setInsertPoint(endBlock);
    
    // Pop loop context
    loopStack.pop();
}

void ASTToIRConverter::convertReturnStmt(ReturnStmt* stmt) {
    if (!functionStack.empty()) {
        auto& funcCtx = functionStack.top();
        
        if (stmt->value) {
            std::string returnValue = convertExpression(stmt->value);
            builder.createStore(IRValue{returnValue}, funcCtx.returnVariable);
        }
        
        builder.createJump(funcCtx.returnLabel);
    } else {
        // Global return (program exit)
        if (stmt->value) {
            std::string returnValue = convertExpression(stmt->value);
            builder.createReturn(IRValue{returnValue});
        } else {
            builder.createReturn(IRValue{0});
        }
    }
}

void ASTToIRConverter::convertBlockStmt(BlockStmt* stmt) {
    for (auto statement : stmt->statements) {
        convertStatement(statement);
    }
}

std::string ASTToIRConverter::convertExpression(Expr* expr) {
    if (auto binaryExpr = dynamic_cast<BinaryExpr*>(expr)) {
        return convertBinaryExpr(binaryExpr);
    } else if (auto unaryExpr = dynamic_cast<UnaryExpr*>(expr)) {
        return convertUnaryExpr(unaryExpr);
    } else if (auto literalExpr = dynamic_cast<LiteralExpr*>(expr)) {
        return convertLiteralExpr(literalExpr);
    } else if (auto varExpr = dynamic_cast<VariableExpr*>(expr)) {
        return convertVariableExpr(varExpr);
    } else if (auto assignExpr = dynamic_cast<AssignExpr*>(expr)) {
        return convertAssignExpr(assignExpr);
    } else if (auto callExpr = dynamic_cast<CallExpr*>(expr)) {
        return convertCallExpr(callExpr);
    } else if (auto groupExpr = dynamic_cast<GroupingExpr*>(expr)) {
        return convertGroupingExpr(groupExpr);
    } else if (auto logicalExpr = dynamic_cast<LogicalExpr*>(expr)) {
        return convertLogicalExpr(logicalExpr);
    }
    
    return generateTempName(); // Fallback
}

std::string ASTToIRConverter::convertBinaryExpr(BinaryExpr* expr) {
    std::string left = convertExpression(expr->left);
    std::string right = convertExpression(expr->right);
    std::string result = generateTempName();
    
    IROpcode opcode = getBinaryOpcode(expr->op.type);
    
    auto instr = std::make_unique<IRInstruction>(opcode, 
        std::vector<IRValue>{left, right}, result);
    
    if (builder.currentBlock) {
        builder.currentBlock->addInstruction(std::move(instr));
    }
    
    return result;
}

std::string ASTToIRConverter::convertUnaryExpr(UnaryExpr* expr) {
    std::string operand = convertExpression(expr->right);
    std::string result = generateTempName();
    
    IROpcode opcode = getUnaryOpcode(expr->op.type);
    
    auto instr = std::make_unique<IRInstruction>(opcode, 
        std::vector<IRValue>{operand}, result);
    
    if (builder.currentBlock) {
        builder.currentBlock->addInstruction(std::move(instr));
    }
    
    return result;
}

std::string ASTToIRConverter::convertLiteralExpr(LiteralExpr* expr) {
    std::string result = generateTempName();
    IRValue value = convertLiteralValue(expr->value);
    
    // Store literal in temporary variable
    builder.createStore(value, result);
    
    return result;
}

std::string ASTToIRConverter::convertVariableExpr(VariableExpr* expr) {
    std::string varName = expr->name.value;
    std::string irVar = getVariableIR(varName);
    std::string result = generateTempName();
    
    // Load variable value
    builder.createLoad(irVar, result);
    
    return result;
}

std::string ASTToIRConverter::convertAssignExpr(AssignExpr* expr) {
    std::string value = convertExpression(expr->value);
    std::string varName = expr->name.value;
    std::string irVar = getVariableIR(varName);
    
    // Store value to variable
    builder.createStore(IRValue{value}, irVar);
    
    return value;
}

std::string ASTToIRConverter::convertCallExpr(CallExpr* expr) {
    std::string funcName;
    if (auto varExpr = dynamic_cast<VariableExpr*>(expr->callee)) {
        funcName = varExpr->name.value;
    } else {
        funcName = "unknown";
    }
    
    // Convert arguments
    std::vector<IRValue> args;
    for (auto arg : expr->arguments) {
        std::string argValue = convertExpression(arg);
        args.push_back(IRValue{argValue});
    }
    
    std::string result = generateTempName();
    builder.createCall(funcName, args, result);
    
    return result;
}

std::string ASTToIRConverter::convertGroupingExpr(GroupingExpr* expr) {
    return convertExpression(expr->expression);
}

std::string ASTToIRConverter::convertLogicalExpr(LogicalExpr* expr) {
    // Short-circuit evaluation for logical operators
    std::string result = generateTempName();
    
    if (expr->op.type == TokenType::OR) {
        // left || right
        std::string rightLabel = generateLabel("or_right");
        std::string endLabel = generateLabel("or_end");
        
        std::string left = convertExpression(expr->left);
        builder.createCondJump(IRValue{left}, endLabel, rightLabel);
        
        // Right evaluation
        auto rightBlock = currentFunction->createBlock(rightLabel);
        builder.setInsertPoint(rightBlock);
        std::string right = convertExpression(expr->right);
        builder.createStore(IRValue{right}, result);
        builder.createJump(endLabel);
        
        // End block
        auto endBlock = currentFunction->createBlock(endLabel);
        builder.setInsertPoint(endBlock);
        builder.createStore(IRValue{left}, result);
        
    } else if (expr->op.type == TokenType::AND) {
        // left && right
        std::string rightLabel = generateLabel("and_right");
        std::string endLabel = generateLabel("and_end");
        
        std::string left = convertExpression(expr->left);
        builder.createCondJump(IRValue{left}, rightLabel, endLabel);
        
        // Right evaluation
        auto rightBlock = currentFunction->createBlock(rightLabel);
        builder.setInsertPoint(rightBlock);
        std::string right = convertExpression(expr->right);
        builder.createStore(IRValue{right}, result);
        builder.createJump(endLabel);
        
        // End block
        auto endBlock = currentFunction->createBlock(endLabel);
        builder.setInsertPoint(endBlock);
        builder.createStore(IRValue{false}, result);
    }
    
    return result;
}

// Utility functions

std::string ASTToIRConverter::generateTempName() {
    return "%t" + std::to_string(tempCounter++);
}

std::string ASTToIRConverter::generateLabel(const std::string& prefix) {
    return prefix + "_" + std::to_string(labelCounter++);
}

void ASTToIRConverter::declareVariable(const std::string& name, const std::string& irName) {
    variableMap[name] = irName;
}

std::string ASTToIRConverter::getVariableIR(const std::string& name) {
    auto it = variableMap.find(name);
    if (it != variableMap.end()) {
        return it->second;
    }
    
    // Variable not found, create new one
    std::string irName = generateTempName();
    declareVariable(name, irName);
    return irName;
}

IRValue ASTToIRConverter::convertLiteralValue(const Value& value) {
    if (std::holds_alternative<int>(value)) {
        return IRValue{std::get<int>(value)};
    } else if (std::holds_alternative<double>(value)) {
        return IRValue{std::get<double>(value)};
    } else if (std::holds_alternative<std::string>(value)) {
        return IRValue{std::get<std::string>(value)};
    } else if (std::holds_alternative<bool>(value)) {
        return IRValue{std::get<bool>(value)};
    }
    
    return IRValue{0}; // Default
}

IROpcode ASTToIRConverter::getBinaryOpcode(TokenType op) {
    switch (op) {
        case TokenType::PLUS: return IROpcode::ADD;
        case TokenType::MINUS: return IROpcode::SUB;
        case TokenType::MULTIPLY: return IROpcode::MUL;
        case TokenType::DIVIDE: return IROpcode::DIV;
        case TokenType::MODULO: return IROpcode::MOD;
        case TokenType::EQUAL_EQUAL: return IROpcode::EQ;
        case TokenType::BANG_EQUAL: return IROpcode::NE;
        case TokenType::LESS: return IROpcode::LT;
        case TokenType::LESS_EQUAL: return IROpcode::LE;
        case TokenType::GREATER: return IROpcode::GT;
        case TokenType::GREATER_EQUAL: return IROpcode::GE;
        default: return IROpcode::NOP;
    }
}

IROpcode ASTToIRConverter::getUnaryOpcode(TokenType op) {
    switch (op) {
        case TokenType::MINUS: return IROpcode::SUB; // Negate
        case TokenType::BANG: return IROpcode::NOT;
        default: return IROpcode::NOP;
    }
}

IROpcode ASTToIRConverter::getComparisonOpcode(TokenType op) {
    return getBinaryOpcode(op);
}

// High-level conversion function
std::unique_ptr<IRModule> convertASTToIR(const std::vector<Stmt*>& statements, const std::string& moduleName) {
    auto module = std::make_unique<IRModule>(moduleName);
    ASTToIRConverter converter(module.get());
    converter.convertProgram(statements);
    return module;
}