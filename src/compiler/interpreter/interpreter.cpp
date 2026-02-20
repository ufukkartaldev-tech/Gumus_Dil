#include "interpreter.h"
#include "native_functions.h" // Modüler Native Fonksiyonlar
#include <functional>
#include <cstdlib>
#include <ctime>
#include <cmath>
#include <algorithm>
#include <sstream>
#include <fstream>
#include <filesystem>
#include <thread>
#include <chrono>
#include <iostream>
#include <map>
#include "../debug.h"
#include "../json_hata.h"
#include "../lexer/tokenizer.h"
#include "../parser/parser.h"
#include "property_handlers.h"

static int _levenshteinDistance(const std::string& a, const std::string& b) {
    const size_t n = a.size();
    const size_t m = b.size();
    if (n == 0) return (int)m;
    if (m == 0) return (int)n;
    std::vector<int> prev(m + 1), cur(m + 1);
    for (size_t j = 0; j <= m; ++j) prev[j] = (int)j;
    for (size_t i = 1; i <= n; ++i) {
        cur[0] = (int)i;
        for (size_t j = 1; j <= m; ++j) {
            int cost = (a[i - 1] == b[j - 1]) ? 0 : 1;
            int del = prev[j] + 1;
            int ins = cur[j - 1] + 1;
            int sub = prev[j - 1] + cost;
            cur[j] = std::min({del, ins, sub});
        }
        prev.swap(cur);
    }
    return prev[m];
}

static bool _isSuggestionAcceptable(const std::string& name, const std::string& cand, int dist) {
    if (name.size() < 3) return false;
    if (cand.empty()) return false;
    if (name[0] != cand[0]) return false;
    const int maxLen = (int)std::max(name.size(), cand.size());
    if (maxLen <= 4) return dist <= 1;
    if (dist > 2) return false;
    if ((double)dist / (double)maxLen > 0.34) return false;
    return true;
}

static std::string _bestSuggestion(const Interpreter& interpreter, const std::string& name) {
    if (name.size() < 3) return "";
    std::string best;
    int bestDist = 999999;
    for (const auto& kv : interpreter.functions) {
        int d = _levenshteinDistance(name, kv.first);
        if (_isSuggestionAcceptable(name, kv.first, d) && d < bestDist) {
            bestDist = d;
            best = kv.first;
        }
    }
    if (interpreter.environment != nullptr) {
        for (const auto& kv : interpreter.environment->values) {
            int d = _levenshteinDistance(name, kv.first);
            if (_isSuggestionAcceptable(name, kv.first, d) && d < bestDist) {
                bestDist = d;
                best = kv.first;
            }
        }
    }
    return best;
}

#ifdef _WIN32
#include <windows.h>
#ifndef ENABLE_VIRTUAL_TERMINAL_PROCESSING
#define ENABLE_VIRTUAL_TERMINAL_PROCESSING 0x0004
#endif
#endif

Interpreter::Interpreter() {
#ifdef _WIN32
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    if (hOut != INVALID_HANDLE_VALUE) {
        DWORD dwMode = 0;
        if (GetConsoleMode(hOut, &dwMode)) {
            dwMode |= ENABLE_VIRTUAL_TERMINAL_PROCESSING;
            SetConsoleMode(hOut, dwMode);
        }
    }
#endif
    srand(time(0));
    globals = std::make_shared<Environment>();
    environment = globals;
    searchPaths.push_back(".");
    searchPaths.push_back("lib");
    searchPaths.push_back("std_lib");
    registerNativeFunctions(*this);
}

void Interpreter::interpret(const std::vector<std::shared_ptr<Stmt>>& statements) {
    for (const auto& stmt : statements) {
        execute(stmt);
    }
}

