#include "bytecode_generator.h"
#include "../optimizer/optimizer.h"
#include <chrono>
#include <iostream>

// 🎯 Bytecode Generator Implementation

Chunk BytecodeGenerator::generateBytecode() {
    Chunk chunk;
    currentChunk = &chunk;
    
    // Generate code for all functions
    for (auto& function : module->functions) {
        generateFunction(function.get(), &chunk);
    }
    
    // Add program termination
    chunk.write(OP_HALT, currentLine);
    
    return chunk;
}

void BytecodeGenerator::generateFunction(IRFunction* function, Chunk* chunk) {
    currentChunk = chunk;
    
    // Function prologue
    if (function->name != "main") {
        // Mark function start
        int functionConstant = addConstant(Value(function->name));
        chunk->write(OP_DEFINE_FUNCTION, currentLine);
        chunk->write(functionConstant, currentLine);
    }
    
    // Generate code for each basic block
    for (auto& block : function->blocks) {
        // Set label address
        setLabelAddress(block->label, chunk->code.size());
        generateBasicBlock(block.get());
    }
    
    // Function epilogue
    if (function->name != "main") {
        chunk->write(OP_RETURN, currentLine);
    }
}

void BytecodeGenerator::generateBasicBlock(BasicBlock* block) {
    for (auto& instr : block->instructions) {
        if (instr->line > 0) {
            setCurrentLine(instr->line);
        }
        generateInstruction(instr.get());
    }
}

void BytecodeGenerator::generateInstruction(IRInstruction* instr) {
    switch (instr->opcode) {
        // Arithmetic operations
        case IROpcode::ADD:
        case IROpcode::SUB:
        case IROpcode::MUL:
        case IROpcode::DIV:
        case IROpcode::MOD:
            generateArithmetic(instr);
            break;
            
        // Comparison operations
        case IROpcode::EQ:
        case IROpcode::NE:
        case IROpcode::LT:
        case IROpcode::LE:
        case IROpcode::GT:
        case IROpcode::GE:
            generateComparison(instr);
            break;
            
        // Logical operations
        case IROpcode::AND:
        case IROpcode::OR:
        case IROpcode::NOT:
            generateLogical(instr);
            break;
            
        // Memory operations
        case IROpcode::LOAD:
        case IROpcode::STORE:
        case IROpcode::ALLOC:
        case IROpcode::FREE:
            generateMemory(instr);
            break;
            
        // Control flow
        case IROpcode::JMP:
        case IROpcode::JZ:
        case IROpcode::JNZ:
        case IROpcode::RET:
            generateControlFlow(instr);
            break;
            
        // Function calls
        case IROpcode::CALL:
            generateFunctionCall(instr);
            break;
            
        // I/O operations
        case IROpcode::PRINT:
        case IROpcode::READ:
            generateIO(instr);
            break;
            
        // Variable operations
        case IROpcode::GET_VAR:
            currentChunk->write(OP_GET_GLOBAL, currentLine);
            currentChunk->write(getVariableSlot(std::get<std::string>(instr->operands[0])), currentLine);
            break;
            
        case IROpcode::SET_VAR:
            currentChunk->write(OP_SET_GLOBAL, currentLine);
            currentChunk->write(getVariableSlot(std::get<std::string>(instr->operands[1])), currentLine);
            break;
            
        case IROpcode::DEF_VAR:
            currentChunk->write(OP_DEFINE_GLOBAL, currentLine);
            currentChunk->write(getVariableSlot(std::get<std::string>(instr->operands[0])), currentLine);
            break;
            
        // Special operations
        case IROpcode::NOP:
            // No operation - skip
            break;
            
        case IROpcode::HALT:
            currentChunk->write(OP_HALT, currentLine);
            break;
            
        default:
            std::cerr << "Unknown IR opcode: " << static_cast<int>(instr->opcode) << std::endl;
            break;
    }
}

