#ifndef VM_H
#define VM_H

#include <vector>
#include <map>
#include <string>
#include "chunk.h"
#include "op_code.h"
#include "../interpreter/value.h"

enum InterpretResult {
    INTERPRET_OK,
    INTERPRET_COMPILE_ERROR,
    INTERPRET_RUNTIME_ERROR
};

class VM {
public:
    VM();
    ~VM();

    InterpretResult run(Chunk* chunk);

private:
    Chunk* chunk;
    uint8_t* ip;
    std::vector<Value> stack;
    std::vector<Value> globals;

    void push(Value value);
    Value pop();
    uint8_t readByte();
    Value readConstant();
    std::string readString();
};

#endif // VM_H
