#include "serial_port.h"
#include <iostream>

SerialPort::SerialPort(const std::string& portName) {
    this->connected = false;

    // Windows'ta port adları "\\\\.\\COM3" seklinde daha güvenli açılır (10 üzeri portlar için)
    std::string deviceName = "\\\\.\\" + portName;

    this->handler = CreateFileA(static_cast<LPCSTR>(deviceName.c_str()),
                                GENERIC_READ | GENERIC_WRITE,
                                0,
                                NULL,
                                OPEN_EXISTING,
                                FILE_ATTRIBUTE_NORMAL,
                                NULL);

    if (this->handler == INVALID_HANDLE_VALUE) {
        if (GetLastError() == ERROR_FILE_NOT_FOUND) {
            std::cerr << "HATA: Port bulunamadı: " << portName << "\n";
        } else {
            std::cerr << "HATA: Port acilamadi (Baska bir program kullaniyor olabilir): " << portName << "\n";
        }
    } else {
        DCB dcbSerialParameters = {0};

        if (!GetCommState(this->handler, &dcbSerialParameters)) {
            std::cerr << "HATA: Port parametreleri alinamadi.\n";
        } else {
            dcbSerialParameters.BaudRate = CBR_9600;
            dcbSerialParameters.ByteSize = 8;
            dcbSerialParameters.StopBits = ONESTOPBIT;
            dcbSerialParameters.Parity = NOPARITY;
            dcbSerialParameters.fDtrControl = DTR_CONTROL_ENABLE;

            if (!SetCommState(handler, &dcbSerialParameters)) {
                std::cerr << "HATA: Port ayarlari yapilamadi.\n";
            } else {
                this->connected = true;
                PurgeComm(this->handler, PURGE_RXCLEAR | PURGE_TXCLEAR);
                Sleep(2000); // Arduino reset'i icin bekle
            }
        }
    }
}

SerialPort::~SerialPort() {
    if (this->connected) {
        this->connected = false;
        CloseHandle(this->handler);
    }
}

bool SerialPort::isConnected() {
    return this->connected;
}

bool SerialPort::writeSerialPort(const std::string& data) {
    DWORD bytesSend;
    if (!WriteFile(this->handler, (void*)data.c_str(), data.length(), &bytesSend, 0)) {
        ClearCommError(this->handler, &this->errors, &this->status);
        return false;
    }
    return true;
}

std::string SerialPort::readSerialPort() {
    DWORD bytesRead;
    unsigned int toRead = 0;
    char buffer[256]; // Kucuk buffer
    std::string result = "";

    ClearCommError(this->handler, &this->errors, &this->status);

    if (this->status.cbInQue > 0) {
        // En fazla buffer kadar oku
        toRead = this->status.cbInQue;
        if (toRead > 255) toRead = 255;

        if (ReadFile(this->handler, buffer, toRead, &bytesRead, NULL)) {
            result = std::string(buffer, bytesRead);
        }
    }
    return result;
}

void SerialPort::closeSerial() {
    CloseHandle(this->handler);
    this->connected = false;
}
