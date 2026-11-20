# 🌿 SNC | Akıllı Satın Alma — Karar Destek Sistemi (`G04_HalFiyat`)

Ege Bölgesi'nde 12 şubesi bulunan bir restoran zincirinin sebze-meyve satın alma kararlarını optimize etmek amacıyla **İzmir Büyükşehir Belediyesi Açık Veri Portalı Hal Fiyatları (2006–2025)** ve **TCMB EVDS TÜFE** verileri kullanılarak geliştirilmiş yapay zekâ ve karar destek uygulamasıdır.

---

## 📁 Proje Klasör Yapısı (5'li Teslim Standardı)

```text
G04_HalFiyat/
├── .streamlit/
│   └── config.toml                          # Kurumsal zümrüt yeşili (#1B7A43) Streamlit teması
├── 01_Veri/
│   ├── 01_veri_cekme.ipynb                  # CKAN API veri çekme, temizleme, TÜFE ve özellik türetme
│   ├── hal_reel_ozellikli.csv               # Lag, oynaklık ve Min/Max fiyat sütunlu ana model verisi
│   ├── ilk_25_aylik_reel_fiyat.csv          # 25 ürün x 12 ay mevsimsel reel fiyat tablosu
│   ├── ilk_25_reel_karar_destegi.csv        # En ucuz/pahalı ay ve mevsimsel fark karar tablosu
│   ├── ilk_25_reel_ozet.csv                 # Nominal ve reel fiyat özet istatistikleri (ITHAL birleşik)
│   ├── gunluk_satinalma_karar.csv           # Günlük satın alma sinyalleri (DURUM)
│   ├── haftalik_satinalma_karar.csv         # Haftalık satın alma sinyalleri (DURUM)
│   ├── aylik_satinalma_karar.csv            # Aylık satın alma sinyalleri (DURUM)
│   ├── mevsimsel_satinalma_karar.csv        # Mevsimsel satın alma sinyalleri (DURUM)
│   ├── ornek_veri.csv                       # İlk 100 satırlık örnek veri
│   └── veri_sozlugu.xlsx                    # Değişken tanımları ve veri tipleri
├── 02_Kod/
│   ├── 01_veri_cekme.ipynb                  # Veri çekme ve ön işleme notebook'u
│   ├── 02_eda.ipynb                         # Keşifsel veri analizi (EDA) ve karar tabloları notebook'u
│   ├── 03_model.ipynb                       # K-Means kümeleme ve fiyat tahmin modelleri (RF, GB, Baseline)
│   ├── app.py                               # SNC | Akıllı Satın Alma Streamlit arayüzü (5 Sekme)
│   ├── requirements.txt                     # Gerekli Python kütüphaneleri
│   └── README.md                            # Kurulum ve çalıştırma kılavuzu
├── 03_Model/
│   └── model.joblib                         # Eğitilmiş makine öğrenmesi Pipeline modeli
├── 04_Rapor/
│   ├── grafik_1_nominal_vs_reel.png         # EDA Grafik 1
│   ├── grafik_2_en_oynak_urunler.png        # EDA Grafik 2
│   ├── grafik_3_aylik_mevsimsel_reel.png    # EDA Grafik 3
│   ├── grafik_4_mal_turu_reel_fiyat.png     # EDA Grafik 4
│   ├── grafik_5_en_yuksek_reel_fiyat_urunler.png # EDA Grafik 5
│   └── grafik_6_reel_degisim_dagilimi.png   # EDA Grafik 6
└── 05_Sunum/
    └── README.md                            # Sunum (G04_Sunum.pdf) ve demo videosu (G04_Demo.mp4)
```

---

## 🚀 Kurulum ve Çalıştırma

1. **Gerekli Kütüphaneleri Yükleyin:**
   ```bash
   pip install -r 02_Kod/requirements.txt
   ```

2. **Streamlit Arayüzünü Başlatın:**
   Proje ana dizinindeyken:
   ```bash
   streamlit run 02_Kod/app.py
   ```
   *(Not: Uygulama `02_Kod/` dizini içinden `streamlit run app.py` komutuyla çalıştırıldığında da tüm `01_Veri/` ve `03_Model/` yollarını otomatik olarak çözer.)*

---

## 🖥️ Arayüz Özellikleri (5 Sekme)

1. **📊 Panel & Özet:** Kısa dönem oynaklığı (`REEL_OYNAKLIK_7 > REEL_OYNAKLIK_30`) artan ürünler için **Fiyat Şoku Alarmı**, 4 temel KPI kartı ve `.txt` olarak indirilebilen **Tek Tıkla Pazartesi Sabahı Yönetici Özeti**.
2. **📅 Analiz & Zamanlama:** Nominal (`ASGARI_UCRET – AZAMI_UCRET` bandı) ve Reel fiyat geçmişi, **25 Ürün × 12 Ay En Ucuz Aylar Isı Haritası**, **Haftanın Hangi Günü Hal'e Gidilmeli?** analizi ve **Enflasyon Aynası (Nominal vs. TÜFE vs. Reel)**.
3. **🎯 Strateji & Risk:** 4 bölgeli **Kraljic Satın Alma Matrisi**, **Pazarlık Gücü & Kalite Makası** ve son 1 yıllık **Backtest (Geçen Yıl Bu Sistemi Dinleseydik Ne Olurdu?)** simülasyonu.
4. **🤖 Karar Ekranı:** 4 zaman dilimli sinyal kartı (Günlük/Haftalık/Aylık/Mevsimsel), `03_Model/model.joblib` (veya güvenli yedek trend) ile **Gelecek Hafta Fiyat Tahmini & Belirsizlik Aralığı**, küme bazlı ikame önerisi ve **Tedarikçi Teklif Kontrolü**.
5. **🏪 Tasarruf Simülatörü:** Şube sayısı (1–50), fire oranı (%), depolama maliyeti (%) ve `st.data_editor` ile şube başı tüketim miktarlarına göre yıllık net tasarruf hesabı, fiziksel stok zararlıysa **Sabit Fiyat Sözleşmesi** uyarısı ve `openpyxl` ile biçimlendirilmiş **Kurumsal Excel (`.xlsx`) Satın Alma Planı** indirme özelliği.
