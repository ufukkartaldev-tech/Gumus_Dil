#include "vm.h"
#include "chunk.h"
#include "../interpreter/garbage_collector.h"
#include <iostream>
#include <stdexcept>
#include <cmath>
#include <chrono>

VM::VM() : chunk(nullptr), ip(nullptr), frameCount(0), openUpvalues(nullptr) {
    // Initialize call stack
    frames.resize(FRAMES_MAX);
    
    // Initialize stack
    stack.reserve(STACK_MAX);
    stackTop = stack.data();
    
    // Initialize globals table
    globals.reserve(256);
    
    // Performance counters
    instructionCount = 0;
    gcTriggerThreshold = 1024 * 1024; // 1MB
    
    if (gumus_debug) {
        std::cout << "🚀 VM initialized with " << STACK_MAX << " stack slots\n";
    }
}

VM::~VM() {
    // Cleanup upvalues
    while (openUpvalues != nullptr) {
        Upvalue* upvalue = openUpvalues;
        openUpvalues = upvalue->next;
        delete upvalue;
    }
}

InterpretResult VM::run(Chunk* chunk) {
    this->chunk = chunk;
    this->ip = chunk->code.data();
    
    auto startTime = std::chrono::high_resolution_clock::now();
    
    try {
        return runLoop();
    } catch (const std::exception& e) {
        std::cerr << "🚨 Runtime error: " << e.what() << "\n";
        return INTERPRET_RUNTIME_ERROR;
    }
}

