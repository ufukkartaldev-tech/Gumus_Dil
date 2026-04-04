#pragma once
#include "optimizer.h"

namespace gumus {
namespace compiler {
namespace optimizer {

/**
 * Dead Code Elimination Pass
 * Removes unreachable and unused code
 */
class DeadCodeEliminationPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    
    const char* getName() const override { return "DeadCodeElimination"; }

private:
    bool modified = false;
    
    void markLiveInstructions(IRFunction* function, std::unordered_set<IRInstruction*>& liveSet);
    void removeDeadInstructions(IRFunction* function, const std::unordered_set<IRInstruction*>& liveSet);
};

} // namespace optimizer
} // namespace compiler  
} // namespace gumus