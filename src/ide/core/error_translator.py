import re

class ErrorTranslator:
    """
    Derleyiciden gelen İngilizce hata mesajlarını insancıl Türkçeye çevirir.
    Regex desenleri kullanarak hataları yakalar ve eğitici mesajlar üretir.
    """
    
    TRANSLATIONS = [
        # --- Kritik Hatalar ---
        (r"syntax error", "Bak hele! Kodun yapısında bir bozukluk var, daktilo burada mühür basamadı."),
        (r"parse error", "Kodu okurken kafam biraz karıştı yeğenim, buralarda bir yerlerde bir eksiklik var sanki."),
        (r"fatal error", "Eyvah! Derleme durduruldu, kritik bir hata var. Hele bir bak şuraya."),
        
        # --- Değişken ve Kapsam Hataları ---
        (r"error: '(.+?)' was not declared in this scope", "🔍 Bak hele! '{0}' diye bir değişken kullanmaya çalıştın ama onu henüz 'değişken' mührüyle tanıtmamışsın."),
        (r"undefined variable '(.+?)'", "Tanımsız Değişken: '{0}'. Bunu tanıtmadan kullanmaya çalıştın, önce bir mührünü basalım bunun."),
        (r"redefinition of '(.+?)'", "Çakışma var yeğenim! '{0}' ismini zaten kullanmışsın, her mühür benzersiz olmalı."),
        
        # --- Sözdizimi ve Beklenen Karakterler ---
        (r"error: expected '(.+?)' before '(.+?)'", "Sözdizimi: '{1}' ifadesinden önce bir '{0}' beklerdim, gözünden kaçmış olabilir mi?"),
        (r"error: expected ';' before '(.+?)'", "'{0}' ifadesinden önce noktalı virgül (;) eksik kalmış, daktilo orayı atlayamaz."),
        (r"expected '(.+?)'", "Şu ifade bekleniyor: '{0}'. Unutmuş olabilir misin yeğenim?"),
        (r"missing '(.+?)'", "Eksik karakterimiz var: '{0}'. Bir kontrol etsen iyi olur."),
        (r"expected expression", "Burada bir ifade (sayı, değişken vs.) bekliyorum, boş geçmeyelim."),
        (r"expected ';'", "Satır sonuna noktalı virgül (;) koymayı unutmuşsun, daktilo burada durdu."),
        
        # --- Tür ve Fonksiyon Hataları ---
        (r"error: invalid conversion from '(.+?)' to '(.+?)'", "Tür uyumsuzluğu! '{0}' türünü alıp '{1}' yapmaya çalışıyorsun ama bu boya bu duvara tutmaz."),
        (r"error: no matching function for call to '(.+?)'", "'{0}' fonksiyonu bu bilgilerle çalışamaz, parametreleri bir kontrol et."),
        (r"function '(.+?)' not found", "Fonksiyon Bulunamadı: '{0}'. İsmi doğru yazdın mı? Belki dahil etmen gereken bir kütüphane vardır."),
        (r"unknown type '(.+?)'", "Bilinmeyen Tür: '{0}'. GümüşDil'in dağarcığında böyle bir veri tipi yok."),
        
        # --- Blok ve Parantez Hataları ---
        (r"unmatched '\{'", "Kapatılmamış Blok: '{ ' açtın ama kapısını ( } ) ardına kadar açık bıraktın."),
        (r"unmatched '\}'", "Fazladan Kapatma: ' } ' var ama bunun açılışı ({) nerede yeğenim?"),
        
        # --- Çalışma Zamanı Hataları (Runtime) ---
        (r"segmentation fault", "⛔ Bellek Erişim Hatası! Erişim yetkin olmayan bir yere dokundun, sistem kendini korumaya aldı."),
        (r"division by zero", "⛔ Sıfıra Bölme Hatası! Matematiği bükemezsin yeğenim, payda sıfır olamaz!"),
        (r"stack overflow", "⛔ Yığın Taşması! Sonsuz bir döngünün içinde kaybolmuş olabilirsin, daktilo yetişemiyor."),
        
        # --- Dosya Hataları ---
        (r"no such file or directory", "Belirttiğin adreste böyle bir dosya veya klasör yok yeğenim."),
        (r"permission denied", "Erişim Reddedildi! Kapılar kapalı, yetkin yetmiyor veya dosya şu an meşgul.")
    ]

    @staticmethod
    def translate(text):
        """Metindeki hata mesajlarını bulup Türkçeye çevirir"""
        if not text: return text
        
        lines = text.split('\n')
        translated_lines = []
        
        for line in lines:
            line_str = line.strip()
            
            # Sadece hata veya uyarı içeren satırları çevirmeye çalış
            if not ("error" in line_str.lower() or "warning" in line_str.lower() or "hata" in line_str.lower()):
                translated_lines.append(line)
                continue
                
            found = False
            for pattern, template in ErrorTranslator.TRANSLATIONS:
                match = re.search(pattern, line_str, re.IGNORECASE)
                if match:
                    # Hata bulundu!
                    if match.groups():
                        translated_msg = template.format(*match.groups())
                    else:
                        translated_msg = template
                    
                    # Orijinal satır numarasını korumaya çalış (örn: line 10: error...)
                    line_match = re.search(r'(line\s+\d+|:\d+:)', line_str, re.IGNORECASE)
                    prefix = ""
                    if line_match:
                        prefix = f"📍 {line_match.group(0)} "
                    
                    # Hata ise Kırmızı, Uyarı ise Sarı emoji
                    icon = "⚠️" if "warning" in line_str.lower() else "🔴 HATA:"
                    
                    translated_lines.append(f"{prefix}{icon} {translated_msg}")
                    found = True
                    break
            
            if not found:
                # Eşleşme yoksa ama error kelimesi varsa
                if "error" in line_str.lower():
                    translated_lines.append(f"🔴 {line_str}")
                elif "warning" in line_str.lower():
                    translated_lines.append(f"⚠️ {line_str}")
                else:
                    translated_lines.append(line)
                    
        return '\n'.join(translated_lines)

