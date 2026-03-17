#include "op_code.h"

// 🔧 OpCode utility functions implementation

const char* getOpCodeName(OpCode opcode) {
    switch (opcode) {
        // Constants and literals
        case OP_CONSTANT: return "OP_CONSTANT";
        case OP_NIL: return "OP_NIL";
        case OP_TRUE: return "OP_TRUE";
        case OP_FALSE: return "OP_FALSE";
        
        // Stack operations
        case OP_POP: return "OP_POP";
        case OP_DUP: return "OP_DUP";
        case OP_SWAP: return "OP_SWAP";
        
        // Variable operations
        case OP_GET_LOCAL: return "OP_GET_LOCAL";
        case OP_SET_LOCAL: return "OP_SET_LOCAL";
        case OP_GET_GLOBAL: return "OP_GET_GLOBAL";
        case OP_DEFINE_GLOBAL: return "OP_DEFINE_GLOBAL";
        case OP_SET_GLOBAL: return "OP_SET_GLOBAL";
        case OP_GET_UPVALUE: return "OP_GET_UPVALUE";
        case OP_SET_UPVALUE: return "OP_SET_UPVALUE";
        
        // Property operations
        case OP_GET_PROPERTY: return "OP_GET_PROPERTY";
        case OP_SET_PROPERTY: return "OP_SET_PROPERTY";
        case OP_GET_SUPER: return "OP_GET_SUPER";
        
        // Comparison operations
        case OP_EQUAL: return "OP_EQUAL";
        case OP_NOT_EQUAL: return "OP_NOT_EQUAL";
        case OP_GREATER: return "OP_GREATER";
        case OP_GREATER_EQUAL: return "OP_GREATER_EQUAL";
        case OP_LESS: return "OP_LESS";
        case OP_LESS_EQUAL: return "OP_LESS_EQUAL";
        
        // Arithmetic operations
        case OP_ADD: return "OP_ADD";
        case OP_SUBTRACT: return "OP_SUBTRACT";
        case OP_MULTIPLY: return "OP_MULTIPLY";
        case OP_DIVIDE: return "OP_DIVIDE";
        case OP_MODULO: return "OP_MODULO";
        case OP_NEGATE: return "OP_NEGATE";
        
        // Logical operations
        case OP_AND: return "OP_AND";
        case OP_OR: return "OP_OR";
        case OP_NOT: return "OP_NOT";
        
        // I/O operations
        case OP_PRINT: return "OP_PRINT";
        case OP_READ: return "OP_READ";
        
        // Control flow
        case OP_JUMP: return "OP_JUMP";
        case OP_JUMP_IF_FALSE: return "OP_JUMP_IF_FALSE";
        case OP_JUMP_IF_TRUE: return "OP_JUMP_IF_TRUE";
        case OP_LOOP: return "OP_LOOP";
        
        // Function operations
        case OP_CALL: return "OP_CALL";
        case OP_INVOKE: return "OP_INVOKE";
        case OP_SUPER_INVOKE: return "OP_SUPER_INVOKE";
        case OP_CLOSURE: return "OP_CLOSURE";
        case OP_CLOSE_UPVALUE: return "OP_CLOSE_UPVALUE";
        case OP_RETURN: return "OP_RETURN";
        case OP_DEFINE_FUNCTION: return "OP_DEFINE_FUNCTION";
        
        // Object-oriented operations
        case OP_CLASS: return "OP_CLASS";
        case OP_INHERIT: return "OP_INHERIT";
        case OP_METHOD: return "OP_METHOD";
        
        // Array operations
        case OP_ARRAY_NEW: return "OP_ARRAY_NEW";
        case OP_ARRAY_GET: return "OP_ARRAY_GET";
        case OP_ARRAY_SET: return "OP_ARRAY_SET";
        case OP_ARRAY_LENGTH: return "OP_ARRAY_LENGTH";
        
        // String operations
        case OP_STRING_CONCAT: return "OP_STRING_CONCAT";
        case OP_STRING_LENGTH: return "OP_STRING_LENGTH";
        case OP_STRING_SUBSTR: return "OP_STRING_SUBSTR";
        
        // Type operations
        case OP_TYPEOF: return "OP_TYPEOF";
        case OP_CAST: return "OP_CAST";
        
        // Debug operations
        case OP_DEBUG_LINE: return "OP_DEBUG_LINE";
        case OP_DEBUG_VAR: return "OP_DEBUG_VAR";
        
        // Special operations
        case OP_NOP: return "OP_NOP";
        case OP_HALT: return "OP_HALT";
        
        default: return "UNKNOWN_OPCODE";
    }
}

