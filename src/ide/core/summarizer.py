# -*- coding: utf-8 -*-
import re
from .symbols import SymbolExtractor

class GumusSummarizer:
    """Gümüşdil kodunu analiz eder ve insan dilinde (Türkçe) özet çıkarır."""

    @staticmethod
    def summarize(code_text):
        if not code_text.strip():
            return "Boş bir daktilo sayfası gibi... Hiçbir şey yazılmamış yeğenim."

        symbols = SymbolExtractor.extract_from_text(code_text)
        
        # Temel analiz
        classes = [s for s in symbols if s['type'] == 'class']
        functions = [s for s in symbols if s['type'] == 'function']
        variables = [s for s in symbols if s['type'] == 'variable']
        
        # Kütüphane bağımlılıklarını bul
        includes = re.findall(r'dahil_et\s*\(?[\'"](.+)[\'"]\)?', code_text)
        
        # Özet metni oluştur (Sade ve Şık)
        summary = "### � Kod Analiz Raporu\n\n"
        
        # 1. Genel Modül Tipi
        if "zeka.tr" in str(includes):
            summary += "Bu modül **yapay zeka** yetenekleri barındırıyor. "
        elif "grafik.tr" in str(includes):
            summary += "Bu modül **görsel/grafik** işlemleri odaklı. "
        elif "veritabani.tr" in str(includes):
            summary += "Bu modül **veri depolama** ve mühürleme üzerine kurulu. "
        else:
            summary += "Standart bir Gümüşdil daktilosu örneği. "

        summary += "\n\n"

        # 2. Yapısal Özet
        if classes:
            summary += f"- **Yapı:** {len(classes)} adet sınıf mühürlenmiş: " + ", ".join([f"`{c['name']}`" for c in classes]) + ".\n"
        
        if functions:
            summary += f"- **İşlev:** {len(functions)} fonksiyon tanımlanmış. Önemli olanlar: " + ", ".join([f"`{f['name']}`" for f in functions[:3]]) + ("..." if len(functions) > 3 else "") + "\n"

        if variables:
            summary += f"- **Hafıza:** {len(variables)} adet kavanoz (değişken) mevcut.\n"

        # 3. Mantıksal Tahmin
        if any(word in code_text for word in ["döngü", "dongu", "eğer", "eger"]):
            summary += "\n--- \n"
            if "döngü" in code_text or "dongu" in code_text:
                summary += "• İçerideki döngülerle işler otomatiğe bağlanmış.\n"
            if "eğer" in code_text or "eger" in code_text:
                summary += "• Karar mekanizmimarirıyla kodun iradesi güçlendirilmiş.\n"

        # 4. Final Notu
        summary += "\n**Dayı'nın Notu:** "
        if len(code_text.split('\n')) > 100:
            summary += "Maşallah, Gümüşhane kalesi gibi sağlam bir kod. Parçalara ayırmayı unutma."
        elif len(functions) == 0 and len(code_text) > 200:
            summary += "Kod biraz düz gidiyor yeğenim, fonksiyon kullanmak daktiloyu yormaz."
        else:
            summary += "Janti ve temiz bir çalışma. Daktilo tıkır tıkır işliyor."

        return summary


