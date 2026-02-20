#ifdef _MSC_VER
#pragma execution_character_set("utf-8")
#endif

#include "interpreter.h"
#include "native_functions.h"
#include "../lexer/tokenizer.h"
#include "../parser/parser.h"
#include "../json_hata.h"
#include "../debug.h"
#include "../semantic/resolver.h"

// Standart Kütüphaneler
#include <iostream>
#include <fstream>
#include <sstream>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <algorithm>
#include <thread>
#include <chrono>
#include <vector>

// AG (NETWORK) - Winsock
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")

// --- Helper Functions ---
// (Buraya gerekirse helper eklenir)

// --- NativeFunction Implementation ---

Value NativeFunction::call(Interpreter& interpreter, const std::vector<Value>& arguments) {
    interpreter.callStack.push_back("yerleşik:" + name);
    Value result = func(interpreter, arguments);
    interpreter.callStack.pop_back();
    return result;
}

int NativeFunction::arity() { 
    return arityVal; 
}

std::string NativeFunction::toString() { 
    return "<native " + name + ">"; 
}

// AG (NETWORK) - Winsock Init Helper
static SOCKET aktif_soket = INVALID_SOCKET;
static bool winsock_baslatildi = false;

static void init_winsock() {
    if (!winsock_baslatildi) {
        WSADATA wsaData;
        WSAStartup(MAKEWORD(2, 2), &wsaData);
        winsock_baslatildi = true;
    }
}

