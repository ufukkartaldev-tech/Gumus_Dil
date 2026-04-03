#include "memory_pool.h"
#include <iostream>

// 🌍 Global memory pool instances
ValuePool g_valuePool;
MemoryPool<std::string> g_stringPool;
MemoryPool<std::vector<Value>> g_listPool;

// 📊 Memory Pool Statistics and Management

void printMemoryPoolStats() {
    std::cout << "📊 Memory Pool Statistics:\n";
    std::cout << "  Value Pool:\n";
    std::cout << "    Current Usage: " << g_valuePool.getCurrentUsage() << " bytes\n";
    std::cout << "    Total Allocated: " << g_valuePool.getTotalAllocated() << " bytes\n";
    std::cout << "    Peak Usage: " << g_valuePool.getPeakUsage() << " bytes\n";
    std::cout << "    Fragmentation: " << (g_valuePool.getFragmentation() * 100) << "%\n";
    
    std::cout << "  String Pool:\n";
    std::cout << "    Current Usage: " << g_stringPool.getCurrentUsage() << " bytes\n";
    std::cout << "    Total Allocated: " << g_stringPool.getTotalAllocated() << " bytes\n";
    std::cout << "    Peak Usage: " << g_stringPool.getPeakUsage() << " bytes\n";
    std::cout << "    Block Count: " << g_stringPool.getBlockCount() << "\n";
    
    std::cout << "  List Pool:\n";
    std::cout << "    Current Usage: " << g_listPool.getCurrentUsage() << " bytes\n";
    std::cout << "    Total Allocated: " << g_listPool.getTotalAllocated() << " bytes\n";
    std::cout << "    Peak Usage: " << g_listPool.getPeakUsage() << " bytes\n";
    std::cout << "    Block Count: " << g_listPool.getBlockCount() << "\n";
}

void resetMemoryPools() {
    std::cout << "🧹 Resetting memory pools...\n";
    g_valuePool.reset();
    g_stringPool.reset();
    g_listPool.reset();
    std::cout << "✅ Memory pools reset completed\n";
}

void clearMemoryPools() {
    std::cout << "🗑️ Clearing memory pools...\n";
    g_valuePool.clear();
    g_stringPool.clear();
    g_listPool.clear();
    std::cout << "✅ Memory pools cleared\n";
}

// 🎯 Memory Pool Manager
class MemoryPoolManager {
private:
    static MemoryPoolManager* instance;
    bool initialized = false;
    
public:
    static MemoryPoolManager& getInstance() {
        if (!instance) {
            instance = new MemoryPoolManager();
        }
        return *instance;
    }
    
    void initialize() {
        if (!initialized) {
            std::cout << "🚀 Initializing memory pools...\n";
            // Pools are already initialized as global objects
            initialized = true;
            std::cout << "✅ Memory pools initialized\n";
        }
    }
    
    void shutdown() {
        if (initialized) {
            std::cout << "🛑 Shutting down memory pools...\n";
            printMemoryPoolStats();
            clearMemoryPools();
            initialized = false;
            std::cout << "✅ Memory pools shutdown completed\n";
        }
    }
    
    void performMaintenance() {
        // Check for memory pressure and optimize pools
        size_t totalUsage = g_valuePool.getCurrentUsage() + 
                           g_stringPool.getCurrentUsage() + 
                           g_listPool.getCurrentUsage();
        
        const size_t MEMORY_PRESSURE_THRESHOLD = 50 * 1024 * 1024; // 50MB
        
        if (totalUsage > MEMORY_PRESSURE_THRESHOLD) {
            std::cout << "⚠️ Memory pressure detected (" << totalUsage << " bytes)\n";
            
            // Check fragmentation
            double avgFragmentation = (g_valuePool.getFragmentation() + 
                                     g_stringPool.getFragmentation() + 
                                     g_listPool.getFragmentation()) / 3.0;
            
            if (avgFragmentation > 0.5) { // 50% fragmentation
                std::cout << "🧹 High fragmentation detected, resetting pools\n";
                resetMemoryPools();
            }
        }
    }
    
    bool isHealthy() const {
        // Check if memory pools are in a healthy state
        double valueFragmentation = g_valuePool.getFragmentation();
        double stringFragmentation = g_stringPool.getFragmentation();
        double listFragmentation = g_listPool.getFragmentation();
        
        return valueFragmentation < 0.7 && 
               stringFragmentation < 0.7 && 
               listFragmentation < 0.7;
    }
};

MemoryPoolManager* MemoryPoolManager::instance = nullptr;

// 🌍 Global functions for memory pool management
void initializeMemoryPools() {
    MemoryPoolManager::getInstance().initialize();
}

void shutdownMemoryPools() {
    MemoryPoolManager::getInstance().shutdown();
}

void performMemoryPoolMaintenance() {
    MemoryPoolManager::getInstance().performMaintenance();
}

bool areMemoryPoolsHealthy() {
    return MemoryPoolManager::getInstance().isHealthy();
}