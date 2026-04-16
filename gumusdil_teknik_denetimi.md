# GümüşDil Teknik Denetim Raporu
**Tarih:** 16 Nisan 2026 | **Versiyon:** Post-Architecture Revolution

---

## 1. BELLEK DEVRİMİ: GumusObject + Mark-and-Sweep GC

### Ne Yapıldı
`shared_ptr<void>` tabanlı sahte nesne sistemi, `GumusObject` mirası ve `GarbageCollector::allocateObject<T>()` şablonuyla değiştirildi. Nesneler bağlantılı liste (`next` pointer) üzerinden takip ediliyor.

### Güçlü Yönler
- **`allocateObject<T>` şablonu doğru yazılmış.** `std::forward<Args>()` ile mükemmel yönlendirme (perfect forwarding) kullanılıyor. `new T(...)` sonrası nesneyi hemen `firstObject` zincirine eklemek, yarı oluşturulmuş nesnelerin kaybolmasını engelliyor. Tip güvenliği `static_cast` yerine şablon parametresiyle sağlanıyor — doğru yaklaşım.
- **Yıkıcı (`~GarbageCollector`) düzgün.** Tüm zinciri başından sonuna `delete` çağırarak temizliyor.
- **`GumusList::mark()` ve `GumusMap::mark()` doğru implemente edilmiş.**

### KRİTİK BELLEK SIZINTI RİSKLERİ

**Risk 1 (KRİTİK): GC İki Kez Yaratılıyor, Biri Atıl Kalıyor**

`gc_integration.cpp` satır 7-8:
```cpp
garbageCollector = std::make_unique<GarbageCollector>(globals); // interpreter'a ait
g_gc             = std::make_unique<GarbageCollector>(globals); // global
```
İki ayrı GC örneği var. `interpreter.cpp` içindeki `visitLiteralExpr`, `visitListExpr` vb. **`g_gc`** global'ini kullanıyor. Ama `Interpreter::collectGarbage()` `garbageCollector`'ı çağırıyor. Yani `g_gc` üzerinde allocate edilen nesneler, hiçbir zaman `garbageCollector` tarafından toplanmıyor. **Bu sistemik bir sızıntıdır.**

**Risk 2 (KRİTİK): `collect()` Fonksiyonu Call Stack Environment'larını Taramıyor**

`garbage_collector.cpp` satır 42-43 (yorum olarak bırakılmış):
```cpp
// In a complete implementation, the interpreter's call stack environments 
// must also be traced here.
```
`collect()` sadece global environment ve explicit `roots` vektörünü tarıyor. Fonksiyon çağrısı sırasında stackte yaşayan `Environment` nesneleri içindeki değerler (lokal değişkenler) **root olarak işaretlenmiyor.** Sonuç: herhangi bir fonksiyon çağrısının ortasında GC tetiklenirse, stackteki canlı nesneler silinebilir. Bu **use-after-free**'ye kapı açar.

**Risk 3 (Önemli): `bytesAllocated` Reset Mantığı Bozuk**

`garbage_collector.cpp` satır 61:
```cpp
bytesAllocated = 0; // Simplistic approach: reset counter...
```
Sweep sonrası sayaç sıfırlanıyor ama silinenlerin boyutu düşülmüyor. GC eşiği gerçek bellek kullanımını yansıtmıyor.

**Risk 4 (Önemli): `IS_OBJ` Makrosu BOOLEAN için Yanlış Sonuç Veriyor**

```cpp
#define IS_OBJ(value) ((value).type >= ValueType::STRING)
```
`ValueType` enum sırasında STRING (indeks 2) sonrası LIST (3), **BOOLEAN (4)**, NIL (5)... var. BOOLEAN için `IS_OBJ` `true` döndürüyor — bu **yanlış**. `markValue` içinde null `as.obj` okunursa UB.

**Risk 5 (Önemli): LoxInstance ve LoxClass hâlâ `shared_ptr` ile yaşıyor**

```cpp
auto instance = std::make_shared<LoxInstance>(...);
auto klass    = std::make_shared<LoxClass>(...);
```
Bu nesneler `GumusObject` zincirinin dışında. GC onları göremiyor. `Value.as.obj` union alanına `shared_ptr::get()` ham pointer'ı verilince, GC o adresi zincirde bulamaz → double-free/dangling pointer riski.

**Risk 6 (Önemli): Legacy Kurucular `as.obj = nullptr` Yapıyor Ama Hâlâ Çağrılıyor**

