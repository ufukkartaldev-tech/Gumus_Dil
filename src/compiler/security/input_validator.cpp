#include "input_validator.h"
#include <algorithm>
#include <cctype>
#include <sstream>

InputValidator::InputValidator(const ValidationConfig& cfg) : config(cfg) {
    compilePatterns();
}

void InputValidator::compilePatterns() {
    // Compile blocked patterns
    blockedRegexes.clear();
    for (const auto& pattern : config.blockedPatterns) {
        try {
            blockedRegexes.emplace_back(pattern, std::regex_constants::icase);
        } catch (const std::regex_error&) {
            // Skip invalid patterns
        }
    }
    
    // Compile allowed patterns
    allowedRegexes.clear();
    for (const auto& pattern : config.allowedPatterns) {
        try {
            allowedRegexes.emplace_back(pattern, std::regex_constants::icase);
        } catch (const std::regex_error&) {
            // Skip invalid patterns
        }
    }
}

InputValidator::ValidationResult InputValidator::validateString(const std::string& input) {
    // Length check
    if (input.length() < config.minLength) {
        return ValidationResult::INVALID_LENGTH;
    }
    if (input.length() > config.maxLength) {
        return ValidationResult::INVALID_LENGTH;
    }
    
    // Encoding validation
    if (!isValidUTF8(input)) {
        return ValidationResult::ENCODING_ERROR;
    }
    
    // Null byte check
    if (containsNullBytes(input)) {
        return ValidationResult::INVALID_CHARACTERS;
    }
    
    // Control character check
    if (!config.allowUnicode && containsControlChars(input)) {
        return ValidationResult::INVALID_CHARACTERS;
    }
    
    // Injection pattern checks
    if (containsSQLInjection(input)) {
        return ValidationResult::POTENTIAL_INJECTION;
    }
    
    if (containsShellInjection(input)) {
        return ValidationResult::POTENTIAL_INJECTION;
    }
    
    if (containsPathTraversal(input)) {
        return ValidationResult::MALICIOUS_PATTERN;
    }
    
    if (containsXSS(input)) {
        return ValidationResult::MALICIOUS_PATTERN;
    }
    
    // Pattern matching
    if (matchesAnyPattern(input, blockedRegexes)) {
        return ValidationResult::MALICIOUS_PATTERN;
    }
    
    // If allowed patterns are specified, input must match at least one
    if (!allowedRegexes.empty() && !matchesAnyPattern(input, allowedRegexes)) {
        return ValidationResult::MALICIOUS_PATTERN;
    }
    
    return ValidationResult::VALID;
}

InputValidator::ValidationResult InputValidator::validateFilePath(const std::string& path) {
    // Basic string validation first
    auto result = validateString(path);
    if (result != ValidationResult::VALID) {
        return result;
    }
    
    // Path traversal check
    if (containsPathTraversal(path)) {
        return ValidationResult::MALICIOUS_PATTERN;
    }
    
    // Check for dangerous file extensions in strict mode
    if (config.strictMode) {
        std::string lowerPath = path;
        std::transform(lowerPath.begin(), lowerPath.end(), lowerPath.begin(), ::tolower);
        
        std::vector<std::string> dangerousExts = {
            ".exe", ".bat", ".cmd", ".com", ".scr", ".pif",
            ".dll", ".sys", ".vbs", ".js", ".jar", ".sh"
        };
        
        for (const auto& ext : dangerousExts) {
            if (lowerPath.size() >= ext.size() && 
                lowerPath.substr(lowerPath.size() - ext.size()) == ext) {
                return ValidationResult::MALICIOUS_PATTERN;
            }
        }
    }
    
    return ValidationResult::VALID;
}

InputValidator::ValidationResult InputValidator::validateSQLQuery(const std::string& query) {
    auto result = validateString(query);
    if (result != ValidationResult::VALID) {
        return result;
    }
    
    if (containsSQLInjection(query)) {
        return ValidationResult::POTENTIAL_INJECTION;
    }
    
    return ValidationResult::VALID;
}

