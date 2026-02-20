import customtkinter as ctk

def gumus_kayit(manager):
    print("🚀 [Plugin] Merhaba Dünya eklentisi kayit oluyor!")
    manager.register_hook("on_startup", selamla)
    manager.register_hook("on_ui_setup", ui_ekle)
    return "MerhabaInstance"

def selamla():
    print("👋 [Plugin Hook] IDE açıldı, Gümüş-Modül devrede! Selamlar komutan.")

def ui_ekle(app):
    """
    Bu fonksiyon IDE başlatılırken çağrılır.
    'app' parametresi MainWindow nesnesidir.
    """
    print("🎨 [Plugin Hook] UI hazırlanıyor, toolbar'a buton ekleniyor...")
    
    # Araç çubuğuna (Toolbar) yeni bir buton ekleyelim
    try:
        # MainWindow'un 'toolbar_frame' bileşenine erişiyoruz
        btn = ctk.CTkButton(
            app.toolbar_frame, 
            text="👋 Eklenti", 
            command=lambda: app.show_toast("Merhaba Dünya! Gümüş-Modül çalışıyor. 🚀", "success"),
            fg_color="#8e24aa", # Mor renk
            hover_color="#ab47bc",
            width=100,
            height=32,
            corner_radius=4,
            font=("Segoe UI", 12, "bold")
        )
        # Mevcut butonların sağına ekle
        btn.pack(side="left", padx=5, pady=8)
        
    except Exception as e:
        print(f"❌ [Plugin Error] UI güncelleme hatası: {e}")

