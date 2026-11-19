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

if "REEL_DEGISIM_YUZDE" in df.columns:
  degisim = df["REEL_DEGISIM_YUZDE"].dropna()
  # Uç değerlerin histogramı ezmemesi için 1. ve 99. yüzdelik aralığı
  alt, ust = degisim.quantile(0.01), degisim.quantile(0.99)
  filtreli = degisim[(degisim >= alt) & (degisim <= ust)]

  plt.figure(figsize=(10, 5))
  plt.hist(filtreli, bins=40)
  plt.axvline(0, linestyle="--", linewidth=1.5)
  plt.title("Dönemsel Reel Fiyat Değişim Yüzdesi Dağılımı (%1-%99 Aralığı)")
  plt.xlabel("Reel Fiyat Değişimi (%)")
  plt.ylabel("Kayıt Sayısı")
  plt.grid(True, alpha=0.3)
  plt.tight_layout()

  cikti = grafik_klasoru / "grafik_6_reel_degisim_dagilimi.png"
  plt.savefig(cikti, dpi=150)
  print("Kaydedildi:", cikti)
else:
  print("REEL_DEGISIM_YUZDE sütunu bulunamadı.")