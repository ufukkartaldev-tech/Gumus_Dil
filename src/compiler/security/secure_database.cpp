#include "secure_database.h"
#include <iostream>
#include <algorithm>

SecureDatabase::SecureDatabase(SecurityContext::TrustLevel trustLevel) 
    : securityContext(trustLevel) {}

bool SecureDatabase::connect(const std::string& connectionStr) {
    // Validate connection string
    auto validation = validator.validateString(connectionStr);
    if (validation != InputValidator::ValidationResult::VALID) {
        return false;
    }
    
    // Check if database operations are allowed
    if (!securityContext.isOperationAllowed(SecurityContext::Operation::DATABASE_QUERY)) {
        return false;
    }
    
    connectionString = connectionStr;
    connected = true;
    
    std::cout << "[SECURE DB] Connected to database (simulated)" << std::endl;
    return true;
}

void SecureDatabase::disconnect() {
    connected = false;
    connectionString.clear();
    std::cout << "[SECURE DB] Disconnected from database" << std::endl;
}

SecureDatabase::QueryResult SecureDatabase::executeQuery(const std::string& query) {
    if (!connected) {
        return createErrorResult("Database not connected");
    }
    
    if (!validateQuery(query)) {
        logSecurityViolation(query, "Query validation failed");
        return createErrorResult("Query validation failed");
    }
    
    // Simulate query execution
    QueryResult result;
    result.success = true;
    result.affectedRows = 1;
    
    // Add sample data
    std::unordered_map<std::string, std::string> row;
    row["id"] = "1";
    row["name"] = "test";
    result.rows.push_back(row);
    
    return result;
}

SecureDatabase::QueryResult SecureDatabase::executePrepared(const std::string& statementId, 
                                                           const std::vector<std::string>& params) {
    if (!connected) {
        return createErrorResult("Database not connected");
    }
    
    auto it = preparedStatements.find(statementId);
    if (it == preparedStatements.end()) {
        return createErrorResult("Prepared statement not found");
    }
    
    // Validate parameters
    for (const auto& param : params) {
        auto validation = validator.validateString(param);
        if (validation != InputValidator::ValidationResult::VALID) {
            return createErrorResult("Parameter validation failed");
        }
    }
    
    // Build and execute query
    std::string query = buildParameterizedQuery(it->second.query, params);
    return executeQuery(query);
}

bool SecureDatabase::prepareStatement(const std::string& id, const std::string& query) {
    if (!validateQuery(query)) {
        return false;
    }
    
    PreparedStatement stmt;
    stmt.query = query;
    stmt.type = parseQueryType(query);
    
    preparedStatements[id] = stmt;
    return true;
}

bool SecureDatabase::bindParameter(const std::string& statementId, int index, const std::string& value) {
    auto it = preparedStatements.find(statementId);
    if (it == preparedStatements.end()) {
        return false;
    }
    
    // Validate parameter value
    auto validation = validator.validateString(value);
    if (validation != InputValidator::ValidationResult::VALID) {
        return false;
    }
    
    // Ensure parameters vector is large enough
    if (it->second.parameters.size() <= static_cast<size_t>(index)) {
        it->second.parameters.resize(index + 1);
    }
    
    it->second.parameters[index] = escapeParameter(value);
    return true;
}

SecureDatabase::QueryResult SecureDatabase::select(const std::string& table, 
                                                  const std::vector<std::string>& columns,
                                                  const std::string& whereClause, 
                                                  const std::vector<std::string>& params) {
    if (!isValidTableName(table)) {
        return createErrorResult("Invalid table name");
    }
    
    // Validate columns
    for (const auto& col : columns) {
        if (!isValidColumnName(col)) {
            return createErrorResult("Invalid column name: " + col);
        }
    }
    
    // Build query
    std::string query = "SELECT ";
    if (columns.empty()) {
        query += "*";
    } else {
        for (size_t i = 0; i < columns.size(); i++) {
            if (i > 0) query += ", ";
            query += columns[i];
        }
    }
    query += " FROM " + table;
    
    if (!whereClause.empty()) {
        query += " WHERE " + whereClause;
    }
    
    return executeQuery(buildParameterizedQuery(query, params));
}

