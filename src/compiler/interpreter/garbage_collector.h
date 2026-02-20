#ifndef GARBAGE_COLLECTOR_H
#define GARBAGE_COLLECTOR_H

#include "value.h"
#include "interpreter.h"
#include <vector>
#include <unordered_set>
#include <memory>
#include <chrono>

class GarbageCollector {
private:
    std::vector<std::shared_ptr<Value>> heap;
    std::unordered_set<std::shared_ptr<Value>> roots;
    std::shared_ptr<Environment> globalEnvironment;
    
    // Statistics
    size_t totalCollections = 0;
    std::chrono::milliseconds totalGCTime{0};
    size_t memoryFreed = 0;
    size_t objectsCollected = 0;
    size_t circularReferencesDetected = 0;
    std::chrono::milliseconds maxGCPause{0};
    std::chrono::milliseconds minGCPause{999999};
    
public:
    GarbageCollector(std::shared_ptr<Environment> globals) 
        : globalEnvironment(globals) {}
    
    // 🗑️ Core GC Operations
    void mark(std::shared_ptr<Value> obj);
    void sweep();
    void collect();
    
    // 📊 Memory Management
    void addToHeap(std::shared_ptr<Value> obj);
    void addRoot(std::shared_ptr<Value> obj);
    void removeRoot(std::shared_ptr<Value> obj);
    
    // 🔍 Analytics
    size_t getHeapSize() const { return heap.size(); }
    size_t getRootCount() const { return roots.size(); }
    size_t getTotalCollections() const { return totalCollections; }
    double getAverageGCTime() const;
    size_t getMemoryFreed() const { return memoryFreed; }
    size_t getObjectsCollected() const { return objectsCollected; }
    size_t getCircularReferencesDetected() const { return circularReferencesDetected; }
    double getMaxGCPause() const { return maxGCPause.count(); }
    double getMinGCPause() const { return minGCPause.count(); }
    
    // 📈 Memory Statistics
    struct MemoryStats {
        size_t heapSize;
        size_t rootCount;
        size_t totalCollections;
        double averageGCTime;
        size_t memoryFreed;
        size_t objectsCollected;
        std::map<ValueType, size_t> typeDistribution;
    };
    
    MemoryStats getMemoryStats() const;
    std::string generateReport() const;
    
    // 🎯 Debug Support
    void dumpHeap() const;
    void detectLeaks();
    void validateHeap() const;
    void detectCircularReferences();
    
private:
    // 🔧 Internal Methods
    void markRoots();
    void markEnvironment(std::shared_ptr<Environment> env);
    void markValue(std::shared_ptr<Value> value);
    bool isMarked(std::shared_ptr<Value> obj) const;
    void setMarked(std::shared_ptr<Value> obj, bool marked);
    
    // 📊 Type-specific marking
    void markList(std::shared_ptr<ValueList> list);
    void markMap(std::shared_ptr<std::map<std::string, Value>> map);
    void markObject(std::shared_ptr<void> obj, ValueType type);
};

// Global GC instance
extern std::unique_ptr<GarbageCollector> g_gc;

// GC Macros
#define GC_ADD_ROOT(obj) if (g_gc) g_gc->addRoot(obj)
#define GC_REMOVE_ROOT(obj) if (g_gc) g_gc->removeRoot(obj)
#define GC_COLLECT() if (g_gc) g_gc->collect()
#define GC_STATS() (g_gc ? g_gc->getMemoryStats() : GarbageCollector::MemoryStats{})

#endif // GARBAGE_COLLECTOR_H
