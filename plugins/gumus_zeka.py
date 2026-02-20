import tkinter as tk

def gumus_kayit(manager):
    print("🤖 [Plugin] Gümüş Zeka Bağlantısı (AI Bridge) yükleniyor...")
    manager.register_hook("on_editor_init", editor_bagla)
    return "GumusZekaBridge"

def editor_bagla(editor):
    """Editör sağ tık menüsüne 'AI'ya Sor' ekle"""
    try:
        text_widget = editor._textbox
        
        # Mevcut bind'ları kontrol etmek zor, direkt ekleyelim
        # Tkinter'da sağ tık menüsü genelde yeniden oluşturulur.
        # Bizim 'hazir_kodlar.py' plugin'i de sağ tık kullanıyor.
        # Çakışmayı önlemek için ayrı bir bind yerine, varolan menüye ekleme şansımız yok (Tkinter event-driven).
        # Ancak bind add="+" dediğimiz için her iki plugin de kendi menüsünü açmaya çalışacak.
        # Bu UX açısından kötü olabilir (iki menü üst üste).
        
        # ÇÖZÜM: 'hazir_kodlar.py' gibi kendi menümüzü açmak yerine,
        # Sol alt köşeye veya toolbar'a bir buton eklemek daha güvenli olabilir.
        # YA DA: Seçili metni alıp AI paneline gönderen bir kısayol (Ctrl+Shift+A).
        
        # Kısayol Ekleme (Ctrl+Shift+Q -> Question)
        text_widget.bind("<Control-Q>", lambda e: ai_sor(editor))
        text_widget.bind("<Control-q>", lambda e: ai_sor(editor))
        
        # Sağ tık menüsü (Alternatif: Shift+Sağ Tık)
        text_widget.bind("<Shift-Button-3>", lambda e: sag_tik_ai(e, editor))

    except Exception as e:
        print(f"❌ [AI Plugin] Hata: {e}")

def sag_tik_ai(event, editor):
    """Shift+Sağ Tık ile AI menüsü"""
    menu = tk.Menu(editor, tearoff=0)
    menu.add_command(label="🤖 Bunu Gümüş Zeka'ya Sor", command=lambda: ai_sor(editor))
    menu.tk_popup(event.x_root, event.y_root)

def ai_sor(editor):
    """Seçili metni veya tüm kodu AI paneline gönder"""
    try:
        text_widget = editor._textbox
        
        # Seçili metni al
        try:
            secilen = text_widget.get("sel.first", "sel.last")
        except:
            secilen = ""
            
        if not secilen.strip():
            # Seçim yoksa satırı al veya uyar
            # secilen = text_widget.get("insert linestart", "insert lineend")
            pass
            
        if not secilen.strip():
            print("⚠️ [AI Plugin] Soru sormak için kod seçmelisin.")
            return

        # PluginManager üzerinden APP'e ulaşmamız lazım.
        # Editor nesnesi üzerinden parent zinciri ile app'e (MainWindow) ulaşabiliriz.
        # editor -> editor_content_area -> editor_main_frame -> right_pane -> paned_window -> workspace -> main_container -> root
        # Bu çok kırılgan.
        
        # PluginManager singleton değil ama MainWindow tarafından oluşturuluyor.
        # 'gumus_kayit' fonksiyonunda 'manager.ide' (MainWindow instance) mevcut!
        # Ancak 'editor_bagla' o instance'a sahip değil.
        # Global veya closure kullanabiliriz.
        pass

    except Exception as e:
        print(f"Hata: {e}")

# Closure için global trick (basit çözüm)
MAIN_APP = None

def gumus_kayit(manager):
    global MAIN_APP
    MAIN_APP = manager.ide # MainWindow referansı
    
    print("🤖 [Plugin] Gümüş Zeka Bağlantısı (AI Bridge) yükleniyor...")
    manager.register_hook("on_editor_init", editor_bagla)
    return "GumusZekaBridge"

def editor_bagla(editor):
    text_widget = editor._textbox
    # Ctrl+Q kısayolu
    text_widget.bind("<Control-Q>", lambda e: ai_sor(editor))
    text_widget.bind("<Control-q>", lambda e: ai_sor(editor))
    # Shift+Sağ Tık
    text_widget.bind("<Shift-Button-3>", lambda e: sag_tik_ai(e, editor))

def sag_tik_ai(event, editor):
    menu = tk.Menu(editor, tearoff=0, font=("Segoe UI", 10))
    menu.add_command(label="🤖 Gümüş Zeka'ya Sor", command=lambda: ai_sor(editor))
    menu.tk_popup(event.x_root, event.y_root)

def ai_sor(editor):
    if not MAIN_APP: return
    
    try:
        text_widget = editor._textbox
        try:
            prompt = text_widget.get("sel.first", "sel.last")
        except:
            prompt = "" # text_widget.get("1.0", "end") # Çok uzun olabilir
            
        if not prompt.strip():
            MAIN_APP.show_toast("Önce sormak istediğin kodu seçmelisin! 🖱️", "warning")
            return
            
        # 1. AI Paneline Geç
        if hasattr(MAIN_APP, 'sidebar'):
            MAIN_APP.sidebar.switch_mode("ai")
            
            # 2. Soruyu Gönder
            ai_panel = MAIN_APP.sidebar.ai_panel
            
            # Kullanıcı mesajı olarak ekle
            ai_panel.add_message(prompt, is_user=True)
            
            # AI cevabını tetikle
            # Biraz "context" ekleyelim
            full_prompt = f"Bu kod parçası hakkında ne düşünüyorsun?\n\n{prompt}"
            MAIN_APP.root.after(500, lambda: ai_panel.process_response(prompt))
            
    except Exception as e:
        print(f"AI Bridge Hatası: {e}")

