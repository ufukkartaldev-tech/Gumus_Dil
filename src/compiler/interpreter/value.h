#ifndef VALUE_H
#define VALUE_H

#include <string>
#include <vector>
#include <map>
#include <variant>
#include <iostream>
#include <memory> 
#include <sstream>

enum class ValueType {
    INTEGER,
    FLOAT,
    STRING,
    LIST,
    BOOLEAN,
    NIL,
    CLASS,
    INSTANCE,
    FUNCTION,
    MAP
};

struct Value;

using ValueList = std::vector<Value>;

struct Value {
    ValueType type;
    int intVal = 0;
    double floatVal = 0.0;
    std::string stringVal;
    std::shared_ptr<ValueList> listVal;
    std::shared_ptr<std::map<std::string, Value>> mapVal;
    bool boolVal = false;
    std::shared_ptr<void> obj; // Stores LoxClass or LoxInstance
    std::string name; // Meta-data for objects (Function name, Class name, Instance info)
    std::string internalState; // JSON representation of internal fields (for Instances)
    
    // 🗑️ Garbage Collection Support
    bool isMarked = false;
    
    // 📊 Memory Analytics
    size_t getSize() const {
        switch (type) {
            case ValueType::INTEGER: return sizeof(int);
            case ValueType::FLOAT: return sizeof(double);
            case ValueType::BOOLEAN: return sizeof(bool);
            case ValueType::STRING: return stringVal.size();
            case ValueType::LIST: 
                return listVal ? listVal->size() * sizeof(Value) : 0;
            case ValueType::MAP:
                return mapVal ? mapVal->size() * sizeof(std::pair<std::string, Value>) : 0;
            case ValueType::CLASS:
            case ValueType::INSTANCE:
            case ValueType::FUNCTION:
                return sizeof(void*) + name.size();
            case ValueType::NIL:
            default:
                return 0;
        }
    }

    Value() : type(ValueType::NIL) {}
    Value(int v) : type(ValueType::INTEGER), intVal(v) {}
    Value(double v) : type(ValueType::FLOAT), floatVal(v) {}
    Value(std::string v) : type(ValueType::STRING), stringVal(v) {}
    Value(bool v) : type(ValueType::BOOLEAN), boolVal(v) {}
    Value(std::shared_ptr<ValueList> v) : type(ValueType::LIST), listVal(v) {}
    Value(std::shared_ptr<std::map<std::string, Value>> v) : type(ValueType::MAP), mapVal(v) {}
    Value(std::shared_ptr<void> o, ValueType t, std::string n = "") : type(t), obj(o), name(n) {} // For Class/Instance

