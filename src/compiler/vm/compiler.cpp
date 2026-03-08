#include "compiler.h"
#include <iostream>

Compiler::Compiler() : currentChunk(nullptr) {}

Chunk* Compiler::compile(const std::vector<Stmt*>& statements) {
    Chunk* chunk = new Chunk();
    currentChunk = chunk;

    for (const auto& stmt : statements) {
        stmt->accept(*this);
    }

    emitByte(OP_RETURN, statements.empty() ? 0 : statements.back()->line);
    return chunk;
}

void Compiler::emitByte(uint8_t byte, int line) {
    currentChunk->write(byte, line);
}

void Compiler::emitBytes(uint8_t byte1, uint8_t byte2, int line) {
    emitByte(byte1, line);
    emitByte(byte2, line);
}

void Compiler::emitConstant(Value value, int line) {
    int constant = currentChunk->addConstant(value);
    emitBytes(OP_CONSTANT, (uint8_t)constant, line);
}

int Compiler::emitJump(uint8_t instruction, int line) {
    emitByte(instruction, line);
    emitByte(0xff, line);
    emitByte(0xff, line);
    return currentChunk->code.size() - 2;
}

void Compiler::patchJump(int offset) {
    int jump = currentChunk->code.size() - offset - 2;
    currentChunk->code[offset] = (jump >> 8) & 0xff;
    currentChunk->code[offset + 1] = jump & 0xff;
}

// StmtVisitor
void Compiler::visitExpressionStmt(ExpressionStmt* stmt) {
    stmt->expression->accept(*this);
    emitByte(OP_POP, stmt->line);
}

void Compiler::visitPrintStmt(PrintStmt* stmt) {
    stmt->expression->accept(*this);
    emitByte(OP_PRINT, stmt->line);
}

void Compiler::visitBlockStmt(BlockStmt* stmt) {
    for (const auto& s : stmt->statements) {
        s->accept(*this);
    }
}

void Compiler::visitVarStmt(VarStmt* stmt) {
    if (stmt->initializer != nullptr) {
        stmt->initializer->accept(*this);
    } else {
        emitByte(OP_NIL, stmt->line);
    }

    int nameIndex = getGlobalIndex(stmt->name.value);
    emitBytes(OP_DEFINE_GLOBAL, (uint8_t)nameIndex, stmt->line);
}

void Compiler::visitIfStmt(IfStmt* stmt) {
    stmt->condition->accept(*this);
    int thenJump = emitJump(OP_JUMP_IF_FALSE, stmt->line);
    emitByte(OP_POP, stmt->line);

    stmt->thenBranch->accept(*this);

    int elseJump = emitJump(OP_JUMP, stmt->line);

    patchJump(thenJump);
    emitByte(OP_POP, stmt->line);

    if (stmt->elseBranch != nullptr) stmt->elseBranch->accept(*this);
    patchJump(elseJump);
}

void Compiler::visitWhileStmt(WhileStmt* stmt) {
    int loopStart = currentChunk->code.size();
    stmt->condition->accept(*this);

    int exitJump = emitJump(OP_JUMP_IF_FALSE, stmt->line);
    emitByte(OP_POP, stmt->line);

    stmt->body->accept(*this);
    
    // Loop back
    emitByte(OP_LOOP, stmt->line);
    int offset = currentChunk->code.size() - loopStart + 2;
    emitByte((offset >> 8) & 0xff, stmt->line);
    emitByte(offset & 0xff, stmt->line);

    patchJump(exitJump);
    emitByte(OP_POP, stmt->line);
}
void Compiler::visitBreakStmt(BreakStmt* stmt) {
    // İleride döngü çıkışları için jump offset'leri tutularak eklenecek
}

void Compiler::visitContinueStmt(ContinueStmt* stmt) {
    // İleride döngü başına jump için eklenecek
}

void Compiler::visitForStmt(ForStmt* stmt) {
    // For döngüsü derlemesi (init -> cond -> body -> inc -> jump) mimarisi eklenecek
}

void Compiler::visitFunctionStmt(FunctionStmt* stmt) {
    // TODO: Yeni bir Compiler context/Chunk oluşturulacak,
    // argümanlar yerel değişken olarak eklenecek ve OP_CLOSURE üretilecek.
}

void Compiler::visitReturnStmt(ReturnStmt* stmt) {
    if (stmt->value != nullptr) {
        stmt->value->accept(*this);
    } else {
        emitByte(OP_NIL, stmt->line);
    }
    emitByte(OP_RETURN, stmt->line);
}

void Compiler::visitClassStmt(ClassStmt* stmt) {
    // TODO: OP_CLASS ve metod tanımlamaları
}

void Compiler::visitTryCatchStmt(TryCatchStmt* stmt) {
    // Hata yakalama mekanizması 
}

void Compiler::visitModuleStmt(ModuleStmt* stmt) {
    // Modül import/export sistemi
}

