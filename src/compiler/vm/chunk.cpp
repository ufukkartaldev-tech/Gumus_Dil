#include "chunk.h"
#include <iostream>

// 📦 Chunk Implementation - Bytecode container with optimizations

Chunk::Chunk() {
    // Reserve initial capacity for better performance
    code.reserve(256);
    lines.reserve(256);
    constants.reserve(64);
}

Chunk::~Chunk() {
    // Cleanup handled by vectors automatically
}

void Chunk::write(uint8_t byte, int line) {
    code.push_back(byte);
    lines.push_back(line);
}

void Chunk::writeConstant(Value value, int line) {
    int index = addConstant(value);
    if (index < 256) {
        write(OP_CONSTANT, line);
        write((uint8_t)index, line);
    } else {
        // Handle large constant pools
        write(OP_CONSTANT_LONG, line);
        write((uint8_t)(index & 0xFF), line);
        write((uint8_t)((index >> 8) & 0xFF), line);
        write((uint8_t)((index >> 16) & 0xFF), line);
    }
}

int Chunk::addConstant(Value value) {
    // Check for duplicate constants to save memory
    for (size_t i = 0; i < constants.size(); i++) {
        if (constants[i].equals(value)) {
            return (int)i;
        }
    }
    
    constants.push_back(value);
    return constants.size() - 1;
}

void Chunk::disassemble(const std::string& name) const {
    std::cout << "== " << name << " ==\n";
    
    for (size_t offset = 0; offset < code.size();) {
        offset = disassembleInstruction(offset);
    }
}

size_t Chunk::disassembleInstruction(size_t offset) const {
    std::cout << std::setfill('0') << std::setw(4) << offset << " ";
    
    if (offset > 0 && lines[offset] == lines[offset - 1]) {
        std::cout << "   | ";
    } else {
        std::cout << std::setw(4) << lines[offset] << " ";
    }
    
    uint8_t instruction = code[offset];
    switch (instruction) {
        case OP_CONSTANT:
            return constantInstruction("OP_CONSTANT", offset);
        case OP_CONSTANT_LONG:
            return constantLongInstruction("OP_CONSTANT_LONG", offset);
        case OP_NIL:
            return simpleInstruction("OP_NIL", offset);
        case OP_TRUE:
            return simpleInstruction("OP_TRUE", offset);
        case OP_FALSE:
            return simpleInstruction("OP_FALSE", offset);
        case OP_POP:
            return simpleInstruction("OP_POP", offset);
        case OP_GET_LOCAL:
            return byteInstruction("OP_GET_LOCAL", offset);
        case OP_SET_LOCAL:
            return byteInstruction("OP_SET_LOCAL", offset);
        case OP_GET_GLOBAL:
            return constantInstruction("OP_GET_GLOBAL", offset);
        case OP_DEFINE_GLOBAL:
            return constantInstruction("OP_DEFINE_GLOBAL", offset);
        case OP_SET_GLOBAL:
            return constantInstruction("OP_SET_GLOBAL", offset);
        case OP_EQUAL:
            return simpleInstruction("OP_EQUAL", offset);
        case OP_GREATER:
            return simpleInstruction("OP_GREATER", offset);
        case OP_LESS:
            return simpleInstruction("OP_LESS", offset);
        case OP_ADD:
            return simpleInstruction("OP_ADD", offset);
        case OP_SUBTRACT:
            return simpleInstruction("OP_SUBTRACT", offset);
        case OP_MULTIPLY:
            return simpleInstruction("OP_MULTIPLY", offset);
        case OP_DIVIDE:
            return simpleInstruction("OP_DIVIDE", offset);
        case OP_NOT:
            return simpleInstruction("OP_NOT", offset);
        case OP_NEGATE:
            return simpleInstruction("OP_NEGATE", offset);
        case OP_PRINT:
            return simpleInstruction("OP_PRINT", offset);
        case OP_JUMP:
            return jumpInstruction("OP_JUMP", 1, offset);
        case OP_JUMP_IF_FALSE:
            return jumpInstruction("OP_JUMP_IF_FALSE", 1, offset);
        case OP_LOOP:
            return jumpInstruction("OP_LOOP", -1, offset);
        case OP_CALL:
            return byteInstruction("OP_CALL", offset);
        case OP_RETURN:
            return simpleInstruction("OP_RETURN", offset);
        default:
            std::cout << "Unknown opcode " << (int)instruction << "\n";
            return offset + 1;
    }
}

