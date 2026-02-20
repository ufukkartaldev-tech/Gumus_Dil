#ifndef SERIAL_PORT_H
#define SERIAL_PORT_H

#include <string>
#include <windows.h>

class SerialPort {
public:
    SerialPort(const std::string& portName);
    ~SerialPort();

    bool isConnected();
    bool writeSerialPort(const std::string& data);
    std::string readSerialPort(); 
    void closeSerial();

private:
    HANDLE handler;
    bool connected;
    COMSTAT status;
    DWORD errors;
};

#endif // SERIAL_PORT_H
