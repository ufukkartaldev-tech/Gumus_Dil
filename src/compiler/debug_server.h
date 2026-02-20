#ifndef DEBUG_SERVER_H
#define DEBUG_SERVER_H

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include "interpreter/interpreter.h"

// Basit Debug Sunucusu (Stdin/Stdout üzerinden haberleşir)
class DebugServer {
public:
    static bool is_attached;
    static bool is_stepping;
    static int step_depth; // 0: over, 1: into

    static void onMove(int line, Environment* env) {
        if (!is_attached) return;

        // Breakpoint kontrolü (Basitlik için her satırda duruyoruz ve IDE karar veriyor, 
        // ya da "stepping" modundaysak duruyoruz)
        
        // Şimdilik her satırda IDE'ye "Ben buradayım" diyelim
        std::cout << "__DEBUG_EVENT__{\"type\": \"line\", \"line\": " << line << "}" << std::endl;

        // Eğer adımlıyorsak veya IDE durmamızı istediyse dur
        if (is_stepping) {
            handleCommands(env);
        }
    }

    static void handleCommands(Environment* env) {
        // İstemciden (IDE) komut bekle
        std::string line;
        while (std::getline(std::cin, line)) {
            if (line == "STEP_OVER") {
                is_stepping = true;
                break;
            } 
            else if (line == "CONTINUE") {
                is_stepping = false;
                break;
            }
            else if (line == "VARS") {
                // Değişkenleri dök
                if (env) {
                    std::cout << "__DEBUG_DATA__" << env->toJson() << std::endl;
                } else {
                    std::cout << "__DEBUG_DATA__{}" << std::endl;
                }
            }
            else if (line == "STOP") {
                exit(0);
            }
        }
    }
};

inline bool DebugServer::is_attached = false;
inline bool DebugServer::is_stepping = false;
inline int DebugServer::step_depth = 0;

#endif
