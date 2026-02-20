#include "garbage_collector.h"
#include "interpreter.h"
#include <iostream>
#include <algorithm>

// Global GC instance
std::unique_ptr<GarbageCollector> g_gc;

// 🗑️ Core GC Operations
void GarbageCollector::mark(std::shared_ptr<Value> obj) {
    if (!obj || isMarked(obj)) return;
    
    setMarked(obj, true);
    markValue(obj);
}

void GarbageCollector::sweep() {
    auto start = std::chrono::high_resolution_clock::now();
    
    size_t initialHeapSize = heap.size();
    heap.erase(
        std::remove_if(heap.begin(), heap.end(), 
            [this](std::shared_ptr<Value> obj) {
                if (!isMarked(obj)) {
                    // Object is unreachable - collect it
                    objectsCollected++;
                    memoryFreed += obj->getSize();
                    return true;
                }
                // Reset mark for next collection
                setMarked(obj, false);
                return false;
            }
        ),
        heap.end()
    );
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    totalCollections++;
    totalGCTime += duration;
    
    // Track min/max pause times (Stop-the-World metrics)
    if (duration > maxGCPause) maxGCPause = duration;
    if (duration < minGCPause) minGCPause = duration;
    
    if (gumus_debug) {
        std::cout << "🗑️ GC: Collected " << objectsCollected 
                  << " objects, freed " << memoryFreed 
                  << " bytes in " << duration.count() << "ms\n";
        std::cout << "   🔴 Stop-the-World pause: " << duration.count() << "ms\n";
    }
}

void GarbageCollector::collect() {
    if (gumus_debug) {
        std::cout << "🧹 Starting garbage collection...\n";
        std::cout << "   Heap size: " << heap.size() << " objects\n";
        std::cout << "   Root count: " << roots.size() << "\n";
    }
    
    // Mark phase
    markRoots();
    
    // Sweep phase
    sweep();
    
    if (gumus_debug) {
        std::cout << "✅ GC completed. Heap size: " << heap.size() << " objects\n";
    }
}

// 📊 Memory Management
void GarbageCollector::addToHeap(std::shared_ptr<Value> obj) {
    if (obj) {
        heap.push_back(obj);
    }
}

void GarbageCollector::addRoot(std::shared_ptr<Value> obj) {
    if (obj) {
        roots.insert(obj);
    }
}

void GarbageCollector::removeRoot(std::shared_ptr<Value> obj) {
    roots.erase(obj);
}

// 📈 Memory Statistics
GarbageCollector::MemoryStats GarbageCollector::getMemoryStats() const {
    MemoryStats stats;
    stats.heapSize = heap.size();
    stats.rootCount = roots.size();
    stats.totalCollections = totalCollections;
    stats.averageGCTime = getAverageGCTime();
    stats.memoryFreed = memoryFreed;
    stats.objectsCollected = objectsCollected;
    
    // Type distribution
    for (const auto& obj : heap) {
        stats.typeDistribution[obj->type]++;
    }
    
    return stats;
}

double GarbageCollector::getAverageGCTime() const {
    return totalCollections > 0 ? 
        static_cast<double>(totalGCTime.count()) / totalCollections : 0.0;
}

std::string GarbageCollector::generateReport() const {
    auto stats = getMemoryStats();
    std::string report = "📊 Memory Statistics:\n";
    report += "   Heap Size: " + std::to_string(stats.heapSize) + " objects\n";
    report += "   Root Count: " + std::to_string(stats.rootCount) + "\n";
    report += "   Total Collections: " + std::to_string(stats.totalCollections) + "\n";
    report += "   Average GC Time: " + std::to_string(stats.averageGCTime) + "ms\n";
    report += "   Memory Freed: " + std::to_string(stats.memoryFreed) + " bytes\n";
    report += "   Objects Collected: " + std::to_string(stats.objectsCollected) + "\n";
    
    report += "   Type Distribution:\n";
    for (const auto& pair : stats.typeDistribution) {
        report += "     " + valueTypeName(pair.first) + ": " + std::to_string(pair.second) + "\n";
    }
    
    return report;
}

// 🎯 Debug Support
void GarbageCollector::dumpHeap() const {
    std::cout << "🗑️ Heap Dump (" << heap.size() << " objects):\n";
    for (size_t i = 0; i < heap.size(); ++i) {
        const auto& obj = heap[i];
        std::cout << "   [" << i << "] " << valueTypeName(obj->type) 
                  << " (" << obj->toString() << ") "
                  << (isMarked(obj) ? "[MARKED]" : "[UNMARKED]") << "\n";
    }
}

void GarbageCollector::detectLeaks() {
    // Simple leak detection: objects that should be freed but aren't
    std::vector<std::shared_ptr<Value>> leaked;
    
    for (const auto& obj : heap) {
        if (obj->type == ValueType::STRING || 
            obj->type == ValueType::LIST || 
            obj->type == ValueType::MAP) {
            // These should be temporary objects
            leaked.push_back(obj);
        }
    }
    
    if (!leaked.empty()) {
        std::cout << "⚠️ Potential memory leaks detected:\n";
        for (const auto& obj : leaked) {
            std::cout << "   Leaked: " << valueTypeName(obj->type) 
                      << " (" << obj->toString() << ")\n";
        }
    } else {
        std::cout << "✅ No memory leaks detected\n";
    }
}

