#ifndef VALUE_H
#define VALUE_H

#include <string>
#include <vector>
#include <map>
#include <iostream>
#include <memory>
#include <sstream>
#include <iomanip>

// Forward declaration - dairesel bagimliligi onler
class GarbageCollector;

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

enum class ObjectType {
    OBJ_STRING,
    OBJ_LIST,
    OBJ_MAP,
    OBJ_CLASS,
    OBJ_INSTANCE,
    OBJ_FUNCTION,
    OBJ_NATIVE
};

struct GumusObject {
    ObjectType objType;
    bool isMarked;
    GumusObject* next; // GC zinciri

    GumusObject(ObjectType type) : objType(type), isMarked(false), next(nullptr) {}
    virtual ~GumusObject() = default;
    // Polimorfik mark: GC referansini alir, g_gc kullanmaz
    virtual void mark(GarbageCollector* gc) {}
};

struct Value;
using ValueList = std::vector<Value>;

struct GumusString : public GumusObject {
    std::string str;
    GumusString(const std::string& str) : GumusObject(ObjectType::OBJ_STRING), str(str) {}
};

struct GumusList : public GumusObject {
    ValueList elements;
    GumusList() : GumusObject(ObjectType::OBJ_LIST) {}
    void mark(GarbageCollector* gc) override;
};

struct GumusMap : public GumusObject {
    std::map<std::string, Value> items;
    GumusMap() : GumusObject(ObjectType::OBJ_MAP) {}
    void mark(GarbageCollector* gc) override;
};

// Object Macros to safely extract types
// IS_OBJ: sadece gercek heap nesneleri icin true - BOOLEAN ve NIL dahil edilmez!
#define IS_OBJ(value)       ((value).type == ValueType::STRING || \
                             (value).type == ValueType::LIST   || \
                             (value).type == ValueType::MAP    || \
                             (value).type == ValueType::CLASS  || \
                             (value).type == ValueType::INSTANCE || \
                             (value).type == ValueType::FUNCTION)
#define AS_OBJ(value)       ((value).as.obj)
#define AS_STRING(value)    ((GumusString*)AS_OBJ(value))
#define AS_CSTRING(value)   (((GumusString*)AS_OBJ(value))->str)
#define AS_LIST(value)      ((GumusList*)AS_OBJ(value))
#define AS_MAP(value)       ((GumusMap*)AS_OBJ(value))

/**
 * @brief GümüşDil Değer (Value) Yapısı - RAW POINTER REVISION
 * 
 * shared_ptr tamamen kaldirildi! Object tabanli Mark-and-Sweep modeli kullanilir.
 */
struct Value {
    ValueType type;
    union {
        int intVal;
        double floatVal;
        bool boolVal;
        GumusObject* obj; // Heap nesneleri için RAW işaretçi
    } as;
    
    // Kurucular
    Value() : type(ValueType::NIL) { as.floatVal = 0.0; }
    explicit Value(ValueType t) : type(t) { as.floatVal = 0.0; }
    Value(int v) : type(ValueType::INTEGER) { as.intVal = v; }
    Value(double v) : type(ValueType::FLOAT) { as.floatVal = v; }
    Value(bool v) : type(ValueType::BOOLEAN) { as.boolVal = v; }
    
    // GumusObject* ham isaretci ile nesne referansi (GC zincirine dahil)
    Value(GumusObject* o, ValueType t) : type(t) { as.obj = o; }

    // Yardimci Erisim Metotlari
    std::string& getString() const { return AS_STRING(*this)->str; }
    ValueList& getList() const { return AS_LIST(*this)->elements; }
    std::map<std::string, Value>& getMap() const { return AS_MAP(*this)->items; }

    // 📊 Bellek Analizi ve Optimizasyon
    size_t getSize() const {
        switch (type) {
            case ValueType::INTEGER: return sizeof(int);
            case ValueType::FLOAT: return sizeof(double);
            case ValueType::BOOLEAN: return sizeof(bool);
            case ValueType::STRING: return as.obj ? AS_CSTRING(*this).size() + sizeof(GumusString) : 0;
            case ValueType::LIST: return as.obj ? getList().size() * sizeof(Value) + sizeof(GumusList) : 0;
            case ValueType::MAP: return as.obj ? getMap().size() * 32 + sizeof(GumusMap) : 0;
            case ValueType::CLASS:
            case ValueType::INSTANCE:
            case ValueType::FUNCTION: return 100; // Tahmini nesne boyutu
            case ValueType::NIL:
            default: return 0;
        }
    }

    void optimize() {}

    bool equals(const Value& other) const {
        if (type != other.type) return false;
        
        switch (type) {
            case ValueType::INTEGER: return as.intVal == other.as.intVal;
            case ValueType::FLOAT: return as.floatVal == other.as.floatVal;
            case ValueType::BOOLEAN: return as.boolVal == other.as.boolVal;
            case ValueType::NIL: return true;
            case ValueType::STRING: 
                return as.obj && other.as.obj && AS_CSTRING(*this) == AS_CSTRING(other);
            default:
                return as.obj == other.as.obj; // Pointer checking for objects
        }
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
            case ValueType::INTEGER: return std::to_string(as.intVal);
            case ValueType::FLOAT: {
                std::ostringstream ss;
                ss.imbue(std::locale::classic());
                ss << as.floatVal;
                return ss.str();
            }
            case ValueType::STRING: return AS_CSTRING(*this);
            case ValueType::BOOLEAN: return as.boolVal ? "dogru" : "yanlis";
            case ValueType::LIST: {
                std::string s = "[";
                if (as.obj) {
                    const auto& list = getList();
                    for (size_t i = 0; i < list.size(); ++i) {
                        s += list[i].toString();
                        if (i < list.size() - 1) s += ", ";
                    }
                }
                s += "]";
                return s;
            }
            case ValueType::MAP: {
                std::string s = "{";
                if (as.obj) {
                    const auto& map = getMap();
                    bool first = true;
                    for (const auto& pair : map) {
                        if (!first) s += ", ";
                        s += "\"" + pair.first + "\": " + pair.second.toString();
                        first = false;
                    }
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
        
        void* addr = as.obj;
        if (type == ValueType::LIST && as.obj) {
            json += "\"size\": " + std::to_string(getList().size()) + ", ";
            json += "\"elements\": [";
            const auto& list = getList();
            for (size_t i = 0; i < list.size(); ++i) {
                json += list[i].toJson();
                if (i < list.size() - 1) json += ", ";
            }
            json += "], ";
        }
        else if (type == ValueType::MAP && as.obj) {
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
        else if (type == ValueType::STRING && as.obj) {
            json += "\"length\": " + std::to_string(AS_CSTRING(*this).length()) + ", ";
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

