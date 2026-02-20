# 🌉 GÜMÜŞ BAĞLANTI - İKİ DÜNYANIN KÖPRÜSÜ
## C++ Motoru ↔️ Python IDE Entegrasyon Mimarisi

---

## 📡 BAĞLANTI KATMANLARı

### **Katman 1: Subprocess IPC (Inter-Process Communication)**

```
┌─────────────────┐         subprocess.Popen()         ┌──────────────────┐
│   Python IDE    │ ───────────────────────────────────▶│   C++ Motor      │
│  (main_window)  │                                      │   (gumus.exe)    │
└─────────────────┘                                      └──────────────────┘
         ▲                                                        │
         │                                                        │
         │          STDOUT/STDERR (Text Streams)                 │
         └────────────────────────────────────────────────────────┘
```

**Python Tarafı (compiler.py):**
```python
process = subprocess.Popen(
    [str(COMPILER_PATH), str(source_file)],
    stdin=subprocess.PIPE,    # ◀ Girdi kanalı
    stdout=subprocess.PIPE,   # ◀ Çıktı kanalı
    stderr=subprocess.PIPE,   # ◀ Hata kanalı
    text=True,
    encoding='utf-8',
    bufsize=0  # Unbuffered - Anında iletişim!
)
```

**C++ Tarafı (main.cpp):**
```cpp
int main(int argc, char* argv[]) {
    // Komut satırı argümanlarını parse et
    if (arg == "--dump-ast") {
        dumpAst = true;
    } else if (arg == "--dump-memory") {
        dumpMemory = true;
    }
    
    runFile(filename, dumpAst, dumpMemory);
}
```

---

### **Katman 2: Protokol Tanımları (Özel İşaretleyiciler)**

#### 2.1 **JSON Hata Protokolü**

**C++ → Python (Hata Bildirimi)**

```cpp
// json_hata.h
void JsonHata(const std::string& type, const std::string& message, 
              int line, const std::string& file, const std::string& suggestion) {
    std::cerr << "{\"type\": \"" << JsonEscape(type) << "\", \"line\": " << line
              << ", \"message\": \"" << JsonEscape(message) << "\"";
    if (!suggestion.empty()) {
        std::cerr << ", \"suggestion\": \"" << JsonEscape(suggestion) << "\"";
    }
    std::cerr << "}\n";
}
```

**Python Tarafında Parse:**
```python
# terminal.py - write_smart_error()
try:
    error_obj = json.loads(line)
    if error_obj.get("suggestion"):
        # AI'ya gönder: Otomatik düzeltme öner
        self.ai_panel.suggest_fix(error_obj)
except:
    # Normal metin olarak göster
    self.write_text(line)
```

---

#### 2.2 **Hafıza Dump Protokolü**

**C++ → Python (Memory Snapshot)**

```cpp
// main.cpp - run()
if (dumpMemory) {
    std::cout << "\n__MEMORY_JSON_START__\n";
    std::cout << interpreter.environment->toJson();
    std::cout << "\n__MEMORY_JSON_END__\n";
}
```

**Python Tarafında Yakalama:**
```python
# main_window.py - _read_stream()
if "__MEMORY_JSON_START__" in line:
    self.is_collecting_memory = True
    self.memory_buffer = []
elif "__MEMORY_JSON_END__" in line:
    json_str = "".join(self.memory_buffer)
    # Memory View'a gönder
    self.sidebar.memory_panel.update_memory(json_str)
```

**Environment JSON Formatı (C++):**
```cpp
// environment.cpp
std::string Environment::toJson() const {
    std::ostringstream oss;
    oss << "{";
    oss << "\"variables\": {";
    for (const auto& [name, value] : values) {
        oss << "\"" << name << "\": {";
        oss << "\"value\": \"" << value.toString() << "\",";
        oss << "\"type\": \"" << value.typeString() << "\",";
        oss << "\"address\": \"" << std::hex << &value << "\"";
        oss << "},";
    }
    oss << "},";
    oss << "\"parent\": " << (enclosing ? enclosing->toJson() : "null");
    oss << "}";
    return oss.str();
}
```

---

#### 2.3 **AST Dump Protokolü**

**C++ → Python (Syntax Tree)**

