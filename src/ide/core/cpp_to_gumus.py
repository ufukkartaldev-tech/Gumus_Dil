# -*- coding: utf-8 -*-
import re

class CppToGumusTranspiler:
    """C++ kodunu basit seviyede GümüşDil'e çevirir."""

    def __init__(self):
        pass

    def transpile(self, cpp_code):
        try:
            code = cpp_code
            
            # 1. Gereksiz kütüphane eklemelerini kaldır
            code = re.sub(r'#include\s*<.*?>', '', code)
            code = re.sub(r'using namespace std;', '', code)
            
            # 2. std::cout -> yazdır
            def handle_cout(match):
                inner = match.group(1)
                # << ile ayrılan parçaları bul
                parts = re.split(r'<<', inner)
                results = []
                for p in parts:
                    p = p.strip()
                    if not p or p in ["std::endl", "endl", '"\\n"']:
                        continue
                    results.append(p)
                return f"yazdır({' + '.join(results)})"

            code = re.sub(r'std::cout\s*<<\s*(.*?);', handle_cout, code)
            code = re.sub(r'cout\s*<<\s*(.*?);', handle_cout, code)

            # 3. std::cin -> girdi
            code = re.sub(r'std::cin\s*>>\s*([a-zA-Z_]\w*);', r'\1 = girdi()', code)
            code = re.sub(r'cin\s*>>\s*([a-zA-Z_]\w*);', r'\1 = girdi()', code)

            # 3.1 std::stoi, std::to_string, size()
            code = re.sub(r'std::stoi\((.*?)\)', r'sayı(\1)', code)
            code = re.sub(r'stoi\((.*?)\)', r'sayı(\1)', code)
            code = re.sub(r'std::to_string\((.*?)\)', r'metin(\1)', code)
            code = re.sub(r'to_string\((.*?)\)', r'metin(\1)', code)
            code = re.sub(r'([a-zA-Z_]\w*)\.size\(\)', r'uzunluk(\1)', code)

            # 4. Değişken Tanımları
            types = ['int', 'float', 'double', 'string', 'char', 'bool', 'auto', 'long']
            for t in types:
                # Değişken tanımı: int x = 5; -> değişken x = 5
                code = re.sub(r'\b' + t + r'\s+([a-zA-Z_]\w*)\s*=\s*(.*?);', r'değişken \1 = \2', code)
                # İlklendirilmemiş: int x; -> değişken x = yok
                code = re.sub(r'\b' + t + r'\s+([a-zA-Z_]\w*)\s*;', r'değişken \1 = yok', code)
                # Fonksiyon tanımı: int topla(int a) -> fonksiyon topla(a)
                # Bu regex biraz karmaşık, basitleştirelim
                code = re.sub(r'\b' + t + r'\s+([a-zA-Z_]\w*)\s*\(', r'fonksiyon \1(', code)

            code = re.sub(r'\bvoid\s+([a-zA-Z_]\w*)\s*\(', r'fonksiyon \1(', code)

            # 5. Parametre Tiplerini Temizle (fonksiyon tanımlarındaki)
            # Örn: (int a, string b) -> (a, b)
            def clean_params(match):
                params_str = match.group(2)
                if not params_str.strip(): return match.group(1) + "()"
                
                params = params_str.split(',')
                cleaned = []
                for p in params:
                    p = p.strip()
                    # Tip kısmını at (son kelimeyi al)
                    parts = p.split()
                    if parts:
                        cleaned.append(parts[-1])
                return f"{match.group(1)}({', '.join(cleaned)})"

            code = re.sub(r'(fonksiyon\s+[a-zA-Z_]\w*)\((.*?)\)', clean_params, code)

            # 6. Kontrol Yapıları
            code = re.sub(r'\bif\b', 'eğer', code)
            code = re.sub(r'\belse if\b', 'değilse eğer', code)
            code = re.sub(r'\belse\b', 'değilse', code)
            code = re.sub(r'\bwhile\b', 'döngü', code)
            code = re.sub(r'\bfor\b', 'döngü', code)
            code = re.sub(r'\breturn\b', 'dön', code)
            code = re.sub(r'\bbreak\b', 'kır', code)
            code = re.sub(r'\bcontinue\b', 'devam et', code)
            code = re.sub(r'\bexit\(.*?\)', 'çık()', code)
            
            # 7. Mantıksal Değerler ve Operatörler
            code = re.sub(r'\btrue\b', 'doğru', code)
            code = re.sub(r'\bfalse\b', 'yanlış', code)
            code = re.sub(r'\bNULL\b|\bnullptr\b', 'yok', code)
            code = re.sub(r'&&', 've', code)
            code = re.sub(r'\|\|', 'veya', code)
            code = re.sub(r'!', 'değil ', code) # 'değil' space to avoid sticking to identifier

            # 8. Try - Catch
            code = re.sub(r'\btry\b', 'dene', code)
            code = re.sub(r'\bcatch\b', 'yakala', code)

            # 9. Temizlik (Semicolons)
            # Satır sonundaki noktalı virgülleri kaldır (Blok içindekiler dahil)
            code = re.sub(r';\s*$', '', code, flags=re.MULTILINE)
            
            # Fazla boşlukları temizle
            code = code.strip()

            return code
        except Exception as e:
            return f"// C++ tercüme hatası: {str(e)}"

