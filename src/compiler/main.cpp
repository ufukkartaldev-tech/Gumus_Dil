#ifdef _MSC_VER
#pragma execution_character_set("utf-8")
#endif

#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <cstring>
#include <clocale>
#include <chrono>

// Compiler components
#include "lexer/tokenizer.h"
#include "lexer/token.h"
#include "parser/ast.h"
#include "parser/ast_serializer.h"
#include "interpreter/interpreter.h"
#include "semantic/resolver.h"
#include "ir/ir_instruction.h"
#include "ir/ast_to_ir.h"
#include "optimizer/optimizer.h"
#include "codegen/bytecode_generator.h"
#include "vm/compiler.h"
#include "vm/vm.h"
#include "json_hata.h"
#include "lsp_server.h"
#include "debug.h"

// Security framework
#include "security/input_validator.h"
#include "security/secure_database.h"
#include "security/secure_subprocess.h"

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

// Compilation modes
enum class CompilationMode {
    INTERPRETER,    // Direct AST interpretation
    BYTECODE_VM,   // Compile to bytecode and run on VM
    IR_DUMP,       // Dump IR representation
    OPTIMIZED_IR,  // Dump optimized IR
    BYTECODE_DUMP  // Dump bytecode
};

// Global configuration
struct CompilerConfig {
    CompilationMode mode = CompilationMode::BYTECODE_VM;
    OptimizationLevel optLevel = OptimizationLevel::O2;
    bool dumpAst = false;
    bool dumpMemory = false;
    bool enableDebug = false;
    bool enableProfiling = false;
    std::string outputFile;
    SecurityContext::TrustLevel securityLevel = SecurityContext::TrustLevel::MEDIUM;
};

CompilerConfig config;

// Global security components
InputValidator g_inputValidator;
SecurityContext g_securityContext(SecurityContext::TrustLevel::MEDIUM);

void printUsage(const char* programName) {
    std::cout << "GümüşDil Compiler v2.0\n";
    std::cout << "Usage: " << programName << " [options] <file>\n\n";
    std::cout << "Options:\n";
    std::cout << "  --mode <mode>        Compilation mode (interpreter|vm|ir|opt-ir|bytecode)\n";
    std::cout << "  --opt <level>        Optimization level (O0|O1|O2|O3|Os|Oz)\n";
    std::cout << "  --dump-ast          Dump AST in JSON format\n";
    std::cout << "  --dump-memory       Dump memory state\n";
    std::cout << "  --debug             Enable debug mode\n";
    std::cout << "  --profile           Enable profiling\n";
    std::cout << "  --security <level>  Security level (low|medium|high|system)\n";
    std::cout << "  --output <file>     Output file (for code generation)\n";
    std::cout << "  --help              Show this help message\n\n";
    std::cout << "Examples:\n";
    std::cout << "  " << programName << " program.tr\n";
    std::cout << "  " << programName << " --mode vm --opt O3 program.tr\n";
    std::cout << "  " << programName << " --dump-ast program.tr\n";
}

