import customtkinter as ctk
import tkinter as tk
import json

class GameView(ctk.CTkFrame):
    def __init__(self, parent, config, **kwargs):
        super().__init__(parent, **kwargs)
        self.config = config
        
        # Grid/Blok Ayarları
        self.block_width = 40   # Bloğun genişliği
        self.block_height = 20  # Bloğun üst yüzeyinin yüksekliği (basıklık)
        self.y_step = 20        # Y ekseninde (yukarı) her blok için kaç piksel çıkılacak
        
        self.offset_x = 0
        self.offset_y = 0
        self.voxels = {} # (x, y, z) -> type_id
        
        # UI Setup
        self.top_bar = ctk.CTkFrame(self, height=40)
        self.top_bar.pack(fill="x", padx=5, pady=5)
        
        self.info_label = ctk.CTkLabel(self.top_bar, text="Voxel Engine (İzometrik) Hazır 🎮", font=("Segoe UI", 12, "bold"))
        self.info_label.pack(side="left", padx=10)

        self.reset_btn = ctk.CTkButton(self.top_bar, text="Sıfırla", width=80, height=24, command=self.reset_world)
        self.reset_btn.pack(side="right", padx=5)
        
        # Canvas
        self.canvas = tk.Canvas(self, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Etkilesim
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set()) # Mouse gelince odaklan (Klavye için)
        
        # Klavye (WASD + Yön Tuşları)
        self.canvas.bind("<w>", lambda e: self.move_camera(0, 20))
        self.canvas.bind("<s>", lambda e: self.move_camera(0, -20))
        self.canvas.bind("<a>", lambda e: self.move_camera(20, 0))
        self.canvas.bind("<d>", lambda e: self.move_camera(-20, 0))
        self.canvas.bind("<Up>", lambda e: self.move_camera(0, 20))
        self.canvas.bind("<Down>", lambda e: self.move_camera(0, -20))
        self.canvas.bind("<Left>", lambda e: self.move_camera(20, 0))
        self.canvas.bind("<Right>", lambda e: self.move_camera(-20, 0))
        
        self.configure_colors()

    def configure_colors(self):
        # Temel Renkler
        self.base_colors = {
            1: "#66bb6a",  # Çimen (Canlı Yeşil)
            2: "#90a4ae",  # Taş (Mavi-Gri)
            3: "#42a5f5",  # Su (Mavi)
            4: "#ffa726",  # Tahta (Turuncu)
            5: "#ef5350",  # Tuğla (Kırmızı)
            "default": "#bdbdbd"
        }

    def get_shaded_colors(self, type_id):
        """Bir renk için gölgeli (Üst, Sağ, Sol) versiyonlarını döndür"""
        base = self.base_colors.get(type_id, self.base_colors["default"])
        
        # Hex to RGB
        r = int(base[1:3], 16)
        g = int(base[3:5], 16)
        b = int(base[5:7], 16)
        
        def darken(factor):
            return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"
            
        # Basit Işıklandırma:
        # Üst Yüzey: En parlak (Güneş tepede)
        # Sağ Yüzey: Orta karanlık
        # Sol Yüzey: En karanlık (Gölge tarafı)
        
        return {
            "top": base,
            "right": darken(0.8), # %80 parlaklık
            "left": darken(0.6)   # %60 parlaklık
        }

    def process_command(self, cmd_json):
        try:
            data = json.loads(cmd_json)
            command = data.get("islem")
            
            x = data.get("x", 0)
            y = data.get("y", 0)
            z = data.get("z", 0)
            
            if command == "ekle":
                tip = data.get("tip", 1)
                self.voxels[(x, y, z)] = tip
                self.info_label.configure(text=f"İnşa: ({x},{y},{z}) Tip:{tip}")
                
            elif command == "sil":
                if (x, y, z) in self.voxels:
                    del self.voxels[(x, y, z)]
                self.info_label.configure(text=f"Yıkım: ({x},{y},{z})")
            
            elif command == "temizle":
                self.voxels = {}
                self.canvas.delete("all")
                self.info_label.configure(text="Dünya sıfırlandı.")
            
            self.draw_world()
            
        except Exception as e:
            print(f"GameView Error: {e}")

    def reset_world(self):
        self.voxels = {}
        self.canvas.delete("all")
        self.draw_world() # Grid çiz

    def draw_world(self):
        self.canvas.delete("all")
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        center_x = w // 2 + self.offset_x
        center_y = h // 2 + self.offset_y
        
        # --- DERİNLİK SIRALAMASI (DEPTH SORTING) ---
        # İzometrikte 'arkadan öne' çizmek için:
        # X küçük -> büyük
        # Z küçük -> büyük (veya tersi eksen yönüne göre, burada X+Z derinliği verir)
        # Y küçük -> büyük (aşağıdan yukarı)
        
        # Sıralama anahtarı: (x + z, y, x) 
        # Matematiksel olarak ekran Y koordinatına göre sıralamak en garantisidir ama
        # basit grid sisteminde (x, y, z) tuple sıralaması genelde iş görür.
        # Ancak izometrikte (x+z) derinliktir.
        
        sorted_blocks = sorted(self.voxels.items(), key=lambda item: (item[0][0] + item[0][2], item[0][1], item[0][0]))
        
        # Grid veya Zemin Referansı (Opsiyonel)
        # self.canvas.create_line(center_x-200, center_y, center_x+200, center_y, fill="#333")
        
        for (vx, vy, vz), vtype in sorted_blocks:
            self.draw_block(center_x, center_y, vx, vy, vz, vtype)

    def draw_block(self, cx, cy, x, y, z, type_id):
        """Tek bir izometrik blok çizer"""
        
        # İzometrik Projeksiyon Formülü
        # Screen X = (x - z) * width
        # Screen Y = (x + z) * height - (y * y_step)
        
        sx = cx + (x - z) * self.block_width
        sy = cy + (x + z) * self.block_height - (y * self.y_step)
        
        colors = self.get_shaded_colors(type_id)
        
        # Köşe Noktaları (Blok Merkezi sx, sy olsun - alt orta nokta)
        # Aslında sx, sy bloğun taban merkezi olsun.
        
        mw = self.block_width
        mh = self.block_height
        h = self.y_step # Yükseklik
        
        # Koordinatlar (Merkeze göre)
        #       Top
        #   L       R
        #     Bottom
        
        # ÜST YÜZEY (Baklava)
        # p1: Üst (sx, sy - h - mh*2) -> Biraz karışık, basit düşünelim.
        # sy noktası bloğun en alt noktası olsun.
        
        # Taban Noktaları
        b_bottom = (sx, sy)
        b_right  = (sx + mw, sy - mh)
        b_top    = (sx, sy - 2*mh)
        b_left   = (sx - mw, sy - mh)
        
        # Tavan Noktaları (Yüksekliğe göre yukarı kaydır)
        # Y ekseni ekranda yukarı (-) yönündedir.
        # Blok yüksekliği kadar yukarı (negatif y)
        
        # Dikkat: Parametre 'y' zaten 'sy' hesabında kullanıldı.
        # Burada sadece tek bir bloğun yüksekliğini (kalınlığını) çiziyoruz.
        # Gerçekten küp olması için bir kalınlık (thickness) belirleyelim.
        thickness = 25 # Blok kalınlığı piksel
        
        # Alt yüzey (Zemin) çizmeye gerek yok, görünmez.
        
        # Tavanın Merkezi
        ty = sy - thickness
        
        t_bottom = (sx, ty)
        t_right  = (sx + mw, ty - mh)
        t_top    = (sx, ty - 2*mh)
        t_left   = (sx - mw, ty - mh)
        
        # 1. SOL YÜZEY (Left Face)
        # Points: b_bottom, b_left, t_left, t_bottom
        self.canvas.create_polygon(
            b_bottom[0], b_bottom[1],
            b_left[0], b_left[1],
            t_left[0], t_left[1],
            t_bottom[0], t_bottom[1],
            fill=colors['left'], outline="black", width=1
        )
        
        # 2. SAĞ YÜZEY (Right Face)
        # Points: b_bottom, b_right, t_right, t_bottom
        self.canvas.create_polygon(
            b_bottom[0], b_bottom[1],
            b_right[0], b_right[1],
            t_right[0], t_right[1],
            t_bottom[0], t_bottom[1],
            fill=colors['right'], outline="black", width=1
        )
        
        # 3. ÜST YÜZEY (Top Face)
        # Points: t_bottom, t_right, t_top, t_left
        self.canvas.create_polygon(
            t_bottom[0], t_bottom[1],
            t_right[0], t_right[1],
            t_top[0], t_top[1],
            t_left[0], t_left[1],
            fill=colors['top'], outline="black", width=1
        )
        
        # Koordinat Text (Debug için)
        # self.canvas.create_text(sx, ty-mh, text=f"{y}", font=("Arial", 8), fill="white")


    def on_drag_start(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def on_drag(self, event):
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        self.offset_x += dx
        self.offset_y += dy
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self.draw_world()

    def move_camera(self, dx, dy):
        self.offset_x += dx
        self.offset_y += dy
        self.draw_world()

