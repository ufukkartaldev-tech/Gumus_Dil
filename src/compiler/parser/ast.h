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

// Helper for JSON string escaping
inline std::string jsonEscape(const std::string& s) {
    std::string res = "";
    for (char c : s) {
        if (c == '"') res += "\\\"";
        else if (c == '\\') res += "\\\\";
        else if (c == '\n') res += "\\n";
        else if (c == '\r') res += "\\r";
        else if (c == '\t') res += "\\t";
        else res += c;
    }
    return res;
}

// Base Node
struct AstNode {
    virtual ~AstNode() = default;
    virtual std::string toString() const = 0;
    virtual std::string toJson() const = 0;
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
    std::string toString() const override { return "Literal(" + value.value + ")"; }
    std::string toJson() const override {
        return "{ \"type\": \"Literal\", \"line\": " + std::to_string(value.line) + 
               ", \"value\": \"" + jsonEscape(value.value) + "\", \"children\": [] }";
    }
};

struct BinaryExpr : public Expr {
    std::shared_ptr<Expr> left;
    Token op;
    std::shared_ptr<Expr> right;
    BinaryExpr(std::shared_ptr<Expr> left, Token op, std::shared_ptr<Expr> right) : left(move(left)), op(op), right(move(right)) {}
    void accept(ExprVisitor& visitor) override { visitor.visitBinaryExpr(this); }
    std::string toString() const override { return "Binary(" + left->toString() + " " + op.value + " " + right->toString() + ")"; }
    std::string toJson() const override {
        return "{ \"type\": \"BinaryExpr\", \"line\": " + std::to_string(op.line) + 
               ", \"value\": \"" + jsonEscape(op.value) + "\", \"children\": [" + left->toJson() + ", " + right->toJson() + "] }";
    }
};

struct VariableExpr : public Expr {
    Token name;
    int distance = -1; // Resolver tarafından doldurulacak
    int slot = -1;     // Opsiyonel: Yerel indeksleme için

    VariableExpr(Token name) : name(name) {}
    void accept(ExprVisitor& visitor) override { visitor.visitVariableExpr(this); }
    std::string toString() const override { return "Var(" + name.value + ")"; }
    std::string toJson() const override {
        return "{ \"type\": \"Variable\", \"line\": " + std::to_string(name.line) + 
               ", \"value\": \"" + jsonEscape(name.value) + "\", \"distance\": " + std::to_string(distance) + ", \"children\": [] }";
    }
};

struct UnaryExpr : public Expr {
    Token op;
    std::shared_ptr<Expr> right;
    UnaryExpr(Token op, std::shared_ptr<Expr> right) : op(op), right(move(right)) {}
    void accept(ExprVisitor& visitor) override { visitor.visitUnaryExpr(this); }
    std::string toString() const override { return "Unary(" + op.value + " " + right->toString() + ")"; }
    std::string toJson() const override {
        return "{ \"type\": \"UnaryExpr\", \"line\": " + std::to_string(op.line) + 
               ", \"value\": \"" + jsonEscape(op.value) + "\", \"children\": [" + right->toJson() + "] }";
    }
};

struct LogicalExpr : public Expr {
    std::shared_ptr<Expr> left;
    Token op;
    std::shared_ptr<Expr> right;
    LogicalExpr(std::shared_ptr<Expr> left, Token op, std::shared_ptr<Expr> right) : left(move(left)), op(op), right(move(right)) {}
    void accept(ExprVisitor& visitor) override { visitor.visitLogicalExpr(this); }
    std::string toString() const override { return "Logical(" + left->toString() + " " + op.value + " " + right->toString() + ")"; }
    std::string toJson() const override {
         return "{ \"type\": \"LogicalExpr\", \"line\": " + std::to_string(op.line) + 
                ", \"value\": \"" + jsonEscape(op.value) + "\", \"children\": [" + left->toJson() + ", " + right->toJson() + "] }";
    }
};

struct AssignExpr : public Expr {
    Token name;
    std::shared_ptr<Expr> value;
    int distance = -1; // Resolver tarafından doldurulacak

    AssignExpr(Token name, std::shared_ptr<Expr> value) : name(name), value(move(value)) {}
    void accept(ExprVisitor& visitor) override { visitor.visitAssignExpr(this); }
    std::string toString() const override { return "Assign(" + name.value + " = " + value->toString() + ")"; }
    std::string toJson() const override {
        return "{ \"type\": \"AssignExpr\", \"line\": " + std::to_string(name.line) + 
               ", \"value\": \"" + jsonEscape(name.value) + "\", \"distance\": " + std::to_string(distance) + ", \"children\": [" + value->toJson() + "] }";
    }
};

