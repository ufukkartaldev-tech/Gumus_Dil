# -*- coding: utf-8 -*-
"""
GümüşAST Görselleştirme Ünitesi
Reingold-Tilford algoritması ile dinamik ağaç çizimi
"""
import customtkinter as ctk
import tkinter as tk
import json
from typing import Dict, List, Tuple, Optional

class ASTNode:
    """AST Düğüm Yapısı"""
    def __init__(self, data: dict):
        self.type = data.get('type', 'Unknown')
        self.value = data.get('value', '')
        self.children = [ASTNode(child) for child in data.get('children', [])]
        self.line = data.get('line', 0)
        
        # Koordinat bilgileri (hesaplanacak)
        self.x = 0
        self.y = 0
        self.mod = 0  # Reingold-Tilford modifier

class ASTViewer(ctk.CTkToplevel):
    """AST Görselleştirme Penceresi"""
    
    # Çizim Sabitleri (Stratejik Konumlandırma)
    NODE_WIDTH = 120
    NODE_HEIGHT = 40
    LEVEL_HEIGHT = 80  # Y ekseni derinlik
    SIBLING_DISTANCE = 30  # Kardeş düğümler arası mesafe
    SUBTREE_DISTANCE = 50  # Alt ağaçlar arası mesafe
    
    # Renk Paleti (Gümüş Teması)
    COLORS = {
        'Program': '#569cd6',      # Mavi
        'FunctionDecl': '#4ec9b0', # Turkuaz
        'VariableDecl': '#9cdcfe', # Açık Mavi
        'Assignment': '#ce9178',   # Turuncu
        'BinaryOp': '#dcdcaa',     # Sarı
        'IfStmt': '#c586c0',       # Mor
        'WhileStmt': '#c586c0',    # Mor
        'Literal': '#b5cea8',      # Yeşil
        'Identifier': '#9cdcfe',   # Açık Mavi
        'default': '#808080'       # Gri
    }
    
    def __init__(self, parent, ast_json: str, config):
        super().__init__(parent)
        self.config = config
        self.title("🌳 GümüşAST - Ağaç Görselleştirme")
        
        # Ekran boyutuna göre dinamik boyutlandırma
        screen_w = parent.winfo_screenwidth()
        screen_h = parent.winfo_screenheight()
        w = min(1200, int(screen_w * 0.8))
        h = min(800, int(screen_h * 0.8))
        
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(800, 600)
        
        # Zoom ve Pan değişkenleri
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.drag_start = None
        self.highlighted_line = -1
        self.highlighted_nodes = [] # Hali hazırda parlayan düğümler (glow effect için)
        
        # AST Verisi
        try:
            ast_data = json.loads(ast_json)
            
            # Eğer liste ise, Program düğümü oluştur
            if isinstance(ast_data, list):
                ast_data = {
                    "type": "Program",
                    "line": 0,
                    "value": "",
                    "children": ast_data
                }
            
            self.root_node = ASTNode(ast_data)
            
        except json.JSONDecodeError as e:
            self.root_node = None
            self.show_error(f"JSON Parse Hatası: {e}")
            return
        except Exception as e:
            self.root_node = None
            self.show_error(f"AST Oluşturma Hatası: {e}")
            return
        
        self.setup_ui()
        
        # Canvas hazır olana kadar bekle
        self.after(100, self.draw_tree)
    
    def setup_ui(self):
        """Arayüz Kurulumu"""
        # Tema renklerini al
        theme = self.config.THEMES[self.config.theme]
        
        # Toolbar
        toolbar = ctk.CTkFrame(self, height=40, fg_color=theme['sidebar_bg'])
        toolbar.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(toolbar, text="🌳 GümüşAST Görselleştirme", 
                    font=('Segoe UI', 16, 'bold'),
                    text_color=theme['accent']).pack(side="left", padx=10)
        
        ctk.CTkButton(toolbar, text="Sıfırla", width=80,
                     command=self.reset_view,
                     fg_color=theme['accent'],
                     hover_color=theme['select_bg']).pack(side="right", padx=5)
        
        ctk.CTkButton(toolbar, text="Yakınlaştır (+)", width=120,
                     command=self.zoom_in,
                     fg_color=theme['accent'],
                     hover_color=theme['select_bg']).pack(side="right", padx=5)
        
        ctk.CTkButton(toolbar, text="Uzaklaştır (-)", width=120,
                     command=self.zoom_out,
                     fg_color=theme['accent'],
                     hover_color=theme['select_bg']).pack(side="right", padx=5)
        
        # Canvas (Çizim Alanı) - Tema rengini kullan
        self.canvas = tk.Canvas(self, bg=theme['editor_bg'], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Event Bindings
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
    
    def show_error(self, message: str):
        """Hata Mesajı Göster"""
        theme = self.config.THEMES[self.config.theme]
        
        error_frame = ctk.CTkFrame(self, fg_color=theme['bg'])
        error_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        label = ctk.CTkLabel(
            error_frame, 
            text=f"❌ {message}", 
            text_color="#ff6b6b",
            font=('Segoe UI', 14, 'bold'),
            wraplength=600
        )
        label.pack(expand=True, pady=20)
        
        close_btn = ctk.CTkButton(
            error_frame,
            text="Kapat",
            command=self.destroy,
            fg_color=theme['accent'],
            hover_color=theme['select_bg'],
            width=120,
            height=35
        )
        close_btn.pack(pady=10)
    
    def calculate_positions(self):
        """Koordinat Hesaplama (Reingold-Tilford Algoritması)"""
        if not self.root_node:
            return
        
        # İlk geçiş: Alt ağaçları konumlandır
        self._first_walk(self.root_node, 0)
        
        # İkinci geçiş: Mutlak koordinatları hesapla
        canvas_width = self.canvas.winfo_width() or 1200
        start_x = canvas_width / 2
        self._second_walk(self.root_node, 0, start_x, 0)
    
    def _first_walk(self, node: ASTNode, level: int):
        """Reingold-Tilford İlk Geçiş"""
        node.y = level
        
        if not node.children:
            # Yaprak düğüm
            node.x = 0
            return
        
        # Çocukları işle
        for child in node.children:
            self._first_walk(child, level + 1)
        
        # Bu düğümü çocuklarının ortasına yerleştir
        if len(node.children) == 1:
            node.x = node.children[0].x
        else:
            left_child = node.children[0]
            right_child = node.children[-1]
            node.x = (left_child.x + right_child.x) / 2
    
    def _second_walk(self, node: ASTNode, level: int, x: float, mod: float):
        """Reingold-Tilford İkinci Geçiş - Mutlak Koordinatlar"""
        node.x = x + mod
        node.y = level * self.LEVEL_HEIGHT + 50
        
        # Çocukları işle
        child_mod = mod
        for i, child in enumerate(node.children):
            child_x = node.x + (i - len(node.children)/2 + 0.5) * (self.NODE_WIDTH + self.SIBLING_DISTANCE)
            self._second_walk(child, level + 1, child_x, child_mod)
    
    def draw_tree(self):
        """Ağacı Çiz (Ana Çizim Motoru)"""
        if not self.root_node:
            return
        
        self.canvas.delete("all")
        self.calculate_positions()
        
        # Önce bağlantıları çiz (arka planda kalsın)
        self._draw_edges(self.root_node)
        
        # Sonra düğümleri çiz (üstte görünsün)
        self._draw_nodes(self.root_node)
    
    def _draw_edges(self, node: ASTNode):
        """Bağlantı Çizgileri (Baba-Çocuk)"""
        theme = self.config.THEMES[self.config.theme]
        
        for child in node.children:
            # Koordinatları zoom ve pan ile ayarla
            x1 = node.x * self.zoom_level + self.pan_x
            y1 = (node.y + self.NODE_HEIGHT/2) * self.zoom_level + self.pan_y
            x2 = child.x * self.zoom_level + self.pan_x
            y2 = (child.y - self.NODE_HEIGHT/2) * self.zoom_level + self.pan_y
            
            # Tema rengini kullan
            self.canvas.create_line(x1, y1, x2, y2, 
                                   fill=theme.get('accent', '#4ec9b0'), 
                                   width=2, 
                                   smooth=True, tags="edge")
            
            # Özyinelemeli çocukları çiz
            self._draw_edges(child)
    
    def _draw_nodes(self, node: ASTNode):
        """Düğümleri Çiz (Kutu + Metin)"""
        theme = self.config.THEMES[self.config.theme]
        
        x = node.x * self.zoom_level + self.pan_x
        y = node.y * self.zoom_level + self.pan_y
        w = self.NODE_WIDTH * self.zoom_level
        h = self.NODE_HEIGHT * self.zoom_level
        
        # Renk seçimi - tema renklerini kullan
        type_colors = {
            'Program': theme.get('keyword', '#569cd6'),
            'FunctionStmt': theme.get('function', '#4ec9b0'),
            'VarStmt': theme.get('keyword', '#9cdcfe'),
            'ClassStmt': theme.get('class', '#4ec9b0'),
            'PrintStmt': theme.get('function', '#ce9178'),
            'IfStmt': theme.get('keyword', '#c586c0'),
            'WhileStmt': theme.get('keyword', '#c586c0'),
            'ForStmt': theme.get('keyword', '#c586c0'),
            'BinaryExpr': theme.get('number', '#dcdcaa'),
            'Literal': theme.get('number', '#b5cea8'),
            'Variable': theme.get('fg', '#9cdcfe'),
            'CallExpr': theme.get('function', '#dcdcaa'),
        }
        
        color = type_colors.get(node.type, theme.get('comment', '#808080'))
        is_highlighted = (node.line == self.highlighted_line)
        
        # Parlama Efekti (Glow Effect)
        if is_highlighted:
            # 3 katmanlı parlama
            for i in range(3, 0, -1):
                glow_w = w + (i * 8) * self.zoom_level
                glow_h = h + (i * 8) * self.zoom_level
                self.canvas.create_rectangle(
                    x - glow_w/2, y - glow_h/2, x + glow_w/2, y + glow_h/2,
                    fill="", 
                    outline=theme.get('accent', '#4ec9b0'), 
                    width=1,
                    tags="glow"
                )
        
        # Yuvarlatılmış köşeli kutu
        border_width = 4 if is_highlighted else 2
        outline_color = theme.get('accent', '#ffffff') if is_highlighted else theme.get('border', '#ffffff')
        
        self.canvas.create_rectangle(
            x - w/2, y - h/2, x + w/2, y + h/2,
            fill=color, 
            outline=outline_color, 
            width=border_width,
            tags=("node", f"node_{id(node)}")
        )
        
        # Düğüm tipi (üstte)
        self.canvas.create_text(
            x, y - h/4,
            text=node.type,
            fill=theme.get('bg', '#ffffff'),
            font=('Consolas', int(10 * self.zoom_level), 'bold'),
            tags="node"
        )
        
        # Değer (altta, varsa)
        if node.value:
            value_text = str(node.value)[:15]  # Uzun değerleri kısalt
            self.canvas.create_text(
                x, y + h/4,
                text=value_text,
                fill=theme.get('bg', '#ffffff'),
                font=('Consolas', int(8 * self.zoom_level)),
                tags="node"
            )
        
        # Özyinelemeli çocukları çiz
        for child in node.children:
            self._draw_nodes(child)
    
    # === Etkileşim Fonksiyonları ===
    
    def zoom_in(self):
        """Yakınlaştır"""
        self.zoom_level *= 1.2
        self.draw_tree()
    
    def zoom_out(self):
        """Uzaklaştır"""
        self.zoom_level /= 1.2
        self.draw_tree()
    
    def reset_view(self):
        """Görünümü Sıfırla"""
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.draw_tree()
    
    def on_mousewheel(self, event):
        """Fare Tekerleği ile Zoom"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def on_drag_start(self, event):
        """Sürükleme Başlangıcı"""
        self.drag_start = (event.x, event.y)
    
    def on_drag_motion(self, event):
        """Sürükleme Hareketi (Pan)"""
        if self.drag_start:
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.pan_x += dx
            self.pan_y += dy
            self.drag_start = (event.x, event.y)
            self.draw_tree()
    
    def on_drag_end(self, event):
        """Sürükleme Bitişi"""
        self.drag_start = None

    def highlight_line(self, line: int):
        """Dışarıdan çağrılan vurgulama metodu"""
        if self.highlighted_line == line:
            return
            
        self.highlighted_line = line
        self.draw_tree() # Tüm ağacı yeniden çiz (Şimdilik en güvenli yol)
        
        # Eğer varsa, vurgulanan düğüme odaklan (scroll/pan)
        # TODO: Otomatik odaklanma eklenebilir

