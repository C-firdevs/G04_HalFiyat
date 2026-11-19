# 02_Kod

Bu klasör, G04_HalFiyat (Hâl Fiyatlarıyla Akıllı Satın Alma) projesinin veri toplama, ön işleme, keşifçi veri analizi (EDA) ve karar destek kodlarını içerir.

## Dosyalar
- `01_veri_cekme.ipynb`: İzmir Büyükşehir Belediyesi Açık Veri Portalı'ndan hâl fiyat verilerinin ve TÜFE endeksinin çekilmesi, temizlenmesi, `MAL_TURU` alanındaki `İTHAL`/`İTHAL..` tutarsızlıklarının `ITHAL` olarak birleştirilmesi, `ASGARI_UCRET` (Min) ve `AZAMI_UCRET` (Max) sütunlarının korunması ve reel fiyat/özellik türetimi.
- `02_eda.ipynb`: Keşifsel veri analizi (EDA), mevsimsel ve aylık/haftalık/günlük fiyat analizleri, ilk 25 ürün karar destek özeti ve 6 adet görselleştirme (`grafik_1` - `grafik_6`, çıktılar `04_Rapor/` dizinine kaydedilir).
- `requirements.txt`: Proje Python bağımlılıkları.
