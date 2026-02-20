import tkinter as tk

def gumus_kayit(manager):
    print("✨ [Plugin] Hazır Kodlar (Snippets) eklentisi yükleniyor...")
    manager.register_hook("on_editor_init", editor_bagla)

def editor_bagla(editor):
    """Her yeni editör açıldığında çalışır ve sağ tık menüsünü bağlar"""
    try:
        # Editörün içindeki esas Text widget'ını al
        text_widget = editor._textbox
        
        # Sağ tık menüsünü oluştur
        menu = tk.Menu(text_widget, tearoff=0, font=("Segoe UI", 10))
        
        # Menü Başlığı (Disabled)
        menu.add_command(label="💎 Gümüş Kodlar", state="disabled")
        menu.add_separator()
        
        # --- Alt Menü: Kontrol Yapıları ---
        kontrol_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Kontrol Yapıları", menu=kontrol_menu)
        
        kontrol_menu.add_command(label="Eğer Bloğu", command=lambda: kod_ekle(text_widget, 
            "eğer (koşul) {\n    // Kodlar buraya\n}"))
            
        kontrol_menu.add_command(label="Eğer-Değilse", command=lambda: kod_ekle(text_widget, 
            "eğer (koşul) {\n    // Doğruysa\n} değilse {\n    // Yanlışsa\n}"))
            
        kontrol_menu.add_command(label="Döngü (While)", command=lambda: kod_ekle(text_widget, 
            "döngü (koşul) {\n    // Tekrarla\n}"))

        # --- Alt Menü: Tanımlamimarir ---
        tanim_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Tanımlamimarir", menu=tanim_menu)
        
        tanim_menu.add_command(label="Fonksiyon", command=lambda: kod_ekle(text_widget, 
            "fonksiyon isim(p1) {\n    dön p1\n}"))
            
        tanim_menu.add_command(label="Sınıf", command=lambda: kod_ekle(text_widget, 
            "sınıf Araba {\n    fonksiyon baslat() {\n        yazdır(\"Vrum!\")\n    }\n}"))

        menu.add_separator()
        menu.add_command(label="Temel Yazdır", command=lambda: kod_ekle(text_widget, "yazdır(\"Merhaba Dünya!\")"))
        
        # Sağ tık olayını bağla
        # Windows/Linux için <Button-3>, Mac için <Button-2> gerekebilir ama genelde 3 sağ tıktır.
        text_widget.bind("<Button-3>", lambda event: popup_ack(event, menu), add="+")
        
        # print(f"✨ [Snippet Plugin] Editöre bağlandı.")
        
    except Exception as e:
        print(f"❌ [Snippet Plugin] Hata: {e}")

def popup_ack(event, menu):
    """Menüyü farenin olduğu yerde açar"""
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        # Menü kapandığında focus olayını düzeltmek için (opsiyonel)
        menu.grab_release()

def kod_ekle(text_widget, kod_parcasi):
    """İmlecin olduğu yere kodu ekler"""
    try:
        text_widget.insert("insert", kod_parcasi)
        # Eklenen kodu seçili hale getirmek istersen:
        # text_widget.tag_add("sel", "insert-%dc" % len(kod_parcasi), "insert")
    except Exception as e:
        print(f"Hata: {e}")


