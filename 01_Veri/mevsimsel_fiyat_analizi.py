import pandas as pd

df = pd.read_csv(
    "01_Veri/temiz_hal_fiyatlari.csv", encoding="utf-8-sig", low_memory=False
)
ilk_25_listesi = pd.read_csv("01_Veri/ilk_25_urun.csv", encoding="utf-8-sig")[
    "MAL_ADI"
].tolist()
df = df[df["MAL_ADI"].isin(ilk_25_listesi)].copy()

df["TARIH"] = pd.to_datetime(df["TARIH"], errors="coerce")
df["AY"] = df["TARIH"].dt.month


def mevsim_bul(ay):
  if ay in [3, 4, 5]:
    return "Ilkbahar"
  elif ay in [6, 7, 8]:
    return "Yaz"
  elif ay in [9, 10, 11]:
    return "Sonbahar"
  else:
    return "Kis"


df["MEVSIM"] = df["AY"].apply(mevsim_bul)

mevsimsel = (
    df.groupby(["MAL_ADI", "MEVSIM"])["ORTALAMA_UCRET"]
    .agg(
        MIN_FIYAT="min",
        ORT_FIYAT="mean",
        MAX_FIYAT="max",
        KAYIT_SAYISI="count",
    )
    .reset_index()
)

mevsimsel["ORT_FIYAT"] = mevsimsel["ORT_FIYAT"].round(2)

genel_ort = (
    df.groupby("MAL_ADI")["ORTALAMA_UCRET"]
    .mean()
    .round(2)
    .reset_index(name="GENEL_ORT_FIYAT")
)

mevsimsel_karar = mevsimsel.merge(genel_ort, on="MAL_ADI")
mevsimsel_karar["FIYAT_SKALASI"] = (
    mevsimsel_karar["MIN_FIYAT"].astype(str)
    + " - "
    + mevsimsel_karar["MAX_FIYAT"].astype(str)
)
mevsimsel_karar["DURUM"] = mevsimsel_karar.apply(
    lambda r: (
        "UYGUN MEVSIM"
        if r["ORT_FIYAT"] < r["GENEL_ORT_FIYAT"] * 0.9
        else (
            "PAHALI MEVSIM"
            if r["ORT_FIYAT"] > r["GENEL_ORT_FIYAT"] * 1.1
            else "NORMAL"
        )
    ),
    axis=1,
)

mevsim_sirasi = ["Ilkbahar", "Yaz", "Sonbahar", "Kis"]
mevsimsel_karar["MEVSIM"] = pd.Categorical(
    mevsimsel_karar["MEVSIM"], categories=mevsim_sirasi, ordered=True
)
mevsimsel_karar = mevsimsel_karar.sort_values(
    ["MAL_ADI", "MEVSIM"]
).reset_index(drop=True)

mevsimsel_karar.to_csv(
    "01_Veri/mevsimsel_satinalma_karar.csv", index=False, encoding="utf-8-sig"
)

print(
    "Mevsimsel karar tablosu kaydedildi. Satır sayısı:",
    len(mevsimsel_karar),
)
print(
    mevsimsel_karar[[
        "MAL_ADI",
        "MEVSIM",
        "MIN_FIYAT",
        "ORT_FIYAT",
        "MAX_FIYAT",
        "FIYAT_SKALASI",
        "DURUM",
    ]].head(12)
)