#ifndef GUMUS_PARSER_ARENA_H
#define GUMUS_PARSER_ARENA_H

#include <vector>
#include <cstdint>
#include <cstdlib>
#include <new>

class MemoryArena {
public:
    MemoryArena(size_t blockSize = 1024 * 1024) : blockSize(blockSize) {
        currentBlock = nullptr;
        currentOffset = 0;
        currentCapacity = 0;
    }

    ~MemoryArena() {
        for (void* block : blocks) {
            std::free(block);
        }
    }

    template <typename T, typename... Args>
    T* alloc(Args&&... args) {
        void* ptr = allocate(sizeof(T));
        return new (ptr) T(std::forward<Args>(args)...);
    }

    void clear() {
        // Note: This doesn't call destructors! 
        // AST nodes in this project don't seem to have complex destructors 
        // (mostly just unique_ptrs which we are removing).
        // If we needed destructors, we'd need a different approach (e.g. tracking objects).
        for (void* block : blocks) {
            std::free(block);
        }
        blocks.clear();
        currentBlock = nullptr;
        currentOffset = 0;
        currentCapacity = 0;
    }

private:
    void* allocate(size_t size) {
        // Aligned allocation (8 bytes)
        size = (size + 7) & ~7;

        if (currentOffset + size > currentCapacity) {
            size_t nextSize = size > blockSize ? size : blockSize;
            currentBlock = std::malloc(nextSize);
            blocks.push_back(currentBlock);
            currentOffset = 0;
            currentCapacity = nextSize;
        }

        void* ptr = static_cast<char*>(currentBlock) + currentOffset;
        currentOffset += size;
        return ptr;
    }

    std::vector<void*> blocks;
    void* currentBlock;
    size_t currentOffset;
    size_t currentCapacity;
    size_t blockSize;
};

#endif // GUMUS_PARSER_ARENA_H
