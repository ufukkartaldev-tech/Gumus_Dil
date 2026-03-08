#ifndef GUMUS_PARSER_AST_H
#define GUMUS_PARSER_AST_H

#include <memory>
#include <string>
#include <vector>
#include "../lexer/token.h"

// Forward Declarations
struct AstNode;
struct LiteralExpr;
struct BinaryExpr;
struct UnaryExpr;
struct LogicalExpr;
struct VariableExpr;
struct AssignExpr;
struct CallExpr;
struct ListExpr;
struct GetExpr; // Indexing (Get)
struct PropertyExpr; // Dot Access
struct SetExpr; // Property Set
struct IndexSetExpr; // List Index Set (New!)
struct ThisExpr;
struct SuperExpr; // Super Access (New!)
struct ScopeResolutionExpr;
struct MapExpr;

struct ExpressionStmt;
struct PrintStmt;
struct BlockStmt;
struct IfStmt;
struct WhileStmt;
struct BreakStmt; // Break (New!)
struct ContinueStmt; // Continue (New!)
struct ForStmt; // For (New!)
struct FunctionStmt;
struct ReturnStmt;
struct VarStmt;
struct ClassStmt;
struct TryCatchStmt;
struct ModuleStmt;

// Base Node
struct AstNode {
    virtual ~AstNode() = default;
};

// Visitor Interfaces
class ExprVisitor {
public:
    virtual ~ExprVisitor() = default;
    virtual void visitLiteralExpr(LiteralExpr* expr) = 0;
    virtual void visitBinaryExpr(BinaryExpr* expr) = 0;
    virtual void visitUnaryExpr(UnaryExpr* expr) = 0;
    virtual void visitLogicalExpr(LogicalExpr* expr) = 0;
    virtual void visitVariableExpr(VariableExpr* expr) = 0;
    virtual void visitAssignExpr(AssignExpr* expr) = 0;
    virtual void visitCallExpr(CallExpr* expr) = 0;
    virtual void visitListExpr(ListExpr* expr) = 0;
    virtual void visitGetExpr(GetExpr* expr) = 0;
    virtual void visitPropertyExpr(PropertyExpr* expr) = 0;
    virtual void visitSetExpr(SetExpr* expr) = 0;
    virtual void visitIndexSetExpr(IndexSetExpr* expr) = 0;
    virtual void visitThisExpr(ThisExpr* expr) = 0;
    virtual void visitSuperExpr(SuperExpr* expr) = 0;
    virtual void visitScopeResolutionExpr(ScopeResolutionExpr* expr) = 0;
    virtual void visitMapExpr(MapExpr* expr) = 0;
};

class StmtVisitor {
public:
    virtual ~StmtVisitor() = default;
    virtual void visitExpressionStmt(ExpressionStmt* stmt) = 0;
    virtual void visitPrintStmt(PrintStmt* stmt) = 0;
    virtual void visitBlockStmt(BlockStmt* stmt) = 0;
    virtual void visitIfStmt(IfStmt* stmt) = 0;
    virtual void visitWhileStmt(WhileStmt* stmt) = 0;
    virtual void visitBreakStmt(BreakStmt* stmt) = 0;
    virtual void visitContinueStmt(ContinueStmt* stmt) = 0;
    virtual void visitForStmt(ForStmt* stmt) = 0;
    virtual void visitFunctionStmt(FunctionStmt* stmt) = 0;
    virtual void visitReturnStmt(ReturnStmt* stmt) = 0;
    virtual void visitVarStmt(VarStmt* stmt) = 0;
    virtual void visitClassStmt(ClassStmt* stmt) = 0;
    virtual void visitTryCatchStmt(TryCatchStmt* stmt) = 0;
    virtual void visitModuleStmt(ModuleStmt* stmt) = 0;
};

// Expressions
struct Expr : public AstNode {
    int line = 0;
    virtual void accept(ExprVisitor& visitor) = 0;
};

// Statements
struct Stmt : public AstNode {
    int line = 0;
    virtual void accept(StmtVisitor& visitor) = 0;
};


// --- IMPLEMENTATIONS WITH LINE NUMBERS ---

struct LiteralExpr : public Expr {
    Token value;
    LiteralExpr(Token value) : value(value) {}
    void accept(ExprVisitor& visitor) override { visitor.visitLiteralExpr(this); }
};

