#include "ir_instruction.h"
#include <sstream>
#include <iostream>
#include <algorithm>

// 📝 IR Instruction Implementation

std::string IRInstruction::toString() const {
    std::ostringstream oss;
    
    // Add result if present
    if (!result.empty()) {
        oss << result << " = ";
    }
    
    // Add opcode
    switch (opcode) {
        case IROpcode::ADD: oss << "add"; break;
        case IROpcode::SUB: oss << "sub"; break;
        case IROpcode::MUL: oss << "mul"; break;
        case IROpcode::DIV: oss << "div"; break;
        case IROpcode::MOD: oss << "mod"; break;
        
        case IROpcode::AND: oss << "and"; break;
        case IROpcode::OR: oss << "or"; break;
        case IROpcode::NOT: oss << "not"; break;
        
        case IROpcode::EQ: oss << "eq"; break;
        case IROpcode::NE: oss << "ne"; break;
        case IROpcode::LT: oss << "lt"; break;
        case IROpcode::LE: oss << "le"; break;
        case IROpcode::GT: oss << "gt"; break;
        case IROpcode::GE: oss << "ge"; break;
        
        case IROpcode::LOAD: oss << "load"; break;
        case IROpcode::STORE: oss << "store"; break;
        case IROpcode::ALLOC: oss << "alloc"; break;
        case IROpcode::FREE: oss << "free"; break;
        
        case IROpcode::JMP: oss << "jmp"; break;
        case IROpcode::JZ: oss << "jz"; break;
        case IROpcode::JNZ: oss << "jnz"; break;
        case IROpcode::CALL: oss << "call"; break;
        case IROpcode::RET: oss << "ret"; break;
        
        case IROpcode::PUSH: oss << "push"; break;
        case IROpcode::POP: oss << "pop"; break;
        
        case IROpcode::GET_VAR: oss << "get_var"; break;
        case IROpcode::SET_VAR: oss << "set_var"; break;
        case IROpcode::DEF_VAR: oss << "def_var"; break;
        
        case IROpcode::PRINT: oss << "print"; break;
        case IROpcode::READ: oss << "read"; break;
        
        case IROpcode::NOP: oss << "nop"; break;
        case IROpcode::HALT: oss << "halt"; break;
        
        default: oss << "unknown"; break;
    }
    
    // Add operands
    for (size_t i = 0; i < operands.size(); ++i) {
        if (i == 0) oss << " ";
        else oss << ", ";
        
        std::visit([&oss](const auto& value) {
            using T = std::decay_t<decltype(value)>;
            if constexpr (std::is_same_v<T, int>) {
                oss << value;
            } else if constexpr (std::is_same_v<T, double>) {
                oss << value;
            } else if constexpr (std::is_same_v<T, std::string>) {
                oss << value;
            } else if constexpr (std::is_same_v<T, bool>) {
                oss << (value ? "true" : "false");
            }
        }, operands[i]);
    }
    
    // Add comment if present
    if (!comment.empty()) {
        oss << " ; " << comment;
    }
    
    return oss.str();
}

bool IRInstruction::isTerminator() const {
    return opcode == IROpcode::JMP || opcode == IROpcode::JZ || 
           opcode == IROpcode::JNZ || opcode == IROpcode::RET || 
           opcode == IROpcode::HALT;
}

bool IRInstruction::hasSideEffects() const {
    return opcode == IROpcode::STORE || opcode == IROpcode::CALL ||
           opcode == IROpcode::PRINT || opcode == IROpcode::FREE ||
           opcode == IROpcode::SET_VAR || opcode == IROpcode::DEF_VAR;
}

// 🏗️ Basic Block Implementation

void BasicBlock::addInstruction(std::unique_ptr<IRInstruction> instr) {
    instructions.push_back(std::move(instr));
}

void BasicBlock::addSuccessor(BasicBlock* block) {
    if (std::find(successors.begin(), successors.end(), block) == successors.end()) {
        successors.push_back(block);
        block->addPredecessor(this);
    }
}

void BasicBlock::addPredecessor(BasicBlock* block) {
    if (std::find(predecessors.begin(), predecessors.end(), block) == predecessors.end()) {
        predecessors.push_back(block);
    }
}

bool BasicBlock::isTerminated() const {
    return !instructions.empty() && instructions.back()->isTerminator();
}

std::string BasicBlock::toString() const {
    std::ostringstream oss;
    oss << label << ":\n";
    
    for (const auto& instr : instructions) {
        oss << "  " << instr->toString() << "\n";
    }
    
    return oss.str();
}