`value.h` satır 103-106:
```cpp
Value(std::shared_ptr<void> fake, ...) { as.obj = nullptr; /* LEGACY: SILINECEK */ }
Value(std::string v) : type(ValueType::STRING) { as.obj = nullptr; /* LEGACY: SILINECEK */ }
```
`visitFunctionStmt` satır 152'de aktif olarak çağrılıyor. STRING türünden bir Value yaratıp `AS_CSTRING` yapılırsa null pointer dereference.

---

## 2. HIZ ve ERİŞİM: Slot-based Index Sistemi

### Ne Yapıldı
`Resolver` sınıfı, derleme zamanında her değişkene `distance` (scope derinliği) ve `slot` (pozisyon) ataması yapıyor. `Environment` artık `valuesArray` ile O(1) indeks erişimi sunuyor.

### Güçlü Yönler
- **Resolver'ın `declare/define` mantığı sağlam.** `isDefined` bayrağı ile özbaşvuru koruması altyapısı mevcut.
- **`getAtSlot/assignAtSlot` doğru implemente edilmiş.** Distance traversal + slot indexi temiz.

### Kritik Sorunlar

**Sorun 1 (KRİTİK): Slot Sistemi ve Map Sistemi Aynı Anda Çalışıyor**

`interpreter.cpp` satır 161-168 (`visitVarStmt`):
```cpp
if (stmt->slot != -1) {
    environment->defineFast(value);          // valuesArray'e ekle
    environment->define(stmt->name.value, value); // AYNI ANDA map'e de ekle!
}
```
Her değişken tanımı hem array'e hem map'e yazılıyor. O(1) kazancı bellek ve yazma maliyeti açısından mahvediliyor.

**Sorun 2 (KRİTİK): `visitAssignExpr`'de Aynı Çifte Yazma**

`interpreter.cpp` satır 301-304:
```cpp
if (expr->slot != -1) {
    environment->assignAtSlot(expr->distance, expr->slot, value);
}
environment->assignAt(expr->distance, expr->name.value, value); // Her zaman map'e de yaz!
```
"Legacy fallback sync" yorumuyla bırakılmış. Senkronizasyon zorunluysa sistem yarı-yolda kalmış demektir; ikisi birden hem veri tutarsızlığı potansiyeli taşıyor hem de yavaş.

**Sorun 3 (Orta): Global Değişkenler Slot Sisteminden Yararlanamıyor**

`visitVariableExpr` satır 286-294: `distance == -1` ise `globals->get()` = map lookup. `hiz_testi.tr`'de `toplam` ve `i` global scope'ta tanımlı — yani döngü boyunca slot'un hiçbir faydası yok. Hız testi, tam olarak test etmek istediği şeyi ölçemiyor.

**Sorun 4 (Orta): `getAtSlot` lock() Başarısızlığı Kontrol Edilmiyor**

```cpp
auto parent = current->enclosing.lock();
current = parent.get(); // parent nullptr olursa?
```
Distance yanlışsa null pointer dereference. Resolver ile Interpreter arasındaki tutarsızlık bu crash'i tetikleyebilir.

### Performans Tavanı Değerlendirmesi

Slot sistemi tam çalışır hale getirilse (global'ler dahil edilse, map paraleli kaldırılsa) bu bir tree-walking yorumlayıcı için makul performans sağlar. Ancak her ifade için sanal fonksiyon çağrısı (vtable + `lastEvaluatedValue` yan kanal pattern'ı) HER ZAMAN bir maliyet. Bytecode VM'e kıyasla yaklaşık **2-10x daha yavaş** kalacak. Mevcut durumiyle tree-walking tavanına yaklaşıldı ama aşmak mümkün değil.

---

## 3. HATA YAKALAMA: Görsel İşaretçi ve Traceback

### Güçlü Yönler
- `^` işaretçi mekanizması doğru fikir; Token'dan `lineContent` + `column` alınıyor.
- Callstack snapshot `execute()` içinde yakalanıyor.
- Levenshtein tabanlı değişken önerisi gerçek bir kalite katkısı.

### Ciddi Eksiklikler

**Eksiklik 1 (Önemli): `^` İşaretçisi Runtime Hatalarının %90'ında Çalışmıyor**

`interpreter.cpp` içindeki hataların büyük çoğunluğu:
```cpp
throw LoxRuntimeException(expr->bracket.line, "Mesaj...");  // int alan kurucu
// BOŞ lineContent ve column! ^ görünmeyecek.
```
Oysa `Token` alan kurucu `lineContent` ve `column`'u dolduruyor. **Token kurucusu zorunlu hale getirilmeli.** `int line` alan kurucu gizli (veya kaldırılmalı).

