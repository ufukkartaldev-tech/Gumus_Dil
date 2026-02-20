#include "interpreter.h"
#include "garbage_collector.h"

// 🗑️ Garbage Collection Implementation
void Interpreter::initializeGC() {
    if (!garbageCollector) {
        garbageCollector = std::make_unique<GarbageCollector>(globals);
        g_gc = std::make_unique<GarbageCollector>(globals);
        
        if (gumus_debug) {
            std::cout << "🗑️ Garbage Collector initialized\n";
        }
    }
}

void Interpreter::collectGarbage() {
    if (garbageCollector) {
        garbageCollector->collect();
    }
}

GarbageCollector::MemoryStats Interpreter::getMemoryStats() const {
    if (garbageCollector) {
        return garbageCollector->getMemoryStats();
    }
    return GarbageCollector::MemoryStats{};
}

std::string Interpreter::generateMemoryReport() const {
    if (garbageCollector) {
        return garbageCollector->generateReport();
    }
    return "🗑️ Garbage Collector not initialized";
}