ExecutionStatus Interpreter::execute(std::shared_ptr<Stmt> stmt) {
    if (stmt == nullptr) return ExecutionStatus(ExecutionResult::OK);
    currentLine = stmt->line;
    stmt->accept(*this);
    ExecutionStatus result = lastEvaluatedStatus;
    if (gumus_memory_dump) {
        std::cout << "\n__MEMORY_JSON_START__\n";
        std::cout << "{ \"line\": " << currentLine << ", ";
        std::cout << "\"stack\": [";
        for (size_t i = 0; i < callStack.size(); ++i) {
            std::cout << "\"" << callStack[i] << "\"";
            if (i < callStack.size() - 1) std::cout << ", ";
        }
        std::cout << "], ";
        std::cout << "\"env\": " ;
        if (environment != nullptr) std::cout << environment->toJson();
        else std::cout << "null";
        std::cout << " }\n";
        std::cout << "__MEMORY_JSON_END__\n";
    }
    return result;
}

void Interpreter::visitFunctionStmt(FunctionStmt* stmt) {
    auto function = std::make_shared<UserFunction>(std::shared_ptr<FunctionStmt>(stmt, [](FunctionStmt*){}), environment);
    environment->define(stmt->name.value, Value(function, ValueType::FUNCTION, stmt->name.value));
    if (environment == globals) functions[stmt->name.value] = function;
    lastEvaluatedStatus = ExecutionStatus(ExecutionResult::OK);
}

void Interpreter::visitVarStmt(VarStmt* stmt) {
    Value value;
    if (stmt->initializer != nullptr) value = evaluate(stmt->initializer);
    environment->define(stmt->name.value, value);
    lastEvaluatedStatus = ExecutionStatus(ExecutionResult::OK);
}

void Interpreter::visitReturnStmt(ReturnStmt* stmt) {
    Value value;
    if (stmt->value != nullptr) value = evaluate(stmt->value);
    lastEvaluatedStatus = ExecutionStatus(ExecutionResult::RETURN, value);
}

void Interpreter::visitExpressionStmt(ExpressionStmt* stmt) {
    evaluate(stmt->expression);
    lastEvaluatedStatus = ExecutionStatus(ExecutionResult::OK);
}

void Interpreter::visitTryCatchStmt(TryCatchStmt* stmt) {
    try {
        visitBlockStmt(dynamic_cast<BlockStmt*>(stmt->tryBlock.get()));
        if (lastEvaluatedStatus.type != ExecutionResult::OK) return;
    } catch (LoxRuntimeException& ex) {
        auto catchEnv = std::make_shared<Environment>(environment, "HataYakalama");
        catchEnv->define(stmt->errorName.value, ex.errorValue);
        lastEvaluatedStatus = executeBlock(dynamic_cast<BlockStmt*>(stmt->catchBlock.get())->statements, catchEnv);
        return;
    } catch (std::runtime_error& ex) {
        auto catchEnv = std::make_shared<Environment>(environment, "HataYakalama");
        catchEnv->define(stmt->errorName.value, Value(std::string(ex.what())));
        lastEvaluatedStatus = executeBlock(dynamic_cast<BlockStmt*>(stmt->catchBlock.get())->statements, catchEnv);
        return;
    }
    lastEvaluatedStatus = ExecutionStatus(ExecutionResult::OK);
}

void Interpreter::visitPrintStmt(PrintStmt* stmt) {
    Value value = evaluate(stmt->expression);
    std::cout << value.toString() << "\n";
    lastEvaluatedStatus = ExecutionStatus(ExecutionResult::OK);
}

void Interpreter::visitIfStmt(IfStmt* stmt) {
    Value cond = evaluate(stmt->condition);
    bool isTrue = true;
    if (cond.type == ValueType::BOOLEAN && !cond.boolVal) isTrue = false;
    if (cond.type == ValueType::INTEGER && cond.intVal == 0) isTrue = false;
    if (cond.type == ValueType::NIL) isTrue = false;
    if (isTrue) execute(stmt->thenBranch);
    else if (stmt->elseBranch != nullptr) execute(stmt->elseBranch);
}