void BytecodeGenerator::generateArithmetic(IRInstruction* instr) {
    // Load operands onto stack
    for (const auto& operand : instr->operands) {
        if (std::holds_alternative<std::string>(operand)) {
            // Variable reference
            std::string varName = std::get<std::string>(operand);
            currentChunk->write(OP_GET_GLOBAL, currentLine);
            currentChunk->write(getVariableSlot(varName), currentLine);
        } else {
            // Constant value
            int constantIndex = addConstant(convertIRValue(operand));
            currentChunk->write(OP_CONSTANT, currentLine);
            currentChunk->write(constantIndex, currentLine);
        }
    }
    
    // Generate arithmetic operation
    OpCode opCode = getArithmeticOpCode(instr->opcode);
    currentChunk->write(opCode, currentLine);
    
    // Store result if needed
    if (!instr->result.empty()) {
        currentChunk->write(OP_SET_GLOBAL, currentLine);
        currentChunk->write(getVariableSlot(instr->result), currentLine);
    }
}

void BytecodeGenerator::generateComparison(IRInstruction* instr) {
    // Load operands
    for (const auto& operand : instr->operands) {
        if (std::holds_alternative<std::string>(operand)) {
            std::string varName = std::get<std::string>(operand);
            currentChunk->write(OP_GET_GLOBAL, currentLine);
            currentChunk->write(getVariableSlot(varName), currentLine);
        } else {
            int constantIndex = addConstant(convertIRValue(operand));
            currentChunk->write(OP_CONSTANT, currentLine);
            currentChunk->write(constantIndex, currentLine);
        }
    }
    
    // Generate comparison
    OpCode opCode = getComparisonOpCode(instr->opcode);
    currentChunk->write(opCode, currentLine);
    
    // Store result
    if (!instr->result.empty()) {
        currentChunk->write(OP_SET_GLOBAL, currentLine);
        currentChunk->write(getVariableSlot(instr->result), currentLine);
    }
}

void BytecodeGenerator::generateLogical(IRInstruction* instr) {
    if (instr->opcode == IROpcode::NOT) {
        // Unary NOT operation
        if (std::holds_alternative<std::string>(instr->operands[0])) {
            std::string varName = std::get<std::string>(instr->operands[0]);
            currentChunk->write(OP_GET_GLOBAL, currentLine);
            currentChunk->write(getVariableSlot(varName), currentLine);
        } else {
            int constantIndex = addConstant(convertIRValue(instr->operands[0]));
            currentChunk->write(OP_CONSTANT, currentLine);
            currentChunk->write(constantIndex, currentLine);
        }
        
        currentChunk->write(OP_NOT, currentLine);
    } else {
        // Binary logical operations (AND, OR)
        for (const auto& operand : instr->operands) {
            if (std::holds_alternative<std::string>(operand)) {
                std::string varName = std::get<std::string>(operand);
                currentChunk->write(OP_GET_GLOBAL, currentLine);
                currentChunk->write(getVariableSlot(varName), currentLine);
            } else {
                int constantIndex = addConstant(convertIRValue(operand));
                currentChunk->write(OP_CONSTANT, currentLine);
                currentChunk->write(constantIndex, currentLine);
            }
        }
        
        OpCode opCode = getLogicalOpCode(instr->opcode);
        currentChunk->write(opCode, currentLine);
    }
    
    // Store result
    if (!instr->result.empty()) {
        currentChunk->write(OP_SET_GLOBAL, currentLine);
        currentChunk->write(getVariableSlot(instr->result), currentLine);
    }
}

