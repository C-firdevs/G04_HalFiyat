from pathlib import Path
import pandas as pd


def veri_klasoru_bul(baslangic: Path) -> Path:
  for aday in [baslangic] + list(baslangic.parents):
    if aday.name == "01_Veri":
      return aday
    hedef = aday / "01_Veri"
    if hedef.exists() and hedef.is_dir():
      return hedef
  raise FileNotFoundError("'01_Veri' klasörü bulunamadı.")


veri_klasoru = veri_klasoru_bul(Path(__file__).resolve().parent)
df = pd.read_csv(veri_klasoru / "hal_reel_ozellikli.csv")

ornek_yolu = veri_klasoru / "ornek_veri.csv"
df.head(100).to_csv(ornek_yolu, index=False)
print("Tamamlandı:", ornek_yolu)