InterpretResult VM::runLoop() {
    // Traditional switch-based dispatch
    for (;;) {
        instructionCount++;
        if (instructionCount % 1000 == 0) {
            checkGC();
        }
        
        uint8_t instruction = readByte();
        
        switch (instruction) {
            case OP_CONSTANT:
                push(readConstant());
                break;
                
            case OP_CONSTANT_LONG:
                push(readConstantLong());
                break;
                
            case OP_NIL:
                push(Value());
                break;
                
            case OP_TRUE:
                push(Value(true));
                break;
                
            case OP_FALSE:
                push(Value(false));
                break;
                
            case OP_POP:
                pop();
                break;
                
            case OP_DUP:
                push(peek(0));
                break;
                
            case OP_SWAP: {
                Value a = pop();
                Value b = pop();
                push(a);
                push(b);
                break;
            }
            
            case OP_GET_LOCAL: {
                uint8_t slot = readByte();
                push(getCurrentFrame()->slots[slot]);
                break;
            }
            
            case OP_SET_LOCAL: {
                uint8_t slot = readByte();
                getCurrentFrame()->slots[slot] = peek(0);
                break;
            }
            
            case OP_GET_GLOBAL: {
                uint8_t index = readByte();
                if (index >= globals.size() || globals[index].type == ValueType::UNDEFINED) {
                    runtimeError("Undefined variable.");
                    return INTERPRET_RUNTIME_ERROR;
                }
                push(globals[index]);
                break;
            }
            
            case OP_DEFINE_GLOBAL: {
                uint8_t index = readByte();
                if (index >= globals.size()) {
                    globals.resize(index + 1, Value(ValueType::UNDEFINED));
                }
                globals[index] = pop();
                break;
            }
            
            case OP_SET_GLOBAL: {
                uint8_t index = readByte();
                if (index >= globals.size() || globals[index].type == ValueType::UNDEFINED) {
                    runtimeError("Undefined variable.");
                    return INTERPRET_RUNTIME_ERROR;
                }
                globals[index] = peek(0);
                break;
            }
            
            case OP_EQUAL: {
                Value b = pop();
                Value a = pop();
                push(Value(valuesEqual(a, b)));
                break;
            }
            
            case OP_NOT_EQUAL: {
                Value b = pop();
                Value a = pop();
                push(Value(!valuesEqual(a, b)));
                break;
            }
            
            case OP_GREATER: {
                BINARY_OP(>, >);
                break;
            }
            
            case OP_GREATER_EQUAL: {
                BINARY_OP(>=, >=);
                break;
            }
            
            case OP_LESS: {
                BINARY_OP(<, <);
                break;
            }
            
            case OP_LESS_EQUAL: {
                BINARY_OP(<=, <=);
                break;
            }
            
            case OP_ADD: {
                Value b = pop();
                Value a = pop();
                
                if (a.type == ValueType::STRING || b.type == ValueType::STRING) {
                    push(Value(a.toString() + b.toString()));
                } else if (a.type == ValueType::FLOAT || b.type == ValueType::FLOAT) {
                    double av = (a.type == ValueType::FLOAT) ? a.floatVal : (double)a.intVal;
                    double bv = (b.type == ValueType::FLOAT) ? b.floatVal : (double)b.intVal;
                    push(Value(av + bv));
                } else if (a.type == ValueType::INTEGER && b.type == ValueType::INTEGER) {
                    push(Value(a.intVal + b.intVal));
                } else {
                    runtimeError("Operands must be numbers or strings.");
                    return INTERPRET_RUNTIME_ERROR;
                }
                break;
            }
            
            case OP_SUBTRACT: {
                BINARY_OP(-, -);
                break;
            }
            
            case OP_MULTIPLY: {
                BINARY_OP(*, *);
                break;
            }
            
            case OP_DIVIDE: {
                Value b = pop();
                Value a = pop();
                
                if (a.type == ValueType::FLOAT || b.type == ValueType::FLOAT) {
                    double av = (a.type == ValueType::FLOAT) ? a.floatVal : (double)a.intVal;
                    double bv = (b.type == ValueType::FLOAT) ? b.floatVal : (double)b.intVal;
                    
                    if (bv == 0.0) {
                        runtimeError("Division by zero.");
                        return INTERPRET_RUNTIME_ERROR;
                    }
                    
                    push(Value(av / bv));
                } else if (a.type == ValueType::INTEGER && b.type == ValueType::INTEGER) {
                    if (b.intVal == 0) {
                        runtimeError("Division by zero.");
                        return INTERPRET_RUNTIME_ERROR;
                    }
                    push(Value(a.intVal / b.intVal));
                } else {
                    runtimeError("Operands must be numbers.");
                    return INTERPRET_RUNTIME_ERROR;
                }
                break;
            }
            
            case OP_MODULO: {
                Value b = pop();
                Value a = pop();
                
                if (a.type == ValueType::INTEGER && b.type == ValueType::INTEGER) {
                    if (b.intVal == 0) {
                        runtimeError("Modulo by zero.");
                        return INTERPRET_RUNTIME_ERROR;
                    }
                    push(Value(a.intVal % b.intVal));
                } else {
                    runtimeError("Operands must be integers.");
                    return INTERPRET_RUNTIME_ERROR;
                }
                break;
            }
            
            case OP_NEGATE: {
                Value val = pop();
                if (val.type == ValueType::FLOAT) {
                    push(Value(-val.floatVal));
                } else if (val.type == ValueType::INTEGER) {
                    push(Value(-val.intVal));
                } else {
                    runtimeError("Operand must be a number.");
                    return INTERPRET_RUNTIME_ERROR;
                }
                break;
            }
            
            case OP_NOT: {
                push(Value(isFalsey(pop())));
                break;
            }
            
            case OP_PRINT: {
                std::cout << pop().toString() << "\n";
                break;
            }
            
            case OP_JUMP: {
                uint16_t offset = readShort();
                ip += offset;
                break;
            }
            
            case OP_JUMP_IF_FALSE: {
                uint16_t offset = readShort();
                if (isFalsey(peek(0))) ip += offset;
                break;
            }
            
            case OP_JUMP_IF_TRUE: {
                uint16_t offset = readShort();
                if (!isFalsey(peek(0))) ip += offset;
                break;
            }
            
            case OP_LOOP: {
                uint16_t offset = readShort();
                ip -= offset;
                break;
            }
            
            case OP_CALL: {
                int argCount = readByte();
                if (!callValue(peek(argCount), argCount)) {
                    return INTERPRET_RUNTIME_ERROR;
                }
                break;
            }
            
            case OP_RETURN: {
                Value result = pop();
                
                // Close upvalues
                closeUpvalues(getCurrentFrame()->slots);
                
                frameCount--;
                if (frameCount == 0) {
                    pop(); // Pop the script function
                    return INTERPRET_OK;
                }
                
                // Reset stack
                stackTop = getCurrentFrame()->slots;
                push(result);
                break;
            }
            
            case OP_HALT:
                return INTERPRET_OK;
                
            case OP_NOP:
                break;
                
            default:
                runtimeError("Unknown opcode.");
                return INTERPRET_RUNTIME_ERROR;
        }
    }
}

