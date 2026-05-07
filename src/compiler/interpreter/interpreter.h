#pragma once

#include "../parser/ast.h"
#include "../parser/arena.h"
#include "value.h"
#include "garbage_collector.h"
#include "../json_hata.h"
#include <memory>
#include <functional>
#include <unordered_map>
#include <vector>
#include <string>
#include <set>
#include <map>

// ============================================================
// Forward declarations
// ============================================================
class Interpreter;
class LoxInstance;
class LoxClass;

// ============================================================
// Callable — Çağrılabilir nesnelerin soyut arayüzü
// ============================================================
struct Callable {
    virtual ~Callable() = default;
    virtual Value call(Interpreter& interpreter, const std::vector<Value>& arguments) = 0;
    virtual int arity() = 0;
    virtual std::string toString() = 0;
};

// ============================================================
// Environment — Değişken kapsam yönetimi
// ============================================================
class Environment : public std::enable_shared_from_this<Environment> {
public:
    std::weak_ptr<Environment> enclosing;
    std::unordered_map<std::string, Value> values; // Geriye donuk uyumluluk (map tabanlı)
    std::vector<Value> valuesArray;                // YENI: Hizli index tabanli erisim
    std::string name;

    Environment() : name("Global") {}
    Environment(std::shared_ptr<Environment> enc, std::string n = "Blok")
        : enclosing(enc), name(n) {}

    // --- Hizli slot tabanlı erisim ---
    int defineFast(Value value) {
        valuesArray.push_back(value);
        return (int)valuesArray.size() - 1;
    }

    Value getAtSlot(int distance, int slot) {
        Environment* cur = this;
        for (int i = 0; i < distance; i++) cur = cur->enclosing.lock().get();
        return cur->valuesArray[slot];
    }

    void assignAtSlot(int distance, int slot, Value value) {
        Environment* cur = this;
        for (int i = 0; i < distance; i++) cur = cur->enclosing.lock().get();
        cur->valuesArray[slot] = value;
    }

    // --- Klasik map tabanlı erisim ---
    void define(const std::string& n, Value v) { values[n] = v; }

    Value get(const std::string& n) {
        for (Environment* cur = this; cur != nullptr;) {
            auto it = cur->values.find(n);
            if (it != cur->values.end()) return it->second;
            auto parent = cur->enclosing.lock();
            if (!parent) break;
            cur = parent.get();
        }
        throw GumusException("runtime_error", 0, "Tanımlanmamış değişken '" + n + "'.");
    }

    void assign(const std::string& n, Value v) {
        for (Environment* cur = this; cur != nullptr;) {
            auto it = cur->values.find(n);
            if (it != cur->values.end()) { it->second = v; return; }
            auto parent = cur->enclosing.lock();
            if (!parent) break;
            cur = parent.get();
        }
        throw GumusException("runtime_error", 0, "Tanımlanmamış değişken '" + n + "'.");
    }

    bool has(const std::string& n) {
        for (Environment* cur = this; cur != nullptr;) {
            if (cur->values.count(n)) return true;
            auto parent = cur->enclosing.lock();
            if (!parent) break;
            cur = parent.get();
        }
        return false;
    }

    Value getAt(int distance, const std::string& n) {
        Environment* cur = this;
        for (int i = 0; i < distance; i++) cur = cur->enclosing.lock().get();
        return cur->values[n];
    }

    void assignAt(int distance, const std::string& n, Value v) {
        Environment* cur = this;
        for (int i = 0; i < distance; i++) cur = cur->enclosing.lock().get();
        cur->values[n] = v;
    }

    std::string toJson() {
        std::string json = "{ \"scope\": \"" + name + "\", ";
        json += "\"id\": \"" + std::to_string((unsigned long long)this) + "\", ";
        json += "\"variables\": {";
        bool first = true;
        for (const auto& pair : values) {
            if (!first) json += ", ";
            json += "\"" + pair.first + "\": " + pair.second.toJson();
            first = false;
        }
        json += "}";
        auto parent = enclosing.lock();
        if (parent)
            json += ", \"parent_id\": \"" + std::to_string((unsigned long long)parent.get()) + "\"";
        else
            json += ", \"parent\": null";
        json += "}";
        return json;
    }
};

