#include <gtest/gtest.h>
#include "../../src/compiler/codegen/bytecode_generator.h"
#include "../../src/compiler/ir/ir_instruction.h"
#include "../../src/compiler/vm/chunk.h"
#include "../../src/compiler/vm/op_code.h"

class BytecodeGeneratorTest : public ::testing::Test {
protected:
    std::unique_ptr<IRModule> module;
    std::unique_ptr<BytecodeGenerator> generator;
    
    void SetUp() override {
        module = std::make_unique<IRModule>();
        generator = std::make_unique<BytecodeGenerator>(module.get());
    }
    
    void TearDown() override {
        generator.reset();
        module.reset();
    }
    
    std::unique_ptr<IRFunction> createTestFunction(const std::string& name) {
        auto func = std::make_unique<IRFunction>();
        func->name = name;
        func->blocks.push_back(std::make_unique<BasicBlock>("entry"));
        return func;
    }
    
    void addInstruction(BasicBlock* block, IROpcode opcode, 
                       const std::vector<IRValue>& operands = {},
                       const std::string& result = "") {
        auto instr = std::make_unique<IRInstruction>();
        instr->opcode = opcode;
        instr->operands = operands;
        instr->result = result;
        instr->line = 1;
        block->instructions.push_back(std::move(instr));
    }
};

// 🧪 Basic Bytecode Generation Test
TEST_F(BytecodeGeneratorTest, BasicArithmetic) {
    auto func = createTestFunction("main");
    auto* block = func->blocks[0].get();
    
    // Add simple arithmetic: a = 5 + 3
    addInstruction(block, IROpcode::ADD, {5, 3}, "a");
    addInstruction(block, IROpcode::HALT);
    
    module->functions.push_back(std::move(func));
    
    Chunk chunk = generator->generateBytecode();
    
    // Verify bytecode structure
    EXPECT_GT(chunk.code.size(), 0);
    EXPECT_EQ(chunk.code.back(), OP_HALT);
    
    // Check for arithmetic operations
    bool foundAdd = false;
    for (size_t i = 0; i < chunk.code.size(); i++) {
        if (chunk.code[i] == OP_ADD) {
            foundAdd = true;
            break;
        }
    }
    EXPECT_TRUE(foundAdd);
}

// 🧪 Variable Operations Test
TEST_F(BytecodeGeneratorTest, VariableOperations) {
    auto func = createTestFunction("main");
    auto* block = func->blocks[0].get();
    
    // x = 42
    addInstruction(block, IROpcode::DEF_VAR, {"x"});
    addInstruction(block, IROpcode::SET_VAR, {42, "x"});
    // y = x
    addInstruction(block, IROpcode::GET_VAR, {"x"}, "y");
    addInstruction(block, IROpcode::HALT);
    
    module->functions.push_back(std::move(func));
    
    Chunk chunk = generator->generateBytecode();
    
    // Verify variable operations exist
    std::vector<OpCode> expectedOps = {
        OP_DEFINE_GLOBAL, OP_SET_GLOBAL, OP_GET_GLOBAL, OP_HALT
    };
    
    for (OpCode op : expectedOps) {
        bool found = false;
        for (size_t i = 0; i < chunk.code.size(); i++) {
            if (chunk.code[i] == op) {
                found = true;
                break;
            }
        }
        EXPECT_TRUE(found) << "Missing opcode: " << static_cast<int>(op);
    }
}

// 🧪 Control Flow Test
TEST_F(BytecodeGeneratorTest, ControlFlow) {
    auto func = createTestFunction("main");
    auto* block = func->blocks[0].get();
    
    // if (true) jump to label
    addInstruction(block, IROpcode::JZ, {true, "end"});
    addInstruction(block, IROpcode::PRINT, {"Hello"});
    // label: end
    addInstruction(block, IROpcode::HALT);
    
    module->functions.push_back(std::move(func));
    
    Chunk chunk = generator->generateBytecode();
    
    // Check for jump instructions
    bool foundJump = false;
    for (size_t i = 0; i < chunk.code.size(); i++) {
        if (chunk.code[i] == OP_JUMP_IF_FALSE) {
            foundJump = true;
            break;
        }
    }
    EXPECT_TRUE(foundJump);
}

