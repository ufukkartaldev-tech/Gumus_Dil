# -*- coding: utf-8 -*-
import os
import json
import requests

class GumusIntelligenceEngine:
    """
    GümüşDil Akıllı Zeka Motoru
    Ollama API üzerinden yerel LLM (gumus_zeka) ile iletişim kurar.
    """
    
    def __init__(self, use_local_model=True):
        self.use_local_model = use_local_model
        self.local_model_endpoint = "http://localhost:11434/api/generate"
        self.model_name = "gumus_zeka"
        
    def generate_response(self, query, context_code=""):
        """Gelen sorguya Gümüş Zeka usulü cevap ver"""
        
        if not self.use_local_model:
            return "⚠️ Yerel model devre dışı yeğenim. Ayarlardan bi el atıver."

        return self._call_local_llm(query, context_code)

    def _call_local_llm(self, query, context_code):
        """Ollama üzerinden gumus_zeka modelini çağırır"""
        try:
            # Gelişmiş prompt yapılandırması
            prompt = query
            if context_code:
                prompt = (
                    f"Aşağıdaki GümüşDil kodunu incele ve soruyu ona göre cevapla:\n"
                    f"```gümüşdil\n{context_code}\n```\n\n"
                    f"Soru: {query}"
                )
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.6,
                    "top_p": 0.9,
                    "stop": ["```"]
                }
            }
            
            response = requests.post(self.local_model_endpoint, json=payload, timeout=45)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "").strip()
                
                if not ai_response:
                    return "Bak hele yeğenim, daktilo mürekkep kaçırmış herhalde, cevap gelmedi."
                
                return ai_response
            else:
                return (
                    f"⚠️ Eyvah yeğenim! Daktilo arıza yaptı (Hata: {response.status_code}).\n"
                    f"Ollama'ya bi' bak hele, duman mı çıkarıyor?"
                )
                
        except requests.exceptions.ConnectionError:
            return self._offline_fallback(query)
        except Exception as e:
            return f"❌ Beklenmedik bir durum oldu yeğenim: {str(e)}"
            
    def _offline_fallback(self, query):
        """Ollama çalışmadığında JSON/JSONL veri setlerinden en yakın cevabı bulur"""
        import difflib
        
        # Olası veri dosyaları
        dataset_paths = [
            os.path.join(os.path.dirname(__file__), "..", "data", "ai_egitim_verisi.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "gumusdil_dataset.jsonl")
        ]
        
        sorular = []
        cevaplar = []
        
        for p in dataset_paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        if p.endswith(".json"):
                            veri = json.load(f)
                            for item in veri:
                                if "talep" in item and "kod" in item:
                                    sorular.append(item["talep"])
                                    cevaplar.append(f"```gümüşdil\n{item['kod']}\n```")
                        elif p.endswith(".jsonl"):
                            for line in f:
                                item = json.loads(line)
                                if "instruction" in item and "output" in item:
                                    sorular.append(item["instruction"])
                                    cevaplar.append(item["output"])
                except Exception:
                    pass
                    
        if sorular:
            eslesen = difflib.get_close_matches(query, sorular, n=1, cutoff=0.4)
            if eslesen:
                idx = sorular.index(eslesen[0])
                return (
                    f"⚠️ [Çevrimdışı Mod] Ollama kapalı olduğu için kendi hafızamdan cevaplıyorum:\n\n"
                    f"{cevaplar[idx]}"
                )
                
        return (
            "❌ Bağlantı koptu aslanım! Ollama çalışmıyor ve kendi belleğimde de bu sorunun cevabını bulamadım.\n"
            "Terminali aç, 'ollama serve' yaz, yaylayı ayağa kaldır!"
        )

    def get_system_status(self):
        """Ollama servisinin durumunu kontrol eder"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                is_ready = any(m.get("name") == self.model_name or m.get("name").startswith(self.model_name) for m in models)
                if is_ready:
                    return "✅ Gümüş Zeka hazır, daktilo başında!"
                else:
                    return f"⚠️ Ollama çalışıyor ama '{self.model_name}' modelini bulamadım yeğenim."
            return "❓ Ollama'dan ses gelmiyor."
        except:
            return "❌ Ollama servisi kapalı. Milli daktilo çalışmaz!"