// ============================================================
// NativeFunction
// ============================================================
class NativeFunction : public Callable {
    std::function<Value(Interpreter&, const std::vector<Value>&)> func;
    int arityVal;
    std::string name;
public:
    NativeFunction(std::string name, int arity,
                   std::function<Value(Interpreter&, const std::vector<Value>&)> func)
        : name(name), arityVal(arity), func(func) {}

    Value call(Interpreter& interpreter, const std::vector<Value>& arguments) override;
    int arity() override;
    std::string toString() override;
};

// ============================================================
// UserFunction
// ============================================================
class UserFunction : public Callable {
public:
    FunctionStmt* declaration;
    std::shared_ptr<Environment> closure;

    UserFunction(FunctionStmt* declaration, std::shared_ptr<Environment> closure);

    int arity() override;
    std::shared_ptr<UserFunction> bind(std::shared_ptr<LoxInstance> instance);
    Value call(Interpreter& interpreter, const std::vector<Value>& arguments) override;
    std::string toString() override;
};

// ============================================================
// LoxInstance & LoxClass
// ============================================================
class LoxInstance : public std::enable_shared_from_this<LoxInstance> {
public:
    std::shared_ptr<LoxClass> klass;
    std::map<std::string, Value> fields;

    LoxInstance(std::shared_ptr<LoxClass> klass);
    Value get(Token name);
    void set(Token name, Value value);
    std::string toString();
};

class LoxClass : public Callable, public std::enable_shared_from_this<LoxClass> {
public:
    std::string name;
    std::shared_ptr<LoxClass> superclass;
    std::map<std::string, std::shared_ptr<Callable>> methods;

    LoxClass(std::string n, std::shared_ptr<LoxClass> sc,
             std::map<std::string, std::shared_ptr<Callable>> m)
        : name(n), superclass(sc), methods(m) {}

    Value call(Interpreter& interpreter, const std::vector<Value>& arguments) override;
    int arity() override;
    std::string toString() override;
    std::shared_ptr<Callable> findMethod(std::string name);
};

// ============================================================
// ExecutionResult & ExecutionStatus
// ============================================================
enum class ExecutionResult { OK, RETURN, BREAK, CONTINUE };

struct ExecutionStatus {
    ExecutionResult type;
    Value value;

    ExecutionStatus(ExecutionResult type = ExecutionResult::OK) : type(type) {}
    ExecutionStatus(ExecutionResult type, Value value) : type(type), value(value) {}
};

// ============================================================
// LoxRuntimeException
// ============================================================
struct LoxRuntimeException : public std::runtime_error {
    Value errorValue;
    int line = 0;
    int column = 0;
    std::string lineContent;
    std::vector<std::string> callstack;
    bool isSystemError = false;
    std::string suggestion;

    // Kullanıcı tanımlı fırlatma (firlat "hata")
    explicit LoxRuntimeException(Value errorValue)
        : std::runtime_error("runtime_error"), errorValue(errorValue), isSystemError(false) {}

    // Token tabanlı sistem hatası — TERCIH EDILEN kurucu
    LoxRuntimeException(const Token& token, const std::string& message,
                        const std::string& suggestion = "")
        : std::runtime_error(message), line(token.line), column(token.column),
          lineContent(token.lineContent), isSystemError(true), suggestion(suggestion) {
        errorValue = Value();
    }

    // Sadece satır numarası bilinen fallback — KULLANILMAMALI
    [[deprecated("Token& alan kurucuyu kullanin: LoxRuntimeException(token, mesaj)")]]
    LoxRuntimeException(int line, const std::string& message,
                        const std::string& suggestion = "")
        : std::runtime_error(message), line(line), column(0),
          isSystemError(true), suggestion(suggestion) {}
};