InputValidator::ValidationResult InputValidator::validateShellCommand(const std::string& command) {
    auto result = validateString(command);
    if (result != ValidationResult::VALID) {
        return result;
    }
    
    if (containsShellInjection(command)) {
        return ValidationResult::POTENTIAL_INJECTION;
    }
    
    return ValidationResult::VALID;
}

InputValidator::ValidationResult InputValidator::validateVariableName(const std::string& name) {
    if (name.empty() || name.length() > 64) {
        return ValidationResult::INVALID_LENGTH;
    }
    
    // Must start with letter or underscore
    if (!std::isalpha(name[0]) && name[0] != '_') {
        return ValidationResult::INVALID_CHARACTERS;
    }
    
    // Rest must be alphanumeric or underscore
    for (size_t i = 1; i < name.length(); i++) {
        if (!std::isalnum(name[i]) && name[i] != '_') {
            return ValidationResult::INVALID_CHARACTERS;
        }
    }
    
    return ValidationResult::VALID;
}

InputValidator::ValidationResult InputValidator::validateFunctionName(const std::string& name) {
    return validateVariableName(name); // Same rules for now
}

std::string InputValidator::sanitizeString(const std::string& input) {
    std::string result;
    result.reserve(input.length());
    
    for (char c : input) {
        if (isSafeChar(c)) {
            result += c;
        } else if (c == '\t') {
            result += "    "; // Replace tab with spaces
        } else if (c == '\r' || c == '\n') {
            result += c; // Keep line breaks
        }
        // Skip other unsafe characters
    }
    
    return result;
}

std::string InputValidator::sanitizeFilePath(const std::string& path) {
    std::string result = path;
    
    // Remove path traversal sequences
    for (const auto& pattern : pathTraversalPatterns) {
        size_t pos = 0;
        while ((pos = result.find(pattern, pos)) != std::string::npos) {
            result.erase(pos, pattern.length());
        }
    }
    
    // Remove null bytes
    result.erase(std::remove(result.begin(), result.end(), '\0'), result.end());
    
    return result;
}

std::string InputValidator::sanitizeSQLString(const std::string& input) {
    std::string result = input;
    
    // Escape single quotes
    size_t pos = 0;
    while ((pos = result.find('\'', pos)) != std::string::npos) {
        result.replace(pos, 1, "''");
        pos += 2;
    }
    
    // Remove SQL comments
    pos = 0;
    while ((pos = result.find("--", pos)) != std::string::npos) {
        result.erase(pos, 2);
    }
    
    // Remove block comments
    pos = 0;
    while ((pos = result.find("/*", pos)) != std::string::npos) {
        size_t endPos = result.find("*/", pos + 2);
        if (endPos != std::string::npos) {
            result.erase(pos, endPos - pos + 2);
        } else {
            result.erase(pos);
            break;
        }
    }
    
    return result;
}

std::string InputValidator::sanitizeShellArgument(const std::string& arg) {
    std::string result;
    result.reserve(arg.length() * 2); // Reserve extra space for escaping
    
    for (char c : arg) {
        if (isAlphanumeric(c) || c == '.' || c == '_' || c == '-') {
            result += c;
        } else {
            // Escape special characters
            result += '\\';
            result += c;
        }
    }
    
    return result;
}

bool InputValidator::isValidUTF8(const std::string& input) {
    // Basic UTF-8 validation
    for (size_t i = 0; i < input.length(); ) {
        unsigned char c = input[i];
        
        if (c < 0x80) {
            // ASCII character
            i++;
        } else if ((c >> 5) == 0x06) {
            // 110xxxxx - 2 byte sequence
            if (i + 1 >= input.length() || (input[i + 1] & 0xC0) != 0x80) {
                return false;
            }
            i += 2;
        } else if ((c >> 4) == 0x0E) {
            // 1110xxxx - 3 byte sequence
            if (i + 2 >= input.length() || 
                (input[i + 1] & 0xC0) != 0x80 || 
                (input[i + 2] & 0xC0) != 0x80) {
                return false;
            }
            i += 3;
        } else if ((c >> 3) == 0x1E) {
            // 11110xxx - 4 byte sequence
            if (i + 3 >= input.length() || 
                (input[i + 1] & 0xC0) != 0x80 || 
                (input[i + 2] & 0xC0) != 0x80 || 
                (input[i + 3] & 0xC0) != 0x80) {
                return false;
            }
            i += 4;
        } else {
            return false;
        }
    }
    
    return true;
}

