from datetime import datetime
import pandas as pd
import requests

KAYNAK = (
    "İzmir Büyükşehir Belediyesi Açık Veri Portalı - Sebze ve Meyve Hal"
    " Fiyatları"
)
CEKME_TARIHI = datetime.now().strftime("%Y-%m-%d")
LISANS = "İzmir Büyükşehir Belediyesi Açık Veri Lisansı"

dataset_id = "39f883f1-5627-4ec0-b424-8f65baf01969"
show_url = "https://acikveri.bizizmir.com/api/3/action/package_show"

resp = requests.get(show_url, params={"id": dataset_id}, timeout=30)
resp.raise_for_status()
resources = resp.json()["result"]["resources"]

csv_resources = [
    r for r in resources if str(r.get("format", "")).upper() == "CSV"
]

parcalar = []
for r in csv_resources:
  ad = r.get("name", "adsiz")
  url = r.get("url")
  try:
    df_parca = pd.read_csv(url, sep=";")
    df_parca["kaynak_dosya"] = ad
    parcalar.append(df_parca)
  except Exception as e:
    print(f"HATA -> {ad} | {e}")

ham_df = pd.concat(parcalar, ignore_index=True)

print(f"Kaynak: {KAYNAK} | Çekme Tarihi: {CEKME_TARIHI} | Lisans: {LISANS}")
print("Düzgün ayrılmış tablo boyutu (satır, sütun):", ham_df.shape)
print("Sütunlar:", list(ham_df.columns))
print("\nİlk 5 satır:")
print(ham_df.head(5))
print("\nEn çok geçen ilk 25 ürün (MAL_ADI):")
print(ham_df["MAL_ADI"].value_counts().head(25))
ham_df.to_csv("01_Veri/ham_hal_fiyatlari.csv", index=False, encoding="utf-8-sig")
ilk_25 = ham_df["MAL_ADI"].value_counts().head(25).reset_index()
ilk_25.columns = ["MAL_ADI", "ADET"]
ilk_25.to_csv("01_Veri/ilk_25_urun.csv", index=False, encoding="utf-8-sig")