void Interpreter::visitWhileStmt(WhileStmt* stmt) {
    while (true) {
        Value cond = evaluate(stmt->condition);
        bool isTrue = true;
        if (cond.type == ValueType::BOOLEAN && !cond.boolVal) isTrue = false;
        if (cond.type == ValueType::INTEGER && cond.intVal == 0) isTrue = false;
        if (cond.type == ValueType::NIL) isTrue = false;
        if (!isTrue) break;
        execute(stmt->body);
        if (lastEvaluatedStatus.type == ExecutionResult::BREAK) { lastEvaluatedStatus = ExecutionStatus(ExecutionResult::OK); break; }
        if (lastEvaluatedStatus.type == ExecutionResult::CONTINUE) { lastEvaluatedStatus = ExecutionStatus(ExecutionResult::OK); continue; }
        if (lastEvaluatedStatus.type == ExecutionResult::RETURN) return;
    }
    lastEvaluatedStatus = ExecutionStatus(ExecutionResult::OK);
}

Value Interpreter::evaluate(std::shared_ptr<Expr> expr) {
    if (!expr) return Value();
    expr->accept(*this);
    return lastEvaluatedValue;
}

void Interpreter::visitLiteralExpr(LiteralExpr* expr) {
    if (expr->value.type == TokenType::KW_DOGRU || expr->value.value == "dogru") lastEvaluatedValue = Value(true);
    else if (expr->value.type == TokenType::KW_YANLIS || expr->value.value == "yanlis") lastEvaluatedValue = Value(false);
    else if (expr->value.type == TokenType::KW_BOS || expr->value.value == "bos") lastEvaluatedValue = Value();
    else if (expr->value.type == TokenType::INTEGER) {
        if (expr->value.value.find('.') != std::string::npos) lastEvaluatedValue = Value(std::stod(expr->value.value));
        else {
            try { lastEvaluatedValue = Value(std::stoi(expr->value.value)); }
            catch (...) { lastEvaluatedValue = Value(expr->value.value); }
        }
    } else lastEvaluatedValue = Value(expr->value.value);
}

void Interpreter::visitCallExpr(CallExpr* expr) {
    Value callee;
    try {
        callee = evaluate(expr->callee);
    } catch (const LoxRuntimeException& ex) {
        if (auto var = dynamic_cast<VariableExpr*>(expr->callee.get())) {
            throw LoxRuntimeException(var->name.line, "Tanimlanmamis fonksiyon: '" + var->name.value + "'.", ex.suggestion);
        }
        throw;
    }
    std::shared_ptr<Callable> function = nullptr;
    if (callee.type == ValueType::CLASS || callee.type == ValueType::FUNCTION) function = std::static_pointer_cast<Callable>(callee.obj);
    if (!function) throw LoxRuntimeException(0, "Sadece fonksiyonlar ve siniflar cagrilabilir."); 
    if (expr->arguments.size() != function->arity()) {
        std::string func_name = "bilinmeyen";
        if (auto var = dynamic_cast<VariableExpr*>(expr->callee.get())) func_name = var->name.value;
        else if (auto prop = dynamic_cast<PropertyExpr*>(expr->callee.get())) func_name = prop->name.value;
        throw LoxRuntimeException(expr->paren.line, "Fonksiyon '" + func_name + "': Beklenen parametre " + std::to_string(function->arity()) + " ama alinan " + std::to_string(expr->arguments.size()) + ".");
    }
    std::vector<Value> arguments;
    for (const auto& arg : expr->arguments) arguments.push_back(evaluate(arg));
    lastEvaluatedValue = function->call(*this, arguments);
}

void Interpreter::visitVariableExpr(VariableExpr* expr) {
    if (expr->name.type == TokenType::KW_DOGRU) { lastEvaluatedValue = Value(true); return; }
    if (expr->name.type == TokenType::KW_YANLIS) { lastEvaluatedValue = Value(false); return; }
    if (expr->distance != -1) lastEvaluatedValue = environment->getAt(expr->distance, expr->name.value);
    else {
        try { lastEvaluatedValue = globals->get(expr->name.value); }
        catch (const std::runtime_error&) {
            if (functions.count(expr->name.value)) {
                lastEvaluatedValue = Value(functions[expr->name.value], ValueType::FUNCTION, expr->name.value);
                return;
            }
            throw LoxRuntimeException(expr->name.line, "Tanimlanmamis degisken: '" + expr->name.value + "'.");
        }
    }
}

