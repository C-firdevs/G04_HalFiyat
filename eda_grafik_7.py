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

df = pd.read_csv(veri_klasoru / "hal_reel_don_ozellikli.csv")

don_ozet = (
    df.dropna(subset=["DON_VAR_MI", "REEL_ORTALAMA_UCRET"])
    .groupby("DON_VAR_MI", as_index=False)["REEL_ORTALAMA_UCRET"]
    .mean()
)

etiket_map = {0: "Don Yok (0)", 1: "Don Var (1)"}
don_ozet["DURUM"] = don_ozet["DON_VAR_MI"].map(etiket_map)

plt.figure(figsize=(8, 5))
plt.bar(don_ozet["DURUM"], don_ozet["REEL_ORTALAMA_UCRET"])
plt.title("İzmir Don Durumuna Göre Ortalama Reel Fiyat (<= 0°C)")
plt.xlabel("Don Durumu")
plt.ylabel("Ortalama Reel Fiyat")
plt.grid(True, axis="y", alpha=0.3)
plt.tight_layout()

cikti = grafik_klasoru / "grafik_7_don_etkisi_reel_fiyat.png"
plt.savefig(cikti, dpi=150)
print("Kaydedildi:", cikti)