void BytecodeGenerator::generateMemory(IRInstruction* instr) {
    switch (instr->opcode) {
        case IROpcode::LOAD:
            if (std::holds_alternative<std::string>(instr->operands[0])) {
                std::string varName = std::get<std::string>(instr->operands[0]);
                currentChunk->write(OP_GET_GLOBAL, currentLine);
                currentChunk->write(getVariableSlot(varName), currentLine);
            } else {
                int constantIndex = addConstant(convertIRValue(instr->operands[0]));
                currentChunk->write(OP_CONSTANT, currentLine);
                currentChunk->write(constantIndex, currentLine);
            }
            break;
            
        case IROpcode::STORE:
            // Load value to store
            if (std::holds_alternative<std::string>(instr->operands[0])) {
                std::string varName = std::get<std::string>(instr->operands[0]);
                currentChunk->write(OP_GET_GLOBAL, currentLine);
                currentChunk->write(getVariableSlot(varName), currentLine);
            } else {
                int constantIndex = addConstant(convertIRValue(instr->operands[0]));
                currentChunk->write(OP_CONSTANT, currentLine);
                currentChunk->write(constantIndex, currentLine);
            }
            
            // Store to variable
            if (instr->operands.size() > 1 && std::holds_alternative<std::string>(instr->operands[1])) {
                std::string varName = std::get<std::string>(instr->operands[1]);
                currentChunk->write(OP_SET_GLOBAL, currentLine);
                currentChunk->write(getVariableSlot(varName), currentLine);
            }
            break;
            
        case IROpcode::ALLOC:
            // Memory allocation (for future implementation)
            currentChunk->write(OP_NIL, currentLine); // Placeholder
            break;
            
        case IROpcode::FREE:
            // Memory deallocation (for future implementation)
            currentChunk->write(OP_POP, currentLine); // Placeholder
            break;
    }
}

void BytecodeGenerator::generateControlFlow(IRInstruction* instr) {
    switch (instr->opcode) {
        case IROpcode::JMP: {
            std::string label = std::get<std::string>(instr->operands[0]);
            int address = getLabelAddress(label);
            
            currentChunk->write(OP_JUMP, currentLine);
            if (address >= 0) {
                currentChunk->write(address, currentLine);
            } else {
                // Forward jump - add to patch list
                patchList.push_back(currentChunk->code.size());
                currentChunk->write(0, currentLine); // Placeholder
            }
            break;
        }
        
        case IROpcode::JZ: {
            // Load condition
            if (std::holds_alternative<std::string>(instr->operands[0])) {
                std::string varName = std::get<std::string>(instr->operands[0]);
                currentChunk->write(OP_GET_GLOBAL, currentLine);
                currentChunk->write(getVariableSlot(varName), currentLine);
            } else {
                int constantIndex = addConstant(convertIRValue(instr->operands[0]));
                currentChunk->write(OP_CONSTANT, currentLine);
                currentChunk->write(constantIndex, currentLine);
            }
            
            // Jump if false
            std::string label = std::get<std::string>(instr->operands[1]);
            int address = getLabelAddress(label);
            
            currentChunk->write(OP_JUMP_IF_FALSE, currentLine);
            if (address >= 0) {
                currentChunk->write(address, currentLine);
            } else {
                patchList.push_back(currentChunk->code.size());
                currentChunk->write(0, currentLine);
            }
            break;
        }
        
        case IROpcode::JNZ: {
            // Load condition
            if (std::holds_alternative<std::string>(instr->operands[0])) {
                std::string varName = std::get<std::string>(instr->operands[0]);
                currentChunk->write(OP_GET_GLOBAL, currentLine);
                currentChunk->write(getVariableSlot(varName), currentLine);
            } else {
                int constantIndex = addConstant(convertIRValue(instr->operands[0]));
                currentChunk->write(OP_CONSTANT, currentLine);
                currentChunk->write(constantIndex, currentLine);
            }
            
            // Jump if true (negate condition first)
            currentChunk->write(OP_NOT, currentLine);
            
            std::string label = std::get<std::string>(instr->operands[1]);
            int address = getLabelAddress(label);
            
            currentChunk->write(OP_JUMP_IF_FALSE, currentLine);
            if (address >= 0) {
                currentChunk->write(address, currentLine);
            } else {
                patchList.push_back(currentChunk->code.size());
                currentChunk->write(0, currentLine);
            }
            break;
        }
        
        case IROpcode::RET:
            if (!instr->operands.empty()) {
                // Load return value
                if (std::holds_alternative<std::string>(instr->operands[0])) {
                    std::string varName = std::get<std::string>(instr->operands[0]);
                    currentChunk->write(OP_GET_GLOBAL, currentLine);
                    currentChunk->write(getVariableSlot(varName), currentLine);
                } else {
                    int constantIndex = addConstant(convertIRValue(instr->operands[0]));
                    currentChunk->write(OP_CONSTANT, currentLine);
                    currentChunk->write(constantIndex, currentLine);
                }
            } else {
                // Return nil
                currentChunk->write(OP_NIL, currentLine);
            }
            
            currentChunk->write(OP_RETURN, currentLine);
            break;
    }
}

