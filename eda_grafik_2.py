from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def veri_klasoru_bul(baslangic: Path) -> Path:
  for aday in [baslangic] + list(baslangic.parents):
    if aday.name == "01_Veri":
      return aday
    hedef = aday / "01_Veri"
    if hedef.exists() and hedef.is_dir():
      return hedef
  raise FileNotFoundError("'01_Veri' klasörü bulunamadı.")


ana_dizin = Path(__file__).resolve().parent
veri_klasoru = veri_klasoru_bul(ana_dizin)
grafik_klasoru = ana_dizin / "03_Grafikler"
grafik_klasoru.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(veri_klasoru / "hal_reel_ozellikli.csv")

oynaklik_kolonu = None
for aday in ["REEL_OYNAKLIK_30", "REEL_OYNAKLIK_7", "REEL_DEGISIM_YUZDE"]:
  if aday in df.columns:
    oynaklik_kolonu = aday
    break

if oynaklik_kolonu is None:
  raise ValueError("Oynaklık sütunu bulunamadı.")

if oynaklik_kolonu == "REEL_DEGISIM_YUZDE":
  df["_OYNAKLIK_METRIK"] = df[oynaklik_kolonu].abs()
else:
  df["_OYNAKLIK_METRIK"] = df[oynaklik_kolonu]

en_oynak = (
    df.dropna(subset=["MAL_ADI", "_OYNAKLIK_METRIK"])
    .groupby("MAL_ADI", as_index=False)["_OYNAKLIK_METRIK"]
    .mean()
    .sort_values("_OYNAKLIK_METRIK", ascending=False)
    .head(10)
    .sort_values("_OYNAKLIK_METRIK", ascending=True)
)

plt.figure(figsize=(10, 5))
plt.barh(en_oynak["MAL_ADI"], en_oynak["_OYNAKLIK_METRIK"])
plt.title(f"En Yüksek Reel Fiyat Oynaklığına Sahip İlk 10 Ürün ({oynaklik_kolonu})")
plt.xlabel("Ortalama Oynaklık Değeri")
plt.ylabel("Ürün")
plt.grid(True, axis="x", alpha=0.3)
plt.tight_layout()

cikti = grafik_klasoru / "grafik_2_en_oynak_urunler.png"
plt.savefig(cikti, dpi=150)
print("Kaydedildi:", cikti)