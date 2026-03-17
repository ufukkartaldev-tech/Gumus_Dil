#include <gtest/gtest.h>
#include "../../src/compiler/optimizer/optimizer.h"
#include "../../src/compiler/optimizer/advanced_passes.h"

class OptimizerAdvancedTest : public ::testing::Test {
protected:
    void SetUp() override {
        module = std::make_unique<IRModule>("test_module");
        function = module->createFunction("test_function");
        block = function->createBlock("entry");
    }
    
    std::unique_ptr<IRModule> module;
    IRFunction* function;
    BasicBlock* block;
};

// 🎯 Turkish String Optimization Tests
TEST_F(OptimizerAdvancedTest, TurkishStringConcatenation) {
    // Create Turkish string concatenation
    auto instr = std::make_unique<IRInstruction>(IROpcode::STR_CONCAT);
    instr->operands.push_back(IRValue{"Merhaba"});
    instr->operands.push_back(IRValue{"Dünya"});
    instr->result = "result";
    
    block->addInstruction(std::move(instr));
    
    TurkishStringOptimizationPass pass;
    bool modified = pass.runOnFunction(function);
    
    EXPECT_TRUE(modified);
    EXPECT_EQ(block->instructions[0]->opcode, IROpcode::LOAD);
    EXPECT_EQ(std::get<std::string>(block->instructions[0]->operands[0]), "MerhabaDünya");
}

TEST_F(OptimizerAdvancedTest, TurkishCaseConversion) {
    // Create Turkish case conversion call
    auto instr = std::make_unique<IRInstruction>(IROpcode::CALL_FUNC);
    instr->operands.push_back(IRValue{"buyukHarf"});
    instr->operands.push_back(IRValue{"istanbul"});
    instr->result = "result";
    
    block->addInstruction(std::move(instr));
    
    TurkishStringOptimizationPass pass;
    bool modified = pass.runOnFunction(function);
    
    EXPECT_TRUE(modified);
    EXPECT_EQ(block->instructions[0]->opcode, IROpcode::LOAD);
    EXPECT_EQ(std::get<std::string>(block->instructions[0]->operands[0]), "İSTANBUL");
}

// 🔥 Profile-Guided Optimization Tests
TEST_F(OptimizerAdvancedTest, ProfileGuidedOptimization) {
    ProfileGuidedOptimizationPass pass;
    
    // Simulate profile data
    pass.loadProfileData("test_profile.txt");
    
    // Add some instructions
    auto instr1 = std::make_unique<IRInstruction>(IROpcode::ADD);
    instr1->operands.push_back(IRValue{"a"});
    instr1->operands.push_back(IRValue{"b"});
    instr1->result = "c";
    
    block->addInstruction(std::move(instr1));
    
    bool modified = pass.runOnFunction(function);
    
    // Should not modify without profile data, but should run successfully
    EXPECT_FALSE(modified);
}

// ⚡ Parallel Optimization Tests
TEST_F(OptimizerAdvancedTest, ParallelOptimization) {
    // Create a simple loop-like structure
    auto block2 = function->createBlock("loop");
    
    // Add arithmetic instructions that could be parallelized
    auto instr1 = std::make_unique<IRInstruction>(IROpcode::ADD);
    instr1->operands.push_back(IRValue{"a"});
    instr1->operands.push_back(IRValue{"b"});
    instr1->result = "c";
    
    auto instr2 = std::make_unique<IRInstruction>(IROpcode::MUL);
    instr2->operands.push_back(IRValue{"d"});
    instr2->operands.push_back(IRValue{"e"});
    instr2->result = "f";
    
    auto instr3 = std::make_unique<IRInstruction>(IROpcode::ADD);
    instr3->operands.push_back(IRValue{"g"});
    instr3->operands.push_back(IRValue{"h"});
    instr3->result = "i";
    
    block2->addInstruction(std::move(instr1));
    block2->addInstruction(std::move(instr2));
    block2->addInstruction(std::move(instr3));
    
    // Create loop back edge
    block2->addSuccessor(block2);
    block2->addPredecessor(block2);
    
    ParallelOptimizationPass pass;
    bool modified = pass.runOnFunction(function);
    
    EXPECT_TRUE(modified);
    
    // Check if parallel hints were added
    bool foundParallelHint = false;
    for (const auto& instr : block2->instructions) {
        if (instr->comment.find("PARALLEL-CANDIDATE") != std::string::npos) {
            foundParallelHint = true;
            break;
        }
    }
    EXPECT_TRUE(foundParallelHint);
}