SecureDatabase::QueryResult SecureDatabase::insert(const std::string& table, 
                                                  const std::unordered_map<std::string, std::string>& data) {
    if (!isValidTableName(table)) {
        return createErrorResult("Invalid table name");
    }
    
    std::string query = "INSERT INTO " + table + " (";
    std::string values = " VALUES (";
    
    bool first = true;
    for (const auto& pair : data) {
        if (!isValidColumnName(pair.first)) {
            return createErrorResult("Invalid column name: " + pair.first);
        }
        
        if (!first) {
            query += ", ";
            values += ", ";
        }
        query += pair.first;
        values += "'" + escapeParameter(pair.second) + "'";
        first = false;
    }
    
    query += ")" + values + ")";
    return executeQuery(query);
}

SecureDatabase::QueryResult SecureDatabase::update(const std::string& table, 
                                                  const std::unordered_map<std::string, std::string>& data,
                                                  const std::string& whereClause, 
                                                  const std::vector<std::string>& params) {
    if (!isValidTableName(table)) {
        return createErrorResult("Invalid table name");
    }
    
    std::string query = "UPDATE " + table + " SET ";
    
    bool first = true;
    for (const auto& pair : data) {
        if (!isValidColumnName(pair.first)) {
            return createErrorResult("Invalid column name: " + pair.first);
        }
        
        if (!first) query += ", ";
        query += pair.first + " = '" + escapeParameter(pair.second) + "'";
        first = false;
    }
    
    if (!whereClause.empty()) {
        query += " WHERE " + whereClause;
    }
    
    return executeQuery(buildParameterizedQuery(query, params));
}

SecureDatabase::QueryResult SecureDatabase::deleteFrom(const std::string& table, 
                                                      const std::string& whereClause,
                                                      const std::vector<std::string>& params) {
    if (!isValidTableName(table)) {
        return createErrorResult("Invalid table name");
    }
    
    std::string query = "DELETE FROM " + table;
    
    if (!whereClause.empty()) {
        query += " WHERE " + whereClause;
    }
    
    return executeQuery(buildParameterizedQuery(query, params));
}

void SecureDatabase::addAllowedTable(const std::string& table) {
    allowedTables.push_back(table);
}

void SecureDatabase::addAllowedColumn(const std::string& column) {
    allowedColumns.push_back(column);
}

void SecureDatabase::setTrustLevel(SecurityContext::TrustLevel level) {
    securityContext.setTrustLevel(level);
}

bool SecureDatabase::isValidTableName(const std::string& name) {
    if (name.empty() || name.length() > 64) {
        return false;
    }
    
    // Check whitelist if enabled
    if (useWhitelist && !allowedTables.empty()) {
        return std::find(allowedTables.begin(), allowedTables.end(), name) != allowedTables.end();
    }
    
    // Basic validation: alphanumeric and underscore only
    for (char c : name) {
        if (!std::isalnum(c) && c != '_') {
            return false;
        }
    }
    
    return true;
}

bool SecureDatabase::isValidColumnName(const std::string& name) {
    return isValidTableName(name); // Same rules for now
}

bool SecureDatabase::isQueryAllowed(const std::string& query) {
    return validateQuery(query);
}

bool SecureDatabase::validateQuery(const std::string& query) {
    auto validation = validator.validateSQLQuery(query);
    return validation == InputValidator::ValidationResult::VALID;
}

bool SecureDatabase::validateTableAccess(const std::string& table) {
    return isValidTableName(table);
}

bool SecureDatabase::validateColumnAccess(const std::string& column) {
    return isValidColumnName(column);
}

