#ifndef OPTIMIZER_H
#define OPTIMIZER_H

#include "../ir/ir_instruction.h"
#include <unordered_set>
#include <unordered_map>

// 🚀 IR Optimization Framework

// Base class for all optimization passes
class OptimizationPass {
public:
    virtual ~OptimizationPass() = default;
    virtual bool runOnFunction(IRFunction* function) = 0;
    virtual bool runOnModule(IRModule* module) = 0;
    virtual std::string getName() const = 0;
    
protected:
    bool modified = false;
};

// 🔧 Dead Code Elimination Pass
class DeadCodeEliminationPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "DeadCodeElimination"; }
    
private:
    void markLiveInstructions(IRFunction* function, std::unordered_set<IRInstruction*>& liveSet);
    void removeDeadInstructions(IRFunction* function, const std::unordered_set<IRInstruction*>& liveSet);
    bool hasLiveUses(IRInstruction* instr, const std::unordered_set<IRInstruction*>& liveSet);
};

// 🎯 Constant Folding Pass
class ConstantFoldingPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "ConstantFolding"; }
    
private:
    bool foldInstruction(IRInstruction* instr);
    bool isConstant(const IRValue& value);
    IRValue evaluateConstantExpression(IROpcode op, const IRValue& lhs, const IRValue& rhs);
    IRValue evaluateUnaryExpression(IROpcode op, const IRValue& operand);
};

// 🔄 Copy Propagation Pass
class CopyPropagationPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "CopyPropagation"; }
    
private:
    void propagateCopies(BasicBlock* block, std::unordered_map<std::string, std::string>& copyMap);
    bool isCopyInstruction(IRInstruction* instr);
    void updateOperands(IRInstruction* instr, const std::unordered_map<std::string, std::string>& copyMap);
};

// 🏗️ Common Subexpression Elimination Pass
class CommonSubexpressionEliminationPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "CommonSubexpressionElimination"; }
    
private:
    struct ExpressionKey {
        IROpcode opcode;
        std::vector<std::string> operands;
        
        bool operator==(const ExpressionKey& other) const;
    };
    
    struct ExpressionKeyHash {
        size_t operator()(const ExpressionKey& key) const;
    };
    
    void eliminateCommonSubexpressions(BasicBlock* block);
    ExpressionKey getExpressionKey(IRInstruction* instr);
    bool isEliminatable(IRInstruction* instr);
};

// 🔀 Control Flow Optimization Pass
class ControlFlowOptimizationPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "ControlFlowOptimization"; }
    
private:
    bool eliminateUnreachableBlocks(IRFunction* function);
    bool mergeBlocks(IRFunction* function);
    bool eliminateEmptyBlocks(IRFunction* function);
    bool simplifyBranches(IRFunction* function);
    
    bool isUnreachable(BasicBlock* block, const std::unordered_set<BasicBlock*>& reachable);
    bool canMergeBlocks(BasicBlock* block1, BasicBlock* block2);
    void mergeBlockInstructions(BasicBlock* dest, BasicBlock* src);
};

// 🎛️ Loop Optimization Pass
class LoopOptimizationPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "LoopOptimization"; }
    
private:
    struct Loop {
        BasicBlock* header;
        std::unordered_set<BasicBlock*> blocks;
        std::vector<BasicBlock*> exits;
    };
    
    std::vector<Loop> findLoops(IRFunction* function);
    bool optimizeLoop(const Loop& loop);
    bool hoistInvariants(const Loop& loop);
    bool strengthReduction(const Loop& loop);
    
    bool isLoopInvariant(IRInstruction* instr, const Loop& loop);
    bool canHoist(IRInstruction* instr, const Loop& loop);
};

// 🎯 Function Inlining Pass
class FunctionInliningPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "FunctionInlining"; }
    
    void setInlineThreshold(int threshold) { inlineThreshold = threshold; }
    
private:
    int inlineThreshold = 50; // Maximum instructions to inline
    
    bool shouldInline(IRFunction* callee, IRInstruction* callSite);
    void inlineFunction(IRFunction* caller, IRInstruction* callSite, IRFunction* callee);
    int calculateInstructionCost(IRFunction* function);
    bool hasRecursiveCall(IRFunction* function);
};

// 🚀 Register Allocation Pass
class RegisterAllocationPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "RegisterAllocation"; }
    
private:
    struct LiveRange {
        std::string variable;
        int start;
        int end;
        int spillCost;
    };
    
    std::vector<LiveRange> computeLiveRanges(IRFunction* function);
    void allocateRegisters(IRFunction* function, const std::vector<LiveRange>& liveRanges);
    bool interfere(const LiveRange& a, const LiveRange& b);
    void insertSpillCode(IRFunction* function, const std::string& variable);
};