void Interpreter::visitAssignExpr(AssignExpr* expr) {
    Value value = evaluate(expr->value);
    if (expr->distance != -1) environment->assignAt(expr->distance, expr->name.value, value);
    else globals->assign(expr->name.value, value);
    lastEvaluatedValue = value;
}

void Interpreter::visitSetExpr(SetExpr* expr) {
    Value object = evaluate(expr->object);
    if (object.type != ValueType::INSTANCE) {
        throw LoxRuntimeException(expr->name.line, "Sadece nesnelerin ozellikleri atanabilir. Alinan tip: " + std::to_string((int)object.type));
    }
    if (!expr->name.value.empty() && expr->name.value[0] == '_') {
        if (activeInstance != object.obj) throw LoxRuntimeException(expr->name.line, "Ozel ozellige atama engellendi: '" + expr->name.value + "'.");
    }
    Value value = evaluate(expr->value);
    auto instance = std::static_pointer_cast<LoxInstance>(object.obj);
    instance->set(expr->name, value);
    lastEvaluatedValue = value;
}

void Interpreter::visitThisExpr(ThisExpr* expr) {
    if (expr->distance != -1) lastEvaluatedValue = environment->getAt(expr->distance, expr->keyword.value);
    else lastEvaluatedValue = globals->get(expr->keyword.value);
}

void Interpreter::visitListExpr(ListExpr* expr) {
    auto list = std::make_shared<ValueList>();
    for (const auto& el : expr->elements) list->push_back(evaluate(el));
    lastEvaluatedValue = Value(list);
}

void Interpreter::visitMapExpr(MapExpr* expr) {
    auto map = std::make_shared<std::map<std::string, Value>>();
    for (size_t i = 0; i < expr->keys.size(); ++i) {
        Value key = evaluate(expr->keys[i]);
        Value value = evaluate(expr->values[i]);
        (*map)[key.toString()] = value;
    }
    lastEvaluatedValue = Value(map);
}

void Interpreter::visitGetExpr(GetExpr* expr) {
    Value object = evaluate(expr->object);
    Value index = evaluate(expr->index);
    if (object.type == ValueType::LIST) {
        if (index.type != ValueType::INTEGER) throw LoxRuntimeException(expr->bracket.line, "Liste indeksi tamsayi olmalidir.");
        int i = index.intVal;
        if (i < 0 || i >= (int)object.listVal->size()) throw LoxRuntimeException(expr->bracket.line, "Liste indeks hatasi (sinir disi).");
        lastEvaluatedValue = (*object.listVal)[i];
    } else if (object.type == ValueType::MAP) {
        std::string key = index.toString();
        if (object.mapVal->count(key)) lastEvaluatedValue = (*object.mapVal)[key];
        else lastEvaluatedValue = Value();
    } else if (object.type == ValueType::STRING) {
        if (index.type != ValueType::INTEGER) throw LoxRuntimeException(expr->bracket.line, "Metin indeksi tamsayi olmalidir.");
        int i = index.intVal;
        if (i < 0 || i >= (int)object.stringVal.length()) throw LoxRuntimeException(expr->bracket.line, "Metin indeks hatasi (sinir disi).");
        lastEvaluatedValue = Value(std::string(1, object.stringVal[i]));
    } else throw LoxRuntimeException(expr->bracket.line, "Sadece listeler, metinler ve sozlukler indekslenebilir.");
}

