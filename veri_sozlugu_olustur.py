from pathlib import Path
import numpy as np
import pandas as pd


def veri_klasoru_bul(baslangic: Path) -> Path:
  for aday in [baslangic] + list(baslangic.parents):
    if aday.name == "01_Veri":
      return aday
    hedef = aday / "01_Veri"
    if hedef.exists() and hedef.is_dir():
      return hedef
  raise FileNotFoundError("'01_Veri' klasörü bulunamadı.")


veri_klasoru = veri_klasoru_bul(Path(__file__).resolve().parent)
df = pd.read_csv(veri_klasoru / "hal_reel_ozellikli.csv")

aciklamalar = {
    "TARIH": "Fiyat kaydının ait olduğu tarih bilgisi.",
    "YIL": "Tarih bilgisinden çıkarılan yıl değeri.",
    "AY": "Tarih bilgisinden çıkarılan ay numarası (1-12).",
    "MAL_TURU": "Ürünün ana kategori/tür bilgisi (standartlaştırılmış büyük harf).",
    "MAL_ADI": "Haldeki ürün adı (standartlaştırılmış büyük harf).",
    "BIRIM": "Ürünün fiyatlandırma birimi (KG, ADET, BAĞ vb.).",
    "REEL_ORTALAMA_UCRET": (
        "TÜFE ile enflasyondan arındırılmış reel ortalama fiyat."
    ),
    "REEL_LAG_1": (
        "Aynı ürün ve birimde bir önceki kayıttaki reel ortalama fiyat (1"
        " dönem gecikme)."
    ),
    "REEL_LAG_7": (
        "Aynı ürün ve birimde 7 kayıt önceki reel ortalama fiyat (7 dönem"
        " gecikme)."
    ),
    "REEL_LAG_30": (
        "Aynı ürün ve birimde 30 kayıt önceki reel ortalama fiyat (30 dönem"
        " gecikme)."
    ),
    "REEL_DEGISIM_YUZDE": (
        "Bir önceki kayda göre reel fiyattaki yüzde değişim oranı."
    ),
    "REEL_OYNAKLIK_7": (
        "Aynı ürün ve birimde son 7 kayıttaki reel fiyatın standart sapması"
        " (kısa dönem oynaklık)."
    ),
    "REEL_OYNAKLIK_30": (
        "Aynı ürün ve birimde son 30 kayıttaki reel fiyatın standart sapması"
        " (orta dönem oynaklık)."
    ),
}

satirlar = []
for sutun in df.columns:
  ornek = (
      df[sutun].dropna().iloc[0] if not df[sutun].dropna().empty else np.nan
  )
  satirlar.append({
      "DEGISKEN_ADI": sutun,
      "VERI_TIPI": str(df[sutun].dtype),
      "EKSIK_DEGER_SAYISI": int(df[sutun].isna().sum()),
      "ORNEK_DEGER": ornek,
      "ACIKLAMA": aciklamalar.get(
          sutun, "Analiz sürecinde kullanılan veya türetilen değişken."
      ),
  })

sozluk_df = pd.DataFrame(satirlar)
xlsx_yolu = veri_klasoru / "veri_sozlugu.xlsx"

try:
  sozluk_df.to_excel(xlsx_yolu, index=False)
  print("Tamamlandı:", xlsx_yolu)
except ModuleNotFoundError:
  csv_yedek = veri_klasoru / "veri_sozlugu.csv"
  sozluk_df.to_csv(csv_yedek, index=False)
  print("openpyxl bulunamadı, CSV kaydedildi:", csv_yedek)