// ============================================================
// Module
// ============================================================
struct Module {
    std::string name;
    std::shared_ptr<Environment> environment;
};

// ============================================================
// GumusFunction (forward — interpreter.cpp içinde kullanılıyor)
// ============================================================
class GumusFunction : public Callable {};

// ============================================================
// Interpreter — TEK VE GERÇEK TANIM
// interpreter.cpp bu sınıfı implement eder.
// ============================================================
class Interpreter : public ExprVisitor, public StmtVisitor {
public:
    Interpreter();

    void interpret(const std::vector<Stmt*>& statements);
    void executeBlock(const std::vector<Stmt*>& statements,
                      std::shared_ptr<Environment> environment);
    Value evaluate(Expr* expr);
    void execute(Stmt* stmt);

    // --- Public state (UserFunction, native_functions, property_handlers erişimi) ---
    std::shared_ptr<Environment> globals;
    std::shared_ptr<Environment> environment;

    std::map<std::string, std::shared_ptr<Module>>   modules;
    std::map<std::string, std::shared_ptr<Callable>> functions;

    std::shared_ptr<void> activeInstance; // LoxInstance* (dairesel bağımlılık önlenir)

    std::set<std::string>    loadedFiles;
    std::vector<std::string> searchPaths;

    Value           lastEvaluatedValue;
    ExecutionStatus lastEvaluatedStatus;
    int             currentLine = 0;
    std::vector<std::string> callStack;

    MemoryArena      astArena;
    std::vector<Stmt*> astList;
    void persistAst(const std::vector<Stmt*>& statements);

    // 🗑️ Garbage Collection
    std::unique_ptr<GarbageCollector> garbageCollector;
    void initializeGC();
    void collectGarbage();
    size_t getGCObjectCount() const;
    size_t getGCBytesAllocated() const;

private:
    // --- Stmt Visitors ---
    void visitExpressionStmt(ExpressionStmt* stmt) override;
    void visitPrintStmt(PrintStmt* stmt) override;
    void visitIfStmt(IfStmt* stmt) override;
    void visitWhileStmt(WhileStmt* stmt) override;
    void visitBreakStmt(BreakStmt* stmt) override;
    void visitContinueStmt(ContinueStmt* stmt) override;
    void visitForStmt(ForStmt* stmt) override;
    void visitFunctionStmt(FunctionStmt* stmt) override;
    void visitReturnStmt(ReturnStmt* stmt) override;
    void visitBlockStmt(BlockStmt* stmt) override;
    void visitVarStmt(VarStmt* stmt) override;
    void visitClassStmt(ClassStmt* stmt) override;
    void visitTryCatchStmt(TryCatchStmt* stmt) override;
    void visitModuleStmt(ModuleStmt* stmt) override;
    void visitImportStmt(ImportStmt* stmt) override;

    // --- Expr Visitors ---
    void visitLiteralExpr(LiteralExpr* expr) override;
    void visitBinaryExpr(BinaryExpr* expr) override;
    void visitLogicalExpr(LogicalExpr* expr) override;
    void visitUnaryExpr(UnaryExpr* expr) override;
    void visitCallExpr(CallExpr* expr) override;
    void visitVariableExpr(VariableExpr* expr) override;
    void visitAssignExpr(AssignExpr* expr) override;
    void visitListExpr(ListExpr* expr) override;
    void visitGetExpr(GetExpr* expr) override;
    void visitIndexSetExpr(IndexSetExpr* expr) override;
    void visitPropertyExpr(PropertyExpr* expr) override;
    void visitSetExpr(SetExpr* expr) override;
    void visitThisExpr(ThisExpr* expr) override;
    void visitSuperExpr(SuperExpr* expr) override;
    void visitScopeResolutionExpr(ScopeResolutionExpr* expr) override;
    void visitMapExpr(MapExpr* expr) override;
};