bool InputValidator::containsNullBytes(const std::string& input) {
    return input.find('\0') != std::string::npos;
}

bool InputValidator::containsControlChars(const std::string& input) {
    for (char c : input) {
        if (std::iscntrl(c) && c != '\t' && c != '\n' && c != '\r') {
            return true;
        }
    }
    return false;
}

bool InputValidator::containsSQLInjection(const std::string& input) {
    std::string upperInput = input;
    std::transform(upperInput.begin(), upperInput.end(), upperInput.begin(), ::toupper);
    
    for (const auto& keyword : sqlKeywords) {
        if (upperInput.find(keyword) != std::string::npos) {
            return true;
        }
    }
    
    // Check for SQL injection patterns
    std::vector<std::string> patterns = {
        "'", "\"", ";", "--", "/*", "*/", "xp_", "sp_",
        "union", "select", "insert", "update", "delete",
        "drop", "create", "alter", "exec", "execute"
    };
    
    for (const auto& pattern : patterns) {
        if (upperInput.find(pattern) != std::string::npos) {
            return true;
        }
    }
    
    return false;
}

bool InputValidator::containsShellInjection(const std::string& input) {
    for (const auto& meta : shellMetaChars) {
        if (input.find(meta) != std::string::npos) {
            return true;
        }
    }
    return false;
}

bool InputValidator::containsPathTraversal(const std::string& input) {
    for (const auto& pattern : pathTraversalPatterns) {
        if (input.find(pattern) != std::string::npos) {
            return true;
        }
    }
    return false;
}

bool InputValidator::containsXSS(const std::string& input) {
    std::string lowerInput = input;
    std::transform(lowerInput.begin(), lowerInput.end(), lowerInput.begin(), ::tolower);
    
    std::vector<std::string> xssPatterns = {
        "<script", "</script>", "javascript:", "vbscript:",
        "onload=", "onerror=", "onclick=", "onmouseover=",
        "eval(", "alert(", "document.cookie", "window.location"
    };
    
    for (const auto& pattern : xssPatterns) {
        if (lowerInput.find(pattern) != std::string::npos) {
            return true;
        }
    }
    
    return false;
}

void InputValidator::setConfig(const ValidationConfig& cfg) {
    config = cfg;
    compilePatterns();
}

void InputValidator::addBlockedPattern(const std::string& pattern) {
    config.blockedPatterns.push_back(pattern);
    compilePatterns();
}

void InputValidator::addAllowedPattern(const std::string& pattern) {
    config.allowedPatterns.push_back(pattern);
    compilePatterns();
}

std::string InputValidator::getValidationError(ValidationResult result) {
    switch (result) {
        case ValidationResult::VALID:
            return "Valid input";
        case ValidationResult::INVALID_LENGTH:
            return "Input length is invalid";
        case ValidationResult::INVALID_CHARACTERS:
            return "Input contains invalid characters";
        case ValidationResult::POTENTIAL_INJECTION:
            return "Input contains potential injection patterns";
        case ValidationResult::MALICIOUS_PATTERN:
            return "Input contains malicious patterns";
        case ValidationResult::ENCODING_ERROR:
            return "Input has encoding errors";
        default:
            return "Unknown validation error";
    }
}

bool InputValidator::matchesAnyPattern(const std::string& input, const std::vector<std::regex>& patterns) {
    for (const auto& pattern : patterns) {
        if (std::regex_search(input, pattern)) {
            return true;
        }
    }
    return false;
}

std::string InputValidator::normalizeString(const std::string& input) {
    std::string result = input;
    
    // Convert to lowercase for case-insensitive matching
    std::transform(result.begin(), result.end(), result.begin(), ::tolower);
    
    // Remove extra whitespace
    result = std::regex_replace(result, std::regex("\\s+"), " ");
    
    return result;
}

bool InputValidator::isAlphanumeric(char c) {
    return std::isalnum(c);
}

