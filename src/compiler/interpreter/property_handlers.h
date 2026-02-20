#ifndef PROPERTY_HANDLERS_H
#define PROPERTY_HANDLERS_H

#include "value.h"
#include "interpreter.h"
#include <memory>
#include <vector>

class PropertyHandlers {
public:
    static bool handle(Interpreter& interpreter, Value object, const std::string& propertyName, Value& result);
private:
    static bool handleList(Value object, const std::string& name, Value& result);
    static bool handleString(Value object, const std::string& name, Value& result);
    static bool handleMap(Value object, const std::string& name, Value& result);
};

#endif