int getOpCodeOperandCount(OpCode opcode) {
    switch (opcode) {
        // No operands
        case OP_NIL:
        case OP_TRUE:
        case OP_FALSE:
        case OP_POP:
        case OP_DUP:
        case OP_SWAP:
        case OP_ADD:
        case OP_SUBTRACT:
        case OP_MULTIPLY:
        case OP_DIVIDE:
        case OP_MODULO:
        case OP_NEGATE:
        case OP_AND:
        case OP_OR:
        case OP_NOT:
        case OP_EQUAL:
        case OP_NOT_EQUAL:
        case OP_GREATER:
        case OP_GREATER_EQUAL:
        case OP_LESS:
        case OP_LESS_EQUAL:
        case OP_PRINT:
        case OP_READ:
        case OP_RETURN:
        case OP_CLOSE_UPVALUE:
        case OP_ARRAY_NEW:
        case OP_ARRAY_GET:
        case OP_ARRAY_SET:
        case OP_ARRAY_LENGTH:
        case OP_STRING_CONCAT:
        case OP_STRING_LENGTH:
        case OP_TYPEOF:
        case OP_CAST:
        case OP_NOP:
        case OP_HALT:
            return 0;
            
        // One operand
        case OP_CONSTANT:
        case OP_GET_LOCAL:
        case OP_SET_LOCAL:
        case OP_GET_GLOBAL:
        case OP_DEFINE_GLOBAL:
        case OP_SET_GLOBAL:
        case OP_GET_UPVALUE:
        case OP_SET_UPVALUE:
        case OP_GET_PROPERTY:
        case OP_SET_PROPERTY:
        case OP_GET_SUPER:
        case OP_JUMP:
        case OP_JUMP_IF_FALSE:
        case OP_JUMP_IF_TRUE:
        case OP_LOOP:
        case OP_INVOKE:
        case OP_SUPER_INVOKE:
        case OP_CLOSURE:
        case OP_CLASS:
        case OP_INHERIT:
        case OP_METHOD:
        case OP_DEFINE_FUNCTION:
        case OP_DEBUG_LINE:
        case OP_DEBUG_VAR:
            return 1;
            
        // Two operands
        case OP_CALL:
        case OP_STRING_SUBSTR:
            return 2;
            
        // Three operands
        // (none currently)
            
        default:
            return 0;
    }
}

bool isJumpInstruction(OpCode opcode) {
    return opcode == OP_JUMP || 
           opcode == OP_JUMP_IF_FALSE || 
           opcode == OP_JUMP_IF_TRUE || 
           opcode == OP_LOOP;
}

bool hasConstantOperand(OpCode opcode) {
    return opcode == OP_CONSTANT ||
           opcode == OP_GET_GLOBAL ||
           opcode == OP_DEFINE_GLOBAL ||
           opcode == OP_SET_GLOBAL ||
           opcode == OP_GET_PROPERTY ||
           opcode == OP_SET_PROPERTY ||
           opcode == OP_CALL ||
           opcode == OP_INVOKE ||
           opcode == OP_CLASS ||
           opcode == OP_METHOD ||
           opcode == OP_DEFINE_FUNCTION;
}