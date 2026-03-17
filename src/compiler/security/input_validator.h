#ifndef INPUT_VALIDATOR_H
#define INPUT_VALIDATOR_H

#include <string>
#include <vector>
#include <regex>
#include <unordered_set>

// 🛡️ Input Validation Framework

class InputValidator {
public:
    enum class ValidationResult {
        VALID,
        INVALID_LENGTH,
        INVALID_CHARACTERS,
        POTENTIAL_INJECTION,
        MALICIOUS_PATTERN,
        ENCODING_ERROR
    };
    
    struct ValidationConfig {
        size_t maxLength = 1024;
        size_t minLength = 0;
        bool allowUnicode = true;
        bool allowSpecialChars = false;
        bool strictMode = false;
        std::vector<std::string> blockedPatterns;
        std::vector<std::string> allowedPatterns;
    };
    
private:
    ValidationConfig config;
    std::vector<std::regex> blockedRegexes;
    std::vector<std::regex> allowedRegexes;
    
    // SQL Injection patterns
    std::unordered_set<std::string> sqlKeywords = {
        "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
        "UNION", "JOIN", "WHERE", "ORDER", "GROUP", "HAVING", "EXEC",
        "EXECUTE", "DECLARE", "CAST", "CONVERT", "SUBSTRING", "CHAR",
        "ASCII", "WAITFOR", "DELAY", "BENCHMARK", "SLEEP"
    };
    
    // Shell injection patterns
    std::unordered_set<std::string> shellMetaChars = {
        ";", "&", "|", "`", "$", "(", ")", "{", "}", "[", "]",
        "<", ">", "&&", "||", ">>", "<<", "2>", "2>&1"
    };
    
    // Path traversal patterns
    std::vector<std::string> pathTraversalPatterns = {
        "../", "..\\", "/..", "\\..", "%2e%2e", "%252e%252e",
        "..%2f", "..%5c", "%2e%2e%2f", "%2e%2e%5c"
    };
    
public:
    InputValidator(const ValidationConfig& cfg = ValidationConfig{});
    
    // Main validation functions
    ValidationResult validateString(const std::string& input);
    ValidationResult validateFilePath(const std::string& path);
    ValidationResult validateSQLQuery(const std::string& query);
    ValidationResult validateShellCommand(const std::string& command);
    ValidationResult validateVariableName(const std::string& name);
    ValidationResult validateFunctionName(const std::string& name);
    
    // Sanitization functions
    std::string sanitizeString(const std::string& input);
    std::string sanitizeFilePath(const std::string& path);
    std::string sanitizeSQLString(const std::string& input);
    std::string sanitizeShellArgument(const std::string& arg);
    
    // Encoding validation
    bool isValidUTF8(const std::string& input);
    bool containsNullBytes(const std::string& input);
    bool containsControlChars(const std::string& input);
    
    // Pattern matching
    bool containsSQLInjection(const std::string& input);
    bool containsShellInjection(const std::string& input);
    bool containsPathTraversal(const std::string& input);
    bool containsXSS(const std::string& input);
    
    // Configuration
    void setConfig(const ValidationConfig& cfg);
    void addBlockedPattern(const std::string& pattern);
    void addAllowedPattern(const std::string& pattern);
    
    // Error reporting
    std::string getValidationError(ValidationResult result);
    
private:
    void compilePatterns();
    bool matchesAnyPattern(const std::string& input, const std::vector<std::regex>& patterns);
    std::string normalizeString(const std::string& input);
    bool isAlphanumeric(char c);
    bool isSafeChar(char c);
};

// 🔒 Secure String Builder
class SecureStringBuilder {
private:
    std::string buffer;
    size_t maxSize;
    InputValidator validator;
    
public:
    SecureStringBuilder(size_t maxSize = 4096);
    
    bool append(const std::string& str);
    bool appendSafe(const std::string& str);
    bool appendEscaped(const std::string& str);
    
    std::string toString() const;
    void clear();
    size_t size() const;
    bool isFull() const;
};

// 🛡️ Security Context
class SecurityContext {
public:
    enum class TrustLevel {
        UNTRUSTED = 0,
        LOW = 1,
        MEDIUM = 2,
        HIGH = 3,
        SYSTEM = 4
    };
    
    enum class Operation {
        READ_FILE,
        WRITE_FILE,
        EXECUTE_COMMAND,
        NETWORK_ACCESS,
        DATABASE_QUERY,
        SYSTEM_CALL
    };
    
private:
    TrustLevel currentLevel;
    std::unordered_set<Operation> allowedOperations;
    std::vector<std::string> allowedPaths;
    std::vector<std::string> blockedPaths;
    
public:
    SecurityContext(TrustLevel level = TrustLevel::UNTRUSTED);
    
    bool isOperationAllowed(Operation op) const;
    bool isPathAllowed(const std::string& path) const;
    bool canExecuteCommand(const std::string& command) const;
    
    void setTrustLevel(TrustLevel level);
    void allowOperation(Operation op);
    void blockOperation(Operation op);
    void addAllowedPath(const std::string& path);
    void addBlockedPath(const std::string& path);
    
    TrustLevel getTrustLevel() const { return currentLevel; }
};

// 🚨 Security Exception
class SecurityException : public std::exception {
private:
    std::string message;
    std::string operation;
    std::string input;
    
public:
    SecurityException(const std::string& msg, const std::string& op = "", const std::string& inp = "")
        : message(msg), operation(op), input(inp) {}
    
    const char* what() const noexcept override {
        return message.c_str();
    }
    
    const std::string& getOperation() const { return operation; }
    const std::string& getInput() const { return input; }
};

#endif // INPUT_VALIDATOR_H