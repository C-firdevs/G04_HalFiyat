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

df["TARIH_DT"] = pd.to_datetime(df["TARIH"], errors="coerce")
df = df.dropna(subset=["TARIH_DT", "REEL_ORTALAMA_UCRET"]).copy()
df["DONEM"] = df["TARIH_DT"].dt.to_period("M").dt.to_timestamp()

nominal_kolon = None
for aday in ["ORTALAMA_UCRET", "NOMINAL_FIYAT", "FIYAT", "ORTALAMA_FIYAT"]:
  if aday in df.columns:
    nominal_kolon = aday
    break

ozet = df.groupby("DONEM", as_index=False)["REEL_ORTALAMA_UCRET"].mean()
if nominal_kolon:
  nom_ozet = df.groupby("DONEM", as_index=False)[nominal_kolon].mean()
  ozet = ozet.merge(nom_ozet, on="DONEM", how="left")

plt.figure(figsize=(10, 5))
if nominal_kolon:
  plt.plot(
      ozet["DONEM"], ozet[nominal_kolon], label="Nominal Ortalama", linewidth=2
  )
plt.plot(
    ozet["DONEM"],
    ozet["REEL_ORTALAMA_UCRET"],
    label="Reel Ortalama (TÜFE Bazlı)",
    linewidth=2,
)
plt.title("Dönemsel Ortalama Fiyat: Nominal vs. Reel")
plt.xlabel("Dönem")
plt.ylabel("Fiyat")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

cikti = grafik_klasoru / "grafik_1_nominal_vs_reel.png"
plt.savefig(cikti, dpi=150)
print("Kaydedildi:", cikti)