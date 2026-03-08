#include "vm.h"
#include <iostream>
#include <stdexcept>
#include <cmath>

VM::VM() {
    ip = nullptr;
    chunk = nullptr;
}

VM::~VM() {}

InterpretResult VM::run(Chunk* chunk) {
    this->chunk = chunk;
    this->ip = chunk->code.data();

#ifdef __GNUC__
    static void* dispatchTable[] = {
        &&label_OP_CONSTANT, &&label_OP_NIL, &&label_OP_TRUE, &&label_OP_FALSE,
        &&label_OP_POP, &&label_OP_GET_LOCAL, &&label_OP_SET_LOCAL, &&label_OP_GET_GLOBAL,
        &&label_OP_DEFINE_GLOBAL, &&label_OP_SET_GLOBAL, &&label_OP_GET_UPVALUE, &&label_OP_SET_UPVALUE,
        &&label_OP_GET_PROPERTY, &&label_OP_SET_PROPERTY, &&label_OP_GET_SUPER, &&label_OP_EQUAL,
        &&label_OP_GREATER, &&label_OP_LESS, &&label_OP_ADD, &&label_OP_SUBTRACT,
        &&label_OP_MULTIPLY, &&label_OP_DIVIDE, &&label_OP_NOT, &&label_OP_NEGATE,
        &&label_OP_PRINT, &&label_OP_JUMP, &&label_OP_JUMP_IF_FALSE, &&label_OP_LOOP,
        &&label_OP_CALL, &&label_OP_INVOKE, &&label_OP_SUPER_INVOKE, &&label_OP_CLOSURE,
        &&label_OP_CLOSE_UPVALUE, &&label_OP_RETURN, &&label_OP_CLASS, &&label_OP_INHERIT,
        &&label_OP_METHOD
    };

    #define DISPATCH() goto *dispatchTable[readByte()]
    
    DISPATCH();

label_OP_CONSTANT:
    {
        Value constant = readConstant();
        push(constant);
        DISPATCH();
    }
label_OP_NIL: push(Value()); DISPATCH();
label_OP_TRUE: push(Value(true)); DISPATCH();
label_OP_FALSE: push(Value(false)); DISPATCH();
label_OP_POP: pop(); DISPATCH();

label_OP_GET_LOCAL:
label_OP_SET_LOCAL:
label_OP_GET_UPVALUE:
label_OP_SET_UPVALUE:
label_OP_GET_PROPERTY:
label_OP_SET_PROPERTY:
label_OP_GET_SUPER:
label_OP_CALL:
label_OP_INVOKE:
label_OP_SUPER_INVOKE:
label_OP_CLOSURE:
label_OP_CLOSE_UPVALUE:
label_OP_CLASS:
label_OP_INHERIT:
label_OP_METHOD:
    return INTERPRET_RUNTIME_ERROR;

label_OP_EQUAL:
    {
        Value b = pop();
        Value a = pop();
        bool isEqual = false;
        if (a.type == b.type) {
            switch (a.type) {
                case ValueType::INTEGER: isEqual = (a.intVal == b.intVal); break;
                case ValueType::FLOAT: isEqual = (a.floatVal == b.floatVal); break;
                case ValueType::BOOLEAN: isEqual = (a.boolVal == b.boolVal); break;
                case ValueType::STRING: isEqual = (a.getString() == b.getString()); break;
                case ValueType::NIL: isEqual = true; break;
                default: isEqual = false; break; 
            }
        }
        push(Value(isEqual));
        DISPATCH();
    }
label_OP_GREATER:
    {
        Value b = pop();
        Value a = pop();
        if (a.type == b.type && a.type == ValueType::INTEGER) push(Value(a.intVal > b.intVal));
        else if (a.type == ValueType::FLOAT || b.type == ValueType::FLOAT) {
            double av = (a.type == ValueType::FLOAT) ? a.floatVal : (double)a.intVal;
            double bv = (b.type == ValueType::FLOAT) ? b.floatVal : (double)b.intVal;
            push(Value(av > bv));
        }
        DISPATCH();
    }
label_OP_LESS:
    {
        Value b = pop();
        Value a = pop();
        if (a.type == b.type && a.type == ValueType::INTEGER) push(Value(a.intVal < b.intVal));
        else if (a.type == ValueType::FLOAT || b.type == ValueType::FLOAT) {
            double av = (a.type == ValueType::FLOAT) ? a.floatVal : (double)a.intVal;
            double bv = (b.type == ValueType::FLOAT) ? b.floatVal : (double)b.intVal;
            push(Value(av < bv));
        }
        DISPATCH();
    }
label_OP_ADD:
    {
        Value b = pop();
        Value a = pop();
        if (a.type == ValueType::STRING || b.type == ValueType::STRING) {
            push(Value(a.toString() + b.toString()));
        } else if (a.type == ValueType::FLOAT || b.type == ValueType::FLOAT) {
            double av = (a.type == ValueType::FLOAT) ? a.floatVal : (double)a.intVal;
            double bv = (b.type == ValueType::FLOAT) ? b.floatVal : (double)b.intVal;
            push(Value(av + bv));
        } else {
            push(Value(a.intVal + b.intVal));
        }
        DISPATCH();
    }
label_OP_SUBTRACT:
    {
        Value b = pop();
        Value a = pop();
        if (a.type == ValueType::FLOAT || b.type == ValueType::FLOAT) {
            double av = (a.type == ValueType::FLOAT) ? a.floatVal : (double)a.intVal;
            double bv = (b.type == ValueType::FLOAT) ? b.floatVal : (double)b.intVal;
            push(Value(av - bv));
        } else {
            push(Value(a.intVal - b.intVal));
        }
        DISPATCH();
    }
label_OP_MULTIPLY:
    {
        Value b = pop();
        Value a = pop();
        if (a.type == ValueType::FLOAT || b.type == ValueType::FLOAT) {
            double av = (a.type == ValueType::FLOAT) ? a.floatVal : (double)a.intVal;
            double bv = (b.type == ValueType::FLOAT) ? b.floatVal : (double)b.intVal;
            push(Value(av * bv));
        } else {
            push(Value(a.intVal * b.intVal));
        }
        DISPATCH();
    }
label_OP_DIVIDE:
    {
        Value b = pop();
        Value a = pop();
        double bv = (b.type == ValueType::FLOAT) ? b.floatVal : (double)b.intVal;
        if (bv == 0) return INTERPRET_RUNTIME_ERROR;
        if (a.type == ValueType::FLOAT || b.type == ValueType::FLOAT) {
            double av = (a.type == ValueType::FLOAT) ? a.floatVal : (double)a.intVal;
            push(Value(av / bv));
        } else {
            push(Value(a.intVal / (int)bv));
        }
        DISPATCH();
    }
label_OP_NOT:
    {
        Value val = pop();
        bool isTrue = true;
        if (val.type == ValueType::BOOLEAN && !val.boolVal) isTrue = false;
        else if (val.type == ValueType::INTEGER && val.intVal == 0) isTrue = false;
        else if (val.type == ValueType::NIL) isTrue = false;
        push(Value(!isTrue));
        DISPATCH();
    }
label_OP_NEGATE:
    {
        Value val = pop();
        if (val.type == ValueType::FLOAT) push(Value(-val.floatVal));
        else push(Value(-val.intVal));
        DISPATCH();
    }
label_OP_PRINT:
    {
        std::cout << pop().toString() << "\n";
        DISPATCH();
    }
label_OP_DEFINE_GLOBAL:
    {
        uint8_t index = readByte();
        if (index >= globals.size()) globals.resize(index + 1, Value(ValueType::UNDEFINED));
        globals[index] = pop();
        DISPATCH();
    }
label_OP_GET_GLOBAL:
    {
        uint8_t index = readByte();
        if (index >= globals.size() || globals[index].type == ValueType::UNDEFINED) {
            return INTERPRET_RUNTIME_ERROR;
        }
        push(globals[index]);
        DISPATCH();
    }
label_OP_SET_GLOBAL:
    {
        uint8_t index = readByte();
        if (index >= globals.size() || globals[index].type == ValueType::UNDEFINED) {
            return INTERPRET_RUNTIME_ERROR;
        }
        globals[index] = stack.back(); 
        DISPATCH();
    }
label_OP_JUMP:
    {
        uint16_t offset = (uint16_t)(readByte() << 8);
        offset |= readByte();
        ip += offset;
        DISPATCH();
    }
label_OP_JUMP_IF_FALSE:
    {
        uint16_t offset = (uint16_t)(readByte() << 8);
        offset |= readByte();
        Value val = stack.back();
        bool isTrue = true;
        if (val.type == ValueType::BOOLEAN && !val.boolVal) isTrue = false;
        else if (val.type == ValueType::INTEGER && val.intVal == 0) isTrue = false;
        else if (val.type == ValueType::NIL) isTrue = false;
        
        if (!isTrue) ip += offset;
        DISPATCH();
    }
label_OP_LOOP:
    {
        uint16_t offset = (uint16_t)(readByte() << 8);
        offset |= readByte();
        ip -= offset;
        DISPATCH();
    }
label_OP_RETURN:
    return INTERPRET_OK;

#else
    for (;;) {
        uint8_t instruction = readByte();
        switch (instruction) {
            case OP_CONSTANT: {
                Value constant = readConstant();
                push(constant);
                break;
            }
            case OP_NIL: push(Value()); break;
            case OP_TRUE: push(Value(true)); break;
            case OP_FALSE: push(Value(false)); break;
            case OP_POP: pop(); break;
            
            case OP_EQUAL: {
                Value b = pop();
                Value a = pop();
                bool isEqual = false;
                if (a.type == b.type) {
                    switch (a.type) {
                        case ValueType::INTEGER: isEqual = (a.intVal == b.intVal); break;
                        case ValueType::FLOAT: isEqual = (a.floatVal == b.floatVal); break;
                        case ValueType::BOOLEAN: isEqual = (a.boolVal == b.boolVal); break;
                        case ValueType::STRING: isEqual = (a.getString() == b.getString()); break;
                        case ValueType::NIL: isEqual = true; break;
                        default: isEqual = false; break; 
                    }
                }
                push(Value(isEqual));
                break;
            }
            case OP_GREATER: {
                Value b = pop();
                Value a = pop();
                if (a.type == b.type && a.type == ValueType::INTEGER) push(Value(a.intVal > b.intVal));
                else if (a.type == ValueType::FLOAT || b.type == ValueType::FLOAT) {
                    double av = (a.type == ValueType::FLOAT) ? a.floatVal : (double)a.intVal;
                    double bv = (b.type == ValueType::FLOAT) ? b.floatVal : (double)b.intVal;
                    push(Value(av > bv));
                }
                break;
            }
            case OP_LESS: {
                Value b = pop();
                Value a = pop();
                if (a.type == b.type && a.type == ValueType::INTEGER) push(Value(a.intVal < b.intVal));
                else if (a.type == ValueType::FLOAT || b.type == ValueType::FLOAT) {
                    double av = (a.type == ValueType::FLOAT) ? a.floatVal : (double)a.intVal;
                    double bv = (b.type == ValueType::FLOAT) ? b.floatVal : (double)b.intVal;
                    push(Value(av < bv));
                }
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
                } else {
                    push(Value(a.intVal + b.intVal));
                }
                break;
            }
            case OP_SUBTRACT: {
                Value b = pop();
                Value a = pop();
                if (a.type == ValueType::FLOAT || b.type == ValueType::FLOAT) {
                    double av = (a.type == ValueType::FLOAT) ? a.floatVal : (double)a.intVal;
                    double bv = (b.type == ValueType::FLOAT) ? b.floatVal : (double)b.intVal;
                    push(Value(av - bv));
                } else {
                    push(Value(a.intVal - b.intVal));
                }
                break;
            }
            case OP_MULTIPLY: {
                Value b = pop();
                Value a = pop();
                if (a.type == ValueType::FLOAT || b.type == ValueType::FLOAT) {
                    double av = (a.type == ValueType::FLOAT) ? a.floatVal : (double)a.intVal;
                    double bv = (b.type == ValueType::FLOAT) ? b.floatVal : (double)b.intVal;
                    push(Value(av * bv));
                } else {
                    push(Value(a.intVal * b.intVal));
                }
                break;
            }
            case OP_DIVIDE: {
                Value b = pop();
                Value a = pop();
                double bv = (b.type == ValueType::FLOAT) ? b.floatVal : (double)b.intVal;
                if (bv == 0) return INTERPRET_RUNTIME_ERROR;
                if (a.type == ValueType::FLOAT || b.type == ValueType::FLOAT) {
                    double av = (a.type == ValueType::FLOAT) ? a.floatVal : (double)a.intVal;
                    push(Value(av / bv));
                } else {
                    push(Value(a.intVal / (int)bv));
                }
                break;
            }
            case OP_NOT: {
                Value val = pop();
                bool isTrue = true;
                if (val.type == ValueType::BOOLEAN && !val.boolVal) isTrue = false;
                else if (val.type == ValueType::INTEGER && val.intVal == 0) isTrue = false;
                else if (val.type == ValueType::NIL) isTrue = false;
                push(Value(!isTrue));
                break;
            }
            case OP_NEGATE: {
                Value val = pop();
                if (val.type == ValueType::FLOAT) push(Value(-val.floatVal));
                else push(Value(-val.intVal));
                break;
            }
            case OP_PRINT: {
                std::cout << pop().toString() << "\n";
                break;
            }
            case OP_DEFINE_GLOBAL: {
                uint8_t index = readByte();
                if (index >= globals.size()) globals.resize(index + 1, Value(ValueType::UNDEFINED));
                globals[index] = pop();
                break;
            }
            case OP_GET_GLOBAL: {
                uint8_t index = readByte();
                if (index >= globals.size() || globals[index].type == ValueType::UNDEFINED) {
                    return INTERPRET_RUNTIME_ERROR;
                }
                push(globals[index]);
                break;
            }
            case OP_SET_GLOBAL: {
                uint8_t index = readByte();
                if (index >= globals.size() || globals[index].type == ValueType::UNDEFINED) {
                    return INTERPRET_RUNTIME_ERROR;
                }
                globals[index] = stack.back(); 
                break;
            }
            case OP_JUMP: {
                uint16_t offset = (uint16_t)(readByte() << 8);
                offset |= readByte();
                ip += offset;
                break;
            }
            case OP_JUMP_IF_FALSE: {
                uint16_t offset = (uint16_t)(readByte() << 8);
                offset |= readByte();
                Value val = stack.back();
                bool isTrue = true;
                if (val.type == ValueType::BOOLEAN && !val.boolVal) isTrue = false;
                else if (val.type == ValueType::INTEGER && val.intVal == 0) isTrue = false;
                else if (val.type == ValueType::NIL) isTrue = false;
                
                if (!isTrue) ip += offset;
                break;
            }
            case OP_LOOP: {
                uint16_t offset = (uint16_t)(readByte() << 8);
                offset |= readByte();
                ip -= offset;
                break;
            }
            case OP_RETURN: {
                return INTERPRET_OK;
            }
        }
    }
#endif
}

void VM::push(Value value) {
    stack.push_back(value);
}

Value VM::pop() {
    Value val = stack.back();
    stack.pop_back();
    return val;
}

uint8_t VM::readByte() {
    return *ip++;
}

Value VM::readConstant() {
    return chunk->constants[readByte()];
}

std::string VM::readString() {
    return readConstant().getString();
}
