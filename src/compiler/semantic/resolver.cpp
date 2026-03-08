#include "resolver.h"
#include "../interpreter/interpreter.h"

Resolver::Resolver(Interpreter& interpreter) : interpreter(interpreter) {}

void Resolver::resolve(const std::vector<std::unique_ptr<Stmt>>& statements) {
    for (const auto& statement : statements) {
        resolve(statement.get());
    }
}

void Resolver::resolve(Stmt* stmt) {
    if (stmt) stmt->accept(*this);
}

void Resolver::resolve(Expr* expr) {
    if (expr) expr->accept(*this);
}

void Resolver::beginScope() {
    scopes.push_back(std::unordered_map<std::string, bool>());
}

void Resolver::endScope() {
    scopes.pop_back();
}

void Resolver::declare(const Token& name) {
    if (scopes.empty()) return;

    std::unordered_map<std::string, bool>& scope = scopes.back();
    scope[name.value] = false; // Tanımlandı ama henüz başlatılmadı
}

void Resolver::define(const Token& name) {
    if (scopes.empty()) return;
    scopes.back()[name.value] = true; // Başlatıldı
}

void Resolver::resolveLocal(Expr* expr, const Token& name) {
    for (int i = (int)scopes.size() - 1; i >= 0; i--) {
        if (scopes[i].count(name.value)) {
            int distance = (int)scopes.size() - 1 - i;
            if (name.value == "\xC3\xB6" "z") {
                // std::cout << "DEBUG: RESOLVED 'oz' at distance " << distance << " line " << name.line << std::endl;
            }
            
            // Raw pointer cast işlemleri
            if (auto var = dynamic_cast<VariableExpr*>(expr)) {
                var->distance = distance;
            } else if (auto assign = dynamic_cast<AssignExpr*>(expr)) {
                assign->distance = distance;
            } else if (auto thiz = dynamic_cast<ThisExpr*>(expr)) {
                thiz->distance = distance;
            } else if (auto superNode = dynamic_cast<SuperExpr*>(expr)) {
                superNode->distance = distance;
            }
            return;
        }
    }
}

void Resolver::resolveFunction(FunctionStmt* function, FunctionType type) {
    FunctionType enclosingFunction = currentFunction;
    currentFunction = type;

    beginScope();
    for (const Token& param : function->params) {
        declare(param);
        define(param);
    }
    for (const auto& stmt : function->body) {
        resolve(stmt.get());
    }
    endScope();
    currentFunction = enclosingFunction;
}

// Stmt Visitors
void Resolver::visitBlockStmt(BlockStmt* stmt) {
    beginScope();
    for (const auto& s : stmt->statements) resolve(s.get());
    endScope();
}

void Resolver::visitVarStmt(VarStmt* stmt) {
    declare(stmt->name);
    if (stmt->initializer != nullptr) {
        resolve(stmt->initializer.get());
    }
    define(stmt->name);
}

void Resolver::visitFunctionStmt(FunctionStmt* stmt) {
    declare(stmt->name);
    define(stmt->name);
    resolveFunction(stmt, FunctionType::FUNCTION);
}

void Resolver::visitExpressionStmt(ExpressionStmt* stmt) {
    resolve(stmt->expression.get());
}

void Resolver::visitIfStmt(IfStmt* stmt) {
    resolve(stmt->condition.get());
    resolve(stmt->thenBranch.get());
    if (stmt->elseBranch != nullptr) resolve(stmt->elseBranch.get());
}

void Resolver::visitPrintStmt(PrintStmt* stmt) {
    resolve(stmt->expression.get());
}

void Resolver::visitReturnStmt(ReturnStmt* stmt) {
    if (stmt->value != nullptr) {
        resolve(stmt->value.get());
    }
}

void Resolver::visitWhileStmt(WhileStmt* stmt) {
    resolve(stmt->condition.get());
    resolve(stmt->body.get());
}

