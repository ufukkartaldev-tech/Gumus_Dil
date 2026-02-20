class ContextActionHandler:
    """Sağ Tık (Context) Aksiyonlarını Yönetir"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        # self.sidebar = main_window.sidebar # Sidebar init sonrası referanslanmalı
        
    def handle_action(self, action, text):
        """Editör üzerindeki yüzen bar'dan gelen aksiyonları işle"""
        sidebar = getattr(self.main_window, 'sidebar', None)
        
        if action == "summarize":
            if sidebar and hasattr(sidebar, 'ai_panel'):
                sidebar.switch_mode("ai")
                sidebar.ai_panel.receive_external_query(f"Seçili kodu özetle: \n```\n{text}\n```")
        
        elif action == "explain":
            if sidebar and hasattr(sidebar, 'ai_panel'):
                sidebar.switch_mode("ai")
                sidebar.ai_panel.receive_external_query(f"Bu kod ne yapıyor, açıklar mısın? \n```\n{text}\n```")
        
        elif action == "run":
            self._handle_run_snippet(text)
            
        elif action == "quick_fix":
            if sidebar and hasattr(sidebar, 'ai_panel'):
                sidebar.switch_mode("ai")
                data = text # Dict containing line, error, code
                sidebar.ai_panel.request_quick_fix(data)
                self.main_window.show_toast("Gümüş-Tamir Analiz Başlatıldı... 🧠", "info")

    def _handle_run_snippet(self, text):
        """Seçili bloğu yeni bir dosyada (geçici) çalıştır"""
        if not text.strip():
            self.main_window.show_toast("Çalıştıracak bir kod seçmedin yeğenim!", "warning")
            return
            
        from ..config import TEMP_DIR
        import os, threading
        
        if not TEMP_DIR.exists(): os.makedirs(TEMP_DIR)
        ctx_run_file = TEMP_DIR / "ctx_run.tr"
        
        try:
            with open(ctx_run_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            term = self.main_window.terminal
            term.write_text("\n>>> Seçili Blok Çalıştırılıyor...\n")
            
            # TODO: MainWindow üzerindeki butonları kontrol etmek yerine CodeRunner event'lerini kullanmalı
            # Şimdilik direkt CodeRunner'a paslıyoruz ama buton state'leri MainWindow'da kalıyor
            # self.main_window.run_btn.configure... (Bu tight-coupling'i çözmek lazım)
            
            # Threading mantığını CodeRunner zaten yapıyor ama bu "geçici dosya çalıştırma" özel bir durum.
            # CodeRunner'a `run_file(path, temporary=True)` gibi bir özellik eklenebilir.
            # Şimdilik eski mantığı koruyarak buraya taşıyalım.

            self.main_window.code_runner.run_code(file_path=ctx_run_file)
            self.main_window.show_toast("Seçili blok başlatıldı! ⚙️", "success")
            
        except Exception as e:
            self.main_window.show_toast(f"Çalıştırma Hatası: {e}", "error")

    def handle_fix_request(self, error_data):
        """Terminaldeki 'GümüşTamir' butonuna tıklandığında çalışır"""
        sidebar = getattr(self.main_window, 'sidebar', None)
        if not sidebar: return

        # Sidebar'ı AI moduna sok ve görünür yap
        sidebar.switch_mode("ai")
        
        # Hata bilgilerini AI Paneline gönder
        class ErrorInfo:
            def __init__(self, data):
                self.line = data.get('line', '?')
                self.type = type('obj', (object,), {'value': data.get('type', 'HATA')})
                self.message = data.get('message', 'Bilinmeyen hata.')
                self.ai_analysis = data.get('suggestion', "Bu hata üzerinde çalışıyorum...")
        
        # AI paneline pasla
        if hasattr(sidebar, 'ai_panel'):
            sidebar.ai_panel.handle_error(ErrorInfo(error_data))
            
        # Toast bildirimi
        self.main_window.show_toast("GümüşTamir Analiz Ediyor... 🧠", "info")

