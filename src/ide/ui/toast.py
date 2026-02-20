import customtkinter as ctk

class ToastNotifier:
    """Bildirim Merkezi: Kullanıcıya geçici mesaj göster"""
    
    def __init__(self, root, config):
        self.root = root
        self.config = config
        
    def show(self, message, kind='info'):
        theme = self.config.THEMES[self.config.theme]
        
        # Renkler
        colors = {
            'success': '#2e7d32', # Yeşil
            'error': '#c62828',   # Kırmızı
            'info': '#0277bd',    # Mavi
            'warning': '#ef6c00'  # Turuncu
        }
        bg_color = colors.get(kind, theme['accent'])
        
        # Toast Frame
        toast = ctk.CTkFrame(self.root, fg_color=bg_color, corner_radius=8, border_width=1, border_color="#ffffff")
        
        # İkonlar
        icons = {'success': '✅', 'error': '❌', 'info': 'ℹ️', 'warning': '⚠️'}
        icon = icons.get(kind, 'ℹ️')
        
        label = ctk.CTkLabel(
            toast, 
            text=f"{icon}  {message}", 
            text_color="white", 
            font=("Segoe UI", 12, "bold"),
            padx=15, 
            pady=10
        )
        label.pack()
        
        # Animasyonlu Gösterim (Sağ Alt Köşe)
        # Hedef konum (Sağ alt, biraz içeride)
        toast.place(rely=1.0, relx=1.0, x=-20, y=-40, anchor="se")
        toast.lift()
        
        # Kaybolma zamanlayıcısı
        self.root.after(3000, lambda: self._fade_toast(toast))
        
    def _fade_toast(self, toast, alpha=1.0):
        """Toast'u yavaşça yok et (Görsel İyileştirme)"""
        try:
            if alpha > 0:
                alpha -= 0.1
                # CustomTkinter widgets don't support partial transparency easily via attributes
                # so we can either destroy or try to change the bg color if possible.
                # Since CTkFrame doesn't support transparency well, we'll just delay and destroy
                # but with a 'sliding down' effect as an alternative to alpha.
                self.root.after(50, lambda: self._fade_toast(toast, alpha))
            else:
                toast.destroy()
        except:
            try: toast.destroy()
            except: pass

