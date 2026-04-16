#ifndef GARBAGE_COLLECTOR_H
#define GARBAGE_COLLECTOR_H

#include "value.h"
#include <vector>
#include <memory>
#include <chrono>
#include <iostream>

class Environment;

class GarbageCollector {
private:
    GumusObject* firstObject = nullptr;
    
    size_t bytesAllocated = 0;
    size_t nextGC = 1024 * 1024; // 1 MB limit for threshold
    
    // Explicit roots for C++ side objects
    std::vector<Value*> roots;
    
    // Global Env
    std::shared_ptr<Environment> globalEnvironment;
    
public:
    GarbageCollector(std::shared_ptr<Environment> globals) 
        : globalEnvironment(globals) {}
        
    ~GarbageCollector();
    
    // Raw Object Allocation
    template <typename T, typename... Args>
    T* allocateObject(Args&&... args) {
        size_t size = sizeof(T);
        bytesAllocated += size;
        
        if (bytesAllocated > nextGC) {
            collect();
        }
        
        T* object = new T(std::forward<Args>(args)...);
        object->next = firstObject;
        firstObject = object;
        
        return object;
    }

    void markValue(Value value);
    void markObject(GumusObject* obj);
    void sweep();
    void collect();
    
    void addRoot(Value* value) { roots.push_back(value); }
    void removeRoot(Value* value) {
        for (auto it = roots.begin(); it != roots.end(); ++it) {
            if (*it == value) {
                roots.erase(it);
                break;
            }
        }
    }
};

extern std::unique_ptr<GarbageCollector> g_gc;

#define GC_COLLECT() if (g_gc) g_gc->collect()

#endif // GARBAGE_COLLECTOR_H
