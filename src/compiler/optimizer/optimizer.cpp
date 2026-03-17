#include "optimizer.h"
#include <iostream>
#include <algorithm>
#include <queue>

// 🔧 Dead Code Elimination Pass Implementation

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

// 🎯 Constant Folding Pass Implementation

bool ConstantFoldingPass::runOnFunction(IRFunction* function) {
    modified = false;
    
    for (auto& block : function->blocks) {
        for (auto& instr : block->instructions) {
            if (foldInstruction(instr.get())) {
                modified = true;
            }
        }
    }
    
    return modified;
}

bool ConstantFoldingPass::runOnModule(IRModule* module) {
    bool moduleModified = false;
    
    for (auto& function : module->functions) {
        if (runOnFunction(function.get())) {
            moduleModified = true;
        }
    }
    
    return moduleModified;
}

bool ConstantFoldingPass::foldInstruction(IRInstruction* instr) {
    // Only fold arithmetic and logical operations
    if (instr->operands.size() == 2) {
        const auto& lhs = instr->operands[0];
        const auto& rhs = instr->operands[1];
        
        if (isConstant(lhs) && isConstant(rhs)) {
            IRValue result = evaluateConstantExpression(instr->opcode, lhs, rhs);
            
            // Replace instruction with constant load
            instr->opcode = IROpcode::LOAD;
            instr->operands.clear();
            instr->operands.push_back(result);
            
            return true;
        }
    } else if (instr->operands.size() == 1) {
        const auto& operand = instr->operands[0];
        
        if (isConstant(operand)) {
            IRValue result = evaluateUnaryExpression(instr->opcode, operand);
            
            // Replace instruction with constant load
            instr->opcode = IROpcode::LOAD;
            instr->operands.clear();
            instr->operands.push_back(result);
            
            return true;
        }
    }
    
    return false;
}

bool ConstantFoldingPass::isConstant(const IRValue& value) {
    return std::holds_alternative<int>(value) || 
           std::holds_alternative<double>(value) || 
           std::holds_alternative<bool>(value);
}

IRValue ConstantFoldingPass::evaluateConstantExpression(IROpcode op, const IRValue& lhs, const IRValue& rhs) {
    // Handle integer operations
    if (std::holds_alternative<int>(lhs) && std::holds_alternative<int>(rhs)) {
        int l = std::get<int>(lhs);
        int r = std::get<int>(rhs);
        
        switch (op) {
            case IROpcode::ADD: return IRValue{l + r};
            case IROpcode::SUB: return IRValue{l - r};
            case IROpcode::MUL: return IRValue{l * r};
            case IROpcode::DIV: return r != 0 ? IRValue{l / r} : IRValue{0};
            case IROpcode::MOD: return r != 0 ? IRValue{l % r} : IRValue{0};
            case IROpcode::EQ: return IRValue{l == r};
            case IROpcode::NE: return IRValue{l != r};
            case IROpcode::LT: return IRValue{l < r};
            case IROpcode::LE: return IRValue{l <= r};
            case IROpcode::GT: return IRValue{l > r};
            case IROpcode::GE: return IRValue{l >= r};
            default: break;
        }
    }
    
    // Handle boolean operations
    if (std::holds_alternative<bool>(lhs) && std::holds_alternative<bool>(rhs)) {
        bool l = std::get<bool>(lhs);
        bool r = std::get<bool>(rhs);
        
        switch (op) {
            case IROpcode::AND: return IRValue{l && r};
            case IROpcode::OR: return IRValue{l || r};
            case IROpcode::EQ: return IRValue{l == r};
            case IROpcode::NE: return IRValue{l != r};
            default: break;
        }
    }
    
    return lhs; // Fallback
}

IRValue ConstantFoldingPass::evaluateUnaryExpression(IROpcode op, const IRValue& operand) {
    if (std::holds_alternative<int>(operand)) {
        int val = std::get<int>(operand);
        
        switch (op) {
            case IROpcode::SUB: return IRValue{-val}; // Negate
            default: break;
        }
    }
    
    if (std::holds_alternative<bool>(operand)) {
        bool val = std::get<bool>(operand);
        
        switch (op) {
            case IROpcode::NOT: return IRValue{!val};
            default: break;
        }
    }
    
    return operand; // Fallback
}

// 🔄 Copy Propagation Pass Implementation

bool CopyPropagationPass::runOnFunction(IRFunction* function) {
    modified = false;
    
    for (auto& block : function->blocks) {
        std::unordered_map<std::string, std::string> copyMap;
        propagateCopies(block.get(), copyMap);
    }
    
    return modified;
}

bool CopyPropagationPass::runOnModule(IRModule* module) {
    bool moduleModified = false;
    
    for (auto& function : module->functions) {
        if (runOnFunction(function.get())) {
            moduleModified = true;
        }
    }
    
    return moduleModified;
}