**Eksiklik 2 (Orta): Traceback Yönü Şüpheli**

```cpp
for (auto it = error.callstack.rbegin(); it != error.callstack.rend(); ++it)
    finalMsg += "  -> " + *it + " icinde\n";
```
`callStack`'e fonksiyonlar `push_back` (içe doğru) ile ekleniyor; `rbegin` ile ters çevriliyor. Python/Rust tarzında en üstte **en son çağrılan** (hatanın yaşandığı yer) görünmeli. Gerçek çıktı test edilmeden emin olunmuyor.

**Eksiklik 3 (Düşük): `DayiDilHataCeviri` Kırılgan Spagetti**

String `find()` karşılaştırmasına dayalı hata çevirisi. Yeni bir hata mesajı eklendiğinde bu fonksiyon güncellenmezse "Gümüş Motor tekledi evlat" fallback'ine düşüyor. Hata kodu enum'u daha sağlam olurdu.

---

## 4. GELECEK VİZYONU

### Bytecode VM Hazırlık Skoru

| Bileşen | Durum | Not |
|---|---|---|
| Slot Sistemi (Resolver) | ✅ Var | `LOAD_LOCAL [slot]` opcode'a doğrudan dönüşür |
| GumusObject GC Zinciri | ⚠️ Yarı-hazır | Çift-GC sorunu çözülmeli |
| `Environment` Chain | ❌ Tree-walking'e özgü | VM'de `Value* stack` + frame offset'e dönüşür |
| LoxClass/LoxInstance (shared_ptr) | ❌ Uyumsuz | GC'nin dışında yaşıyor |
| Callstack | ✅ Var | `CallFrame` dizisine dönüşmesi kolay |
| `vm/` dizini | ⚠️ İskelet var | `main.cpp`'de IR→Bytecode→VM akışı var ama interpreter ile bağlantısı kopuk |

### Hangi Adım Önce?

**Cevap: Bytecode VM. Modül sistemi ikinci.**

Gerekçe:
1. `vm/` ve `ir/` dizinleri zaten var — yarım bırakılmış yatırım var. Önce modül kurulursa, VM geçişinde ikinci kez yazılacak.
2. Tree-walking tavanına ulaşıldı. Kullanıcı güveni için bir sonraki sıçrama **ölçülebilir hız artışı** — bu bytecode demek.
3. Slot sistemi, Resolver altyapısı doğrudan `LOAD_LOCAL/STORE_LOCAL` opcode'larına map edilebilir durumda.
4. Modül sistemi (`visitModuleStmt`) şu an tree-walking üzerinde çalışıyor; bytecode'a geçişte zaten yeniden yazılacak.

---

## 5. ÖZET: Hâlâ Sırıtan Durumlar

| # | Sorun | Önem |
|---|---|---|
| 1 | Çift GC örneği — `garbageCollector` vs `g_gc`, hangisi çalışacak? | 🔴 Kritik |
| 2 | GC Call Stack'i root olarak taramıyor — aktif nesneler silinebilir | 🔴 Kritik |
| 3 | `IS_OBJ` makrosu BOOLEAN için yanlış `true` dönüyor | 🔴 Kritik |
| 4 | Slot + Map çifte yazma — slot sisteminin anlamı yok | 🟠 Önemli |
| 5 | Legacy `Value(std::string)` kurucusu `as.obj = nullptr` ama hâlâ çağrılıyor | 🟠 Önemli |
| 6 | `LoxInstance`/`LoxClass` GC'nin dışında yaşıyor | 🟠 Önemli |
| 7 | `^` işaretçisi çoğu runtime hatasında görünmüyor (int line kullanılıyor) | 🟡 Orta |
| 8 | Global değişkenler slot hızından yararlanamıyor | 🟡 Orta |
| 9 | `interpreter.h` içinde çift `Environment`/`Interpreter` tanımı (namespace içi + dışı) | 🟡 Orta |
| 10 | `DayiDilHataCeviri` string karşılaştırmasına dayalı, kırılgan | 🟢 Düşük |

**Özet karar:** Mimari yön doğru. Ama yarım kalmış geçiş (legacy kurucular, çift GC, slot+map ikiliği) sistemi hem yavaş hem tehlikeli yapıyor. "Tamamla ya da geri al" prensibiyle legacy kod tamamen temizlenmeli, sonra Bytecode VM adımı atılmalı.
