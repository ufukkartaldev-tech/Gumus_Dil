#include <gtest/gtest.h>
#include "../../src/compiler/vm/vm.h"
#include "../../src/compiler/vm/chunk.h"
#include "../../src/compiler/vm/op_code.h"
#include "../../src/compiler/interpreter/value.h"

class VMTest : public ::testing::Test {
protected:
    std::unique_ptr<VM> vm;
    std::unique_ptr<Chunk> chunk;
    
    void SetUp() override {
        vm = std::make_unique<VM>();
        chunk = std::make_unique<Chunk>();
    }
    
    void TearDown() override {
        vm.reset();
        chunk.reset();
    }
    
    void addConstant(const Value& value) {
        chunk->addConstant(value);
    }
    
    void addInstruction(OpCode op, int line = 1) {
        chunk->write(op, line);
    }
    
    void addInstructionWithOperand(OpCode op, uint8_t operand, int line = 1) {
        chunk->write(op, line);
        chunk->write(operand, line);
    }
};

// 🧪 Basic VM Operations Test
TEST_F(VMTest, BasicArithmetic) {
    // Test: 5 + 3
    addConstant(Value(5));
    addConstant(Value(3));
    
    addInstructionWithOperand(OP_CONSTANT, 0);  // Load 5
    addInstructionWithOperand(OP_CONSTANT, 1);  // Load 3
    addInstruction(OP_ADD);                     // Add
    addInstruction(OP_HALT);                    // Halt
    
    InterpretResult result = vm->run(chunk.get());
    EXPECT_EQ(result, INTERPRET_OK);
    
    // Check VM stats
    VMStats stats = vm->getStats();
    EXPECT_GT(stats.instructionCount, 0);
}

// 🧪 Stack Operations Test
TEST_F(VMTest, StackOperations) {
    addConstant(Value(42));
    addConstant(Value(24));
    
    addInstructionWithOperand(OP_CONSTANT, 0);  // Push 42
    addInstruction(OP_DUP);                     // Duplicate top
    addInstructionWithOperand(OP_CONSTANT, 1);  // Push 24
    addInstruction(OP_SWAP);                    // Swap top two
    addInstruction(OP_POP);                     // Pop one
    addInstruction(OP_HALT);
    
    InterpretResult result = vm->run(chunk.get());
    EXPECT_EQ(result, INTERPRET_OK);
    
    VMStats stats = vm->getStats();
    EXPECT_GE(stats.stackSize, 0);
}

