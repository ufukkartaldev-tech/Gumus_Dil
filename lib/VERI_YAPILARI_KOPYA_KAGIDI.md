# 📋 GümüşDil Veri Yapıları - Hızlı Referans

## 🚀 Hızlı Başlangıç

```gumus
// Kütüphaneyi yükle
yukle("lib/veri_yapilari.tr")

// Kullan!
değişken yigin = yeni Yigin()
yigin.ekle(42)
```

---

## 📚 Veri Yapıları Özet Tablosu

| Yapı | Ne Zaman Kullan? | Güçlü Yönü | Zayıf Yönü |
|------|------------------|------------|------------|
| **Yığın** | Geri alma, fonksiyon çağrıları | Son eklenen hızlı erişim | Ortadaki elemana erişim yok |
| **Kuyruk** | Sıralı işleme, BFS | İlk eklenen hızlı erişim | Ortadaki elemana erişim yok |
| **Öncelikli Kuyruk** | Görev zamanlama, Dijkstra | Önceliğe göre işlem | Ekleme yavaş (O(n)) |
| **Bağlı Liste** | Dinamik boyut, sık ekleme/çıkarma | Başa/sona ekleme hızlı | Arama yavaş (O(n)) |
| **Hash Tablosu** | Hızlı arama, cache | O(1) erişim | Sıralama yok |
| **İkili Arama Ağacı** | Sıralı veri, aralık sorguları | Sıralı erişim | Dengesiz olabilir |

---

## 🎯 Kod Örnekleri

### Yığın (Stack)
```gumus
değişken yigin = yeni Yigin()
yigin.ekle(10)           // Push
yigin.ekle(20)
yazdır(yigin.ust())      // Peek → 20
yazdır(yigin.cikar())    // Pop → 20
yazdır(yigin.bosmu())    // false
yigin.temizle()          // Clear
```

### Kuyruk (Queue)
```gumus
değişken kuyruk = yeni Kuyruk()
kuyruk.ekle("A")         // Enqueue
kuyruk.ekle("B")
yazdır(kuyruk.ilk())     // Peek → "A"
yazdır(kuyruk.cikar())   // Dequeue → "A"
yazdır(kuyruk.bosmu())   // false
```

### Öncelikli Kuyruk
```gumus
değişken pq = yeni OncelikliKuyruk()
pq.ekle("Düşük", 10)     // (eleman, öncelik)
pq.ekle("Yüksek", 1)     // Küçük = yüksek öncelik
yazdır(pq.cikar())       // → "Yüksek"
```

### Bağlı Liste
```gumus
değişken liste = yeni BagliListe()
liste.sonaEkle(10)       // Append
liste.basaEkle(5)        // Prepend
liste.yazdir()           // → [5, 10]
yazdır(liste.ara(10))    // → 1 (indeks)
liste.bastanCikar()      // → 5
```

### Hash Tablosu
```gumus
değişken tablo = yeni HashTablosu(10)
tablo.ekle("isim", "Ufuk")
tablo.ekle("yas", 25)
yazdır(tablo.al("isim")) // → "Ufuk"
yazdır(tablo.varmi("yas")) // → true
```

### İkili Arama Ağacı
```gumus
değişken agac = yeni IkiliAramaAgaci()
agac.ekle(50)
agac.ekle(30)
agac.ekle(70)
yazdır(agac.ara(30))     // → true
agac.inorder()           // → 30, 50, 70 (sıralı)
```

---

## 💡 Hangi Veri Yapısını Seçmeliyim?

### Soru: "En son eklenen elemanı hızlıca almak istiyorum"
**Cevap:** ✅ **Yığın (Stack)**

### Soru: "İlk gelen ilk işlensin (sıra mantığı)"
**Cevap:** ✅ **Kuyruk (Queue)**

### Soru: "Önceliğe göre işlem yapmak istiyorum"
**Cevap:** ✅ **Öncelikli Kuyruk**

### Soru: "Sık sık başa/sona eleman ekleyip çıkaracağım"
**Cevap:** ✅ **Bağlı Liste**

### Soru: "Anahtar-değer çiftleri, hızlı erişim"
**Cevap:** ✅ **Hash Tablosu**

### Soru: "Sıralı veri tutmak ve hızlı aramak istiyorum"
**Cevap:** ✅ **İkili Arama Ağacı**

---

## 🎓 Karmaşıklık Karşılaştırması

### En Hızlı Ekleme
1. **Yığın** - O(1)
2. **Kuyruk** - O(1)
3. **Bağlı Liste** (başa/sona) - O(1)
4. **Hash Tablosu** - O(1) ortalama

### En Hızlı Arama
1. **Hash Tablosu** - O(1) ortalama
2. **İkili Arama Ağacı** - O(log n) dengeli
3. **Diğerleri** - O(n)

### En Az Bellek
Hepsi O(n) - eleman sayısına göre

---

## 🔥 Pro İpuçları

### 1. Yığın Kullanımı
```gumus
// ✅ İYİ: Geri alma (undo)
değişken islemler = yeni Yigin()
islemler.ekle("Metin yazdı")
islemler.ekle("Resim ekledi")
islemler.cikar()  // Son işlemi geri al
```

### 2. Kuyruk Kullanımı
```gumus
// ✅ İYİ: Görev sırası
değişken gorevler = yeni Kuyruk()
gorevler.ekle("Email gönder")
gorevler.ekle("Rapor oluştur")
// İlk eklenen ilk işlenir
```

### 3. Hash Tablosu Kullanımı
```gumus
// ✅ İYİ: Hızlı veri erişimi
değişken kullanicilar = yeni HashTablosu(100)
kullanicilar.ekle("user123", "Ufuk Kartal")
// O(1) erişim!
```

### 4. İkili Arama Ağacı Kullanımı
```gumus
// ✅ İYİ: Sıralı veri
değişken puanlar = yeni IkiliAramaAgaci()
puanlar.ekle(85)
puanlar.ekle(92)
puanlar.ekle(78)
puanlar.inorder()  // Sıralı: 78, 85, 92
```

---

## ⚠️ Yaygın Hatalar

### ❌ YANLIŞ
```gumus
değişken yigin = yeni Yigin()
yazdır(yigin.cikar())  // Boş yığından çıkarma!
```

### ✅ DOĞRU
```gumus
değişken yigin = yeni Yigin()
eğer (!yigin.bosmu()) {
    yazdır(yigin.cikar())
}
```

---

## 📖 Daha Fazla Bilgi

- **Detaylı Dokümantasyon:** `lib/VERI_YAPILARI_OKU_BENI.md`
- **Unit Testler:** `tests/test_veri_yapilari.tr`
- **Gerçek Örnekler:** `examples/veri_yapilari_ornekler.tr`

---

**Not:** Modern GümüşDil sözdizimi - noktalı virgül kullanma! 🚫;

© 2026 Ufuk Kartal - GümüşDil Veri Yapıları Kütüphanesi

