# -*- coding: utf-8 -*-
import json
import os

def convert_to_jsonl(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Hata: {input_file} bulunamadı.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    formatted_data = []
    for item in raw_data:
        entry = {
            "instruction": "Aşağıdaki talebi GümüşDil programlama dilini kullanarak yerine getir ve daktilo jargonunu unutma.",
            "input": item["talep"],
            "output": f"Bak hele yeğenim, istediğin kodu daktiloda mühürledim:\n\n```gümüşdil\n{item['kod']}\n```\n\nBu kodun çıktısı şöyle olur: {item['çıktı']}"
        }
        formatted_data.append(entry)

    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in formatted_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    print(f"✓ Başarılı: {len(formatted_data)} örnek {output_file} dosyasına mühürlendi.")

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_path, "..", "data", "ai_egitim_verisi.json")
    output_path = os.path.join(base_path, "..", "..", "..", "gumusdil_dataset.jsonl")
    convert_to_jsonl(input_path, output_path)

