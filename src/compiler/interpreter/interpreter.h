#pragma once

#include "../parser/ast.h"
#include "../parser/arena.h"
#include "value.h"
#include "garbage_collector.h"
#include <memory> 
#include <functional>
#include <unordered_map>
#include <vector>
#include <string>
#include <set>

namespace gumus {
namespace compiler {
namespace interpreter {

// Forward declarations for modular components
class StatementExecutor;
class ExpressionEvaluator;
class ErrorSuggestion;

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

class Environment : public std::enable_shared_from_this<Environment> {
public:
    std::weak_ptr<Environment> enclosing;
    std::unordered_map<std::string, Value> values; // Geriye donuk uyumluluk
    std::vector<Value> valuesArray;                // YENI: Hizli Index tabanli erisim
    std::string name;

    Environment() : name("Global") {}
    Environment(std::shared_ptr<Environment> enclosing, std::string name = "Blok") : enclosing(enclosing), name(name) {}

    // Yeni Hizli Erisim Yapisi (Resolver'da slot atamasi gectikten sonra kullanilacak)
    int defineFast(Value value) {
        valuesArray.push_back(value);
        return valuesArray.size() - 1; // Slot indexini donderir
    }

    Value getAtSlot(int distance, int slot) {
        Environment* current = this;
        for (int i = 0; i < distance; i++) {
            auto parent = current->enclosing.lock();
            current = parent.get();
        }
        return current->valuesArray[slot];
    }

    void assignAtSlot(int distance, int slot, Value value) {
        Environment* current = this;
        for (int i = 0; i < distance; i++) {
            auto parent = current->enclosing.lock();
            current = parent.get();
        }
        current->valuesArray[slot] = value;
    }

    // Klasik yavas map tabanli methodlar 
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
        
        throw GumusException("runtime_error", 0, "Tanımlanmamış değişken '" + name + "'.");
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
        
        throw GumusException("runtime_error", 0, "Tanımlanmamış değişken '" + name + "'.");
    }
};

/**
 * Main Interpreter class - now modular and focused on coordination
 * Delegates specific execution tasks to specialized components
 */
class Interpreter : public ExprVisitor<Value>, public StmtVisitor<Value> {
public:
    Interpreter();
    
    // Main execution methods
    void interpret(const std::vector<Stmt*>& statements);
    Value evaluate(Expr* expr);
    void execute(Stmt* stmt);
    
    // Public interface for modular components
    std::shared_ptr<Environment> globals;
    std::shared_ptr<Environment> environment;
    std::unordered_map<std::string, std::shared_ptr<GumusFunction>> functions;
    std::vector<std::string> searchPaths;
    
    // Visitor interface (delegated to modules)
    Value visitBinaryExpr(BinaryExpr* expr) override;
    Value visitUnaryExpr(UnaryExpr* expr) override;
    Value visitCallExpr(CallExpr* expr) override;
    Value visitGetExpr(GetExpr* expr) override;
    Value visitSetExpr(SetExpr* expr) override;
    Value visitAssignExpr(AssignExpr* expr) override;
    Value visitVariableExpr(VariableExpr* expr) override;
    Value visitLiteralExpr(LiteralExpr* expr) override;
    Value visitGroupingExpr(GroupingExpr* expr) override;
    Value visitLogicalExpr(LogicalExpr* expr) override;
    Value visitThisExpr(ThisExpr* expr) override;
    Value visitSuperExpr(SuperExpr* expr) override;
    
    Value visitFunctionStmt(FunctionStmt* stmt) override;
    Value visitClassStmt(ClassStmt* stmt) override;
    Value visitBlockStmt(BlockStmt* stmt) override;
    Value visitVarStmt(VarStmt* stmt) override;
    Value visitIfStmt(IfStmt* stmt) override;
    Value visitWhileStmt(WhileStmt* stmt) override;
    Value visitReturnStmt(ReturnStmt* stmt) override;
    Value visitPrintStmt(PrintStmt* stmt) override;
    Value visitExpressionStmt(ExpressionStmt* stmt) override;

private:
    // Modular components
    std::unique_ptr<StatementExecutor> statementExecutor;
    std::unique_ptr<ExpressionEvaluator> expressionEvaluator;
    std::unique_ptr<ErrorSuggestion> errorSuggestion;
    
    // Helper methods
    void initializeNativeFunctions();
    void setupSearchPaths();
    
    friend class StatementExecutor;
    friend class ExpressionEvaluator;
    friend class ErrorSuggestion;
};

} // namespace interpreter
} // namespace compiler  
} // namespace gumus        throw std::runtime_error("Tanimlanmamis degisken: '" + name + "'.");
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
    FunctionStmt* declaration;
    std::shared_ptr<Environment> closure;

    UserFunction(FunctionStmt* declaration, std::shared_ptr<Environment> closure);

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
    int column = 0;
    std::string lineContent = "";
    std::vector<std::string> callstack;
    bool isSystemError = false;
    std::string suggestion;

    // User-defined throw (firlat "hata")
    LoxRuntimeException(Value errorValue)
        : std::runtime_error("runtime_error"), errorValue(errorValue), isSystemError(false) {}

    // System error with TOKEN - TERCIH EDILEN kurucu (^ isareti calisir)
    LoxRuntimeException(const Token& token, const std::string& message, const std::string& suggestion = "")
        : std::runtime_error(message), line(token.line), column(token.column),
          lineContent(token.lineContent), isSystemError(true), suggestion(suggestion) {
        errorValue = Value();
    }

    // int line alan kurucu - KULLANILMAMALI, sadece Token bilinemediginde fallback
    // Yeni kod Token& alan kurucuyu kullanmali
    [[deprecated("Token& alan kurucuyu kullanin: LoxRuntimeException(token, mesaj)")]]
    LoxRuntimeException(int line, const std::string& message, const std::string& suggestion = "")
        : std::runtime_error(message), line(line), column(0), isSystemError(true), suggestion(suggestion) {}
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
    void interpret(const std::vector<Stmt*>& statements);
    void executeBlock(const std::vector<Stmt*>& statements, std::shared_ptr<Environment> environment);
    
    Value evaluate(Expr* expr);
    void execute(Stmt* stmt);
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

    // AST Persistence & Memory Management
    MemoryArena astArena;
    std::vector<Stmt*> astList;
    void persistAst(const std::vector<Stmt*>& statements);
    
    // 🗑️ Garbage Collection (Tek Rejim)
    std::unique_ptr<GarbageCollector> garbageCollector;

    void initializeGC();
    void collectGarbage();
    size_t getGCObjectCount() const;
    size_t getGCBytesAllocated() const;
private:
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
    void visitImportStmt(ImportStmt* stmt) override;


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