    // 🏷️ Type name helper
    static std::string valueTypeName(ValueType type) {
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
            default: return "Unknown";
        }
    }

    std::string toString() const {
        switch (type) {
            case ValueType::INTEGER: return std::to_string(intVal);
            case ValueType::FLOAT: {
                std::ostringstream ss;
                ss.imbue(std::locale::classic()); // Force dot as decimal separator
                ss << floatVal;
                return ss.str();
            }
            case ValueType::STRING: return stringVal;
            case ValueType::BOOLEAN: return boolVal ? "dogru" : "yanlis";
            case ValueType::LIST: {
                std::string s = "[";
                if (listVal) {
                    for (size_t i = 0; i < listVal->size(); ++i) {
                        s += (*listVal)[i].toString();
                        if (i < listVal->size() - 1) s += ", ";
                    }
                }
                s += "]";
                return s;
            }
            case ValueType::CLASS: return name.empty() ? "<sinif>" : "<sinif " + name + ">";

            case ValueType::INSTANCE: return name.empty() ? "<nesne>" : name + " nesnesi";
            case ValueType::FUNCTION: return name.empty() ? "<fonksiyon>" : "<fonksiyon " + name + ">";
            case ValueType::MAP: {
                std::string s = "{";
                if (mapVal) {
                    bool first = true;
                    for (const auto& pair : *mapVal) {
                        if (!first) s += ", ";
                        s += "\"" + pair.first + "\": " + pair.second.toString();
                        first = false;
                    }
                }
                s += "}";
                return s;
            }
            case ValueType::NIL: return "nil";
        }
        return "";
    }

    std::string getTypeName() const {
        switch (type) {
            case ValueType::INTEGER: return "Tamsayı";
            case ValueType::FLOAT: return "Ondalıklı";
            case ValueType::STRING: return "Metin";
            case ValueType::BOOLEAN: return "Mantıksal";
            case ValueType::LIST: return "Liste";
            case ValueType::MAP: return "Sözlük";
            case ValueType::CLASS: return "Sınıf";
            case ValueType::INSTANCE: return "Nesne";
            case ValueType::FUNCTION: return "Fonksiyon";
            case ValueType::NIL: return "Boş";
            default: return "Bilinmeyen";
        }
    }

    std::string getCategory() const {
        switch (type) {
            case ValueType::INTEGER:
            case ValueType::FLOAT:
            case ValueType::BOOLEAN:
            case ValueType::NIL:
                return "Basit";
            case ValueType::STRING:
                return "Metin";
            case ValueType::LIST:
            case ValueType::MAP:
                return "Karmaşık";
            case ValueType::CLASS:
            case ValueType::INSTANCE:
            case ValueType::FUNCTION:
                return "Nesne/Heap";
            default:
                return "Bilinmeyen";
        }
    }

    std::string toJson() const {
        std::string json = "{";
        json += "\"type\": \"" + getTypeName() + "\", ";
        json += "\"category\": \"" + getCategory() + "\", ";
        
        std::string valStr = toString();
        std::string escaped;
        for (char c : valStr) {
            if (c == '"') escaped += "\\\"";
            else if (c == '\\') escaped += "\\\\";
            else if (c == '\n') escaped += "\\n";
            else if (c == '\r') escaped += "\\r";
            else if (c == '\t') escaped += "\\t";
            else escaped += c;
        }
        json += "\"value\": \"" + escaped + "\", ";
        
        void* addr = nullptr;
        if (type == ValueType::LIST) {
            addr = listVal.get();
            json += "\"size\": " + (listVal ? std::to_string(listVal->size()) : "0") + ", ";
            json += "\"elements\": [";
            if (listVal) {
                for (size_t i = 0; i < listVal->size(); ++i) {
                    json += (*listVal)[i].toJson();
                    if (i < listVal->size() - 1) json += ", ";
                }
            }
            json += "], ";
        }
        else if (type == ValueType::MAP) {
            addr = mapVal.get();
            json += "\"size\": " + (mapVal ? std::to_string(mapVal->size()) : "0") + ", ";
            json += "\"items\": {";
            if (mapVal) {
                bool first = true;
                for (const auto& pair : *mapVal) {
                    if (!first) json += ", ";
                    json += "\"" + pair.first + "\": " + pair.second.toJson();
                    first = false;
                }
            }
            json += "}, ";
        }
        else if (type == ValueType::STRING) {
            json += "\"length\": " + std::to_string(stringVal.length()) + ", ";
        }
        else if (type == ValueType::INSTANCE || type == ValueType::CLASS || type == ValueType::FUNCTION) {
            addr = obj.get();
            json += "\"details\": \"" + (!name.empty() ? name : toString()) + "\", ";
            if (!internalState.empty()) {
                json += "\"fields\": " + internalState + ", ";
            }
        }
        
        std::stringstream ss;
        if (addr) ss << addr; // Hex format varsayilan sstream davranisidir (0x ekler bazen)
        else ss << "0";
        
        std::string addrStr = ss.str();
        if (addrStr.find("0x") == std::string::npos && addrStr != "0") addrStr = "0x" + addrStr;

        json += "\"address\": \"" + addrStr + "\"";
        json += "}";
        return json;
    }


};


#endif // VALUE_H
