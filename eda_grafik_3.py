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
df["AY"] = df["TARIH_DT"].dt.month

ay_isimleri = {
    1: "Oca",
    2: "Şub",
    3: "Mar",
    4: "Nis",
    5: "May",
    6: "Haz",
    7: "Tem",
    8: "Ağu",
    9: "Eyl",
    10: "Eki",
    11: "Kas",
    12: "Ara",
}

aylik = (
    df.groupby("AY", as_index=False)["REEL_ORTALAMA_UCRET"]
    .mean()
    .sort_values("AY")
)
aylik["AY_ADI"] = aylik["AY"].map(ay_isimleri)

plt.figure(figsize=(10, 5))
plt.plot(
    aylik["AY_ADI"], aylik["REEL_ORTALAMA_UCRET"], marker="o", linewidth=2
)
plt.title("Aylara Göre Ortalama Reel Fiyat (Mevsimsel Profil)")
plt.xlabel("Ay")
plt.ylabel("Ortalama Reel Fiyat")
plt.grid(True, alpha=0.3)
plt.tight_layout()

cikti = grafik_klasoru / "grafik_3_aylik_mevsimsel_reel.png"
plt.savefig(cikti, dpi=150)
print("Kaydedildi:", cikti)