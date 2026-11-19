import pandas as pd

df = pd.read_csv(
    "01_Veri/temiz_hal_fiyatlari.csv", encoding="utf-8-sig", low_memory=False
)
ilk_25_listesi = pd.read_csv("01_Veri/ilk_25_urun.csv", encoding="utf-8-sig")[
    "MAL_ADI"
].tolist()
df = df[df["MAL_ADI"].isin(ilk_25_listesi)]

df["TARIH"] = pd.to_datetime(df["TARIH"], errors="coerce")
df["GUN"] = df["TARIH"].dt.date

gunluk = (
    df.groupby(["MAL_ADI", "GUN"])["ORTALAMA_UCRET"]
    .mean()
    .round(2)
    .reset_index(name="GUNLUK_ORT_FIYAT")
)

genel_ort = (
    df.groupby("MAL_ADI")["ORTALAMA_UCRET"]
    .mean()
    .round(2)
    .reset_index(name="GENEL_ORT_FIYAT")
)

gunluk_karar = gunluk.merge(genel_ort, on="MAL_ADI")
gunluk_karar["DURUM"] = gunluk_karar.apply(
    lambda r: (
        "UYGUN GUN"
        if r["GUNLUK_ORT_FIYAT"] < r["GENEL_ORT_FIYAT"] * 0.9
        else ("PAHALI GUN" if r["GUNLUK_ORT_FIYAT"] > r["GENEL_ORT_FIYAT"] * 1.1 else "NORMAL")
    ),
    axis=1,
)

gunluk_karar.to_csv(
    "01_Veri/gunluk_satinalma_karar.csv", index=False, encoding="utf-8-sig"
)
print(
    "Günlük karar tablosu kaydedildi. Satır sayısı:",
    len(gunluk_karar),
)
print(gunluk_karar.head(10))