void Interpreter::visitBinaryExpr(BinaryExpr* expr) {
    Value left;
    if (expr->left != nullptr) left = evaluate(expr->left);
    Value right = evaluate(expr->right);
    if (expr->left == nullptr) {
        switch (expr->op.type) {
            case TokenType::MINUS: lastEvaluatedValue = Value(-right.intVal); break;
            case TokenType::BANG: lastEvaluatedValue = Value(!right.boolVal && right.intVal == 0); break;
            default: break;
        }
        return;
    }
    if (expr->op.type == TokenType::EQUAL_EQUAL || expr->op.type == TokenType::BANG_EQUAL) {
        bool isEqual = false;
        if (left.type == right.type) {
             switch (left.type) {
                 case ValueType::INTEGER: isEqual = (left.intVal == right.intVal); break;
                 case ValueType::FLOAT: isEqual = (left.floatVal == right.floatVal); break;
                 case ValueType::BOOLEAN: isEqual = (left.boolVal == right.boolVal); break;
                 case ValueType::STRING: isEqual = (left.stringVal == right.stringVal); break;
                 case ValueType::NIL: isEqual = true; break;
                 default: isEqual = false; break; 
             }
        }
        if (expr->op.type == TokenType::EQUAL_EQUAL) lastEvaluatedValue = Value(isEqual);
        else lastEvaluatedValue = Value(!isEqual);
        return;
    }
    if ((left.type == ValueType::INTEGER || left.type == ValueType::FLOAT) && (right.type == ValueType::INTEGER || right.type == ValueType::FLOAT)) {
        bool isFloat = (left.type == ValueType::FLOAT || right.type == ValueType::FLOAT);
        double l = (left.type == ValueType::FLOAT) ? left.floatVal : (double)left.intVal;
        double r = (right.type == ValueType::FLOAT) ? right.floatVal : (double)right.intVal;
        switch (expr->op.type) {
            case TokenType::PLUS: lastEvaluatedValue = isFloat ? Value(l + r) : Value((int)(l + r)); break;
            case TokenType::MINUS: lastEvaluatedValue = isFloat ? Value(l - r) : Value((int)(l - r)); break;
            case TokenType::MULTIPLY: lastEvaluatedValue = isFloat ? Value(l * r) : Value((int)(l * r)); break;
            case TokenType::DIVIDE: if (r == 0) throw LoxRuntimeException(expr->op.line, "Sifira bolunme hatasi."); lastEvaluatedValue = isFloat ? Value(l / r) : Value((int)(l / r)); break;
            case TokenType::MOD: if (r == 0) throw LoxRuntimeException(expr->op.line, "Sifira gore mod alma hatasi."); lastEvaluatedValue = isFloat ? Value(std::fmod(l, r)) : Value((int)l % (int)r); break;
            case TokenType::GREATER: lastEvaluatedValue = Value(l > r); break;
            case TokenType::GREATER_EQUAL: lastEvaluatedValue = Value(l >= r); break;
            case TokenType::LESS: lastEvaluatedValue = Value(l < r); break;
            case TokenType::LESS_EQUAL: lastEvaluatedValue = Value(l <= r); break;
            default: break;
        }
    } else if (expr->op.type == TokenType::PLUS) {
        if (left.type == ValueType::STRING) lastEvaluatedValue = Value(left.stringVal + right.toString());
        else if (right.type == ValueType::STRING) lastEvaluatedValue = Value(left.toString() + right.stringVal);
        else lastEvaluatedValue = Value();
    } else lastEvaluatedValue = Value();
}

void Interpreter::visitClassStmt(ClassStmt* stmt) {
    std::shared_ptr<LoxClass> superclass = nullptr;
    if (stmt->superclass != nullptr) {
        Value scVal = evaluate(stmt->superclass);
        if (scVal.type != ValueType::CLASS) throw LoxRuntimeException(stmt->name.line, "Ust sinif bir sinif olmalidir.");
        superclass = std::static_pointer_cast<LoxClass>(scVal.obj);
    }
    environment->define(stmt->name.value, Value());
    if (superclass != nullptr) {
        environment = std::make_shared<Environment>(environment, "SinifAta");
        environment->define("ata", Value(superclass, ValueType::CLASS, superclass->name));
    }
    std::map<std::string, std::shared_ptr<Callable>> methods;
    for (const auto& method : stmt->methods) {
        auto function = std::make_shared<UserFunction>(method, environment);
        methods[method->name.value] = function;
    }
    auto klass = std::make_shared<LoxClass>(stmt->name.value, superclass, methods);
    if (superclass != nullptr) environment = environment->enclosing.lock();
    environment->assign(stmt->name.value, Value(klass, ValueType::CLASS, stmt->name.value));
    lastEvaluatedStatus = ExecutionStatus(ExecutionResult::OK);
}

