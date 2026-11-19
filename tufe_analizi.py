from pathlib import Path
import pandas as pd

ana_dizin = Path(__file__).resolve().parent
veri_klasoru = ana_dizin / "01_Veri"

df_25_liste = pd.read_csv(veri_klasoru / "ilk_25_urun.csv")
df_tufe = pd.read_csv(veri_klasoru / "tufe_temiz.csv")
df_hal = pd.read_csv(veri_klasoru / "temiz_hal_fiyatlari.csv")

# 1. İlk 25 ürünü filtrele
secili_urunler = df_25_liste["MAL_ADI"].dropna().unique()
df_hal_25 = df_hal[df_hal["MAL_ADI"].isin(secili_urunler)].copy()

# 2. Birim yazımlarını standartlaştır (boşluk temizliği + büyük harf)
if "BIRIM" in df_hal_25.columns:
    df_hal_25["BIRIM"] = (
        df_hal_25["BIRIM"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

if "MAL_TURU" in df_hal_25.columns:
    df_hal_25["MAL_TURU"] = df_hal_25["MAL_TURU"].astype(str).str.strip().str.upper()

if "MAL_ADI" in df_hal_25.columns:
    df_hal_25["MAL_ADI"] = df_hal_25["MAL_ADI"].astype(str).str.strip().str.upper()

# 3. Tarihten YIL ve AY çıkarıp TÜFE ile birleştir
tarih_dt = pd.to_datetime(df_hal_25["TARIH"], errors="coerce")
df_hal_25["YIL"] = tarih_dt.dt.year
df_hal_25["AY"] = tarih_dt.dt.month

df_birlesik = df_hal_25.merge(df_tufe, on=["YIL", "AY"], how="left")

# 4. Baz TÜFE ve reel ortalama ücreti hesapla
gecerli_tufe = df_birlesik.dropna(subset=["TUFE"]).sort_values(["YIL", "AY"])
baz_tufe = float(gecerli_tufe["TUFE"].iloc[-1])

df_birlesik["REEL_ORTALAMA_UCRET"] = (
    df_birlesik["ORTALAMA_UCRET"] * (baz_tufe / df_birlesik["TUFE"])
).round(2)

df_birlesik.to_csv(veri_klasoru / "hal_reel_fiyatli.csv", index=False)

# 5. Standartlaştırılmış birimlere göre özet tablo üret
grup_kolonlari = [c for c in ["MAL_TURU", "MAL_ADI", "BIRIM"] if c in df_birlesik.columns]
ozet_25 = (
    df_birlesik.groupby(grup_kolonlari, as_index=False)
    .agg(
        KAYIT=("REEL_ORTALAMA_UCRET", "count"),
        NOMINAL_ORT=("ORTALAMA_UCRET", "mean"),
        REEL_ORT=("REEL_ORTALAMA_UCRET", "mean"),
        REEL_MIN=("REEL_ORTALAMA_UCRET", "min"),
        REEL_MAX=("REEL_ORTALAMA_UCRET", "max"),
    )
    .round(2)
    .sort_values("REEL_ORT", ascending=False)
)

ozet_25.to_csv(veri_klasoru / "ilk_25_reel_ozet.csv", index=False)

print("Benzersiz birim listesi:", sorted(df_birlesik["BIRIM"].dropna().unique().tolist()) if "BIRIM" in df_birlesik.columns else [])
print("\nStandartlaştırılmış ilk 25 ürün reel fiyat özeti:")
print(ozet_25.to_string(index=False))