void CopyPropagationPass::propagateCopies(BasicBlock* block, std::unordered_map<std::string, std::string>& copyMap) {
    for (auto& instr : block->instructions) {
        // Update operands with known copies
        updateOperands(instr.get(), copyMap);
        
        // Check if this is a copy instruction
        if (isCopyInstruction(instr.get())) {
            std::string dest = instr->result;
            std::string src = std::get<std::string>(instr->operands[0]);
            
            // Add to copy map
            copyMap[dest] = src;
            modified = true;
        } else if (!instr->result.empty()) {
            // This instruction defines a variable, remove it from copy map
            copyMap.erase(instr->result);
        }
    }
}

bool CopyPropagationPass::isCopyInstruction(IRInstruction* instr) {
    return instr->opcode == IROpcode::LOAD && 
           instr->operands.size() == 1 && 
           std::holds_alternative<std::string>(instr->operands[0]) &&
           !instr->result.empty();
}

void CopyPropagationPass::updateOperands(IRInstruction* instr, const std::unordered_map<std::string, std::string>& copyMap) {
    for (auto& operand : instr->operands) {
        if (std::holds_alternative<std::string>(operand)) {
            std::string varName = std::get<std::string>(operand);
            auto it = copyMap.find(varName);
            if (it != copyMap.end()) {
                operand = IRValue{it->second};
                modified = true;
            }
        }
    }
}

// 🏗️ Common Subexpression Elimination Pass Implementation

bool CommonSubexpressionEliminationPass::ExpressionKey::operator==(const ExpressionKey& other) const {
    return opcode == other.opcode && operands == other.operands;
}

size_t CommonSubexpressionEliminationPass::ExpressionKeyHash::operator()(const ExpressionKey& key) const {
    size_t hash = std::hash<int>{}(static_cast<int>(key.opcode));
    for (const auto& operand : key.operands) {
        hash ^= std::hash<std::string>{}(operand) + 0x9e3779b9 + (hash << 6) + (hash >> 2);
    }
    return hash;
}

bool CommonSubexpressionEliminationPass::runOnFunction(IRFunction* function) {
    modified = false;
    
    for (auto& block : function->blocks) {
        eliminateCommonSubexpressions(block.get());
    }
    
    return modified;
}

bool CommonSubexpressionEliminationPass::runOnModule(IRModule* module) {
    bool moduleModified = false;
    
    for (auto& function : module->functions) {
        if (runOnFunction(function.get())) {
            moduleModified = true;
        }
    }
    
    return moduleModified;
}

void CommonSubexpressionEliminationPass::eliminateCommonSubexpressions(BasicBlock* block) {
    std::unordered_map<ExpressionKey, std::string, ExpressionKeyHash> expressionMap;
    
    for (auto& instr : block->instructions) {
        if (isEliminatable(instr.get())) {
            ExpressionKey key = getExpressionKey(instr.get());
            
            auto it = expressionMap.find(key);
            if (it != expressionMap.end()) {
                // Found common subexpression, replace with copy
                instr->opcode = IROpcode::LOAD;
                instr->operands.clear();
                instr->operands.push_back(IRValue{it->second});
                modified = true;
            } else {
                // Record this expression
                expressionMap[key] = instr->result;
            }
        }
    }
}

CommonSubexpressionEliminationPass::ExpressionKey CommonSubexpressionEliminationPass::getExpressionKey(IRInstruction* instr) {
    ExpressionKey key;
    key.opcode = instr->opcode;
    
    for (const auto& operand : instr->operands) {
        if (std::holds_alternative<std::string>(operand)) {
            key.operands.push_back(std::get<std::string>(operand));
        } else {
            // Convert other types to string representation
            key.operands.push_back("const");
        }
    }
    
    return key;
}

bool CommonSubexpressionEliminationPass::isEliminatable(IRInstruction* instr) {
    // Only eliminate pure arithmetic and logical operations
    return !instr->hasSideEffects() && !instr->isTerminator() && 
           (instr->opcode == IROpcode::ADD || instr->opcode == IROpcode::SUB ||
            instr->opcode == IROpcode::MUL || instr->opcode == IROpcode::DIV ||
            instr->opcode == IROpcode::AND || instr->opcode == IROpcode::OR ||
            instr->opcode == IROpcode::EQ || instr->opcode == IROpcode::NE ||
            instr->opcode == IROpcode::LT || instr->opcode == IROpcode::LE ||
            instr->opcode == IROpcode::GT || instr->opcode == IROpcode::GE);
}

// 🔀 Control Flow Optimization Pass Implementation

bool ControlFlowOptimizationPass::runOnFunction(IRFunction* function) {
    modified = false;
    
    // Run multiple optimization phases
    bool changed = true;
    while (changed) {
        changed = false;
        changed |= eliminateUnreachableBlocks(function);
        changed |= mergeBlocks(function);
        changed |= eliminateEmptyBlocks(function);
        changed |= simplifyBranches(function);
        
        if (changed) modified = true;
    }
    
    return modified;
}

