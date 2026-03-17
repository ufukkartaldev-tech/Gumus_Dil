#include "memory_pool.h"
#include <iostream>

// 🌍 Global memory pool instances
ValuePool g_valuePool;
MemoryPool<std::string> g_stringPool;
MemoryPool<std::vector<Value>> g_listPool;

// 📊 Memory statistics and reporting
namespace MemoryStats {
    void printReport() {
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
        
        std::cout << "  List Pool:\n";
        std::cout << "    Current Usage: " << g_listPool.getCurrentUsage() << " bytes\n";
        std::cout << "    Total Allocated: " << g_listPool.getTotalAllocated() << " bytes\n";
        std::cout << "    Peak Usage: " << g_listPool.getPeakUsage() << " bytes\n";
    }
    
    void resetAll() {
        g_valuePool.reset();
        g_stringPool.reset();
        g_listPool.reset();
        std::cout << "🧹 All memory pools reset\n";
    }
    
    void clearAll() {
        g_valuePool.clear();
        g_stringPool.clear();
        g_listPool.clear();
        std::cout << "🗑️ All memory pools cleared\n";
    }
    
    size_t getTotalMemoryUsage() {
        return g_valuePool.getCurrentUsage() + 
               g_stringPool.getCurrentUsage() + 
               g_listPool.getCurrentUsage();
    }
}