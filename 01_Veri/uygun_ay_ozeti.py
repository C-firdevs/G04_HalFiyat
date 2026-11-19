import pandas as pd

karar_df = pd.read_csv(
    "01_Veri/aylik_satinalma_karar.csv", encoding="utf-8-sig"
)

ozet_satirlari = []

for urun, grup in karar_df.groupby("MAL_ADI"):
  uygun_aylar = (
      grup[grup["DURUM"] == "UYGUN DONEM"]["AY"]
      .sort_values()
      .astype(str)
      .tolist()
  )
  pahali_aylar = (
      grup[grup["DURUM"] == "PAHALI DONEM"]["AY"]
      .sort_values()
      .astype(str)
      .tolist()
  )
  en_ucuz_satir = grup.loc[grup["AYLIK_ORT_FIYAT"].idxmin()]
  en_pahali_satir = grup.loc[grup["AYLIK_ORT_FIYAT"].idxmax()]

  ozet_satirlari.append({
      "MAL_ADI": urun,
      "GENEL_ORT_FIYAT": en_ucuz_satir["GENEL_ORT_FIYAT"],
      "EN_UCUZ_AY": int(en_ucuz_satir["AY"]),
      "EN_UCUZ_FIYAT": en_ucuz_satir["AYLIK_ORT_FIYAT"],
      "EN_PAHALI_AY": int(en_pahali_satir["AY"]),
      "EN_PAHALI_FIYAT": en_pahali_satir["AYLIK_ORT_FIYAT"],
      "UYGUN_AYLAR": ", ".join(uygun_aylar) if uygun_aylar else "-",
      "PAHALI_AYLAR": ", ".join(pahali_aylar) if pahali_aylar else "-",
  })

ozet_df = pd.DataFrame(ozet_satirlari).sort_values("MAL_ADI")
ozet_df.to_csv(
    "01_Veri/urun_uygun_ay_ozeti.csv", index=False, encoding="utf-8-sig"
)

print("Ürün bazlı uygun/pahalı ay özeti kaydedildi. Satır sayısı:", len(ozet_df))
print(ozet_df.head(10))