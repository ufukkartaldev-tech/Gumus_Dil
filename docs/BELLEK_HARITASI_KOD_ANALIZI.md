# 🧠 Gümüşdil Bellek Haritası Kodu

## 📍 **Konum:** `src/ide/ui/memory_view.py`

## 🎯 **Bellek Haritası Özellikleri**

### **🏗️ Ana Sınıflar:**

#### **1. MemoryCell - Bellek Hücresi**
```python
class MemoryCell(ctk.CTkFrame):
    """Bellek hücresi - Adres, değer, tip ve animasyon"""
    
    def __init__(self, parent, address, value, v_type, color, theme, data_json=None):
        # 🎨 Görsel özellikler:
        - Adres çipi (hash-based renk)
        - Type ikonları (🔢📝🛒☯️🗺️ƒ📦🚫)
        - Hover etkileri (border büyüme)
        - Leak detection (kırmızı uyarı)
        - Death animasyonu (parçalanarak kaybolma)
```

#### **2. MemoryView - Ana Bellek Arayüzü**
```python
class MemoryView(ctk.CTkFrame):
    """Bellek yönetimi ve görselleştirme"""
    
    def __init__(self, parent, config, on_jump=None, on_ask_ai=None):
        # 🎮 Zaman makinesi kontrolleri:
        - Play/Pause/Durdur/İleri/Geri
        - Snapshot yükle/kaydet
        - AI analiz butonu
        
        # 📊 Performans metrikleri:
        - CPU ve Memory barları
        - Nesne sayısı
        - Big-O karmaşıklığı grafiği
        - Layout modu (linear/tree)
```

### **🎨 Görselleştirme Özellikleri:**

#### **1. 🧠 Matriks Estetiği**
```python
def address_to_color(addr):
    """Adrese göre pastel renk üretimi"""
    h = hash(addr)
    r = (h & 0xFF0000) >> 16
    g = (h & 0x00FF00) >> 8
    b = h & 0x0000FF
    # Renkleri yumuşat (pastel)
    r = (r + 255) // 2
    g = (g + 255) // 2
    b = (b + 255) // 2
    return f"#{r:02x}{g:02x}{b:02x}"
```

#### **2. 🎭 Type İkonları**
```python
icon_map = {
    "int": "🔢", "float": "🔢", "string": "📝", 
    "list": "🛒", "bool": "☯️",
    "map": "🗺️", "func": "ƒ", 
    "class": "📦", "null": "🚫"
}
```

#### **3. 🏰 OOP Nesne Görselleştirme**
```python
def _render_class_instance(self, data):
    """Sınıf nesnesini görselleştir"""
    - Sınıf başlığı (miras badge)
    - Members (özellikler ve metotlar)
    - Virtual method vtable gösterimi
    - Method çağrı butonları
```

#### **4. 📊 Heap Görselleştirme**
```python
def _display_heap(self, data, prev):
    """Heap belleğini görselleştir"""
    - Canvas üzerinde 2D layout
    - Pointer okları (referans gösterimi)
    - Renk kodlaması (tipe göre)
    - Scrollable alan
```

#### **5. ⏰ Zaman Makinesi**
```python
def update_memory(self, memory_json):
    """Zaman makinesi güncelleme"""
    - History management (step-by-step)
    - Play/Pause kontrolleri
    - Slider ile zaman atlama
    - Snapshot save/load
```

## 🎮 **Kullanım Örnekleri**

### **IDE Entegrasyonu:**
```python
# main_window.py'de ekle
from .memory_view import MemoryView

# Sidebar'a ekle
self.memory_panel = MemoryView(left_pane, self.config, 
                              on_jump=self.jump_to_line,
                              on_ask_ai=self.ask_ai_suggestion)
```

### **JSON Veri Formatı:**
```json
{
    "step": 0,
    "line": 42,
    "env": {
        "scope": "Global",
        "variables": {
            "x": {"type": "integer", "value": 42},
            "name": {"type": "string", "value": "merhaba"}
        }
    },
    "heap": [
        {
            "address": "0x1000",
            "type": "integer", 
            "value": 42
        }
    ]
}
```