struct BinaryExpr : public Expr {
    Expr* left;
    Token op;
    Expr* right;
    BinaryExpr(Expr* left, Token op, Expr* right) : left(left), op(op), right(right) {}
    void accept(ExprVisitor& visitor) override { visitor.visitBinaryExpr(this); }
};

struct VariableExpr : public Expr {
    Token name;
    int distance = -1; // Resolver tarafından doldurulacak
    int slot = -1;     // Opsiyonel: Yerel indeksleme için

    VariableExpr(Token name) : name(name) {}
    void accept(ExprVisitor& visitor) override { visitor.visitVariableExpr(this); }
};

struct UnaryExpr : public Expr {
    Token op;
    Expr* right;
    UnaryExpr(Token op, Expr* right) : op(op), right(right) {}
    void accept(ExprVisitor& visitor) override { visitor.visitUnaryExpr(this); }
};

struct LogicalExpr : public Expr {
    Expr* left;
    Token op;
    Expr* right;
    LogicalExpr(Expr* left, Token op, Expr* right) : left(left), op(op), right(right) {}
    void accept(ExprVisitor& visitor) override { visitor.visitLogicalExpr(this); }
};

struct AssignExpr : public Expr {
    Token name;
    Expr* value;
    int distance = -1; // Resolver tarafından doldurulacak

    AssignExpr(Token name, Expr* value) : name(name), value(value) {}
    void accept(ExprVisitor& visitor) override { visitor.visitAssignExpr(this); }
};

struct ExpressionStmt : public Stmt {
    Expr* expression;
    ExpressionStmt(Expr* expression) : expression(expression) {}
    void accept(StmtVisitor& visitor) override { visitor.visitExpressionStmt(this); }
};

struct PrintStmt : public Stmt {
    Expr* expression;
    PrintStmt(Expr* expression) : expression(expression) {}
    void accept(StmtVisitor& visitor) override { visitor.visitPrintStmt(this); }
};

struct BlockStmt : public Stmt {
    std::vector<Stmt*> statements;
    BlockStmt(std::vector<Stmt*> statements) : statements(std::move(statements)) {}
    void accept(StmtVisitor& visitor) override { visitor.visitBlockStmt(this); }
};

struct IfStmt : public Stmt {
    Expr* condition;
    Stmt* thenBranch;
    Stmt* elseBranch;
    IfStmt(Expr* c, Stmt* t, Stmt* e) : condition(c), thenBranch(t), elseBranch(e) {}
    void accept(StmtVisitor& visitor) override { visitor.visitIfStmt(this); }
};

struct WhileStmt : public Stmt {
    Expr* condition;
    Stmt* body;
    WhileStmt(Expr* c, Stmt* b) : condition(c), body(b) {}
    void accept(StmtVisitor& visitor) override { visitor.visitWhileStmt(this); }
};

struct BreakStmt : public Stmt {
    Token keyword;
    BreakStmt(Token k) : keyword(k) {}
    void accept(StmtVisitor& visitor) override { visitor.visitBreakStmt(this); }
};

struct ContinueStmt : public Stmt {
    Token keyword;
    ContinueStmt(Token k) : keyword(k) {}
    void accept(StmtVisitor& visitor) override { visitor.visitContinueStmt(this); }
};

struct TryCatchStmt : public Stmt {
    Stmt* tryBlock;
    Token errorName;
    Stmt* catchBlock;
    TryCatchStmt(Stmt* t, Token err, Stmt* c) : tryBlock(t), errorName(err), catchBlock(c) {}
    void accept(StmtVisitor& visitor) override { visitor.visitTryCatchStmt(this); }
};

struct ListExpr : public Expr {
    std::vector<Expr*> elements;
    ListExpr(std::vector<Expr*> elements) : elements(std::move(elements)) {}
    void accept(ExprVisitor& visitor) override { visitor.visitListExpr(this); }
};

struct GetExpr : public Expr {
    Expr* object;
    Token bracket; // Indexleme tokeni [
    Expr* index;
    GetExpr(Expr* o, Token b, Expr* i) : object(o), bracket(b), index(i) {}
    void accept(ExprVisitor& visitor) override { visitor.visitGetExpr(this); }
};

