#ifdef _MSC_VER
#pragma execution_character_set("utf-8")
#endif

#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <cstring>
#include <clocale>
// Windows header moved down
#include "lexer/tokenizer.h"
#include "lexer/token.h"
#include "parser/parser.h"
#include "parser/ast.h"
#include "interpreter/interpreter.h"
#include "semantic/resolver.h"
#include "json_hata.h"
#include "debug.h"
#include <chrono>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

// Global interpreter instance to keep state (variables, functions) alive in REPL
// MOVED inside runPrompt and runFile to avoid global static initialization order fiasco potentially

void run(Interpreter& interpreter, const std::string& source, bool dumpAst, bool dumpMemory = false) {
    std::vector<Token> tokens;
    std::vector<std::shared_ptr<Stmt>> statements;

    try {
        // 1. Lexer (Sozcuk Analizi)
        Tokenizer tokenizer(source);
        tokens = tokenizer.tokenize();

        // 2. Parser (Sozdizimi Analizi)
        Parser parser(tokens);
        statements = parser.parse();
        if (parser.hasError()) {
            return;
        }

        // 3. Resolver (Semantik Analiz - Değişken Çözümleme)
        Resolver resolver(interpreter);
        resolver.resolve(statements);

    } catch (const GumusException& error) {
        JsonHata(error.type, error.what(), error.line);
        return;
    } catch (const std::exception& error) {
        JsonHata("system_error", error.what(), 0);
        return;
    }
    
    // DEBUG: Tokenlari yazdir
    if (gumus_debug) {
        for (const auto& t : tokens) {
            std::cout << "Token: " << t.toString() << "\n";
        }
    }

    // Hata varsa dur (Simdilik exception firlatiyorlar, yakalamak lazim ama Tokenizer genelde firlatmaz)
    
    // AST Dump istegi varsa JSON bas ve cik
    if (dumpAst) {
        std::cout << "[";
        for (size_t i = 0; i < statements.size(); ++i) {
            std::cout << statements[i]->toJson();
            if (i < statements.size() - 1) std::cout << ", ";
        }
        std::cout << "]\n";
        return;
    }

    // 3. Interpreter (Yorumlayici)
    if (!statements.empty()) {
        try {
            interpreter.interpret(statements);
        } catch (const LoxRuntimeException& error) {
            std::string msg = error.isSystemError ? std::string(error.what()) : error.errorValue.toString();
            JsonHata("runtime_error", msg, error.line, "", error.suggestion);
        } catch (const std::exception& error) {
             JsonHata("system_error", error.what(), 0);
        }
    }

    if (dumpMemory) {
        std::cout << "\n__MEMORY_JSON_START__\n";
        if (interpreter.environment != nullptr) {
            std::cout << interpreter.environment->toJson();
        } else {
            std::cout << "{}";
        }
        std::cout << "\n__MEMORY_JSON_END__\n";
    }
}

void runFile(const std::string& path, bool dumpAst, bool dumpMemory) {
    // Binary modda açıp BOM kontrolü ve temizliği yapalım
    std::ifstream file(path, std::ios::binary);
    if (!file.is_open()) {
        JsonHata("file_error", "Dosya okunamadi: " + path, 0);
        exit(1); 
    }

    std::stringstream buffer;
    buffer << file.rdbuf();
    std::string content = buffer.str();
    
    // UTF-8 BOM Kontrolü (EF BB BF)
    if (content.size() >= 3 && 
        (unsigned char)content[0] == 0xEF && 
        (unsigned char)content[1] == 0xBB && 
        (unsigned char)content[2] == 0xBF) {
        content.erase(0, 3); // BOM sil
    }

    Interpreter interpreter;
    run(interpreter, content, dumpAst, dumpMemory);
}

void runPrompt() {
    std::cout << "Turkce Programlama Dili (v2.0) - Kodlamaya Hos Geldiniz!\n";
    std::cout << "Yeni Ozellikler: rastgele(), zaman(), karekok(), tip() ve duzeltmeler.\n";
    std::cout << "Cikmak icin CTRL+C veya dosya sonu (EOF) gonderin.\n";
    std::cout << "--------------------------------------------------\n";
    
    Interpreter interpreter;
    std::string line;
    while (true) {
        std::cout << "> ";
        if (!std::getline(std::cin, line)) break; // EOF check
        if (line.empty()) continue;
        run(interpreter, line, false);
    }
}

int main(int argc, char* argv[]) {
    setlocale(LC_ALL, ".UTF8");
    #ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    #endif
    // Argument parsing
    if (argc == 1) {
        runPrompt();
        return 0;
    }

    bool dumpAst = false;
    bool dumpMemory = false;
    bool debug = false;
    std::string filename;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--dump-ast") {
            dumpAst = true;
        } else if (arg == "--dump-memory") {
            dumpMemory = true;
        } else if (arg == "--debug" || arg == "--hata-ayikla") {
            debug = true;
        } else {
            filename = arg;
        }
    }

    gumus_debug = debug;
    gumus_memory_dump = dumpMemory;

    if (!filename.empty()) {

        std::chrono::steady_clock::time_point start;
        if (debug) start = std::chrono::steady_clock::now();

        runFile(filename, dumpAst, dumpMemory);

        if (debug) {
            auto end = std::chrono::steady_clock::now();
            auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
            std::cout << "[DEBUG] Program " << ms << " ms icinde tamamlandi.\n";
        }
    } else {
        std::cout << "Kullanim:\n";
        std::cout << "  program [dosya.tr]                  : Dosyayi calistir\n";
        std::cout << "  program --dump-ast [dosya.tr]       : AST JSON ciktisi al\n"; 
        std::cout << "  program --dump-memory [dosya.tr]    : Bellek durumu dökümü al\n";
        std::cout << "  program --debug [dosya.tr]          : Debug ciktilari goster\n";
        return 64;
    }

    return 0;
}