SecureDatabase::QueryType SecureDatabase::parseQueryType(const std::string& query) {
    std::string upperQuery = query;
    std::transform(upperQuery.begin(), upperQuery.end(), upperQuery.begin(), ::toupper);
    
    if (upperQuery.find("SELECT") == 0) return QueryType::SELECT;
    if (upperQuery.find("INSERT") == 0) return QueryType::INSERT;
    if (upperQuery.find("UPDATE") == 0) return QueryType::UPDATE;
    if (upperQuery.find("DELETE") == 0) return QueryType::DELETE;
    if (upperQuery.find("CREATE") == 0) return QueryType::CREATE;
    if (upperQuery.find("DROP") == 0) return QueryType::DROP;
    if (upperQuery.find("ALTER") == 0) return QueryType::ALTER;
    
    return QueryType::SELECT; // Default
}

std::vector<std::string> SecureDatabase::extractTableNames(const std::string& query) {
    // Simplified table name extraction
    std::vector<std::string> tables;
    // This would need a proper SQL parser for production use
    return tables;
}

std::vector<std::string> SecureDatabase::extractColumnNames(const std::string& query) {
    // Simplified column name extraction
    std::vector<std::string> columns;
    // This would need a proper SQL parser for production use
    return columns;
}

std::string SecureDatabase::escapeParameter(const std::string& param) {
    std::string escaped = param;
    
    // Escape single quotes
    size_t pos = 0;
    while ((pos = escaped.find('\'', pos)) != std::string::npos) {
        escaped.replace(pos, 1, "''");
        pos += 2;
    }
    
    return escaped;
}

std::string SecureDatabase::buildParameterizedQuery(const std::string& query, 
                                                   const std::vector<std::string>& params) {
    std::string result = query;
    
    for (size_t i = 0; i < params.size(); i++) {
        std::string placeholder = "?" + std::to_string(i + 1);
        size_t pos = result.find(placeholder);
        if (pos != std::string::npos) {
            result.replace(pos, placeholder.length(), "'" + escapeParameter(params[i]) + "'");
        }
    }
    
    return result;
}

SecureDatabase::QueryResult SecureDatabase::createErrorResult(const std::string& error) {
    QueryResult result;
    result.success = false;
    result.error = error;
    result.affectedRows = 0;
    return result;
}

void SecureDatabase::logSecurityViolation(const std::string& query, const std::string& reason) {
    std::cerr << "[SECURITY VIOLATION] Database query blocked: " << reason << std::endl;
    std::cerr << "[QUERY] " << query.substr(0, 100) << "..." << std::endl;
}

// SafeQueryBuilder implementation
SafeQueryBuilder::SafeQueryBuilder(const std::string& table) : tableName(table) {}

SafeQueryBuilder& SafeQueryBuilder::select(const std::vector<std::string>& columns) {
    selectColumns = columns;
    return *this;
}

SafeQueryBuilder& SafeQueryBuilder::where(const std::string& condition, const std::string& param) {
    whereConditions.push_back(condition);
    if (!param.empty()) {
        addParameter(param);
    }
    return *this;
}

SafeQueryBuilder& SafeQueryBuilder::whereEquals(const std::string& column, const std::string& value) {
    whereConditions.push_back(column + " = ?");
    addParameter(value);
    return *this;
}

SafeQueryBuilder& SafeQueryBuilder::whereIn(const std::string& column, const std::vector<std::string>& values) {
    std::string condition = column + " IN (";
    for (size_t i = 0; i < values.size(); i++) {
        if (i > 0) condition += ", ";
        condition += "?";
        addParameter(values[i]);
    }
    condition += ")";
    whereConditions.push_back(condition);
    return *this;
}

SafeQueryBuilder& SafeQueryBuilder::whereLike(const std::string& column, const std::string& pattern) {
    whereConditions.push_back(column + " LIKE ?");
    addParameter(pattern);
    return *this;
}

SafeQueryBuilder& SafeQueryBuilder::orderBy(const std::string& column, bool ascending) {
    orderBy = column + (ascending ? " ASC" : " DESC");
    return *this;
}

SafeQueryBuilder& SafeQueryBuilder::groupBy(const std::string& column) {
    groupBy = column;
    return *this;
}