// 🔧 Helper methods
void VM::push(Value value) {
    if (stackTop - stack.data() >= STACK_MAX) {
        runtimeError("Stack overflow.");
        throw std::runtime_error("Stack overflow");
    }
    *stackTop = value;
    stackTop++;
}

Value VM::pop() {
    if (stackTop == stack.data()) {
        runtimeError("Stack underflow.");
        throw std::runtime_error("Stack underflow");
    }
    stackTop--;
    return *stackTop;
}

Value VM::peek(int distance) {
    return stackTop[-1 - distance];
}

uint8_t VM::readByte() {
    return *ip++;
}

uint16_t VM::readShort() {
    ip += 2;
    return (uint16_t)((ip[-2] << 8) | ip[-1]);
}

Value VM::readConstant() {
    return chunk->constants[readByte()];
}

Value VM::readConstantLong() {
    uint32_t index = readByte() | (readByte() << 8) | (readByte() << 16);
    return chunk->constants[index];
}

std::string VM::readString() {
    return readConstant().getString();
}

bool VM::valuesEqual(const Value& a, const Value& b) {
    if (a.type != b.type) return false;
    
    switch (a.type) {
        case ValueType::BOOLEAN: return a.boolVal == b.boolVal;
        case ValueType::NIL: return true;
        case ValueType::INTEGER: return a.intVal == b.intVal;
        case ValueType::FLOAT: return a.floatVal == b.floatVal;
        case ValueType::STRING: return a.getString() == b.getString();
        default: return false;
    }
}

bool VM::isFalsey(const Value& value) {
    return value.type == ValueType::NIL || 
           (value.type == ValueType::BOOLEAN && !value.boolVal) ||
           (value.type == ValueType::INTEGER && value.intVal == 0);
}

void VM::runtimeError(const std::string& message) {
    std::cerr << "🚨 Runtime Error: " << message << "\n";
    
    // Print stack trace
    for (int i = frameCount - 1; i >= 0; i--) {
        CallFrame* frame = &frames[i];
        size_t instruction = frame->ip - frame->function->chunk.code.data() - 1;
        std::cerr << "[line " << frame->function->chunk.lines[instruction] << "] in ";
        
        if (frame->function->name.empty()) {
            std::cerr << "script\n";
        } else {
            std::cerr << frame->function->name << "()\n";
        }
    }
    
    resetStack();
}

void VM::resetStack() {
    stackTop = stack.data();
    frameCount = 0;
    openUpvalues = nullptr;
}

CallFrame* VM::getCurrentFrame() {
    return &frames[frameCount - 1];
}

bool VM::callValue(Value callee, int argCount) {
    // Simplified call implementation
    // In a full implementation, this would handle different callable types
    runtimeError("Calling not yet implemented.");
    return false;
}

void VM::closeUpvalues(Value* last) {
    while (openUpvalues != nullptr && openUpvalues->location >= last) {
        Upvalue* upvalue = openUpvalues;
        upvalue->closed = *upvalue->location;
        upvalue->location = &upvalue->closed;
        openUpvalues = upvalue->next;
    }
}

void VM::checkGC() {
    // Trigger GC if memory usage exceeds threshold
    size_t currentMemory = getCurrentMemoryUsage();
    if (currentMemory > gcTriggerThreshold) {
        if (gumus_debug) {
            std::cout << "🧹 Triggering GC: " << currentMemory << " bytes used\n";
            std::cout << "ℹ️  GC yalnizca Interpreter uzerinden calisir (Tek GC Rejimi).\n";
        }
        // VM kendi GC'sini tetiklemiyor - g_gc KALDIRILDI.
        // Bytecode VM icin ilerleyen surumde Interpreter::garbageCollector
        // VM'e referans olarak verilecek.
        gcTriggerThreshold *= 2; // Esigi yukari cek, tekrar tetiklenmesin

    }
}

size_t VM::getCurrentMemoryUsage() const {
    return stack.capacity() * sizeof(Value) +
           globals.capacity() * sizeof(Value) +
           frames.capacity() * sizeof(CallFrame);
}

VMStats VM::getStats() const {
    VMStats stats;
    stats.instructionCount = instructionCount;
    stats.stackSize = stackTop - stack.data();
    stats.frameCount = frameCount;
    stats.globalCount = globals.size();
    stats.memoryUsage = getCurrentMemoryUsage();
    stats.gcTriggerThreshold = gcTriggerThreshold;
    return stats;
}

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