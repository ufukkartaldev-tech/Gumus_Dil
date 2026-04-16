#include "garbage_collector.h"
#include "interpreter.h"
#include <iostream>

// Global GC instance
std::unique_ptr<GarbageCollector> g_gc;

GarbageCollector::~GarbageCollector() {
    GumusObject* object = firstObject;
    while (object != nullptr) {
        GumusObject* next = object->next;
        delete object;
        object = next;
    }
}

void GarbageCollector::markValue(Value value) {
    if (!IS_OBJ(value)) return;
    markObject(AS_OBJ(value));
}

void GarbageCollector::markObject(GumusObject* obj) {
    if (obj == nullptr) return;
    if (obj->isMarked) return;
    
    obj->isMarked = true;
    obj->mark();
}

void GarbageCollector::collect() {
    // 1. Mark Roots
    for (Value* value : roots) {
        markValue(*value);
    }
    
    // Global environment values
    if (globalEnvironment) {
       for(auto& pair : globalEnvironment->values) {
           markValue(pair.second);
       }
    }
    // In a complete implementation, the interpreter's call stack environments 
    // must also be traced here.
    
    sweep();
}

void GarbageCollector::sweep() {
    GumusObject** object = &firstObject;
    while (*object != nullptr) {
        if (!(*object)->isMarked) {
            GumusObject* unreached = *object;
            *object = unreached->next;
            delete unreached;
        } else {
            (*object)->isMarked = false;
            object = &(*object)->next;
        }
    }
    
    bytesAllocated = 0; // Simplistic approach: reset counter so we wait another 1MB.
}

// ---------------------------------------------------------
// Objektif mark() Gerçekleştirmeleri
// ---------------------------------------------------------

void GumusList::mark() {
    for (auto& el : elements) {
        if (g_gc) g_gc->markValue(el);
    }
}

void GumusMap::mark() {
    for (auto& pair : items) {
        if (g_gc) g_gc->markValue(pair.second);
    }
}
