#include "error_suggestion.h"
#include <algorithm>
#include <vector>

namespace gumus {
namespace compiler {
namespace interpreter {

std::string ErrorSuggestion::suggestVariable(const std::string& name) const {
    if (name.size() < MIN_NAME_LENGTH) return "";
    
    std::vector<std::string> candidates;
    
    // Collect variable names from current environment
    if (interpreter->environment != nullptr) {
        for (const auto& kv : interpreter->environment->values) {
            candidates.push_back(kv.first);
        }
    }
    
    return findBestMatch(name, candidates);
}

std::string ErrorSuggestion::suggestFunction(const std::string& name) const {
    if (name.size() < MIN_NAME_LENGTH) return "";
    
    std::vector<std::string> candidates;
    
    // Collect function names
    for (const auto& kv : interpreter->functions) {
        candidates.push_back(kv.first);
    }
    
    return findBestMatch(name, candidates);
}

std::string ErrorSuggestion::suggestMethod(const std::string& className, const std::string& methodName) const {
    // This would require access to class definitions
    // Implementation depends on how classes are stored in interpreter
    return "";
}

int ErrorSuggestion::calculateDistance(const std::string& a, const std::string& b) {
    const size_t n = a.size();
    const size_t m = b.size();
    
    if (n == 0) return (int)m;
    if (m == 0) return (int)n;
    
    std::vector<int> prev(m + 1), cur(m + 1);
    
    // Initialize first row
    for (size_t j = 0; j <= m; ++j) {
        prev[j] = (int)j;
    }
    
    // Fill the matrix
    for (size_t i = 1; i <= n; ++i) {
        cur[0] = (int)i;
        
        for (size_t j = 1; j <= m; ++j) {
            int cost = (a[i - 1] == b[j - 1]) ? 0 : 1;
            int deletion = prev[j] + 1;
            int insertion = cur[j - 1] + 1;
            int substitution = prev[j - 1] + cost;
            
            cur[j] = std::min({deletion, insertion, substitution});
        }
        
        prev.swap(cur);
    }
    
    return prev[m];
}

bool ErrorSuggestion::isAcceptableSuggestion(const std::string& name, const std::string& candidate, int distance) const {
    if (name.size() < MIN_NAME_LENGTH) return false;
    if (candidate.empty()) return false;
    if (name[0] != candidate[0]) return false; // First character must match
    
    const int maxLen = (int)std::max(name.size(), candidate.size());
    
    // For short names, allow only 1 character difference
    if (maxLen <= 4) return distance <= 1;
    
    // For longer names, check distance and ratio
    if (distance > MAX_SUGGESTION_DISTANCE) return false;
    if ((double)distance / (double)maxLen > MAX_DISTANCE_RATIO) return false;
    
    return true;
}

std::string ErrorSuggestion::findBestMatch(const std::string& name, const std::vector<std::string>& candidates) const {
    std::string best;
    int bestDistance = 999999;
    
    for (const std::string& candidate : candidates) {
        int distance = calculateDistance(name, candidate);
        
        if (isAcceptableSuggestion(name, candidate, distance) && distance < bestDistance) {
            bestDistance = distance;
            best = candidate;
        }
    }
    
    return best;
}

} // namespace interpreter
} // namespace compiler  
} // namespace gumus