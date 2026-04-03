#include <gtest/gtest.h>
#include "../../src/compiler/codegen/bytecode_generator.h"
#include "../../src/compiler/vm/vm.h"
#include "../../src/compiler/interpreter/garbage_collector.h"
#include "../../src/compiler/vm/memory_pool.h"
#include <chrono>
#include <vector>
#include <random>

class PerformanceBenchmarkTest : public ::testing::Test {
protected:
    void SetUp() override {
        initializeMemoryPools();
    }
    
    void TearDown() override {
        shutdownMemoryPools();
    }
    
    double measureExecutionTime(std::function<void()> func) {
        auto start = std::chrono::high_resolution_clock::now();
        func();
        auto end = std::chrono::high_resolution_clock::now();
        return std::chrono::duration<double, std::milli>(end - start).count();
    }
};

// 🧪 Bytecode Generation Performance
TEST_F(PerformanceBenchmarkTest, BytecodeGenerationPerformance) {
    auto module = std::make_unique<IRModule>();
    auto func = std::make_unique<IRFunction>();
    func->name = "performance_test";
    func->blocks.push_back(std::make_unique<BasicBlock>("entry"));
    
    auto* block = func->blocks[0].get();
    
    // Generate large number of instructions
    const int NUM_INSTRUCTIONS = 10000;
    for (int i = 0; i < NUM_INSTRUCTIONS; i++) {
        auto instr = std::make_unique<IRInstruction>();
        instr->opcode = IROpcode::ADD;
        instr->operands = {i, i + 1};
        instr->result = "var" + std::to_string(i);
        instr->line = i + 1;
        block->instructions.push_back(std::move(instr));
    }
    
    module->functions.push_back(std::move(func));
    
    // Measure bytecode generation time
    double generationTime = measureExecutionTime([&]() {
        BytecodeGenerator generator(module.get());
        Chunk chunk = generator.generateBytecode();
        EXPECT_GT(chunk.code.size(), NUM_INSTRUCTIONS);
    });
    
    // Should generate 10k instructions in < 100ms
    EXPECT_LT(generationTime, 100.0);
    std::cout << "📊 Bytecode generation: " << generationTime << "ms for " 
              << NUM_INSTRUCTIONS << " instructions\n";
}

// 🧪 VM Execution Performance
TEST_F(PerformanceBenchmarkTest, VMExecutionPerformance) {
    auto vm = std::make_unique<VM>();
    auto chunk = std::make_unique<Chunk>();
    
    // Create arithmetic-heavy program
    const int NUM_OPERATIONS = 5000;
    
    // Add constants
    for (int i = 0; i < 100; i++) {
        chunk->addConstant(Value(i));
    }
    
    // Generate arithmetic operations
    for (int i = 0; i < NUM_OPERATIONS; i++) {
        chunk->write(OP_CONSTANT, 1);
        chunk->write(i % 100, 1);
        chunk->write(OP_CONSTANT, 1);
        chunk->write((i + 1) % 100, 1);
        chunk->write(OP_ADD, 1);
        chunk->write(OP_POP, 1); // Remove result
    }
    chunk->write(OP_HALT, 1);
    
    // Measure execution time
    double executionTime = measureExecutionTime([&]() {
        InterpretResult result = vm->run(chunk.get());
        EXPECT_EQ(result, INTERPRET_OK);
    });
    
    // Should execute 5k operations in < 50ms
    EXPECT_LT(executionTime, 50.0);
    
    VMStats stats = vm->getStats();
    std::cout << "📊 VM execution: " << executionTime << "ms for " 
              << stats.instructionCount << " instructions\n";
    std::cout << "   Instructions/ms: " << (stats.instructionCount / executionTime) << "\n";
}

