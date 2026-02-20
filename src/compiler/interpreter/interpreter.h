#ifndef INTERPRETER_H
#define INTERPRETER_H

#include "../parser/ast.h"
#include "value.h"
#include "garbage_collector.h"
#include <memory> 
#include <functional>
#include <unordered_map>
#include <vector>
#include <string>
#include <set>

// Forward decls
class Interpreter;
class LoxInstance;
class LoxClass;

struct Callable {
    virtual ~Callable() = default;
    virtual Value call(Interpreter& interpreter, const std::vector<Value>& arguments) = 0;
    virtual int arity() = 0;
    virtual std::string toString() = 0;
};

// Environment Class for Scoping (Moved UP because UserFunction needs it)
class Environment : public std::enable_shared_from_this<Environment> {
public:
    std::weak_ptr<Environment> enclosing;
    std::unordered_map<std::string, Value> values;
    std::string name;

    Environment() : name("Global") {}
    Environment(std::shared_ptr<Environment> enclosing, std::string name = "Blok") : enclosing(enclosing), name(name) {}

    void define(const std::string& name, Value value) {
        values[name] = value;
    }

    Value get(const std::string& name) {
        Environment* current = this;
        while (current != nullptr) {
            auto it = current->values.find(name);
            if (it != current->values.end()) return it->second;
            
            auto parent = current->enclosing.lock();
            if (parent == nullptr) break;
            current = parent.get();
        }
        throw std::runtime_error("Tanimlanmamis degisken: '" + name + "'.");
    }

    void assign(const std::string& name, Value value) {
        Environment* current = this;
        while (current != nullptr) {
            auto it = current->values.find(name);
            if (it != current->values.end()) {
                it->second = value;
                return;
            }
            
            auto parent = current->enclosing.lock();
            if (parent == nullptr) break;
            current = parent.get();
        }
        throw std::runtime_error("Tanimlanmamis degisken: '" + name + "'.");
    }
    
    bool has(const std::string& name) {
        Environment* current = this;
        while (current != nullptr) {
            if (current->values.count(name)) return true;
            
            auto parent = current->enclosing.lock();
            if (parent == nullptr) break;
            current = parent.get();
        }
        return false;
    }

    Value getAt(int distance, const std::string& name) {
        Environment* current = this;
        for (int i = 0; i < distance; i++) {
            auto parent = current->enclosing.lock();
            current = parent.get();
        }
        return current->values[name];
    }

    void assignAt(int distance, const std::string& name, Value value) {
        Environment* current = this;
        for (int i = 0; i < distance; i++) {
            auto parent = current->enclosing.lock();
            current = parent.get();
        }
        current->values[name] = value;
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
        if (parent != nullptr) {
            json += ", \"parent_id\": \"" + std::to_string((unsigned long long)parent.get()) + "\"";
        } else {
            json += ", \"parent\": null";
        }
        json += "}";
        return json;
    }
};

// --- NativeFunction & UserFunction Definitions ---

class NativeFunction : public Callable {
    std::function<Value(Interpreter&, const std::vector<Value>&)> func;
    int arityVal;
    std::string name;
public:
    NativeFunction(std::string name, int arity, std::function<Value(Interpreter&, const std::vector<Value>&)> func)
        : name(name), arityVal(arity), func(func) {}

    Value call(Interpreter& interpreter, const std::vector<Value>& arguments);
    int arity();
    std::string toString();
};

class UserFunction : public Callable {
public:
    std::shared_ptr<FunctionStmt> declaration;
    std::shared_ptr<Environment> closure;

    UserFunction(std::shared_ptr<FunctionStmt> declaration, std::shared_ptr<Environment> closure);

    int arity();
    std::shared_ptr<UserFunction> bind(std::shared_ptr<LoxInstance> instance);
    Value call(Interpreter& interpreter, const std::vector<Value>& arguments);
    std::string toString();
};


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

    LoxClass(std::string name, std::shared_ptr<LoxClass> superclass, std::map<std::string, std::shared_ptr<Callable>> methods)
        : name(name), superclass(superclass), methods(methods) {}

    Value call(Interpreter& interpreter, const std::vector<Value>& arguments);
    int arity();
    std::string toString();
    
    std::shared_ptr<Callable> findMethod(std::string name);
};


enum class ExecutionResult {
    OK,
    RETURN,
    BREAK,
    CONTINUE
};

struct ExecutionStatus {
    ExecutionResult type;
    Value value;

    ExecutionStatus(ExecutionResult type = ExecutionResult::OK) : type(type) {}
    ExecutionStatus(ExecutionResult type, Value value) : type(type), value(value) {}
};

// Exception for User-Level Lox Errors (Try-Catch) & System Errors
struct LoxRuntimeException : public std::runtime_error {
    Value errorValue;
    int line = 0;
    bool isSystemError = false;
    std::string suggestion;

    // User-defined throw (firlat "hata")
    LoxRuntimeException(Value errorValue) 
        : std::runtime_error("runtime_error"), errorValue(errorValue), isSystemError(false) {}

    // System error (e.g. division by zero)
    LoxRuntimeException(int line, const std::string& message, const std::string& suggestion = "") 
        : std::runtime_error(message), line(line), isSystemError(true), suggestion(suggestion) {
            errorValue = Value(message);
        }
};

// Environment Class...

struct Module {
    std::string name;
    std::shared_ptr<Environment> environment;
};

// ... NativeFunction definintions ...

class Interpreter : public ExprVisitor, public StmtVisitor {

public:
    Interpreter(); 
    void interpret(const std::vector<std::shared_ptr<Stmt>>& statements);
    ExecutionStatus executeBlock(const std::vector<std::shared_ptr<Stmt>>& statements, std::shared_ptr<Environment> environmentVal);

    // Environment Management (Public for UserFunction Access)
    std::shared_ptr<Environment> globals;
    std::shared_ptr<Environment> environment;
    
    // Module Map
    std::map<std::string, std::shared_ptr<Module>> modules;
    
    // Function Map
    std::map<std::string, std::shared_ptr<Callable>> functions;

    // Access Control: Currently executing instance (this)
    std::shared_ptr<void> activeInstance; // void* to avoid circular dependency loop in header logic
    
    // Import Management
    std::set<std::string> loadedFiles;
    std::vector<std::string> searchPaths;

    // Visitor Pattern Support
    Value lastEvaluatedValue;
    ExecutionStatus lastEvaluatedStatus;
    int currentLine = 0;
    std::vector<std::string> callStack;

    // AST Persistence (to prevent dangling pointers in imported functions)
    std::vector<std::vector<std::shared_ptr<Stmt>>> astList;
    
    // 🗑️ Garbage Collection
    std::unique_ptr<GarbageCollector> garbageCollector;
    
    // 📊 Memory Analytics
    void initializeGC();
    void collectGarbage();
    GarbageCollector::MemoryStats getMemoryStats() const;
    std::string generateMemoryReport() const;
private:
    ExecutionStatus execute(std::shared_ptr<Stmt> stmt);
    Value evaluate(std::shared_ptr<Expr> expr);

    // Visitor Pattern Implementation - Stmt Visitors
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


    // Visitor Pattern Implementation - Expr Visitors
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

#endif // INTERPRETER_H