```cpp
// main.cpp
if (dumpAst) {
    std::cout << "[";
    for (size_t i = 0; i < statements.size(); ++i) {
        std::cout << statements[i]->toJson();
        if (i < statements.size() - 1) std::cout << ", ";
    }
    std::cout << "]\n";
    return;  // Sadece AST bas, çalıştırma!
}
```

**Python Tarafında Kullanım:**
```python
# compiler.py
def get_ast_json(source_file):
    res = subprocess.run(
        [str(COMPILER_PATH), "--dump-ast", str(source_file)],
        capture_output=True
    )
    return json.loads(res.stdout)

# main_window.py - AST Viewer
ast_data = CompilerRunner.get_ast_json(file_path)
self.ast_viewer.render_tree(ast_data)
```

---

#### 2.4 **Özel Komut Protokolleri**

**Canvas Komutları:**
```cpp
// C++ Native Function
std::cout << "__CANVAS__:circle 100 100 50 #ff0000\n";
```

```python
# Python IDE
if "__CANVAS__:" in line:
    cmd = line.split("__CANVAS__:")[1].strip()
    self.canvas_panel.process_command(cmd)
```

**Voxel Engine:**
```cpp
std::cout << "__VOXEL__:spawn cube 5 0 5\n";
```

**Fabrika Simülasyonu:**
```cpp
std::cout << "__FABRIKA__:produce widget 100\n";
```

---

### **Katman 3: Fallback Mekanizması (Simülatör)**

```python
# compiler.py
@staticmethod
def is_compiler_viable():
    """C++ derleyici çalışıyor mu?"""
    try:
        res = subprocess.run([COMPILER_PATH, "--help"], timeout=2)
        return res.returncode != DLL_NOT_FOUND_ERROR
    except:
        return False

@staticmethod
def start_interactive(source_file):
    # FALLBACK: C++ yoksa Python simülatörü kullan
    if not CompilerRunner.is_compiler_viable():
        simulator_script = Path(__file__).parent / "run_simulator.py"
        process = subprocess.Popen(
            [sys.executable, str(simulator_script), str(source_file)],
            # ... (aynı pipe'lar)
        )
        return process
    
    # Normal: C++ motoru
    process = subprocess.Popen([COMPILER_PATH, source_file], ...)
    return process
```

---

## 🔄 TAM ÇALIŞMA AKIŞI

### **Senaryo 1: Normal Kod Çalıştırma**

```
1. Kullanıcı F5'e basar
   ↓
2. Python: Kodu temp dosyaya yazar
   ↓
3. Python: subprocess.Popen([gumus.exe, temp.tr])
   ↓
4. C++: Dosyayı okur, tokenize eder, parse eder
   ↓
5. C++: Resolver ile scope'ları çözer
   ↓
6. C++: Interpreter çalıştırır
   ↓
7. C++: stdout'a yazdır("Merhaba") → "Merhaba\n"
   ↓
8. Python: _read_stream() thread'i satırı yakalar
   ↓
9. Python: Terminal'e yazar (GUI)
   ↓
10. C++: Program biter, exit code döner
    ↓
11. Python: Toast bildirim gösterir
```

---

### **Senaryo 2: Hata Durumu**

```
1. Kod hatası: değişken x = 10 / 0
   ↓
2. C++: LoxRuntimeException fırlatır
   ↓
3. C++: JsonHata("runtime_error", "Sıfıra bölme", 1, "", "Bölen sıfır olamaz")
   ↓
4. C++: stderr'e JSON yazar
   ↓
5. Python: _read_stream(stderr, is_error=True)
   ↓
6. Python: terminal.write_smart_error(line)
   ↓
7. Python: JSON parse eder, suggestion varsa AI'ya gönderir
   ↓
8. AI Panel: "Bölen sıfır olamaz. Kontrol eklemek ister misin?"
   ↓
9. Kullanıcı: "Evet" → Kod otomatik düzeltilir
```

---

### **Senaryo 3: Hafıza Görselleştirme**

```
1. Kullanıcı: "Memory View" açar
   ↓
2. Python: subprocess.Popen([gumus.exe, --dump-memory, file.tr])
   ↓
3. C++: Her satır çalıştıktan sonra:
        std::cout << "__MEMORY_JSON_START__\n";
        std::cout << environment->toJson();
        std::cout << "__MEMORY_JSON_END__\n";
   ↓
4. Python: İşaretleyicileri yakalar, buffer'a toplar
   ↓
5. Python: memory_panel.update_memory(json_str)
   ↓
6. Memory View: Stack/Heap görselleştirir
   ↓
7. Animasyonlar: Yeni nesne → Yeşil parlama
                 Silinen → Kırmızı fade + fragmentasyon
```

