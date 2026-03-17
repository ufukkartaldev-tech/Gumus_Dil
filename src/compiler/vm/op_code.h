#ifndef OP_CODE_H
#define OP_CODE_H

#include <cstdint>

enum OpCode : uint8_t {
    // Constants and literals
    OP_CONSTANT,
    OP_NIL,
    OP_TRUE,
    OP_FALSE,
    
    // Stack operations
    OP_POP,
    OP_DUP,
    OP_SWAP,
    
    // Variable operations
    OP_GET_LOCAL,
    OP_SET_LOCAL,
    OP_GET_GLOBAL,
    OP_DEFINE_GLOBAL,
    OP_SET_GLOBAL,
    OP_GET_UPVALUE,
    OP_SET_UPVALUE,
    
    // Property operations
    OP_GET_PROPERTY,
    OP_SET_PROPERTY,
    OP_GET_SUPER,
    
    // Comparison operations
    OP_EQUAL,
    OP_NOT_EQUAL,
    OP_GREATER,
    OP_GREATER_EQUAL,
    OP_LESS,
    OP_LESS_EQUAL,
    
    // Arithmetic operations
    OP_ADD,
    OP_SUBTRACT,
    OP_MULTIPLY,
    OP_DIVIDE,
    OP_MODULO,
    OP_NEGATE,
    
    // Logical operations
    OP_AND,
    OP_OR,
    OP_NOT,
    
    // I/O operations
    OP_PRINT,
    OP_READ,
    
    // Control flow
    OP_JUMP,
    OP_JUMP_IF_FALSE,
    OP_JUMP_IF_TRUE,
    OP_LOOP,
    
    // Function operations
    OP_CALL,
    OP_INVOKE,
    OP_SUPER_INVOKE,
    OP_CLOSURE,
    OP_CLOSE_UPVALUE,
    OP_RETURN,
    OP_DEFINE_FUNCTION,
    
    // Object-oriented operations
    OP_CLASS,
    OP_INHERIT,
    OP_METHOD,
    
    // Array operations
    OP_ARRAY_NEW,
    OP_ARRAY_GET,
    OP_ARRAY_SET,
    OP_ARRAY_LENGTH,
    
    // String operations
    OP_STRING_CONCAT,
    OP_STRING_LENGTH,
    OP_STRING_SUBSTR,
    
    // Type operations
    OP_TYPEOF,
    OP_CAST,
    
    // Debug operations
    OP_DEBUG_LINE,
    OP_DEBUG_VAR,
    
    // Special operations
    OP_NOP,
    OP_HALT
};

// 🔧 OpCode utility functions
const char* getOpCodeName(OpCode opcode);
int getOpCodeOperandCount(OpCode opcode);
bool isJumpInstruction(OpCode opcode);
bool hasConstantOperand(OpCode opcode);

#endif // OP_CODE_H
