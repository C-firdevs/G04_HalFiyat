from pathlib import Path
import pandas as pd


def veri_klasoru_bul(baslangic: Path) -> Path:
  for aday in [baslangic] + list(baslangic.parents):
    if aday.name == "01_Veri":
      return aday
    hedef = aday / "01_Veri"
    if hedef.exists() and hedef.is_dir():
      return hedef
  raise FileNotFoundError(
      "'01_Veri' klasörü bulunamadı. Lütfen proje klasörü içinde çalıştırın."
  )


karar_klasoru = Path(__file__).resolve().parent
karar_klasoru.mkdir(parents=True, exist_ok=True)
veri_klasoru = veri_klasoru_bul(karar_klasoru)

aylik_df = pd.read_csv(veri_klasoru / "ilk_25_aylik_reel_fiyat.csv")
mevsim_df = pd.read_csv(veri_klasoru / "ilk_25_mevsimsel_reel_ozet.csv")

mevsim_kolonlari = [
    m for m in ["Kış", "İlkbahar", "Yaz", "Sonbahar"] if m in mevsim_df.columns
]

if mevsim_kolonlari:
  mevsim_uzun = mevsim_df.melt(
      id_vars=["MAL_ADI", "BIRIM"],
      value_vars=mevsim_kolonlari,
      var_name="MEVSIM",
      value_name="MEVSIM_REEL_ORT",
  ).dropna(subset=["MEVSIM_REEL_ORT"])

  en_ucuz_mevsim = (
      mevsim_uzun.sort_values(["MEVSIM_REEL_ORT", "MEVSIM"])
      .groupby(["MAL_ADI", "BIRIM"], as_index=False)
      .first()[["MAL_ADI", "BIRIM", "MEVSIM", "MEVSIM_REEL_ORT"]]
      .rename(
          columns={
              "MEVSIM": "EN_UYGUN_MEVSIM",
              "MEVSIM_REEL_ORT": "EN_UYGUN_MEVSIM_ORT",
          }
      )
  )

  en_pahali_mevsim = (
      mevsim_uzun.sort_values(
          ["MEVSIM_REEL_ORT", "MEVSIM"], ascending=[False, True]
      )
      .groupby(["MAL_ADI", "BIRIM"], as_index=False)
      .first()[["MAL_ADI", "BIRIM", "MEVSIM", "MEVSIM_REEL_ORT"]]
      .rename(
          columns={
              "MEVSIM": "EN_PAHALI_MEVSIM",
              "MEVSIM_REEL_ORT": "EN_PAHALI_REEL_ORT",
          }
      )
  )
else:
  en_ucuz_mevsim = pd.DataFrame(
      columns=["MAL_ADI", "BIRIM", "EN_UYGUN_MEVSIM", "EN_UYGUN_MEVSIM_ORT"]
  )
  en_pahali_mevsim = pd.DataFrame(
      columns=["MAL_ADI", "BIRIM", "EN_PAHALI_MEVSIM", "EN_PAHALI_REEL_ORT"]
  )

yillik_reel_ort = (
    aylik_df.groupby(["MAL_ADI", "BIRIM"], as_index=False)["AYLIK_REEL_ORT"]
    .mean()
    .round(2)
    .rename(columns={"AYLIK_REEL_ORT": "YILLIK_REEL_ORT"})
)

karar_df = (
    mevsim_df[[
        "MAL_ADI",
        "BIRIM",
        "EN_UCUZ_AY",
        "EN_UCUZ_REEL",
        "EN_PAHALI_AY",
        "EN_PAHALI_REEL",
        "MEVSIMSEL_FARK",
    ]]
    .merge(en_ucuz_mevsim, on=["MAL_ADI", "BIRIM"], how="left")
    .merge(en_pahali_mevsim, on=["MAL_ADI", "BIRIM"], how="left")
    .merge(yillik_reel_ort, on=["MAL_ADI", "BIRIM"], how="left")
)

karar_df["FARK_YUZDE"] = (
    (karar_df["MEVSIMSEL_FARK"] / karar_df["EN_UCUZ_REEL"]) * 100
).round(1)

karar_df["KARAR_NOTU"] = (
    karar_df["EN_UCUZ_AY"].astype(str)
    + " ("
    + karar_df["EN_UYGUN_MEVSIM"].astype(str)
    + ") alim icin uygun; "
    + karar_df["EN_PAHALI_AY"].astype(str)
    + " ("
    + karar_df["EN_PAHALI_MEVSIM"].astype(str)
    + ") en yuksek reel seviye"
)

karar_df = karar_df.sort_values("MEVSIMSEL_FARK", ascending=False).reset_index(
    drop=True
)

cikti_yolu = karar_klasoru / "ilk_25_reel_karar_destegi.csv"
karar_df.to_csv(cikti_yolu, index=False)

print("Karar çıktı dosyası:", cikti_yolu)
print(
    karar_df[[
        "MAL_ADI",
        "BIRIM",
        "EN_UYGUN_MEVSIM",
        "EN_UCUZ_AY",
        "EN_UCUZ_REEL",
        "EN_PAHALI_AY",
        "EN_PAHALI_REEL",
        "MEVSIMSEL_FARK",
        "FARK_YUZDE",
    ]].to_string(index=False)
)