// 🎯 IR Function Implementation

BasicBlock* IRFunction::createBlock(const std::string& label) {
    auto block = std::make_unique<BasicBlock>(label);
    BasicBlock* blockPtr = block.get();
    blocks.push_back(std::move(block));
    return blockPtr;
}

BasicBlock* IRFunction::getEntryBlock() {
    return blocks.empty() ? nullptr : blocks[0].get();
}

BasicBlock* IRFunction::getExitBlock() {
    // Find block with return instruction
    for (auto& block : blocks) {
        if (!block->instructions.empty() && 
            block->instructions.back()->opcode == IROpcode::RET) {
            return block.get();
        }
    }
    return nullptr;
}

void IRFunction::addParameter(const std::string& param) {
    parameters.push_back(param);
}

std::string IRFunction::toString() const {
    std::ostringstream oss;
    oss << "function " << name << "(";
    
    for (size_t i = 0; i < parameters.size(); ++i) {
        if (i > 0) oss << ", ";
        oss << parameters[i];
    }
    
    oss << ") {\n";
    
    for (const auto& block : blocks) {
        oss << block->toString();
    }
    
    oss << "}\n";
    return oss.str();
}

std::vector<BasicBlock*> IRFunction::getPostOrder() {
    std::vector<BasicBlock*> result;
    std::set<BasicBlock*> visited;
    
    std::function<void(BasicBlock*)> dfs = [&](BasicBlock* block) {
        if (visited.count(block)) return;
        visited.insert(block);
        
        for (auto successor : block->successors) {
            dfs(successor);
        }
        
        result.push_back(block);
    };
    
    if (!blocks.empty()) {
        dfs(blocks[0].get());
    }
    
    return result;
}

std::vector<BasicBlock*> IRFunction::getReversePostOrder() {
    auto postOrder = getPostOrder();
    std::reverse(postOrder.begin(), postOrder.end());
    return postOrder;
}

// 📦 IR Module Implementation

IRFunction* IRModule::createFunction(const std::string& name) {
    auto func = std::make_unique<IRFunction>(name);
    IRFunction* funcPtr = func.get();
    functions.push_back(std::move(func));
    return funcPtr;
}

IRFunction* IRModule::getFunction(const std::string& name) {
    for (auto& func : functions) {
        if (func->name == name) {
            return func.get();
        }
    }
    return nullptr;
}

void IRModule::addGlobalVariable(const std::string& name) {
    globalVariables.push_back(name);
}

std::string IRModule::toString() const {
    std::ostringstream oss;
    oss << "module " << name << " {\n";
    
    // Global variables
    if (!globalVariables.empty()) {
        oss << "  globals:\n";
        for (const auto& var : globalVariables) {
            oss << "    " << var << "\n";
        }
        oss << "\n";
    }
    
    // Functions
    for (const auto& func : functions) {
        oss << func->toString() << "\n";
    }
    
    oss << "}\n";
    return oss.str();
}

void IRModule::dump() const {
    std::cout << toString();
}

// 🔧 IR Builder Implementation

void IRBuilder::setInsertPoint(BasicBlock* block) {
    currentBlock = block;
}

void IRBuilder::setCurrentFunction(IRFunction* func) {
    currentFunction = func;
}

IRInstruction* IRBuilder::createAdd(const IRValue& lhs, const IRValue& rhs, const std::string& result) {
    std::string resultName = result.empty() ? generateTempName() : result;
    auto instr = std::make_unique<IRInstruction>(IROpcode::ADD, std::vector<IRValue>{lhs, rhs}, resultName);
    IRInstruction* instrPtr = instr.get();
    
    if (currentBlock) {
        currentBlock->addInstruction(std::move(instr));
    }
    
    return instrPtr;
}

IRInstruction* IRBuilder::createSub(const IRValue& lhs, const IRValue& rhs, const std::string& result) {
    std::string resultName = result.empty() ? generateTempName() : result;
    auto instr = std::make_unique<IRInstruction>(IROpcode::SUB, std::vector<IRValue>{lhs, rhs}, resultName);
    IRInstruction* instrPtr = instr.get();
    
    if (currentBlock) {
        currentBlock->addInstruction(std::move(instr));
    }
    
    return instrPtr;
}

