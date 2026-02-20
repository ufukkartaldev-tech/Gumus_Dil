#include "property_handlers.h"
#include <algorithm>
#include <fstream>
#include <sstream>
#include <filesystem>
#include <iostream>

bool PropertyHandlers::handle(Interpreter& interpreter, Value object, const std::string& propertyName, Value& result) {
    if (object.type == ValueType::LIST) return handleList(object, propertyName, result);
    if (object.type == ValueType::STRING) return handleString(object, propertyName, result);
    if (object.type == ValueType::MAP) return handleMap(object, propertyName, result);
    return false;
}

bool PropertyHandlers::handleList(Value object, const std::string& name, Value& result) {
    auto list = object.listVal;
    if (name == "uzunluk") {
        result = Value(std::make_shared<NativeFunction>("uzunluk", 0, [list](Interpreter&, const std::vector<Value>& args) {
            return Value((int)list->size());
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "ekle") {
        result = Value(std::make_shared<NativeFunction>("ekle", 1, [list](Interpreter&, const std::vector<Value>& args) {
            list->push_back(args[0]);
            return Value(list);
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "sil") {
        result = Value(std::make_shared<NativeFunction>("sil", 1, [list](Interpreter&, const std::vector<Value>& args) {
            if (args[0].type != ValueType::INTEGER) return Value(list);
            int idx = args[0].intVal;
            if (idx >= 0 && idx < (int)list->size()) list->erase(list->begin() + idx);
            return Value(list);
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "bul") {
        result = Value(std::make_shared<NativeFunction>("bul", 1, [list](Interpreter&, const std::vector<Value>& args) {
            for (size_t i = 0; i < list->size(); ++i) {
                if ((*list)[i].type == args[0].type && (*list)[i].toString() == args[0].toString()) return Value((int)i);
            }
            return Value(-1);
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "metin") {
        result = Value(std::make_shared<NativeFunction>("metin", 1, [list](Interpreter&, const std::vector<Value>& args) {
            std::string delimiter = "";
            if (args[0].type == ValueType::STRING) delimiter = args[0].stringVal;
            std::string res = "";
            for (size_t i = 0; i < list->size(); ++i) {
                res += (*list)[i].toString();
                if (i < list->size() - 1) res += delimiter;
            }
            return Value(res);
        }), ValueType::FUNCTION);
        return true;
    }
    return false;
}

bool PropertyHandlers::handleString(Value object, const std::string& name, Value& result) {
    std::string s = object.stringVal;
    if (name == "uzunluk") {
        result = Value(std::make_shared<NativeFunction>("uzunluk", 0, [s](Interpreter&, const std::vector<Value>& args) {
            return Value((int)s.length());
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "buyuk") {
        result = Value(std::make_shared<NativeFunction>("buyuk", 0, [s](Interpreter&, const std::vector<Value>& args) {
            std::string res = s;
            std::transform(res.begin(), res.end(), res.begin(), [](unsigned char c){ return std::toupper(c); });
            return Value(res);
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "kucuk") {
        result = Value(std::make_shared<NativeFunction>("kucuk", 0, [s](Interpreter&, const std::vector<Value>& args) {
            std::string res = s;
            std::transform(res.begin(), res.end(), res.begin(), [](unsigned char c){ return std::tolower(c); });
            return Value(res);
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "parcala") {
        result = Value(std::make_shared<NativeFunction>("parcala", 1, [s](Interpreter&, const std::vector<Value>& args) {
            auto list = std::make_shared<ValueList>();
            std::string delimiter = " ";
            if (args[0].type == ValueType::STRING) delimiter = args[0].stringVal;
            if (delimiter.empty()) { list->push_back(Value(s)); return Value(list); }
            std::string temp = s;
            size_t pos = 0;
            while ((pos = temp.find(delimiter)) != std::string::npos) {
                list->push_back(Value(temp.substr(0, pos)));
                temp.erase(0, pos + delimiter.length());
            }
            list->push_back(Value(temp));
            return Value(list);
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "sayi") {
        result = Value(std::make_shared<NativeFunction>("sayi", 0, [s](Interpreter&, const std::vector<Value>& args) {
            try { return Value(std::stoi(s)); } catch(...) { return Value(0); }
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "icerir") {
        result = Value(std::make_shared<NativeFunction>("icerir", 1, [s](Interpreter&, const std::vector<Value>& args) {
            if (args[0].type != ValueType::STRING) return Value(false);
            return Value(s.find(args[0].stringVal) != std::string::npos);
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "dosya_oku") {
        result = Value(std::make_shared<NativeFunction>("dosya_oku", 0, [s](Interpreter&, const std::vector<Value>& args) {
            std::ifstream file(s);
            if (file.is_open()) {
                std::stringstream buffer;
                buffer << file.rdbuf();
                return Value(buffer.str());
            }
            return Value(std::string("")); 
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "dosya_yaz") {
        result = Value(std::make_shared<NativeFunction>("dosya_yaz", 1, [s](Interpreter&, const std::vector<Value>& args) {
            if (args[0].type != ValueType::STRING) return Value(false);
            std::ofstream file(s);
            if (file.is_open()) {
                file << args[0].stringVal;
                return Value(true);
            }
            return Value(false);
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "dosya_ekle") {
        result = Value(std::make_shared<NativeFunction>("dosya_ekle", 1, [s](Interpreter&, const std::vector<Value>& args) {
            if (args[0].type != ValueType::STRING) return Value(false);
            std::ofstream file(s, std::ios_base::app);
            if (file.is_open()) {
                file << args[0].stringVal;
                return Value(true);
            }
            return Value(false);
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "dosya_varmi") {
        result = Value(std::make_shared<NativeFunction>("dosya_varmi", 0, [s](Interpreter&, const std::vector<Value>& args) {
            return Value(std::filesystem::exists(s));
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "dosya_sil") {
        result = Value(std::make_shared<NativeFunction>("dosya_sil", 0, [s](Interpreter&, const std::vector<Value>& args) {
            return Value(std::filesystem::remove(s));
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "klasor_olustur") {
        result = Value(std::make_shared<NativeFunction>("klasor_olustur", 0, [s](Interpreter&, const std::vector<Value>& args) {
            return Value(std::filesystem::create_directories(s));
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "klasor_listele") {
        result = Value(std::make_shared<NativeFunction>("klasor_listele", 0, [s](Interpreter&, const std::vector<Value>& args) {
            auto fileList = std::make_shared<ValueList>();
            if (std::filesystem::exists(s) && std::filesystem::is_directory(s)) {
                for (const auto& entry : std::filesystem::directory_iterator(s)) {
                    fileList->push_back(Value(entry.path().filename().string()));
                }
            }
            return Value(fileList);
        }), ValueType::FUNCTION);
        return true;
    }
    return false;
}

bool PropertyHandlers::handleMap(Value object, const std::string& name, Value& result) {
    auto map = object.mapVal;
    if (name == "uzunluk") {
        result = Value(std::make_shared<NativeFunction>("uzunluk", 0, [map](Interpreter&, const std::vector<Value>& args) {
            return Value((int)map->size());
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "anahtarlar") {
        result = Value(std::make_shared<NativeFunction>("anahtarlar", 0, [map](Interpreter&, const std::vector<Value>& args) {
            auto keys = std::make_shared<ValueList>();
            for (const auto& pair : *map) keys->push_back(Value(pair.first));
            return Value(keys);
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "degerler") {
        result = Value(std::make_shared<NativeFunction>("degerler", 0, [map](Interpreter&, const std::vector<Value>& args) {
            auto values = std::make_shared<ValueList>();
            for (const auto& pair : *map) values->push_back(pair.second);
            return Value(values);
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "sil") {
        result = Value(std::make_shared<NativeFunction>("sil", 1, [map](Interpreter&, const std::vector<Value>& args) {
            map->erase(args[0].toString());
            return Value();
        }), ValueType::FUNCTION);
        return true;
    }
    if (name == "temizle") {
        result = Value(std::make_shared<NativeFunction>("temizle", 0, [map](Interpreter&, const std::vector<Value>& args) {
            map->clear();
            return Value();
        }), ValueType::FUNCTION);
        return true;
    }
    return false;
}