bool ControlFlowOptimizationPass::runOnModule(IRModule* module) {
    bool moduleModified = false;
    
    for (auto& function : module->functions) {
        if (runOnFunction(function.get())) {
            moduleModified = true;
        }
    }
    
    return moduleModified;
}

bool ControlFlowOptimizationPass::eliminateUnreachableBlocks(IRFunction* function) {
    if (function->blocks.empty()) return false;
    
    std::unordered_set<BasicBlock*> reachable;
    std::queue<BasicBlock*> workList;
    
    // Start from entry block
    BasicBlock* entry = function->getEntryBlock();
    reachable.insert(entry);
    workList.push(entry);
    
    // Mark all reachable blocks
    while (!workList.empty()) {
        BasicBlock* current = workList.front();
        workList.pop();
        
        for (BasicBlock* successor : current->successors) {
            if (reachable.find(successor) == reachable.end()) {
                reachable.insert(successor);
                workList.push(successor);
            }
        }
    }
    
    // Remove unreachable blocks
    bool removed = false;
    auto it = function->blocks.begin();
    while (it != function->blocks.end()) {
        if (isUnreachable(it->get(), reachable)) {
            it = function->blocks.erase(it);
            removed = true;
        } else {
            ++it;
        }
    }
    
    return removed;
}

bool ControlFlowOptimizationPass::mergeBlocks(IRFunction* function) {
    bool merged = false;
    
    for (auto& block : function->blocks) {
        if (block->successors.size() == 1) {
            BasicBlock* successor = block->successors[0];
            
            if (canMergeBlocks(block.get(), successor)) {
                mergeBlockInstructions(block.get(), successor);
                
                // Update successors
                block->successors = successor->successors;
                
                // Update predecessor links
                for (BasicBlock* succ : successor->successors) {
                    for (auto& pred : succ->predecessors) {
                        if (pred == successor) {
                            pred = block.get();
                        }
                    }
                }
                
                // Remove merged block from function
                auto it = std::find_if(function->blocks.begin(), function->blocks.end(),
                    [successor](const std::unique_ptr<BasicBlock>& b) { return b.get() == successor; });
                if (it != function->blocks.end()) {
                    function->blocks.erase(it);
                }
                
                merged = true;
            }
        }
    }
    
    return merged;
}

bool ControlFlowOptimizationPass::eliminateEmptyBlocks(IRFunction* function) {
    bool eliminated = false;
    
    auto it = function->blocks.begin();
    while (it != function->blocks.end()) {
        BasicBlock* block = it->get();
        
        // Check if block is empty (only contains jump)
        if (block->instructions.size() == 1 && 
            block->instructions[0]->opcode == IROpcode::JMP &&
            block->successors.size() == 1) {
            
            BasicBlock* target = block->successors[0];
            
            // Redirect all predecessors to target
            for (BasicBlock* pred : block->predecessors) {
                for (auto& succ : pred->successors) {
                    if (succ == block) {
                        succ = target;
                    }
                }
                
                // Update jump instructions in predecessors
                for (auto& instr : pred->instructions) {
                    if ((instr->opcode == IROpcode::JMP || instr->opcode == IROpcode::JZ || instr->opcode == IROpcode::JNZ) &&
                        !instr->operands.empty() && std::holds_alternative<std::string>(instr->operands.back())) {
                        std::string label = std::get<std::string>(instr->operands.back());
                        if (label == block->label) {
                            instr->operands.back() = IRValue{target->label};
                        }
                    }
                }
            }
            
            // Update target's predecessors
            target->predecessors.erase(
                std::remove(target->predecessors.begin(), target->predecessors.end(), block),
                target->predecessors.end());
            
            for (BasicBlock* pred : block->predecessors) {
                if (std::find(target->predecessors.begin(), target->predecessors.end(), pred) == target->predecessors.end()) {
                    target->predecessors.push_back(pred);
                }
            }
            
            it = function->blocks.erase(it);
            eliminated = true;
        } else {
            ++it;
        }
    }
    
    return eliminated;
}

bool ControlFlowOptimizationPass::simplifyBranches(IRFunction* function) {
    bool simplified = false;
    
    for (auto& block : function->blocks) {
        for (auto& instr : block->instructions) {
            // Simplify conditional jumps with constant conditions
            if (instr->opcode == IROpcode::JZ || instr->opcode == IROpcode::JNZ) {
                if (instr->operands.size() >= 2 && std::holds_alternative<bool>(instr->operands[0])) {
                    bool condition = std::get<bool>(instr->operands[0]);
                    
                    if ((instr->opcode == IROpcode::JZ && !condition) ||
                        (instr->opcode == IROpcode::JNZ && condition)) {
                        // Always jump - convert to unconditional jump
                        instr->opcode = IROpcode::JMP;
                        instr->operands.erase(instr->operands.begin()); // Remove condition
                        simplified = true;
                    } else {
                        // Never jump - remove instruction
                        instr->opcode = IROpcode::NOP;
                        instr->operands.clear();
                        simplified = true;
                    }
                }
            }
        }
    }
    
    return simplified;
}

