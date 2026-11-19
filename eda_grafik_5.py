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

en_pahali = (
    df.dropna(subset=["MAL_ADI", "REEL_ORTALAMA_UCRET"])
    .groupby("MAL_ADI", as_index=False)["REEL_ORTALAMA_UCRET"]
    .mean()
    .sort_values("REEL_ORTALAMA_UCRET", ascending=False)
    .head(10)
    .sort_values("REEL_ORTALAMA_UCRET", ascending=True)
)

plt.figure(figsize=(10, 5))
plt.barh(en_pahali["MAL_ADI"], en_pahali["REEL_ORTALAMA_UCRET"])
plt.title("Ortalama Reel Fiyatı En Yüksek İlk 10 Ürün")
plt.xlabel("Ortalama Reel Fiyat")
plt.ylabel("Ürün")
plt.grid(True, axis="x", alpha=0.3)
plt.tight_layout()

cikti = grafik_klasoru / "grafik_5_en_yuksek_reel_fiyat_urunler.png"
plt.savefig(cikti, dpi=150)
print("Kaydedildi:", cikti)