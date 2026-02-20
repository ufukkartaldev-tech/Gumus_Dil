#include "interpreter.h"
#include <sstream>

// Moved to value.h context or handled differently


// --- UserFunction Implementation ---

UserFunction::UserFunction(std::shared_ptr<FunctionStmt> declaration, std::shared_ptr<Environment> closure) 
    : declaration(declaration), closure(closure) {}

int UserFunction::arity() { 
    return declaration->params.size(); 
}

std::shared_ptr<UserFunction> UserFunction::bind(std::shared_ptr<LoxInstance> instance) {
    auto environment = std::make_shared<Environment>(closure, "Baglam:oz");
    environment->define("\xC3\xB6" "z", Value(instance, ValueType::INSTANCE, instance->klass->name));
    return std::make_shared<UserFunction>(declaration, environment);


}

Value UserFunction::call(Interpreter& interpreter, const std::vector<Value>& arguments) {
    auto environment = std::make_shared<Environment>(closure, "Fonksiyon:" + declaration->name.value);
    interpreter.callStack.push_back(declaration->name.value);
    
    // Save and update active instance for access control
    auto previousInstance = interpreter.activeInstance;
    if (closure->has("\xC3\xB6" "z")) {
        interpreter.activeInstance = closure->get("\xC3\xB6" "z").obj;
    } else {



        interpreter.activeInstance = nullptr;
    }

    // Define args
    for (size_t i = 0; i < declaration->params.size(); ++i) {
        environment->define(declaration->params[i].value, arguments[i]);
    }

    Value returnValue; // Defaults to NIL
    try {
        ExecutionStatus status = interpreter.executeBlock(declaration->body, environment);
        if (status.type == ExecutionResult::RETURN) {
            returnValue = status.value;
        }
    } catch (...) {
        interpreter.activeInstance = previousInstance;
        throw;
    }

    interpreter.activeInstance = previousInstance;
    interpreter.callStack.pop_back();
    return returnValue;
}

std::string UserFunction::toString() { 
    return "<fonksiyon " + declaration->name.value + ">"; 
}

// --- LoxInstance Implementation ---
LoxInstance::LoxInstance(std::shared_ptr<LoxClass> klass) : klass(klass) {}

Value LoxInstance::get(Token name) {
   if (fields.count(name.value)) {
       return fields[name.value];
   }

   std::shared_ptr<Callable> method = klass->findMethod(name.value);
   if (method) {
        // UserFunction bind islemi
        if (auto userFunc = std::dynamic_pointer_cast<UserFunction>(method)) {
             return Value(userFunc->bind(shared_from_this()), ValueType::FUNCTION, name.value);
        }
        return Value(method, ValueType::FUNCTION, name.value);
   }

   throw LoxRuntimeException(name.line, "Belirsiz ozellik '" + name.value + "'.");
}

void LoxInstance::set(Token name, Value value) {
   fields[name.value] = value;
}

// Removed to resolve linker issues

std::string LoxInstance::toString() {
   return klass->name + " nesnesi";
}

Value LoxClass::call(Interpreter& interpreter, const std::vector<Value>& arguments) {
    auto instance = std::make_shared<LoxInstance>(shared_from_this());
    interpreter.callStack.push_back(name + "::kurucu");
    
    std::shared_ptr<Callable> initializer = findMethod("kurucu");
    if (initializer != nullptr) {
        // Init bind edilir
        if (auto userFunc = std::dynamic_pointer_cast<UserFunction>(initializer)) {
             userFunc->bind(instance)->call(interpreter, arguments);
        } else {
            initializer->call(interpreter, arguments); 
        }
    }
    
    interpreter.callStack.pop_back();
    return Value(instance, ValueType::INSTANCE, name);
}

int LoxClass::arity() {
    std::shared_ptr<Callable> initializer = findMethod("kurucu");
    if (initializer != nullptr) return initializer->arity();
    return 0;
}

std::string LoxClass::toString() { 
    return "<sinif " + name + ">"; 
}

std::shared_ptr<Callable> LoxClass::findMethod(std::string name) {
    if (methods.count(name)) return methods[name];
    
    if (superclass != nullptr) {
        return superclass->findMethod(name);
    }

    return nullptr;
}