bool ControlFlowOptimizationPass::isUnreachable(BasicBlock* block, const std::unordered_set<BasicBlock*>& reachable) {
    return reachable.find(block) == reachable.end();
}

bool ControlFlowOptimizationPass::canMergeBlocks(BasicBlock* block1, BasicBlock* block2) {
    return block2->predecessors.size() == 1 && 
           block2->predecessors[0] == block1 &&
           !block1->instructions.empty() &&
           block1->instructions.back()->opcode == IROpcode::JMP;
}

void ControlFlowOptimizationPass::mergeBlockInstructions(BasicBlock* dest, BasicBlock* src) {
    // Remove the jump instruction from dest
    if (!dest->instructions.empty() && dest->instructions.back()->opcode == IROpcode::JMP) {
        dest->instructions.pop_back();
    }
    
    // Move all instructions from src to dest
    for (auto& instr : src->instructions) {
        dest->instructions.push_back(std::move(instr));
    }
    src->instructions.clear();
}

// 🎛️ Loop Optimization Pass Implementation

bool LoopOptimizationPass::runOnFunction(IRFunction* function) {
    modified = false;
    
    std::vector<Loop> loops = findLoops(function);
    
    for (const auto& loop : loops) {
        if (optimizeLoop(loop)) {
            modified = true;
        }
    }
    
    return modified;
}

bool LoopOptimizationPass::runOnModule(IRModule* module) {
    bool moduleModified = false;
    
    for (auto& function : module->functions) {
        if (runOnFunction(function.get())) {
            moduleModified = true;
        }
    }
    
    return moduleModified;
}

std::vector<LoopOptimizationPass::Loop> LoopOptimizationPass::findLoops(IRFunction* function) {
    std::vector<Loop> loops;
    
    // Simple loop detection - find back edges
    for (auto& block : function->blocks) {
        for (BasicBlock* successor : block->successors) {
            // Check if this is a back edge (successor dominates current block)
            // For simplicity, we'll use a heuristic: if successor appears earlier in the block list
            auto currentIt = std::find_if(function->blocks.begin(), function->blocks.end(),
                [&block](const std::unique_ptr<BasicBlock>& b) { return b.get() == block.get(); });
            auto successorIt = std::find_if(function->blocks.begin(), function->blocks.end(),
                [successor](const std::unique_ptr<BasicBlock>& b) { return b.get() == successor; });
            
            if (successorIt < currentIt) {
                // Found a potential loop
                Loop loop;
                loop.header = successor;
                loop.blocks.insert(successor);
                loop.blocks.insert(block.get());
                
                // Find all blocks in the loop (simplified)
                std::queue<BasicBlock*> workList;
                workList.push(block.get());
                
                while (!workList.empty()) {
                    BasicBlock* current = workList.front();
                    workList.pop();
                    
                    for (BasicBlock* pred : current->predecessors) {
                        if (loop.blocks.find(pred) == loop.blocks.end() && pred != successor) {
                            loop.blocks.insert(pred);
                            workList.push(pred);
                        }
                    }
                }
                
                loops.push_back(loop);
            }
        }
    }
    
    return loops;
}

bool LoopOptimizationPass::optimizeLoop(const Loop& loop) {
    bool optimized = false;
    
    optimized |= hoistInvariants(loop);
    optimized |= strengthReduction(loop);
    
    return optimized;
}

bool LoopOptimizationPass::hoistInvariants(const Loop& loop) {
    bool hoisted = false;
    
    // Find loop-invariant instructions and hoist them
    for (BasicBlock* block : loop.blocks) {
        if (block == loop.header) continue; // Don't hoist from header
        
        auto it = block->instructions.begin();
        while (it != block->instructions.end()) {
            if (isLoopInvariant(it->get(), loop) && canHoist(it->get(), loop)) {
                // Move instruction to preheader (simplified: move to header's first predecessor)
                if (!loop.header->predecessors.empty()) {
                    BasicBlock* preheader = loop.header->predecessors[0];
                    
                    // Insert before the last instruction (usually a jump)
                    auto insertPos = preheader->instructions.end();
                    if (!preheader->instructions.empty() && preheader->instructions.back()->isTerminator()) {
                        --insertPos;
                    }
                    
                    preheader->instructions.insert(insertPos, std::move(*it));
                    it = block->instructions.erase(it);
                    hoisted = true;
                }
            } else {
                ++it;
            }
        }
    }
    
    return hoisted;
}

