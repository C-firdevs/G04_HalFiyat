import pandas as pd

df = pd.read_csv(
    "01_Veri/temiz_hal_fiyatlari.csv", encoding="utf-8-sig", low_memory=False
)
ilk_25_listesi = pd.read_csv("01_Veri/ilk_25_urun.csv", encoding="utf-8-sig")[
    "MAL_ADI"
].tolist()
df = df[df["MAL_ADI"].isin(ilk_25_listesi)]
df["TARIH"] = pd.to_datetime(df["TARIH"], errors="coerce")
df["AY"] = df["TARIH"].dt.month

aylik = (
    df.groupby(["MAL_ADI", "AY"])["ORTALAMA_UCRET"]
    .mean()
    .round(2)
    .reset_index(name="AYLIK_ORT_FIYAT")
)

genel_ort = (
    df.groupby("MAL_ADI")["ORTALAMA_UCRET"]
    .mean()
    .round(2)
    .reset_index(name="GENEL_ORT_FIYAT")
)

karar_df = aylik.merge(genel_ort, on="MAL_ADI")
karar_df["DURUM"] = karar_df.apply(
    lambda r: (
        "UYGUN DONEM"
        if r["AYLIK_ORT_FIYAT"] < r["GENEL_ORT_FIYAT"] * 0.9
        else ("PAHALI DONEM" if r["AYLIK_ORT_FIYAT"] > r["GENEL_ORT_FIYAT"] * 1.1 else "NORMAL")
    ),
    axis=1,
)

karar_df.to_csv(
    "01_Veri/aylik_satinalma_karar.csv", index=False, encoding="utf-8-sig"
)
print("Karar tablosu kaydedildi. İlk 10 satır:")
print(karar_df.head(10))
