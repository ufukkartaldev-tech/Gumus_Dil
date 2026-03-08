#include "lsp_server.h"
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <map>
#include <algorithm>
#include "lexer/tokenizer.h"
#include "parser/parser.h"
#include "semantic/resolver.h"
#include "interpreter/interpreter.h"
#include "json_hata.h"

#ifdef _WIN32
#include <io.h>
#include <fcntl.h>
#endif

void LSPServer::run() {
#ifdef _WIN32
    _setmode(_fileno(stdin), _O_BINARY);
    _setmode(_fileno(stdout), _O_BINARY);
#endif

    std::string line;
    while (std::getline(std::cin, line)) {
        if (line.substr(0, 16) == "Content-Length: ") {
            int length = std::stoi(line.substr(16));
            std::getline(std::cin, line); // Read empty line \r\n

            std::vector<char> buffer(length);
            std::cin.read(buffer.data(), length);
            std::string body(buffer.begin(), buffer.end());

            // Very crude JSON parsing for demonstration
            // In a real scenario, use a JSON library
            std::string method = "";
            size_t methodPos = body.find("\"method\":\"");
            if (methodPos != std::string::npos) {
                size_t start = methodPos + 10;
                size_t end = body.find("\"", start);
                method = body.substr(start, end - start);
            }

            std::string id = "";
            size_t idPos = body.find("\"id\":");
            if (idPos != std::string::npos) {
                size_t start = idPos + 5;
                if (body[start] == '"') {
                    start++;
                    size_t end = body.find("\"", start);
                    id = body.substr(start, end - start);
                } else {
                    size_t end = body.find_first_of(",}", start);
                    id = body.substr(start, end - start);
                }
            }

            if (!id.empty()) {
                handleRequest(method, body, id);
            } else {
                handleNotification(method, body);
            }
        }
    }
}

void LSPServer::handleRequest(const std::string& method, const std::string& params, const std::string& id) {
    if (method == "initialize") {
        std::string result = "{\"capabilities\":{"
                             "\"textDocumentSync\":1,"
                             "\"hoverProvider\":true,"
                             "\"definitionProvider\":true"
                             "}}";
        sendResponse(id, result);
    } else if (method == "shutdown") {
        sendResponse(id, "null");
    }
}

void LSPServer::handleNotification(const std::string& method, const std::string& params) {
    if (method == "textDocument/didOpen" || method == "textDocument/didChange" || method == "textDocument/didSave") {
        // Extract URI and context
        size_t uriPos = params.find("\"uri\":\"");
        if (uriPos == std::string::npos) return;
        size_t start = uriPos + 7;
        size_t end = params.find("\"", start);
        std::string uri = params.substr(start, end - start);

        // For didChange, it's more complex, but let's assume we get the full text for simplicity
        // in a basic implementation or if we use textDocumentSync: 1 (Full)
        size_t textPos = params.find("\"text\":\"");
        if (textPos != std::string::npos) {
            size_t tStart = textPos + 8;
            size_t tEnd = params.find("\"", tStart);
            std::string content = params.substr(tStart, tEnd - tStart);
            
            // Unescape simple JSON escapes (demonstration)
            std::string unescaped = "";
            for (size_t i = 0; i < content.length(); ++i) {
                if (content[i] == '\\' && i + 1 < content.length()) {
                    if (content[i+1] == 'n') { unescaped += '\n'; i++; }
                    else if (content[i+1] == '"') { unescaped += '"'; i++; }
                    else if (content[i+1] == '\\') { unescaped += '\\'; i++; }
                    else unescaped += content[i];
                } else {
                    unescaped += content[i];
                }
            }

            publishDiagnostics(uri, unescaped);
        }
    }
}

void LSPServer::sendResponse(const std::string& id, const std::string& result) {
    std::string body = "{\"jsonrpc\":\"2.0\",\"id\":" + id + ",\"result\":" + result + "}";
    std::cout << "Content-Length: " << body.length() << "\r\n\r\n" << body << std::flush;
}

void LSPServer::sendNotification(const std::string& method, const std::string& params) {
    std::string body = "{\"jsonrpc\":\"2.0\",\"method\":\"" + method + "\",\"params\":" + params + "}";
    std::cout << "Content-Length: " << body.length() << "\r\n\r\n" << body << std::flush;
}

void LSPServer::publishDiagnostics(const std::string& uri, const std::string& content) {
    std::stringstream errorStream;
    std::streambuf* oldCerr = std::cerr.rdbuf(errorStream.rdbuf());

    try {
        Interpreter interpreter;
        Tokenizer tokenizer(content);
        std::vector<Token> tokens = tokenizer.tokenize();
        Parser parser(tokens, interpreter.astArena);
        std::vector<Stmt*> statements = parser.parse();
        
        Resolver resolver(interpreter);
        resolver.resolve(statements);
    } catch (...) {
        // Errors are captured in errorStream
    }

    std::cerr.rdbuf(oldCerr);

    std::string line;
    std::string diagnostics = "";
    bool first = true;
    while (std::getline(errorStream, line)) {
        if (line.empty()) continue;
        if (!first) diagnostics += ",";
        
        // The errors are already JSON: {"type": "...", "line": 1, "message": "..."}
        // We need to transform them to LSP Diagnostic format:
        // {"range": {"start": {"line": L-1, "character": 0}, "end": {"line": L-1, "character": 100}}, "severity": 1, "message": "..."}
        
        // Simple extraction for demonstration
        size_t linePos = line.find("\"line\": ");
        int lineNum = 0;
        if (linePos != std::string::npos) {
            lineNum = std::stoi(line.substr(linePos + 8));
        }

        size_t msgPos = line.find("\"message\": \"");
        std::string msg = "";
        if (msgPos != std::string::npos) {
            size_t start = msgPos + 12;
            size_t end = line.find("\"", start);
            msg = line.substr(start, end - start);
        }

        diagnostics += "{\"range\":{\"start\":{\"line\":" + std::to_string(std::max(0, lineNum - 1)) + ",\"character\":0},"
                       "\"end\":{\"line\":" + std::to_string(std::max(0, lineNum - 1)) + ",\"character\":100}},"
                       "\"severity\":1,\"message\":\"" + msg + "\"}";
        first = false;
    }

    std::string diagnosticParams = "{\"uri\":\"" + uri + "\",\"diagnostics\":[" + diagnostics + "]}";
    sendNotification("textDocument/publishDiagnostics", diagnosticParams);
}
