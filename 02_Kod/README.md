# 🌿 SNC | Akıllı Satın Alma (G04_HalFiyat)

🌐 **Canlı Uygulama Linki:** https://snc-akilli-satin-alma.streamlit.app/

**Mersin Üniversitesi • Erdemli Uygulamalı Teknoloji ve İşletmecilik Yüksekokulu (UTİYO) • Yönetim Bilişim Sistemleri • Yapay Zekâ Dersi Dönem Projesi (2026–2027 Güz)**

1 şubeden 50 şubeye kadar çok şubeli restoran zincirlerinin sebze ve meyve satın alma kararlarını optimize etmek amacıyla **İzmir Büyükşehir Belediyesi Açık Veri Portalı Hal Fiyatları (2006–2025, 131.888 kayıt, 25 ürün)**, **TCMB EVDS TÜFE** ve **Open-Meteo İzmir Zirai Don (3.535 kayıt)** verileri birleştirilerek geliştirilmiş uçtan uca veri bilimi, makine öğrenmesi ve Streamlit karar destek platformudur.

---

## 👥 Ekip Üyeleri (Grup G04)

* **Nesrin İleri** (`24430040031`) — Veri Mühendisliği, CKAN API Veri Çekme, TÜFE Enflasyon Arındırması, Ön İşleme ve Keşifsel Veri Analizi (EDA)
* **Suzan Özer** (`24430040041`) — Makine Öğrenmesi Modelleme (1 Haftalık & 1 Aylık Fiyat Tahmini, K-Means Mevsimsel Kümeleme, SHAP Açıklanabilirlik ve 15 Özellikli İzmir Don İklim Modeli)
* **Cennet Firdevs Uzan** (`24430040039`) — 6 Panelli Kurumsal Streamlit Karar Destek Arayüzü (`SNC | Akıllı Satın Alma`), 1–50 Şube Tasarruf Simülatörü, Menü & Reçete Maliyet Asistanı, Final Raporu ve Teslim Paketi

---

## 📁 Proje Klasör Yapısı (5'li Teslim Standardı)

```text
G04_HalFiyat/
├── 01_Veri/     # Ham/temiz hal verileri, TÜFE verisi, don & özellik CSV'leri, karar tabloları ve veri sözlüğü (.csv, .xlsx)
├── 02_Kod/      # Veri çekme (01_veri_cekme.ipynb), EDA (02_eda.ipynb), modelleme (03_model.ipynb), Streamlit arayüzü (app.py), QR/logo, requirements.txt ve README.md
├── 03_Model/    # Eğitilmiş Pipeline modelleri (model.joblib, model_aylik.joblib, model_don_ozellikli.joblib) ile SHAP, K-Means ve Don analiz görselleri
├── 04_Rapor/    # Keşifsel veri analizi, SHAP, K-Means & Don grafikleri (.png) ve final proje raporu (G04_FinalRapor.pdf — 8 sayfa)
└── 05_Sunum/    # Final sunum dosyası (G04_Sunum.pptx — 12 slayt) ve HD canlı demo videosu (G04_Demo.mp4)
```

| Klasör | İçerik ve Görev |
| :--- | :--- |
| **`01_Veri`** | İzmir BB CKAN API'den çekilen 20 yıllık hal fiyatları (`131.888` kayıt), TCMB EVDS TÜFE verisi, `hal_reel_ozellikli.csv`, `hal_reel_don_ozellikli.csv`, karar destek özet tabloları, ürün kümeleri, model/don performans CSV'leri, `ornek_veri.csv` ve `veri_sozlugu.xlsx`. |
| **`02_Kod`** | Tüm çalışma notebook'ları (`01_veri_cekme.ipynb`, `02_eda.ipynb`, `03_model.ipynb`), mobil uyumlu kurumsal anasayfa + 6 panelli Streamlit uygulaması (`app.py`), `requirements.txt`, QR/logo görselleri ve kurulum kılavuzu (`README.md`). |
| **`03_Model`** | Kayıtlı 1 haftalık (`model.joblib`), 1 aylık (`model_aylik.joblib`) ve 15 özellikli iklim/don (`model_don_ozellikli.joblib`) Pipeline modelleri ile `shap_aciklanabilirlik.png`, `kumeleme_mevsimsel_profiller.png` ve `don_etkisi_analiz.png`. |
| **`04_Rapor`** | 11 adet analiz/model grafiği (`grafik_1..10.png`) ve şablona uygun **8 sayfalık final proje raporu** (`G04_FinalRapor.pdf`). |
| **`05_Sunum`** | Gerçek uygulama ekranlı **12 slaytlık final sunumu** (`G04_Sunum.pptx`) ve tüm 6 panel ile 16 açılır pencereyi kapsayan **HD canlı demo videosu** (`G04_Demo.mp4`). |

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

## 🖥️ Arayüz Modülleri (Kurumsal Anasayfa + 6 Panel)

* **🌿 Kurumsal Anasayfa:** Masaüstü ve mobil uyumlu karşılama ekranı, telefonla taratılabilen Mobil QR erişimi, etkileşimli Örnek AI Alım Sinyali önizleme kartı ve 6 panel özeti.
1. **📊 Panel & Özet:** Kısa dönem Fiyat Şoku Alarmı, 4 temel KPI kartı, renk kodlu Pazartesi Sabahı Yönetici Brifingi (`.txt` ve renkli A4 `.pdf` indirme), 4'lü model karşılaştırma tablosu, K-Means ürün kümeleri ve SHAP açıklanabilirlik görselleri.
2. **📅 Analiz & Zamanlama:** Nominal (Taban–Tavan bantlı) & Reel fiyat geçmişi, 25×12 En Ucuz Aylar Isı Haritası, Haftanın En Ucuz Hal Günü, Enflasyon Aynası, canlı Kruskal-Wallis hipotez testleri, 20 yılda reel olarak en çok pahalanan/ucuzlayan ürünler, 12 Aylık Sözleşme Ajandası ve **İzmir Zirai Don Olaylarının 1–4 Haftalık Gecikmeli Fiyat Etkisi**.
3. **🎯 Strateji & Risk:** 4 bölgeli Kraljic Satın Alma Strateji Matrisi + 4 bölge özet tablosu, Pazarlık Gücü & Kalite Makası ve Geçmiş 1 Yıllık Strateji Doğrulaması (Backtest).
4. **🤖 Karar Ekranı:** 4 zaman dilimli durum kartları, Hedef Alım Tarihi seçimi, **Canlı İklim ve Don Senaryosu (15 Özellikli İklim Modeli)**, 1 Haftalık ve 1 Aylık (4 Haftalık) güven bantlı fiyat projeksiyonu, Tedarikçi Teklif Kontrolü ve küme bazlı ikame önerileri.
5. **🏪 Tasarruf Simülatörü (İmza Özellik 1):** 1–50 dinamik şube sayısı, zayi/bozulma (%) ve soğuk depo (%) giderlerine göre Spot vs. Akıllı Alım hesabı (12 şubede yıllık **2.411.072 TL / -%20,7** net tasarruf), dinamik rozetli Senaryo A vs. Senaryo B karşılaştırması, Yönetime 3 Stratejik Öneri ve 2 sayfalı renk kodlu kurumsal Excel (`.xlsx`) çıktısı.
6. **🥗 Menü & Reçete (İmza Özellik 2):** 4 hazır Ege restoran tarifi + serbest reçete oluşturucu, 12 aylık porsiyon maliyet eğrisi, Maliyet Katili tespiti ve K-Means mevsimlik ikame önerisi.
