import os
import threading
import tkinter as tk
import time
import json
from ..config import TEMP_DIR
from ..core.compiler import CompilerRunner

class CodeRunner:
    """Kod Yürütme ve Process Yönetimi (Thread-Safe)"""
    
    def __init__(self, main_window, config):
        self.main_window = main_window
        self.config = config
        self.process = None
        self.is_collecting_memory = False
        self.memory_buffer = []
        
        # UI Throttle
        self.last_ui_update_time = 0
        self.last_vars_update_time = 0
        self.ui_update_interval = 0.05 # 50ms

    def run_code(self):
        """Aktif editördeki kodu çalıştır"""
        editor = self.main_window.get_current_editor()
        if not editor: return
        
        # UI Temizliği
        editor.clear_errors() if hasattr(editor, 'clear_errors') else None
        self.main_window.terminal.clear()
        
        # Bellek Görünümünü Sıfırla (Sidebaer -> MemoryPanel)
        if hasattr(self.main_window, 'sidebar') and hasattr(self.main_window.sidebar, 'memory_panel'):
            mp = self.main_window.sidebar.memory_panel
            if hasattr(mp, 'reset'): mp.reset() # Varsa reset metodunu kullan
            else:
                 # Elle resetle
                 mp.history = []
                 mp.current_index = -1
                 mp.cells = {}
                 mp.canvas.delete("all")
        
        self.main_window.terminal.write_text(">>> Program Başlatılıyor...\n")
        self.main_window.terminal.prompt_label.configure(text=" GİRDİ > ")
        self.main_window.terminal.set_input_callback(self._send_input_to_process)
        
        # Geçici Dosyaya Yaz
        if not TEMP_DIR.exists(): os.makedirs(TEMP_DIR)
        run_file = TEMP_DIR / "temp_run.tr"
        
        try:
            with open(run_file, 'w', encoding='utf-8') as f:
                f.write(editor.get('1.0', tk.END))
        except Exception as e:
            self.main_window.terminal.write_text(f"Geçici dosya hatası: {e}\n")
            return
            
        # UI Güncelle (Butonları Kilitle)
        if hasattr(self.main_window, 'toolbar'):
            self.main_window.toolbar.set_run_state(True)
        elif hasattr(self.main_window, 'run_btn'): # Eski uyumluluk
            self.main_window.run_btn.configure(state="disabled", text="⏳ Çalışıyor...")
            self.main_window.stop_btn.configure(state="normal")
            
        # Thread Başlat
        t = threading.Thread(target=self._start_interactive_thread, args=(run_file,))
        t.daemon = True
        t.start()
        
    def stop_code(self):
        """Çalışan programı zorla durdur"""
        if self.process:
            try:
                self.process.kill()
                self.main_window.terminal.write_text("\n>>> Program kullanıcı tarafından durduruldu. 🛑\n")
            except: pass
            self.process = None
            
        # UI Güncelle
        if hasattr(self.main_window, 'toolbar'):
             self.main_window.toolbar.set_run_state(False)
        elif hasattr(self.main_window, 'run_btn'):
             self.main_window.run_btn.configure(state="normal", text="▶ ÇALIŞTIR (F5)")
             self.main_window.stop_btn.configure(state="disabled")

    def _start_interactive_thread(self, file_path):
        """Process'i başlatır ve I/O threadlerini yönetir"""
        try:
            self.process = CompilerRunner.start_with_memory(file_path)
            
            if not self.process:
                 self.main_window.root.after(0, lambda: self.main_window.terminal.write_text("❌ Kritik Hata: Process başlatılamadı!\n"))
                 self.stop_code() # UI Reset
                 return

            # STDOUT & STDERR Threadleri
            t_out = threading.Thread(target=self._read_stream, args=(self.process.stdout, False))
            t_out.daemon = True
            t_out.start()
            
            t_err = threading.Thread(target=self._read_stream, args=(self.process.stderr, True))
            t_err.daemon = True
            t_err.start()
            
            # Bekle
            self.process.wait()
            ret_code = self.process.returncode
            self.process = None
            
            # Bitiş İşlemleri
            self.main_window.root.after(0, lambda: self._on_process_finish(ret_code))
            
        except Exception as e:
            self.main_window.root.after(0, lambda: self.main_window.terminal.write_text(f"Çalıştırma Hatası: {e}\n"))
            self.main_window.root.after(0, lambda: self.stop_code())
            
    def _read_stream(self, stream, is_error):
        """Stream okuma ve parsing (Log, Memory, Profile, Trace)"""
        try:
            for line in iter(stream.readline, ''):
                if not line: break
                
                # Parsing Logic (Bellek, Canvas, Trace, Vars, Profile...)
                # Bu kısım main_window'daki karmaşık if-else bloğunun aynısı
                self._parse_output_line(line, is_error)
                
        except: pass

    def _parse_output_line(self, line, is_error):
        """Gelen satırı analiz et ve ilgili UI bileşenine yönlendir"""
        mw = self.main_window
        
        # 1. Bellek Dökümü (JSON)
        if "__MEMORY_JSON_START__" in line:
            self.is_collecting_memory = True
            self.memory_buffer = []
            return
        elif "__MEMORY_JSON_END__" in line:
            self.is_collecting_memory = False
            json_str = "".join(self.memory_buffer)
            mw.root.after(0, lambda: mw.sidebar.memory_panel.update_memory(json_str) if hasattr(mw, 'sidebar') else None)
            return
        if self.is_collecting_memory:
            self.memory_buffer.append(line)
            return

        # 2. Canvas
        if "__CANVAS__:" in line:
            cmd = line.split("__CANVAS__:")[1].strip()
            mw.root.after(0, lambda: mw.canvas_panel.process_command(cmd) if hasattr(mw, 'canvas_panel') else None)
            return
            
        # 3. Trace (Satır Takibi)
        if "__TRACE__:" in line:
             try:
                 line_num = int(line.split("__TRACE__:")[1].strip())
                 editor = mw.get_current_editor()
                 if editor:
                     mw.root.after(0, lambda: editor.highlight_line(line_num))
             except: pass
             return

        # 4. Profiler (CPU/RAM)
        if "__PROFILE__:" in line:
            now = time.time()
            if now - self.last_ui_update_time > self.ui_update_interval:
                try:
                    prof_data = json.loads(line.split("__PROFILE__:")[1].strip())
                    status_text = f"CPU: {prof_data['cpu']}% | MEM: {prof_data['mem']}MB"
                    if hasattr(mw, 'status_bar'):
                         mw.root.after(0, lambda: mw.status_bar.radar_label.configure(text=status_text))
                    self.last_ui_update_time = now
                except: pass
            return

        # 5. Normal Çıktı
        if is_error:
             mw.root.after(0, lambda: mw.terminal.write_smart_error(line) if hasattr(mw.terminal, 'write_smart_error') else mw.terminal.write_text(line))
        else:
             mw.root.after(0, lambda: mw.terminal.write_text(line))

    def _on_process_finish(self, ret_code):
        """Program bittiğinde UI güncelle"""
        self.main_window.terminal.write_text(f"\n>>> Program Sonlandı (Kod: {ret_code}).\n")
        self.main_window.terminal.prompt_label.configure(text=" GÜMÜŞ > ")
        
        # Butonları eski haline getir
        if hasattr(self.main_window, 'toolbar'):
             self.main_window.toolbar.set_run_state(False)
        elif hasattr(self.main_window, 'run_btn'):
             self.main_window.run_btn.configure(state="normal", text="▶ ÇALIŞTIR (F5)")
             self.main_window.stop_btn.configure(state="disabled")
             
        # Toast
        if ret_code == 0:
            if hasattr(self.main_window, 'show_toast'): self.main_window.show_toast("Başarılı! 🚀", "success")
        else:
            if hasattr(self.main_window, 'show_toast'): self.main_window.show_toast("Hata ile Sonlandı.", "error")

    def _send_input_to_process(self, text):
        """Terminal girdisini process'e ilet"""
        if self.process and self.process.stdin:
            try:
                self.process.stdin.write(text + "\n")
                self.process.stdin.flush()
            except: pass

