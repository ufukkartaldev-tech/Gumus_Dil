#ifndef IR_INSTRUCTION_H
#define IR_INSTRUCTION_H

#include <string>
#include <vector>
#include <memory>
#include <variant>

// 🔧 IR Instruction Types
enum class IROpcode {
    // Arithmetic Operations
    ADD, SUB, MUL, DIV, MOD,
    
    // Logical Operations  
    AND, OR, NOT,
    
    // Comparison Operations
    EQ, NE, LT, LE, GT, GE,
    
    // Memory Operations
    LOAD, STORE, ALLOC, FREE,
    
    // Control Flow
    JMP, JZ, JNZ, CALL, RET,
    
    // Stack Operations
    PUSH, POP,
    
    // Variable Operations
    GET_VAR, SET_VAR, DEF_VAR,
    
    // Function Operations
    DEF_FUNC, CALL_FUNC, RET_FUNC,
    
    // Type Operations
    CAST, TYPEOF,
    
    // String Operations
    STR_CONCAT, STR_LEN, STR_SUBSTR,
    
    // Array Operations
    ARR_GET, ARR_SET, ARR_LEN, ARR_NEW,
    
    // Object Operations
    OBJ_GET, OBJ_SET, OBJ_NEW,
    
    // I/O Operations
    PRINT, READ,
    
    // Debug Operations
    DEBUG_LINE, DEBUG_VAR,
    
    // Optimization Hints
    INLINE_HINT, LOOP_HINT, BRANCH_HINT,
    
    // Special
    NOP, HALT
};

// 🎯 IR Value Types
using IRValue = std::variant<
    int,                    // Integer literal
    double,                 // Float literal
    std::string,           // String literal or variable name
    bool                   // Boolean literal
>;

// 📍 IR Instruction
struct IRInstruction {
    IROpcode opcode;
    std::vector<IRValue> operands;
    std::string result;     // Result variable name (optional)
    int line = 0;          // Source line number
    std::string comment;   // Optional comment for debugging
    
    IRInstruction(IROpcode op) : opcode(op) {}
    
    IRInstruction(IROpcode op, const std::vector<IRValue>& ops) 
        : opcode(op), operands(ops) {}
    
    IRInstruction(IROpcode op, const std::vector<IRValue>& ops, const std::string& res)
        : opcode(op), operands(ops), result(res) {}
    
    std::string toString() const;
    bool isTerminator() const;
    bool hasSideEffects() const;
};

// 🏗️ Basic Block
class BasicBlock {
public:
    std::string label;
    std::vector<std::unique_ptr<IRInstruction>> instructions;
    std::vector<BasicBlock*> predecessors;
    std::vector<BasicBlock*> successors;
    
    BasicBlock(const std::string& name) : label(name) {}
    
    void addInstruction(std::unique_ptr<IRInstruction> instr);
    void addSuccessor(BasicBlock* block);
    void addPredecessor(BasicBlock* block);
    
    bool isTerminated() const;
    std::string toString() const;
};

// 🎯 IR Function
class IRFunction {
public:
    std::string name;
    std::vector<std::string> parameters;
    std::vector<std::unique_ptr<BasicBlock>> blocks;
    std::string returnType;
    
    IRFunction(const std::string& funcName) : name(funcName) {}
    
    BasicBlock* createBlock(const std::string& label);
    BasicBlock* getEntryBlock();
    BasicBlock* getExitBlock();
    
    void addParameter(const std::string& param);
    std::string toString() const;
    
    // Analysis helpers
    std::vector<BasicBlock*> getPostOrder();
    std::vector<BasicBlock*> getReversePostOrder();
};

// 📦 IR Module
class IRModule {
public:
    std::string name;
    std::vector<std::unique_ptr<IRFunction>> functions;
    std::vector<std::string> globalVariables;
    
    IRModule(const std::string& moduleName) : name(moduleName) {}
    
    IRFunction* createFunction(const std::string& name);
    IRFunction* getFunction(const std::string& name);
    void addGlobalVariable(const std::string& name);
    
    std::string toString() const;
    void dump() const;
};

// 🔧 IR Builder Helper
class IRBuilder {
private:
    BasicBlock* currentBlock;
    IRFunction* currentFunction;
    int tempCounter = 0;
    
public:
    IRBuilder() : currentBlock(nullptr), currentFunction(nullptr) {}
    
    void setInsertPoint(BasicBlock* block);
    void setCurrentFunction(IRFunction* func);
    
    // Instruction creation helpers
    IRInstruction* createAdd(const IRValue& lhs, const IRValue& rhs, const std::string& result = "");
    IRInstruction* createSub(const IRValue& lhs, const IRValue& rhs, const std::string& result = "");
    IRInstruction* createMul(const IRValue& lhs, const IRValue& rhs, const std::string& result = "");
    IRInstruction* createDiv(const IRValue& lhs, const IRValue& rhs, const std::string& result = "");
    
    IRInstruction* createLoad(const std::string& var, const std::string& result = "");
    IRInstruction* createStore(const IRValue& value, const std::string& var);
    
    IRInstruction* createJump(const std::string& label);
    IRInstruction* createCondJump(const IRValue& condition, const std::string& trueLabel, const std::string& falseLabel);
    
    IRInstruction* createCall(const std::string& function, const std::vector<IRValue>& args, const std::string& result = "");
    IRInstruction* createReturn(const IRValue& value = IRValue{});
    
    IRInstruction* createPrint(const IRValue& value);
    
    // Utility
    std::string generateTempName();
    std::string generateLabelName(const std::string& prefix = "L");
};

#endif // IR_INSTRUCTION_H