void BytecodeGenerator::generateFunctionCall(IRInstruction* instr) {
    std::string functionName = std::get<std::string>(instr->operands[0]);
    
    // Load arguments onto stack (in reverse order)
    for (int i = instr->operands.size() - 1; i >= 1; i--) {
        const auto& arg = instr->operands[i];
        if (std::holds_alternative<std::string>(arg)) {
            std::string varName = std::get<std::string>(arg);
            currentChunk->write(OP_GET_GLOBAL, currentLine);
            currentChunk->write(getVariableSlot(varName), currentLine);
        } else {
            int constantIndex = addConstant(convertIRValue(arg));
            currentChunk->write(OP_CONSTANT, currentLine);
            currentChunk->write(constantIndex, currentLine);
        }
    }
    
    // Call function
    int functionConstant = addConstant(Value(functionName));
    currentChunk->write(OP_CALL, currentLine);
    currentChunk->write(functionConstant, currentLine);
    currentChunk->write(instr->operands.size() - 1, currentLine); // Argument count
    
    // Store result if needed
    if (!instr->result.empty()) {
        currentChunk->write(OP_SET_GLOBAL, currentLine);
        currentChunk->write(getVariableSlot(instr->result), currentLine);
    }
}

void BytecodeGenerator::generateIO(IRInstruction* instr) {
    switch (instr->opcode) {
        case IROpcode::PRINT:
            // Load value to print
            if (std::holds_alternative<std::string>(instr->operands[0])) {
                std::string varName = std::get<std::string>(instr->operands[0]);
                currentChunk->write(OP_GET_GLOBAL, currentLine);
                currentChunk->write(getVariableSlot(varName), currentLine);
            } else {
                int constantIndex = addConstant(convertIRValue(instr->operands[0]));
                currentChunk->write(OP_CONSTANT, currentLine);
                currentChunk->write(constantIndex, currentLine);
            }
            
            currentChunk->write(OP_PRINT, currentLine);
            break;
            
        case IROpcode::READ:
            // Read input (for future implementation)
            currentChunk->write(OP_NIL, currentLine); // Placeholder
            break;
    }
}

// Utility functions

int BytecodeGenerator::addConstant(const IRValue& value) {
    Value val = convertIRValue(value);
    return currentChunk->addConstant(val);
}

int BytecodeGenerator::getVariableSlot(const std::string& name) {
    auto it = globalVariables.find(name);
    if (it != globalVariables.end()) {
        return it->second;
    }
    
    // Create new variable slot
    int slot = globalVariables.size();
    globalVariables[name] = slot;
    return slot;
}

int BytecodeGenerator::getLabelAddress(const std::string& label) {
    auto it = labelAddresses.find(label);
    return (it != labelAddresses.end()) ? it->second : -1;
}

void BytecodeGenerator::setLabelAddress(const std::string& label, int address) {
    labelAddresses[label] = address;
}

