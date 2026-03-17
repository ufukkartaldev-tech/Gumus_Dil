#ifndef BYTECODE_GENERATOR_H
#define BYTECODE_GENERATOR_H

#include "../ir/ir_instruction.h"
#include "../vm/chunk.h"
#include "../vm/op_code.h"
#include <unordered_map>
#include <vector>

// 🎯 Bytecode Generation from IR

class BytecodeGenerator {
private:
    Chunk* currentChunk;
    IRModule* module;
    
    // Symbol tables
    std::unordered_map<std::string, int> constantPool;
    std::unordered_map<std::string, int> globalVariables;
    std::unordered_map<std::string, int> localVariables;
    std::unordered_map<std::string, int> labelAddresses;
    
    // Generation state
    std::vector<int> patchList; // For forward jumps
    int currentLine = 1;
    
public:
    BytecodeGenerator(IRModule* mod) : module(mod), currentChunk(nullptr) {}
    
    // Main generation functions
    Chunk generateBytecode();
    void generateFunction(IRFunction* function, Chunk* chunk);
    void generateBasicBlock(BasicBlock* block);
    void generateInstruction(IRInstruction* instr);
    
    // Instruction generation
    void generateArithmetic(IRInstruction* instr);
    void generateComparison(IRInstruction* instr);
    void generateLogical(IRInstruction* instr);
    void generateMemory(IRInstruction* instr);
    void generateControlFlow(IRInstruction* instr);
    void generateFunctionCall(IRInstruction* instr);
    void generateIO(IRInstruction* instr);
    
    // Utility functions
    int addConstant(const IRValue& value);
    int getVariableSlot(const std::string& name);
    int getLabelAddress(const std::string& label);
    void setLabelAddress(const std::string& label, int address);
    
    // Value conversion
    Value convertIRValue(const IRValue& irValue);
    OpCode getArithmeticOpCode(IROpcode irOp);
    OpCode getComparisonOpCode(IROpcode irOp);
    OpCode getLogicalOpCode(IROpcode irOp);
    
    // Debug support
    void setCurrentLine(int line) { currentLine = line; }
    void addDebugInfo(const std::string& info);
};

// 🔧 Advanced Bytecode Optimizations
class BytecodeOptimizer {
public:
    // Peephole optimizations
    static void optimizePeephole(Chunk* chunk);
    
    // Jump optimization
    static void optimizeJumps(Chunk* chunk);
    
    // Constant pool optimization
    static void optimizeConstants(Chunk* chunk);
    
    // Dead code elimination at bytecode level
    static void eliminateDeadCode(Chunk* chunk);
    
private:
    // Peephole patterns
    static bool optimizeArithmeticSequence(Chunk* chunk, int start);
    static bool optimizeLoadStore(Chunk* chunk, int start);
    static bool optimizeJumpChain(Chunk* chunk, int start);
    static bool optimizeConstantFolding(Chunk* chunk, int start);
    
    // Analysis helpers
    static bool isArithmeticOp(OpCode op);
    static bool isLoadOp(OpCode op);
    static bool isStoreOp(OpCode op);
    static bool isJumpOp(OpCode op);
};

// 🎯 Register Allocation (for future register-based VM)
class RegisterAllocator {
private:
    struct LiveRange {
        int start;
        int end;
        std::string variable;
    };
    
    std::vector<LiveRange> liveRanges;
    std::unordered_map<std::string, int> variableToRegister;
    int numRegisters;
    
public:
    RegisterAllocator(int maxRegisters = 256) : numRegisters(maxRegisters) {}
    
    // Main allocation function
    std::unordered_map<std::string, int> allocateRegisters(IRFunction* function);
    
    // Analysis
    void computeLiveRanges(IRFunction* function);
    void performAllocation();
    
    // Spilling (when we run out of registers)
    void spillVariable(const std::string& variable);
    void insertSpillCode(IRFunction* function);
    
private:
    bool interferes(const LiveRange& a, const LiveRange& b);
    int findFreeRegister(const LiveRange& range);
    void colorGraph();
};

// 🚀 Code Generation Pipeline
class CodeGenerationPipeline {
private:
    IRModule* module;
    OptimizationLevel optLevel;
    bool enableDebugInfo;
    
public:
    CodeGenerationPipeline(IRModule* mod, OptimizationLevel level = OptimizationLevel::O2)
        : module(mod), optLevel(level), enableDebugInfo(false) {}
    
    // Main pipeline
    Chunk generateOptimizedBytecode();
    
    // Pipeline stages
    void runIROptimizations();
    Chunk generateBytecode();
    void runBytecodeOptimizations(Chunk* chunk);
    
    // Configuration
    void setOptimizationLevel(OptimizationLevel level) { optLevel = level; }
    void setDebugInfo(bool enable) { enableDebugInfo = enable; }
    
    // Statistics
    struct CodeGenStats {
        int originalIRInstructions = 0;
        int optimizedIRInstructions = 0;
        int bytecodeInstructions = 0;
        int constantPoolSize = 0;
        double optimizationTime = 0.0;
        double codegenTime = 0.0;
    };
    
    CodeGenStats getStatistics() const { return stats; }
    
private:
    CodeGenStats stats;
    void collectStatistics();
};

// 🎯 Target-specific code generators
class TargetCodeGenerator {
public:
    virtual ~TargetCodeGenerator() = default;
    virtual std::string generateCode(IRModule* module) = 0;
    virtual std::string getTargetName() const = 0;
};

// C++ code generator (for AOT compilation)
class CppCodeGenerator : public TargetCodeGenerator {
public:
    std::string generateCode(IRModule* module) override;
    std::string getTargetName() const override { return "C++"; }
    
private:
    std::string generateFunction(IRFunction* function);
    std::string generateInstruction(IRInstruction* instr);
    std::string convertType(const IRValue& value);
    std::string sanitizeName(const std::string& name);
};

// JavaScript code generator (for web deployment)
class JavaScriptCodeGenerator : public TargetCodeGenerator {
public:
    std::string generateCode(IRModule* module) override;
    std::string getTargetName() const override { return "JavaScript"; }
    
private:
    std::string generateFunction(IRFunction* function);
    std::string generateInstruction(IRInstruction* instr);
    std::string convertValue(const IRValue& value);
};

// 🚀 High-level code generation interface
class CodeGenerator {
public:
    // Bytecode generation
    static Chunk generateBytecode(IRModule* module, OptimizationLevel level = OptimizationLevel::O2);
    
    // Target code generation
    static std::string generateCpp(IRModule* module);
    static std::string generateJavaScript(IRModule* module);
    
    // Pipeline management
    static std::unique_ptr<CodeGenerationPipeline> createPipeline(IRModule* module, OptimizationLevel level);
};

#endif // BYTECODE_GENERATOR_H