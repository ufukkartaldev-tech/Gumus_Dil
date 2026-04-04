#pragma once
#include "optimizer.h"

namespace gumus {
namespace compiler {
namespace optimizer {

/**
 * Constant Folding Pass
 * Evaluates constant expressions at compile time
 */
class ConstantFoldingPass : public OptimizationPass {
public:
    bool runOnFunction(IRFunction* function) override;
    bool runOnModule(IRModule* module) override;
    
    const char* getName() const override { return "ConstantFolding"; }

private:
    bool modified = false;
    
    bool foldInstruction(IRInstruction* instr);
    bool isConstant(const IRValue& value);
    IRValue evaluateConstantExpression(IROpcode opcode, const IRValue& lhs, const IRValue& rhs);
    IRValue evaluateUnaryExpression(IROpcode opcode, const IRValue& operand);
};

} // namespace optimizer
} // namespace compiler  
} // namespace gumus