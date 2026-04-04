#include "dead_code_elimination.h"
#include <iostream>
#include <algorithm>
#include <queue>

namespace gumus {
namespace compiler {
namespace optimizer {

bool DeadCodeEliminationPass::runOnFunction(IRFunction* function) {
    modified = false;
    
    std::unordered_set<IRInstruction*> liveSet;
    
    // Mark live instructions
    markLiveInstructions(function, liveSet);
    
    // Remove dead instructions
    removeDeadInstructions(function, liveSet);
    
    return modified;
}

bool DeadCodeEliminationPass::runOnModule(IRModule* module) {
    bool moduleModified = false;
    
    for (auto& function : module->functions) {
        if (runOnFunction(function.get())) {
            moduleModified = true;
        }
    }
    
    return moduleModified;
}

void DeadCodeEliminationPass::markLiveInstructions(IRFunction* function, std::unordered_set<IRInstruction*>& liveSet) {
    std::queue<IRInstruction*> workList;
    
    // Mark all instructions with side effects as live
    for (auto& block : function->blocks) {
        for (auto& instr : block->instructions) {
            if (instr->hasSideEffects() || instr->isTerminator()) {
                liveSet.insert(instr.get());
                workList.push(instr.get());
            }
        }
    }
    
    // Propagate liveness backwards
    while (!workList.empty()) {
        IRInstruction* liveInstr = workList.front();
        workList.pop();
        
        // Mark operands as live
        for (const auto& operand : liveInstr->operands) {
            if (std::holds_alternative<std::string>(operand)) {
                std::string varName = std::get<std::string>(operand);
                
                // Find the instruction that defines this variable
                for (auto& block : function->blocks) {
                    for (auto& instr : block->instructions) {
                        if (instr->result == varName && liveSet.find(instr.get()) == liveSet.end()) {
                            liveSet.insert(instr.get());
                            workList.push(instr.get());
                        }
                    }
                }
            }
        }
    }
}

void DeadCodeEliminationPass::removeDeadInstructions(IRFunction* function, const std::unordered_set<IRInstruction*>& liveSet) {
    for (auto& block : function->blocks) {
        auto it = block->instructions.begin();
        while (it != block->instructions.end()) {
            if (liveSet.find(it->get()) == liveSet.end()) {
                it = block->instructions.erase(it);
                modified = true;
            } else {
                ++it;
            }
        }
    }
}

} // namespace optimizer
} // namespace compiler  
} // namespace gumus