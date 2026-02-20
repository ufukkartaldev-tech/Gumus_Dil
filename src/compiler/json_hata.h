#ifndef JSON_HATA_H
#define JSON_HATA_H

#include <string>
#include <iostream>
#include <stdexcept>

struct GumusException : public std::runtime_error {
    std::string type;
    int line;

    GumusException(const std::string& type, int line, const std::string& message)
        : std::runtime_error(message), type(type), line(line) {}
};

inline std::string JsonEscape(const std::string& s) {
    std::string out;
    out.reserve(s.size());
    for (char c : s) {
        switch (c) {
            case '\\': out += "\\\\"; break;
            case '"': out += "\\\""; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default:
                if (static_cast<unsigned char>(c) < 0x20) {
                    out += ' ';
                } else {
                    out += c;
                }
                break;
        }
    }
    return out;
}

inline void JsonHata(const std::string& type, const std::string& message, int line, const std::string& file, const std::string& suggestion) {
    std::cerr << "{\"type\": \"" << JsonEscape(type) << "\", \"line\": " << line
              << ", \"message\": \"" << JsonEscape(message) << "\"";
    if (!file.empty()) {
        std::cerr << ", \"file\": \"" << JsonEscape(file) << "\"";
    }
    if (!suggestion.empty()) {
        std::cerr << ", \"suggestion\": \"" << JsonEscape(suggestion) << "\"";
    }
    std::cerr << "}\n";
}

inline void JsonHata(const std::string& type, const std::string& message, int line, const std::string& file) {
    JsonHata(type, message, line, file, "");
}

inline void JsonHata(const std::string& type, const std::string& message, int line) {
    JsonHata(type, message, line, "", "");
}

#endif
