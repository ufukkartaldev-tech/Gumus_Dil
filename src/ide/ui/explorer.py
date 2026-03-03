# -*- coding: utf-8 -*-
import customtkinter as ctk
from pathlib import Path
from tkinter import ttk, Menu, simpledialog, messagebox
import shutil
import os

class ExplorerTree(ctk.CTkFrame):
    def __init__(self, parent, config, on_file_select):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_file_select = on_file_select
        self.current_root = None
        self.nodes = {} # id -> path
        
        theme = self.config.THEMES[self.config.theme]
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("Sidebar.Treeview",
                        background=theme['sidebar_bg'],
                        foreground=theme['fg'],
                        fieldbackground=theme['sidebar_bg'],
                        borderwidth=0,
                        rowheight=26,
                        font=("Segoe UI", 11))
        style.map("Sidebar.Treeview", 
                  background=[('selected', theme['hover'])],
                  foreground=[('selected', theme['accent'])])
                  
        self.tree = ttk.Treeview(self, style="Sidebar.Treeview", show="tree", selectmode="browse")
        self.scrollbar = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)
        self.tree.bind("<<TreeviewOpen>>", self._on_tree_open)
        
    def load_root(self, path):
        self.current_root = Path(path)
        self.tree.delete(*self.tree.get_children())
        self.nodes.clear()
        self._insert_node("", self.current_root, is_root=True)

    def refresh(self):
        if self.current_root: self.load_root(self.current_root)

    def _insert_node(self, parent_id, path, is_root=False):
        text = path.name if not is_root else path.name.upper()
        if not text and is_root: # Sürücü kökü durumu (C:\ gibi)
            text = str(path)
            
        if path.is_dir():
            icon = "📂" 
            display_text = f"{icon} {text}"
        else:
            ext = path.suffix.lower()
            icons = {'.tr': '💎', '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨', '.json': '📋', '.md': '📝', '.txt': '📄'}
            icon = icons.get(ext, '📄')
            try:
                size = path.stat().st_size
                size_kb = f"{size/1024:.1f} KB"
            except:
                size_kb = ""
            display_text = f"{icon} {text}   [{size_kb}]"
        node_id = self.tree.insert(parent_id, "end", text=display_text, open=is_root)
        self.nodes[node_id] = path
        
        if path.is_dir():
            self.tree.insert(node_id, "end", text="yükleniyor...")
            if is_root: self._load_children(node_id)
                
    def _on_tree_open(self, event):
        node_id = self.tree.focus()
        if node_id: self._load_children(node_id)
        
    def _load_children(self, node_id):
        path = self.nodes.get(node_id)
        if not path or not path.is_dir(): return
        
        children = self.tree.get_children(node_id)
        if len(children) == 1 and self.tree.item(children[0], "text") == "yükleniyor...":
            self.tree.delete(children[0])
            try:
                items = list(path.iterdir())
                items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
                for item in items:
                    if item.name.startswith('.') or item.name == '__pycache__': continue
                    self._insert_node(node_id, item)
            except Exception as e:
                messagebox.showerror("Gezgin Hatası", f"Klasör okunamadı: {path}\n{e}")

    def _on_double_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if item:
            path = self.nodes.get(item)
            if path and path.is_file() and self.on_file_select:
                self.on_file_select(str(path))

    def reveal_file(self, file_path):
        """Dosyayı ağaç yapısında bul ve seç"""
        target_path = Path(file_path).resolve()
        
        # Eğer kök yoksa veya dosya kök dışında kalıyorsa, kökü otomatik ayarla
        if not self.current_root or not str(target_path).startswith(str(self.current_root)):
             self.load_root(target_path.parent)
             
        root_nodes = self.tree.get_children("")
        if not root_nodes: return
        node_id = root_nodes[0]
        
        try:
            relative = target_path.relative_to(self.current_root)
        except ValueError:
            return

        # Parçaları takip et
        parts = relative.parts
        for part in parts:
            self._load_children(node_id)
            self.tree.item(node_id, open=True)
            
            found = False
            for child_id in self.tree.get_children(node_id):
                child_path = self.nodes.get(child_id)
                if child_path and child_path.name == part:
                    node_id = child_id
                    found = True
                    break
            if not found: return
            
        self.tree.selection_set(node_id)
        self.tree.see(node_id)
        self.tree.focus(node_id)

    def _on_right_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if item:
            self.tree.selection_set(item)
            self.tree.focus(item)
        target_path = self.nodes.get(item) if item else self.current_root
        if not target_path: return
        
        menu = Menu(self, tearoff=0)
        menu.add_command(label="📄 Yeni Dosya", command=lambda: self._new_file(target_path))
        menu.add_command(label="📁 Yeni Klasör", command=lambda: self._new_folder(target_path))
        menu.add_separator()
        if target_path != self.current_root:
            menu.add_command(label="🖋️ Yeniden Adlandır", command=lambda: self._rename(target_path))
            menu.add_command(label="🗑️ Sil", command=lambda: self._delete(target_path))
            menu.add_separator()
            
        menu.add_command(label="💻 Burada Terminal Aç", command=lambda: self._open_in_terminal(target_path))
        menu.add_separator()
        menu.add_command(label="🔄 Yenile", command=self.refresh)
        
        menu.tk_popup(event.x_root, event.y_root)
        
    def _new_file(self, target_path):
        parent_dir = target_path if target_path.is_dir() else target_path.parent
        res = simpledialog.askstring("Yeni Dosya", "Dosya adı (.tr vs.):")
        if res:
            try:
                if not res.endswith('.tr') and '.' not in res: res += '.tr'
                (parent_dir / res).touch()
                self.refresh()
                if self.on_file_select: self.on_file_select(str(parent_dir / res))
            except Exception as e: messagebox.showerror("Hata", str(e))
                
    def _new_folder(self, target_path):
        parent_dir = target_path if target_path.is_dir() else target_path.parent
        res = simpledialog.askstring("Yeni Klasör", "Klasör adı:")
        if res:
            try:
                (parent_dir / res).mkdir()
                self.refresh()
            except Exception as e: messagebox.showerror("Hata", str(e))
                
    def _rename(self, target_path):
        res = simpledialog.askstring("Yeniden Adlandır", "Yeni ad:", initialvalue=target_path.name)
        if res and res != target_path.name:
            try:
                target_path.rename(target_path.parent / res)
                self.refresh()
            except Exception as e: messagebox.showerror("Hata", str(e))
                
    def _delete(self, target_path):
        if messagebox.askyesno("Silme Onayı", f"'{target_path.name}' silinecek. Emin misin?"):
            try:
                if target_path.is_dir(): shutil.rmtree(target_path)
                else: target_path.unlink()
                self.refresh()
            except Exception as e: messagebox.showerror("Hata", str(e))

    def _open_in_terminal(self, target_path):
        import subprocess
        parent_dir = target_path if target_path.is_dir() else target_path.parent
        try:
            if os.name == 'nt':
                subprocess.Popen(['cmd.exe', '/c', 'start', 'cmd.exe', '/K', f'cd /d {parent_dir}'])
            else:
                subprocess.Popen(['x-terminal-emulator', '--working-directory', str(parent_dir)])
        except Exception as e:
            messagebox.showerror("Hata", f"Terminal açılamadı:\n{e}")