bool LoopOptimizationPass::strengthReduction(const Loop& loop) {
    // Simplified strength reduction - convert multiplications by loop variables to additions
    bool reduced = false;
    
    for (BasicBlock* block : loop.blocks) {
        for (auto& instr : block->instructions) {
            if (instr->opcode == IROpcode::MUL && instr->operands.size() == 2) {
                // Check if one operand is a loop induction variable
                // This is a simplified implementation
                if (std::holds_alternative<std::string>(instr->operands[0]) ||
                    std::holds_alternative<std::string>(instr->operands[1])) {
                    // Could be optimized to use addition instead
                    // For now, just mark as potentially optimizable
                    instr->comment = "Strength reduction candidate";
                    reduced = true;
                }
            }
        }
    }
    
    return reduced;
}

bool LoopOptimizationPass::isLoopInvariant(IRInstruction* instr, const Loop& loop) {
    // An instruction is loop invariant if all its operands are defined outside the loop
    for (const auto& operand : instr->operands) {
        if (std::holds_alternative<std::string>(operand)) {
            std::string varName = std::get<std::string>(operand);
            
            // Check if this variable is defined inside the loop
            for (BasicBlock* block : loop.blocks) {
                for (const auto& blockInstr : block->instructions) {
                    if (blockInstr->result == varName) {
                        return false; // Defined inside loop
                    }
                }
            }
        }
    }
    
    return !instr->hasSideEffects(); // Must not have side effects
}

bool LoopOptimizationPass::canHoist(IRInstruction* instr, const Loop& loop) {
    return !instr->hasSideEffects() && !instr->isTerminator();
}

// 🎯 Function Inlining Pass Implementation

bool FunctionInliningPass::runOnFunction(IRFunction* function) {
    modified = false;
    
    for (auto& block : function->blocks) {
        auto it = block->instructions.begin();
        while (it != block->instructions.end()) {
            if ((*it)->opcode == IROpcode::CALL_FUNC && (*it)->operands.size() > 0 &&
                std::holds_alternative<std::string>((*it)->operands[0])) {
                
                std::string calleeName = std::get<std::string>((*it)->operands[0]);
                
                // Find the callee function (simplified - would need module context)
                // For now, just check if it should be inlined based on heuristics
                if (calleeName.length() < 10) { // Simple heuristic
                    (*it)->comment = "Inline candidate: " + calleeName;
                    modified = true;
                }
            }
            ++it;
        }
    }
    
    return modified;
}

bool FunctionInliningPass::runOnModule(IRModule* module) {
    bool moduleModified = false;
    
    for (auto& function : module->functions) {
        for (auto& block : function->blocks) {
            auto it = block->instructions.begin();
            while (it != block->instructions.end()) {
                if ((*it)->opcode == IROpcode::CALL_FUNC && (*it)->operands.size() > 0 &&
                    std::holds_alternative<std::string>((*it)->operands[0])) {
                    
                    std::string calleeName = std::get<std::string>((*it)->operands[0]);
                    IRFunction* callee = module->getFunction(calleeName);
                    
                    if (callee && shouldInline(callee, it->get())) {
                        inlineFunction(function.get(), it->get(), callee);
                        it = block->instructions.erase(it);
                        moduleModified = true;
                    } else {
                        ++it;
                    }
                } else {
                    ++it;
                }
            }
        }
    }
    
    return moduleModified;
}

bool FunctionInliningPass::shouldInline(IRFunction* callee, IRInstruction* callSite) {
    if (hasRecursiveCall(callee)) return false;
    
    int cost = calculateInstructionCost(callee);
    return cost <= inlineThreshold;
}

void FunctionInliningPass::inlineFunction(IRFunction* caller, IRInstruction* callSite, IRFunction* callee) {
    // Simplified inlining - just add a comment for now
    // Full implementation would copy callee's instructions and handle variable renaming
    callSite->comment = "Inlined: " + callee->name;
}

int FunctionInliningPass::calculateInstructionCost(IRFunction* function) {
    int cost = 0;
    for (const auto& block : function->blocks) {
        cost += block->instructions.size();
    }
    return cost;
}

bool FunctionInliningPass::hasRecursiveCall(IRFunction* function) {
    for (const auto& block : function->blocks) {
        for (const auto& instr : block->instructions) {
            if (instr->opcode == IROpcode::CALL_FUNC && instr->operands.size() > 0 &&
                std::holds_alternative<std::string>(instr->operands[0])) {
                std::string calleeName = std::get<std::string>(instr->operands[0]);
                if (calleeName == function->name) {
                    return true;
                }
            }
        }
    }
    return false;
}

// 🚀 Optimization Manager Implementation

OptimizationManager::OptimizationManager() {
    resetStatistics();
}

void OptimizationManager::addPass(std::unique_ptr<OptimizationPass> pass) {
    passes.push_back(std::move(pass));
}