bool parseArguments(int argc, char* argv[]) {
    if (argc < 2) {
        printUsage(argv[0]);
        return false;
    }
    
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        
        if (arg == "--help") {
            printUsage(argv[0]);
            return false;
        } else if (arg == "--mode" && i + 1 < argc) {
            std::string mode = argv[++i];
            if (mode == "interpreter") config.mode = CompilationMode::INTERPRETER;
            else if (mode == "vm") config.mode = CompilationMode::BYTECODE_VM;
            else if (mode == "ir") config.mode = CompilationMode::IR_DUMP;
            else if (mode == "opt-ir") config.mode = CompilationMode::OPTIMIZED_IR;
            else if (mode == "bytecode") config.mode = CompilationMode::BYTECODE_DUMP;
            else {
                std::cerr << "Unknown mode: " << mode << std::endl;
                return false;
            }
        } else if (arg == "--opt" && i + 1 < argc) {
            std::string level = argv[++i];
            if (level == "O0") config.optLevel = OptimizationLevel::O0;
            else if (level == "O1") config.optLevel = OptimizationLevel::O1;
            else if (level == "O2") config.optLevel = OptimizationLevel::O2;
            else if (level == "O3") config.optLevel = OptimizationLevel::O3;
            else if (level == "Os") config.optLevel = OptimizationLevel::Os;
            else if (level == "Oz") config.optLevel = OptimizationLevel::Oz;
            else {
                std::cerr << "Unknown optimization level: " << level << std::endl;
                return false;
            }
        } else if (arg == "--dump-ast") {
            config.dumpAst = true;
        } else if (arg == "--dump-memory") {
            config.dumpMemory = true;
        } else if (arg == "--debug") {
            config.enableDebug = true;
            gumus_debug = true;
        } else if (arg == "--profile") {
            config.enableProfiling = true;
        } else if (arg == "--security" && i + 1 < argc) {
            std::string level = argv[++i];
            if (level == "low") config.securityLevel = SecurityContext::TrustLevel::LOW;
            else if (level == "medium") config.securityLevel = SecurityContext::TrustLevel::MEDIUM;
            else if (level == "high") config.securityLevel = SecurityContext::TrustLevel::HIGH;
            else if (level == "system") config.securityLevel = SecurityContext::TrustLevel::SYSTEM;
            else {
                std::cerr << "Unknown security level: " << level << std::endl;
                return false;
            }
        } else if (arg == "--output" && i + 1 < argc) {
            config.outputFile = argv[++i];
        } else if (!arg.empty() && arg[0] != '-') {
            // This is the input file
            return true;
        } else {
            std::cerr << "Unknown option: " << arg << std::endl;
            return false;
        }
    }
    
    return true;
}