// 🧪 Garbage Collection Performance
TEST_F(PerformanceBenchmarkTest, GarbageCollectionPerformance) {
    auto globalEnv = std::make_shared<Environment>();
    auto gc = std::make_unique<GarbageCollector>(globalEnv);
    
    const int NUM_OBJECTS = 50000;
    std::vector<std::shared_ptr<Value>> objects;
    
    // Create objects
    double allocationTime = measureExecutionTime([&]() {
        for (int i = 0; i < NUM_OBJECTS; i++) {
            auto obj = std::make_shared<Value>();
            obj->type = ValueType::INTEGER;
            obj->intVal = i;
            
            // Create some references (10% chance)
            if (i > 0 && (i % 10 == 0)) {
                obj->references.push_back(objects[i - 1]);
            }
            
            objects.push_back(obj);
            gc->addToHeap(obj);
        }
    });
    
    // Add roots (keep 10% alive)
    for (int i = 0; i < NUM_OBJECTS / 10; i++) {
        gc->addRoot(objects[i * 10]);
    }
    
    // Measure GC performance
    double gcTime = measureExecutionTime([&]() {
        gc->collect();
    });
    
    // GC should complete in reasonable time (< 100ms for 50k objects)
    EXPECT_LT(gcTime, 100.0);
    
    std::cout << "📊 GC Performance:\n";
    std::cout << "   Allocation: " << allocationTime << "ms for " << NUM_OBJECTS << " objects\n";
    std::cout << "   Collection: " << gcTime << "ms\n";
    std::cout << "   Objects collected: " << gc->getObjectsCollected() << "\n";
    std::cout << "   Collection rate: " << (gc->getObjectsCollected() / gcTime) << " objects/ms\n";
}

// 🧪 Memory Pool Performance
TEST_F(PerformanceBenchmarkTest, MemoryPoolPerformance) {
    ValuePool pool;
    const int NUM_ALLOCATIONS = 100000;
    
    std::vector<Value*> values;
    values.reserve(NUM_ALLOCATIONS);
    
    // Measure allocation performance
    double allocationTime = measureExecutionTime([&]() {
        for (int i = 0; i < NUM_ALLOCATIONS; i++) {
            Value* val = pool.allocateValue();
            val->type = ValueType::INTEGER;
            val->intVal = i;
            values.push_back(val);
        }
    });
    
    // Measure deallocation performance
    double deallocationTime = measureExecutionTime([&]() {
        for (Value* val : values) {
            pool.deallocateValue(val);
        }
    });
    
    // Should be very fast (< 20ms for 100k allocations)
    EXPECT_LT(allocationTime, 20.0);
    EXPECT_LT(deallocationTime, 10.0);
    
    std::cout << "📊 Memory Pool Performance:\n";
    std::cout << "   Allocation: " << allocationTime << "ms for " << NUM_ALLOCATIONS << " objects\n";
    std::cout << "   Deallocation: " << deallocationTime << "ms\n";
    std::cout << "   Allocation rate: " << (NUM_ALLOCATIONS / allocationTime) << " objects/ms\n";
    std::cout << "   Peak usage: " << pool.getPeakUsage() << " bytes\n";
    std::cout << "   Fragmentation: " << (pool.getFragmentation() * 100) << "%\n";
}

