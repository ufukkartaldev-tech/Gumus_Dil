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
            return (
                "❌ Bağlantı koptu aslanım! Ollama çalışıyor mu?\n"
                "Terminali aç, 'ollama serve' yaz, yaylayı ayağa kaldır!"
            )
        except Exception as e:
            return f"❌ Beklenmedik bir durum oldu yeğenim: {str(e)}"

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