struct ExpressionStmt : public Stmt {
    std::shared_ptr<Expr> expression;
    ExpressionStmt(std::shared_ptr<Expr> expression) : expression(move(expression)) {}
    void accept(StmtVisitor& visitor) override { visitor.visitExpressionStmt(this); }
    std::string toString() const override { return "ExprStmt(" + expression->toString() + ")"; }
    std::string toJson() const override {
         return "{ \"type\": \"ExpressionStmt\", \"line\": 0, \"value\": \"\", \"children\": [" + expression->toJson() + "] }";
    }
};

struct PrintStmt : public Stmt {
    std::shared_ptr<Expr> expression;
    PrintStmt(std::shared_ptr<Expr> expression) : expression(move(expression)) {}
    void accept(StmtVisitor& visitor) override { visitor.visitPrintStmt(this); }
    std::string toString() const override { return "Print(" + expression->toString() + ")"; }
    std::string toJson() const override {
        return "{ \"type\": \"PrintStmt\", \"line\": 0, \"value\": \"yazdir\", \"children\": [" + expression->toJson() + "] }";
    }
};

struct BlockStmt : public Stmt {
    std::vector<std::shared_ptr<Stmt>> statements;
    BlockStmt(std::vector<std::shared_ptr<Stmt>> statements) : statements(move(statements)) {}
    void accept(StmtVisitor& visitor) override { visitor.visitBlockStmt(this); }
    std::string toString() const override { return "Block"; }
    std::string toJson() const override {
        std::string s = "{ \"type\": \"BlockStmt\", \"line\": 0, \"value\": \"{}\", \"children\": [";
        for (size_t i = 0; i < statements.size(); ++i) {
            s += statements[i]->toJson();
            if (i < statements.size() - 1) s += ", ";
        }
        s += "] }";
        return s;
    }
};

struct IfStmt : public Stmt {
    std::shared_ptr<Expr> condition;
    std::shared_ptr<Stmt> thenBranch;
    std::shared_ptr<Stmt> elseBranch;
    IfStmt(std::shared_ptr<Expr> c, std::shared_ptr<Stmt> t, std::shared_ptr<Stmt> e) : condition(move(c)), thenBranch(move(t)), elseBranch(move(e)) {}
    void accept(StmtVisitor& visitor) override { visitor.visitIfStmt(this); }
    std::string toString() const override { return "If"; }
    std::string toJson() const override {
        std::string s = "{ \"type\": \"IfStmt\", \"line\": 0, \"value\": \"eger\", \"children\": [" + condition->toJson() + ", " + thenBranch->toJson();
        if (elseBranch) s += ", " + elseBranch->toJson();
        s += "] }";
        return s;
    }
};

struct WhileStmt : public Stmt {
    std::shared_ptr<Expr> condition;
    std::shared_ptr<Stmt> body;
    WhileStmt(std::shared_ptr<Expr> c, std::shared_ptr<Stmt> b) : condition(move(c)), body(move(b)) {}
    void accept(StmtVisitor& visitor) override { visitor.visitWhileStmt(this); }
    std::string toString() const override { return "While"; }
    std::string toJson() const override {
        return "{ \"type\": \"WhileStmt\", \"line\": 0, \"value\": \"dongu\", \"children\": [" + condition->toJson() + ", " + body->toJson() + "] }";
    }
};

struct BreakStmt : public Stmt {
    Token keyword;
    BreakStmt(Token k) : keyword(k) {}
    void accept(StmtVisitor& visitor) override { visitor.visitBreakStmt(this); }
    std::string toString() const override { return "Break"; }
    std::string toJson() const override {
        return "{ \"type\": \"BreakStmt\", \"line\": " + std::to_string(keyword.line) + 
               ", \"value\": \"kir\", \"children\": [] }";
    }
};

struct ContinueStmt : public Stmt {
    Token keyword;
    ContinueStmt(Token k) : keyword(k) {}
    void accept(StmtVisitor& visitor) override { visitor.visitContinueStmt(this); }
    std::string toString() const override { return "Continue"; }
    std::string toJson() const override {
        return "{ \"type\": \"ContinueStmt\", \"line\": " + std::to_string(keyword.line) + 
               ", \"value\": \"devam\", \"children\": [] }";
    }
};

