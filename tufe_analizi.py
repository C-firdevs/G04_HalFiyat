from pathlib import Path
import pandas as pd

ana_dizin = Path(__file__).resolve().parent
veri_klasoru = ana_dizin / "01_Veri"

df_tufe = pd.read_csv(veri_klasoru / "tufe_temiz.csv")

df_hal = None
secilen_dosya = None
for aday in ["ilk_25_urun.csv", "temiz_hal_fiyatlari.csv"]:
    yol = veri_klasoru / aday
    if yol.exists():
        tmp = pd.read_csv(yol)
        print(f"{aday} -> sütunlar: {tmp.columns.tolist()} | şekil: {tmp.shape}")
        if "TARIH" in tmp.columns and "ORTALAMA_UCRET" in tmp.columns:
            df_hal = tmp
            secilen_dosya = aday
            break

if df_hal is None:
    print("Uyarı: TARIH ve ORTALAMA_UCRET sütunlarına sahip dosya bulunamadı.")
    raise SystemExit

print(f"\nKullanılan dosya: {secilen_dosya}")

tarih_dt = pd.to_datetime(df_hal["TARIH"], errors="coerce")
df_hal["YIL"] = tarih_dt.dt.year
df_hal["AY"] = tarih_dt.dt.month

df_birlesik = df_hal.merge(df_tufe, on=["YIL", "AY"], how="left")

# En çok kaydı olan ilk 25 ürünü seç ve filtrele
secili_25_urun = df_birlesik["MAL_ADI"].value_counts().head(25).index
df_birlesik = df_birlesik[df_birlesik["MAL_ADI"].isin(secili_25_urun)].copy()

gecerli_tufe = df_birlesik.dropna(subset=["TUFE"]).sort_values(["YIL", "AY"])
baz_tufe = float(gecerli_tufe["TUFE"].iloc[-1])
baz_yil = int(gecerli_tufe["YIL"].iloc[-1])
baz_ay = int(gecerli_tufe["AY"].iloc[-1])

df_birlesik["REEL_ORTALAMA_UCRET"] = (
    df_birlesik["ORTALAMA_UCRET"] * (baz_tufe / df_birlesik["TUFE"])
).round(2)

cikti_yolu = veri_klasoru / "hal_reel_fiyatli.csv"
df_birlesik.to_csv(cikti_yolu, index=False)

print("Benzersiz ürün sayısı:", df_birlesik["MAL_ADI"].nunique())
print("İlk 25 ürün:", list(secili_25_urun))
print(f"Baz dönem: {baz_yil}-{baz_ay:02d} (Baz TÜFE: {baz_tufe})")
print(
    df_birlesik[["TARIH", "MAL_ADI", "ORTALAMA_UCRET", "TUFE", "REEL_ORTALAMA_UCRET"]]
    .head(10)
    .to_string(index=False)
)