void run(const std::string& source, const std::string& filename) {
    std::vector<Token> tokens;
    std::vector<Stmt*> statements;
    
    auto startTime = std::chrono::high_resolution_clock::now();
    
    try {
        // 1. Lexical Analysis (Tokenization)
        if (config.enableDebug) {
            std::cout << "🔤 Lexical Analysis..." << std::endl;
        }
        
        Tokenizer tokenizer(source);
        tokens = tokenizer.tokenize();
        
        if (config.enableDebug) {
            std::cout << "Generated " << tokens.size() << " tokens" << std::endl;
        }
        
        // 2. Syntax Analysis (Parsing)
        if (config.enableDebug) {
            std::cout << "🌳 Syntax Analysis..." << std::endl;
        }
        
        MemoryArena arena;
        Parser parser(tokens, arena);
        statements = parser.parse();
        
        if (parser.hasError()) {
            return;
        }
        
        if (config.enableDebug) {
            std::cout << "Generated AST with " << statements.size() << " statements" << std::endl;
        }
        
        // 3. Semantic Analysis
        if (config.enableDebug) {
            std::cout << "🔍 Semantic Analysis..." << std::endl;
        }
        
        Interpreter tempInterpreter; // For resolver
        Resolver resolver(tempInterpreter);
        resolver.resolve(statements);
        
        // AST Dump (if requested)
        if (config.dumpAst) {
            AstJsonSerializer serializer;
            std::cout << serializer.serialize(statements) << std::endl;
            return;
        }
        
        // 4. Choose execution path based on mode
        switch (config.mode) {
            case CompilationMode::INTERPRETER: {
                if (config.enableDebug) {
                    std::cout << "🎭 Running Interpreter..." << std::endl;
                }
                
                Interpreter interpreter;
                for (auto stmt : statements) {
                    interpreter.execute(stmt);
                }
                break;
            }
            
            case CompilationMode::IR_DUMP:
            case CompilationMode::OPTIMIZED_IR: {
                if (config.enableDebug) {
                    std::cout << "🔧 Generating IR..." << std::endl;
                }
                
                // Convert AST to IR
                auto irModule = convertASTToIR(statements, filename);
                
                if (config.mode == CompilationMode::OPTIMIZED_IR) {
                    if (config.enableDebug) {
                        std::cout << "⚡ Optimizing IR..." << std::endl;
                    }
                    Optimizer::optimizeModule(irModule.get(), config.optLevel);
                }
                
                // Dump IR
                irModule->dump();
                break;
            }
            
            case CompilationMode::BYTECODE_DUMP:
            case CompilationMode::BYTECODE_VM: {
                if (config.enableDebug) {
                    std::cout << "🔧 Generating IR..." << std::endl;
                }
                
                // Convert AST to IR
                auto irModule = convertASTToIR(statements, filename);
                
                if (config.enableDebug) {
                    std::cout << "⚡ Optimizing IR..." << std::endl;
                }
                
                // Optimize IR
                Optimizer::optimizeModule(irModule.get(), config.optLevel);
                
                if (config.enableDebug) {
                    std::cout << "📦 Generating Bytecode..." << std::endl;
                }
                
                // Generate bytecode
                Chunk chunk = CodeGenerator::generateBytecode(irModule.get(), config.optLevel);
                
                if (config.mode == CompilationMode::BYTECODE_DUMP) {
                    // Dump bytecode
                    chunk.disassemble(filename);
                } else {
                    // Execute on VM
                    if (config.enableDebug) {
                        std::cout << "🚀 Running on VM..." << std::endl;
                    }
                    
                    VM vm;
                    InterpretResult result = vm.run(&chunk);
                    
                    if (result == INTERPRET_COMPILE_ERROR) {
                        std::cerr << "Compilation error" << std::endl;
                    } else if (result == INTERPRET_RUNTIME_ERROR) {
                        std::cerr << "Runtime error" << std::endl;
                    }
                }
                break;
            }
        }
        
        // Memory dump (if requested)
        if (config.dumpMemory) {
            // Memory analysis would go here
            std::cout << "Memory analysis not yet implemented" << std::endl;
        }
        
    } catch (const GumusException& error) {
        JsonHata(error.type, error.what(), error.line);
        return;
    } catch (const LoxRuntimeException& error) {
        std::string finalMsg = error.what();
        
        // Hata Izi (Call Stack)
        if (!error.callstack.empty()) {
            finalMsg += "\n\nHata Izi (Traceback):\n";
            for (auto it = error.callstack.rbegin(); it != error.callstack.rend(); ++it) {
                finalMsg += "  -> " + *it + " icinde\n";
            }
        }
        
        // Gorsellestirme (Visual Pointer)
        if (!error.lineContent.empty() && error.column > 0) {
            finalMsg += "\n" + error.lineContent + "\n";
            for (int i = 1; i < error.column; ++i) finalMsg += " ";
            finalMsg += "^ Burası Gümüşhaneli!";
        }

        JsonHata("runtime_error", finalMsg, error.line, filename, error.suggestion);
        return;
    } catch (const std::exception& error) {
        JsonHata("system_error", error.what(), 0);
        return;
    }
    
    // Performance profiling
    if (config.enableProfiling) {
        auto endTime = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime);
        std::cout << "⏱️ Execution time: " << duration.count() << "ms" << std::endl;
    }
}

