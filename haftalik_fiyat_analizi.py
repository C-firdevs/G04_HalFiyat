import pandas as pd

df = pd.read_csv(
    "01_Veri/temiz_hal_fiyatlari.csv", encoding="utf-8-sig", low_memory=False
)
ilk_25_listesi = pd.read_csv("01_Veri/ilk_25_urun.csv", encoding="utf-8-sig")[
    "MAL_ADI"
].tolist()
df = df[df["MAL_ADI"].isin(ilk_25_listesi)]

df["TARIH"] = pd.to_datetime(df["TARIH"], errors="coerce")
df["HAFTA"] = df["TARIH"].dt.to_period("W").apply(lambda r: r.start_time.date())

haftalik = (
    df.groupby(["MAL_ADI", "HAFTA"])["ORTALAMA_UCRET"]
    .mean()
    .round(2)
    .reset_index(name="HAFTALIK_ORT_FIYAT")
)

genel_ort = (
    df.groupby("MAL_ADI")["ORTALAMA_UCRET"]
    .mean()
    .round(2)
    .reset_index(name="GENEL_ORT_FIYAT")
)

haftalik_karar = haftalik.merge(genel_ort, on="MAL_ADI")
haftalik_karar["DURUM"] = haftalik_karar.apply(
    lambda r: (
        "UYGUN HAFTA"
        if r["HAFTALIK_ORT_FIYAT"] < r["GENEL_ORT_FIYAT"] * 0.9
        else (
            "PAHALI HAFTA"
            if r["HAFTALIK_ORT_FIYAT"] > r["GENEL_ORT_FIYAT"] * 1.1
            else "NORMAL"
        )
    ),
    axis=1,
)

haftalik_karar.to_csv(
    "01_Veri/haftalik_satinalma_karar.csv", index=False, encoding="utf-8-sig"
)
print(
    "Haftalık karar tablosu kaydedildi. Satır sayısı:",
    len(haftalik_karar),
)
print(haftalik_karar.head(10))