struct TryCatchStmt : public Stmt {
    std::shared_ptr<Stmt> tryBlock;
    Token errorName;
    std::shared_ptr<Stmt> catchBlock;
    TryCatchStmt(std::shared_ptr<Stmt> t, Token err, std::shared_ptr<Stmt> c) : tryBlock(t), errorName(err), catchBlock(c) {}
    void accept(StmtVisitor& visitor) override { visitor.visitTryCatchStmt(this); }
    std::string toString() const override { return "TryCatch"; }
    std::string toJson() const override {
        return "{ \"type\": \"TryCatchStmt\", \"line\": 0, \"value\": \"deneme\", \"children\": [" + tryBlock->toJson() + ", " + catchBlock->toJson() + "] }";
    }
};

struct ListExpr : public Expr {
    std::vector<std::shared_ptr<Expr>> elements;
    ListExpr(std::vector<std::shared_ptr<Expr>> elements) : elements(move(elements)) {}
    void accept(ExprVisitor& visitor) override { visitor.visitListExpr(this); }
    std::string toString() const override { return "List"; }
    std::string toJson() const override {
        std::string s = "{ \"type\": \"ListExpr\", \"line\": 0, \"value\": \"[]\", \"children\": [";
        for (size_t i = 0; i < elements.size(); ++i) {
            s += elements[i]->toJson();
            if (i < elements.size() - 1) s += ", ";
        }
        s += "] }";
        return s;
    }
};

struct GetExpr : public Expr {
    std::shared_ptr<Expr> object;
    Token bracket; // Indexleme tokeni [
    std::shared_ptr<Expr> index;
    GetExpr(std::shared_ptr<Expr> o, Token b, std::shared_ptr<Expr> i) : object(move(o)), bracket(b), index(move(i)) {}
    void accept(ExprVisitor& visitor) override { visitor.visitGetExpr(this); }
    std::string toString() const override { return "Get"; }
    std::string toJson() const override {
        return "{ \"type\": \"IndexGetExpr\", \"line\": " + std::to_string(bracket.line) + 
               ", \"value\": \"[]\", \"children\": [" + object->toJson() + ", " + index->toJson() + "] }";
    }
};

struct IndexSetExpr : public Expr {
    std::shared_ptr<Expr> object;
    Token bracket;
    std::shared_ptr<Expr> index;
    std::shared_ptr<Expr> value;
    IndexSetExpr(std::shared_ptr<Expr> o, Token b, std::shared_ptr<Expr> i, std::shared_ptr<Expr> v) 
        : object(move(o)), bracket(b), index(move(i)), value(move(v)) {}
    void accept(ExprVisitor& visitor) override { visitor.visitIndexSetExpr(this); }
    std::string toString() const override { return "IndexSet"; }
    std::string toJson() const override {
        return "{ \"type\": \"IndexSetExpr\", \"line\": " + std::to_string(bracket.line) + 
               ", \"value\": \"[]=\", \"children\": [" + object->toJson() + ", " + index->toJson() + ", " + value->toJson() + "] }";
    }
};

struct PropertyExpr : public Expr {
    std::shared_ptr<Expr> object;
    Token name;
    PropertyExpr(std::shared_ptr<Expr> o, Token n) : object(move(o)), name(n) {}
    void accept(ExprVisitor& visitor) override { visitor.visitPropertyExpr(this); }
    std::string toString() const override { return "Prop"; }
    std::string toJson() const override {
        return "{ \"type\": \"PropertyExpr\", \"line\": " + std::to_string(name.line) + 
               ", \"value\": \".\" + \"" + jsonEscape(name.value) + "\", \"children\": [" + object->toJson() + "] }";
    }
};

struct SetExpr : public Expr {
    std::shared_ptr<Expr> object;
    Token name;
    std::shared_ptr<Expr> value;
    SetExpr(std::shared_ptr<Expr> o, Token n, std::shared_ptr<Expr> v) : object(move(o)), name(n), value(move(v)) {}
    void accept(ExprVisitor& visitor) override { visitor.visitSetExpr(this); }
    std::string toString() const override { return "Set"; }
    std::string toJson() const override {
        return "{ \"type\": \"SetExpr\", \"line\": " + std::to_string(name.line) + 
               ", \"value\": \"" + jsonEscape(name.value) + "\", \"children\": [" + object->toJson() + ", " + value->toJson() + "] }";
    }
};

struct ThisExpr : public Expr {
    Token keyword;
    int distance = -1;

