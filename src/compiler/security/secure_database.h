#ifndef SECURE_DATABASE_H
#define SECURE_DATABASE_H

#include "input_validator.h"
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>

// 🛡️ Secure Database Interface

class SecureDatabase {
public:
    enum class QueryType {
        SELECT,
        INSERT,
        UPDATE,
        DELETE,
        CREATE,
        DROP,
        ALTER
    };
    
    struct QueryResult {
        bool success;
        std::string error;
        std::vector<std::unordered_map<std::string, std::string>> rows;
        int affectedRows = 0;
    };
    
    struct PreparedStatement {
        std::string query;
        std::vector<std::string> parameters;
        QueryType type;
    };
    
private:
    std::string connectionString;
    bool connected = false;
    InputValidator validator;
    SecurityContext securityContext;
    
    // Prepared statements cache
    std::unordered_map<std::string, PreparedStatement> preparedStatements;
    
    // Query whitelist for additional security
    std::vector<std::string> allowedTables;
    std::vector<std::string> allowedColumns;
    bool useWhitelist = false;
    
public:
    SecureDatabase(SecurityContext::TrustLevel trustLevel = SecurityContext::TrustLevel::MEDIUM);
    
    // Connection management
    bool connect(const std::string& connectionStr);
    void disconnect();
    bool isConnected() const { return connected; }
    
    // Secure query execution
    QueryResult executeQuery(const std::string& query);
    QueryResult executePrepared(const std::string& statementId, const std::vector<std::string>& params);
    
    // Prepared statements
    bool prepareStatement(const std::string& id, const std::string& query);
    bool bindParameter(const std::string& statementId, int index, const std::string& value);
    
    // Safe query builders
    QueryResult select(const std::string& table, const std::vector<std::string>& columns = {},
                      const std::string& whereClause = "", const std::vector<std::string>& params = {});
    
    QueryResult insert(const std::string& table, const std::unordered_map<std::string, std::string>& data);
    
    QueryResult update(const std::string& table, const std::unordered_map<std::string, std::string>& data,
                      const std::string& whereClause, const std::vector<std::string>& params = {});
    
    QueryResult deleteFrom(const std::string& table, const std::string& whereClause,
                          const std::vector<std::string>& params = {});
    
    // Security configuration
    void enableWhitelist(bool enable) { useWhitelist = enable; }
    void addAllowedTable(const std::string& table);
    void addAllowedColumn(const std::string& column);
    void setTrustLevel(SecurityContext::TrustLevel level);
    
    // Validation helpers
    bool isValidTableName(const std::string& name);
    bool isValidColumnName(const std::string& name);
    bool isQueryAllowed(const std::string& query);
    
private:
    // Internal validation
    bool validateQuery(const std::string& query);
    bool validateTableAccess(const std::string& table);
    bool validateColumnAccess(const std::string& column);
    
    // Query parsing
    QueryType parseQueryType(const std::string& query);
    std::vector<std::string> extractTableNames(const std::string& query);
    std::vector<std::string> extractColumnNames(const std::string& query);
    
    // Parameter escaping
    std::string escapeParameter(const std::string& param);
    std::string buildParameterizedQuery(const std::string& query, const std::vector<std::string>& params);
    
    // Error handling
    QueryResult createErrorResult(const std::string& error);
    void logSecurityViolation(const std::string& query, const std::string& reason);
};

// 🔒 Database Connection Pool (for future use)
class SecureDatabasePool {
private:
    std::vector<std::unique_ptr<SecureDatabase>> connections;
    size_t maxConnections;
    size_t currentIndex = 0;
    
public:
    SecureDatabasePool(size_t maxConn = 10) : maxConnections(maxConn) {}
    
    std::shared_ptr<SecureDatabase> getConnection();
    void releaseConnection(std::shared_ptr<SecureDatabase> conn);
    void closeAll();
};

// 🛡️ ORM-style Safe Query Builder
class SafeQueryBuilder {
private:
    std::string tableName;
    std::vector<std::string> selectColumns;
    std::vector<std::string> whereConditions;
    std::vector<std::string> parameters;
    std::unordered_map<std::string, std::string> updateData;
    std::string orderBy;
    std::string groupBy;
    int limitCount = -1;
    int offsetCount = -1;
    
    InputValidator validator;
    
public:
    SafeQueryBuilder(const std::string& table);
    
    // Query building methods
    SafeQueryBuilder& select(const std::vector<std::string>& columns = {});
    SafeQueryBuilder& where(const std::string& condition, const std::string& param = "");
    SafeQueryBuilder& whereEquals(const std::string& column, const std::string& value);
    SafeQueryBuilder& whereIn(const std::string& column, const std::vector<std::string>& values);
    SafeQueryBuilder& whereLike(const std::string& column, const std::string& pattern);
    SafeQueryBuilder& orderBy(const std::string& column, bool ascending = true);
    SafeQueryBuilder& groupBy(const std::string& column);
    SafeQueryBuilder& limit(int count);
    SafeQueryBuilder& offset(int count);
    
    // Update/Insert methods
    SafeQueryBuilder& set(const std::string& column, const std::string& value);
    SafeQueryBuilder& setMultiple(const std::unordered_map<std::string, std::string>& data);
    
    // Query generation
    std::string buildSelect();
    std::string buildInsert();
    std::string buildUpdate();
    std::string buildDelete();
    
    // Parameter access
    const std::vector<std::string>& getParameters() const { return parameters; }
    
    // Validation
    bool validate();
    
private:
    void addParameter(const std::string& param);
    std::string escapeIdentifier(const std::string& identifier);
    bool isValidIdentifier(const std::string& identifier);
};

#endif // SECURE_DATABASE_H