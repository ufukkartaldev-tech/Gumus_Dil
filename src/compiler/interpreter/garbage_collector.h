#ifndef GARBAGE_COLLECTOR_H
#define GARBAGE_COLLECTOR_H

#include "value.h"
#include <vector>
#include <chrono>
#include <iostream>

class Environment;

class GarbageCollector {
private:
    GumusObject* firstObject = nullptr;

    size_t bytesAllocated = 0;
    size_t bytesFreed     = 0;
    size_t nextGC         = 1024 * 1024; // 1 MB ilk esik

    // Explicit C++ taraflı kökler
    std::vector<Value*> roots;

    // Global ortam (daima kök)
    std::shared_ptr<Environment> globalEnvironment;

    // İç mark yardımcıları
    void markEnvironmentChain(Environment* env);

public:
    GarbageCollector(std::shared_ptr<Environment> globals)
        : globalEnvironment(globals) {}

    ~GarbageCollector();

    // Ham nesne tahsisi - tipli şablon, GC zincirine ekler
    template <typename T, typename... Args>
    T* allocateObject(Args&&... args) {
        size_t size = sizeof(T);
        bytesAllocated += size;

        if (bytesAllocated - bytesFreed > nextGC) {
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

    // Call-stack ortamlarını kök olarak işaretle
    void markEnvironment(std::shared_ptr<Environment> env);

    // Explicit kökler (C++ tarafından tutulanan Value*)
    void addRoot(Value* value) { roots.push_back(value); }
    void removeRoot(Value* value) {
        for (auto it = roots.begin(); it != roots.end(); ++it) {
            if (*it == value) { roots.erase(it); break; }
        }
    }

    // İstatistikler
    size_t getBytesAllocated() const { return bytesAllocated; }
    size_t getObjectCount() const {
        size_t count = 0;
        GumusObject* obj = firstObject;
        while (obj) { ++count; obj = obj->next; }
        return count;
    }
};

// GarbageCollector global pointer'ı KALDIRILDI.
// Tek kaynak: Interpreter::garbageCollector
// Tum allocateObject cagrilari interpreter.gc() uzerinden yapilacak.

#endif // GARBAGE_COLLECTOR_H
