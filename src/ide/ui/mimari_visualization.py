# -*- coding: utf-8 -*-
"""
🏭 Gümüşdil mimari Görselleştirme - 3D Factory Simulation
Lexer, Parser, Interpreter'i fabrika ve şehir olarak görselleştirir
"""
import customtkinter as ctk
import tkinter as tk
import math
import random
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class Building3D:
    """3D bina nesnesi"""
    def __init__(self, building_type: str, x: int, y: int, z: int, color: str):
        self.type = building_type
        self.x, self.y, self.z = x, y, z
        self.color = color
        self.width = 60
        self.height = 80
        self.depth = 40
        self.animation_offset = random.random() * math.pi * 2
        self.production_rate = random.uniform(0.5, 2.0)
        
    def get_3d_points(self, camera_x: int, camera_y: int) -> List[Tuple[int, int]]:
        """İzometrik 3D projeksiyon"""
        # İzometrik dönüşüm
        iso_x = (self.x - self.y) * 0.866 + camera_x
        iso_y = (self.x + self.y) * 0.5 - self.z + camera_y
        
        return [
            (iso_x, iso_y),
            (iso_x + self.width, iso_y),
            (iso_x + self.width, iso_y - self.height),
            (iso_x, iso_y - self.height)
        ]

class FactorySimulation(ctk.CTkFrame):
    """🏭 Gümüşdil compiler süreçlerini fabrika olarak görselleştirir"""
    
    # 🎨 mimari renk paleti
    COLORS = {
        'factory_brick': '#8B4513',      # Tuğla kahvesi
        'machine_gold': '#FFD700',        # Makine altını
        'conveyor_gray': '#696969',       # Konveyör grisi
        'forest_green': '#228B22',       # Orman yeşili
        'steel_blue': '#4682B4',         # Çelik mavisi
        'safety_yellow': '#FFD700',       # Güvenlik sarısı
        'smoke_gray': '#808080',         # Duman grisi
        'window_light': '#FFFFE0',        # Pencere ışığı
    }
    
    def __init__(self, parent, config, **kwargs):
        super().__init__(parent, **kwargs)
        self.config = config
        
        # 🏭 Fabrika bileşenleri
        self.buildings = []
        self.conveyor_belts = []
        self.smoke_particles = []
        self.production_stats = {
            'tokens_produced': 0,
            'errors_detected': 0,
            'efficiency': 100.0,
            'uptime': 0
        }
        
        # 🎮 Kamera ve kontrol
        self.camera_x = 400
        self.camera_y = 100
        self.zoom = 1.0
        self.simulation_speed = 1.0
        self.is_running = True
        
        # 🕐 Animasyon zamanı
        self.animation_time = 0
        self.last_update = time.time()
        
        self.setup_ui()
        self.initialize_factory()
        
    def setup_ui(self):
        """UI kurulumu"""
        # Üst kontrol paneli
        self.control_panel = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.control_panel.pack(fill="x", padx=5, pady=5)
        
        # Başlık
        title_label = ctk.CTkLabel(
            self.control_panel, 
            text="🏭 GÜMÜŞDİL FABRİKA SİMÜLASYONU", 
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(side="left", padx=10)
        
        # Kontrol butonları
        self.play_pause_btn = ctk.CTkButton(
            self.control_panel, 
            text="⏸️ DURDUR", 
            width=100, 
            command=self.toggle_simulation
        )
        self.play_pause_btn.pack(side="right", padx=5)
        
        self.reset_btn = ctk.CTkButton(
            self.control_panel, 
            text="🔄 SIFIRLA", 
            width=100, 
            command=self.reset_simulation
        )
        self.reset_btn.pack(side="right", padx=5)
        
        # Hız kontrolü
        speed_frame = ctk.CTkFrame(self.control_panel, fg_color="transparent")
        speed_frame.pack(side="right", padx=20)
        
        ctk.CTkLabel(speed_frame, text="Hız:").pack(side="left")
        self.speed_slider = ctk.CTkSlider(
            speed_frame, 
            from_=0.1, 
            to=3.0, 
            number_of_steps=20,
            width=150
        )
        self.speed_slider.set(1.0)
        self.speed_slider.pack(side="left", padx=5)
        self.speed_slider.configure(command=self.update_speed)
        
        # Canvas
        theme = self.config.THEMES[self.config.theme]
        self.canvas = tk.Canvas(
            self, 
            bg=theme['bg'], 
            highlightthickness=0,
            width=1200, 
            height=600
        )
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # İstatistik paneli
        self.stats_panel = ctk.CTkFrame(self, height=80, fg_color="transparent")
        self.stats_panel.pack(fill="x", padx=5, pady=5)
        
        self.stats_label = ctk.CTkLabel(
            self.stats_panel,
            text="📊 Üretim: 0 | Hata: 0 | Verim: 100% | Çalışma: 0s",
            font=("Consolas", 11)
        )
        self.stats_label.pack(pady=10)
        
        # Canvas etkileşimleri
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", lambda e: self.zoom_in())  # Linux
        self.canvas.bind("<Button-5>", lambda e: self.zoom_out())  # Linux
        
    def initialize_factory(self):
        """Fabrika bileşenlerini oluştur"""
        # 🏭 LEXER FABRİKASI
        lexer_factory = Building3D(
            "lexer_factory", 
            100, 100, 0, 
            self.COLORS['factory_brick']
        )
        self.buildings.append(lexer_factory)
        
        # 🏗️ PARSER ATÖLYESİ
        parser_workshop = Building3D(
            "parser_workshop",
            300, 100, 0,
            self.COLORS['steel_blue']
        )
        self.buildings.append(parser_workshop)
        
        # ⚙️ INTERPRETER MOTORU
        interpreter_engine = Building3D(
            "interpreter_engine",
            500, 100, 0,
            self.COLORS['forest_green']
        )
        self.buildings.append(interpreter_engine)
        
        # 🏭 DEPO BİNALARI
        for i in range(3):
            warehouse = Building3D(
                "warehouse",
                200 + i * 150, 250, 0,
                self.COLORS['conveyor_gray']
            )
            self.buildings.append(warehouse)
        
        # 🛣️ KONVEYÖR HATLARI
        self.conveyor_belts = [
            {'start': (160, 140), 'end': (300, 140), 'speed': 2.0},
            {'start': (360, 140), 'end': (500, 140), 'speed': 2.0},
            {'start': (560, 140), 'end': (200, 250), 'speed': 1.5},
            {'start': (350, 250), 'end': (500, 250), 'speed': 1.5},
            {'start': (560, 250), 'end': (650, 250), 'speed': 1.0},
        ]
        
    def render_scene(self):
        """3D sahneyi çiz"""
        self.canvas.delete("all")
        
        # 🌅 Zemin çiz
        self.draw_ground()
        
        # 🛣️ Konveyör hatları
        for belt in self.conveyor_belts:
            self.draw_conveyor_belt(belt)
        
        # 🏭 Binaları çiz
        for building in self.buildings:
            self.draw_building(building)
        
        # 💨 Duman parçacıkları
        self.draw_smoke_particles()
        
        # 📊 İstatistikleri güncelle
        self.update_stats_display()
        
    def draw_ground(self):
        """Zemin çizimi"""
        # Izgaralı zemin
        for x in range(0, 1200, 40):
            for y in range(0, 600, 40):
                # İzometrik dönüşüm
                iso_x = (x - y) * 0.866 + self.camera_x
                iso_y = (x + y) * 0.5 + self.camera_y
                
                color = "#2a2a2a" if (x // 40 + y // 40) % 2 == 0 else "#333333"
                self.canvas.create_rectangle(
                    iso_x, iso_y, iso_x + 40, iso_y + 20,
                    fill=color, outline=""
                )
    
    def draw_building(self, building: Building3D):
        """3D bina çizimi"""
        points = building.get_3d_points(self.camera_x, self.camera_y)
        
        # Bina gövdesi
        self.canvas.create_polygon(
            points, 
            fill=building.color, 
            outline="#000000", 
            width=2
        )
        
        # Çatı
        roof_points = [
            points[0],
            points[1],
            (points[2][0], points[2][1] - 20),
            (points[3][0], points[3][1] - 20)
        ]
        self.canvas.create_polygon(
            roof_points,
            fill=self.adjust_brightness(building.color, 1.2),
            outline="#000000",
            width=2
        )
        
        # Pencereler (ışıklandırma)
        if building.type in ["lexer_factory", "parser_workshop", "interpreter_engine"]:
            window_x = points[0][0] + building.width // 2 - 10
            window_y = points[0][1] - building.height // 2
            self.canvas.create_rectangle(
                window_x, window_y, window_x + 20, window_y + 15,
                fill=self.COLORS['window_light'],
                outline="#000000"
            )
        
        # Bina etiketi
        label_x = points[0][0] + building.width // 2
        label_y = points[0][1] + 10
        
        type_names = {
            "lexer_factory": "🏭 LEXER",
            "parser_workshop": "🏗️ PARSER", 
            "interpreter_engine": "⚙️ INTERPRETER",
            "warehouse": "🏪 DEPO"
        }
        
        self.canvas.create_text(
            label_x, label_y,
            text=type_names.get(building.type, building.type.upper()),
            fill="white",
            font=("Segoe UI", 10, "bold"),
            anchor="center"
        )
        
    def draw_conveyor_belt(self, belt: Dict):
        """Konveyör hattı çizimi"""
        # İzometrik dönüşüm
        start_x = (belt['start'][0] - belt['start'][1]) * 0.866 + self.camera_x
        start_y = (belt['start'][0] + belt['start'][1]) * 0.5 + self.camera_y
        end_x = (belt['end'][0] - belt['end'][1]) * 0.866 + self.camera_x
        end_y = (belt['end'][0] + belt['end'][1]) * 0.5 + self.camera_y
        
        # Konveyör bandı
        self.canvas.create_line(
            start_x, start_y, end_x, end_y,
            fill=self.COLORS['conveyor_gray'],
            width=8,
            capstyle="round"
        )
        
        # Hareketli parçalar
        num_parts = 5
        for i in range(num_parts):
            t = (self.animation_time * belt['speed'] + i * 0.2) % 1.0
            part_x = start_x + (end_x - start_x) * t
            part_y = start_y + (end_y - start_y) * t
            
            self.canvas.create_oval(
                part_x - 4, part_y - 4, part_x + 4, part_y + 4,
                fill=self.COLORS['machine_gold'],
                outline="#000000"
            )
    
    def draw_smoke_particles(self):
        """Duman parçacıkları çizimi"""
        for particle in self.smoke_particles[:]:
            # İzometrik dönüşüm
            iso_x = (particle['x'] - particle['y']) * 0.866 + self.camera_x
            iso_y = (particle['x'] + particle['y']) * 0.5 - particle['z'] + self.camera_y
            
            # Duman halkası
            size = particle['size'] * self.zoom
            alpha = max(0, 1 - particle['age'] / 100)
            color = self.adjust_alpha(self.COLORS['smoke_gray'], alpha)
            
            self.canvas.create_oval(
                iso_x - size, iso_y - size,
                iso_x + size, iso_y + size,
                fill=color, outline=""
            )
            
            # Parçacığı güncelle
            particle['z'] += 0.5
            particle['age'] += 1
            particle['size'] += 0.1
        
        # Eski parçacıkları temizle
        self.smoke_particles = [p for p in self.smoke_particles if p['age'] < 100]
    
    def update_simulation(self):
        """Simülasyon güncelleme"""
        if not self.is_running:
            return
        
        current_time = time.time()
        dt = (current_time - self.last_update) * self.simulation_speed
        self.last_update = current_time
        self.animation_time += dt
        
        # 🏭 Üretim simülasyonu
        self.simulate_production()
        
        # 💨 Duman üretimi
        if random.random() < 0.1:  # %10 ihtimalle duman
            self.add_smoke_particle()
        
        # 📊 İstatistik güncelleme
        self.production_stats['uptime'] += dt
        
        # Sahneyi yeniden çiz
        self.render_scene()
        
        # Sonraki frame
        self.after(50, self.update_simulation)  # 20 FPS
    
    def simulate_production(self):
        """Üretim sürecini simüle et"""
        for building in self.buildings:
            if building.type in ["lexer_factory", "parser_workshop", "interpreter_engine"]:
                # Rastgele üretim
                if random.random() < 0.05 * building.production_rate:  # %5 ihtimal
                    self.production_stats['tokens_produced'] += 1
                    
                    # Verimlilik hesabı
                    if random.random() < 0.02:  # %2 hata ihtimali
                        self.production_stats['errors_detected'] += 1
                        self.production_stats['efficiency'] = max(0, self.production_stats['efficiency'] - 0.1)
                    else:
                        self.production_stats['efficiency'] = min(100, self.production_stats['efficiency'] + 0.05)
    
    def add_smoke_particle(self):
        """Duman parçacığı ekle"""
        if self.buildings:
            # İlk binanın üzerine duman
            building = self.buildings[0]
            particle = {
                'x': building.x + building.width // 2,
                'y': building.y + building.height // 2,
                'z': building.height,
                'size': random.uniform(3, 8),
                'age': 0
            }
            self.smoke_particles.append(particle)
    
    def update_stats_display(self):
        """İstatistik görüntüsünü güncelle"""
        stats = self.production_stats
        text = f"📊 Üretim: {stats['tokens_produced']} | Hata: {stats['errors_detected']} | Verim: {stats['efficiency']:.1f}% | Çalışma: {stats['uptime']:.1f}s"
        self.stats_label.configure(text=text)
    
    # 🎮 Kontrol fonksiyonları
    def toggle_simulation(self):
        """Simülasyonu başlat/durdur"""
        self.is_running = not self.is_running
        if self.is_running:
            self.play_pause_btn.configure(text="⏸️ DURDUR")
            self.last_update = time.time()
            self.update_simulation()
        else:
            self.play_pause_btn.configure(text="▶️ BAŞLAT")
    
    def reset_simulation(self):
        """Simülasyonu sıfırla"""
        self.production_stats = {
            'tokens_produced': 0,
            'errors_detected': 0,
            'efficiency': 100.0,
            'uptime': 0
        }
        self.smoke_particles.clear()
        self.animation_time = 0
        self.render_scene()
    
    def update_speed(self, value):
        """Simülasyon hızını güncelle"""
        self.simulation_speed = float(value)
    
    def on_drag_start(self, event):
        """Sürükleme başlangıcı"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def on_drag(self, event):
        """Sürükleme"""
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        self.camera_x += dx
        self.camera_y += dy
        
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        self.render_scene()
    
    def on_zoom(self, event):
        """Zoom işlemi"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def zoom_in(self):
        """Yakınlaştır"""
        self.zoom = min(3.0, self.zoom * 1.1)
        self.render_scene()
    
    def zoom_out(self):
        """Uzaklaştır"""
        self.zoom = max(0.3, self.zoom / 1.1)
        self.render_scene()
    
    # 🎨 Yardımcı fonksiyonlar
    def adjust_brightness(self, color: str, factor: float) -> str:
        """Renk parlaklığını ayarla"""
        # Hex'den RGB'ye çevir
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        
        # Parlaklığı ayarla
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def adjust_alpha(self, color: str, alpha: float) -> str:
        """Renk şeffaflığını ayarla"""
        # Basit alpha karıştırma (arka plan siyah)
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        
        r = int(r * alpha)
        g = int(g * alpha)
        b = int(b * alpha)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def process_command(self, cmd: str):
        """mimari komutlarını işle"""
        cmd = cmd.strip().lower()
        
        if cmd == "hızlandır":
            self.simulation_speed = min(3.0, self.simulation_speed + 0.5)
            self.speed_slider.set(self.simulation_speed)
            
        elif cmd == "yavaşlat":
            self.simulation_speed = max(0.1, self.simulation_speed - 0.5)
            self.speed_slider.set(self.simulation_speed)
            
        elif cmd == "sıfırla":
            self.reset_simulation()
            
        elif cmd == "dur":
            self.is_running = False
            self.play_pause_btn.configure(text="▶️ BAŞLAT")
            
        elif cmd == "başlat":
            self.is_running = True
            self.play_pause_btn.configure(text="⏸️ DURDUR")
            self.last_update = time.time()
            self.update_simulation()
            
        elif cmd.startswith("bina ekle "):
            # Yeni bina ekle
            building_type = cmd[11:].strip()
            if building_type in ["lexer_factory", "parser_workshop", "interpreter_engine", "warehouse"]:
                x = random.randint(100, 600)
                y = random.randint(100, 300)
                color = random.choice(list(self.COLORS.values()))
                building = Building3D(building_type, x, y, 0, color)
                self.buildings.append(building)
                
        elif cmd == "liste":
            # Bina listesi
            building_count = {}
            for building in self.buildings:
                building_count[building.type] = building_count.get(building.type, 0) + 1
            
            print(f"\n🏭 Fabrika Durumu:")
            for btype, count in building_count.items():
                print(f"  {btype}: {count} adet")
                
        else:
            print(f"Bilinmeyen komut: {cmd}")
            print("Kullanılabilir komutlar: hızlandır, yavaşlat, sıfırla, dur, başlat, bina ekle <tip>, liste")


