#include "constant_folding.h"
#include <iostream>

namespace gumus {
namespace compiler {
namespace optimizer {

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

IRValue ConstantFoldingPass::evaluateConstantExpression(IROpcode opcode, const IRValue& lhs, const IRValue& rhs) {
    // Handle integer operations
    if (std::holds_alternative<int>(lhs) && std::holds_alternative<int>(rhs)) {
        int left = std::get<int>(lhs);
        int right = std::get<int>(rhs);
        
        switch (opcode) {
            case IROpcode::ADD: return left + right;
            case IROpcode::SUB: return left - right;
            case IROpcode::MUL: return left * right;
            case IROpcode::DIV: return (right != 0) ? left / right : left;
            case IROpcode::MOD: return (right != 0) ? left % right : left;
            case IROpcode::EQ: return left == right;
            case IROpcode::NE: return left != right;
            case IROpcode::LT: return left < right;
            case IROpcode::LE: return left <= right;
            case IROpcode::GT: return left > right;
            case IROpcode::GE: return left >= right;
            default: break;
        }
    }
    
    // Handle double operations
    if (std::holds_alternative<double>(lhs) && std::holds_alternative<double>(rhs)) {
        double left = std::get<double>(lhs);
        double right = std::get<double>(rhs);
        
        switch (opcode) {
            case IROpcode::ADD: return left + right;
            case IROpcode::SUB: return left - right;
            case IROpcode::MUL: return left * right;
            case IROpcode::DIV: return (right != 0.0) ? left / right : left;
            case IROpcode::EQ: return left == right;
            case IROpcode::NE: return left != right;
            case IROpcode::LT: return left < right;
            case IROpcode::LE: return left <= right;
            case IROpcode::GT: return left > right;
            case IROpcode::GE: return left >= right;
            default: break;
        }
    }
    
    // Handle boolean operations
    if (std::holds_alternative<bool>(lhs) && std::holds_alternative<bool>(rhs)) {
        bool left = std::get<bool>(lhs);
        bool right = std::get<bool>(rhs);
        
        switch (opcode) {
            case IROpcode::AND: return left && right;
            case IROpcode::OR: return left || right;
            case IROpcode::EQ: return left == right;
            case IROpcode::NE: return left != right;
            default: break;
        }
    }
    
    // Return original value if can't fold
    return lhs;
}

IRValue ConstantFoldingPass::evaluateUnaryExpression(IROpcode opcode, const IRValue& operand) {
    if (std::holds_alternative<int>(operand)) {
        int value = std::get<int>(operand);
        switch (opcode) {
            case IROpcode::NEG: return -value;
            case IROpcode::NOT: return !value;
            default: break;
        }
    }
    
    if (std::holds_alternative<double>(operand)) {
        double value = std::get<double>(operand);
        switch (opcode) {
            case IROpcode::NEG: return -value;
            default: break;
        }
    }
    
    if (std::holds_alternative<bool>(operand)) {
        bool value = std::get<bool>(operand);
        switch (opcode) {
            case IROpcode::NOT: return !value;
            default: break;
        }
    }
    
    return operand;
}

} // namespace optimizer
} // namespace compiler  
} // namespace gumus