void Resolver::visitForStmt(ForStmt* stmt) {
    beginScope();
    if (stmt->initializer) resolve(stmt->initializer.get());
    if (stmt->condition) resolve(stmt->condition.get());
    if (stmt->increment) resolve(stmt->increment.get());
    resolve(stmt->body.get());
    endScope();
}

void Resolver::visitBreakStmt(BreakStmt* stmt) {}
void Resolver::visitContinueStmt(ContinueStmt* stmt) {}

void Resolver::visitClassStmt(ClassStmt* stmt) {
    ClassType enclosingClass = currentClass;
    currentClass = ClassType::CLASS;

    declare(stmt->name);
    define(stmt->name);

    if (stmt->superclass != nullptr) {
        currentClass = ClassType::SUBCLASS;
        resolve(stmt->superclass.get());
        beginScope();
        scopes.back()["ata"] = true;
    }

    beginScope();
    scopes.back()["\xC3\xB6" "z"] = true; // "öz" key

    for (const auto& method : stmt->methods) {
        FunctionType declaration = FunctionType::METHOD;
        if (method->name.value == "kurucu") {
            declaration = FunctionType::INITIALIZER;
        }
        resolveFunction(method.get(), declaration);
    }

    endScope();
    if (stmt->superclass != nullptr) endScope();
    currentClass = enclosingClass;
}

void Resolver::visitTryCatchStmt(TryCatchStmt* stmt) {
    resolve(stmt->tryBlock.get());
    beginScope();
    declare(stmt->errorName);
    define(stmt->errorName);
    resolve(stmt->catchBlock.get());
    endScope();
}

void Resolver::visitModuleStmt(ModuleStmt* stmt) {
    beginScope();
    for(const auto& s : stmt->statements) resolve(s.get());
    endScope();
}

// Expr Visitors
void Resolver::visitVariableExpr(VariableExpr* expr) {
    resolveLocal(expr, expr->name);
}

void Resolver::visitAssignExpr(AssignExpr* expr) {
    resolve(expr->value.get());
    resolveLocal(expr, expr->name);
}

void Resolver::visitBinaryExpr(BinaryExpr* expr) {
    resolve(expr->left.get());
    resolve(expr->right.get());
}

void Resolver::visitCallExpr(CallExpr* expr) {
    resolve(expr->callee.get());
    for (const auto& arg : expr->arguments) {
        resolve(arg.get());
    }
}

void Resolver::visitLiteralExpr(LiteralExpr* expr) {}

void Resolver::visitLogicalExpr(LogicalExpr* expr) {
    resolve(expr->left.get());
    resolve(expr->right.get());
}

void Resolver::visitUnaryExpr(UnaryExpr* expr) {
    resolve(expr->right.get());
}

void Resolver::visitListExpr(ListExpr* expr) {
    for (const auto& el : expr->elements) resolve(el.get());
}

void Resolver::visitGetExpr(GetExpr* expr) {
    resolve(expr->object.get());
    resolve(expr->index.get());
}

void Resolver::visitSetExpr(SetExpr* expr) {
    resolve(expr->value.get());
    resolve(expr->object.get());
}

void Resolver::visitThisExpr(ThisExpr* expr) {
    resolveLocal(expr, expr->keyword);
}

void Resolver::visitSuperExpr(SuperExpr* expr) {
    resolveLocal(expr, expr->keyword);
}

void Resolver::visitPropertyExpr(PropertyExpr* expr) {
    resolve(expr->object.get());
}

void Resolver::visitIndexSetExpr(IndexSetExpr* expr) {
    resolve(expr->object.get());
    resolve(expr->index.get());
    resolve(expr->value.get());
}

void Resolver::visitScopeResolutionExpr(ScopeResolutionExpr* expr) {}

void Resolver::visitMapExpr(MapExpr* expr) {
    for (size_t i = 0; i < expr->keys.size(); i++) {
        resolve(expr->keys[i].get());
        resolve(expr->values[i].get());
    }
}
