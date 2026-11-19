import pandas as pd

df = pd.read_csv(
    "01_Veri/temiz_hal_fiyatlari.csv", encoding="utf-8-sig", low_memory=False
)
df["TARIH"] = pd.to_datetime(df["TARIH"], errors="coerce")

urun_ozeti = (
    df.groupby("MAL_ADI")
    .agg(
        KAYIT_SAYISI=("ORTALAMA_UCRET", "count"),
        MIN_ORT_FIYAT=("ORTALAMA_UCRET", "min"),
        ORTALAMA_FIYAT=("ORTALAMA_UCRET", "mean"),
        MAX_ORT_FIYAT=("ORTALAMA_UCRET", "max"),
    )
    .sort_values("KAYIT_SAYISI", ascending=False)
    .reset_index()
)

urun_ozeti["ORTALAMA_FIYAT"] = urun_ozeti["ORTALAMA_FIYAT"].round(2)
urun_ozeti.to_csv(
    "01_Veri/urun_fiyat_ozeti.csv", index=False, encoding="utf-8-sig"
)

print("En çok kaydı olan ilk 10 ürünün fiyat özeti:")
print(urun_ozeti.head(10))