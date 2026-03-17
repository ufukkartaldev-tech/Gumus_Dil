#ifndef CHUNK_H
#define CHUNK_H

#include <vector>
#include <cstdint>
#include <string>
#include <iomanip>
#include "../interpreter/value.h"
#include "op_code.h"

class Chunk {
public:
    std::vector<uint8_t> code;
    std::vector<int> lines;
    std::vector<Value> constants;

    Chunk();
    ~Chunk();

    // 📝 Basic operations
    void write(uint8_t byte, int line);
    void writeConstant(Value value, int line);
    int addConstant(Value value);

    // 🔍 Debug and disassembly
    void disassemble(const std::string& name) const;
    size_t disassembleInstruction(size_t offset) const;

    // 🎯 Memory optimization
    void optimize();
    void shrinkToFit();
    size_t getMemoryUsage() const;

private:
    // 🔧 Disassembly helpers
    size_t simpleInstruction(const std::string& name, size_t offset) const;
    size_t constantInstruction(const std::string& name, size_t offset) const;
    size_t constantLongInstruction(const std::string& name, size_t offset) const;
    size_t byteInstruction(const std::string& name, size_t offset) const;
    size_t jumpInstruction(const std::string& name, int sign, size_t offset) const;

    // 🎯 Optimization helpers
    void removeRedundantInstructions();
    void optimizeConstants();
};

#endif // CHUNK_H
