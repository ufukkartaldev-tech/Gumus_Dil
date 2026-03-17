#ifndef ADVANCED_PASSES_H
#define ADVANCED_PASSES_H

#include "optimizer.h"

// 🚀 Türkçe Dil Özel Optimizasyonları

// 🎯 Turkish String Optimization Pass
class TurkishStringOptimizationPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "TurkishStringOptimization"; }
    
private:
    bool optimizeTurkishStringOperations(IRInstruction* instr);
    bool isTurkishStringConstant(const IRValue& value);
    void optimizeCharacterConversions(IRFunction* function);
};

// 🔥 Profile-Guided Optimization Pass
class ProfileGuidedOptimizationPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "ProfileGuidedOptimization"; }
    
    void loadProfileData(const std::string& profileFile);
    
private:
    struct ProfileData {
        std::unordered_map<std::string, int> functionCallCounts;
        std::unordered_map<std::string, double> branchProbabilities;
        std::unordered_map<std::string, int> loopIterationCounts;
    } profileData;
    
    void optimizeHotPaths(IRFunction* function);
    void reorderBasicBlocksByFrequency(IRFunction* function);
};

// ⚡ Parallel Optimization Pass
class ParallelOptimizationPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "ParallelOptimization"; }
    
private:
    struct ParallelizableLoop {
        BasicBlock* header;
        std::vector<IRInstruction*> parallelizableInstructions;
        int estimatedSpeedup;
    };
    
    std::vector<ParallelizableLoop> findParallelizableLoops(IRFunction* function);
    bool canParallelize(const std::vector<IRInstruction*>& instructions);
    void insertParallelDirectives(const ParallelizableLoop& loop);
};

// 🎯 Memory Pool Optimization Pass
class MemoryPoolOptimizationPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "MemoryPoolOptimization"; }
    
private:
    struct AllocationPattern {
        std::vector<IRInstruction*> allocations;
        std::vector<IRInstruction*> deallocations;
        size_t totalSize;
        int frequency;
    };
    
    std::vector<AllocationPattern> analyzeAllocationPatterns(IRFunction* function);
    void createMemoryPools(const std::vector<AllocationPattern>& patterns);
    void replaceAllocationsWithPoolAccess(IRFunction* function);
};

#endif // ADVANCED_PASSES_H