#ifndef MEMORY_POOL_H
#define MEMORY_POOL_H

#include <vector>
#include <memory>
#include <cstddef>
#include <mutex>

// 🏊 Memory Pool for efficient allocation
template<typename T, size_t BlockSize = 4096>
class MemoryPool {
private:
    struct Block {
        alignas(T) char data[BlockSize];
        size_t used = 0;
        Block* next = nullptr;
    };
    
    Block* currentBlock = nullptr;
    std::vector<std::unique_ptr<Block>> blocks;
    std::mutex poolMutex;
    
    // 📊 Statistics
    size_t totalAllocated = 0;
    size_t totalFreed = 0;
    size_t peakUsage = 0;
    
public:
    MemoryPool() {
        allocateNewBlock();
    }
    
    ~MemoryPool() {
        clear();
    }
    
    // 🎯 Allocation methods
    T* allocate() {
        std::lock_guard<std::mutex> lock(poolMutex);
        
        if (!currentBlock || currentBlock->used + sizeof(T) > BlockSize) {
            allocateNewBlock();
        }
        
        T* ptr = reinterpret_cast<T*>(currentBlock->data + currentBlock->used);
        currentBlock->used += sizeof(T);
        totalAllocated += sizeof(T);
        
        size_t currentUsage = getCurrentUsage();
        if (currentUsage > peakUsage) {
            peakUsage = currentUsage;
        }
        
        return ptr;
    }
    
    void deallocate(T* ptr) {
        // In a pool allocator, we don't actually free individual objects
        // Memory is reclaimed when the entire pool is reset
        totalFreed += sizeof(T);
    }
    
    // 🧹 Pool management
    void clear() {
        std::lock_guard<std::mutex> lock(poolMutex);
        blocks.clear();
        currentBlock = nullptr;
        totalAllocated = 0;
        totalFreed = 0;
    }
    
    void reset() {
        std::lock_guard<std::mutex> lock(poolMutex);
        for (auto& block : blocks) {
            block->used = 0;
        }
        if (!blocks.empty()) {
            currentBlock = blocks[0].get();
        }
    }
    
    // 📊 Statistics
    size_t getCurrentUsage() const {
        size_t usage = 0;
        for (const auto& block : blocks) {
            usage += block->used;
        }
        return usage;
    }
    
    size_t getTotalAllocated() const { return totalAllocated; }
    size_t getTotalFreed() const { return totalFreed; }
    size_t getPeakUsage() const { return peakUsage; }
    size_t getBlockCount() const { return blocks.size(); }
    
    double getFragmentation() const {
        if (totalAllocated == 0) return 0.0;
        return static_cast<double>(totalAllocated - totalFreed) / totalAllocated;
    }
    
private:
    void allocateNewBlock() {
        auto newBlock = std::make_unique<Block>();
        currentBlock = newBlock.get();
        blocks.push_back(std::move(newBlock));
    }
};

// 🎯 Specialized pools for different types
class ValuePool {
private:
    MemoryPool<Value> pool;
    
public:
    Value* allocateValue() {
        Value* ptr = pool.allocate();
        new(ptr) Value(); // Placement new
        return ptr;
    }
    
    void deallocateValue(Value* value) {
        if (value) {
            value->~Value(); // Explicit destructor call
            pool.deallocate(value);
        }
    }
    
    // Statistics
    size_t getCurrentUsage() const { return pool.getCurrentUsage(); }
    size_t getTotalAllocated() const { return pool.getTotalAllocated(); }
    size_t getPeakUsage() const { return pool.getPeakUsage(); }
    double getFragmentation() const { return pool.getFragmentation(); }
    
    void reset() { pool.reset(); }
    void clear() { pool.clear(); }
};

// 🌍 Global memory pools
extern ValuePool g_valuePool;
extern MemoryPool<std::string> g_stringPool;
extern MemoryPool<std::vector<Value>> g_listPool;

// 🎯 Memory management macros
#define ALLOCATE_VALUE() g_valuePool.allocateValue()
#define DEALLOCATE_VALUE(ptr) g_valuePool.deallocateValue(ptr)

#endif // MEMORY_POOL_H