    ThisExpr(Token k) : keyword(k) {}
    void accept(ExprVisitor& visitor) override { visitor.visitThisExpr(this); }
    std::string toString() const override { return "oz"; }
    std::string toJson() const override {
        return "{ \"type\": \"ThisExpr\", \"line\": " + std::to_string(keyword.line) + 
               ", \"value\": \"oz\", \"distance\": " + std::to_string(distance) + ", \"children\": [] }";
    }
};

struct SuperExpr : public Expr {
    Token keyword;
    Token method;
    int distance = -1;

    SuperExpr(Token k, Token m) : keyword(k), method(m) {}
    void accept(ExprVisitor& visitor) override { visitor.visitSuperExpr(this); }
    std::string toString() const override { return "ata"; }
    std::string toJson() const override {
         return "{ \"type\": \"SuperExpr\", \"line\": " + std::to_string(keyword.line) + 
               ", \"value\": \"ata." + jsonEscape(method.value) + "\", \"distance\": " + std::to_string(distance) + ", \"children\": [] }";
    }
};

struct CallExpr : public Expr {
    std::shared_ptr<Expr> callee;
    Token paren;
    std::vector<std::shared_ptr<Expr>> arguments;
    CallExpr(std::shared_ptr<Expr> c, Token p, std::vector<std::shared_ptr<Expr>> args) : callee(move(c)), paren(p), arguments(move(args)) {}
    void accept(ExprVisitor& visitor) override { visitor.visitCallExpr(this); }
    std::string toString() const override { return "Call"; }
    std::string toJson() const override {
        std::string s = "{ \"type\": \"CallExpr\", \"line\": " + std::to_string(paren.line) + 
               ", \"value\": \"()\", \"children\": [" + callee->toJson();
        for (const auto& arg : arguments) s += ", " + arg->toJson();
        s += "] }";
        return s;
    }
};

struct FunctionStmt : public Stmt {
    Token name;
    std::vector<Token> params;
    std::vector<std::shared_ptr<Stmt>> body;
    FunctionStmt(Token n, std::vector<Token> p, std::vector<std::shared_ptr<Stmt>> b) : name(n), params(move(p)), body(move(b)) {}
    void accept(StmtVisitor& visitor) override { visitor.visitFunctionStmt(this); }
    std::string toString() const override { return "Function"; }
    std::string toJson() const override {
        std::string s = "{ \"type\": \"FunctionStmt\", \"line\": " + std::to_string(name.line) + 
               ", \"value\": \"" + jsonEscape(name.value) + "\", \"children\": [";
        // Body block
         std::string bodyJson = "{ \"type\": \"BlockStmt\", \"line\": " + std::to_string(name.line) + 
               ", \"value\": \"body\", \"children\": [";
        for (size_t i = 0; i < body.size(); ++i) {
            bodyJson += body[i]->toJson();
            if (i < body.size() - 1) bodyJson += ", ";
        }
        bodyJson += "] }";
        s += bodyJson + "] }";
        return s;
    }
};

struct ClassStmt : public Stmt {
    Token name;
    std::shared_ptr<VariableExpr> superclass;
    std::vector<std::shared_ptr<FunctionStmt>> methods;
    ClassStmt(Token n, std::shared_ptr<VariableExpr> s, std::vector<std::shared_ptr<FunctionStmt>> m) : name(n), superclass(s), methods(move(m)) {}
    void accept(StmtVisitor& visitor) override { visitor.visitClassStmt(this); }
    std::string toString() const override { return "Class"; }
    std::string toJson() const override {
        std::string s = "{ \"type\": \"ClassStmt\", \"line\": " + std::to_string(name.line) + 
               ", \"value\": \"" + jsonEscape(name.value) + "\", \"children\": [";
        bool first = true;
        if (superclass) { s += superclass->toJson(); first = false; }
        for (const auto& m : methods) {
            if (!first) s += ", ";
            s += m->toJson();
            first = false;
        }
        s += "] }";
        return s;
    }
};

struct VarStmt : public Stmt {
    Token name;
    std::shared_ptr<Expr> initializer;
    VarStmt(Token n, std::shared_ptr<Expr> i) : name(n), initializer(move(i)) {}
    void accept(StmtVisitor& visitor) override { visitor.visitVarStmt(this); }
    std::string toString() const override { return "Var"; }
    std::string toJson() const override {
        std::string s = "{ \"type\": \"VarStmt\", \"line\": " + std::to_string(name.line) + 
               ", \"value\": \"" + jsonEscape(name.value) + "\", \"children\": [";
        if (initializer) s += initializer->toJson();
        s += "] }";
        return s;
    }
};

