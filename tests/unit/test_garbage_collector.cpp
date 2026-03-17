#include <gtest/gtest.h>
#include "../../src/compiler/interpreter/garbage_collector.h"
#include "../../src/compiler/interpreter/value.h"
#include "../../src/compiler/interpreter/environment.h"
#include <memory>

class GarbageCollectorTest : public ::testing::Test {
protected:
    std::shared_ptr<Environment> globalEnv;
    std::unique_ptr<GarbageCollector> gc;
    
    void SetUp() override {
        globalEnv = std::make_shared<Environment>();
        gc = std::make_unique<GarbageCollector>(globalEnv);
    }
    
    void TearDown() override {
        gc.reset();
        globalEnv.reset();
    }
    
    std::shared_ptr<Value> createValue(ValueType type, const std::string& name = "") {
        auto value = std::make_shared<Value>();
        value->type = type;
        if (!name.empty()) {
            value->stringValue = name;
        }
        return value;
    }
};

// 🧪 Heap Management Testi
TEST_F(GarbageCollectorTest, HeapManagement) {
    auto value1 = createValue(ValueType::INTEGER);
    auto value2 = createValue(ValueType::STRING);
    
    gc->addToHeap(value1);
    gc->addToHeap(value2);
    
    EXPECT_EQ(gc->getHeapSize(), 2);
}

// 🧪 Root Set Management Testi
TEST_F(GarbageCollectorTest, RootSetManagement) {
    auto value1 = createValue(ValueType::INTEGER);
    auto value2 = createValue(ValueType::STRING);
    
    gc->addRoot(value1);
    gc->addRoot(value2);
    
    EXPECT_EQ(gc->getRootCount(), 2);
    
    gc->removeRoot(value1);
    EXPECT_EQ(gc->getRootCount(), 1);
}

// 🧪 Mark and Sweep Testi
TEST_F(GarbageCollectorTest, MarkAndSweep) {
    // Create values
    auto rootValue = createValue(ValueType::INTEGER, "root");
    auto reachableValue = createValue(ValueType::STRING, "reachable");
    auto unreachableValue = createValue(ValueType::BOOLEAN, "unreachable");
    
    // Add to heap
    gc->addToHeap(rootValue);
    gc->addToHeap(reachableValue);
    gc->addToHeap(unreachableValue);
    
    // Add root
    gc->addRoot(rootValue);
    
    // Create reference from root to reachable
    rootValue->references.push_back(reachableValue);
    
    size_t initialHeapSize = gc->getHeapSize();
    EXPECT_EQ(initialHeapSize, 3);
    
    // Run garbage collection
    gc->collect();
    
    // Check statistics
    EXPECT_EQ(gc->getTotalCollections(), 1);
    EXPECT_GT(gc->getObjectsCollected(), 0);
}

// 🧪 Circular Reference Detection Testi
TEST_F(GarbageCollectorTest, CircularReferenceDetection) {
    auto value1 = createValue(ValueType::OBJECT, "obj1");
    auto value2 = createValue(ValueType::OBJECT, "obj2");
    
    // Create circular reference
    value1->references.push_back(value2);
    value2->references.push_back(value1);
    
    gc->addToHeap(value1);
    gc->addToHeap(value2);
    
    // Neither is a root, so both should be collected
    gc->collect();
    
    EXPECT_GT(gc->getCircularReferencesDetected(), 0);
}

// 🧪 Performance Metrics Testi
TEST_F(GarbageCollectorTest, PerformanceMetrics) {
    // Add some values
    for (int i = 0; i < 100; i++) {
        auto value = createValue(ValueType::INTEGER);
        gc->addToHeap(value);
    }
    
    // Run collection
    auto startTime = std::chrono::high_resolution_clock::now();
    gc->collect();
    auto endTime = std::chrono::high_resolution_clock::now();
    
    // Check metrics
    EXPECT_EQ(gc->getTotalCollections(), 1);
    EXPECT_GT(gc->getObjectsCollected(), 0);
    EXPECT_GT(gc->getMemoryFreed(), 0);
    
    // Check timing
    double avgTime = gc->getAverageGCTime();
    EXPECT_GT(avgTime, 0.0);
}

// 🧪 Memory Leak Prevention Testi
TEST_F(GarbageCollectorTest, MemoryLeakPrevention) {
    std::vector<std::shared_ptr<Value>> values;
    
    // Create a chain of references
    for (int i = 0; i < 10; i++) {
        auto value = createValue(ValueType::OBJECT, "obj" + std::to_string(i));
        values.push_back(value);
        gc->addToHeap(value);
        
        if (i > 0) {
            values[i-1]->references.push_back(value);
        }
    }
    
    // Only add first value as root
    gc->addRoot(values[0]);
    
    size_t initialHeapSize = gc->getHeapSize();
    EXPECT_EQ(initialHeapSize, 10);
    
    // Remove root reference
    gc->removeRoot(values[0]);
    
    // Run collection - all should be collected
    gc->collect();
    
    EXPECT_EQ(gc->getObjectsCollected(), 10);
}

// 🧪 Environment Integration Testi
TEST_F(GarbageCollectorTest, EnvironmentIntegration) {
    // Add values to global environment
    auto value1 = createValue(ValueType::INTEGER);
    auto value2 = createValue(ValueType::STRING);
    
    globalEnv->define("var1", *value1);
    globalEnv->define("var2", *value2);
    
    gc->addToHeap(value1);
    gc->addToHeap(value2);
    
    // Values should be reachable through environment
    gc->collect();
    
    // Both values should still exist (reachable through global env)
    EXPECT_EQ(gc->getObjectsCollected(), 0);
}

// 🧪 Stress Test
TEST_F(GarbageCollectorTest, StressTest) {
    const int NUM_OBJECTS = 1000;
    std::vector<std::shared_ptr<Value>> values;
    
    // Create many objects with random references
    for (int i = 0; i < NUM_OBJECTS; i++) {
        auto value = createValue(ValueType::OBJECT, "stress_obj" + std::to_string(i));
        values.push_back(value);
        gc->addToHeap(value);
        
        // Create some random references
        if (i > 0 && i % 3 == 0) {
            int refIndex = i / 3;
            values[refIndex]->references.push_back(value);
        }
    }
    
    // Add some roots
    for (int i = 0; i < 10; i++) {
        gc->addRoot(values[i]);
    }
    
    // Run multiple collections
    for (int i = 0; i < 5; i++) {
        gc->collect();
    }
    
    EXPECT_EQ(gc->getTotalCollections(), 5);
    EXPECT_GT(gc->getObjectsCollected(), 0);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}