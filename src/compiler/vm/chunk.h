#ifndef CHUNK_H
#define CHUNK_H

#include <vector>
#include <cstdint>
#include "../interpreter/value.h"

class Chunk {
public:
    std::vector<uint8_t> code;
    std::vector<int> lines;
    std::vector<Value> constants;

    void write(uint8_t byte, int line) {
        code.push_back(byte);
        lines.push_back(line);
    }

    int addConstant(Value value) {
        constants.push_back(value);
        return constants.size() - 1;
    }
};

#endif // CHUNK_H
