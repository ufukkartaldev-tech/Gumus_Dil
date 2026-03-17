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
}

void OptimizationManager::addAggressivePasses() {
    addStandardPasses();
    addPass(std::make_unique<LoopOptimizationPass>());
    addPass(std::make_unique<FunctionInliningPass>());
}

bool OptimizationManager::runOnModule(IRModule* module) {
    bool moduleModified = false;
    
    for (auto& pass : passes) {
        stats.totalPasses++;
        
        if (enableDebug) {
            std::cout << "Running pass: " << pass->getName() << std::endl;
        }
        
        bool passResult = pass->runOnModule(module);
        logPassResult(pass->getName(), passResult);
        
        if (passResult) {
            moduleModified = true;
            stats.successfulPasses++;
        }
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
            optimizer->addAggressivePasses();
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