// 🎯 Peephole Optimization Pass
class PeepholeOptimizationPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "PeepholeOptimization"; }
    
private:
    bool optimizeInstructionSequence(std::vector<std::unique_ptr<IRInstruction>>& instructions, size_t start);
    bool isRedundantLoadStore(IRInstruction* load, IRInstruction* store);
    bool isIdentityOperation(IRInstruction* instr);
};

// 🚀 Advanced Performance Optimization Passes

// 🎯 Vectorization Pass
class VectorizationPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "Vectorization"; }
    
private:
    struct VectorizableLoop {
        BasicBlock* header;
        std::vector<IRInstruction*> vectorizableInstructions;
        int vectorWidth;
    };
    
    std::vector<VectorizableLoop> findVectorizableLoops(IRFunction* function);
    bool canVectorize(IRInstruction* instr);
    void vectorizeLoop(const VectorizableLoop& loop);
};

// 🔥 Cache Optimization Pass
class CacheOptimizationPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "CacheOptimization"; }
    
private:
    void optimizeMemoryAccess(IRFunction* function);
    void reorderInstructions(BasicBlock* block);
    bool isMemoryAccess(IRInstruction* instr);
    int getMemoryAccessStride(IRInstruction* instr);
};

// ⚡ Branch Prediction Optimization Pass
class BranchPredictionPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "BranchPrediction"; }
    
private:
    void optimizeBranchLayout(IRFunction* function);
    void reorderBasicBlocks(IRFunction* function);
    double calculateBranchProbability(BasicBlock* block);
};

// 🎯 Instruction Scheduling Pass
class InstructionSchedulingPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "InstructionScheduling"; }
    
private:
    struct InstructionNode {
        IRInstruction* instruction;
        std::vector<InstructionNode*> dependencies;
        int latency;
        int earliestStart;
    };
    
    void scheduleBasicBlock(BasicBlock* block);
    std::vector<InstructionNode> buildDependencyGraph(BasicBlock* block);
    void listScheduling(std::vector<InstructionNode>& nodes);
    int getInstructionLatency(IRInstruction* instr);
};

// 🚀 Memory Layout Optimization Pass
class MemoryLayoutPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    std::string getName() const override { return "MemoryLayout"; }
    
private:
    void optimizeVariableLayout(IRFunction* function);
    void groupRelatedVariables(IRFunction* function);
    void alignMemoryAccesses(IRFunction* function);
};

// 🚀 Optimization Manager
class OptimizationManager {
private:
    std::vector<std::unique_ptr<OptimizationPass>> passes;
    bool enableDebug = false;
    
public:
    OptimizationManager();
    ~OptimizationManager() = default;
    
    // Pass management
    void addPass(std::unique_ptr<OptimizationPass> pass);
    void addStandardPasses();
    void addAggressivePasses();
    void addPerformancePasses(); // 🚀 Yeni performans optimizasyonları
    
    // Optimization execution
    bool runOnModule(IRModule* module);
    bool runOnFunction(IRFunction* function);
    
    // Configuration
    void setDebugMode(bool debug) { enableDebug = debug; }
    void clearPasses() { passes.clear(); }
    
    // Statistics
    struct OptimizationStats {
        int totalPasses = 0;
        int successfulPasses = 0;
        std::unordered_map<std::string, int> passRunCounts;
        std::unordered_map<std::string, bool> passResults;
        std::unordered_map<std::string, double> passExecutionTimes;
        int instructionsEliminated = 0;
        int constantsFolded = 0;
        int loopsOptimized = 0;
        double totalOptimizationTime = 0.0;
        size_t codeSize = 0;
        size_t optimizedCodeSize = 0;
    };
    
    OptimizationStats getStatistics() const { return stats; }
    void resetStatistics() { stats = OptimizationStats{}; }
    
private:
    OptimizationStats stats;
    void logPassResult(const std::string& passName, bool result);
};

// 🎯 Optimization Levels
enum class OptimizationLevel {
    O0, // No optimization
    O1, // Basic optimizations
    O2, // Standard optimizations
    O3, // Aggressive optimizations
    Os, // Size optimizations
    Oz, // Aggressive size optimizations
    Ofast, // Maximum performance (unsafe optimizations)
    Og, // Debug-friendly optimizations
    Oturk // Turkish language specific optimizations
};

// 🚀 High-level optimization interface
class Optimizer {
public:
    static std::unique_ptr<OptimizationManager> createOptimizer(OptimizationLevel level);
    static bool optimizeModule(IRModule* module, OptimizationLevel level = OptimizationLevel::O2);
    static bool optimizeFunction(IRFunction* function, OptimizationLevel level = OptimizationLevel::O2);
};

#endif // OPTIMIZER_H