void OptimizationManager::addStandardPasses() {
    addPass(std::make_unique<DeadCodeEliminationPass>());
    addPass(std::make_unique<ConstantFoldingPass>());
    addPass(std::make_unique<CopyPropagationPass>());
    addPass(std::make_unique<CommonSubexpressionEliminationPass>());
    addPass(std::make_unique<ControlFlowOptimizationPass>());
    addPass(std::make_unique<PeepholeOptimizationPass>());
}

void OptimizationManager::addAggressivePasses() {
    addStandardPasses();
    addPass(std::make_unique<LoopOptimizationPass>());
    addPass(std::make_unique<FunctionInliningPass>());
    addPass(std::make_unique<RegisterAllocationPass>());
}

void OptimizationManager::addPerformancePasses() {
    addAggressivePasses();
    addPass(std::make_unique<VectorizationPass>());
    addPass(std::make_unique<CacheOptimizationPass>());
    addPass(std::make_unique<BranchPredictionPass>());
    addPass(std::make_unique<InstructionSchedulingPass>());
    addPass(std::make_unique<MemoryLayoutPass>());
    addPass(std::make_unique<MemoryPoolOptimizationPass>());
}

bool OptimizationManager::runOnModule(IRModule* module) {
    bool moduleModified = false;
    auto startTime = std::chrono::high_resolution_clock::now();
    
    // Calculate initial code size
    stats.codeSize = 0;
    for (const auto& function : module->functions) {
        for (const auto& block : function->blocks) {
            stats.codeSize += block->instructions.size();
        }
    }
    
    for (auto& pass : passes) {
        stats.totalPasses++;
        
        if (enableDebug) {
            std::cout << "Running pass: " << pass->getName() << std::endl;
        }
        
        auto passStartTime = std::chrono::high_resolution_clock::now();
        bool passResult = pass->runOnModule(module);
        auto passEndTime = std::chrono::high_resolution_clock::now();
        
        auto passTime = std::chrono::duration<double>(passEndTime - passStartTime).count();
        stats.passExecutionTimes[pass->getName()] = passTime;
        
        logPassResult(pass->getName(), passResult);
        
        if (passResult) {
            moduleModified = true;
            stats.successfulPasses++;
        }
    }
    
    // Calculate optimized code size
    stats.optimizedCodeSize = 0;
    for (const auto& function : module->functions) {
        for (const auto& block : function->blocks) {
            stats.optimizedCodeSize += block->instructions.size();
        }
    }
    
    auto endTime = std::chrono::high_resolution_clock::now();
    stats.totalOptimizationTime = std::chrono::duration<double>(endTime - startTime).count();
    
    if (enableDebug) {
        std::cout << "Optimization completed in " << stats.totalOptimizationTime << " seconds" << std::endl;
        std::cout << "Code size: " << stats.codeSize << " -> " << stats.optimizedCodeSize 
                  << " (" << (100.0 * (stats.codeSize - stats.optimizedCodeSize) / stats.codeSize) << "% reduction)" << std::endl;
    }
    
    return moduleModified;
}

bool OptimizationManager::runOnFunction(IRFunction* function) {
    bool functionModified = false;
    
    for (auto& pass : passes) {
        stats.totalPasses++;
        
        if (enableDebug) {
            std::cout << "Running pass: " << pass->getName() << " on function: " << function->name << std::endl;
        }
        
        bool passResult = pass->runOnFunction(function);
        logPassResult(pass->getName(), passResult);
        
        if (passResult) {
            functionModified = true;
            stats.successfulPasses++;
        }
    }
    
    return functionModified;
}

void OptimizationManager::logPassResult(const std::string& passName, bool result) {
    stats.passRunCounts[passName]++;
    stats.passResults[passName] = result;
}

// 🎯 High-level optimization interface

std::unique_ptr<OptimizationManager> Optimizer::createOptimizer(OptimizationLevel level) {
    auto optimizer = std::make_unique<OptimizationManager>();
    
    switch (level) {
        case OptimizationLevel::O0:
            // No optimizations
            break;
            
        case OptimizationLevel::O1:
            optimizer->addPass(std::make_unique<DeadCodeEliminationPass>());
            optimizer->addPass(std::make_unique<ConstantFoldingPass>());
            break;
            
        case OptimizationLevel::O2:
            optimizer->addStandardPasses();
            break;
            
        case OptimizationLevel::O3:
            optimizer->addPerformancePasses(); // 🚀 En agresif performans optimizasyonları
            break;
            
        case OptimizationLevel::Ofast:
            optimizer->addPerformancePasses();
            optimizer->addPass(std::make_unique<ProfileGuidedOptimizationPass>());
            optimizer->addPass(std::make_unique<ParallelOptimizationPass>());
            break;
            
        case OptimizationLevel::Og:
            // Debug-friendly optimizations
            optimizer->addPass(std::make_unique<DeadCodeEliminationPass>());
            optimizer->addPass(std::make_unique<ConstantFoldingPass>());
            break;
            
        case OptimizationLevel::Oturk:
            optimizer->addStandardPasses();
            optimizer->addPass(std::make_unique<TurkishStringOptimizationPass>());
            break;
            
        case OptimizationLevel::Os:
        case OptimizationLevel::Oz:
            // Size optimizations (similar to O2 for now)
            optimizer->addStandardPasses();
            break;
    }
    
    return optimizer;
}