// 🎯 Memory Pool Optimization Tests
TEST_F(OptimizerAdvancedTest, MemoryPoolOptimization) {
    // Create multiple allocation instructions
    auto alloc1 = std::make_unique<IRInstruction>(IROpcode::ALLOC);
    alloc1->result = "ptr1";
    
    auto alloc2 = std::make_unique<IRInstruction>(IROpcode::ALLOC);
    alloc2->result = "ptr2";
    
    auto alloc3 = std::make_unique<IRInstruction>(IROpcode::ALLOC);
    alloc3->result = "ptr3";
    
    auto free1 = std::make_unique<IRInstruction>(IROpcode::FREE);
    free1->operands.push_back(IRValue{"ptr1"});
    
    block->addInstruction(std::move(alloc1));
    block->addInstruction(std::move(alloc2));
    block->addInstruction(std::move(alloc3));
    block->addInstruction(std::move(free1));
    
    MemoryPoolOptimizationPass pass;
    bool modified = pass.runOnFunction(function);
    
    EXPECT_TRUE(modified);
    
    // Check if pool candidates were marked
    bool foundPoolCandidate = false;
    for (const auto& instr : block->instructions) {
        if (instr->comment.find("POOL-CANDIDATE") != std::string::npos) {
            foundPoolCandidate = true;
            break;
        }
    }
    EXPECT_TRUE(foundPoolCandidate);
}

// 🚀 Optimization Level Tests
TEST_F(OptimizerAdvancedTest, OptimizationLevels) {
    // Test new optimization levels
    auto optimizer_ofast = Optimizer::createOptimizer(OptimizationLevel::Ofast);
    auto optimizer_og = Optimizer::createOptimizer(OptimizationLevel::Og);
    auto optimizer_oturk = Optimizer::createOptimizer(OptimizationLevel::Oturk);
    
    EXPECT_NE(optimizer_ofast, nullptr);
    EXPECT_NE(optimizer_og, nullptr);
    EXPECT_NE(optimizer_oturk, nullptr);
    
    // Add some instructions to test
    auto instr = std::make_unique<IRInstruction>(IROpcode::ADD);
    instr->operands.push_back(IRValue{1});
    instr->operands.push_back(IRValue{2});
    instr->result = "result";
    block->addInstruction(std::move(instr));
    
    // Test that optimizers can run without crashing
    EXPECT_NO_THROW(optimizer_ofast->runOnModule(module.get()));
    EXPECT_NO_THROW(optimizer_og->runOnModule(module.get()));
    EXPECT_NO_THROW(optimizer_oturk->runOnModule(module.get()));
}

// 📊 Statistics Tests
TEST_F(OptimizerAdvancedTest, OptimizationStatistics) {
    auto optimizer = Optimizer::createOptimizer(OptimizationLevel::O2);
    optimizer->setDebugMode(true);
    
    // Add some instructions
    auto instr1 = std::make_unique<IRInstruction>(IROpcode::ADD);
    instr1->operands.push_back(IRValue{1});
    instr1->operands.push_back(IRValue{0}); // Identity operation
    instr1->result = "result1";
    
    auto instr2 = std::make_unique<IRInstruction>(IROpcode::LOAD);
    instr2->operands.push_back(IRValue{42});
    instr2->result = "const1";
    
    block->addInstruction(std::move(instr1));
    block->addInstruction(std::move(instr2));
    
    bool modified = optimizer->runOnModule(module.get());
    auto stats = optimizer->getStatistics();
    
    EXPECT_TRUE(modified);
    EXPECT_GT(stats.totalPasses, 0);
    EXPECT_GE(stats.totalOptimizationTime, 0.0);
    EXPECT_GT(stats.codeSize, 0);
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}