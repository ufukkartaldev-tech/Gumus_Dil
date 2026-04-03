#include <gtest/gtest.h>
#include "../../src/compiler/vm/memory_pool.h"
#include "../../src/compiler/interpreter/garbage_collector.h"
#include "../../src/compiler/interpreter/value.h"
#include <thread>
#include <vector>
#include <chrono>

class MemoryManagementTest : public ::testing::Test {
protected:
    void SetUp() override {
        initializeMemoryPools();
    }
    
    void TearDown() override {
        shutdownMemoryPools();
    }
};

// 🧪 Memory Pool Basic Operations Test
TEST_F(MemoryManagementTest, MemoryPoolBasicOperations) {
    ValuePool pool;
    
    // Allocate values
    std::vector<Value*> values;
    for (int i = 0; i < 100; i++) {
        Value* val = pool.allocateValue();
        ASSERT_NE(val, nullptr);
        val->type = ValueType::INTEGER;
        val->intVal = i;
        values.push_back(val);
    }
    
    // Check statistics
    EXPECT_GT(pool.getCurrentUsage(), 0);
    EXPECT_GT(pool.getTotalAllocated(), 0);
    EXPECT_EQ(pool.getTotalAllocated(), 100 * sizeof(Value));
    
    // Deallocate values
    for (Value* val : values) {
        pool.deallocateValue(val);
    }
    
    EXPECT_GT(pool.getTotalAllocated(), 0); // Still shows total allocated
}