struct IndexSetExpr : public Expr {
    Expr* object;
    Token bracket;
    Expr* index;
    Expr* value;
    IndexSetExpr(Expr* o, Token b, Expr* i, Expr* v) 
        : object(o), bracket(b), index(i), value(v) {}
    void accept(ExprVisitor& visitor) override { visitor.visitIndexSetExpr(this); }
};

struct PropertyExpr : public Expr {
    Expr* object;
    Token name;
    PropertyExpr(Expr* o, Token n) : object(o), name(n) {}
    void accept(ExprVisitor& visitor) override { visitor.visitPropertyExpr(this); }
};

struct SetExpr : public Expr {
    Expr* object;
    Token name;
    Expr* value;
    SetExpr(Expr* o, Token n, Expr* v) : object(o), name(n), value(v) {}
    void accept(ExprVisitor& visitor) override { visitor.visitSetExpr(this); }
};

struct ThisExpr : public Expr {
    Token keyword;
    int distance = -1;

    ThisExpr(Token k) : keyword(k) {}
    void accept(ExprVisitor& visitor) override { visitor.visitThisExpr(this); }
};

struct SuperExpr : public Expr {
    Token keyword;
    Token method;
    int distance = -1;

    SuperExpr(Token k, Token m) : keyword(k), method(m) {}
    void accept(ExprVisitor& visitor) override { visitor.visitSuperExpr(this); }
};

struct CallExpr : public Expr {
    Expr* callee;
    Token paren;
    std::vector<Expr*> arguments;
    CallExpr(Expr* c, Token p, std::vector<Expr*> args) : callee(c), paren(p), arguments(std::move(args)) {}
    void accept(ExprVisitor& visitor) override { visitor.visitCallExpr(this); }
};

struct FunctionStmt : public Stmt {
    Token name;
    std::vector<Token> params;
    std::vector<Stmt*> body;
    FunctionStmt(Token n, std::vector<Token> p, std::vector<Stmt*> b) : name(n), params(std::move(p)), body(std::move(b)) {}
    void accept(StmtVisitor& visitor) override { visitor.visitFunctionStmt(this); }
};

struct ClassStmt : public Stmt {
    Token name;
    VariableExpr* superclass;
    std::vector<FunctionStmt*> methods;
    ClassStmt(Token n, VariableExpr* s, std::vector<FunctionStmt*> m) : name(n), superclass(s), methods(std::move(m)) {}
    void accept(StmtVisitor& visitor) override { visitor.visitClassStmt(this); }
};

struct VarStmt : public Stmt {
    Token name;
    Expr* initializer;
    VarStmt(Token n, Expr* i) : name(n), initializer(i) {}
    void accept(StmtVisitor& visitor) override { visitor.visitVarStmt(this); }
};

struct ReturnStmt : public Stmt {
    Token keyword;
    Expr* value;
    ReturnStmt(Token k, Expr* v) : keyword(k), value(v) {}
    void accept(StmtVisitor& visitor) override { visitor.visitReturnStmt(this); }
};

struct ScopeResolutionExpr : public Expr {
    Token moduleName; Token name;
    ScopeResolutionExpr(Token m, Token n) : moduleName(m), name(n) {}
    void accept(ExprVisitor& visitor) override { visitor.visitScopeResolutionExpr(this); }
};

struct ModuleStmt : public Stmt {
    Token name;
    std::vector<Stmt*> statements;
    ModuleStmt(Token n, std::vector<Stmt*> s) : name(n), statements(std::move(s)) {}
    void accept(StmtVisitor& visitor) override { visitor.visitModuleStmt(this); }
};

struct ForStmt : public Stmt {
    Token keyword;  // 'dongu' keyword for line tracking
    Stmt* initializer;
    Expr* condition;
    Expr* increment;
    Stmt* body;
    
    ForStmt(Token kw, Stmt* init, Expr* cond, Expr* inc, Stmt* b)
    : keyword(kw), initializer(init), condition(cond), increment(inc), body(b) {}
    
    void accept(StmtVisitor& visitor) override { visitor.visitForStmt(this); }
};

struct MapExpr : public Expr {
    std::vector<Expr*> keys;
    std::vector<Expr*> values;
    MapExpr(std::vector<Expr*> k, std::vector<Expr*> v) : keys(std::move(k)), values(std::move(v)) {}
    void accept(ExprVisitor& visitor) override { visitor.visitMapExpr(this); }
};

#endif // GUMUS_PARSER_AST_H