struct ReturnStmt : public Stmt {
    Token keyword;
    std::shared_ptr<Expr> value;
    ReturnStmt(Token k, std::shared_ptr<Expr> v) : keyword(k), value(move(v)) {}
    void accept(StmtVisitor& visitor) override { visitor.visitReturnStmt(this); }
    std::string toString() const override { return "Return"; }
    std::string toJson() const override {
        std::string s = "{ \"type\": \"ReturnStmt\", \"line\": " + std::to_string(keyword.line) + 
               ", \"value\": \"don\", \"children\": [";
        if (value) s += value->toJson();
        s += "] }";
        return s;
    }
};

struct ScopeResolutionExpr : public Expr {
    Token moduleName; Token name;
    ScopeResolutionExpr(Token m, Token n) : moduleName(m), name(n) {}
    void accept(ExprVisitor& visitor) override { visitor.visitScopeResolutionExpr(this); }
    std::string toString() const override { return "Scope"; }
    std::string toJson() const override {
        return "{ \"type\": \"ScopeExpr\", \"line\": " + std::to_string(moduleName.line) + 
               ", \"value\": \"" + jsonEscape(moduleName.value) + "::" + jsonEscape(name.value) + "\", \"children\": [] }";
    }
};

struct ModuleStmt : public Stmt {
    Token name;
    std::vector<std::shared_ptr<Stmt>> statements;
    ModuleStmt(Token n, std::vector<std::shared_ptr<Stmt>> s) : name(n), statements(move(s)) {}
    void accept(StmtVisitor& visitor) override { visitor.visitModuleStmt(this); }
    std::string toString() const override { return "Module"; }
    std::string toJson() const override {
        std::string s = "{ \"type\": \"ModuleStmt\", \"line\": " + std::to_string(name.line) + 
               ", \"value\": \"" + jsonEscape(name.value) + "\", \"children\": [";
        for (size_t i = 0; i < statements.size(); ++i) {
             s += statements[i]->toJson();
             if (i < statements.size()-1) s += ", ";
        }
        s += "] }";
        return s;
    }
};

struct ForStmt : public Stmt {
    Token keyword;  // 'dongu' keyword for line tracking
    std::shared_ptr<Stmt> initializer;
    std::shared_ptr<Expr> condition;
    std::shared_ptr<Expr> increment;
    std::shared_ptr<Stmt> body;
    
    ForStmt(Token kw, std::shared_ptr<Stmt> init, std::shared_ptr<Expr> cond, std::shared_ptr<Expr> inc, std::shared_ptr<Stmt> b)
    : keyword(kw), initializer(init), condition(cond), increment(inc), body(b) {}
    
    void accept(StmtVisitor& visitor) override { visitor.visitForStmt(this); }
    std::string toString() const override { return "For"; }
    std::string toJson() const override {
        std::string s = "{ \"type\": \"ForStmt\", \"line\": " + std::to_string(keyword.line) + 
               ", \"value\": \"dongu\", \"children\": [";
        bool first = true;
        if (initializer) { s += initializer->toJson(); first = false; }
        if (condition) { if(!first) s+=", "; s += condition->toJson(); first = false; }
        if (increment) { if(!first) s+=", "; s += increment->toJson(); first = false; }
        if (body) { if(!first) s+=", "; s += body->toJson(); }
        s += "] }";
        return s;
    }
};

struct MapExpr : public Expr {
    std::vector<std::shared_ptr<Expr>> keys;
    std::vector<std::shared_ptr<Expr>> values;
    MapExpr(std::vector<std::shared_ptr<Expr>> k, std::vector<std::shared_ptr<Expr>> v) : keys(move(k)), values(move(v)) {}
    void accept(ExprVisitor& visitor) override { visitor.visitMapExpr(this); }
    std::string toString() const override { return "Map"; }
    std::string toJson() const override {
        std::string s = "{ \"type\": \"MapExpr\", \"line\": 0, \"value\": \"{}\", \"children\": [";
        for (size_t i = 0; i < keys.size(); ++i) {
            s += "{ \"type\": \"Pair\", \"children\": [" + keys[i]->toJson() + ", " + values[i]->toJson() + "] }";
            if (i < keys.size() - 1) s += ", ";
        }
        s += "] }";
        return s;
    }
};

#endif // GUMUS_PARSER_AST_H
