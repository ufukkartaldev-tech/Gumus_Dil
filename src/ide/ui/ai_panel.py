
import customtkinter as ctk
import random
from datetime import datetime
from ..core.ai_engine import GumusIntelligenceEngine
import difflib
import re
import json
import os

from ..core.summarizer import GumusSummarizer

class AIPanel(ctk.CTkFrame):
    def __init__(self, parent, config, on_apply_code=None, on_get_code=None):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_apply_code = on_apply_code
        self.on_get_code = on_get_code
        
        # --- RAG: Yerel Bilgi Sandığını Yükle ---
        self.knowledge_base = []
        try:
            kb_path = os.path.join(os.getcwd(), "src", "ide", "data", "gumus_bilgi.json")
            if os.path.exists(kb_path):
                with open(kb_path, "r", encoding="utf-8") as f:
                    self.knowledge_base = json.load(f)
                print(f"RAG: {len(self.knowledge_base)} bilgi vagonu yüklendi.")
            else:
                print("RAG: Bilgi sandığı bulunamadı, boş vagonla devam.")
        except Exception as e:
            print(f"RAG Hatası: {e}")
            
        # Üst Başlık
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Premium Logo & Title
        self.ai_icon = ctk.CTkLabel(self.title_frame, text="✨", font=("Segoe UI", 20))
        self.ai_icon.pack(side="left", padx=(0, 5))
        
        self.ai_title = ctk.CTkLabel(self.title_frame, text="GÜMÜŞ ZEKA", font=("Segoe UI", 12, "bold"))
        self.ai_title.pack(side="left")
        
        self.status_indicator = ctk.CTkLabel(
            self.title_frame, 
            text="● Çevrimiçi", 
            font=("Segoe UI", 10, "bold"), 
            text_color="#00e676"
        )
        self.status_indicator.pack(side="right")
        
        # Mesaj Alanı (Chat History)
        self.chat_history = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            label_text="", # Varsayılan etiketi kaldır
        )
        self.chat_history.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Typing Indicator (Gizli başlar)
        self.typing_frame = ctk.CTkFrame(self.chat_history, fg_color="transparent")
        self.typing_label = ctk.CTkLabel(
            self.typing_frame, 
            text="Gümüş Zeka yazıyor...", 
            font=("Segoe UI", 10, "italic"),
            text_color="#888888"
        )
        self.typing_label.pack(side="left", padx=20)
        
        # Giriş Alanı (Modern Glassy look)
        self.input_wrapper = ctk.CTkFrame(self, fg_color=("gray90", "#1e1e1e"), corner_radius=20)
        self.input_wrapper.pack(fill="x", padx=10, pady=10)
        
        self.input_entry = ctk.CTkEntry(
            self.input_wrapper, 
            placeholder_text="Daktiloya bir şeyler fısılda...", 
            height=40,
            font=("Segoe UI", 12),
            fg_color="transparent",
            border_width=0
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(15, 5))
        self.input_entry.bind("<Return>", self.send_message)
        
        self.send_btn = ctk.CTkButton(
            self.input_wrapper, 
            text="🚀", 
            width=36, 
            height=36, 
            corner_radius=18,
            text_color="white",
            font=("Segoe UI", 16),
            command=self.send_message
        )
        self.send_btn.pack(side="right", padx=2)
        
        # Error handling flag
        self.is_error_mode = False
        self.current_error = None
        self.current_fix_line = None
        
        # AI Engine
        self.ai_engine = GumusIntelligenceEngine(use_local_model=True)
        
        # Başlangıç Mesajı
        self.add_message("Merhaba aslanım! Gümüş Zeka emrine amade. Kodun dumanı mı tütüyor yoksa yeni bir mühür mü basacağız?", is_user=False)
    
    def scroll_to_bottom(self):
        """En alta kaydır (Render sonrası garanti olsun diye)"""
        self.chat_history._parent_canvas.update_idletasks()
        self.chat_history._parent_canvas.yview_moveto(1.0)

    def show_typing(self, show=True):
        """Yazıyor... göstergesini yönet"""
        if show:
            self.typing_frame.pack(fill="x", side="bottom", pady=5)
            self.scroll_to_bottom()
        else:
            self.typing_frame.pack_forget()

    def send_message(self, event=None):
        msg = self.input_entry.get().strip()
        if not msg: return
        
        # Kullanıcı mesajını ekle
        self.add_message(msg, is_user=True)
        self.input_entry.delete(0, "end")
        
        # Yazıyor efektini başlat
        self.show_typing(True)
        self.after(1000, lambda: self.process_response(msg))
        
    def _apply_mood(self, text):
        """Metne 'Dayı' ruhu katar (Basit rastgele eklemeler)"""
        if random.random() < 0.2:
            moods = [" yeğenim", " aslanım", " genç meslektaşım"]
            text += random.choice(moods)
        return text

    def add_message(self, text, is_user=False, is_error=False):
        self.show_typing(False) 
        
        if not is_user:
            text = self._apply_mood(text)

        theme = self.config.THEMES[self.config.theme]
        
        # Premium Bubble Styling
        if is_user:
            bg_color = theme['accent']
            text_color = "white"
            align = "right"
            corner_radius = 15
        elif is_error:
            bg_color = "#441111"
            text_color = "#ff4d4d"
            align = "left"
            corner_radius = 15
        else:
            bg_color = theme['editor_bg']
            text_color = theme['fg']
            align = "left"
            corner_radius = 15
            
        # Mesaj Kutusu Wrapper
        container = ctk.CTkFrame(self.chat_history, fg_color="transparent")
        container.pack(fill="x", pady=4, padx=5)
        
        # Baloncuk
        bubble = ctk.CTkFrame(
            container, 
            fg_color=bg_color, 
            corner_radius=15,
            border_width=1 if not is_user else 0,
            border_color=theme['border'] if not is_error else "#ff1744"
        )
        bubble.pack(side=align, padx=5, ipadx=2, ipady=2)
        
        # --- Mesaj İçeriği: Metin ve Kod Bloklarını Ayrıştır ---
        # Regex ile ```kod``` bloklarını bul
        parts = re.split(r'(```[\s\S]*?```)', text)
        
        for part in parts:
            if not part: continue
            
            if part.startswith("```") and part.endswith("```"):
                # Kod Bloğu
                code_content = part.strip("`").strip()
                # Dil etiketini temizle (örn: ```gümüşdil)
                lines = code_content.split('\n')
                if len(lines) > 0 and len(lines[0].split()) == 1 and not lines[0].strip().startswith(('yazdır', 'eğer', 'döngü')):
                     code_content = '\n'.join(lines[1:])
                
                code_box = ctk.CTkTextbox(
                    bubble, 
                    height=min(200, 20 + len(code_content.split('\n')) * 18),
                    font=("Consolas", 11),
                    fg_color=("#f0f0f0", "#121212") if not is_user else ("#ffffff", "#000000"),
                    text_color=theme['fg'] if not is_user else "white",
                    border_width=0,
                    corner_radius=8
                )
                code_box.insert("1.0", code_content)
                code_box.configure(state="disabled")
                code_box.pack(padx=10, pady=5, fill="x")
            else:
                # Normal Metin
                label = ctk.CTkLabel(
                    bubble, 
                    text=part.strip(), 
                    text_color=text_color, 
                    font=("Segoe UI", 11),
                    wraplength=220, 
                    justify="left"
                )
                label.pack(padx=12, pady=5)
        
        # Zaman Damgası (Subtle)
        now = datetime.now().strftime("%H:%M")
        time_label = ctk.CTkLabel(
            container, 
            text=now, 
            font=("Segoe UI", 8), 
            text_color=theme['comment']
        )
        time_label.pack(side=align, padx=10, pady=(0, 5))
        
        self.scroll_to_bottom()

    def process_response(self, query):
        q = query.lower()
        
        # 0. Katman: Yerel Model Kontrolü
        local_resp = self.ai_engine.generate_response(query, self.on_get_code() if self.on_get_code else "")
        if local_resp:
            self.add_message(local_resp, is_user=False)
            return

        # --- ÖZETLEME (Gümüş Anlatıcı) ---
        if any(word in q for word in ["özetle", "özet", "analiz et", "bu kod ne", "ne yapıyor"]):
            if self.on_get_code:
                code = self.on_get_code()
                summary = GumusSummarizer.summarize(code)
                self.add_message(summary, is_user=False)
                return
            else:
                self.add_message("Editöre duman çöktü, kodu okuyamıyorum yeğenim!", is_user=False)
                return

        # --- PYTHON / C++ -> GÜMÜŞ TERCÜMANI ---
        # Eğer mesajda python/c++ geçiyorsa veya kod bloğu varsa 
        is_translation_request = any(word in q for word in ["python", "c++", "cpp", "tercüme", "çevir", "gumus", "gümüş"])
        has_code_block = "```" in query or "\n" in query and any(c in query for c in [":", "def ", "import ", "{", "cout", "int "])
        
        if is_translation_request and has_code_block:
            # Kod bloğunu ayıkla
            code_to_translate = query
            is_cpp = "c++" in q or "cpp" in q or "cout" in q or "std::" in q or "int main" in q
            
            if "```" in query:
                parts = query.split("```")
                code_to_translate = parts[1]
                # Dil belirtecini temizle (python, cpp vb.)
                first_line = code_to_translate.split('\n')[0].strip().lower()
                if first_line in ["python", "cpp", "c++", "c"]:
                    code_to_translate = "\n".join(code_to_translate.split('\n')[1:])
            
            try:
                if is_cpp:
                    from ..core.cpp_to_gumus import CppToGumusTranspiler
                    translator = CppToGumusTranspiler()
                    source_lang = "C++"
                else:
                    from ..core.python_to_gumus import PythonToGumusTranspiler
                    translator = PythonToGumusTranspiler()
                    source_lang = "Python"
                
                gumus_code = translator.transpile(code_to_translate)
                
                resp = f"Ooo, {source_lang} mühürlü bir mesaj geldi! Dayın senin için bunu GümüşDil'e tercüme etti yeğenim:\n\n"
                resp += f"```gümüşdil\n{gumus_code}\n```\n\n"
                resp += "Daktiloya mühürleyelim mi? (Uygula diyebilirsin)"
                
                self.add_message(resp, is_user=False)
                # Uygula butonu ekle
                self.after(500, lambda: self._show_auto_fix_option(gumus_code))
                return
            except Exception as e:
                self.add_message(f"Tercüme dumanı tütüyor ama alev almadı yeğenim! Hata: {e}", is_user=False)
                return

        response = "Hmm, bunu henüz öğrenmedim. Ama seninle birlikte gelişiyorum! 🌱"
        
        # --- RAG: Akıllı Arama (Layer 1) ---
        found_in_rag = False
        
        best_rag_match = None
        max_score = 0
        
        for item in self.knowledge_base:
            score = 0
            keywords = [k.lower() for k in item.get("keywords", [])]
            answer = item.get("answer", "").lower()
            
            # 1. Keyword Tam Eşleşme (Kuvvetli)
            for kw in keywords:
                if kw in q:
                    score += 10
            
            # 2. Bulanık Cümle Eşleşmesi (Levenshtein Ratio)
            pattern = item.get("question", "").lower()
            if pattern:
                ratio = difflib.SequenceMatcher(None, q, pattern).ratio()
                if ratio > 0.6:
                    score += int(ratio * 20)
            
            # 3. Önemli Kelime Kesişimi
            q_words = set(re.findall(r'\w+', q))
            kw_set = set(keywords)
            overlap = len(q_words.intersection(kw_set))
            score += overlap * 2
            
            if score > max_score:
                max_score = score
                best_rag_match = item
        
        # Eşik değer: Yeterli güvenirlik puanı (örn: en az 1-2 keyword veya iyi bir match)
        if best_rag_match and max_score >= 10:
            response = best_rag_match["answer"]
            found_in_rag = True
            
        if found_in_rag:
            self.add_message(response, is_user=False)
            return

        # --- Gümüş Zeka: Başmühendis Bilgi Bankası (Layer 2) ---
        responses = {
            # Karşılama & Hal Hatır
            "merhaba": "Ooo, merhaba genç meslektaşım! Daktilonun tuşları bugün ne kadar hızlı? 🚀",
            "selam": "Aleykümselam yeğenim! Kodlar tıkırında mı? 💻",
            "nasılsın": "Ben bir yapay zekayım ama senin yazdığın o temiz kodları görünce işlemcim ferahlıyor! Sen nasılsın?",
            "kimsin": "Ben Gümüşdil'in Başmühendisiyim. Kodun sıkışırsa, mantığın karışırsa buradayım.",

            # Teknik Kavramlar (Gümüşhane Usulü)
            "değişken": "Değişken dediğin, veriyi sakladığın kavanozdur yeğenim. Ama üstüne etiket yapıştırmayı (isim vermeyi) unutma, sonra 'bu neydi' diye arama.",
            "döngü": "Döngüler, işi otomatiğe bağlar. Ama dikkat et, duracağı yeri söylemezsen Gümüşhane’nin deresi gibi akar gider (Sonsuz Döngü), bilgisayarı yorar. 'kır' komutunu cebinde tut.",
            "eğer": "Hayat gibi kodlama da tercihlerden ibarettir. 'Eğer' (if) ile yolları ayırırsın, 'değilse' (else) ile B planına geçersin.",
            "fonksiyon": "Bir işi iki kere yapıyorsan, onu 'Fonksiyon' yap yeğenim. Kodu parçala, yönet, daktiloyu (ve kendini) boşuna yorma.",
            "sınıf": "Sınıf (Class), nesnenin kalıbıdır. İnşaatın projesi gibi düşün; proje bir tane, bina bin tane.",

            # Mantıksal ve Algoritmik Strateji
            "kısa yol": "Yeğenim, bir problemi çözmenin 50 yolu vardır. Önemli olan en hızlısı değil, daktiloda yazarken en az hataya meyilli olanıdır. Kodu sadeleştir.",
            "böl": "Büyük bir kütüğü tek seferde yakamazsın, parçalara böleceksin. Kod da öyledir; modüllere böl ki hem kafan ferahlasın hem de hata çıkınca nerede olduğunu şak diye bul.",
            "mantık": "Kod çalışıyor ama sonuç yanlışsa buna 'Mantık Hatası' denir. Çayı demledin ama içine şeker yerine tuz attın gibi düşün. Tadı kaçar ama bardak hala çay bardağıdır. ☕🧂",
            "sıfır": "Sayıyı sıfıra mı böldün? Matematikte de yazılımda da bu bir kara deliktir. Yapma yeğenim.",

            # Yazılım Mühendisliği Etiği ve Disiplini
            "test": "Gümüşhane kalesi bir günde yapılmadı, her taşı tek tek kontrol edildi. Kodunu test etmeden 'bitti' deme, sonra terminalde kırmızı ışık yanınca üzülürsün. 🏰",
            "eski": "Silme yeğenim, yorum satırına al. Geçmişini bilmeyen geleceğini kuramaz (veya eski kod lazım olur). Bir gün döner bakarsın.",
            "isim": "Değişken ismine a, b, c deme yeğenim. Yarın bakınca 'bu neydi?' dersin. `sayac`, `toplam_puan` gibi net isimler koy ki kodun şiir gibi okunsun.",
            "yorum": "Koduna not düş (yorum satırı), ki senden sonra okuyan (veya 6 ay sonraki sen) sana dua etsin. Kodun hafızası yoktur, yorumun vardır.",
            "karmaşık": "Bir fonksiyonun içine 50 tane 'eğer' koyma; fonksiyonu parçala. Basit olan güzeldir, karmaşık olan kırılgandır.",

            # Psikolojik Konfor ve Zihin Sağlığı
            "takıldım": "Parmakların daktiloda yorulduysa zihnin de yorulmuştur. Yazılım bir maratondur, depar değil. Kalk bir bardak su iç, yaylaları düşün, gelince o hata zaten kendiliğinden çözülecek. 🏞️",
            "mükemmel": "Sana bir sır vereyim yeğenim; mükemmel kod yoktur, çalışan kod vardır. Kendine bu kadar yüklenme, bugün bu haliyle gayet janti duruyor.",
            "sıkıldım": "Yeğenim kalk bir temiz hava al, bir Gümüşhane kuşburnusu iç gel. Çözüm bazen ekrana bakarken değil, uzaklara bakarken gelir. 🏔️",
            "yapamıyorum": "Pes etmek yok! Her hata yeni bir tecrübedir. Kodunu tekrar kontrol et, başarabilirsin! 💪",

            # Daktilo Ruhlu Özel Tetikleyiciler (Dayı Modu)
            "başla": "En zor satır ilk satırdır. Önce bir yazdır('Selam') de, daktilonun sesi gelsin, gerisi çorap söküğü gibi gelir.",
            "çalışmıyor": "Sakin! Daktiloda mürekkep mi bitti? Hayır. Mantıkta bir tıkanıklık var. Satırları tek tek oku, dertleş onlarla.",
            "gümüşhane": "Mühendisliğin başkenti, azmin kalesidir yeğenim! Buradan çıkan kod dünyaya hükmeder. 💎",
            "düzenli": "Kodun Gümüşhane evlerinin mimarisi gibi simetrik ve temiz duruyor. OKB'yi daktilo estetiğine çevirmen şahane! ✨",

            # Yardım Çığlıkları
            "???": "Kafan mı karıştı yeğenim? Dur, derin bir nefes al. Kodun süslü parantezlerini { } bir sayalım, genelde biri eksik çıkar.",
            "imdat": "Sakin ol! Gümüşhane'de kimse yolda kalmaz. Kodun hangi satırı canını yakıyor? Bana hatayı söyle, beraber çözelim.",
            "neden": "Yazılımda 'neden çalışmıyor' sorusunun cevabı genelde bir önceki satırda, 'neden çalışıyor' sorusunun cevabı ise StackOverflow'da gizlidir. 😄",
            
            # Final
            "bitti": "Yeğenim 'biten kod' yoktur, 'çalışan kod' vardır. Test ettin mi? Kenar durumlarına (Edge cases) baktın mı? O zaman hayırlı olsun!",
            "temiz": "Kodun yaylalar gibi ferah duruyor, eline sağlık. Okunaklı kod, çalışan koddan daha değerlidir."
        }
        
        # --- Bulanık Mantık (Fuzzy Matching) ---
        best_match = None
        highest_ratio = 0.0
        
        # Cümlenin içindeki kelimeleri ayır (noktalama işaretlerini at)
        words = re.findall(r'\w+', q)
        
        for key, val in responses.items():
            # 1. Direkt içinde geçiyor mu? (En güçlü eşleşme)
            if key in q:
                highest_ratio = 1.0
                best_match = key
                break
            
            # 2. Cümledeki herhangi bir kelime anahtar kelimeye benziyor mu?
            for word in words:
                # Benzerlik oranı (0.0 - 1.0 arası)
                ratio = difflib.SequenceMatcher(None, word, key).ratio()
                
                # %70'den fazla benziyorsa (örn: 'dongu' -> 'döngü')
                if ratio > 0.70:
                    if ratio > highest_ratio:
                        highest_ratio = ratio
                        best_match = key
        
        # Eşleşme yeterince iyiyse cevabı ver
        if best_match and highest_ratio > 0.65:
             response = responses[best_match]
        else:
            # --- Katman 2: Derin Bilgi (Lite RAG) ---
            advanced_knowledge = {
                "bağlı liste": "Bağlı Liste (Linked List), tren vagonları gibidir yeğenim. Her vagon bir sonrakini tutar. Eklemesi kolaydır ama bir elemanı bulmak için baştan sona yürümen gerekir. 🚃",
                "yığın": "Yığın (Stack), üst üste dizilmiş tabaklar gibidir. En son koyduğunu, ilk alırsın (LIFO). Geri al (Undo) butonu tam olarak böyle çalışır. 🥞",
                "kuyruk": "Kuyruk (Queue), fırın sırası gibidir. İlk gelen ekmeği alır (FIFO). Yazıcıya belge gönderdiğinde sıraya girer ya, işte o. 🥖",
                "ağaç": "Ağaç (Tree), soyağacına benzer. Bir kök vardır, dallar ayrılır. Dosya sistemin (klasörler) aslında kocaman bir ağaçtır. 🌳",
                "hash": "Hash Tablosu, kütüphane indeksi gibidir. Kitabı (veriyi) aramakla uğraşmazsın, yerini şak diye bulursun. Hızın adresi burasıdır. ⚡",
                "big o": "Big O, bir algoritmanın ne kadar 'yakıt' yaktığını ölçer. O(1) uçak gibidir, O(n^2) kağnı gibidir. Mümkünse uçağa bin. ✈️"
            }
            
            # İkinci katman taraması
            for key, val in advanced_knowledge.items():
                if key in q:
                     response = val
                     best_match = True # Bulundu bayrağı
                     break
            
            if not best_match:
                # --- Kayıt Defteri (Feedback Loop) ---
                # Cevap veremediğimiz soruyu mühürle
                try:
                    with open("bilinmeyen_sorular.log", "a", encoding="utf-8") as f:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"[{timestamp}] {query}\n")
                except Exception as e:
                    print(f"Loglama hatası: {e}")
                    
                # --- Katman 4: Kod Açıklama (Context-Aware) ---
                if any(word in q for word in ["açıkla", "ne yapıyor", "anlat", "bu nedir"]):
                    self._explain_code()
                    return

                # --- Katman 3: Kod Yazma (Gümüş-Zeka 2.0) ---
                if any(word in q for word in ["kod", "yaz", "oluştur", "yap", "yazdır", "yazılım"]):
                    self._process_code_gen(q)
                    return

                response = "Hmm, bu konu divanda henüz konuşulmadı yeğenim. Kayıt defterime not düştüm, ustalar yakında bu konuya da el atar. 📜"
                
        self.add_message(response, is_user=False)
    
    def _show_auto_fix_option(self, fix_code: str):
        """Auto-fix için aksiyon butonları ekle"""
        theme = self.config.THEMES[self.config.theme]
        
        # Buton container
        btn_container = ctk.CTkFrame(self.chat_history, fg_color="transparent")
        btn_container.pack(fill="x", pady=5, padx=15)
        
        # Evet butonu
        yes_btn = ctk.CTkButton(
            btn_container,
            text="✓ Evet, Uygula",
            fg_color="#4caf50",
            hover_color="#45a049",
            height=35,
            command=lambda: self._apply_fix(fix_code)
        )
        yes_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        # Hayır butonu
        no_btn = ctk.CTkButton(
            btn_container,
            text="✗ Hayır, Manuel Düzelteceğim",
            fg_color="#f44336",
            hover_color="#da190b",
            height=35,
            command=lambda: self._reject_fix()
        )
        no_btn.pack(side="right", padx=5, expand=True, fill="x")
        
    def _apply_fix(self, fix_code: str):
        """Auto-fix'i uygula"""
        if self.on_apply_code:
            # Satır bilgisi varsa satırı uçur, yoksa imlece ekle
            self.on_apply_code(fix_code, line=self.current_fix_line)
            self.add_message("✅ Düzeltme uygulandı! Kodu kontrol et.", is_user=False)
        else:
            self.add_message("❌ Editöre erişilemedi.", is_user=False, is_error=True)
            
        self.is_error_mode = False
        self.current_fix_line = None
        
    def _reject_fix(self):
        """Auto-fix'i reddet"""
        self.add_message("👍 Anlaşıldı! Manuel düzeltme yapabilirsin.", is_user=False)
        self.is_error_mode = False

    def request_quick_fix(self, data):
        """Editörden gelen hızlı tamir isteğini işle"""
        line = data.get('line')
        self.current_fix_line = line
        error_msg = data.get('error')
        current_code = data.get('code', '').strip()
        
        self.add_message(f"📍 Satır {line}: '{current_code}'\n⚠️ {error_msg}", is_user=True)
        
        # AI Analizi ve Tamir Simülasyonu
        self.after(800, lambda: self._process_ai_fix(line, error_msg, current_code))

    def _process_ai_fix(self, line, error_msg, code):
        suggested_fix = None
        analysis = ""
        
        # 1. İngilizce Anahtar Kelime Tamiri
        forbidden = {
            "var": "değişken", "let": "değişken", "if": "eğer", "else": "değilse",
            "while": "döngü", "for": "her", "function": "fonksiyon", "print": "yazdır",
            "return": "dön", "true": "doğru", "false": "yanlış"
        }
        
        fixed_code = code
        for f, r in forbidden.items():
            if f in code.lower():
                fixed_code = re.sub(rf'\b{f}\b', r, fixed_code, flags=re.IGNORECASE)
        
        if fixed_code != code:
            analysis = "Bak hele yeğenim! Gümüşhane'de yabancı kelime konuşulmaz. İngilizce anahtar kelimeyi Türkçe mühürüyle değiştirdim."
            suggested_fix = fixed_code
            
        # 2. Karşılaştırma Hatası ( = yerine == )
        elif "eğer" in code and "=" in code and "==" not in code and "!=" not in code and ">=" not in code and "<=" not in code:
            analysis = "Eğer (if) içinde karşılaştırma yaparken tek eşittir (=) kullanmışsın. Değer atamak ile karşılaştırmak farklıdır, oraya çift eşittir (==) yakışır."
            suggested_fix = code.replace("=", "==")
            
        # 3. Yazdır Parantez Hatası
        elif "yazdır" in code and "(" not in code:
            analysis = "Yazdır komutunu yalın bırakmışsın. GümüşDil'de bağırmak için parantez ( ) gerekir!"
            parts = code.split("yazdır", 1)
            content = parts[1].strip()
            suggested_fix = f"yazdır({content})"

        # 4. Genel Sözdizimi - Eğer hiçbir kural uymadıysa (Genel AI cevabı)
        else:
            analysis = "Buralarda bir duman tütüyor ama tam seçemedim. Satırı Gümüşhane standartlarına göre tekrar mühürlemeyi denedim."
            # Basitçe tırnakları vs kontrol et (placeholder fix)
            suggested_fix = code 

        self.add_message(f"🧠 **Gümüş-Tamir Analizi:**\n{analysis}", is_user=False)
        
        if suggested_fix:
            self.after(1000, lambda: self._show_auto_fix_option(suggested_fix))

    def _process_code_gen(self, q):
        """Gümüş-Zeka 2.0: Doğal dilden kod üretimi"""
        q = q.lower()
        suggested_code = ""
        analysis = ""
        
        if "merhaba dünya" in q:
            analysis = "Dünyaya selam vermek en büyük mühürdür yeğenim. Al sana 'Merhaba Dünya' kodu."
            suggested_code = 'yazdır("Merhaba Dünya")'
        elif "döngü" in q or "saydır" in q:
            analysis = "Sayıları sıraya dizmek bizim işimiz. 1'den 10'a kadar sayan bir döngü mühürledim."
            suggested_code = 'değişken sayac = 1\ndöngü (sayac <= 10) {\n    yazdır(sayac)\n    sayac = sayac + 1\n}'
        elif "fonksiyon" in q or "topla" in q:
            analysis = "İşleri otomatiğe bağlayalım. İki sayıyı toplayan bir mühür (fonksiyon) hazırladım."
            suggested_code = 'fonksiyon topla(a, b) {\n    dön a + b\n}\n\nyazdır(topla(5, 10))'
        elif "rastgele" in q:
            analysis = "Şansını Gümüşhane yaylalarında denemeye ne dersin? Rastgele sayı üreten bir kod."
            suggested_code = 'dahil et matematik\nyazdır("Şanslı Sayın: " + metin(rastgele_sayı(1, 100)))'
        elif "iha" in q or "radar" in q:
            analysis = "Savunma sanayiine mühür vurmak mı istiyorsun? İşte basit bir radar takip sistemi."
            suggested_code = 'dahil et harita\ndaire_çiz(10, "#00ff00", 150, 150)\nyazdır("Hedef Takipte!")'
        else:
            analysis = "Dediğini duydum ama daktilomu ona göre ayarlayamadım. Şimdilik sana temel bir mühür yapısı vereyim."
            suggested_code = 'yazdır("Gümüş-Zeka emrinde!")'

        self.after(800, lambda: self._show_auto_fix_option(suggested_code))

    def _explain_code(self):
        """Mevcut editördeki kodu analiz et ve hergele usulü açıkla"""
        if not self.on_get_code:
            self.add_message("❌ Daktilodaki kağıdı göremiyorum yeğenim!", is_user=False, is_error=True)
            return
            
        code = self.on_get_code()
        if not code.strip():
            self.add_message("📜 Sayfa bomboş yeğenim, neyini açıklayayım? Bir şeyler karala da mühürleyelim.", is_user=False)
            return

        # Basit Analiz
        explanation = "� **Gümüş-Zeka Kod Analizi Merceği:**\n\n"
        
        if "döngü" in code:
            explanation += "🔄 Bakıyorum buralarda bir **döngü** dönüyor. İşleri otomatiğe bağlamışsın, daktilo yorulmasın diye iyi düşünmüşsün.\n"
        if "fonksiyon" in code:
            explanation += "🛠️ **Fonksiyon** mühürleri görüyorum. Kodu parçalara bölmen ustalığa işarettir, aferin yeğenim.\n"
        if "dahil et" in code:
            explanation += "📦 Dışarıdan **kütüphane** çağırmışsın. Yaylanın dışından gelen bu güçle kodun daha kuvvetli duruyor.\n"
        if "yazdır" in code:
            explanation += "📢 Ekrana bir şeyler **yazdırıyorsun**, sesini duyurmak güzeldir.\n"
        if "eğer" in code:
            explanation += "⚖️ **Eğer** (karar) mekanizması kurmuşsun. Kodun artık kendi yolunu seçebiliyor, büyüdüğünü görmek güzel.\n"
            
        if len(code.splitlines()) > 50:
             explanation += "\n⚠️ Yalnız yeğenim, kodun Gümüşhane deresinden uzun olmuş. Biraz modüllere böl de okurken gözümüz yorulmasın."
        else:
             explanation += "\n✨ Kodun mizanpajı gayet temiz, daktiloda janti duruyor."

        self.add_message(explanation, is_user=False)

    def receive_external_query(self, query):
        """Editör veya başka bir yerden gelen talepleri işle"""
        self.add_message(query, is_user=True)
        self.after(500, lambda: self.process_response(query))


