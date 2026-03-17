#include "value.h"

// 🔧 Utility function implementations
std::string valueTypeName(ValueType type) {
    switch (type) {
        case ValueType::INTEGER: return "Integer";
        case ValueType::FLOAT: return "Float";
        case ValueType::STRING: return "String";
        case ValueType::LIST: return "List";
        case ValueType::BOOLEAN: return "Boolean";
        case ValueType::NIL: return "Nil";
        case ValueType::CLASS: return "Class";
        case ValueType::INSTANCE: return "Instance";
        case ValueType::FUNCTION: return "Function";
        case ValueType::MAP: return "Map";
        case ValueType::UNDEFINED: return "Undefined";
        default: return "Unknown";
    }
}

// 🎯 Global debug flag
extern bool gumus_debug;