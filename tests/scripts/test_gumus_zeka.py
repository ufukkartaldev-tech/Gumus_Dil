# -*- coding: utf-8 -*-
import sys
import codecs

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Path ekleme (modulu bulabilmesi icin)
import sys
import os
sys.path.append(os.getcwd())

from src.ide.core.ai_engine import GumusIntelligenceEngine

print("Gumus Zeka Testi Baslatiliyor...")

# Motoru baslat (yerel modda)
engine = GumusIntelligenceEngine(use_local_model=True)

# Test sorgusu
query = "Bana bir GumusDil 'Merhaba Dunya' kodu yaz."
print(f"\nSoru: {query}")

# Yanıt al
try:
    response = engine.generate_response(query)
    print("\nCevap:")
    print("-" * 40)
    print(response)
    print("-" * 40)
except Exception as e:
    print(f"Hata: {e}")