## 🔧 **Özelleştirme Seçenekleri**

### **🎨 Tema Desteği:**
```python
# Theme-based renkler
self.current_theme = self.config.THEMES[self.config.theme]

# Renk paleti
COLORS = {
    'brick_brown': '#8B4513',      # Tuğla
    'machine_gold': '#FFD700',        # Makine
    'steel_blue': '#4682B4',         # Çelik
    'forest_green': '#228B22',       # Orman
}
```

### **🔧 Callback Fonksiyonları:**
```python
# Jump to editor line
on_jump=lambda line_num: editor.goto_line(line_num)

# AI suggestion
on_ask_ai=lambda query: ai_analyze_memory(query)

# Memory update
on_memory_update=lambda data: memory_view.update_memory(data)
```

## 🚀 **Performans Özellikleri**

### **📊 Metrikler:**
- **Object count**: Aktif nesne sayısı
- **Memory usage**: Bellek kullanım yüzdesi
- **CPU usage**: İşlemci kullanımı (simüle)
- **Big-O analysis**: Algoritma karmaşıklığı
- **Leak detection**: Memory leak tespiti

### **🎮 Animasyonlar:**
- **Birth**: Yeni nesne doğumu (parlama efekti)
- **Death**: Nesne silinimi (kırık parçalanma)
- **Leak**: Memory leak alarmı (kırmızı uyarı)
- **Flash**: Değer değişimi (renk değişimi)

## 📋 **Entegrasyon Noktaları**

### **1. 📡 JSON Parser:**
```cpp
// C++ tarafından gönderilen JSON
std::cout << "__MEMORY_JSON_START__" << std::endl;
std::cout << environment->toJson() << std::endl;
std::cout << "__MEMORY_JSON_END__" << std::endl;
```

### **2. 🖥️ Terminal Komutları:**
```gumus
// Bellek dump'ı tetikle
__mimari__: liste           # Mevcut nesneleri listele
__mimari__: sıfırla        # Belleği temizle
__mimari__: izle <adres>     # Belirli adrese git
```

### **3. 🎨 IDE Event Binding:**
```python
# Compiler output parsing
if "__MEMORY_JSON_START__" in line:
    self.is_collecting_memory = True
    self.memory_buffer.append(line)
elif "__MEMORY_JSON_END__" in line:
    json_str = "".join(self.memory_buffer)
    self.sidebar.memory_panel.update_memory(json_str)
```

## 🎯 **Kullanım Senaryoları**

### **1. 🐛 Debug Modu:**
```gumus
// Debug flag ile bellek dump'ı aktif et
gumus.exe --debug program.gumus

// JSON çıktısı al
{
    "step": 1,
    "line": 15,
    "env": {...}
}
```

### **2. 📊 Bellek Analizi:**
```python
# Memory leak tespiti
if cell.is_leaking:
    cell.leak_alarm()

# Object lifecycle takibi
cell.birth()    # Yeni nesne
cell.die()      # Nesne silindi
```

### **3. 🎮 Etkileşimli Keşif:**
```python
# Sağ tık menü
menu.add_command(label="📋 Adresi Kopyala", command=lambda: clipboard_append(cell.address))

# Watch listesi
cell.toggle_watch()  # İzleme modu
```

## 🏆 **Geliştirme Potansiyeli**

### **🔧 Eklenbilecek Özellikler:**
1. **Real-time GC visualization**: Garbage collector animasyonu
2. **Memory pool allocator**: Bellek havuzu gösterimi
3. **Thread safety**: Multi-threading desteği
4. **Export/Import**: Bellek durumunu kaydet/yükle
5. **Advanced analytics**: Detaylı performans raporları

**Bu bellek haritası kodu, Gümüşdil'in memory management'ini görselleştirir!** 🧠💎


