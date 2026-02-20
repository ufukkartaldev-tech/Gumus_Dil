# 🤝 GümüşDil Geliştirme Rehberi (Contributing)

GümüşDil projesine katkıda bulunmak ve yerli yazılım ekosistemini büyütmek ister misiniz? İşte nasıl başlayacağınıza dair bir yol haritası:

## 💎 1. Yeni Kütüphane Ekleme
GümüşDil modüler bir yapıya sahiptir. Kendi kütüphanenizi oluşturmak için:
1. `lib/` dizini altında `.tr` uzantılı bir dosya oluşturun.
2. `modül` veya `sınıf` yapılarını kullanarak fonksiyonlarınızı tanımlayın.
3. Örnek kullanım dosyasını `ornekler/` dizinine ekleyin.

## 🐛 2. Hata Bildirimi ve Giderme
Eğer bir hata bulursanız veya bir iyileştirme öneriniz varsa:
- Hatanın hangi işletim sisteminde (Pardus/Windows) oluştuğunu belirtin.
- Hata veren kod parçacığını paylaşın.

## 🎨 3. Tema Tasarımı
GümüşDil'in görsel kalitesini artırmak için `src/ide/config.py` içindeki `THEMES` sözlüğüne yeni bir tema ekleyebilir veya `temimarir.json` üzerinden özel temanızı paylaşabilirsiniz.

## 🚀 4. Pardus Entegrasyonu
Pardus'a özel yeni sistem araçları (paket yönetimi, sistem izleme vb.) geliştirmek isterseniz `lib/pardus_sistem.tr` dosyasını genişletebilirsiniz.

**Unutmayın: En iyi kod, başkaları tarafından da okunabilen ve geliştirilebilen koddur.** 🇹🇷 💎


