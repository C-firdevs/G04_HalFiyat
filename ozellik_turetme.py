from pathlib import Path
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
df = pd.read_csv(veri_klasoru / "hal_reel_fiyatli.csv")

for col in ["MAL_TURU", "MAL_ADI", "BIRIM"]:
  if col in df.columns:
    df[col] = df[col].astype(str).str.strip().str.upper()

df["TARIH_DT"] = pd.to_datetime(df["TARIH"], errors="coerce")
grup = [c for c in ["MAL_ADI", "BIRIM"] if c in df.columns]
df = df.sort_values(grup + ["TARIH_DT"]).reset_index(drop=True)

hedef = "REEL_ORTALAMA_UCRET"

# Gecikmeli değişkenler (1, 7, 30 dönem)
for adim in [1, 7, 30]:
  df[f"REEL_LAG_{adim}"] = df.groupby(grup)[hedef].shift(adim).round(2)

# Fiyat oynaklığı (yüzde değişim ve 7-30 dönemlik standart sapma)
df["REEL_DEGISIM_YUZDE"] = df.groupby(grup)[hedef].pct_change().mul(100).round(2)
for pencere in [7, 30]:
  df[f"REEL_OYNAKLIK_{pencere}"] = (
      df.groupby(grup)[hedef]
      .rolling(pencere, min_periods=2)
      .std()
      .reset_index(level=list(range(len(grup))), drop=True)
      .round(2)
  )

df.drop(columns=["TARIH_DT"]).to_csv(
    veri_klasoru / "hal_reel_ozellikli.csv", index=False
)
print("Tamamlandı: hal_reel_ozellikli.csv")