---

## 🎯 PROTOKOL ÖZET TABLOSU

| Protokol | Yön | Format | Kullanım |
|----------|-----|--------|----------|
| **JSON Hata** | C++ → Python | `{"type":"...", "line":N, "message":"..."}` | Hata bildirimi + AI önerisi |
| **Memory Dump** | C++ → Python | `__MEMORY_JSON_START__\n{...}\n__MEMORY_JSON_END__` | Stack/Heap görselleştirme |
| **AST Dump** | C++ → Python | `[{...}, {...}]` (JSON array) | Syntax tree viewer |
| **Canvas** | C++ → Python | `__CANVAS__:command args` | Çizim komutları |
| **Voxel** | C++ → Python | `__VOXEL__:command args` | 3D oyun komutları |
| **Fabrika** | C++ → Python | `__FABRIKA__:command args` | Fabrika simülasyonu |
| **STDIN** | Python → C++ | Text stream | `girdi()` fonksiyonu |

---

## 🔧 THREADING MODELİ

```python
# main_window.py
def run_code_async(self):
    # Ana thread: Process başlat
    self.process = CompilerRunner.start_interactive(file)
    
    # Thread 1: STDOUT okuma
    t_out = threading.Thread(target=self._read_stream, 
                             args=(self.process.stdout, False))
    t_out.daemon = True
    t_out.start()
    
    # Thread 2: STDERR okuma
    t_err = threading.Thread(target=self._read_stream, 
                             args=(self.process.stderr, True))
    t_err.daemon = True
    t_err.start()
    
    # Thread 3: Process wait (blocking)
    self.process.wait()
    
    # Thread-safe UI güncelleme
    self.root.after(0, lambda: self.update_ui())
```

**Neden 3 Thread?**
1. **STDOUT Thread:** Çıktıları anında yakala (blocking read)
2. **STDERR Thread:** Hataları anında yakala (blocking read)
3. **Main Thread:** GUI responsive kalsın (non-blocking)

**Thread-Safe GUI Güncelleme:**
```python
# ❌ YANLIŞ (Thread'den direkt GUI güncelleme)
self.terminal.write_text(line)

# ✅ DOĞRU (Tkinter main loop'una queue'la)
self.root.after(0, lambda l=line: self.terminal.write_text(l))
```

---

## 🚀 PERFORMANS OPTİMİZASYONLARI

### 1. **Unbuffered I/O**
```python
bufsize=0  # Anında iletişim, gecikme yok
```

### 2. **Binary Mode + UTF-8**
```cpp
// BOM temizliği
if (content[0] == 0xEF && content[1] == 0xBB && content[2] == 0xBF) {
    content.erase(0, 3);
}
```

### 3. **Lazy Loading**
```python
# AST sadece istendiğinde yüklenir
if user_clicks_ast_viewer:
    ast_data = CompilerRunner.get_ast_json(file)
```

### 4. **Memory Snapshots**
```python
# Her frame'i kaydet, zaman makinesi yap
self.history.append(memory_json)
self.slider.configure(to=len(self.history) - 1)
```

---

## 🎓 SONUÇ

**GÜMÜŞ BAĞLANTI** üç temel prensip üzerine kurulu:

1. **📡 IPC (Subprocess):** Process-to-process iletişim
2. **📝 Protokoller:** Özel işaretleyiciler + JSON
3. **🔄 Fallback:** C++ yoksa Python simülatör

Bu sayede:
- ✅ C++ hızı + Python esnekliği
- ✅ Modüler mimari (bağımsız geliştirme)
- ✅ Zengin IDE özellikleri (Memory View, AST, AI)
- ✅ Graceful degradation (C++ yoksa simülatör)

**Ustalık Noktası:** İki dil arasında **sıfır kopya** (zero-copy) iletişim, **JSON streaming**, ve **thread-safe GUI** güncellemeleri!

---

© 2026 Ufuk Kartal - GümüşDil Bağlantı Mimarisi