Value BytecodeGenerator::convertIRValue(const IRValue& irValue) {
    if (std::holds_alternative<int>(irValue)) {
        return Value(std::get<int>(irValue));
    } else if (std::holds_alternative<double>(irValue)) {
        return Value(std::get<double>(irValue));
    } else if (std::holds_alternative<std::string>(irValue)) {
        return Value(std::get<std::string>(irValue));
    } else if (std::holds_alternative<bool>(irValue)) {
        return Value(std::get<bool>(irValue));
    }
    
    return Value(); // Nil
}

OpCode BytecodeGenerator::getArithmeticOpCode(IROpcode irOp) {
    switch (irOp) {
        case IROpcode::ADD: return OP_ADD;
        case IROpcode::SUB: return OP_SUBTRACT;
        case IROpcode::MUL: return OP_MULTIPLY;
        case IROpcode::DIV: return OP_DIVIDE;
        case IROpcode::MOD: return OP_MODULO;
        default: return OP_NOP;
    }
}

OpCode BytecodeGenerator::getComparisonOpCode(IROpcode irOp) {
    switch (irOp) {
        case IROpcode::EQ: return OP_EQUAL;
        case IROpcode::NE: return OP_NOT_EQUAL;
        case IROpcode::LT: return OP_LESS;
        case IROpcode::LE: return OP_LESS_EQUAL;
        case IROpcode::GT: return OP_GREATER;
        case IROpcode::GE: return OP_GREATER_EQUAL;
        default: return OP_NOP;
    }
}

OpCode BytecodeGenerator::getLogicalOpCode(IROpcode irOp) {
    switch (irOp) {
        case IROpcode::AND: return OP_AND;
        case IROpcode::OR: return OP_OR;
        case IROpcode::NOT: return OP_NOT;
        default: return OP_NOP;
    }
}

// 🚀 Code Generation Pipeline Implementation

Chunk CodeGenerationPipeline::generateOptimizedBytecode() {
    auto startTime = std::chrono::high_resolution_clock::now();
    
    // Stage 1: IR Optimizations
    runIROptimizations();
    
    auto irOptTime = std::chrono::high_resolution_clock::now();
    stats.optimizationTime = std::chrono::duration<double>(irOptTime - startTime).count();
    
    // Stage 2: Bytecode Generation
    Chunk chunk = generateBytecode();
    
    auto codegenTime = std::chrono::high_resolution_clock::now();
    stats.codegenTime = std::chrono::duration<double>(codegenTime - irOptTime).count();
    
    // Stage 3: Bytecode Optimizations
    runBytecodeOptimizations(&chunk);
    
    collectStatistics();
    return chunk;
}

void CodeGenerationPipeline::runIROptimizations() {
    if (optLevel != OptimizationLevel::O0) {
        Optimizer::optimizeModule(module, optLevel);
    }
}

Chunk CodeGenerationPipeline::generateBytecode() {
    BytecodeGenerator generator(module);
    return generator.generateBytecode();
}

void CodeGenerationPipeline::runBytecodeOptimizations(Chunk* chunk) {
    if (optLevel >= OptimizationLevel::O2) {
        BytecodeOptimizer::optimizePeephole(chunk);
        BytecodeOptimizer::optimizeJumps(chunk);
        BytecodeOptimizer::optimizeConstants(chunk);
    }
    
    if (optLevel >= OptimizationLevel::O3) {
        BytecodeOptimizer::eliminateDeadCode(chunk);
    }
}

void CodeGenerationPipeline::collectStatistics() {
    // Count IR instructions
    for (auto& function : module->functions) {
        for (auto& block : function->blocks) {
            stats.optimizedIRInstructions += block->instructions.size();
        }
    }
}

// 🚀 High-level interface

Chunk CodeGenerator::generateBytecode(IRModule* module, OptimizationLevel level) {
    CodeGenerationPipeline pipeline(module, level);
    return pipeline.generateOptimizedBytecode();
}

std::unique_ptr<CodeGenerationPipeline> CodeGenerator::createPipeline(IRModule* module, OptimizationLevel level) {
    return std::make_unique<CodeGenerationPipeline>(module, level);
}