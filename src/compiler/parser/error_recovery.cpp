#include "error_recovery.h"
#include "../json_hata.h"

namespace gumus {
namespace compiler {
namespace parser {

void ErrorRecovery::handleGumusException(const GumusException& error) {
    parser->hadError = true;
    parser->advance(); // Consume the invalid token to prevent infinite loop
    
    if (error.line >= 0) {
        incrementErrorCount(error.line);
        
        if (shouldSkipLine(error.line)) {
            reportError(error.type, error.what(), error.line);
            reportWarning("Çok fazla hata - satır atlanıyor", error.line);
            synchronizeToNextStatement();
            return;
        }
    }
    
    reportError(error.type, error.what(), error.line);
    panicModeRecovery();
}

void ErrorRecovery::handleStdException(const std::exception& error) {
    parser->hadError = true;
    parser->advance(); // Consume the invalid token
    
    int currentLine = getCurrentLine();
    
    if (currentLine >= 0) {
        incrementErrorCount(currentLine);
        
        if (shouldSkipLine(currentLine)) {
            reportError("parser_error", error.what(), currentLine);
            reportWarning("Çok fazla hata - satır atlanıyor", currentLine);
            synchronizeToNextStatement();
            return;
        }
    }
    
    reportError("parser_error", error.what(), currentLine);
    panicModeRecovery();
}

void ErrorRecovery::panicModeRecovery() {
    while (!parser->isAtEnd()) {
        if (isAtSynchronizationPoint()) break;
        parser->advance();
    }
}

void ErrorRecovery::synchronizeToNextStatement() {
    while (!parser->isAtEnd()) {
        if (parser->previous().type == TokenType::SEMICOLON || 
            parser->previous().type == TokenType::NEW_LINE) break;
        if (isAtStatementStart()) break;
        parser->advance();
    }
}

void ErrorRecovery::skipToNextDeclaration() {
    while (!parser->isAtEnd()) {
        if (isAtDeclarationStart()) break;
        parser->advance();
    }
}

bool ErrorRecovery::shouldSkipLine(int line) {
    return getErrorCount(line) > MAX_ERRORS_PER_LINE;
}

void ErrorRecovery::incrementErrorCount(int line) {
    errorCountPerLine[line]++;
}

int ErrorRecovery::getErrorCount(int line) const {
    auto it = errorCountPerLine.find(line);
    return (it != errorCountPerLine.end()) ? it->second : 0;
}

bool ErrorRecovery::isAtSynchronizationPoint() const {
    return parser->previous().type == TokenType::SEMICOLON || 
           parser->previous().type == TokenType::NEW_LINE ||
           isAtDeclarationStart() ||
           isAtStatementStart();
}

bool ErrorRecovery::isAtDeclarationStart() const {
    return parser->check(TokenType::KW_VAR) || 
           parser->check(TokenType::KW_SINIF) || 
           parser->check(TokenType::KW_FONKSIYON) ||
           parser->check(TokenType::KW_MODUL);
}

bool ErrorRecovery::isAtStatementStart() const {
    return parser->check(TokenType::KW_EGER) ||
           parser->check(TokenType::KW_DONGU) ||
           parser->check(TokenType::KW_ICIN) ||
           parser->check(TokenType::KW_DENE) ||
           parser->check(TokenType::KW_DON) ||
           parser->check(TokenType::KW_KIR) ||
           parser->check(TokenType::KW_DEVAM) ||
           parser->check(TokenType::KW_YAZDIR) ||
           parser->check(TokenType::LBRACE);
}

int ErrorRecovery::getCurrentLine() const {
    if (!parser->tokens.empty() && parser->current > 0 && 
        parser->current <= (int)parser->tokens.size()) {
        return parser->tokens[parser->current - 1].line;
    }
    return 0;
}

void ErrorRecovery::reportError(const std::string& type, const std::string& message, int line) {
    JsonHata(type, message, line);
}

void ErrorRecovery::reportWarning(const std::string& message, int line) {
    JsonHata("parser_warning", message, line);
}

} // namespace parser
} // namespace compiler  
} // namespace gumus