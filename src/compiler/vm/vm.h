#ifndef VM_H
#define VM_H

#include <vector>
#include <map>
#include <string>
#include <memory>
#include "chunk.h"
#include "op_code.h"
#include "../interpreter/value.h"

// 🎯 VM Configuration
#define FRAMES_MAX 64
#define STACK_MAX 256

enum InterpretResult {
    INTERPRET_OK,
    INTERPRET_COMPILE_ERROR,
    INTERPRET_RUNTIME_ERROR
};

// 🔧 VM Data Structures
struct Upvalue {
    Value* location;
    Value closed;
    Upvalue* next;
    
    Upvalue(Value* loc) : location(loc), next(nullptr) {}
};

struct Function {
    std::string name;
    int arity;
    Chunk chunk;
    std::vector<Upvalue*> upvalues;
    
    Function() : arity(0) {}
};

struct CallFrame {
    Function* function;
    uint8_t* ip;
    Value* slots;
};

// 📊 VM Statistics
struct VMStats {
    size_t instructionCount;
    size_t stackSize;
    int frameCount;
    size_t globalCount;
    size_t memoryUsage;
    size_t gcTriggerThreshold;
};

class VM {
public:
    VM();
    ~VM();

    // 🚀 Core execution
    InterpretResult run(Chunk* chunk);
    
    // 📊 Statistics and debugging
    VMStats getStats() const;
    void dumpStack() const;
    void dumpGlobals() const;

private:
    // 💾 VM State
    Chunk* chunk;
    uint8_t* ip;
    std::vector<Value> stack;
    Value* stackTop;
    std::vector<Value> globals;
    std::vector<CallFrame> frames;
    int frameCount;
    Upvalue* openUpvalues;
    
    // 📈 Performance tracking
    size_t instructionCount;
    size_t gcTriggerThreshold;
    
    // 🔧 Core execution loop
    InterpretResult runLoop();
    
    // 📚 Stack operations
    void push(Value value);
    Value pop();
    Value peek(int distance);
    
    // 📖 Bytecode reading
    uint8_t readByte();
    uint16_t readShort();
    Value readConstant();
    Value readConstantLong();
    std::string readString();
    
    // 🎯 Value operations
    bool valuesEqual(const Value& a, const Value& b);
    bool isFalsey(const Value& value);
    
    // 🚨 Error handling
    void runtimeError(const std::string& message);
    void resetStack();
    
    // 📞 Function calls
    CallFrame* getCurrentFrame();
    bool callValue(Value callee, int argCount);
    void closeUpvalues(Value* last);
    
    // 🗑️ Memory management
    void checkGC();
    size_t getCurrentMemoryUsage() const;
};

// 🎯 Binary operation macro
#define BINARY_OP(intOp, floatOp) \
    do { \
        Value b = pop(); \
        Value a = pop(); \
        \
        if (a.type == ValueType::FLOAT || b.type == ValueType::FLOAT) { \
            double av = (a.type == ValueType::FLOAT) ? a.floatVal : (double)a.intVal; \
            double bv = (b.type == ValueType::FLOAT) ? b.floatVal : (double)b.intVal; \
            push(Value(av floatOp bv)); \
        } else if (a.type == ValueType::INTEGER && b.type == ValueType::INTEGER) { \
            push(Value(a.intVal intOp b.intVal)); \
        } else { \
            runtimeError("Operands must be numbers."); \
            return INTERPRET_RUNTIME_ERROR; \
        } \
    } while (false)

#endif // VM_H
