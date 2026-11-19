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

if "MAL_TURU" in df.columns:
  tur_ozet = (
      df.dropna(subset=["MAL_TURU", "REEL_ORTALAMA_UCRET"])
      .groupby("MAL_TURU", as_index=False)["REEL_ORTALAMA_UCRET"]
      .mean()
      .sort_values("REEL_ORTALAMA_UCRET", ascending=True)
  )

  plt.figure(figsize=(10, 5))
  plt.barh(tur_ozet["MAL_TURU"], tur_ozet["REEL_ORTALAMA_UCRET"])
  plt.title("Mal Türüne Göre Ortalama Reel Fiyat")
  plt.xlabel("Ortalama Reel Fiyat")
  plt.ylabel("Mal Türü")
  plt.grid(True, axis="x", alpha=0.3)
  plt.tight_layout()

  cikti = grafik_klasoru / "grafik_4_mal_turu_reel_fiyat.png"
  plt.savefig(cikti, dpi=150)
  print("Kaydedildi:", cikti)
else:
  print("MAL_TURU sütunu bulunamadı.")