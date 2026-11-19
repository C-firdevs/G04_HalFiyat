import pandas as pd

df = pd.read_csv("01_Veri/ham_hal_fiyatlari.csv", encoding="utf-8-sig")
df["TARIH"] = pd.to_datetime(df["TARIH"], errors="coerce")
df["MAL_ADI"] = df["MAL_ADI"].astype(str).str.strip()
df["MAL_TURU"] = df["MAL_TURU"].astype(str).str.strip()

for col in ["AZAMI_UCRET", "ORTALAMA_UCRET"]:
  if col in df.columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["TARIH", "MAL_ADI", "ORTALAMA_UCRET"])
df = df[df["ORTALAMA_UCRET"] > 0]
df = df.drop_duplicates()

df.to_csv("01_Veri/temiz_hal_fiyatlari.csv", index=False, encoding="utf-8-sig")
print("Temiz veri kaydedildi. Boyut:", df.shape)