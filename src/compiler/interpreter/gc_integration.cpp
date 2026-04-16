#include "interpreter.h"
#include "garbage_collector.h"

// ============================================================
// Tek GC Rejimi: Yalnizca Interpreter::garbageCollector kullanilir.
// g_gc global KALDIRILDI. Tum allocateObject cagrilari
// interpreter.garbageCollector->allocateObject<T>() uzerinden yapilir.
// ============================================================

void Interpreter::initializeGC() {
    if (!garbageCollector) {
        garbageCollector = std::make_unique<GarbageCollector>(globals);
        if (gumus_debug) {
            std::cout << "🗑️ Garbage Collector baslatildi (tek rejim)\n";
        }
    }
}

void Interpreter::collectGarbage() {
    if (!garbageCollector) return;

    // Call-stack uzerindeki aktif environment'lari kok olarak isle
    // environment gunceli (gecerli scope), globals her zaman kok
    garbageCollector->markEnvironment(environment);
    garbageCollector->markEnvironment(globals);

    garbageCollector->collect();
}

size_t Interpreter::getGCObjectCount() const {
    if (garbageCollector) return garbageCollector->getObjectCount();
    return 0;
}

size_t Interpreter::getGCBytesAllocated() const {
    if (garbageCollector) return garbageCollector->getBytesAllocated();
    return 0;
}