bool InputValidator::isSafeChar(char c) {
    return std::isprint(c) || c == '\t' || c == '\n' || c == '\r';
}

// SecureStringBuilder implementation
SecureStringBuilder::SecureStringBuilder(size_t maxSize) : maxSize(maxSize) {}

bool SecureStringBuilder::append(const std::string& str) {
    if (buffer.length() + str.length() > maxSize) {
        return false;
    }
    buffer += str;
    return true;
}

bool SecureStringBuilder::appendSafe(const std::string& str) {
    std::string sanitized = validator.sanitizeString(str);
    return append(sanitized);
}

bool SecureStringBuilder::appendEscaped(const std::string& str) {
    std::string escaped;
    escaped.reserve(str.length() * 2);
    
    for (char c : str) {
        if (c == '"' || c == '\'' || c == '\\') {
            escaped += '\\';
        }
        escaped += c;
    }
    
    return append(escaped);
}

std::string SecureStringBuilder::toString() const {
    return buffer;
}

void SecureStringBuilder::clear() {
    buffer.clear();
}

size_t SecureStringBuilder::size() const {
    return buffer.length();
}

bool SecureStringBuilder::isFull() const {
    return buffer.length() >= maxSize;
}

// SecurityContext implementation
SecurityContext::SecurityContext(TrustLevel level) : currentLevel(level) {}

bool SecurityContext::isOperationAllowed(Operation op) const {
    return allowedOperations.find(op) != allowedOperations.end();
}

bool SecurityContext::isPathAllowed(const std::string& path) const {
    // Check blocked paths first
    for (const auto& blocked : blockedPaths) {
        if (path.find(blocked) == 0) {
            return false;
        }
    }
    
    // If no allowed paths specified, allow all (except blocked)
    if (allowedPaths.empty()) {
        return true;
    }
    
    // Check allowed paths
    for (const auto& allowed : allowedPaths) {
        if (path.find(allowed) == 0) {
            return true;
        }
    }
    
    return false;
}

bool SecurityContext::canExecuteCommand(const std::string& command) const {
    if (!isOperationAllowed(Operation::EXECUTE_COMMAND)) {
        return false;
    }
    
    // Additional command-specific checks could go here
    return true;
}

void SecurityContext::setTrustLevel(TrustLevel level) {
    currentLevel = level;
    
    // Configure default permissions based on trust level
    allowedOperations.clear();
    
    switch (level) {
        case TrustLevel::UNTRUSTED:
            // No operations allowed
            break;
            
        case TrustLevel::LOW:
            allowedOperations.insert(Operation::READ_FILE);
            break;
            
        case TrustLevel::MEDIUM:
            allowedOperations.insert(Operation::READ_FILE);
            allowedOperations.insert(Operation::WRITE_FILE);
            allowedOperations.insert(Operation::EXECUTE_COMMAND);
            break;
            
        case TrustLevel::HIGH:
            allowedOperations.insert(Operation::READ_FILE);
            allowedOperations.insert(Operation::WRITE_FILE);
            allowedOperations.insert(Operation::EXECUTE_COMMAND);
            allowedOperations.insert(Operation::NETWORK_ACCESS);
            allowedOperations.insert(Operation::DATABASE_QUERY);
            break;
            
        case TrustLevel::SYSTEM:
            // All operations allowed
            allowedOperations.insert(Operation::READ_FILE);
            allowedOperations.insert(Operation::WRITE_FILE);
            allowedOperations.insert(Operation::EXECUTE_COMMAND);
            allowedOperations.insert(Operation::NETWORK_ACCESS);
            allowedOperations.insert(Operation::DATABASE_QUERY);
            allowedOperations.insert(Operation::SYSTEM_CALL);
            break;
    }
}

void SecurityContext::allowOperation(Operation op) {
    allowedOperations.insert(op);
}

void SecurityContext::blockOperation(Operation op) {
    allowedOperations.erase(op);
}

void SecurityContext::addAllowedPath(const std::string& path) {
    allowedPaths.push_back(path);
}

void SecurityContext::addBlockedPath(const std::string& path) {
    blockedPaths.push_back(path);
}