void runFile(const std::string& path) {
    // Security: Validate file path
    auto pathValidation = g_inputValidator.validateFilePath(path);
    if (pathValidation != InputValidator::ValidationResult::VALID) {
        std::cerr << "🔒 Security Error: " << g_inputValidator.getValidationError(pathValidation) << std::endl;
        exit(74);
    }
    
    // Security: Check if file access is allowed
    if (!g_securityContext.isPathAllowed(path)) {
        std::cerr << "🔒 Security Error: File access denied: " << path << std::endl;
        exit(74);
    }
    
    std::ifstream file(path);
    if (!file.is_open()) {
        std::cerr << "Could not open file: " << path << std::endl;
        exit(74);
    }
    
    std::string source((std::istreambuf_iterator<char>(file)),
                       std::istreambuf_iterator<char>());
    file.close();
    
    // Security: Validate source code content
    auto sourceValidation = g_inputValidator.validateString(source);
    if (sourceValidation != InputValidator::ValidationResult::VALID) {
        std::cerr << "🔒 Security Warning: " << g_inputValidator.getValidationError(sourceValidation) << std::endl;
        // Continue with sanitized source
        source = g_inputValidator.sanitizeString(source);
    }
    
    run(source, path);
}

void runPrompt() {
    std::string line;
    Interpreter interpreter; // Keep state between REPL commands
    
    std::cout << "GümüşDil REPL v2.0 (Bytecode VM) - 🔒 Security Enabled" << std::endl;
    std::cout << "Type 'exit' to quit." << std::endl;
    
    while (true) {
        std::cout << "> ";
        if (!std::getline(std::cin, line)) {
            break;
        }
        
        if (line == "exit" || line == "quit") {
            break;
        }
        
        if (line.empty()) {
            continue;
        }
        
        // Security: Validate REPL input
        auto inputValidation = g_inputValidator.validateString(line);
        if (inputValidation != InputValidator::ValidationResult::VALID) {
            std::cerr << "🔒 Security Warning: " << g_inputValidator.getValidationError(inputValidation) << std::endl;
            
            // For REPL, we can be more permissive but still sanitize
            if (inputValidation == InputValidator::ValidationResult::POTENTIAL_INJECTION ||
                inputValidation == InputValidator::ValidationResult::MALICIOUS_PATTERN) {
                std::cerr << "🔒 Input rejected for security reasons." << std::endl;
                continue;
            }
            
            // Sanitize and continue
            line = g_inputValidator.sanitizeString(line);
        }
        
        // Run in interpreter mode for REPL
        CompilationMode oldMode = config.mode;
        config.mode = CompilationMode::INTERPRETER;
        
        try {
            run(line, "<repl>");
        } catch (const SecurityException& e) {
            std::cerr << "🔒 Security Exception: " << e.what() << std::endl;
        }
        
        config.mode = oldMode;
    }
}

int main(int argc, char* argv[]) {
    // UTF-8 Support
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
#endif
    
    std::setlocale(LC_ALL, "tr_TR.UTF-8");
    
    // Initialize security framework
    g_securityContext.setTrustLevel(config.securityLevel);
    g_securityContext.allowOperation(SecurityContext::Operation::READ_FILE);
    g_securityContext.allowOperation(SecurityContext::Operation::EXECUTE_COMMAND);
    
    // Add safe paths for GümüşDil operations
    g_securityContext.addAllowedPath(".");
    g_securityContext.addAllowedPath("./lib");
    g_securityContext.addAllowedPath("./ornekler");
    g_securityContext.addAllowedPath("./src");
    
    // Block dangerous system paths
    g_securityContext.addBlockedPath("/etc");
    g_securityContext.addBlockedPath("/bin");
    g_securityContext.addBlockedPath("/sbin");
    g_securityContext.addBlockedPath("C:\\Windows");
    g_securityContext.addBlockedPath("C:\\System32");
    
    // Parse command line arguments
    if (!parseArguments(argc, argv)) {
        return 1;
    }
    
    // Update security context with parsed security level
    g_securityContext.setTrustLevel(config.securityLevel);
    
    // Find input file
    std::string inputFile;
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        if (!arg.empty() && arg[0] != '-') {
            inputFile = arg;
            break;
        }
    }
    
    if (inputFile.empty()) {
        // No file provided, start REPL
        runPrompt();
    } else {
        // Run file
        runFile(inputFile);
    }
    
    return 0;
}