// 🧪 Large Project Simulation
TEST_F(PerformanceBenchmarkTest, LargeProjectSimulation) {
    // Simulate a large project with multiple modules
    const int NUM_MODULES = 10;
    const int INSTRUCTIONS_PER_MODULE = 1000;
    
    std::vector<std::unique_ptr<IRModule>> modules;
    std::vector<Chunk> chunks;
    
    // Generate modules
    double moduleGenerationTime = measureExecutionTime([&]() {
        for (int m = 0; m < NUM_MODULES; m++) {
            auto module = std::make_unique<IRModule>();
            auto func = std::make_unique<IRFunction>();
            func->name = "module_" + std::to_string(m);
            func->blocks.push_back(std::make_unique<BasicBlock>("entry"));
            
            auto* block = func->blocks[0].get();
            
            for (int i = 0; i < INSTRUCTIONS_PER_MODULE; i++) {
                auto instr = std::make_unique<IRInstruction>();
                instr->opcode = static_cast<IROpcode>(static_cast<int>(IROpcode::ADD) + (i % 5));
                instr->operands = {i, i + 1};
                instr->result = "var" + std::to_string(i);
                instr->line = i + 1;
                block->instructions.push_back(std::move(instr));
            }
            
            module->functions.push_back(std::move(func));
            modules.push_back(std::move(module));
        }
    });
    
    // Generate bytecode for all modules
    double bytecodeGenerationTime = measureExecutionTime([&]() {
        for (auto& module : modules) {
            BytecodeGenerator generator(module.get());
            chunks.push_back(generator.generateBytecode());
        }
    });
    
    // Execute all modules
    auto vm = std::make_unique<VM>();
    double executionTime = measureExecutionTime([&]() {
        for (auto& chunk : chunks) {
            // Modify chunk to be executable
            chunk.write(OP_HALT, 1);
            InterpretResult result = vm->run(&chunk);
            EXPECT_EQ(result, INTERPRET_OK);
        }
    });
    
    std::cout << "📊 Large Project Simulation:\n";
    std::cout << "   Modules: " << NUM_MODULES << "\n";
    std::cout << "   Instructions per module: " << INSTRUCTIONS_PER_MODULE << "\n";
    std::cout << "   Module generation: " << moduleGenerationTime << "ms\n";
    std::cout << "   Bytecode generation: " << bytecodeGenerationTime << "ms\n";
    std::cout << "   Execution: " << executionTime << "ms\n";
    std::cout << "   Total time: " << (moduleGenerationTime + bytecodeGenerationTime + executionTime) << "ms\n";
    
    // Should complete large project in reasonable time (< 500ms)
    double totalTime = moduleGenerationTime + bytecodeGenerationTime + executionTime;
    EXPECT_LT(totalTime, 500.0);
}

// 🧪 Memory Stress Test
TEST_F(PerformanceBenchmarkTest, MemoryStressTest) {
    auto globalEnv = std::make_shared<Environment>();
    auto gc = std::make_unique<GarbageCollector>(globalEnv);
    ValuePool pool;
    
    const int STRESS_ITERATIONS = 1000;
    const int OBJECTS_PER_ITERATION = 100;
    
    double totalTime = measureExecutionTime([&]() {
        for (int iter = 0; iter < STRESS_ITERATIONS; iter++) {
            // Allocate objects
            std::vector<std::shared_ptr<Value>> gcObjects;
            std::vector<Value*> poolObjects;
            
            for (int i = 0; i < OBJECTS_PER_ITERATION; i++) {
                // GC object
                auto gcObj = std::make_shared<Value>();
                gcObj->type = ValueType::STRING;
                gcObj->stringValue = "stress_" + std::to_string(iter) + "_" + std::to_string(i);
                gcObjects.push_back(gcObj);
                gc->addToHeap(gcObj);
                
                // Pool object
                Value* poolObj = pool.allocateValue();
                poolObj->type = ValueType::FLOAT;
                poolObj->floatVal = iter * i * 1.5;
                poolObjects.push_back(poolObj);
            }
            
            // Occasionally trigger GC
            if (iter % 100 == 0) {
                gc->collect();
                performMemoryPoolMaintenance();
            }
            
            // Cleanup pool objects
            for (Value* obj : poolObjects) {
                pool.deallocateValue(obj);
            }
        }
    });
    
    std::cout << "📊 Memory Stress Test:\n";
    std::cout << "   Iterations: " << STRESS_ITERATIONS << "\n";
    std::cout << "   Objects per iteration: " << OBJECTS_PER_ITERATION << "\n";
    std::cout << "   Total time: " << totalTime << "ms\n";
    std::cout << "   GC collections: " << gc->getTotalCollections() << "\n";
    std::cout << "   Objects collected: " << gc->getObjectsCollected() << "\n";
    std::cout << "   Pool peak usage: " << pool.getPeakUsage() << " bytes\n";
    
    // Should handle stress test without excessive time (< 2 seconds)
    EXPECT_LT(totalTime, 2000.0);
    EXPECT_TRUE(areMemoryPoolsHealthy());
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}