size_t Chunk::simpleInstruction(const std::string& name, size_t offset) const {
    std::cout << name << "\n";
    return offset + 1;
}

size_t Chunk::constantInstruction(const std::string& name, size_t offset) const {
    uint8_t constant = code[offset + 1];
    std::cout << name << " " << (int)constant << " '";
    if (constant < constants.size()) {
        std::cout << constants[constant].toString();
    }
    std::cout << "'\n";
    return offset + 2;
}

size_t Chunk::constantLongInstruction(const std::string& name, size_t offset) const {
    uint32_t constant = code[offset + 1] |
                       (code[offset + 2] << 8) |
                       (code[offset + 3] << 16);
    std::cout << name << " " << constant << " '";
    if (constant < constants.size()) {
        std::cout << constants[constant].toString();
    }
    std::cout << "'\n";
    return offset + 4;
}

size_t Chunk::byteInstruction(const std::string& name, size_t offset) const {
    uint8_t slot = code[offset + 1];
    std::cout << name << " " << (int)slot << "\n";
    return offset + 2;
}

size_t Chunk::jumpInstruction(const std::string& name, int sign, size_t offset) const {
    uint16_t jump = (uint16_t)(code[offset + 1] << 8);
    jump |= code[offset + 2];
    std::cout << name << " " << offset << " -> " << (offset + 3 + sign * jump) << "\n";
    return offset + 3;
}

// 🎯 Memory optimization methods
void Chunk::optimize() {
    // Remove redundant instructions
    removeRedundantInstructions();
    
    // Optimize constant pool
    optimizeConstants();
    
    // Compact memory
    shrinkToFit();
}

void Chunk::removeRedundantInstructions() {
    std::vector<uint8_t> newCode;
    std::vector<int> newLines;
    
    for (size_t i = 0; i < code.size(); i++) {
        uint8_t current = code[i];
        
        // Skip redundant POP followed by another POP
        if (current == OP_POP && i + 1 < code.size() && code[i + 1] == OP_POP) {
            continue;
        }
        
        // Skip NOP instructions
        if (current == OP_NOP) {
            continue;
        }
        
        newCode.push_back(current);
        newLines.push_back(lines[i]);
    }
    
    code = std::move(newCode);
    lines = std::move(newLines);
}

void Chunk::optimizeConstants() {
    // Remove unused constants and update references
    std::vector<bool> used(constants.size(), false);
    std::vector<int> mapping(constants.size());
    
    // Mark used constants
    for (size_t i = 0; i < code.size(); i++) {
        if (code[i] == OP_CONSTANT && i + 1 < code.size()) {
            used[code[i + 1]] = true;
        }
    }
    
    // Create new constant pool
    std::vector<Value> newConstants;
    for (size_t i = 0; i < constants.size(); i++) {
        if (used[i]) {
            mapping[i] = newConstants.size();
            newConstants.push_back(constants[i]);
        }
    }
    
    // Update references
    for (size_t i = 0; i < code.size(); i++) {
        if (code[i] == OP_CONSTANT && i + 1 < code.size()) {
            code[i + 1] = mapping[code[i + 1]];
        }
    }
    
    constants = std::move(newConstants);
}

void Chunk::shrinkToFit() {
    code.shrink_to_fit();
    lines.shrink_to_fit();
    constants.shrink_to_fit();
}

size_t Chunk::getMemoryUsage() const {
    return code.capacity() * sizeof(uint8_t) +
           lines.capacity() * sizeof(int) +
           constants.capacity() * sizeof(Value);
}