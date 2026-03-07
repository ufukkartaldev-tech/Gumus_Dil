# 📚 GümüşDil Veri Yapıları Kütüphanesi

Modern, Türkçe, noktalı virgül kullanmayan veri yapıları kütüphanesi.

## 🎯 İçindekiler

### 1. **Yığın (Stack)** - LIFO
Son giren ilk çıkar prensibiyle çalışan veri yapısı.

**Metodlar:**
- `ekle(eleman)` - Yığına eleman ekle
- `cikar()` - Üstteki elemanı çıkar ve döndür
- `ust()` - Üstteki elemana bak (çıkarmadan)
- `bosmu()` - Yığın boş mu kontrol et
- `temizle()` - Tüm elemanları sil

**Örnek:**
```gumus
değişken yigin = yeni Yigin()
yigin.ekle(10)
yigin.ekle(20)
yazdır(yigin.cikar())  // 20
```

### 2. **Kuyruk (Queue)** - FIFO
İlk giren ilk çıkar prensibiyle çalışan veri yapısı.

**Metodlar:**
- `ekle(eleman)` - Kuyruğa eleman ekle
- `cikar()` - İlk elemanı çıkar ve döndür
- `ilk()` - İlk elemana bak (çıkarmadan)
- `bosmu()` - Kuyruk boş mu kontrol et
- `temizle()` - Tüm elemanları sil

**Örnek:**
```gumus
değişken kuyruk = yeni Kuyruk()
kuyruk.ekle("Ahmet")
kuyruk.ekle("Mehmet")
yazdır(kuyruk.cikar())  // "Ahmet"
```

### 3. **Öncelikli Kuyruk (Priority Queue)**
Öncelik sırasına göre çalışan kuyruk.

**Metodlar:**
- `ekle(eleman, oncelik)` - Öncelikli eleman ekle (küçük sayı = yüksek öncelik)
- `cikar()` - En yüksek öncelikli elemanı çıkar
- `bosmu()` - Kuyruk boş mu kontrol et

**Örnek:**
```gumus
değişken pq = yeni OncelikliKuyruk()
pq.ekle("Düşük", 10)
pq.ekle("Yüksek", 1)
pq.ekle("Orta", 5)
yazdır(pq.cikar())  // "Yüksek"
```

### 4. **Bağlı Liste (Linked List)**
Dinamik boyutlu, bağlantılı düğümlerden oluşan liste.

**Metodlar:**
- `basaEkle(veri)` - Listenin başına ekle
- `sonaEkle(veri)` - Listenin sonuna ekle
- `bastanCikar()` - Baştan eleman çıkar
- `ara(veri)` - Elemanın indeksini bul (-1 = bulunamadı)
- `bosmu()` - Liste boş mu kontrol et
- `yazdir()` - Listeyi ekrana yazdır

**Örnek:**
```gumus
değişken liste = yeni BagliListe()
liste.sonaEkle(10)
liste.sonaEkle(20)
liste.basaEkle(5)
liste.yazdir()  // [5, 10, 20]
```

### 5. **Hash Tablosu (Hash Table)**
Anahtar-değer çiftlerini hızlı erişim için saklayan yapı.

**Metodlar:**
- `ekle(anahtar, deger)` - Anahtar-değer çifti ekle
- `al(anahtar)` - Anahtara karşılık gelen değeri al
- `varmi(anahtar)` - Anahtar var mı kontrol et

**Örnek:**
```gumus
değişken tablo = yeni HashTablosu(10)
tablo.ekle("isim", "Ufuk")
tablo.ekle("yas", 25)
yazdır(tablo.al("isim"))  // "Ufuk"
```

### 6. **İkili Arama Ağacı (Binary Search Tree)**
Sıralı veri saklama ve hızlı arama için ağaç yapısı.

**Metodlar:**
- `ekle(deger)` - Ağaca değer ekle
- `ara(deger)` - Değer var mı ara (true/false)
- `inorder()` - Sıralı şekilde yazdır (sol-kök-sağ)

**Örnek:**
```gumus
değişken agac = yeni IkiliAramaAgaci()
agac.ekle(50)
agac.ekle(30)
agac.ekle(70)
agac.ekle(20)
agac.inorder()  // 20, 30, 50, 70
```

## 🚀 Kullanım

Kütüphaneyi projenize dahil edin:

```gumus
// Kütüphaneyi yükle
yukle("lib/veri_yapilari.tr")

// Kullanmaya başlayın!
değişken yigin = yeni Yigin()
yigin.ekle(42)
```

## 📊 Karmaşıklık Analizi

| Veri Yapısı | Ekleme | Çıkarma | Arama | Bellek |
|-------------|--------|---------|-------|--------|
| Yığın | O(1) | O(1) | O(n) | O(n) |
| Kuyruk | O(1) | O(1) | O(n) | O(n) |
| Öncelikli Kuyruk | O(n) | O(1) | O(n) | O(n) |
| Bağlı Liste | O(1) | O(1) | O(n) | O(n) |
| Hash Tablosu | O(1)* | - | O(1)* | O(n) |
| İkili Arama Ağacı | O(log n)** | O(log n)** | O(log n)** | O(n) |

\* Ortalama durum, en kötü O(n)  
\** Dengeli ağaç için, en kötü O(n)

## 💡 İpuçları

1. **Yığın**: Geri alma (undo) işlemleri, fonksiyon çağrı yığını
2. **Kuyruk**: Görev sıralaması, BFS algoritması
3. **Öncelikli Kuyruk**: Dijkstra algoritması, görev zamanlama
4. **Bağlı Liste**: Dinamik bellek yönetimi, undo/redo
5. **Hash Tablosu**: Hızlı veri erişimi, cache
6. **İkili Arama Ağacı**: Sıralı veri, aralık sorguları

## 🎓 Öğrenme Kaynakları

- [Veri Yapıları ve Algoritmimarir](https://www.example.com)
- [Big O Notation](https://www.example.com)
- [GümüşDil Dokümantasyonu](../docs/OKU_BENI.md)

## 📝 Lisans

MIT License - Ufuk Kartal © 2026

---

**Not:** Bu kütüphane modern GümüşDil sözdizimi kullanır - noktalı virgül kullanmayın! 🚫;


