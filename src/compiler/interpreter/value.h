#ifndef VALUE_H
#define VALUE_H

#include <string>
#include <vector>
#include <map>
#include <iostream>
#include <memory> 
#include <sstream>
#include <iomanip>

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
    MAP,
    UNDEFINED
};

struct Value;
using ValueList = std::vector<Value>;

/**
 * @brief GümüşDil Değer (Value) Yapısı
 * 
 * Bellek kullanımını minimize etmek için 'union' ve 'shared_ptr' kullanır.
 * Küçük değerler (int, float, bool) doğrudan stack'te tutulurken,
 * karmaşık nesneler (string, liste, harita, nesne) Heap'te tutulur.
 */
struct Value {
    ValueType type;
    union {
        int intVal;
        double floatVal;
        bool boolVal;
    };
    std::shared_ptr<void> obj; // Heap nesneleri için genel işaretçi
    
    // 🗑️ Garbage Collection Desteği
    bool isMarked = false;
    std::vector<std::shared_ptr<Value>> references; // GC için referanslar
    mutable size_t refCount = 0; // Reference counting için

    // Kurucular
    Value() : type(ValueType::NIL), floatVal(0.0) {}
    explicit Value(ValueType t) : type(t), floatVal(0.0) {}
    Value(int v) : type(ValueType::INTEGER), intVal(v) {}
    Value(double v) : type(ValueType::FLOAT), floatVal(v) {}
    Value(bool v) : type(ValueType::BOOLEAN), boolVal(v) {}
    Value(std::string v) : type(ValueType::STRING), obj(std::make_shared<std::string>(v)) {}
    Value(std::shared_ptr<ValueList> v) : type(ValueType::LIST), obj(v) {}
    Value(std::shared_ptr<std::map<std::string, Value>> v) : type(ValueType::MAP), obj(v) {}
    Value(std::shared_ptr<void> o, ValueType t, std::string n = "") : type(t), obj(o) {
        // Not: 'name' meta-verisi artık nesnenin kendisinden alınmalıdır.
    }

    // Yardımcı Erişim Metotları
    std::string& getString() const { return *std::static_pointer_cast<std::string>(obj); }
    ValueList& getList() const { return *std::static_pointer_cast<ValueList>(obj); }
    std::map<std::string, Value>& getMap() const { return *std::static_pointer_cast<std::map<std::string, Value>>(obj); }

    // 📊 Bellek Analizi ve Optimizasyon
    size_t getSize() const {
        switch (type) {
            case ValueType::INTEGER: return sizeof(int);
            case ValueType::FLOAT: return sizeof(double);
            case ValueType::BOOLEAN: return sizeof(bool);
            case ValueType::STRING: return obj ? getString().size() + sizeof(std::string) : 0;
            case ValueType::LIST: return obj ? getList().size() * sizeof(Value) + sizeof(ValueList) : 0;
            case ValueType::MAP: return obj ? getMap().size() * 32 + sizeof(std::map<std::string, Value>) : 0;
            case ValueType::CLASS:
            case ValueType::INSTANCE:
            case ValueType::FUNCTION: return 100; // Tahmini nesne boyutu
            case ValueType::NIL:
            default: return 0;
        }
    }

    // 🎯 Memory optimization methods
    void optimize() {
        switch (type) {
            case ValueType::STRING:
                if (obj) {
                    auto& str = getString();
                    str.shrink_to_fit();
                }
                break;
            case ValueType::LIST:
                if (obj) {
                    auto& list = getList();
                    list.shrink_to_fit();
                }
                break;
            case ValueType::MAP:
                // Maps don't have shrink_to_fit, but we can rehash
                break;
            default:
                break;
        }
    }

    bool equals(const Value& other) const {
        if (type != other.type) return false;
        
        switch (type) {
            case ValueType::INTEGER: return intVal == other.intVal;
            case ValueType::FLOAT: return floatVal == other.floatVal;
            case ValueType::BOOLEAN: return boolVal == other.boolVal;
            case ValueType::NIL: return true;
            case ValueType::STRING: 
                return obj && other.obj && getString() == other.getString();
            case ValueType::LIST:
                if (!obj || !other.obj) return obj == other.obj;
                return getList() == other.getList();
            case ValueType::MAP:
                if (!obj || !other.obj) return obj == other.obj;
                return getMap() == other.getMap();
            default:
                return obj == other.obj;
        }
    }

    // 🔄 Copy and move semantics for better memory management
    Value(const Value& other) : type(other.type), obj(other.obj), isMarked(false), refCount(0) {
        switch (type) {
            case ValueType::INTEGER: intVal = other.intVal; break;
            case ValueType::FLOAT: floatVal = other.floatVal; break;
            case ValueType::BOOLEAN: boolVal = other.boolVal; break;
            default: break;
        }
    }