void Interpreter::visitPropertyExpr(PropertyExpr* expr) {
    Value object = evaluate(expr->object);
    Value res;
    if (PropertyHandlers::handle(*this, object, expr->name.value, res)) { lastEvaluatedValue = res; return; }
    if (object.type == ValueType::INSTANCE) {
        if (!expr->name.value.empty() && expr->name.value[0] == '_') {
            if (activeInstance != object.obj) throw LoxRuntimeException(expr->name.line, "Ozel ozellige erisim engellendi: '" + expr->name.value + "'.");
        }
        auto instance = std::static_pointer_cast<LoxInstance>(object.obj);
        lastEvaluatedValue = instance->get(expr->name);
    } else throw LoxRuntimeException(expr->name.line, "Sadece nesnelerin veya yerlesik tiplerin ozellikleri/metotlari olabilir.");
}

ExecutionStatus Interpreter::executeBlock(const std::vector<std::shared_ptr<Stmt>>& statements, std::shared_ptr<Environment> env) {
    std::shared_ptr<Environment> previous = this->environment;
    this->environment = env;
    try {
        for (const auto& stmt : statements) {
            ExecutionStatus result = execute(stmt);
            if (result.type != ExecutionResult::OK) { this->environment = previous; return result; }
        }
    } catch (...) { this->environment = previous; throw; }
    this->environment = previous;
    return ExecutionStatus(ExecutionResult::OK);
}

void Interpreter::visitBlockStmt(BlockStmt* stmt) {
    lastEvaluatedStatus = executeBlock(stmt->statements, std::make_shared<Environment>(environment, "Blok"));
}

void Interpreter::visitLogicalExpr(LogicalExpr* expr) {
    Value left = evaluate(expr->left);
    bool isTrue = true;
    if (left.type == ValueType::BOOLEAN && !left.boolVal) isTrue = false;
    else if (left.type == ValueType::INTEGER && left.intVal == 0) isTrue = false;
    else if (left.type == ValueType::NIL) isTrue = false;
    if (expr->op.type == TokenType::LOGIC_OR) { if (isTrue) { lastEvaluatedValue = left; return; } }
    else { if (!isTrue) { lastEvaluatedValue = left; return; } }
    lastEvaluatedValue = evaluate(expr->right);
}

void Interpreter::visitUnaryExpr(UnaryExpr* expr) {
    Value right = evaluate(expr->right);
    switch (expr->op.type) {
        case TokenType::MINUS: if (right.type == ValueType::INTEGER) lastEvaluatedValue = Value(-right.intVal); break;
        case TokenType::BANG: {
            bool isTrue = true;
            if (right.type == ValueType::BOOLEAN && !right.boolVal) isTrue = false;
            else if (right.type == ValueType::INTEGER && right.intVal == 0) isTrue = false;
            else if (right.type == ValueType::NIL) isTrue = false;
            lastEvaluatedValue = Value(!isTrue);
            break;
        }
        default: break;
    }
}

void Interpreter::visitForStmt(ForStmt* stmt) {
    std::shared_ptr<Environment> previous = this->environment;
    this->environment = std::make_shared<Environment>(previous, "Dongu");
    try {
        if (stmt->initializer != nullptr) execute(stmt->initializer);
        while (true) {
            if (stmt->condition != nullptr) {
                Value cond = evaluate(stmt->condition);
                bool isTrue = true;
                if (cond.type == ValueType::BOOLEAN && !cond.boolVal) isTrue = false;
                else if (cond.type == ValueType::INTEGER && cond.intVal == 0) isTrue = false;
                else if (cond.type == ValueType::NIL) isTrue = false;
                if (!isTrue) break;
            }
            execute(stmt->body);
            if (lastEvaluatedStatus.type == ExecutionResult::BREAK) { lastEvaluatedStatus = ExecutionStatus(ExecutionResult::OK); break; }
            if (lastEvaluatedStatus.type == ExecutionResult::CONTINUE) { lastEvaluatedStatus = ExecutionStatus(ExecutionResult::OK); }
            if (lastEvaluatedStatus.type == ExecutionResult::RETURN) { this->environment = previous; return; }
            if (stmt->increment != nullptr) evaluate(stmt->increment);
        }
    } catch (...) { this->environment = previous; throw; }
    this->environment = previous;
    lastEvaluatedStatus = ExecutionStatus(ExecutionResult::OK);
}