// ExprVisitor
void Compiler::visitLiteralExpr(LiteralExpr* expr) {
    if (expr->value.type == TokenType::KW_DOGRU || expr->value.value == "dogru") emitByte(OP_TRUE, expr->line);
    else if (expr->value.type == TokenType::KW_YANLIS || expr->value.value == "yanlis") emitByte(OP_FALSE, expr->line);
    else if (expr->value.type == TokenType::KW_BOS || expr->value.value == "bos") emitByte(OP_NIL, expr->line);
    else if (expr->value.type == TokenType::INTEGER) {
        if (expr->value.value.find('.') != std::string::npos) emitConstant(Value(std::stod(expr->value.value)), expr->line);
        else emitConstant(Value(std::stoi(expr->value.value)), expr->line);
    } else {
        emitConstant(Value(expr->value.value), expr->line);
    }
}

void Compiler::visitBinaryExpr(BinaryExpr* expr) {
    if (expr->left != nullptr) expr->left->accept(*this);
    expr->right->accept(*this);

    if (expr->left == nullptr) {
        switch (expr->op.type) {
            case TokenType::MINUS: emitByte(OP_NEGATE, expr->line); break;
            case TokenType::BANG: emitByte(OP_NOT, expr->line); break;
            default: break;
        }
        return;
    }

    switch (expr->op.type) {
        case TokenType::PLUS: emitByte(OP_ADD, expr->line); break;
        case TokenType::MINUS: emitByte(OP_SUBTRACT, expr->line); break;
        case TokenType::MULTIPLY: emitByte(OP_MULTIPLY, expr->line); break;
        case TokenType::DIVIDE: emitByte(OP_DIVIDE, expr->line); break;
        case TokenType::EQUAL_EQUAL: emitByte(OP_EQUAL, expr->line); break;
        case TokenType::BANG_EQUAL: emitBytes(OP_EQUAL, OP_NOT, expr->line); break;
        case TokenType::GREATER: emitByte(OP_GREATER, expr->line); break;
        case TokenType::GREATER_EQUAL: emitBytes(OP_LESS, OP_NOT, expr->line); break;
        case TokenType::LESS: emitByte(OP_LESS, expr->line); break;
        case TokenType::LESS_EQUAL: emitBytes(OP_GREATER, OP_NOT, expr->line); break;
        default: break;
    }
}

void Compiler::visitUnaryExpr(UnaryExpr* expr) {
    expr->right->accept(*this);
    switch (expr->op.type) {
        case TokenType::MINUS: emitByte(OP_NEGATE, expr->line); break;
        case TokenType::BANG: emitByte(OP_NOT, expr->line); break;
        default: break;
    }
}

void Compiler::visitLogicalExpr(LogicalExpr* expr) {}

void Compiler::visitVariableExpr(VariableExpr* expr) {
    int nameIndex = getGlobalIndex(expr->name.value);
    emitBytes(OP_GET_GLOBAL, (uint8_t)nameIndex, expr->line);
}

void Compiler::visitAssignExpr(AssignExpr* expr) {
    expr->value->accept(*this);
    int nameIndex = getGlobalIndex(expr->name.value);
    emitBytes(OP_SET_GLOBAL, (uint8_t)nameIndex, expr->line);
}

int Compiler::getGlobalIndex(const std::string& name) {
    if (globalsMap.find(name) == globalsMap.end()) {
        globalsMap[name] = (int)globalsMap.size();
    }
    return globalsMap[name];
}

void Compiler::visitCallExpr(CallExpr* expr) {
    expr->callee->accept(*this);
    for (Expr* arg : expr->arguments) {
        arg->accept(*this);
    }
    emitBytes(OP_CALL, (uint8_t)expr->arguments.size(), expr->line);
}

void Compiler::visitGetExpr(GetExpr* expr) {
    expr->object->accept(*this);
    expr->index->accept(*this);
    // Şimdilik sadece property üzerinden düşünüldüğünde:
    // İndeks veya özellik erişimi için OP_GET_PROPERTY düşünülebilir
}

void Compiler::visitSetExpr(SetExpr* expr) {
    expr->object->accept(*this);
    expr->value->accept(*this);
    // Özellik ataması için OP_SET_PROPERTY vb.
}

void Compiler::visitThisExpr(ThisExpr* expr) {
    // TODO: Yerel değişkenlerden 'bu' (this) aranacak
}

void Compiler::visitSuperExpr(SuperExpr* expr) {
    // TODO: OP_GET_SUPER
}

void Compiler::visitScopeResolutionExpr(ScopeResolutionExpr* expr) {
    // Modül içi erişim
}

void Compiler::visitListExpr(ListExpr* expr) {
    for (auto* element : expr->elements) {
        element->accept(*this);
    }
    // TODO: List öğelerini bellekte tutmak için yeni opcode
}

void Compiler::visitMapExpr(MapExpr* expr) {
    for (size_t i = 0; i < expr->keys.size(); ++i) {
        expr->keys[i]->accept(*this);
        expr->values[i]->accept(*this);
    }
    // TODO: Map yapısını bellekte oluşturacak opcode
}

void Compiler::visitPropertyExpr(PropertyExpr* expr) {
    expr->object->accept(*this);
    int nameIndex = getGlobalIndex(expr->name.value);
    emitBytes(OP_GET_PROPERTY, (uint8_t)nameIndex, expr->line);
}

void Compiler::visitIndexSetExpr(IndexSetExpr* expr) {
    expr->object->accept(*this);
    expr->index->accept(*this);
    expr->value->accept(*this);
    // OP_SET_PROPERTY vb. veya yeni indeksleme opcode'u
}
