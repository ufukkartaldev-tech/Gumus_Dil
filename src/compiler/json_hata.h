#ifndef JSON_HATA_H
#define JSON_HATA_H

#include <string>
#include <iostream>
#include <stdexcept>
#include <algorithm>

struct GumusException : public std::runtime_error {
    std::string type;
    int line;

    GumusException(const std::string& type, int line, const std::string& message)
        : std::runtime_error(message), type(type), line(line) {}
};

inline std::string JsonEscape(const std::string& s) {
    std::string out;
    out.reserve(s.size());
    for (char c : s) {
        switch (c) {
            case '\\': out += "\\\\"; break;
            case '"': out += "\\\""; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default:
                if (static_cast<unsigned char>(c) < 0x20) {
                    out += ' ';
                } else {
                    out += c;
                }
                break;
        }
    }
    return out;
}

inline std::string DayiDilHataCeviri(const std::string& type, const std::string& orjMsg, std::string& suggestion) {
    std::string dayacMsg = orjMsg;

    if (type.find("error") != std::string::npos || type.find("warning") != std::string::npos) {
        
        // 1. Noktalı virgül uyarısı (Özel durum - Parser'dan gelir)
        if (orjMsg.find("noktalı virgül kullanılmaz") != std::string::npos || orjMsg.find("Noktalı virgül kullanılmaz") != std::string::npos) {
            dayacMsg = "Yeğenim C++ yazmıyoruz, noktalı virgül buralarda sökmez. Sil gitsin onu!";
            suggestion = "Satır sonlarına noktalı virgül koymaktan vazgeç aslanım.";
        }
        
        // 2. Bekleniyor / Eksik kapanışlar
        else if (orjMsg.find("bekleniyor") != std::string::npos) {
            if (orjMsg.find("adi") != std::string::npos || orjMsg.find("adı") != std::string::npos) {
                dayacMsg = "İsimsiz kahraman olmaz yeğenim, buna bir isim ver.";
                suggestion = "Boş etiket olmaz, 'değişken benimDegisken = 5' gibi bir ad tanımla.";
            } else if (orjMsg.find("'{'") != std::string::npos) {
                dayacMsg = "Açtığın kapıyı unutmuşsun yeğenim, süslü parantez '{' eksik kalmış.";
                suggestion = "Blokları süslü parantez '{' ile başlatman lazım.";
            } else if (orjMsg.find("'}'") != std::string::npos) {
                dayacMsg = "Açtığın kapıyı kapatmamışsın aslanım, kod cereyan yapıyor! '}' eksik.";
                suggestion = "Döngü, şart veya fonksiyon bloklarını '}' ile sonlandırmalısın.";
            } else if (orjMsg.find("';'") != std::string::npos) {
                dayacMsg = "Eksik parça var buralarda, noktalı virgülü unutmuşsun.";
                suggestion = "Döngü şartı gibi bazı özel yerlerde noktalı virgül ';' mecburidir, dikkat et.";
            } else if (orjMsg.find("')'") != std::string::npos) {
                dayacMsg = "Matematik hocan görse ağlar evladım, sağ parantezi açık bırakmışsın ')' unutma.";
                suggestion = "Sola açtığın her '(' için bir tane de sağa ')' kapatmalısın, kural budur.";
            } else if (orjMsg.find("'('") != std::string::npos) {
                dayacMsg = "Buraya bir normal parantez '(' lazım aslanım, çok çıplak kaldı.";
                suggestion = "Şarttan veya fonksiyondan sonra '(' açmayı ihmal etme.";
            } else {
                dayacMsg = "Eksik matkap ucu var evlat: " + orjMsg;
                suggestion = "Satırlarına dikkatlice bak, mutlaka bir şey unutmuşsundur.";
            }
        }
        
        // 3. Geçersiz atama
        else if (orjMsg.find("Gecersiz atama hedefi") != std::string::npos) {
            dayacMsg = "Havaya çivi çakmaya çalışıyorsun yeğenim, bu atama geçersiz.";
            suggestion = "Eşittir(=) işaretinin sol tarafına mantıklı bir değişken veya hedef koymalısın.";
        }
        
        // 4. Sınıf kuralları
        else if (orjMsg.find("sadece metotlar") != std::string::npos) {
            dayacMsg = "Sınıfın içine gecekondulaşma yapamazsın, buraya sadece metot/fonksiyon konur.";
            suggestion = "Değişken tanımlarını ya sınıf dışına taşı ya da 'kurucu()' fonksiyonun içine al.";
        }
        
        // 5. Çok fazla hata
        else if (orjMsg.find("Çok fazla hata") != std::string::npos) {
            dayacMsg = "Burası arapsaçına dönmüş paşam, bu satırı iptal ettim.";
            suggestion = "O satırdaki temel syntax'ı toparla, bir yerlerde büyük bir dizin hatası var.";
        }

        // 6. Tokenizer - Tanımlanamayan Karakter (Bilinmeyen karakter)
        else if (orjMsg.find("Bilinmeyen karakter") != std::string::npos || orjMsg.find("Tanimlanamayan") != std::string::npos) {
            dayacMsg = "Klavyeye çay mı döküldü yeğenim, bu karakter nedir böyle?";
            suggestion = "GümüşDil klavyesinde olmayan uçuk kaçık bir simge basmışsın, sil onu.";
        }
		
		else {
			dayacMsg = "Gümüş Motor tekledi evlat: " + orjMsg;
			if(suggestion.empty()) {
				suggestion = "Bazen hata senden bazen makineden kaynaklanır. Bi' derin nefes al ve tekrar oku.";
			}
		}
    }
    return dayacMsg;
}

inline void JsonHata(const std::string& type, const std::string& message, int line, const std::string& file, const std::string& defaultSug) {
    std::string suggestion = defaultSug;
    std::string dayiMsg = message;

    // Sadece error ve warning türleriyse Dayı devreye girsin.
    if (type.find("error") != std::string::npos || type.find("warning") != std::string::npos) {
        dayiMsg = DayiDilHataCeviri(type, message, suggestion);
    }

    std::cerr << "{\"type\": \"" << JsonEscape(type) << "\", \"line\": " << line
              << ", \"message\": \"" << JsonEscape(dayiMsg) << "\"";
    if (!file.empty()) {
        std::cerr << ", \"file\": \"" << JsonEscape(file) << "\"";
    }
    if (!suggestion.empty()) {
        std::cerr << ", \"suggestion\": \"" << JsonEscape(suggestion) << "\"";
    }
    std::cerr << "}\n";
}

inline void JsonHata(const std::string& type, const std::string& message, int line, const std::string& file) {
    JsonHata(type, message, line, file, "");
}

inline void JsonHata(const std::string& type, const std::string& message, int line) {
    JsonHata(type, message, line, "", "");
}

#endif