void registerNativeFunctions(Interpreter& interpreter) {
    // ... (Diğer fonksiyonlar)
    
    // 7. AĞ (NETWORK) - GÜMÜŞ AĞI
    // ---------------------------
    
    // ag_sunucu(port)
    auto ag_sunucu = std::make_shared<NativeFunction>("ag_sunucu", 1, [](Interpreter&, const std::vector<Value>& args) {
        init_winsock();
        int port = args[0].intVal;
        
        SOCKET serverSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (serverSocket == INVALID_SOCKET) return Value(false);

        sockaddr_in service;
        service.sin_family = AF_INET;
        service.sin_addr.s_addr = INADDR_ANY;
        service.sin_port = htons(port);
        
        if (bind(serverSocket, (SOCKADDR*)&service, sizeof(service)) == SOCKET_ERROR) {
            closesocket(serverSocket);
            return Value(false);
        }
        
        if (listen(serverSocket, 1) == SOCKET_ERROR) {
             closesocket(serverSocket);
             return Value(false);
        }
        
        std::cout << "AG: Sunucu " << port << " portunda dinliyor..." << std::endl;
        
        // Blocking Accept
        SOCKET clientSocket = accept(serverSocket, NULL, NULL);
        if (clientSocket != INVALID_SOCKET) {
             std::cout << "AG: Baglanti kabul edildi!" << std::endl;
             aktif_soket = clientSocket;
             closesocket(serverSocket); // Stop listening, we have our peer
             return Value(true);
        }
        closesocket(serverSocket);
        return Value(false);
    });
    interpreter.functions["ag_sunucu"] = ag_sunucu;

    // ag_baglan(ip, port)
    auto ag_baglan = std::make_shared<NativeFunction>("ag_baglan", 2, [](Interpreter&, const std::vector<Value>& args) {
        init_winsock();
        std::string ip = args[0].stringVal;
        int port = args[1].intVal;
        
        std::cout << "AG: " << ip << ":" << port << " adresine baglaniliyor..." << std::endl;
        
        SOCKET connectSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (connectSocket == INVALID_SOCKET) return Value(false);

        sockaddr_in clientService;
        clientService.sin_family = AF_INET;
        clientService.sin_addr.s_addr = inet_addr(ip.c_str());
        clientService.sin_port = htons(port);
        
        if (connect(connectSocket, (SOCKADDR*)&clientService, sizeof(clientService)) == SOCKET_ERROR) {
            std::cout << "AG: Baglanti basarisiz." << std::endl;
            closesocket(connectSocket);
            return Value(false);
        }
        
        std::cout << "AG: Baglanti saglandi!" << std::endl;
        aktif_soket = connectSocket;
        return Value(true);
    });
    interpreter.functions["ag_baglan"] = ag_baglan;
    
    // ag_gonder(mesaj)
    auto ag_gonder = std::make_shared<NativeFunction>("ag_gonder", 1, [](Interpreter&, const std::vector<Value>& args) {
        if (aktif_soket == INVALID_SOCKET) return Value(false);
        std::string veri = args[0].toString() + "\n";
        send(aktif_soket, veri.c_str(), (int)veri.length(), 0);
        return Value(true);
    });
    interpreter.functions["ag_gonder"] = ag_gonder;

    // ag_oku()
    auto ag_oku = std::make_shared<NativeFunction>("ag_oku", 0, [](Interpreter&, const std::vector<Value>& args) {
        if (aktif_soket == INVALID_SOCKET) return Value("");
        
        fd_set readfds;
        FD_ZERO(&readfds);
        FD_SET(aktif_soket, &readfds);
        
        timeval timeout;
        timeout.tv_sec = 0;
        timeout.tv_usec = 1000; // 1ms
        
        // MinGW select signature might differ slightly but usually compatible
        int activity = select(0, &readfds, NULL, NULL, &timeout);
        
        if (activity > 0) {
            char buffer[1024];
            int bytesReceived = recv(aktif_soket, buffer, 1023, 0);
            if (bytesReceived > 0) {
                buffer[bytesReceived] = '\0';
                // Remove newline if present at the end for cleaner strings
                std::string s(buffer);
                if (!s.empty() && s.back() == '\n') s.pop_back();
                return Value(s);
            }
        }
        return Value("");
    });
    interpreter.functions["ag_oku"] = ag_oku;


    // 1. TEMEL FONKSİYONLAR
    // ---------------------

    // uzunluk(deger)
    auto uzunluk = std::make_shared<NativeFunction>("uzunluk", 1, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type == ValueType::STRING) return Value((int)args[0].stringVal.length());
        if (args[0].type == ValueType::LIST) return Value((int)args[0].listVal->size());
        return Value(0);
    });
    interpreter.functions["uzunluk"] = uzunluk;

    // girdi()
    auto girdi = std::make_shared<NativeFunction>("girdi", 0, [](Interpreter&, const std::vector<Value>& args) {
        std::string line;
        std::getline(std::cin, line);
        return Value(line);
    });
    interpreter.functions["girdi"] = girdi;

    // sayi(deger)
    auto sayi = std::make_shared<NativeFunction>("sayi", 1, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type == ValueType::STRING) {
            try { return Value(std::stoi(args[0].stringVal)); } catch(...) { return Value(0); }
        }
        if (args[0].type == ValueType::INTEGER) return args[0];
        if (args[0].type == ValueType::BOOLEAN) return Value(args[0].boolVal ? 1 : 0);
        return Value(0);
    });
    interpreter.functions["sayi"] = sayi;
    interpreter.functions["say\xC4\xB1"] = sayi; // Türkçe karakter desteği

    // metin(deger)
    auto metin = std::make_shared<NativeFunction>("metin", 1, [](Interpreter&, const std::vector<Value>& args) {
        return Value(args[0].toString());
    });
    interpreter.functions["metin"] = metin;

    // zaman()
    auto zaman = std::make_shared<NativeFunction>("zaman", 0, [](Interpreter&, const std::vector<Value>& args) {
        return Value((int)time(NULL));
    });
    interpreter.functions["zaman"] = zaman;
    
    // bekle(ms)
    auto bekle = std::make_shared<NativeFunction>("bekle", 1, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type == ValueType::INTEGER) {
            std::this_thread::sleep_for(std::chrono::milliseconds(args[0].intVal));
        }
        return Value();
    });
    interpreter.functions["bekle"] = bekle;

    // 2. LİSTE İŞLEMLERİ
    // ------------------
    
    // ekle(liste, eleman)
    auto ekle = std::make_shared<NativeFunction>("ekle", 2, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type != ValueType::LIST) return Value(0);
        args[0].listVal->push_back(args[1]);
        return args[0];
    });
    interpreter.functions["ekle"] = ekle;

    // sil(liste, index)
    auto sil = std::make_shared<NativeFunction>("sil", 2, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type != ValueType::LIST) return Value(0);
        if (args[1].type != ValueType::INTEGER) return Value(0);
        int idx = args[1].intVal;
        if (idx >= 0 && idx < (int)args[0].listVal->size()) {
            args[0].listVal->erase(args[0].listVal->begin() + idx);
        }
        return args[0];
    });
    interpreter.functions["sil"] = sil;
    
    // sirala(liste)
    auto sirala = std::make_shared<NativeFunction>("sirala", 1, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type != ValueType::LIST) return args[0];
        std::sort(args[0].listVal->begin(), args[0].listVal->end(), [](const Value& a, const Value& b) {
            if (a.type != b.type) return a.type < b.type;
            if (a.type == ValueType::INTEGER) return a.intVal < b.intVal;
            if (a.type == ValueType::STRING) return a.stringVal < b.stringVal;
            return false;
        });
        return args[0];
    });
    interpreter.functions["sirala"] = sirala;

    // 3. MATEMATİK
    // ------------
    
    // karekok(sayi)
    auto karekok = std::make_shared<NativeFunction>("karekok", 1, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type == ValueType::INTEGER) return Value((int)std::sqrt(args[0].intVal));
        return Value(0);
    });
    interpreter.functions["karekok"] = karekok;
    
    auto rastgele = std::make_shared<NativeFunction>("rastgele", 0, [](Interpreter&, const std::vector<Value>& args) {
        return Value((int)std::rand());
    });
    interpreter.functions["rastgele"] = rastgele;

    // 4. DOSYA İŞLEMLERİ (Core)
    // -------------------------

    // dosya_yaz(yol, icerik)
    auto dosya_yaz = std::make_shared<NativeFunction>("dosya_yaz", 2, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type != ValueType::STRING || args[1].type != ValueType::STRING) return Value(false);
        std::ofstream file(args[0].stringVal);
        if (file.is_open()) {
            file << args[1].stringVal;
            file.close();
            return Value(true);
        }
        return Value(false);
    });
    interpreter.functions["_dosya_yaz"] = dosya_yaz;
    interpreter.functions["dosya_yaz"] = dosya_yaz; // Alias

    // dosya_oku(yol)
    auto dosya_oku = std::make_shared<NativeFunction>("dosya_oku", 1, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type != ValueType::STRING) return Value(std::string("")); 
        std::ifstream file(args[0].stringVal);
        if (file.is_open()) {
            std::stringstream buffer;
            buffer << file.rdbuf();
            return Value(buffer.str());
        }
        return Value(std::string("")); 
    });
    interpreter.functions["_dosya_oku"] = dosya_oku;
    interpreter.functions["dosya_oku"] = dosya_oku; // Alias

    // dosya_ekle(yol, icerik)
    auto dosya_ekle = std::make_shared<NativeFunction>("dosya_ekle", 2, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type != ValueType::STRING || args[1].type != ValueType::STRING) return Value(false);
        std::ofstream file(args[0].stringVal, std::ios_base::app);
        if (file.is_open()) {
            file << args[1].stringVal;
            file.close();
            return Value(true);
        }
        return Value(false);
    });
    interpreter.functions["_dosya_ekle"] = dosya_ekle;
    interpreter.functions["dosya_ekle"] = dosya_ekle; // Alias
    
    // dahil_et(dosya) - Critical
    auto dahil_et = std::make_shared<NativeFunction>("dahil_et", 1, [](Interpreter& interpreter, const std::vector<Value>& args) {
        if (args[0].type != ValueType::STRING) return Value(false);
        std::string filename = args[0].stringVal;
        
        if (interpreter.loadedFiles.count(filename)) return Value(true);

        std::string foundPath = "";
        std::ifstream file;
        
        // Search
        for (const auto& path : interpreter.searchPaths) {
            std::string fullPath = path + "/" + filename;
            std::ifstream testFile(fullPath);
            if (testFile.good()) {
                foundPath = fullPath;
                file.open(fullPath);
                break;
            }
        }
        if (!file.is_open()) {
            file.open(filename);
            if (file.is_open()) foundPath = filename;
        }

        if (!file.is_open()) {
            JsonHata("import_error", "Modul bulunamadi: " + filename, 0);
            return Value(false);
        }

        interpreter.loadedFiles.insert(filename);
        std::stringstream buffer;
        buffer << file.rdbuf();
        std::string source = buffer.str();

        // BOM Fix
        if (source.size() >= 3 && (unsigned char)source[0] == 0xEF && (unsigned char)source[1] == 0xBB && (unsigned char)source[2] == 0xBF) {
            source.erase(0, 3);
        }
        
        auto previous = interpreter.environment;
        interpreter.environment = interpreter.globals; // Global scope'a import

        try {
            Tokenizer tokenizer(source);
            std::vector<Token> tokens = tokenizer.tokenize();
            Parser parser(tokens);
            std::vector<std::shared_ptr<Stmt>> statements = parser.parse();
            
            if (!parser.hasError()) {
                // AST'yi canli tut (Dangling pointer onlemi)
                interpreter.astList.push_back(statements);

                // SEMA ANALIZI (Resolver)
                Resolver resolver(interpreter);
                resolver.resolve(statements);
                
                interpreter.executeBlock(statements, interpreter.globals);
            }
        } catch (...) {
            JsonHata("import_error", "Modul yuklenirken hata: " + filename, 0);
        }
        
        interpreter.environment = previous;
        return Value(true);
    });
    interpreter.functions["dahil_et"] = dahil_et;


    // 5. OYUN MOTORU (Voxel World)
    // ----------------------------
    
