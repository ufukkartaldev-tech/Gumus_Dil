#ifndef LSP_SERVER_H
#define LSP_SERVER_H

#include <string>

class LSPServer {
public:
    void run();

private:
    void handleRequest(const std::string& method, const std::string& params, const std::string& id);
    void handleNotification(const std::string& method, const std::string& params);
    void sendResponse(const std::string& id, const std::string& result);
    void sendNotification(const std::string& method, const std::string& params);
    
    // Core LSP logic
    void publishDiagnostics(const std::string& uri, const std::string& content);
};

#endif
