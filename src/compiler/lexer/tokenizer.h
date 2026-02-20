#ifndef TOKENIZER_H
#define TOKENIZER_H

#include <string>
#include <vector>
#include "token.h"

class Tokenizer {
public:
    Tokenizer(const std::string& source);
    std::vector<Token> tokenize();

private:
    std::string source;
    int position;
    int line;
    int column;

    char peek(int offset = 0) const;
    char advance();
    bool isAtEnd() const;
    
    void skipWhitespace();
    Token scanToken();
    bool match(char expected);
    Token number();
    Token string();
    Token identifier();
    void scanTemplateString(std::vector<Token>& tokens);
};

#endif // TOKENIZER_H
