# -*- coding: utf-8 -*-
import random
import re
import difflib
from datetime import datetime

class AIAssistantLogic:
    """Gümüş Zeka için mantıksal katman ve 'Dayı' karakteri"""
    
    RESPONSES = {
        "merhaba": "Ooo, merhaba genç meslektaşım! Daktilonun tuşları bugün ne kadar hızlı? 🚀",
        "selam": "Aleykümselam yeğenim! Kodlar tıkırında mı? 💻",
        "nasılsın": "Ben bir yapay zekayım ama senin yazdığın o temiz kodları görünce işlemcim ferahlıyor! Sen nasılsın?",
        "kimsin": "Ben Gümüşdil'in Başmühendisiyim. Kodun sıkışırsa, mantığın karışırsa buradayım.",
        "değişken": "Değişken dediğin, veriyi sakladığın kavanozdur yeğenim. Ama üstüne etiket yapıştırmayı unutma.",
        "döngü": "Döngüler, işi otomatiğe bağlar. Ama dikkat et, duracağı yeri söylemezsen bilgisayarı yorar.",
        "eğer": "Hayat gibi kodlama da tercihlerden ibarettir. 'Eğer' ile yolları ayırırsın.",
        "fonksiyon": "Bir işi iki kere yapıyorsan, onu 'Fonksiyon' yap yeğenim. Kodu parçala, yönet.",
        "sınıf": "Sınıf (Class), nesnenin kalıbıdır. İnşaatın projesi gibi düşün.",
        "gümüşhane": "Mühendisliğin başkenti, azmin kalesidir yeğenim! 💎"
    }

    ADVANCED_KNOWLEDGE = {
        "bağlı liste": "Bağlı Liste (Linked List), tren vagonları gibidir yeğenim. Her vagon bir sonrakini tutar. 🚃",
        "yığın": "Yığın (Stack), üst üste dizilmiş tabaklar gibidir. En son koyduğunu, ilk alırsın (LIFO). 🥞",
        "kuyruk": "Kuyruk (Queue), fırın sırası gibidir. İlk gelen ekmeği alır (FIFO). 🥖",
        "ağaç": "Ağaç (Tree), soyağacına benzer. Dosya sistemin aslında kocaman bir ağaçtır. 🌳",
        "hash": "Hash Tablosu, kütüphane indeksi gibidir. Hızın adresi burasıdır. ⚡",
        "big o": "Big O, bir algoritmanın ne kadar 'yakıt' yaktığını ölçer. ✈️"
    }

    MOODS = [" yeğenim", " aslanım", " genç meslektaşım", " evladım"]

    @staticmethod
    def apply_mood(text):
        if random.random() < 0.2:
            text += random.choice(AIAssistantLogic.MOODS)
        return text

    @staticmethod
    def get_fuzzy_response(query):
        q = query.lower()
        words = re.findall(r'\w+', q)
        best_match = None
        highest_ratio = 0.0
        
        for key in AIAssistantLogic.RESPONSES:
            if key in q: return AIAssistantLogic.RESPONSES[key]
            for word in words:
                ratio = difflib.SequenceMatcher(None, word, key).ratio()
                if ratio > 0.75 and ratio > highest_ratio:
                    highest_ratio = ratio; best_match = key
        
        if best_match and highest_ratio > 0.7:
             return AIAssistantLogic.RESPONSES[best_match]
        
        for key, val in AIAssistantLogic.ADVANCED_KNOWLEDGE.items():
            if key in q: return val
            
        return None

    @staticmethod
    def generate_code_snippet(query):
        q = query.lower()
        if "merhaba dünya" in q:
            return 'yazdır("Merhaba Dünya")', "Dünyaya selam vermek en büyük mühürdür yeğenim."
        elif "döngü" in q:
            return 'değişken sayac = 1\ndöngü (sayac <= 10) {\n    yazdır(sayac)\n    sayac = sayac + 1\n}', "1'den 10'a kadar sayan bir döngü mühürledim."
        elif "fonksiyon" in q:
            return 'fonksiyon topla(a, b) {\n    dön a + b\n}\n\nyazdır(topla(5, 10))', "İki sayıyı toplayan bir mühür hazırladım."
        return 'yazdır("Bak ne buldum!")', "Sana özel bir mühür bastım."