void Interpreter::visitBreakStmt(BreakStmt* stmt) { lastEvaluatedStatus = ExecutionStatus(ExecutionResult::BREAK); }
void Interpreter::visitContinueStmt(ContinueStmt* stmt) { lastEvaluatedStatus = ExecutionStatus(ExecutionResult::CONTINUE); }

void Interpreter::visitIndexSetExpr(IndexSetExpr* expr) {
    Value object = evaluate(expr->object);
    Value index = evaluate(expr->index);
    Value value = evaluate(expr->value);
    if (object.type == ValueType::LIST) {
        if (index.type != ValueType::INTEGER) throw LoxRuntimeException(expr->bracket.line, "Liste indeksi tamsayi olmalidir.");
        int i = index.intVal;
        if (i < 0 || i >= (int)object.listVal->size()) throw LoxRuntimeException(expr->bracket.line, "Liste indeks hatasi (sinir disi).");
        (*object.listVal)[i] = value;
    } else if (object.type == ValueType::MAP) (*object.mapVal)[index.toString()] = value;
    else throw LoxRuntimeException(expr->bracket.line, "Sadece listelere ve sozluklere indeks ile atama yapilabilir.");
    lastEvaluatedValue = value;
}

void Interpreter::visitSuperExpr(SuperExpr* expr) {
    int distance = expr->distance;
    Value superclass = environment->getAt(distance, "ata");
    Value object = environment->getAt(distance - 1, "\xC3\xB6" "z"); 
    if (superclass.type != ValueType::CLASS) throw LoxRuntimeException(expr->keyword.line, "'ata' bulunamadi. Mesafe: " + std::to_string(distance));
    if (object.type != ValueType::INSTANCE) throw LoxRuntimeException(expr->keyword.line, "'oz' bulunamadi. Mesafe: " + std::to_string(distance - 1));
    auto klass = std::static_pointer_cast<LoxClass>(superclass.obj);
    auto instance = std::static_pointer_cast<LoxInstance>(object.obj);
    std::shared_ptr<Callable> method = klass->findMethod(expr->method.value);
    if (!method) throw LoxRuntimeException(expr->method.line, "Ust sinifta '" + expr->method.value + "' metodu bulunamadi.");
    if (auto userMethod = std::dynamic_pointer_cast<UserFunction>(method)) lastEvaluatedValue = Value(userMethod->bind(instance), ValueType::FUNCTION);
    else lastEvaluatedValue = Value(method, ValueType::FUNCTION);
}

void Interpreter::visitModuleStmt(ModuleStmt* stmt) {
    auto moduleEnv = std::make_shared<Environment>(globals, "Modul:" + stmt->name.value);
    auto module = std::make_shared<Module>();
    module->name = stmt->name.value;
    module->environment = moduleEnv;
    modules[stmt->name.value] = module;
    auto previous = this->environment;
    this->environment = moduleEnv;
    try {
        for (const auto& statement : stmt->statements) {
            execute(statement);
            if (lastEvaluatedStatus.type == ExecutionResult::RETURN) { this->environment = previous; return; }
        }
    } catch (...) { this->environment = previous; throw; }
    this->environment = previous;
    lastEvaluatedStatus = ExecutionStatus(ExecutionResult::OK);
}

void Interpreter::visitScopeResolutionExpr(ScopeResolutionExpr* expr) {
    std::string moduleName = expr->moduleName.value;
    if (modules.find(moduleName) == modules.end()) throw LoxRuntimeException(0, "Modul bulunamadi: '" + moduleName + "'.");
    auto module = modules[moduleName];
    try { lastEvaluatedValue = module->environment->get(expr->name.value); }
    catch (...) { throw LoxRuntimeException(0, "Modul '" + moduleName + "' icinde '" + expr->name.value + "' bulunamadi."); }
}