bool Optimizer::optimizeModule(IRModule* module, OptimizationLevel level) {
    auto optimizer = createOptimizer(level);
    return optimizer->runOnModule(module);
}

bool Optimizer::optimizeFunction(IRFunction* function, OptimizationLevel level) {
    auto optimizer = createOptimizer(level);
    return optimizer->runOnFunction(function);
}

// 🚀 Register Allocation Optimization Pass
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

bool RegisterAllocationPass::runOnFunction(IRFunction* function) {
    modified = false;
    
    auto liveRanges = computeLiveRanges(function);
    allocateRegisters(function, liveRanges);
    
    return modified;
}

bool RegisterAllocationPass::runOnModule(IRModule* module) {
    bool moduleModified = false;
    
    for (auto& function : module->functions) {
        if (runOnFunction(function.get())) {
            moduleModified = true;
        }
    }
    
    return moduleModified;
}

std::vector<RegisterAllocationPass::LiveRange> RegisterAllocationPass::computeLiveRanges(IRFunction* function) {
    std::vector<LiveRange> ranges;
    std::unordered_map<std::string, int> firstUse;
    std::unordered_map<std::string, int> lastUse;
    
    int instructionIndex = 0;
    
    // Compute first and last use for each variable
    for (const auto& block : function->blocks) {
        for (const auto& instr : block->instructions) {
            // Check operands (uses)
            for (const auto& operand : instr->operands) {
                if (std::holds_alternative<std::string>(operand)) {
                    std::string var = std::get<std::string>(operand);
                    if (firstUse.find(var) == firstUse.end()) {
                        firstUse[var] = instructionIndex;
                    }
                    lastUse[var] = instructionIndex;
                }
            }
            
            // Check result (definition)
            if (!instr->result.empty()) {
                if (firstUse.find(instr->result) == firstUse.end()) {
                    firstUse[instr->result] = instructionIndex;
                }
                lastUse[instr->result] = instructionIndex;
            }
            
            instructionIndex++;
        }
    }
    
    // Create live ranges
    for (const auto& pair : firstUse) {
        LiveRange range;
        range.variable = pair.first;
        range.start = pair.second;
        range.end = lastUse[pair.first];
        range.spillCost = range.end - range.start; // Simple heuristic
        ranges.push_back(range);
    }
    
    return ranges;
}

void RegisterAllocationPass::allocateRegisters(IRFunction* function, const std::vector<LiveRange>& liveRanges) {
    const int NUM_REGISTERS = 8; // Assume 8 available registers
    std::vector<std::string> registers = {"r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7"};
    std::vector<bool> registerUsed(NUM_REGISTERS, false);
    std::unordered_map<std::string, std::string> allocation;
    
    // Sort live ranges by start time
    auto sortedRanges = liveRanges;
    std::sort(sortedRanges.begin(), sortedRanges.end(),
        [](const LiveRange& a, const LiveRange& b) { return a.start < b.start; });
    
    for (const auto& range : sortedRanges) {
        bool allocated = false;
        
        // Try to find a free register
        for (int i = 0; i < NUM_REGISTERS; i++) {
            if (!registerUsed[i]) {
                // Check if this register conflicts with any allocated range
                bool conflicts = false;
                for (const auto& otherRange : sortedRanges) {
                    if (otherRange.variable != range.variable && 
                        allocation.find(otherRange.variable) != allocation.end() &&
                        allocation[otherRange.variable] == registers[i] &&
                        interfere(range, otherRange)) {
                        conflicts = true;
                        break;
                    }
                }
                
                if (!conflicts) {
                    allocation[range.variable] = registers[i];
                    registerUsed[i] = true;
                    allocated = true;
                    break;
                }
            }
        }
        
        if (!allocated) {
            // Need to spill
            insertSpillCode(function, range.variable);
        }
    }
    
    // Update instructions with register assignments
    for (auto& block : function->blocks) {
        for (auto& instr : block->instructions) {
            // Update operands
            for (auto& operand : instr->operands) {
                if (std::holds_alternative<std::string>(operand)) {
                    std::string var = std::get<std::string>(operand);
                    if (allocation.find(var) != allocation.end()) {
                        operand = IRValue{allocation[var]};
                        modified = true;
                    }
                }
            }
            
            // Update result
            if (!instr->result.empty() && allocation.find(instr->result) != allocation.end()) {
                instr->result = allocation[instr->result];
                modified = true;
            }
        }
    }
}

bool RegisterAllocationPass::interfere(const LiveRange& a, const LiveRange& b) {
    return !(a.end < b.start || b.end < a.start);
}

