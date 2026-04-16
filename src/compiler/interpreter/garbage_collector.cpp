#include "garbage_collector.h"
#include "interpreter.h"
#include <iostream>

// g_gc KALDIRILDI. Tek GC rejimi: Interpreter::garbageCollector

GarbageCollector::~GarbageCollector() {
    GumusObject* object = firstObject;
    while (object != nullptr) {
        GumusObject* next = object->next;
        delete object;
        object = next;
    }
}

void GarbageCollector::markValue(Value value) {
    if (!IS_OBJ(value)) return;   // IS_OBJ artik BOOLEAN/NIL icin false
    markObject(AS_OBJ(value));
}

void GarbageCollector::markObject(GumusObject* obj) {
    if (obj == nullptr) return;
    if (obj->isMarked) return;    // Zaten islendi, donguye girme
    obj->isMarked = true;
    obj->mark(this);              // Polimorfik: alt siniflar kendi alanlarini isaretler
}

// Environment zincirini (enclosing'e kadar) kök olarak tarar
void GarbageCollector::markEnvironment(std::shared_ptr<Environment> env) {
    Environment* current = env.get();
    while (current != nullptr) {
        // map tabanli degerler
        for (auto& pair : current->values) {
            markValue(pair.second);
        }
        // slot tabanli degerler
        for (auto& val : current->valuesArray) {
            markValue(val);
        }
        auto parent = current->enclosing.lock();
        current = parent.get();
    }
}

void GarbageCollector::markEnvironmentChain(Environment* env) {
    while (env != nullptr) {
        for (auto& pair : env->values)     markValue(pair.second);
        for (auto& val  : env->valuesArray) markValue(val);
        auto parent = env->enclosing.lock();
        env = parent.get();
    }
}

void GarbageCollector::collect() {
    // --- MARK fazı ---

    // 1. Global environment
    if (globalEnvironment) {
        markEnvironmentChain(globalEnvironment.get());
    }

    // 2. Explicit C++ kökleri
    for (Value* value : roots) {
        markValue(*value);
    }

    // NOT: Interpreter, call() sırasında aktif Environment'ları
    // addRoot veya markEnvironment(activeEnv) ile bildirmeli.
    // Bu çağrı Interpreter::collectGarbage() içinden yapılıyor.

    // --- SWEEP fazı ---
    sweep();
}

void GarbageCollector::sweep() {
    size_t freed = 0;
    GumusObject** object = &firstObject;
    while (*object != nullptr) {
        if (!(*object)->isMarked) {
            GumusObject* unreached = *object;
            *object = unreached->next;
            freed += sizeof(*unreached);   // Tahmini boyut
            delete unreached;
        } else {
            (*object)->isMarked = false;   // Bir sonraki GC icin sifirla
            object = &(*object)->next;
        }
    }
    bytesFreed += freed;
    // Bir sonraki GC esigini dinamik olarak ayarla (2× mevcut canli heap)
    size_t live = bytesAllocated - bytesFreed;
    nextGC = (live > 0) ? live * 2 : 1024 * 1024;
}

// -----------------------------------------------------------------
// GumusList ve GumusMap mark() implementasyonlari
// Artik g_gc yerine parametre olarak gelen gc* kullanilir
// -----------------------------------------------------------------

void GumusList::mark(GarbageCollector* gc) {
    for (auto& el : elements) {
        gc->markValue(el);
    }
}

void GumusMap::mark(GarbageCollector* gc) {
    for (auto& pair : items) {
        gc->markValue(pair.second);
    }
}