IRInstruction* IRBuilder::createMul(const IRValue& lhs, const IRValue& rhs, const std::string& result) {
    std::string resultName = result.empty() ? generateTempName() : result;
    auto instr = std::make_unique<IRInstruction>(IROpcode::MUL, std::vector<IRValue>{lhs, rhs}, resultName);
    IRInstruction* instrPtr = instr.get();
    
    if (currentBlock) {
        currentBlock->addInstruction(std::move(instr));
    }
    
    return instrPtr;
}

IRInstruction* IRBuilder::createDiv(const IRValue& lhs, const IRValue& rhs, const std::string& result) {
    std::string resultName = result.empty() ? generateTempName() : result;
    auto instr = std::make_unique<IRInstruction>(IROpcode::DIV, std::vector<IRValue>{lhs, rhs}, resultName);
    IRInstruction* instrPtr = instr.get();
    
    if (currentBlock) {
        currentBlock->addInstruction(std::move(instr));
    }
    
    return instrPtr;
}

IRInstruction* IRBuilder::createLoad(const std::string& var, const std::string& result) {
    std::string resultName = result.empty() ? generateTempName() : result;
    auto instr = std::make_unique<IRInstruction>(IROpcode::LOAD, std::vector<IRValue>{var}, resultName);
    IRInstruction* instrPtr = instr.get();
    
    if (currentBlock) {
        currentBlock->addInstruction(std::move(instr));
    }
    
    return instrPtr;
}

IRInstruction* IRBuilder::createStore(const IRValue& value, const std::string& var) {
    auto instr = std::make_unique<IRInstruction>(IROpcode::STORE, std::vector<IRValue>{value, var});
    IRInstruction* instrPtr = instr.get();
    
    if (currentBlock) {
        currentBlock->addInstruction(std::move(instr));
    }
    
    return instrPtr;
}

IRInstruction* IRBuilder::createJump(const std::string& label) {
    auto instr = std::make_unique<IRInstruction>(IROpcode::JMP, std::vector<IRValue>{label});
    IRInstruction* instrPtr = instr.get();
    
    if (currentBlock) {
        currentBlock->addInstruction(std::move(instr));
    }
    
    return instrPtr;
}

IRInstruction* IRBuilder::createCondJump(const IRValue& condition, const std::string& trueLabel, const std::string& falseLabel) {
    auto instr = std::make_unique<IRInstruction>(IROpcode::JZ, std::vector<IRValue>{condition, falseLabel});
    IRInstruction* instrPtr = instr.get();
    
    if (currentBlock) {
        currentBlock->addInstruction(std::move(instr));
        // Add unconditional jump to true label
        auto jumpInstr = std::make_unique<IRInstruction>(IROpcode::JMP, std::vector<IRValue>{trueLabel});
        currentBlock->addInstruction(std::move(jumpInstr));
    }
    
    return instrPtr;
}

IRInstruction* IRBuilder::createCall(const std::string& function, const std::vector<IRValue>& args, const std::string& result) {
    std::vector<IRValue> operands = {function};
    operands.insert(operands.end(), args.begin(), args.end());
    
    std::string resultName = result.empty() ? generateTempName() : result;
    auto instr = std::make_unique<IRInstruction>(IROpcode::CALL, operands, resultName);
    IRInstruction* instrPtr = instr.get();
    
    if (currentBlock) {
        currentBlock->addInstruction(std::move(instr));
    }
    
    return instrPtr;
}

IRInstruction* IRBuilder::createReturn(const IRValue& value) {
    std::vector<IRValue> operands;
    if (std::holds_alternative<std::string>(value) && std::get<std::string>(value).empty()) {
        // No return value
    } else {
        operands.push_back(value);
    }
    
    auto instr = std::make_unique<IRInstruction>(IROpcode::RET, operands);
    IRInstruction* instrPtr = instr.get();
    
    if (currentBlock) {
        currentBlock->addInstruction(std::move(instr));
    }
    
    return instrPtr;
}

IRInstruction* IRBuilder::createPrint(const IRValue& value) {
    auto instr = std::make_unique<IRInstruction>(IROpcode::PRINT, std::vector<IRValue>{value});
    IRInstruction* instrPtr = instr.get();
    
    if (currentBlock) {
        currentBlock->addInstruction(std::move(instr));
    }
    
    return instrPtr;
}

std::string IRBuilder::generateTempName() {
    return "%t" + std::to_string(tempCounter++);
}

std::string IRBuilder::generateLabelName(const std::string& prefix) {
    static int labelCounter = 0;
    return prefix + std::to_string(labelCounter++);
}