void RegisterAllocationPass::insertSpillCode(IRFunction* function, const std::string& variable) {
    // Insert spill/reload instructions (simplified)
    for (auto& block : function->blocks) {
        for (auto it = block->instructions.begin(); it != block->instructions.end(); ++it) {
            // Check if instruction uses the spilled variable
            bool usesVariable = false;
            for (const auto& operand : (*it)->operands) {
                if (std::holds_alternative<std::string>(operand) && 
                    std::get<std::string>(operand) == variable) {
                    usesVariable = true;
                    break;
                }
            }
            
            if (usesVariable) {
                // Insert reload before use
                auto reloadInstr = std::make_unique<IRInstruction>(IROpcode::LOAD);
                reloadInstr->operands.push_back(IRValue{"spill_" + variable});
                reloadInstr->result = variable + "_temp";
                reloadInstr->comment = "Reload spilled variable";
                
                it = block->instructions.insert(it, std::move(reloadInstr));
                ++it; // Skip the inserted instruction
                modified = true;
            }
            
            // Check if instruction defines the spilled variable
            if ((*it)->result == variable) {
                // Insert spill after definition
                auto spillInstr = std::make_unique<IRInstruction>(IROpcode::STORE);
                spillInstr->operands.push_back(IRValue{variable});
                spillInstr->operands.push_back(IRValue{"spill_" + variable});
                spillInstr->comment = "Spill variable to memory";
                
                ++it;
                it = block->instructions.insert(it, std::move(spillInstr));
                modified = true;
            }
        }
    }
}

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

bool PeepholeOptimizationPass::runOnFunction(IRFunction* function) {
    modified = false;
    
    for (auto& block : function->blocks) {
        for (size_t i = 0; i < block->instructions.size(); i++) {
            if (optimizeInstructionSequence(block->instructions, i)) {
                modified = true;
            }
        }
    }
    
    return modified;
}

bool PeepholeOptimizationPass::runOnModule(IRModule* module) {
    bool moduleModified = false;
    
    for (auto& function : module->functions) {
        if (runOnFunction(function.get())) {
            moduleModified = true;
        }
    }
    
    return moduleModified;
}

bool PeepholeOptimizationPass::optimizeInstructionSequence(std::vector<std::unique_ptr<IRInstruction>>& instructions, size_t start) {
    if (start >= instructions.size()) return false;
    
    IRInstruction* instr = instructions[start].get();
    
    // Remove identity operations (x = x + 0, x = x * 1, etc.)
    if (isIdentityOperation(instr)) {
        instructions.erase(instructions.begin() + start);
        return true;
    }
    
    // Optimize load-store pairs
    if (start + 1 < instructions.size()) {
        IRInstruction* nextInstr = instructions[start + 1].get();
        
        if (isRedundantLoadStore(instr, nextInstr)) {
            instructions.erase(instructions.begin() + start, instructions.begin() + start + 2);
            return true;
        }
        
        // Optimize arithmetic chains: x = a + b; y = x + c -> y = a + b + c
        if (instr->opcode == IROpcode::ADD && nextInstr->opcode == IROpcode::ADD &&
            !instr->result.empty() && nextInstr->operands.size() > 0 &&
            std::holds_alternative<std::string>(nextInstr->operands[0]) &&
            std::get<std::string>(nextInstr->operands[0]) == instr->result) {
            
            // Combine the operations
            nextInstr->operands[0] = instr->operands[0];
            nextInstr->comment = "Combined arithmetic operations";
            instructions.erase(instructions.begin() + start);
            return true;
        }
    }
    
    return false;
}

bool PeepholeOptimizationPass::isRedundantLoadStore(IRInstruction* load, IRInstruction* store) {
    return load->opcode == IROpcode::LOAD && store->opcode == IROpcode::STORE &&
           load->operands.size() > 0 && store->operands.size() > 1 &&
           std::holds_alternative<std::string>(load->operands[0]) &&
           std::holds_alternative<std::string>(store->operands[1]) &&
           std::get<std::string>(load->operands[0]) == std::get<std::string>(store->operands[1]) &&
           store->operands[0] == IRValue{load->result};
}

bool PeepholeOptimizationPass::isIdentityOperation(IRInstruction* instr) {
    if (instr->operands.size() != 2) return false;
    
    // Check for x + 0, x - 0
    if ((instr->opcode == IROpcode::ADD || instr->opcode == IROpcode::SUB) &&
        std::holds_alternative<int>(instr->operands[1]) &&
        std::get<int>(instr->operands[1]) == 0) {
        return true;
    }
    
    // Check for x * 1, x / 1
    if ((instr->opcode == IROpcode::MUL || instr->opcode == IROpcode::DIV) &&
        std::holds_alternative<int>(instr->operands[1]) &&
        std::get<int>(instr->operands[1]) == 1) {
        return true;
    }
    
    return false;
}