// Basit bir Sparse Voxel Map (x,y,z -> tip)
static std::map<std::string, int> voxel_map;


    auto insaa_et = std::make_shared<NativeFunction>("insaa_et", 4, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type != ValueType::INTEGER || args[1].type != ValueType::INTEGER || 
            args[2].type != ValueType::INTEGER || args[3].type != ValueType::INTEGER) return Value(false);
            
        int x = args[0].intVal;
        int y = args[1].intVal;
        int z = args[2].intVal;
        int tip = args[3].intVal;
        
        std::string key = std::to_string(x) + "," + std::to_string(y) + "," + std::to_string(z);
        voxel_map[key] = tip;
        
        std::cout << "__VOXEL__: {\"islem\": \"ekle\", \"x\": " << x << ", \"y\": " << y << ", \"z\": " << z << ", \"tip\": " << tip << "}" << std::endl;
        return Value(true);
    });
    interpreter.functions["insaa_et"] = insaa_et;

    // blok_sil(x, y, z)
    auto blok_sil = std::make_shared<NativeFunction>("blok_sil", 3, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type != ValueType::INTEGER || args[1].type != ValueType::INTEGER || args[2].type != ValueType::INTEGER) return Value(false);
        int x = args[0].intVal;
        int y = args[1].intVal;
        int z = args[2].intVal;
        std::string key = std::to_string(x) + "," + std::to_string(y) + "," + std::to_string(z);
        
        if (voxel_map.count(key)) {
            voxel_map.erase(key);
            std::cout << "__VOXEL__: {\"islem\": \"sil\", \"x\": " << x << ", \"y\": " << y << ", \"z\": " << z << "}" << std::endl;
            return Value(true);
        }
        return Value(false);
    });
    interpreter.functions["blok_sil"] = blok_sil;

    // blok_ne(x, y, z)
    auto blok_ne = std::make_shared<NativeFunction>("blok_ne", 3, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type != ValueType::INTEGER || args[1].type != ValueType::INTEGER || args[2].type != ValueType::INTEGER) return Value(0);
        int x = args[0].intVal;
        int y = args[1].intVal;
        int z = args[2].intVal;
        std::string key = std::to_string(x) + "," + std::to_string(y) + "," + std::to_string(z);
        
        if (voxel_map.count(key)) {
            return Value(voxel_map[key]);
        }
        return Value(0); // 0 = Hava (Eksik olan return buydu)
    });
    interpreter.functions["blok_ne"] = blok_ne;

    // 6. FİZİK MOTORU
    // ----------------
    
    // fizik_guncelle(x, z, menzil) -> İsteğe bağlı menzil dışı dondurma
    auto fizik_guncelle = std::make_shared<NativeFunction>("fizik_guncelle", 3, [](Interpreter&, const std::vector<Value>& args) {
        
        // Optimizasyon Parametreleri
        bool optimizasyon_aktif = false;
        int merkez_x = 0;
        int merkez_z = 0;
        int menzil = 0;

        // Eğer 3 argüman geldiyse (x, z, menzil) optimizasyonu aç
        if (args.size() == 3 && args[0].type == ValueType::INTEGER) {
            optimizasyon_aktif = true;
            merkez_x = args[0].intVal;
            merkez_z = args[1].intVal;
            menzil = args[2].intVal;
        }

        struct Hareket { int x, y, z, tip; };
        std::vector<Hareket> tasinacaklar;
        
        for (auto const& [key, tip] : voxel_map) {
            // Sadece KUM (ID: 6) düşer
            if (tip == 6) { 
                int firstComma = (int)key.find(',');
                int secondComma = (int)key.find(',', firstComma + 1);
                
                int x = std::stoi(key.substr(0, firstComma));
                int y = std::stoi(key.substr(firstComma + 1, secondComma - firstComma - 1));
                int z = std::stoi(key.substr(secondComma + 1));

                // OPTİMİZASYON KONTROLÜ: Menzil dışındaysa hesaplama yapma (Freeze)
                if (optimizasyon_aktif) {
                    int dist_x = std::abs(x - merkez_x);
                    int dist_z = std::abs(z - merkez_z);
                    // Kare mesafe kontrolü (Hızlı olsun diye karekök almıyoruz)
                    if (dist_x > menzil || dist_z > menzil) continue;
                }
                
                // Altı boş mu?
                std::string altKey = std::to_string(x) + "," + std::to_string(y - 1) + "," + std::to_string(z);
                
                if (y > 0 && voxel_map.find(altKey) == voxel_map.end()) {
                    tasinacaklar.push_back({x, y, z, tip});
                }
            }
        }
        
        // Hareketleri Uygula
        int hareket_sayisi = 0;
        for (const auto& h : tasinacaklar) {
            std::string eskiKey = std::to_string(h.x) + "," + std::to_string(h.y) + "," + std::to_string(h.z);
            if (voxel_map.count(eskiKey)) {
                voxel_map.erase(eskiKey);
                std::cout << "__VOXEL__: {\"islem\": \"sil\", \"x\": " << h.x << ", \"y\": " << h.y << ", \"z\": " << h.z << "}" << std::endl;
                
                std::string yeniKey = std::to_string(h.x) + "," + std::to_string(h.y - 1) + "," + std::to_string(h.z);
                voxel_map[yeniKey] = h.tip;
                std::cout << "__VOXEL__: {\"islem\": \"ekle\", \"x\": " << h.x << ", \"y\": " << h.y - 1 << ", \"z\": " << h.z << ", \"tip\": " << h.tip << "}" << std::endl;
                
                hareket_sayisi++;
            }
        }
        
        return Value(hareket_sayisi);
    });
    interpreter.functions["fizik_guncelle"] = fizik_guncelle;

    // dunya_kaydet(dosya_yolu)
    auto dunya_kaydet = std::make_shared<NativeFunction>("dunya_kaydet", 1, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type != ValueType::STRING) return Value(false);
        std::string path = args[0].stringVal;
        
        std::ofstream file(path);
        if (!file.is_open()) return Value(false);
        
        // Format: GHfv1 (Gümüş Harita Formatı Versiyon 1)
        file << "GHfv1" << std::endl;
        
        int count = 0;
        for (const auto& [key, tip] : voxel_map) {
            file << key << ":" << tip << std::endl;
            count++;
        }
        file.close();
        std::cout << "Dünya kaydedildi: " << count << " blok -> " << path << std::endl;
        return Value(true);
    });
    interpreter.functions["dunya_kaydet"] = dunya_kaydet;

    // dunya_yukle(dosya_yolu)
    auto dunya_yukle = std::make_shared<NativeFunction>("dunya_yukle", 1, [](Interpreter&, const std::vector<Value>& args) {
        if (args[0].type != ValueType::STRING) return Value(false);
        std::string path = args[0].stringVal;
        
        std::ifstream file(path);
        if (!file.is_open()) return Value(false);
        
        std::string line;
        std::getline(file, line); // Header oku
        if (line != "GHfv1") {
            std::cout << "HATA: Geçersiz harita formatı!" << std::endl;
            return Value(false);
        }
        
        // Mevcut haritayı temizle ve temizlendiğini bildir
        voxel_map.clear();
        std::cout << "__VOXEL__: {\"islem\": \"temizle\"}" << std::endl; 
        
        int count = 0;
        while (std::getline(file, line)) {
            // Format: x,y,z:tip
            size_t colonPos = line.find(':');
            if (colonPos == std::string::npos) continue;
            
            std::string key = line.substr(0, colonPos);
            int tip = std::stoi(line.substr(colonPos + 1));
            
            voxel_map[key] = tip;
            
            // Koordinatları ayıkla (Visualizer için gönder)
            int firstComma = (int)key.find(',');
            int secondComma = (int)key.find(',', firstComma + 1);
            int x = std::stoi(key.substr(0, firstComma));
            int y = std::stoi(key.substr(firstComma + 1, secondComma - firstComma - 1));
            int z = std::stoi(key.substr(secondComma + 1));
            
            std::cout << "__VOXEL__: {\"islem\": \"ekle\", \"x\": " << x << ", \"y\": " << y << ", \"z\": " << z << ", \"tip\": " << tip << "}" << std::endl;
            count++;
        }
        file.close();
        std::cout << "Dünya yüklendi: " << count << " blok." << std::endl;
        return Value(true);
    });
    interpreter.functions["dunya_yukle"] = dunya_yukle;

    // VOXEL HARITA SERVISINI KAPAT (Eger aciksa)
    if (winsock_baslatildi) {
        WSACleanup();
        winsock_baslatildi = false;
    }
}