# 🌿 G04_HalFiyat — SNC | Akıllı Satın Alma (İzmir Hal Fiyatları Karar Destek Sistemi)

**Mersin Üniversitesi • Yönetim Bilişim Sistemleri • Yapay Zekâ Dersi Dönem Projesi (2026–2027 Güz)**

Ege Bölgesi'ndeki çok şubeli bir restoran zincirinin sebze-meyve satın alma kararlarını optimize etmek amacıyla **İzmir Büyükşehir Belediyesi Açık Veri Portalı Hal Fiyatları (2006–2025, 131.888 kayıt, 25 ürün)** ve **TCMB EVDS TÜFE** verileri kullanılarak geliştirilmiş uçtan uca veri bilimi, makine öğrenmesi ve Streamlit karar destek sistemidir.

---

## 👥 Ekip Üyeleri

* **Nesrin İleri** — Veri Mühendisliği, CKAN API Veri Çekme, Ön İşleme ve Keşifsel Veri Analizi (EDA)
* **Suzan Özer** — Makine Öğrenmesi Modelleme (1 Haftalık & 1 Aylık Fiyat Tahmini, K-Means Kümeleme, SHAP Açıklanabilirlik)
* **Cennet Firdevs Uzan** — Streamlit Karar Destek Arayüzü (`SNC | Akıllı Satın Alma`), Tasarruf Simülatörü, Menü/Reçete Analizi, Final Raporu ve Teslim Paketi

---

## 📁 Proje Klasör Yapısı (5'li Teslim Standardı)

```text
G04_HalFiyat/
├── 01_Veri/     # Ham/temiz hal verileri, TÜFE verisi, özellik türetilmiş CSV'ler, tahmin/küme çıktıları ve veri sözlüğü (.csv, .xlsx)
├── 02_Kod/      # Veri çekme (01_veri_cekme.ipynb), EDA (02_eda.ipynb), modelleme (03_model.ipynb), Streamlit arayüzü (app.py), requirements.txt ve README.md
├── 03_Model/    # Eğitilmiş Pipeline modelleri (model.joblib, model_aylik.joblib) ve SHAP / K-Means analiz görselleri
├── 04_Rapor/    # Keşifsel veri analizi grafikleri (.png) ve final proje raporu (G04_FinalRapor.docx / .pdf)
└── 05_Sunum/    # Final sunum dosyası (G04_Sunum.pdf / .pptx) ve 2–3 dakikalık canlı demo videosu (G04_Demo.mp4)
```

| Klasör | İçerik ve Görev |
| :--- | :--- |
| **`01_Veri`** | İzmir BB CKAN API'den çekilen 20 yıllık hal fiyatları, TCMB EVDS TÜFE verisi, `hal_reel_ozellikli.csv`, karar destek özet tabloları, ürün kümeleri, model performans/özellik önemi CSV'leri, `ornek_veri.csv` ve `veri_sozlugu.xlsx`. |
| **`02_Kod`** | Tüm çalışma notebook'ları (`01_veri_cekme.ipynb`, `02_eda.ipynb`, `03_model.ipynb`), 6 sekmeli kurumsal Streamlit uygulaması (`app.py`), bağımlılık listesi (`requirements.txt`) ve kurulum kılavuzu (`README.md`). |
| **`03_Model`** | Kayıtlı 1 haftalık (`model.joblib`) ve 1 aylık (`model_aylik.joblib`) makine öğrenmesi Pipeline modelleri ile `shap_aciklanabilirlik.png` ve `kumeleme_mevsimsel_profiller.png` görselleri. |
| **`04_Rapor`** | 6 adet EDA grafiği (`grafik_1..6.png`) ve şablona uygun final proje raporu (`G04_FinalRapor.docx` ve `.pdf`). |
| **`05_Sunum`** | Proje sunumu (`G04_Sunum.pdf`) ve canlı uygulama demo kaydı (`G04_Demo.mp4`). |

---

## 🚀 Kurulum ve Çalıştırma Adımları

Proje ana dizininde terminali açıp aşağıdaki iki komutu sırasıyla çalıştırmanız yeterlidir:

1. **Gerekli Python paketlerini yükleyin:**
   ```bash
   pip install -r 02_Kod/requirements.txt
   ```

2. **Streamlit karar destek arayüzünü başlatın:**
   ```bash
   streamlit run 02_Kod/app.py
   ```

*(Uygulama varsayılan olarak tarayıcınızda `http://localhost:8501` adresinde açılır. Tüm veri dosyaları ve kayıtlı modeller yerel diskten okunduğu için sunum ortamında internetsiz olarak da sorunsuz çalışır.)*

---

## 🖥️ Arayüz Modülleri (6 Sekme)

1. **📊 Panel & Özet:** Kısa dönem Fiyat Şoku Alarmı, 4 temel KPI kartı, renk kodlu Pazartesi Sabahı Yönetici Brifingi (`.txt` ve `.pdf` indirme) ve model/SHAP özeti.
2. **📅 Analiz & Zamanlama:** Nominal (Taban–Tavan bantlı) & Reel fiyat geçmişi, 25×12 En Ucuz Aylar Isı Haritası, Haftanın En Ucuz Hal Günü (Pazartesi–Cumartesi), Enflasyon Aynası, canlı Kruskal-Wallis $H_0/H_1$ hipotez testleri, 20 yılda reel olarak en çok pahalanan/ucuzlayan ürünler ve 12 Aylık Sözleşme Ajandası.
3. **🎯 Strateji & Risk:** 4 bölgeli Kraljic Satın Alma Matrisi + 4 bölge özet tablosu, Pazarlık Gücü & Kalite Makası ve 1 yıllık Backtest.
4. **🤖 Karar Ekranı:** 4 zaman dilimli durum kartları, Hedef Alım Tarihi seçimi, 1 Haftalık ve 1 Aylık (4 Haftalık) fiyat projeksiyonu + güven aralığı + stratejik karar rozeti, Tedarikçi Teklif Kontrolü, küme bazlı ikame önerileri ve SHAP/model karşılaştırma paneli.
5. **🏪 Tasarruf Simülatörü:** Dinamik şube sayısı, zayi/bozulma ve soğuk depo oranlarına göre Spot vs. Akıllı Alım hesabı, dinamik rozetli Senaryo A vs. Senaryo B karşılaştırması, Yönetime 3 Altın Öneri ve 2 sayfalı renk kodlu kurumsal Excel (`.xlsx`) çıktısı.
6. **🥗 Menü & Reçete:** 4 hazır Ege restoran tarifi + serbest reçete oluşturucu, 12 aylık porsiyon maliyet eğrisi, Maliyet Katili tespiti ve mevsimlik ikame önerisi.