void GarbageCollector::validateHeap() const {
    // Validate heap integrity
    for (const auto& obj : heap) {
        if (!obj) {
            std::cout << "❌ Null object found in heap!\n";
            continue;
        }
        
        // Validate object type
        if (obj->type >= ValueType::CLASS && obj->type <= ValueType::MAP) {
            if (!obj->obj) {
                std::cout << "❌ Object type without obj pointer!\n";
            }
        }
    }
    
    std::cout << "✅ Heap validation completed\n";
}

void GarbageCollector::detectCircularReferences() {
    // 🔄 Circular Reference Detection
    // Detects A -> B -> A patterns that shared_ptr can't handle
    std::unordered_set<std::shared_ptr<Value>> visited;
    std::unordered_set<std::shared_ptr<Value>> recursionStack;
    size_t cyclesFound = 0;
    
    std::function<bool(std::shared_ptr<Value>)> detectCycle = [&](std::shared_ptr<Value> obj) -> bool {
        if (!obj) return false;
        
        if (recursionStack.find(obj) != recursionStack.end()) {
            // Cycle detected!
            cyclesFound++;
            if (gumus_debug) {
                std::cout << "⚠️ Circular reference detected: " 
                          << valueTypeName(obj->type) << "\n";
            }
            return true;
        }
        
        if (visited.find(obj) != visited.end()) {
            return false; // Already processed
        }
        
        visited.insert(obj);
        recursionStack.insert(obj);
        
        // Check children based on type
        if (obj->type == ValueType::LIST && obj->listVal) {
            for (const auto& item : *obj->listVal) {
                detectCycle(item);
            }
        } else if (obj->type == ValueType::MAP && obj->mapVal) {
            for (const auto& pair : *obj->mapVal) {
                detectCycle(pair.second);
            }
        }
        
        recursionStack.erase(obj);
        return false;
    };
    
    // Check all heap objects
    for (const auto& obj : heap) {
        detectCycle(obj);
    }
    
    circularReferencesDetected = cyclesFound;
    
    if (cyclesFound > 0) {
        std::cout << "⚠️ Found " << cyclesFound << " circular references\n";
        std::cout << "   💡 Tip: Use weak_ptr for back-references to break cycles\n";
    } else {
        std::cout << "✅ No circular references detected\n";
    }
}

// 🔧 Internal Methods
void GarbageCollector::markRoots() {
    // Mark global environment
    if (globalEnvironment) {
        markEnvironment(globalEnvironment);
    }
    
    // Mark explicit roots
    for (const auto& root : roots) {
        mark(root);
    }
}

void GarbageCollector::markEnvironment(std::shared_ptr<Environment> env) {
    if (!env) return;
    
    // Mark all variables in this environment
    for (const auto& pair : env->values) {
        mark(pair.second);
    }
    
    // Mark parent environment
    auto parent = env->enclosing.lock();
    if (parent) {
        markEnvironment(parent);
    }
}

void GarbageCollector::markValue(std::shared_ptr<Value> value) {
    if (!value) return;
    
    switch (value->type) {
        case ValueType::LIST:
            if (value->listVal) {
                markList(value->listVal);
            }
            break;
            
        case ValueType::MAP:
            if (value->mapVal) {
                markMap(value->mapVal);
            }
            break;
            
        case ValueType::CLASS:
        case ValueType::INSTANCE:
        case ValueType::FUNCTION:
            if (value->obj) {
                markObject(value->obj, value->type);
            }
            break;
            
        default:
            // Primitive types - no references to mark
            break;
    }
}

void GarbageCollector::markList(std::shared_ptr<ValueList> list) {
    if (!list) return;
    
    for (const auto& item : *list) {
        mark(item);
    }
}

void GarbageCollector::markMap(std::shared_ptr<std::map<std::string, Value>> map) {
    if (!map) return;
    
    for (const auto& pair : *map) {
        mark(pair.second);
    }
}

void GarbageCollector::markObject(std::shared_ptr<void> obj, ValueType type) {
    // This would need to be implemented based on object types
    // For now, we'll mark the object itself
    // In a full implementation, this would traverse object fields
    
    switch (type) {
        case ValueType::FUNCTION: {
            auto func = std::static_pointer_cast<Callable>(obj);
            // Mark function closure
            if (auto userFunc = std::dynamic_pointer_cast<UserFunction>(func)) {
                markEnvironment(userFunc->closure);
            }
            break;
        }
        
        case ValueType::INSTANCE: {
            auto instance = std::static_pointer_cast<LoxInstance>(obj);
            // Mark instance fields
            for (const auto& field : instance->fields) {
                mark(field.second);
            }
            break;
        }
        
        default:
            break;
    }
}

bool GarbageCollector::isMarked(std::shared_ptr<Value> obj) const {
    // For now, we'll use a simple marking scheme
    // In a real implementation, this would be more sophisticated
    return obj && obj->isMarked;
}

void GarbageCollector::setMarked(std::shared_ptr<Value> obj, bool marked) {
    if (obj) {
        obj->isMarked = marked;
    }
}