// 🧪 Function Call Test
TEST_F(BytecodeGeneratorTest, FunctionCall) {
    auto func = createTestFunction("main");
    auto* block = func->blocks[0].get();
    
    // call print("Hello World")
    addInstruction(block, IROpcode::CALL, {"print", "Hello World"}, "result");
    addInstruction(block, IROpcode::HALT);
    
    module->functions.push_back(std::move(func));
    
    Chunk chunk = generator->generateBytecode();
    
    // Check for call instruction
    bool foundCall = false;
    for (size_t i = 0; i < chunk.code.size(); i++) {
        if (chunk.code[i] == OP_CALL) {
            foundCall = true;
            break;
        }
    }
    EXPECT_TRUE(foundCall);
}

// 🧪 Constant Pool Test
TEST_F(BytecodeGeneratorTest, ConstantPool) {
    auto func = createTestFunction("main");
    auto* block = func->blocks[0].get();
    
    // Use various constants
    addInstruction(block, IROpcode::SET_VAR, {42, "int_var"});
    addInstruction(block, IROpcode::SET_VAR, {3.14, "float_var"});
    addInstruction(block, IROpcode::SET_VAR, {"Hello", "string_var"});
    addInstruction(block, IROpcode::SET_VAR, {true, "bool_var"});
    addInstruction(block, IROpcode::HALT);
    
    module->functions.push_back(std::move(func));
    
    Chunk chunk = generator->generateBytecode();
    
    // Verify constants are added to pool
    EXPECT_GE(chunk.constants.size(), 4);
    
    // Check constant types
    bool hasInt = false, hasFloat = false, hasString = false, hasBool = false;
    for (const auto& constant : chunk.constants) {
        switch (constant.type) {
            case ValueType::INTEGER: hasInt = true; break;
            case ValueType::FLOAT: hasFloat = true; break;
            case ValueType::STRING: hasString = true; break;
            case ValueType::BOOLEAN: hasBool = true; break;
            default: break;
        }
    }
    
    EXPECT_TRUE(hasInt);
    EXPECT_TRUE(hasFloat);
    EXPECT_TRUE(hasString);
    EXPECT_TRUE(hasBool);
}

// 🧪 Optimization Pipeline Test
TEST_F(BytecodeGeneratorTest, OptimizationPipeline) {
    auto func = createTestFunction("main");
    auto* block = func->blocks[0].get();
    
    // Create redundant operations
    addInstruction(block, IROpcode::ADD, {1, 2}, "temp1");
    addInstruction(block, IROpcode::ADD, {3, 4}, "temp2");
    addInstruction(block, IROpcode::ADD, {"temp1", "temp2"}, "result");
    addInstruction(block, IROpcode::HALT);
    
    module->functions.push_back(std::move(func));
    
    // Test different optimization levels
    CodeGenerationPipeline pipeline(module.get(), OptimizationLevel::O0);
    Chunk unoptimized = pipeline.generateOptimizedBytecode();
    
    CodeGenerationPipeline pipelineO2(module.get(), OptimizationLevel::O2);
    Chunk optimized = pipelineO2.generateOptimizedBytecode();
    
    // Optimized version should have different characteristics
    EXPECT_GT(unoptimized.code.size(), 0);
    EXPECT_GT(optimized.code.size(), 0);
}

// 🧪 Error Handling Test
TEST_F(BytecodeGeneratorTest, ErrorHandling) {
    auto func = createTestFunction("main");
    auto* block = func->blocks[0].get();
    
    // Add invalid instruction
    addInstruction(block, static_cast<IROpcode>(999), {}, "invalid");
    addInstruction(block, IROpcode::HALT);
    
    module->functions.push_back(std::move(func));
    
    // Should not crash, but handle gracefully
    EXPECT_NO_THROW({
        Chunk chunk = generator->generateBytecode();
    });
}

// 🧪 Performance Test
TEST_F(BytecodeGeneratorTest, PerformanceTest) {
    auto func = createTestFunction("main");
    auto* block = func->blocks[0].get();
    
    // Generate many instructions
    for (int i = 0; i < 1000; i++) {
        addInstruction(block, IROpcode::ADD, {i, i+1}, "var" + std::to_string(i));
    }
    addInstruction(block, IROpcode::HALT);
    
    module->functions.push_back(std::move(func));
    
    auto start = std::chrono::high_resolution_clock::now();
    Chunk chunk = generator->generateBytecode();
    auto end = std::chrono::high_resolution_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    // Should complete within reasonable time (< 100ms for 1000 instructions)
    EXPECT_LT(duration.count(), 100);
    EXPECT_GT(chunk.code.size(), 1000);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}