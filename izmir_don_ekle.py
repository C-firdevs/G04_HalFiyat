from pathlib import Path
import pandas as pd
import requests


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

# Ana veri dosyasını bul
aday_dosyalar = [
    veri_klasoru / "hal_reel_ozellikli.csv",
    veri_klasoru / "temiz_hal_fiyatlari.csv",
    veri_klasoru / "ornek_veri.csv",
]
girdi_dosyasi = next((p for p in aday_dosyalar if p.exists()), None)
if girdi_dosyasi is None:
  raise FileNotFoundError("Birleştirilecek ana CSV dosyası bulunamadı.")

df = pd.read_csv(girdi_dosyasi)

# Tarih sütununu bul ve normalize et
tarih_kolonu = next(
    (c for c in ["TARIH", "tarih", "DATE", "date"] if c in df.columns), None
)
if tarih_kolonu is None:
  raise ValueError("Veri setinde tarih sütunu bulunamadı.")

df["_TARIH_GUN"] = pd.to_datetime(
    df[tarih_kolonu], errors="coerce"
).dt.normalize()
gecerli_tarihler = df["_TARIH_GUN"].dropna()
if gecerli_tarihler.empty:
  raise ValueError("Geçerli tarih değeri bulunamadı.")

baslangic_tarih = gecerli_tarihler.min().strftime("%Y-%m-%d")
bitis_tarih = gecerli_tarihler.max().strftime("%Y-%m-%d")

# Open-Meteo Archive API üzerinden İzmir günlük minimum sıcaklık verisi
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 38.4237,
    "longitude": 27.1428,
    "start_date": baslangic_tarih,
    "end_date": bitis_tarih,
    "daily": "temperature_2m_min",
    "timezone": "Europe/Istanbul",
}

response = requests.get(url, params=params, timeout=60)
response.raise_for_status()
payload = response.json()

daily = payload.get("daily", {})
don_df = pd.DataFrame({
    "_TARIH_GUN": pd.to_datetime(daily.get("time", []), errors="coerce"),
    "IZMIR_MIN_SICAKLIK_C": daily.get("temperature_2m_min", []),
})

don_df["_TARIH_GUN"] = don_df["_TARIH_GUN"].dt.normalize()
# 0 °C ve altı meteorolojik don; 2 °C ve altı hafif/zirai don riski eşiği
don_df["DON_VAR_MI"] = (don_df["IZMIR_MIN_SICAKLIK_C"] <= 0.0).astype(int)
don_df["HAFIF_DON_RISKI"] = (don_df["IZMIR_MIN_SICAKLIK_C"] <= 2.0).astype(int)

# Mevcut sütunlar varsa çakışmayı önlemek için düşür
birlesik = df.drop(
    columns=[
        c
        for c in ["IZMIR_MIN_SICAKLIK_C", "DON_VAR_MI", "HAFIF_DON_RISKI"]
        if c in df.columns
    ]
).merge(
    don_df[
        [
            "_TARIH_GUN",
            "IZMIR_MIN_SICAKLIK_C",
            "DON_VAR_MI",
            "HAFIF_DON_RISKI",
        ]
    ],
    on="_TARIH_GUN",
    how="left",
)
birlesik = birlesik.drop(columns=["_TARIH_GUN"])

cikti_dosyasi = veri_klasoru / "hal_reel_don_ozellikli.csv"
birlesik.to_csv(cikti_dosyasi, index=False)

print("Kaydedildi:", cikti_dosyasi)
print("Donlu kayıt sayısı (<= 0°C):", int(birlesik["DON_VAR_MI"].sum()))
print(
    "Hafif don riskli kayıt sayısı (<= 2°C):",
    int(birlesik["HAFIF_DON_RISKI"].sum()),
)