SafeQueryBuilder& SafeQueryBuilder::limit(int count) {
    limitCount = count;
    return *this;
}

SafeQueryBuilder& SafeQueryBuilder::offset(int count) {
    offsetCount = count;
    return *this;
}

SafeQueryBuilder& SafeQueryBuilder::set(const std::string& column, const std::string& value) {
    updateData[column] = value;
    return *this;
}

SafeQueryBuilder& SafeQueryBuilder::setMultiple(const std::unordered_map<std::string, std::string>& data) {
    for (const auto& pair : data) {
        updateData[pair.first] = pair.second;
    }
    return *this;
}

std::string SafeQueryBuilder::buildSelect() {
    std::string query = "SELECT ";
    
    if (selectColumns.empty()) {
        query += "*";
    } else {
        for (size_t i = 0; i < selectColumns.size(); i++) {
            if (i > 0) query += ", ";
            query += escapeIdentifier(selectColumns[i]);
        }
    }
    
    query += " FROM " + escapeIdentifier(tableName);
    
    if (!whereConditions.empty()) {
        query += " WHERE ";
        for (size_t i = 0; i < whereConditions.size(); i++) {
            if (i > 0) query += " AND ";
            query += whereConditions[i];
        }
    }
    
    if (!groupBy.empty()) {
        query += " GROUP BY " + escapeIdentifier(groupBy);
    }
    
    if (!orderBy.empty()) {
        query += " ORDER BY " + orderBy;
    }
    
    if (limitCount > 0) {
        query += " LIMIT " + std::to_string(limitCount);
    }
    
    if (offsetCount > 0) {
        query += " OFFSET " + std::to_string(offsetCount);
    }
    
    return query;
}

std::string SafeQueryBuilder::buildInsert() {
    if (updateData.empty()) {
        return "";
    }
    
    std::string query = "INSERT INTO " + escapeIdentifier(tableName) + " (";
    std::string values = " VALUES (";
    
    bool first = true;
    for (const auto& pair : updateData) {
        if (!first) {
            query += ", ";
            values += ", ";
        }
        query += escapeIdentifier(pair.first);
        values += "?";
        addParameter(pair.second);
        first = false;
    }
    
    query += ")" + values + ")";
    return query;
}

std::string SafeQueryBuilder::buildUpdate() {
    if (updateData.empty()) {
        return "";
    }
    
    std::string query = "UPDATE " + escapeIdentifier(tableName) + " SET ";
    
    bool first = true;
    for (const auto& pair : updateData) {
        if (!first) query += ", ";
        query += escapeIdentifier(pair.first) + " = ?";
        addParameter(pair.second);
        first = false;
    }
    
    if (!whereConditions.empty()) {
        query += " WHERE ";
        for (size_t i = 0; i < whereConditions.size(); i++) {
            if (i > 0) query += " AND ";
            query += whereConditions[i];
        }
    }
    
    return query;
}

std::string SafeQueryBuilder::buildDelete() {
    std::string query = "DELETE FROM " + escapeIdentifier(tableName);
    
    if (!whereConditions.empty()) {
        query += " WHERE ";
        for (size_t i = 0; i < whereConditions.size(); i++) {
            if (i > 0) query += " AND ";
            query += whereConditions[i];
        }
    }
    
    return query;
}

bool SafeQueryBuilder::validate() {
    return isValidIdentifier(tableName);
}

void SafeQueryBuilder::addParameter(const std::string& param) {
    parameters.push_back(param);
}

std::string SafeQueryBuilder::escapeIdentifier(const std::string& identifier) {
    // Simple identifier escaping - surround with backticks
    return "`" + identifier + "`";
}

bool SafeQueryBuilder::isValidIdentifier(const std::string& identifier) {
    if (identifier.empty() || identifier.length() > 64) {
        return false;
    }
    
    for (char c : identifier) {
        if (!std::isalnum(c) && c != '_') {
            return false;
        }
    }
    
    return true;
}