// 🧪 Comparison Operations Test
TEST_F(VMTest, ComparisonOperations) {
    addConstant(Value(10));
    addConstant(Value(5));
    
    // Test: 10 > 5
    addInstructionWithOperand(OP_CONSTANT, 0);  // Load 10
    addInstructionWithOperand(OP_CONSTANT, 1);  // Load 5
    addInstruction(OP_GREATER);                 // Compare
    addInstruction(OP_HALT);
    
    InterpretResult result = vm->run(chunk.get());
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Global Variables Test
TEST_F(VMTest, GlobalVariables) {
    addConstant(Value(100));
    
    // Define global variable at slot 0
    addInstructionWithOperand(OP_CONSTANT, 0);     // Load 100
    addInstructionWithOperand(OP_DEFINE_GLOBAL, 0); // Define global[0] = 100
    
    // Get global variable
    addInstructionWithOperand(OP_GET_GLOBAL, 0);   // Load global[0]
    addInstruction(OP_HALT);
    
    InterpretResult result = vm->run(chunk.get());
    EXPECT_EQ(result, INTERPRET_OK);
    
    VMStats stats = vm->getStats();
    EXPECT_GT(stats.globalCount, 0);
}

// 🧪 Jump Instructions Test
TEST_F(VMTest, JumpInstructions) {
    addConstant(Value(true));
    
    addInstructionWithOperand(OP_CONSTANT, 0);     // Load true
    addInstructionWithOperand(OP_JUMP_IF_FALSE, 2); // Skip next instruction if false
    addInstruction(OP_TRUE);                       // This should execute
    addInstruction(OP_HALT);
    
    InterpretResult result = vm->run(chunk.get());
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 String Operations Test
TEST_F(VMTest, StringOperations) {
    addConstant(Value("Hello "));
    addConstant(Value("World"));
    
    // Test string concatenation
    addInstructionWithOperand(OP_CONSTANT, 0);  // Load "Hello "
    addInstructionWithOperand(OP_CONSTANT, 1);  // Load "World"
    addInstruction(OP_ADD);                     // Concatenate
    addInstruction(OP_HALT);
    
    InterpretResult result = vm->run(chunk.get());
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Division by Zero Test
TEST_F(VMTest, DivisionByZero) {
    addConstant(Value(10));
    addConstant(Value(0));
    
    addInstructionWithOperand(OP_CONSTANT, 0);  // Load 10
    addInstructionWithOperand(OP_CONSTANT, 1);  // Load 0
    addInstruction(OP_DIVIDE);                  // Divide by zero
    addInstruction(OP_HALT);
    
    InterpretResult result = vm->run(chunk.get());
    EXPECT_EQ(result, INTERPRET_RUNTIME_ERROR);
}

// 🧪 Stack Overflow Test
TEST_F(VMTest, StackOverflow) {
    addConstant(Value(1));
    
    // Try to push too many values
    for (int i = 0; i < STACK_MAX + 10; i++) {
        addInstructionWithOperand(OP_CONSTANT, 0);
    }
    addInstruction(OP_HALT);
    
    InterpretResult result = vm->run(chunk.get());
    // Should handle gracefully without crashing
    EXPECT_NE(result, INTERPRET_OK);
}

// 🧪 Memory Usage Test
TEST_F(VMTest, MemoryUsage) {
    // Add many constants and operations
    for (int i = 0; i < 100; i++) {
        addConstant(Value(i));
        addInstructionWithOperand(OP_CONSTANT, i % 10);
        if (i % 10 == 0) {
            addInstruction(OP_POP);
        }
    }
    addInstruction(OP_HALT);
    
    size_t initialMemory = vm->getCurrentMemoryUsage();
    InterpretResult result = vm->run(chunk.get());
    size_t finalMemory = vm->getCurrentMemoryUsage();
    
    EXPECT_EQ(result, INTERPRET_OK);
    EXPECT_GT(finalMemory, initialMemory);
}

// 🧪 GC Trigger Test
TEST_F(VMTest, GCTrigger) {
    // Create enough operations to potentially trigger GC
    for (int i = 0; i < 2000; i++) {
        addConstant(Value("String " + std::to_string(i)));
        addInstructionWithOperand(OP_CONSTANT, i % 100);
        addInstruction(OP_POP);
    }
    addInstruction(OP_HALT);
    
    InterpretResult result = vm->run(chunk.get());
    EXPECT_EQ(result, INTERPRET_OK);
    
    VMStats stats = vm->getStats();
    EXPECT_GT(stats.instructionCount, 2000);
}

// 🧪 Boolean Logic Test
TEST_F(VMTest, BooleanLogic) {
    addConstant(Value(true));
    addConstant(Value(false));
    
    // Test: true AND false
    addInstructionWithOperand(OP_CONSTANT, 0);  // Load true
    addInstructionWithOperand(OP_CONSTANT, 1);  // Load false
    addInstruction(OP_AND);                     // AND operation
    addInstruction(OP_HALT);
    
    InterpretResult result = vm->run(chunk.get());
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Negation Test
TEST_F(VMTest, NegationOperations) {
    addConstant(Value(42));
    addConstant(Value(true));
    
    // Test numeric negation
    addInstructionWithOperand(OP_CONSTANT, 0);  // Load 42
    addInstruction(OP_NEGATE);                  // Negate
    
    // Test boolean negation
    addInstructionWithOperand(OP_CONSTANT, 1);  // Load true
    addInstruction(OP_NOT);                     // NOT
    
    addInstruction(OP_HALT);
    
    InterpretResult result = vm->run(chunk.get());
    EXPECT_EQ(result, INTERPRET_OK);
}

// 🧪 Performance Benchmark Test
TEST_F(VMTest, PerformanceBenchmark) {
    // Create a computation-heavy program
    addConstant(Value(1));
    addConstant(Value(2));
    
    auto start = std::chrono::high_resolution_clock::now();
    
    // Fibonacci-like computation
    for (int i = 0; i < 1000; i++) {
        addInstructionWithOperand(OP_CONSTANT, 0);  // Load 1
        addInstructionWithOperand(OP_CONSTANT, 1);  // Load 2
        addInstruction(OP_ADD);                     // Add
        addInstruction(OP_POP);                     // Pop result
    }
    addInstruction(OP_HALT);
    
    InterpretResult result = vm->run(chunk.get());
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    EXPECT_EQ(result, INTERPRET_OK);
    EXPECT_LT(duration.count(), 1000); // Should complete within 1 second
    
    VMStats stats = vm->getStats();
    EXPECT_GT(stats.instructionCount, 3000);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}