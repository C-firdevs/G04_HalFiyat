from pathlib import Path
import pandas as pd

dosya_klasoru = Path(__file__).resolve().parent
veri_klasoru = dosya_klasoru if dosya_klasoru.name == "01_Veri" else dosya_klasoru / "01_Veri"
veri_klasoru.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(veri_klasoru / "hal_reel_fiyatli.csv")

if "YIL" not in df.columns or "AY" not in df.columns:
    tarih_dt = pd.to_datetime(df["TARIH"], errors="coerce")
    df["YIL"] = tarih_dt.dt.year
    df["AY"] = tarih_dt.dt.month

for col in ["MAL_TURU", "MAL_ADI", "BIRIM"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.upper()

mevsim_haritasi = {
    12: "Kış", 1: "Kış", 2: "Kış",
    3: "İlkbahar", 4: "İlkbahar", 5: "İlkbahar",
    6: "Yaz", 7: "Yaz", 8: "Yaz",
    9: "Sonbahar", 10: "Sonbahar", 11: "Sonbahar",
}
ay_adlari = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
    5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
    9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
}

df["MEVSIM"] = df["AY"].map(mevsim_haritasi)
df["AY_ADI"] = df["AY"].map(ay_adlari)

aylik_ozet = (
    df.groupby(["MAL_ADI", "BIRIM", "AY", "AY_ADI", "MEVSIM"], as_index=False)["REEL_ORTALAMA_UCRET"]
    .mean()
    .round(2)
    .rename(columns={"REEL_ORTALAMA_UCRET": "AYLIK_REEL_ORT"})
)
aylik_ozet.to_csv(veri_klasoru / "ilk_25_aylik_reel_fiyat.csv", index=False)

mevsim_pivot = (
    df.pivot_table(
        index=["MAL_ADI", "BIRIM"],
        columns="MEVSIM",
        values="REEL_ORTALAMA_UCRET",
        aggfunc="mean",
    )
    .round(2)
)

mevsim_sirasi = [m for m in ["Kış", "İlkbahar", "Yaz", "Sonbahar"] if m in mevsim_pivot.columns]
mevsim_pivot = mevsim_pivot[mevsim_sirasi]

en_ucuz_ay = (
    aylik_ozet.sort_values(["AYLIK_REEL_ORT", "AY"])
    .groupby(["MAL_ADI", "BIRIM"], as_index=False)
    .first()[["MAL_ADI", "BIRIM", "AY_ADI", "AYLIK_REEL_ORT"]]
    .rename(columns={"AY_ADI": "EN_UCUZ_AY", "AYLIK_REEL_ORT": "EN_UCUZ_REEL"})
)

en_pahali_ay = (
    aylik_ozet.sort_values(["AYLIK_REEL_ORT", "AY"], ascending=[False, True])
    .groupby(["MAL_ADI", "BIRIM"], as_index=False)
    .first()[["MAL_ADI", "BIRIM", "AY_ADI", "AYLIK_REEL_ORT"]]
    .rename(columns={"AY_ADI": "EN_PAHALI_AY", "AYLIK_REEL_ORT": "EN_PAHALI_REEL"})
)

mevsim_ozet = (
    mevsim_pivot.reset_index()
    .merge(en_ucuz_ay, on=["MAL_ADI", "BIRIM"], how="left")
    .merge(en_pahali_ay, on=["MAL_ADI", "BIRIM"], how="left")
)
mevsim_ozet["MEVSIMSEL_FARK"] = (mevsim_ozet["EN_PAHALI_REEL"] - mevsim_ozet["EN_UCUZ_REEL"]).round(2)
mevsim_ozet = mevsim_ozet.sort_values("MEVSIMSEL_FARK", ascending=False).reset_index(drop=True)

mevsim_ozet.to_csv(veri_klasoru / "ilk_25_mevsimsel_reel_ozet.csv", index=False)

print("Kaydedilen dosyalar:")
print("-", veri_klasoru / "ilk_25_aylik_reel_fiyat.csv")
print("-", veri_klasoru / "ilk_25_mevsimsel_reel_ozet.csv")
print("\nİlk 25 ürün mevsimsel reel fiyat özeti:")
print(mevsim_ozet.to_string(index=False))