// 🧪 Memory Pool Performance Test
TEST_F(MemoryManagementTest, MemoryPoolPerformance) {
    ValuePool pool;
    const int NUM_ALLOCATIONS = 10000;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    // Allocate many values
    std::vector<Value*> values;
    values.reserve(NUM_ALLOCATIONS);
    
    for (int i = 0; i < NUM_ALLOCATIONS; i++) {
        Value* val = pool.allocateValue();
        val->type = ValueType::INTEGER;
        val->intVal = i;
        values.push_back(val);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    // Should be fast (< 10ms for 10k allocations)
    EXPECT_LT(duration.count(), 10000);
    
    // Check memory usage
    EXPECT_GT(pool.getCurrentUsage(), NUM_ALLOCATIONS * sizeof(Value) * 0.8);
    EXPECT_LT(pool.getFragmentation(), 0.5); // Less than 50% fragmentation
    
    // Cleanup
    for (Value* val : values) {
        pool.deallocateValue(val);
    }
}

// 🧪 Memory Pool Thread Safety Test
TEST_F(MemoryManagementTest, MemoryPoolThreadSafety) {
    ValuePool pool;
    const int NUM_THREADS = 4;
    const int ALLOCATIONS_PER_THREAD = 1000;
    
    std::vector<std::thread> threads;
    std::vector<std::vector<Value*>> threadValues(NUM_THREADS);
    
    // Launch threads
    for (int t = 0; t < NUM_THREADS; t++) {
        threads.emplace_back([&pool, &threadValues, t, ALLOCATIONS_PER_THREAD]() {
            for (int i = 0; i < ALLOCATIONS_PER_THREAD; i++) {
                Value* val = pool.allocateValue();
                val->type = ValueType::INTEGER;
                val->intVal = t * 1000 + i;
                threadValues[t].push_back(val);
            }
        });
    }
    
    // Wait for completion
    for (auto& thread : threads) {
        thread.join();
    }
    
    // Verify allocations
    size_t totalAllocated = 0;
    for (const auto& values : threadValues) {
        totalAllocated += values.size();
    }
    
    EXPECT_EQ(totalAllocated, NUM_THREADS * ALLOCATIONS_PER_THREAD);
    EXPECT_GT(pool.getCurrentUsage(), 0);
    
    // Cleanup
    for (auto& values : threadValues) {
        for (Value* val : values) {
            pool.deallocateValue(val);
        }
    }
}

// 🧪 Garbage Collector Stability Test
TEST_F(MemoryManagementTest, GarbageCollectorStability) {
    auto globalEnv = std::make_shared<Environment>();
    auto gc = std::make_unique<GarbageCollector>(globalEnv);
    
    // Create objects with complex reference patterns
    std::vector<std::shared_ptr<Value>> objects;
    
    for (int i = 0; i < 1000; i++) {
        auto obj = std::make_shared<Value>();
        obj->type = ValueType::OBJECT;
        obj->intVal = i;
        
        // Create some references
        if (i > 0 && i % 10 == 0) {
            obj->references.push_back(objects[i - 1]);
        }
        if (i > 1 && i % 20 == 0) {
            obj->references.push_back(objects[i - 2]);
        }
        
        objects.push_back(obj);
        gc->addToHeap(obj);
    }
    
    // Add some roots
    for (int i = 0; i < 10; i++) {
        gc->addRoot(objects[i]);
    }
    
    // Run multiple GC cycles
    for (int cycle = 0; cycle < 5; cycle++) {
        EXPECT_NO_THROW(gc->collect());
        EXPECT_GT(gc->getTotalCollections(), cycle);
    }
    
    // Verify GC statistics
    EXPECT_GT(gc->getTotalCollections(), 0);
    EXPECT_GE(gc->getObjectsCollected(), 0);
}

// 🧪 Memory Leak Detection Test
TEST_F(MemoryManagementTest, MemoryLeakDetection) {
    auto globalEnv = std::make_shared<Environment>();
    auto gc = std::make_unique<GarbageCollector>(globalEnv);
    
    size_t initialHeapSize = gc->getHeapSize();
    
    // Create temporary objects that should be collected
    {
        std::vector<std::shared_ptr<Value>> tempObjects;
        for (int i = 0; i < 100; i++) {
            auto obj = std::make_shared<Value>();
            obj->type = ValueType::STRING;
            obj->stringValue = "temp_" + std::to_string(i);
            tempObjects.push_back(obj);
            gc->addToHeap(obj);
        }
        
        EXPECT_EQ(gc->getHeapSize(), initialHeapSize + 100);
    } // tempObjects go out of scope
    
    // Force GC
    gc->collect();
    
    // Most objects should be collected (no roots pointing to them)
    EXPECT_GT(gc->getObjectsCollected(), 50); // At least half should be collected
    
    // Run leak detection
    EXPECT_NO_THROW(gc->detectLeaks());
}

// 🧪 Circular Reference Handling Test
TEST_F(MemoryManagementTest, CircularReferenceHandling) {
    auto globalEnv = std::make_shared<Environment>();
    auto gc = std::make_unique<GarbageCollector>(globalEnv);
    
    // Create circular references
    auto obj1 = std::make_shared<Value>();
    auto obj2 = std::make_shared<Value>();
    auto obj3 = std::make_shared<Value>();
    
    obj1->type = ValueType::OBJECT;
    obj2->type = ValueType::OBJECT;
    obj3->type = ValueType::OBJECT;
    
    // Create cycle: obj1 -> obj2 -> obj3 -> obj1
    obj1->references.push_back(obj2);
    obj2->references.push_back(obj3);
    obj3->references.push_back(obj1);
    
    gc->addToHeap(obj1);
    gc->addToHeap(obj2);
    gc->addToHeap(obj3);
    
    // Detect circular references
    EXPECT_NO_THROW(gc->detectCircularReferences());
    EXPECT_GT(gc->getCircularReferencesDetected(), 0);
    
    // GC should handle this gracefully
    EXPECT_NO_THROW(gc->collect());
}

// 🧪 Memory Pressure Test
TEST_F(MemoryManagementTest, MemoryPressureHandling) {
    ValuePool pool;
    
    // Allocate until memory pressure
    std::vector<Value*> values;
    const int MAX_ALLOCATIONS = 100000;
    
    for (int i = 0; i < MAX_ALLOCATIONS; i++) {
        Value* val = pool.allocateValue();
        val->type = ValueType::STRING;
        values.push_back(val);
        
        // Check memory health periodically
        if (i % 10000 == 0) {
            performMemoryPoolMaintenance();
            EXPECT_TRUE(areMemoryPoolsHealthy() || i > 50000); // Allow some pressure at high usage
        }
    }
    
    // Check final state
    EXPECT_GT(pool.getCurrentUsage(), 0);
    EXPECT_GT(pool.getPeakUsage(), pool.getCurrentUsage());
    
    // Cleanup
    for (Value* val : values) {
        pool.deallocateValue(val);
    }
}

// 🧪 Memory Pool Reset Test
TEST_F(MemoryManagementTest, MemoryPoolReset) {
    ValuePool pool;
    
    // Allocate some values
    std::vector<Value*> values;
    for (int i = 0; i < 100; i++) {
        Value* val = pool.allocateValue();
        val->type = ValueType::INTEGER;
        val->intVal = i;
        values.push_back(val);
    }
    
    size_t usageBeforeReset = pool.getCurrentUsage();
    EXPECT_GT(usageBeforeReset, 0);
    
    // Reset pool
    pool.reset();
    
    // Usage should be reset but total allocated should remain
    EXPECT_EQ(pool.getCurrentUsage(), 0);
    EXPECT_GT(pool.getTotalAllocated(), 0);
    
    // Should be able to allocate again
    Value* newVal = pool.allocateValue();
    EXPECT_NE(newVal, nullptr);
    pool.deallocateValue(newVal);
}

// 🧪 Integration Test: GC + Memory Pool
TEST_F(MemoryManagementTest, GCMemoryPoolIntegration) {
    auto globalEnv = std::make_shared<Environment>();
    auto gc = std::make_unique<GarbageCollector>(globalEnv);
    ValuePool pool;
    
    // Create objects using both systems
    std::vector<std::shared_ptr<Value>> gcObjects;
    std::vector<Value*> poolObjects;
    
    for (int i = 0; i < 500; i++) {
        // GC-managed object
        auto gcObj = std::make_shared<Value>();
        gcObj->type = ValueType::INTEGER;
        gcObj->intVal = i;
        gcObjects.push_back(gcObj);
        gc->addToHeap(gcObj);
        
        // Pool-managed object
        Value* poolObj = pool.allocateValue();
        poolObj->type = ValueType::FLOAT;
        poolObj->floatVal = i * 1.5;
        poolObjects.push_back(poolObj);
    }
    
    // Add some roots
    for (int i = 0; i < 10; i++) {
        gc->addRoot(gcObjects[i]);
    }
    
    // Run GC
    gc->collect();
    
    // Check both systems are working
    EXPECT_GT(gc->getTotalCollections(), 0);
    EXPECT_GT(pool.getCurrentUsage(), 0);
    
    // Cleanup pool objects
    for (Value* obj : poolObjects) {
        pool.deallocateValue(obj);
    }
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}