    Value(Value&& other) noexcept : type(other.type), obj(std::move(other.obj)), isMarked(false), refCount(0) {
        switch (type) {
            case ValueType::INTEGER: intVal = other.intVal; break;
            case ValueType::FLOAT: floatVal = other.floatVal; break;
            case ValueType::BOOLEAN: boolVal = other.boolVal; break;
            default: break;
        }
        other.type = ValueType::NIL;
    }

    Value& operator=(const Value& other) {
        if (this != &other) {
            type = other.type;
            obj = other.obj;
            isMarked = false;
            refCount = 0;
            
            switch (type) {
                case ValueType::INTEGER: intVal = other.intVal; break;
                case ValueType::FLOAT: floatVal = other.floatVal; break;
                case ValueType::BOOLEAN: boolVal = other.boolVal; break;
                default: break;
            }
        }
        return *this;
    }

    Value& operator=(Value&& other) noexcept {
        if (this != &other) {
            type = other.type;
            obj = std::move(other.obj);
            isMarked = false;
            refCount = 0;
            
            switch (type) {
                case ValueType::INTEGER: intVal = other.intVal; break;
                case ValueType::FLOAT: floatVal = other.floatVal; break;
                case ValueType::BOOLEAN: boolVal = other.boolVal; break;
                default: break;
            }
            
            other.type = ValueType::NIL;
        }
        return *this;
    }

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
            case ValueType::UNDEFINED: return "Undefined";
            default: return "Unknown";
        }
    }

    std::string toString() const {
        switch (type) {
            case ValueType::INTEGER: return std::to_string(intVal);
            case ValueType::FLOAT: {
                std::ostringstream ss;
                ss.imbue(std::locale::classic());
                ss << floatVal;
                return ss.str();
            }
            case ValueType::STRING: return getString();
            case ValueType::BOOLEAN: return boolVal ? "dogru" : "yanlis";
            case ValueType::LIST: {
                std::string s = "[";
                const auto& list = getList();
                for (size_t i = 0; i < list.size(); ++i) {
                    s += list[i].toString();
                    if (i < list.size() - 1) s += ", ";
                }
                s += "]";
                return s;
            }
            case ValueType::MAP: {
                std::string s = "{";
                const auto& map = getMap();
                bool first = true;
                for (const auto& pair : map) {
                    if (!first) s += ", ";
                    s += "\"" + pair.first + "\": " + pair.second.toString();
                    first = false;
                }
                s += "}";
                return s;
            }
            case ValueType::CLASS: return "<sinif>";
            case ValueType::INSTANCE: return "<nesne>";
            case ValueType::FUNCTION: return "<fonksiyon>";
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
            case ValueType::UNDEFINED: return "Tanımsız";
            default: return "Bilinmeyen";
        }
    }

    std::string getCategory() const {
        switch (type) {
            case ValueType::INTEGER:
            case ValueType::FLOAT:
            case ValueType::BOOLEAN:
            case ValueType::NIL: return "Basit";
            case ValueType::STRING: return "Metin";
            case ValueType::LIST:
            case ValueType::MAP: return "Karmaşık";
            case ValueType::UNDEFINED: return "Hata";
            default: return "Nesne/Heap";
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
        
        void* addr = obj.get();
        if (type == ValueType::LIST) {
            json += "\"size\": " + std::to_string(getList().size()) + ", ";
            json += "\"elements\": [";
            const auto& list = getList();
            for (size_t i = 0; i < list.size(); ++i) {
                json += list[i].toJson();
                if (i < list.size() - 1) json += ", ";
            }
            json += "], ";
        }
        else if (type == ValueType::MAP) {
            json += "\"size\": " + std::to_string(getMap().size()) + ", ";
            json += "\"items\": {";
            bool first = true;
            for (const auto& pair : getMap()) {
                if (!first) json += ", ";
                json += "\"" + pair.first + "\": " + pair.second.toJson();
                first = false;
            }
            json += "}, ";
        }
        else if (type == ValueType::STRING) {
            json += "\"length\": " + std::to_string(getString().length()) + ", ";
        }
        
        std::stringstream ss;
        if (addr) ss << addr;
        else ss << "0";
        
        std::string addrStr = ss.str();
        if (addrStr.find("0x") == std::string::npos && addrStr != "0") addrStr = "0x" + addrStr;

        json += "\"address\": \"" + addrStr + "\"";
        json += "}";
        return json;
    }
};

// 🔧 Utility functions
std::string valueTypeName(ValueType type);

#endif // VALUE_H

