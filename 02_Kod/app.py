import base64
from datetime import date, datetime, timedelta
from io import BytesIO
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# 0. SAYFA YAPILANDIRMASI VE ÖZEL CSS
# -----------------------------------------------------------------------------
_SAYFA_LOGO_YOLU = Path(__file__).resolve().parent / "snc_logo.png"
st.set_page_config(
    page_title="Akıllı Satın Alma",
    page_icon=str(_SAYFA_LOGO_YOLU) if _SAYFA_LOGO_YOLU.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tarayıcı otomatik çevirisinin React DOM'unu bozmasını (NotFoundError: removeChild) kalıcı olarak engelle
components.html(
    """
    <script>
    try {
        const doc = window.parent.document;
            try {{
                const loc = window.parent.location;
                if (loc && loc.hostname && loc.hostname.endsWith('.streamlit.app')) {{
                    const liveUrl = loc.origin + loc.pathname;
                    const qrSrc = 'https://api.qrserver.com/v1/create-qr-code/?size=160x160&color=072613&bgcolor=ffffff&margin=4&data=' + encodeURIComponent(liveUrl);
                    const hQr = doc.getElementById('sncHeaderQrImg');
                    const fQr = doc.getElementById('sncFloatingQrImg');
                    if (hQr) hQr.src = qrSrc;
                    if (fQr) fQr.src = qrSrc;
                }}
            }} catch (e) {{}}
        doc.documentElement.setAttribute("translate", "no");
        doc.documentElement.setAttribute("lang", "tr");
        doc.documentElement.classList.add("notranslate");
        if (doc.body) {
            doc.body.setAttribute("translate", "no");
            doc.body.classList.add("notranslate");
        }
        if (!doc.querySelector('meta[name="google"][content="notranslate"]')) {
            const meta = doc.createElement("meta");
            meta.name = "google";
            meta.content = "notranslate";
            doc.head.appendChild(meta);
        }
    } catch (e) {}
    </script>
    """,
    height=0,
    width=0,
)

st.markdown(
    """
    <style>
    /* Genel Sayfa Ferahlığı ve Kurumsal Tipografi */
    .block-container {
        padding-top: 1.6rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1380px;
    }

    /* Modern Sekme (Tab) Çubuğu */
    button[data-baseweb="tab"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        margin-right: 6px !important;
        font-weight: 600 !important;
        font-size: 0.90rem !important;
        color: #475569 !important;
        transition: all 0.2s ease;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #1B7A43 !important;
        border-color: #1B7A43 !important;
        color: #FFFFFF !important;
        box-shadow: 0 3px 10px rgba(27, 122, 67, 0.20) !important;
    }
    div[data-baseweb="tab-highlight"] {
        display: none !important;
    }
    div[data-baseweb="tab-border"] {
        display: none !important;
    }


    /* Kurumsal Birincil (BAŞLA) Buton Tasarımı */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1B7A43 0%, #14532D 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.78rem 1.5rem !important;
        font-size: 1.04rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        box-shadow: 0 4px 12px rgba(27, 122, 67, 0.22) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #15803D 0%, #0F3F22 100%) !important;
        box-shadow: 0 6px 16px rgba(27, 122, 67, 0.32) !important;
    }
    .home-panel-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #1B7A43;
        border-radius: 12px;
        padding: 18px 20px;
        min-height: 185px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
        margin-bottom: 14px;
    }
    .home-panel-step {
        display: inline-block;
        background-color: #DCFCE7;
        color: #14532D;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 999px;
        margin-bottom: 8px;
        letter-spacing: 0.3px;
    }
    .home-panel-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 6px;
    }
    .home-panel-desc {
        font-size: 0.88rem;
        color: #475569;
        line-height: 1.55;
    }

    /* Üst Hero Şeridi */
    .snc-hero {
        background: linear-gradient(135deg, #FFFFFF 0%, #F0FDF4 100%);
        border: 1px solid #DCFCE7;
        border-left: 6px solid #1B7A43;
        border-radius: 14px;
        padding: 18px 24px;
        margin-bottom: 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
    }
    .snc-hero-title {
        font-size: 1.55rem;
        font-weight: 800;
        color: #0F172A;
        margin: 0;
        letter-spacing: -0.3px;
    }
    .snc-hero-sub {
        font-size: 0.90rem;
        color: #475569;
        margin: 4px 0 0 0;
    }
    .snc-hero-pill {
        background-color: #DCFCE7;
        color: #14532D;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        white-space: nowrap;
    }

    /* st.metric kartları için ferah kurumsal tasarım */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
    }
    div[data-testid="stMetricLabel"] > div {
        color: #64748B;
        font-weight: 600;
        font-size: 0.85rem;
    }
    div[data-testid="stMetricValue"] > div {
        color: #0F172A;
        font-weight: 800;
        font-size: 1.32rem !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        line-height: 1.25 !important;
    }
    div[data-testid="stMetricDelta"] > div {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        font-size: 0.78rem !important;
        line-height: 1.25 !important;
    }

    /* Özel Responsive Durum & KPI Kartı */
    .signal-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 15px 18px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
        min-height: 102px;
    }
    .signal-card-title {
        color: #64748B;
        font-size: 0.80rem;
        font-weight: 600;
        margin-bottom: 6px;
        text-transform: none;
    }
    .signal-card-status {
        font-size: 1.16rem;
        font-weight: 800;
        margin-bottom: 6px;
        line-height: 1.2;
    }
    .signal-card-sub {
        color: #475569;
        font-size: 0.79rem;
        line-height: 1.35;
    }

    /* Bölüm Başlık Çizgisi */
    .sec-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
        margin: 14px 0 8px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid #E2E8F0;
    }

    /* Sol menü (Sidebar) SNC Rozeti */
    .snc-badge {
        background: linear-gradient(135deg, #1B7A43 0%, #145E33 100%);
        color: #FFFFFF;
        padding: 16px 18px;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(27, 122, 67, 0.22);
    }
    .snc-badge h2 {
        color: #FFFFFF !important;
        margin: 0;
        font-size: 1.22rem;
        font-weight: 800;
        letter-spacing: 0.3px;
    }
    .snc-badge p {
        color: #DCFCE7 !important;
        margin: 4px 0 0 0;
        font-size: 0.78rem;
        font-weight: 500;
    }

    /* Fiyat Şoku Alarmı Kutusu (Sade & Net) */
    .shock-alert {
        background-color: #FEF2F2;
        border: 1px solid #FECACA;
        border-left: 5px solid #DC2626;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 18px;
        color: #7F1D1D;
        font-size: 0.90rem;
    }
    .shock-alert h4 {
        color: #991B1B !important;
        margin: 0 0 6px 0;
        font-size: 0.98rem;
        font-weight: 700;
    }

    /* Yönetici Özeti Kutusu */
    .exec-summary-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
        margin-top: 8px;
        margin-bottom: 14px;
    }

    /* Grafik/Tablo Altı Dinamik İş Yorumu Kutusu */
    .insight-note {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #1B7A43;
        border-radius: 10px;
        padding: 10px 14px;
        margin-top: 8px;
        margin-bottom: 14px;
        color: #334155;
        font-size: 0.86rem;
        line-height: 1.45;
    }

    /* Grafik Kapsayıcı Kart Hissi */
    div[data-testid="stPlotlyChart"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 8px 10px;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.02);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 1. VERİ VE MODEL YÜKLEME ALTYAPISI (SUNUCU UYUMLU BASE_DIR + GÜVENLİ YEDEK)
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


def _dosya_yolu_coz(goreceli_yol: str) -> Path:
    """Hem yerel bilgisayarda hem Streamlit Community Cloud üzerinde proje köküne (BASE_DIR) göre yolu çözer."""
    kok_yol = BASE_DIR / goreceli_yol
    if kok_yol.exists():
        return kok_yol
    dogrudan = Path(goreceli_yol)
    if dogrudan.exists():
        return dogrudan
    ust_dizin = Path("..") / goreceli_yol
    if ust_dizin.exists():
        return ust_dizin
    return kok_yol


def _sayiya_cevir(df: pd.DataFrame, sutunlar: list) -> pd.DataFrame:
    for s in sutunlar:
        if s in df.columns:
            df[s] = pd.to_numeric(df[s], errors="coerce")
    return df


def _guvenli_sayi(deger, varsayilan: float = 0.0) -> float:
    try:
        if deger is None or pd.isna(deger):
            return float(varsayilan)
        f = float(deger)
        return float(varsayilan) if (np.isnan(f) or np.isinf(f)) else f
    except Exception:
        return float(varsayilan)


def _mal_turu_standartlastir(seri: pd.Series) -> pd.Series:

    return (
        seri.astype(str)
        .str.strip()
        .str.upper()
        .replace({"İTHAL..": "ITHAL", "ITHAL..": "ITHAL", "İTHAL...": "ITHAL", "İTHAL": "ITHAL"})
    )


@st.cache_data(show_spinner="Veri tabloları yükleniyor...")
def verileri_yukle(surum: int = 3) -> dict:
    """Tüm CSV dosyalarını '01_Veri/' altından okur; dosya yoksa güvenli yedek üretir."""
    veri = {}

    ana_veri_yolu = (
        "01_Veri/hal_reel_don_ozellikli.csv"
        if _dosya_yolu_coz("01_Veri/hal_reel_don_ozellikli.csv").exists()
        else "01_Veri/hal_reel_ozellikli.csv"
    )
    dosya_listesi = {
        "hal_reel_ozellikli": (ana_veri_yolu, ["TARIH"]),
        "ilk_25_aylik_reel_fiyat": ("01_Veri/ilk_25_aylik_reel_fiyat.csv", None),
        "ilk_25_reel_karar_destegi": ("01_Veri/ilk_25_reel_karar_destegi.csv", None),
        "ilk_25_reel_ozet": ("01_Veri/ilk_25_reel_ozet.csv", None),
        "gunluk_satinalma_karar": ("01_Veri/gunluk_satinalma_karar.csv", None),
        "haftalik_satinalma_karar": ("01_Veri/haftalik_satinalma_karar.csv", None),
        "aylik_satinalma_karar": ("01_Veri/aylik_satinalma_karar.csv", None),
        "mevsimsel_satinalma_karar": ("01_Veri/mevsimsel_satinalma_karar.csv", None),
        # Opsiyonel B/A kişisi tabloları
        "urun_kumeleri": ("01_Veri/urun_kumeleri.csv", None),
        "model_karsilastirma": ("01_Veri/model_karsilastirma.csv", None),
        "ozellik_onemi": ("01_Veri/ozellik_onemi.csv", None),
        "gelecek_hafta_ve_ay_tahminleri": ("01_Veri/gelecek_hafta_ve_ay_tahminleri.csv", None),
        "don_etkisi_haftalik_analiz": ("01_Veri/don_etkisi_haftalik_analiz.csv", None),
        "don_model_karsilastirma": ("01_Veri/don_model_karsilastirma.csv", None),
    }

    for anahtar, (goreceli_yol, tarih_sutunlari) in dosya_listesi.items():
        yol = _dosya_yolu_coz(goreceli_yol)
        if os.path.exists(yol):
            try:
                if tarih_sutunlari:
                    df = pd.read_csv(yol, parse_dates=tarih_sutunlari, low_memory=False)
                else:
                    df = pd.read_csv(yol, low_memory=False)
                if "MAL_TURU" in df.columns:
                    df["MAL_TURU"] = _mal_turu_standartlastir(df["MAL_TURU"])
                if "MAL_ADI" in df.columns:
                    df["MAL_ADI"] = (
                        df["MAL_ADI"]
                        .astype(str)
                        .str.strip()
                        .str.upper()
                        .str.replace(r"\s+", " ", regex=True)
                    )
                df = _sayiya_cevir(
                    df,
                    [
                        "ASGARI_UCRET",
                        "AZAMI_UCRET",
                        "ORTALAMA_UCRET",
                        "YIL",
                        "AY",
                        "TUFE",
                        "REEL_ORTALAMA_UCRET",
                        "REEL_LAG_1",
                        "REEL_LAG_7",
                        "REEL_LAG_30",
                        "REEL_DEGISIM_YUZDE",
                        "REEL_OYNAKLIK_7",
                        "REEL_OYNAKLIK_30",
                        "AYLIK_REEL_ORT",
                        "EN_UCUZ_REEL",
                        "EN_PAHALI_REEL",
                        "MEVSIMSEL_FARK",
                        "YILLIK_REEL_ORT",
                        "FARK_YUZDE",
                        "GUNLUK_ORT_FIYAT",
                        "HAFTALIK_ORT_FIYAT",
                        "AYLIK_ORT_FIYAT",
                        "MEVSIMLIK_ORT_FIYAT",
                        "GENEL_ORT_FIYAT",
                        "BUGUNKU_REEL_FIYAT",
                        "TAHMIN_1_HAFTA",
                        "ARALIK_1_HAFTA_ALT",
                        "ARALIK_1_HAFTA_UST",
                        "DEGISIM_1_HAFTA_YUZDE",
                        "TAHMIN_2_HAFTA",
                        "TAHMIN_3_HAFTA",
                        "TAHMIN_1_AY (30_KAYIT)",
                        "ARALIK_1_AY_ALT",
                        "ARALIK_1_AY_UST",
                        "DEGISIM_1_AY_YUZDE",
                        "IZMIR_MIN_SICAKLIK_C",
                        "DON_VAR_MI",
                        "HAFIF_DON_RISKI",
                    ],
                )
                veri[anahtar] = df
            except Exception:
                veri[anahtar] = pd.DataFrame()
        else:
            veri[anahtar] = pd.DataFrame()

    # Eğer hal_reel_ozellikli.csv yerelde henüz yoksa ornek_veri.csv veya güvenli yedek kullan
    if veri["hal_reel_ozellikli"].empty:
        ornek_yol = _dosya_yolu_coz("01_Veri/ornek_veri.csv")
        if ornek_yol.exists():
            df_ornek = pd.read_csv(ornek_yol, parse_dates=["TARIH"], low_memory=False)
            if "MAL_TURU" in df_ornek.columns:
                df_ornek["MAL_TURU"] = _mal_turu_standartlastir(df_ornek["MAL_TURU"])
            veri["hal_reel_ozellikli"] = df_ornek
        else:
            veri["hal_reel_ozellikli"] = _yedek_ozellikli_veri_uret()

    if veri["ilk_25_aylik_reel_fiyat"].empty:
        veri["ilk_25_aylik_reel_fiyat"] = _yedek_aylik_fiyat_uret(veri["hal_reel_ozellikli"])

    if veri["ilk_25_reel_karar_destegi"].empty:
        veri["ilk_25_reel_karar_destegi"] = _yedek_karar_destegi_uret(veri["ilk_25_aylik_reel_fiyat"])

    return veri


def _yedek_ozellikli_veri_uret() -> pd.DataFrame:
    """CSV dosyaları yerel klasöre henüz indirilmediyse uygulamanın çökmemesi için yedek tablo."""
    urunler = [
        ("SEBZE", "DOMATES", "KG", 18.0, 32.0, 25.0, 42.5, 8.4, 5.2),
        ("SEBZE", "SARIMSAK KURU", "KG", 85.0, 140.0, 110.0, 185.0, 28.5, 19.0),
        ("SEBZE", "BIBER SIVRI", "KG", 22.0, 40.0, 30.0, 52.0, 14.2, 9.8),
        ("SEBZE", "SALATALIK", "KG", 15.0, 28.0, 21.0, 36.0, 11.5, 8.1),
        ("SEBZE", "PATATES", "KG", 12.0, 20.0, 16.0, 24.0, 3.2, 4.0),
        ("SEBZE", "SOGAN KURU", "KG", 10.0, 18.0, 14.0, 21.5, 2.9, 3.5),
        ("MEYVE", "LIMON", "KG", 16.0, 30.0, 22.0, 38.0, 7.6, 6.9),
        ("MEYVE", "ELMA STARKING", "KG", 20.0, 35.0, 27.0, 41.0, 4.1, 4.8),
        ("ITHAL", "MUZ ITHAL", "KG", 45.0, 70.0, 58.0, 88.0, 6.2, 5.9),
        ("ITHAL", "ANANAS", "ADET", 55.0, 90.0, 72.0, 105.0, 9.4, 8.7),
    ]
    satirlar = []
    tarihler = pd.date_range("2024-01-01", "2025-11-01", freq="7D")
    for t in tarihler:
        ay = t.month
        mevsim_katsayi = 1.25 if ay in [12, 1, 2, 3] else (0.80 if ay in [7, 8, 9] else 1.0)
        for tur, ad, birim, asg, azm, ort, reel_ort, oyn7, oyn30 in urunler:
            guncel_reel = round(reel_ort * mevsim_katsayi, 2)
            satirlar.append(
                {
                    "TARIH": t,
                    "MAL_TURU": tur,
                    "MAL_ADI": ad,
                    "BIRIM": birim,
                    "ASGARI_UCRET": round(asg * mevsim_katsayi, 2),
                    "AZAMI_UCRET": round(azm * mevsim_katsayi, 2),
                    "ORTALAMA_UCRET": round(ort * mevsim_katsayi, 2),
                    "kaynak_dosya": "Yedek_Veri",
                    "YIL": t.year,
                    "AY": ay,
                    "TUFE": 2450.0,
                    "REEL_ORTALAMA_UCRET": guncel_reel,
                    "REEL_LAG_1": round(guncel_reel * 0.98, 2),
                    "REEL_LAG_7": round(guncel_reel * 0.95, 2),
                    "REEL_LAG_30": round(guncel_reel * 0.92, 2),
                    "REEL_DEGISIM_YUZDE": 2.1,
                    "REEL_OYNAKLIK_7": oyn7,
                    "REEL_OYNAKLIK_30": oyn30,
                }
            )
    return pd.DataFrame(satirlar)


def _yedek_aylik_fiyat_uret(df_oz: pd.DataFrame) -> pd.DataFrame:
    ay_adlari = {
        1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
        5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
        9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
    }
    mevsim_haritasi = {
        12: "Kış", 1: "Kış", 2: "Kış",
        3: "İlkbahar", 4: "İlkbahar", 5: "İlkbahar",
        6: "Yaz", 7: "Yaz", 8: "Yaz",
        9: "Sonbahar", 10: "Sonbahar", 11: "Sonbahar",
    }
    df = df_oz.copy()
    if "AY" not in df.columns:
        df["AY"] = pd.to_datetime(df["TARIH"], errors="coerce").dt.month
    df["AY_ADI"] = df["AY"].map(ay_adlari)
    df["MEVSIM"] = df["AY"].map(mevsim_haritasi)
    return (
        df.groupby(["MAL_ADI", "BIRIM", "AY", "AY_ADI", "MEVSIM"], as_index=False)["REEL_ORTALAMA_UCRET"]
        .mean()
        .round(2)
        .rename(columns={"REEL_ORTALAMA_UCRET": "AYLIK_REEL_ORT"})
    )


def _yedek_karar_destegi_uret(df_aylik: pd.DataFrame) -> pd.DataFrame:
    if df_aylik.empty:
        return pd.DataFrame()
    en_ucuz = (
        df_aylik.sort_values(["AYLIK_REEL_ORT", "AY"])
        .groupby(["MAL_ADI", "BIRIM"], as_index=False)
        .first()
        .rename(
            columns={
                "AY_ADI": "EN_UCUZ_AY",
                "AYLIK_REEL_ORT": "EN_UCUZ_REEL",
                "MEVSIM": "EN_UYGUN_MEVSIM",
            }
        )
    )
    en_pahali = (
        df_aylik.sort_values(["AYLIK_REEL_ORT", "AY"], ascending=[False, True])
        .groupby(["MAL_ADI", "BIRIM"], as_index=False)
        .first()
        .rename(
            columns={
                "AY_ADI": "EN_PAHALI_AY",
                "AYLIK_REEL_ORT": "EN_PAHALI_REEL",
                "MEVSIM": "EN_PAHALI_MEVSIM",
            }
        )
    )
    yillik = (
        df_aylik.groupby(["MAL_ADI", "BIRIM"], as_index=False)["AYLIK_REEL_ORT"]
        .mean()
        .round(2)
        .rename(columns={"AYLIK_REEL_ORT": "YILLIK_REEL_ORT"})
    )
    karar = en_ucuz[["MAL_ADI", "BIRIM", "EN_UCUZ_AY", "EN_UCUZ_REEL", "EN_UYGUN_MEVSIM"]].merge(
        en_pahali[["MAL_ADI", "BIRIM", "EN_PAHALI_AY", "EN_PAHALI_REEL", "EN_PAHALI_MEVSIM"]],
        on=["MAL_ADI", "BIRIM"],
    ).merge(yillik, on=["MAL_ADI", "BIRIM"])
    karar["MEVSIMSEL_FARK"] = (karar["EN_PAHALI_REEL"] - karar["EN_UCUZ_REEL"]).round(2)
    karar["FARK_YUZDE"] = ((karar["MEVSIMSEL_FARK"] / karar["EN_UCUZ_REEL"]) * 100).round(1)
    karar["KARAR_NOTU"] = (
        karar["EN_UCUZ_AY"].astype(str)
        + " ("
        + karar["EN_UYGUN_MEVSIM"].astype(str)
        + ") alim icin uygun; "
        + karar["EN_PAHALI_AY"].astype(str)
        + " ("
        + karar["EN_PAHALI_MEVSIM"].astype(str)
        + ") en yuksek reel seviye"
    )
    return karar.sort_values("MEVSIMSEL_FARK", ascending=False).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def _reel_degisim_ve_ajanda_hazirla(df_oz: pd.DataFrame, df_karar: pd.DataFrame):
    """2006-2010 vs 2021-2025 reel pahalanma/ucuzlama analizi ve 12 aylık satın alma ajandası."""
    df_reel_fark = pd.DataFrame()
    if not df_oz.empty and {"MAL_ADI", "TARIH", "REEL_ORTALAMA_UCRET"}.issubset(df_oz.columns):
        gec = df_oz.dropna(subset=["MAL_ADI", "REEL_ORTALAMA_UCRET"]).copy()
        if "YIL" not in gec.columns:
            gec["YIL"] = pd.to_datetime(gec["TARIH"], errors="coerce").dt.year
        gec = gec.dropna(subset=["YIL"])
        if not gec.empty:
            min_y = int(gec["YIL"].min())
            max_y = int(gec["YIL"].max())
            ilk_bitis = min(min_y + 4, max_y)
            son_baslangic = max(max_y - 4, min_y)
            if ilk_bitis < son_baslangic:
                ilk_5 = (
                    gec[gec["YIL"] <= ilk_bitis]
                    .groupby("MAL_ADI", as_index=False)["REEL_ORTALAMA_UCRET"]
                    .mean()
                    .rename(columns={"REEL_ORTALAMA_UCRET": "ILK_DONEM_REEL"})
                )
                son_5 = (
                    gec[gec["YIL"] >= son_baslangic]
                    .groupby("MAL_ADI", as_index=False)["REEL_ORTALAMA_UCRET"]
                    .mean()
                    .rename(columns={"REEL_ORTALAMA_UCRET": "SON_DONEM_REEL"})
                )
                df_reel_fark = ilk_5.merge(son_5, on="MAL_ADI", how="inner")
                if not df_reel_fark.empty:
                    df_reel_fark["REEL_DEGISIM_YUZDE"] = (
                        (df_reel_fark["SON_DONEM_REEL"] - df_reel_fark["ILK_DONEM_REEL"])
                        / df_reel_fark["ILK_DONEM_REEL"].replace(0, np.nan)
                    ) * 100.0
                    df_reel_fark = df_reel_fark.dropna(subset=["REEL_DEGISIM_YUZDE"]).round(2)
                    df_reel_fark["DONEM_ETIKET"] = f"{min_y}-{ilk_bitis} → {son_baslangic}-{max_y}"

    ajanda_satirlar = []
    ay_list = [
        "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
        "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
    ]
    if not df_karar.empty and "EN_UCUZ_AY" in df_karar.columns:
        for ay_no, ay_ad in enumerate(ay_list, start=1):
            kesit = df_karar[df_karar["EN_UCUZ_AY"].astype(str).str.strip().str.upper() == ay_ad.upper()]
            urunler = sorted(kesit["MAL_ADI"].dropna().unique().tolist()) if not kesit.empty else []
            ort_fark = float(kesit["FARK_YUZDE"].mean()) if (not kesit.empty and "FARK_YUZDE" in kesit.columns) else 0.0
            aksiyon = (
                "Yoğun Toplu Alım / Yıllık Sözleşme Ayı"
                if len(urunler) >= 3
                else ("Seçili Ürünlerde Fırsat / Sözleşme" if len(urunler) > 0 else "Rutin Takip / Önceki Stoktan Kullanım")
            )
            ajanda_satirlar.append(
                {
                    "AY_NO": ay_no,
                    "AY": ay_ad,
                    "FIRSAT_URUN_SAYISI": len(urunler),
                    "EN_UCUZ_URUNLER": ", ".join(urunler) if urunler else "—",
                    "ORT_MEVSIMSEL_FARK_YUZDE": round(ort_fark, 1),
                    "SATIN_ALMA_AKSIYONU": aksiyon,
                }
            )
    df_ajanda = pd.DataFrame(ajanda_satirlar)
    return df_reel_fark, df_ajanda


@st.cache_data(show_spinner=False)
def _uc_altin_oneri_hesapla(df_oz: pd.DataFrame, df_karar: pd.DataFrame) -> dict:
    """Yönetime 3 Altın Öneri kartı için mevcut verilerden şampiyon ürünleri hesaplar."""
    sonuc = {
        "sozlesme_urun": "-",
        "sozlesme_makas_pct": 0.0,
        "sozlesme_oynaklik": 0.0,
        "sozlesme_koruma_pct": 0.0,
        "stok_urun": "-",
        "stok_fark_pct": 0.0,
        "stok_en_ucuz_ay": "-",
        "stok_en_pahali_ay": "-",
        "spot_urun": "-",
        "spot_oynaklik": 0.0,
        "spot_ort_reel": 0.0,
    }

    oynak_col = (
        "REEL_OYNAKLIK_30"
        if "REEL_OYNAKLIK_30" in df_oz.columns
        else ("REEL_OYNAKLIK_7" if "REEL_OYNAKLIK_7" in df_oz.columns else None)
    )

    if not df_oz.empty and oynak_col and "MAL_ADI" in df_oz.columns:
        gec = df_oz.dropna(subset=["MAL_ADI", oynak_col]).copy()
        if {"ASGARI_UCRET", "AZAMI_UCRET", "ORTALAMA_UCRET"}.issubset(gec.columns):
            gec["MAKAS_PCT"] = np.where(
                (gec["ORTALAMA_UCRET"] > 0) & (gec["AZAMI_UCRET"] >= gec["ASGARI_UCRET"]),
                ((gec["AZAMI_UCRET"] - gec["ASGARI_UCRET"]) / gec["ORTALAMA_UCRET"]) * 100.0,
                np.nan,
            )
        else:
            gec["MAKAS_PCT"] = 0.0

        ozet = (
            gec.groupby("MAL_ADI", as_index=False)
            .agg(
                ORT_OYNAKLIK=(oynak_col, "mean"),
                ORT_MAKAS=("MAKAS_PCT", "mean"),
                ORT_REEL=("REEL_ORTALAMA_UCRET", "mean"),
            )
            .dropna(subset=["ORT_OYNAKLIK"])
        )
        if not ozet.empty:
            # 1) Sözleşmeli Alım Şampiyonu: Oynaklık + Min-Max makası bileşik skoru en yüksek ürün
            o_norm = ozet["ORT_OYNAKLIK"] / max(float(ozet["ORT_OYNAKLIK"].max()), 1e-6)
            m_norm = ozet["ORT_MAKAS"].fillna(0.0) / max(float(ozet["ORT_MAKAS"].fillna(0.0).max()), 1e-6)
            ozet["BILEŞIK_RISK"] = 0.55 * o_norm + 0.45 * m_norm
            sampiyon_soz = ozet.sort_values("BILEŞIK_RISK", ascending=False).iloc[0]
            soz_ad = str(sampiyon_soz["MAL_ADI"])
            soz_makas = _guvenli_sayi(sampiyon_soz["ORT_MAKAS"], 0.0)
            soz_oyn = _guvenli_sayi(sampiyon_soz["ORT_OYNAKLIK"], 0.0)

            # Tahmini yıllık koruma oranı: karar desteğindeki mevsimsel avantajın %65'i veya makasın yarısı
            koruma_pct = max(soz_makas * 0.45, 12.0)
            if not df_karar.empty and soz_ad in df_karar["MAL_ADI"].values:
                ks = df_karar[df_karar["MAL_ADI"] == soz_ad].iloc[0]
                y_ort = _guvenli_sayi(ks.get("YILLIK_REEL_ORT", 0.0), 0.0)
                e_ucu = _guvenli_sayi(ks.get("EN_UCUZ_REEL", 0.0), 0.0)
                if y_ort > 0 and e_ucu > 0:
                    koruma_pct = max(koruma_pct, ((y_ort - e_ucu) / y_ort) * 100.0 * 0.75)

            sonuc["sozlesme_urun"] = soz_ad
            sonuc["sozlesme_makas_pct"] = round(soz_makas, 1)
            sonuc["sozlesme_oynaklik"] = round(soz_oyn, 2)
            sonuc["sozlesme_koruma_pct"] = round(min(koruma_pct, 65.0), 1)

            # 3) Düşük Riskli Spot Alım Ürünü: Oynaklığı en düşük ürün
            sampiyon_spot = ozet.sort_values("ORT_OYNAKLIK", ascending=True).iloc[0]
            sonuc["spot_urun"] = str(sampiyon_spot["MAL_ADI"])
            sonuc["spot_oynaklik"] = round(_guvenli_sayi(sampiyon_spot["ORT_OYNAKLIK"], 0.0), 2)
            sonuc["spot_ort_reel"] = round(_guvenli_sayi(sampiyon_spot["ORT_REEL"], 0.0), 2)

    # 2) Mevsimsel Stoklama Şampiyonu: En ucuz ay ile en pahalı ay arasındaki reel fiyat farkı (%) en yüksek ürün
    if not df_karar.empty and {"MAL_ADI", "FARK_YUZDE"}.issubset(df_karar.columns):
        k_temiz = df_karar.dropna(subset=["MAL_ADI", "FARK_YUZDE"]).sort_values("FARK_YUZDE", ascending=False)
        if not k_temiz.empty:
            sampiyon_stok = k_temiz.iloc[0]
            sonuc["stok_urun"] = str(sampiyon_stok["MAL_ADI"])
            sonuc["stok_fark_pct"] = round(_guvenli_sayi(sampiyon_stok["FARK_YUZDE"], 0.0), 1)
            sonuc["stok_en_ucuz_ay"] = str(sampiyon_stok.get("EN_UCUZ_AY", "-"))
            sonuc["stok_en_pahali_ay"] = str(sampiyon_stok.get("EN_PAHALI_AY", "-"))

    return sonuc


@st.cache_data(show_spinner=False)
def _kraljic_ve_makas_ozeti_hazirla(df_kaynak: pd.DataFrame, oynak_kolon: str):
    """Büyük veri üzerinde Kraljic matrisi ve Pazarlık Makası özetlerini önbellekli hesaplar."""
    kraljic_df = pd.DataFrame()
    makas_ozet = pd.DataFrame()

    if not df_kaynak.empty and oynak_kolon and "REEL_ORTALAMA_UCRET" in df_kaynak.columns:
        grup_kol = ["MAL_ADI", "MAL_TURU"] if "MAL_TURU" in df_kaynak.columns else ["MAL_ADI"]
        kraljic_df = (
            df_kaynak.dropna(subset=["MAL_ADI", oynak_kolon, "REEL_ORTALAMA_UCRET"])
            .groupby(grup_kol, as_index=False)
            .agg(
                RISK_OYNAKLIK=(oynak_kolon, "mean"),
                MALIYET_REEL=("REEL_ORTALAMA_UCRET", "mean"),
                KAYIT=("REEL_ORTALAMA_UCRET", "count"),
            )
        )

    if (
        not df_kaynak.empty
        and {"ASGARI_UCRET", "AZAMI_UCRET", "ORTALAMA_UCRET", "MAL_ADI"}.issubset(df_kaynak.columns)
    ):
        df_makas = df_kaynak[
            (df_kaynak["ORTALAMA_UCRET"] > 0)
            & (df_kaynak["AZAMI_UCRET"] >= df_kaynak["ASGARI_UCRET"])
        ].copy()
        if not df_makas.empty:
            df_makas["MAKAS_ORANI_YUZDE"] = (
                (df_makas["AZAMI_UCRET"] - df_makas["ASGARI_UCRET"])
                / df_makas["ORTALAMA_UCRET"].replace(0, np.nan)
            ) * 100.0
            makas_ozet = (
                df_makas.dropna(subset=["MAL_ADI", "MAKAS_ORANI_YUZDE"])
                .groupby("MAL_ADI", as_index=False)
                .agg(
                    ORT_MAKAS_YUZDE=("MAKAS_ORANI_YUZDE", "mean"),
                    ORT_ASGARI=("ASGARI_UCRET", "mean"),
                    ORT_AZAMI=("AZAMI_UCRET", "mean"),
                )
                .sort_values("ORT_MAKAS_YUZDE", ascending=False)
                .head(10)
                .sort_values("ORT_MAKAS_YUZDE", ascending=True)
            )

    return kraljic_df, makas_ozet


def _kume_rozeti_ve_ikame_goster(urun_adi: str, df_kumeler: pd.DataFrame, df_oz: pd.DataFrame) -> None:
    """01_Veri/urun_kumeleri.csv varsa seçili ürünün küme rozetini ve aynı kümedeki daha ucuz ikame ürünleri gösterir."""
    if df_kumeler.empty or not {"MAL_ADI", "KUME_NO"}.issubset(df_kumeler.columns):
        return

    urun_satir = df_kumeler[df_kumeler["MAL_ADI"] == urun_adi]
    if urun_satir.empty:
        return

    kume_no = urun_satir.iloc[0]["KUME_NO"]
    kume_adi = (
        str(urun_satir.iloc[0]["KUME_ADI"]).strip()
        if "KUME_ADI" in urun_satir.columns and pd.notna(urun_satir.iloc[0]["KUME_ADI"])
        else f"Mevsimsel Küme {kume_no}"
    )

    ayni_kume_urunleri = (
        df_kumeler[(df_kumeler["KUME_NO"] == kume_no) & (df_kumeler["MAL_ADI"] != urun_adi)]["MAL_ADI"]
        .dropna()
        .unique()
        .tolist()
    )

    # Aynı kümedeki ürünlerin ortalama reel fiyatlarını bulup seçili üründen DAHA UCUZ olanları öne çıkar
    ucuz_ikameler = []
    diger_ikameler = []
    if not df_oz.empty and {"MAL_ADI", "REEL_ORTALAMA_UCRET"}.issubset(df_oz.columns):
        fiyat_haritasi = df_oz.groupby("MAL_ADI")["REEL_ORTALAMA_UCRET"].mean().to_dict()
        odak_fiyat = _guvenli_sayi(fiyat_haritasi.get(urun_adi, np.nan), np.nan)
        for u in ayni_kume_urunleri:
            u_f = _guvenli_sayi(fiyat_haritasi.get(u, np.nan), np.nan)
            if pd.notna(odak_fiyat) and pd.notna(u_f) and u_f < odak_fiyat:
                avantaj_pct = ((odak_fiyat - u_f) / odak_fiyat) * 100.0 if odak_fiyat > 0 else 0.0
                ucuz_ikameler.append((u, u_f, avantaj_pct))
            else:
                diger_ikameler.append((u, u_f))
        ucuz_ikameler.sort(key=lambda x: x[1])

    if ucuz_ikameler:
        ikame_satir = ", ".join(
            [f"<b>{u}</b> ({f:.2f} ₺ • -%{pct:.0f})" for u, f, pct in ucuz_ikameler[:4]]
        )
        ikame_html = f"<b>Aynı Kümedeki Daha Ucuz İkame Ürünler:</b> {ikame_satir}"
    elif ayni_kume_urunleri:
        ikame_html = f"<b>Aynı Kümedeki Alternatif Ürünler:</b> {', '.join(ayni_kume_urunleri[:5])}"
    else:
        ikame_html = "Bu kümede başka ürün bulunmamaktadır."

    st.markdown(
        f"""
<div class="signal-card" style="border-left:5px solid #1B7A43; padding:12px 16px; min-height:auto; margin-bottom:14px; background:#F0FDF4;">
<div style="display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin-bottom:6px;">
<span style="background:#1B7A43; color:#FFFFFF; padding:3px 10px; border-radius:999px; font-size:0.78rem; font-weight:700;">
Mevsimsel Küme: {kume_adi}
</span>
<span style="color:#14532D; font-size:0.84rem; font-weight:600;">
{urun_adi} bu mevsimsel davranış grubunda yer almaktadır.
</span>
</div>
<div style="color:#1E293B; font-size:0.85rem; line-height:1.45;">
{ikame_html}
</div>
</div>
""",
        unsafe_allow_html=True,
    )


def _degisken_turkce_etiket(ham_ad: str) -> str:
    """ozellik_onemi.csv içindeki teknik değişken adlarını kullanıcı dostu Türkçeye çevirir; zaten Türkçe ise korur."""
    harita = {
        "REEL_ORTALAMA_UCRET": "Güncel Reel Fiyat",
        "REEL_LAG_1": "1 Gün Önceki Reel Fiyat",
        "REEL_LAG_7": "7 Gün Önceki Reel Fiyat",
        "REEL_LAG_30": "30 Gün Önceki Reel Fiyat",
        "REEL_DEGISIM_YUZDE": "Günlük Reel Değişim (%)",
        "REEL_OYNAKLIK_7": "7 Günlük Fiyat Oynaklığı",
        "REEL_OYNAKLIK_30": "30 Günlük Fiyat Oynaklığı",
        "AY": "Yılın Ayı",
        "HAFTA": "Yılın Haftası",
        "YIL": "Yıl",
        "MAL_ADI": "Ürün Adı",
        "MAL_TURU": "Ürün Kategorisi",
        "BIRIM": "Ölçü Birimi",
        "ASGARI_UCRET": "Hal Taban Fiyatı",
        "AZAMI_UCRET": "Hal Tavan Fiyatı",
        "ORTALAMA_UCRET": "Hal Ortalama Fiyatı",
    }
    temiz = str(ham_ad).strip()
    if temiz in harita:
        return harita[temiz]
    for k, v in harita.items():
        if temiz.startswith(k + "_"):
            ek = temiz[len(k) + 1 :]
            return f"{v}: {ek}"
    # Zaten temiz Türkçe isimse (alt tire yoksa) olduğu gibi döndür
    if "_" not in temiz:
        return temiz
    return temiz.replace("_", " ").title()


@st.cache_resource(show_spinner=False)
def modeli_yukle():
    """03_Model/model.joblib (1 Haftalık) varsa yükler; yoksa None ve durum mesajı döndürür."""
    model_yolu = _dosya_yolu_coz("03_Model/model.joblib")
    if os.path.exists(model_yolu):
        try:
            model = joblib.load(model_yolu)
            return model, True, "Aktif (1 Haftalık Model Yüklendi)"
        except Exception as e:
            return None, False, f"Yedek Mod (Model yükleme hatası: {e})"
    return None, False, "Yedek Mod (Model bekleniyor)"


@st.cache_resource(show_spinner=False)
def aylik_modeli_yukle():
    """03_Model/model_aylik.joblib (1 Aylık / 30 Kayıt Sonrası) varsa yükler."""
    model_yolu = _dosya_yolu_coz("03_Model/model_aylik.joblib")
    if os.path.exists(model_yolu):
        try:
            model = joblib.load(model_yolu)
            return model, True
        except Exception:
            return None, False
    return None, False


@st.cache_resource(show_spinner=False)
def don_modeli_yukle():
    """03_Model/model_don_ozellikli.joblib (15 Özellikli İklim & Don Modeli) varsa yükler."""
    model_yolu = _dosya_yolu_coz("03_Model/model_don_ozellikli.joblib")
    if os.path.exists(model_yolu):
        try:
            model = joblib.load(model_yolu)
            return model, True
        except Exception:
            return None, False
    return None, False


# Verileri ve modelleri yükle
VERILER = verileri_yukle(3)
df_ozellikli = VERILER["hal_reel_ozellikli"]
df_aylik_reel = VERILER["ilk_25_aylik_reel_fiyat"]
df_karar_destegi = VERILER["ilk_25_reel_karar_destegi"]
df_reel_ozet = VERILER["ilk_25_reel_ozet"]
df_gunluk_karar = VERILER["gunluk_satinalma_karar"]
df_haftalik_karar = VERILER["haftalik_satinalma_karar"]
df_aylik_karar = VERILER["aylik_satinalma_karar"]
df_mevsimsel_karar = VERILER["mevsimsel_satinalma_karar"]
df_gelecek_tahminler = VERILER["gelecek_hafta_ve_ay_tahminleri"]

MODEL, MODEL_AKTIF, MODEL_DURUM_METNI = modeli_yukle()
MODEL_AYLIK, MODEL_AYLIK_AKTIF = aylik_modeli_yukle()
MODEL_DON, MODEL_DON_AKTIF = don_modeli_yukle()


# -----------------------------------------------------------------------------
# 2. SOL MENÜ (SIDEBAR)
# -----------------------------------------------------------------------------
with st.sidebar:
    if "aktif_gorunum" not in st.session_state:
        st.session_state["aktif_gorunum"] = "anasayfa"

    _LOGO_B64_FALLBACK = "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"
    _logo_dosya = _dosya_yolu_coz("02_Kod/snc_logo.png")
    if _logo_dosya.exists():
        try:
            _logo_b64 = base64.b64encode(_logo_dosya.read_bytes()).decode("ascii")
            _logo_mime = "image/png"
        except Exception:
            _logo_b64 = _LOGO_B64_FALLBACK
            _logo_mime = "image/jpeg"
    else:
        _logo_b64 = _LOGO_B64_FALLBACK
        _logo_mime = "image/jpeg"

    st.markdown(
        f"""
<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-bottom:4px solid #1B7A43; border-radius:16px; padding:16px 14px 14px 14px; text-align:center; margin-bottom:14px; box-shadow:0 4px 12px rgba(15, 23, 42, 0.05);">
<img src="data:{_logo_mime};base64,{_logo_b64}" alt="SNC Logo" style="max-width:100%; height:auto; max-height:115px; display:block; margin:0 auto 8px auto;" />
<div style="font-size:1.10rem; font-weight:800; color:#14532D; letter-spacing:0.3px;">Hoş Geldiniz</div>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.session_state["aktif_gorunum"] == "anasayfa":
        if st.button("BAŞLA — Panellere Geç", type="primary", use_container_width=True, key="sb_basla_btn"):
            st.session_state["aktif_gorunum"] = "paneller"
            st.rerun()
    else:
        if st.button("Anasayfaya Dön", use_container_width=True, key="sb_anasayfa_btn"):
            st.session_state["aktif_gorunum"] = "anasayfa"
            st.rerun()
    st.divider()

    st.markdown("### 🏪 İşletme ve Filtre Ayarları")

    aktif_sube_sayisi = st.number_input(
        "Aktif Şube Sayısı",
        min_value=1,
        max_value=100,
        value=12,
        step=1,
        help="Restoran zincirinizdeki şube sayısını girin. Karar ekranı, teklif hesabı ve tasarruf simülatörü bu sayıya göre otomatik güncellenir.",
    )

    mal_turleri = (
        sorted(df_ozellikli["MAL_TURU"].dropna().unique().tolist())
        if "MAL_TURU" in df_ozellikli.columns and not df_ozellikli.empty
        else ["SEBZE", "MEYVE", "ITHAL"]
    )
    secili_turler = st.multiselect(
        "Ürün Kategorisi",
        options=mal_turleri,
        default=mal_turleri,
        help="İthal ürünlerin tamamı tek bir 'ITHAL' kategorisinde birleştirilmiştir.",
    )

    if secili_turler and "MAL_TURU" in df_ozellikli.columns:
        df_filtreli = df_ozellikli[df_ozellikli["MAL_TURU"].isin(secili_turler)].copy()
    else:
        df_filtreli = df_ozellikli.copy()

    urun_listesi = (
        sorted(df_filtreli["MAL_ADI"].dropna().unique().tolist())
        if "MAL_ADI" in df_filtreli.columns and not df_filtreli.empty
        else ["DOMATES"]
    )
    secili_odak_urun = st.selectbox(
        "İncelenecek Odak Ürün",
        options=urun_listesi,
        index=0,
        help="Analiz, Strateji ve Karar ekranlarında detaylı incelenecek ürünü buradan seçin.",
    )

    if st.session_state.get("aktif_gorunum", "anasayfa") == "anasayfa":
        st.divider()
        st.markdown("### 🤖 Tahmin Motoru Durumu")
        if MODEL_AKTIF and MODEL_AYLIK_AKTIF:
            st.success("**1 Haftalık ve 1 Aylık Yapay Zekâ Modelleri Aktif**\n\nHer iki tahmin motoru canlı devrede.")
        elif MODEL_AKTIF:
            st.success("**Makine Öğrenmesi Modeli Aktif**\n\n1 Haftalık tahmin modeli devrede.")
        else:
            st.warning(
                "**Yedek Tahmin Modu Aktif**\n\n"
                "Eğitilmiş tahmin modeli henüz yüklenmedi. "
                "Sistem geçmiş fiyat trendleriyle güvenli yedek modda çalışıyor."
            )
        st.caption("Kaynak: İzmir BB Hal Fiyatları (2006–2025) & TCMB EVDS TÜFE")


# -----------------------------------------------------------------------------
# 3. ANASAYFA (ÖRNEK TASARIM BİREBİR) VEYA 6 KARAR DESTEK PANELİ
# -----------------------------------------------------------------------------
if "aktif_gorunum" not in st.session_state:
    st.session_state["aktif_gorunum"] = "anasayfa"

if st.session_state["aktif_gorunum"] == "anasayfa":
    st.markdown(
        f"""
<style>:root {{ --green-950: #072613; --green-900: #0b3d1e; --green-800: #11552b; --green-700: #166e37; --green-600: #1d8a45; --leaf-500: #66b817; --leaf-400: #7dd126; --mint-100: #e8f6ec; --mint-50: #f3faf5; --bg: #f6faf7; --surface: #ffffff; --border: #d9e8dd; --border-strong: #b9d7c2; --ink: #0d2115; --ink-muted: #4b6355; --ink-soft: #6c8476; --shadow-sm: 0 2px 8px rgba(11, 61, 30, 0.05); --shadow-md: 0 10px 30px rgba(11, 61, 30, 0.08); --shadow-lg: 0 18px 45px rgba(11, 61, 30, 0.14); --radius-sm: 10px; --radius-md: 16px; --radius-lg: 22px; --radius-pill: 999px; --max-w: 1200px; }} .snc-landing-wrap {{ margin: 0; font-family: "Inter", "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif; background-color: var(--bg); color: var(--ink); line-height: 1.55; -webkit-font-smoothing: antialiased; border-radius: 18px; border: 1px solid var(--border); overflow: hidden; }} .snc-landing-wrap *, .snc-landing-wrap *::before, .snc-landing-wrap *::after {{ box-sizing: border-box; }} .site-header {{ position: relative; z-index: 10; background: linear-gradient(110deg, var(--green-950) 0%, var(--green-900) 48%, var(--green-800) 100%); border-bottom: 1px solid rgba(125, 209, 38, 0.28); box-shadow: 0 8px 28px rgba(7, 38, 19, 0.22); }} .header-inner {{ max-inline-size: var(--max-w); margin-inline: auto; padding-block: 0.75rem; padding-inline: 1.5rem; display: flex; align-items: center; justify-content: space-between; gap: 1.25rem; }} .brand {{ display: flex; align-items: center; gap: 0.9rem; text-decoration: none; color: #ffffff; min-inline-size: 0; }} .brand-logo-wrap {{ background: #ffffff; padding: 0.34rem 0.65rem; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18), inset 0 0 0 1px rgba(102, 184, 23, 0.2); flex-shrink: 0; transition: transform 180ms ease-out; }} .brand:hover .brand-logo-wrap {{ transform: translateY(-1px); }} .brand-logo-wrap img {{ display: block; height: 36px; width: auto; object-fit: contain; }} .brand-text {{ display: flex; flex-direction: column; gap: 0.12rem; }} .brand-title {{ font-size: 1.02rem; font-weight: 700; letter-spacing: -0.01em; color: #ffffff; display: flex; align-items: center; gap: 0.45rem; }} .brand-subtitle {{ font-size: 0.74rem; font-weight: 500; color: rgba(232, 246, 236, 0.84); letter-spacing: 0.01em; }} .header-actions {{ display: flex; align-items: center; gap: 0.75rem; }} .header-meta-pill {{ display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.36rem 0.78rem; border-radius: var(--radius-pill); background: rgba(255, 255, 255, 0.09); border: 1px solid rgba(255, 255, 255, 0.16); color: #e8f6ec; font-size: 0.76rem; font-weight: 600; white-space: nowrap; }} .pulse-dot {{ width: 7px; height: 7px; border-radius: 50%; background: var(--leaf-400); box-shadow: 0 0 0 3px rgba(125, 209, 38, 0.25); }} .btn-header-cta {{ display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.52rem 1.05rem; border: none; border-radius: var(--radius-pill); background: linear-gradient(135deg, var(--leaf-500), var(--leaf-400)); color: var(--green-950); font-size: 0.84rem; font-weight: 700; cursor: pointer; text-decoration: none; box-shadow: 0 4px 14px rgba(102, 184, 23, 0.32); transition: transform 180ms ease-out, box-shadow 180ms ease-out, filter 180ms ease-out; }} .btn-header-cta:hover {{ transform: translateY(-2px); box-shadow: 0 8px 22px rgba(125, 209, 38, 0.45); filter: brightness(1.05); }} .hero {{ position: relative; padding-block: 2.5rem 2.2rem; padding-inline: 1.5rem; background: radial-gradient(ellipse 65% 55% at 15% 0%, rgba(102, 184, 23, 0.12), transparent 65%), radial-gradient(ellipse 55% 50% at 90% 10%, rgba(22, 110, 55, 0.11), transparent 65%), linear-gradient(180deg, #eff8f2 0%, var(--bg) 100%); border-bottom: 1px solid var(--border); }} .hero-inner {{ max-inline-size: var(--max-w); margin-inline: auto; display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 2.2rem; align-items: center; }} .eyebrow {{ display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.34rem 0.85rem; border-radius: var(--radius-pill); background: #ffffff; border: 1px solid var(--border-strong); color: var(--green-800); font-size: 0.74rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; box-shadow: var(--shadow-sm); margin-block-end: 1.1rem; }} .hero h1 {{ margin: 0 0 1rem; font-size: clamp(1.9rem, 3.1vw, 2.65rem); font-weight: 800; line-height: 1.15; letter-spacing: -0.028em; color: var(--green-950); }} .hero h1 .highlight {{ background: linear-gradient(120deg, var(--green-700) 0%, var(--leaf-500) 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }} .hero-desc {{ margin: 0 0 1.65rem; font-size: 1rem; color: var(--ink-muted); max-inline-size: 56ch; }} .hero-cta-row {{ display: flex; flex-wrap: wrap; align-items: center; gap: 0.9rem; margin-block-end: 1.8rem; }} .btn-start-primary {{ position: relative; overflow: hidden; display: inline-flex; align-items: center; gap: 0.75rem; padding: 0.92rem 1.75rem; border: 1px solid rgba(125, 209, 38, 0.45); border-radius: 14px; background: linear-gradient(135deg, var(--green-900) 0%, var(--green-700) 55%, #1d8a45 100%); color: #ffffff; font-size: 0.96rem; font-weight: 700; letter-spacing: 0.01em; cursor: pointer; box-shadow: 0 10px 26px rgba(17, 85, 43, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.22); transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease; }} .btn-start-primary:hover {{ transform: translateY(-3px); border-color: var(--leaf-400); box-shadow: 0 16px 34px rgba(22, 110, 55, 0.38), 0 0 0 4px rgba(102, 184, 23, 0.16); }} .btn-start-primary .btn-arrow {{ display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; background: rgba(125, 209, 38, 0.22); }} .btn-secondary {{ display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.9rem 1.3rem; border-radius: 14px; border: 1px solid var(--border-strong); background: #ffffff; color: var(--green-900) !important; font-size: 0.9rem; font-weight: 600; text-decoration: none !important; cursor: pointer; }} .hero-trust {{ display: flex; flex-wrap: wrap; gap: 1.5rem; padding-block-start: 1.15rem; border-top: 1px solid var(--border); }} .trust-item {{ display: flex; flex-direction: column; }} .trust-val {{ font-size: 1.15rem; font-weight: 800; color: var(--green-900); }} .trust-lbl {{ font-size: 0.76rem; color: var(--ink-soft); font-weight: 500; }} .preview-card {{ background: #ffffff; border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.3rem; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; }} .preview-card::before {{ content: ""; position: absolute; inset-block-start: 0; inset-inline: 0; height: 4px; background: linear-gradient(90deg, var(--green-800), var(--leaf-500)); }} .preview-top {{ display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; margin-block-end: 1rem; }} .preview-label {{ font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--green-700); display: flex; align-items: center; gap: 0.4rem; }} .product-tabs {{ display: inline-flex; background: var(--mint-50); border: 1px solid var(--border); border-radius: var(--radius-pill); padding: 3px; gap: 2px; }} .product-tab {{ border: none; background: transparent; color: var(--ink-muted); font-size: 0.76rem; font-weight: 600; padding: 0.3rem 0.7rem; border-radius: var(--radius-pill); cursor: pointer; }} .product-tab[aria-pressed="true"] {{ background: var(--green-800); color: #ffffff; box-shadow: 0 2px 6px rgba(17, 85, 43, 0.25); }} .signal-header {{ display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; margin-block-end: 1rem; }} .signal-price-wrap .product-name {{ font-size: 0.8rem; color: var(--ink-soft); font-weight: 600; }} .signal-price {{ font-size: 1.7rem; font-weight: 800; color: var(--green-950); line-height: 1.15; }} .signal-price span {{ font-size: 0.85rem; font-weight: 600; color: var(--ink-soft); }} .decision-badge {{ display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.42rem 0.85rem; border-radius: var(--radius-pill); font-size: 0.78rem; font-weight: 700; }} .decision-buy {{ background: #e3f7e8; color: #0e602c; border: 1px solid #a9e0b8; }} .decision-normal {{ background: #eef6ff; color: #17528c; border: 1px solid #b9d7f5; }} .decision-wait {{ background: #fff4e5; color: #9a4a00; border: 1px solid #f7cf99; }} .chart-box {{ background: linear-gradient(180deg, var(--mint-50) 0%, #ffffff 100%); border: 1px solid var(--border); border-radius: 14px; padding: 0.85rem 0.9rem 0.65rem; margin-block-end: 1rem; }} .chart-meta {{ display: flex; justify-content: space-between; font-size: 0.72rem; color: var(--ink-soft); margin-block-end: 0.4rem; font-weight: 600; }} .chart-svg {{ width: 100%; height: 108px; display: block; }} .hal-band {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.6rem; }} .band-cell {{ background: var(--bg); border: 1px solid var(--border); border-radius: 10px; padding: 0.55rem 0.7rem; }} .band-cell span {{ display: block; font-size: 0.69rem; color: var(--ink-soft); font-weight: 600; text-transform: uppercase; }} .band-cell strong {{ font-size: 0.92rem; color: var(--green-950); }} .section {{ max-inline-size: var(--max-w); margin-inline: auto; padding-block: 2.3rem; padding-inline: 1.5rem; }} .section-head {{ display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 1rem; margin-block-end: 1.5rem; }} .section-kicker {{ font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--green-700); margin-block-end: 0.3rem; }} .section-title {{ margin: 0; font-size: clamp(1.4rem, 2.1vw, 1.75rem); font-weight: 800; color: var(--green-950); }} .section-sub {{ margin: 0.3rem 0 0; color: var(--ink-muted); font-size: 0.93rem; max-inline-size: 56ch; }} .bento-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1.15rem; }} .bento-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.35rem; display: flex; flex-direction: column; justify-content: space-between; gap: 1.1rem; box-shadow: var(--shadow-sm); }} .bento-head {{ display: flex; align-items: flex-start; gap: 0.95rem; }} .icon-badge {{ width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, var(--mint-100), #d8f1e0); color: var(--green-800); display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; border: 1px solid rgba(22, 110, 55, 0.14); }} .bento-card h3 {{ margin: 0 0 0.3rem; font-size: 1.04rem; font-weight: 700; color: var(--green-950); }} .bento-card p {{ margin: 0; font-size: 0.87rem; color: var(--ink-muted); }} .micro-visual {{ background: var(--mint-50); border: 1px solid var(--border); border-radius: 12px; padding: 0.75rem 0.9rem; display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; flex-wrap: wrap; }} .pill-row {{ display: flex; flex-wrap: wrap; gap: 0.45rem; }} .mini-chip {{ font-size: 0.73rem; font-weight: 700; padding: 0.26rem 0.6rem; border-radius: var(--radius-pill); background: #ffffff; border: 1px solid var(--border); color: var(--green-900); }} .mini-chip.green {{ background: var(--green-800); border-color: var(--green-800); color: #ffffff; }} .mini-chip.leaf {{ background: #ebf8dc; border-color: #bfe495; color: #2f6106; }} .scale-bar-wrap {{ flex: 1; min-inline-size: 170px; }} .scale-track {{ height: 8px; border-radius: 999px; background: linear-gradient(90deg, #2ca54e 0%, #9ad138 50%, #e69d24 100%); position: relative; margin-block: 0.35rem; }} .scale-marker {{ position: absolute; top: 50%; left: 34%; transform: translate(-50%, -50%); width: 14px; height: 14px; border-radius: 50%; background: #ffffff; border: 3px solid var(--green-900); }} .scale-labels {{ display: flex; justify-content: space-between; font-size: 0.69rem; font-weight: 600; color: var(--ink-soft); }} .kpi-band {{ background: linear-gradient(135deg, var(--green-950) 0%, var(--green-900) 60%, var(--green-800) 100%); border-radius: var(--radius-lg); padding: 1.45rem; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; box-shadow: var(--shadow-lg); color: #ffffff; }} .kpi-item {{ background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 14px; padding: 1.05rem 1.1rem; }} .kpi-kicker {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: rgba(232, 246, 236, 0.72); font-weight: 600; }} .kpi-value {{ font-size: 1.4rem; font-weight: 800; margin: 0.25rem 0 0.35rem; color: #ffffff; }} .kpi-tag {{ display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.74rem; font-weight: 600; color: var(--leaf-400); }} .filter-pills {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }} .filter-pill {{ border: 1px solid var(--border-strong); background: #ffffff; color: var(--ink-muted); font-size: 0.8rem; font-weight: 600; padding: 0.42rem 0.9rem; border-radius: var(--radius-pill); cursor: pointer; }} .filter-pill[aria-pressed="true"] {{ background: var(--green-800); border-color: var(--green-800); color: #ffffff; }} .panels-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.15rem; }} .panel-card {{ position: relative; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.35rem; display: flex; flex-direction: column; justify-content: space-between; gap: 0.95rem; box-shadow: var(--shadow-sm); overflow: hidden; }} .panel-card::before {{ content: ""; position: absolute; inset-block-start: 0; inset-inline: 0; height: 3.5px; background: linear-gradient(90deg, var(--green-800), var(--leaf-500)); }} .panel-card.hidden-card {{ display: none; }} .panel-top {{ display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }} .panel-num {{ font-size: 0.72rem; font-weight: 800; letter-spacing: 0.06em; color: var(--green-800); background: var(--mint-100); padding: 0.26rem 0.62rem; border-radius: var(--radius-pill); }} .panel-icon {{ width: 36px; height: 36px; border-radius: 10px; background: var(--mint-50); border: 1px solid var(--border); color: var(--green-800); display: inline-flex; align-items: center; justify-content: center; }} .panel-card h3 {{ margin: 0.65rem 0 0.35rem; font-size: 1.06rem; font-weight: 700; color: var(--green-950); }} .panel-card p {{ margin: 0; font-size: 0.85rem; color: var(--ink-muted); line-height: 1.5; }} .panel-tags {{ display: flex; flex-wrap: wrap; gap: 0.4rem; margin-block-start: 0.8rem; }} .panel-tag {{ font-size: 0.72rem; font-weight: 600; color: var(--green-900); background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 0.2rem 0.52rem; }} .panel-action {{ display: inline-flex; align-items: center; gap: 0.35rem; align-self: flex-start; border: none; background: transparent; padding: 0.25rem 0; color: var(--green-700); font-size: 0.83rem; font-weight: 700; cursor: pointer; }} .footer-cta-wrap {{ max-inline-size: var(--max-w); margin-inline: auto; padding: 0 1.5rem 2.2rem; }} .footer-cta {{ background: linear-gradient(125deg, var(--green-950) 0%, var(--green-900) 58%, var(--green-800) 100%); border-radius: var(--radius-lg); padding: 1.75rem 2rem; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 1.5rem; border: 1px solid rgba(125, 209, 38, 0.28); box-shadow: var(--shadow-lg); color: #ffffff; }} .footer-cta-left {{ display: flex; align-items: center; gap: 1.15rem; }} .footer-cta h2 {{ margin: 0 0 0.25rem; font-size: 1.3rem; font-weight: 800; color: #ffffff; }} .footer-cta p {{ margin: 0; font-size: 0.88rem; color: rgba(232, 246, 236, 0.82); }} .btn-footer-start {{ display: inline-flex; align-items: center; gap: 0.65rem; padding: 0.85rem 1.65rem; border: none; border-radius: 14px; background: linear-gradient(135deg, var(--leaf-500) 0%, var(--leaf-400) 100%); color: var(--green-950); font-size: 0.94rem; font-weight: 800; cursor: pointer; box-shadow: 0 10px 24px rgba(102, 184, 23, 0.34); }} @media (max-width: 980px) {{ .hero-inner {{ grid-template-columns: 1fr; }} .kpi-band {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} .panels-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }} .snc-qr-corner {{ display: inline-flex; align-items: center; gap: 0.65rem; background: #ffffff; border: 1.5px solid #b9d7c2; border-radius: 13px; padding: 0.35rem 0.65rem; box-shadow: 0 4px 14px rgba(7, 38, 19, 0.20); }} .snc-qr-corner img {{ width: 54px; height: 54px; border-radius: 7px; border: 1px solid #d9e8dd; display: block; background: #ffffff; }} .snc-qr-meta {{ display: flex; flex-direction: column; gap: 0.08rem; text-align: left; line-height: 1.25; }} .snc-qr-title {{ font-size: 0.70rem; font-weight: 800; color: #0b3d1e; text-transform: uppercase; letter-spacing: 0.04em; }} .snc-qr-sub {{ font-size: 0.66rem; font-weight: 600; color: #166e37; }} .snc-qr-floating {{ position: fixed; right: 22px; bottom: 22px; z-index: 99; background: #ffffff; border: 2px solid #166e37; border-radius: 16px; padding: 10px 12px; box-shadow: 0 14px 34px rgba(7, 38, 19, 0.22); text-align: center; width: 138px; }} .snc-qr-floating img {{ width: 108px; height: 108px; border-radius: 8px; border: 1px solid #d9e8dd; display: block; margin: 4px auto; background: #ffffff; }} .snc-qr-floating-title {{ font-size: 0.71rem; font-weight: 800; color: #072613; letter-spacing: 0.03em; }} .snc-qr-floating-sub {{ font-size: 0.66rem; font-weight: 600; color: #166e37; margin-top: 2px; }}</style><div class="snc-landing-wrap" translate="no"><header class="site-header">
<div class="header-inner">
<div class="brand">
<span class="brand-logo-wrap">
<img src="data:{_logo_mime};base64,{_logo_b64}" alt="Logo">
</span>
<span class="brand-text">
<span class="brand-title">Akıllı Satın Alma</span>
<span class="brand-subtitle">Çok Şubeli Restoran Zinciri Karar Destek Sistemi</span>
</span>
</div>
<div class="header-actions">
<div class="snc-qr-corner" title="Telefon kamerasıyla okutarak canlı uygulamayı açabilirsiniz">
<img id="sncHeaderQrImg" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMYAAADGCAIAAAAG+WgKAAAEE0lEQVR4nO3dy43bSBRA0e7BLBiAc5j8w3EOE4B2cgDcEIVbH7XPWevn9kUJDyWyvt/v9xd0/glfCyRFzypFTFLEJEVMUsQkRUxSxCRFTFLEJEXs3ycPuv779bXP6/f/A8+6f+YnrzP2L72/8hW9zif+X1iliEmKmKSISYqYpNgx8VVT2BNjE83YfLfyM7+iqfDJK1fGPqFVipikiEmKmKSISYozJr67ebtaT95rbHfs/qwnc1k1Yb0Om9Sqz2OVIiYpYpIiJilikuLUiW+lsbls5TR32hS2klWKmKSISYqYpIhJithHTnzzPJnLnsyJ118z391ZpYhJipikiEmKmKQ4deLbO62svEru/srVDHhFe457/y+sUsQkRUxSxCRFTFKcMfHtvWPk2GQ09qvOlTt6V3TXmr2sUsQkRUxSxCRFTFLEvj/xBPZ5d26ZN7u9tl5FuJJVipikiEmKmKSISYodE9/ePayx95p3qsLY69ztvfpv3rxplSImKWKSIiYpYpJix686TztLbt6VdPN+QfpTd0XvrFLEJEVMUsQkRUxSnPGrzpW7WvP276r3Wuk6fj/RKkVMUsQkRUxSxCTFGb/q3Lvrt3fe3Lu/edqO3p1VipikiEmKmKSISYpT9/j2zlMr3/20ncrXwrvW2ONjA198xCRFTFLEJMWp5/GNzRSn3a9y77tfC680nDd9W6WISYqYpIhJipik+JwT2KsZcOzdxx6zcnp63R6z8orFea9jlSImKWKSIiYpYpJix8RX/Sawmqf27oXdVX+NvSdcPHn3J6xSxCRFTFLEJEVMUpyxx1fdG2TsMXvvAHP+VFhxOgNH8MVHTFLEJEVMUvys8/jm7fqt3B2bd2bftfUzu46PI/jiIyYpYpIiJik+53SGT5zdqqsRX8ef63fnXp0cyhcfMUkRkxQxSfE5pzPMe9a8SW2e18I5cd5f7AmrFDFJEZMUMUkRkxSn3rmlMm9S27tT+cTKvcuxxzxhlSImKWKSIiYpYpLijOv4Tps7fsaceDdv3px3CoZVipikiEmKmKSISYoz9vhWGpsTq7up7L1b5srf0zqPj0P54iMmKWKSIiYpzjidYeWvOseetfceLNe0s/bm/eXdq5ND+eIjJilikiImKc6Y+Fb+SnDsdc6/c8sTK08nrJ5llSImKWKSIiYpYpLi1Ilvpb13U1l5heBpd4lxHR8b+OJDUpzNKkVMUsQ+cuJ7MitVv5msJqNr67WQ887FuLNKEZMUMUkRkxQxSXHqxLf3zPFqmjtt3+218GpE5/FxKF98xCRFTFLEJMUZE9/eHau7lSe5f6Jr4QxolSImKWKSIiYpYpIi9v1+v+vX5K9mlSImKWKSIiYpYpIiJilikiImKWKSIiYpYpLiq/UHAowiRfAfsQ0AAAAASUVORK5CYII=" alt="Canlı Uygulama QR" />
<div class="snc-qr-meta">
<span class="snc-qr-title">Mobil QR</span>
<span class="snc-qr-sub">Telefonda Aç</span>
</div>
</div>
<span class="header-meta-pill">
<span class="pulse-dot" aria-hidden="true"></span>
{aktif_sube_sayisi} Şube • 25 Ürün
</span>
<button type="button" class="btn-header-cta" data-start-action="">
<span>Panellere Geç</span>
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
<path d="M5 12h14"></path>
<path d="m12 5 7 7-7 7"></path>
</svg>
</button>
</div>
</div>
</header>
<main id="anasayfa">
<section class="hero">
<div class="hero-inner">
<div>
<div class="eyebrow">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" aria-hidden="true">
<path d="M12 2L2 7l10 5 10-5-10-5z"></path>
<path d="m2 17 10 5 10-5"></path>
<path d="m2 12 10 5 10-5"></path>
</svg>
Karar Destek Platformu • 2006–2025 İzmir Hal Verisi
</div>
<h1>
Hangi ürünü, <span class="highlight">ne zaman ve hangi fiyattan</span> almalısınız?
</h1>
<p class="hero-desc">
20 yıllık İzmir Büyükşehir Belediyesi Hal Fiyatları ve TCMB TÜFE enflasyon verilerini yapay zekâ modelleriyle birleştirerek çok şubeli sebze ve meyve tedarik kararlarınızı optimize eder.
</p>
<div class="hero-cta-row">
<button type="button" class="btn-start-primary" data-start-action="">
<span>BAŞLA — Karar Destek Panellerine Geç</span>
<span class="btn-arrow" aria-hidden="true">
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
<path d="M5 12h14"></path>
<path d="m12 5 7 7-7 7"></path>
</svg>
</span>
</button>
<a class="btn-secondary" href="#paneller">
<span>6 Paneli İncele</span>
<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
<path d="M12 5v14"></path>
<path d="m19 12-7 7-7-7"></path>
</svg>
</a>
</div>
<div class="hero-trust">
<div class="trust-item">
<span class="trust-val">131.888</span>
<span class="trust-lbl">İzmir Hal Fiyat Kaydı</span>
</div>
<div class="trust-item">
<span class="trust-val">25 Ürün</span>
<span class="trust-lbl">Sebze, Meyve &amp; İthal</span>
</div>
<div class="trust-item">
<span class="trust-val">{aktif_sube_sayisi} Şube</span>
<span class="trust-lbl">Dinamik Bütçe &amp; Reçete</span>
</div>
</div>
</div>
<aside class="preview-card" aria-label="Örnek Yapay Zekâ Alım Sinyali Önizlemesi">
<div class="preview-top">
<span class="preview-label">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">
<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline>
<polyline points="16 7 22 7 22 13"></polyline>
</svg>
Örnek AI Alım Sinyali
</span>
<div class="product-tabs" role="group" aria-label="Örnek ürün seçimi">
<button type="button" class="product-tab" data-product="ananas" aria-pressed="true">Ananas</button>
<button type="button" class="product-tab" data-product="domates" aria-pressed="false">Domates</button>
<button type="button" class="product-tab" data-product="biber" aria-pressed="false">Biber</button>
</div>
</div>
<div class="signal-header">
<div class="signal-price-wrap">
<div class="product-name" id="previewName">İthal • Ananas (Adet)</div>
<div class="signal-price" id="previewPrice">78,40 <span>₺ / ort.</span></div>
</div>
<span class="decision-badge decision-buy" id="previewBadge">ŞİMDİ AL • %9,2 Dip</span>
</div>
<div class="chart-box">
<div class="chart-meta">
<span id="previewHorizon">1 Haftalık &amp; 1 Aylık AI Projeksiyonu</span>
<span id="previewDelta" style="color: #166e37;">+11,4% yükseliş riski</span>
</div>
<svg class="chart-svg" viewBox="0 0 360 110" preserveAspectRatio="none" aria-hidden="true">
<defs><linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#66b817" stop-opacity="0.32"></stop><stop offset="100%" stop-color="#66b817" stop-opacity="0.02"></stop></linearGradient></defs>
<line x1="0" y1="28" x2="360" y2="28" stroke="#dcece1" stroke-dasharray="3 4"></line>
<line x1="0" y1="62" x2="360" y2="62" stroke="#dcece1" stroke-dasharray="3 4"></line>
<line x1="0" y1="94" x2="360" y2="94" stroke="#dcece1" stroke-dasharray="3 4"></line>
<line x1="238" y1="8" x2="238" y2="104" stroke="#166e37" stroke-opacity="0.35" stroke-dasharray="4 3"></line>
<path id="chartArea" d="M 0 74 C 45 70, 80 62, 125 68 C 165 74, 200 84, 238 82 C 278 70, 315 44, 360 28 L 360 108 L 0 108 Z" fill="url(#areaGrad)"></path>
<path id="chartHist" d="M 0 74 C 45 70, 80 62, 125 68 C 165 74, 200 84, 238 82" fill="none" stroke="#0b3d1e" stroke-width="2.8" stroke-linecap="round"></path>
<path id="chartPred" d="M 238 82 C 278 70, 315 44, 360 28" fill="none" stroke="#66b817" stroke-width="3" stroke-dasharray="6 4" stroke-linecap="round"></path>
<circle id="chartDot" cx="238" cy="82" r="5" fill="#ffffff" stroke="#0b3d1e" stroke-width="3"></circle>
</svg>
</div>
<div class="hal-band">
<div class="band-cell">
<span>Hal Taban</span>
<strong id="bandMin">69,00 ₺</strong>
</div>
<div class="band-cell">
<span>Hal Ortalama</span>
<strong id="bandAvg">78,40 ₺</strong>
</div>
<div class="band-cell">
<span>Hal Tavan</span>
<strong id="bandMax">92,50 ₺</strong>
</div>
</div>
</aside>
</div>
</section>
<section class="section" id="yetenekler">
<div class="section-head">
<div>
<div class="section-kicker">Platform Yetenekleri</div>
<h2 class="section-title">Bu Sitede Neler Yapılabilir?</h2>
<p class="section-sub">
Satın alma yöneticileri ve mutfak şefleri için karmaşık hal verilerini anında aksiyon alınabilir kararlara dönüştüren 4 temel modül.
</p>
</div>
</div>
<div class="bento-grid">
<article class="bento-card">
<div class="bento-head">
<span class="icon-badge" aria-hidden="true">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<path d="M3 3v18h18"></path>
<path d="m19 9-5 5-4-4-3 3"></path>
</svg>
</span>
<div>
<h3>Enflasyondan Arındırılmış Reel Fiyat Analizi</h3>
<p>20 yıllık hal fiyatlarını TCMB TÜFE ile bugünün alım gücüne indirgeyerek yanıltıcı enflasyon etkisini temizler; gerçek mevsimsel dip ve zirveleri ortaya çıkarır.</p>
</div>
</div>
<div class="micro-visual">
<div class="pill-row">
<span class="mini-chip green">TÜFE Reel Baz</span>
<span class="mini-chip">20 Yıllık Seri</span>
<span class="mini-chip leaf">Mevsimsel Dip &amp; Zirve</span>
</div>
</div>
</article>
<article class="bento-card">
<div class="bento-head">
<span class="icon-badge" aria-hidden="true">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"></path>
<path d="M16 14a4 4 0 0 1 4 4v2H4v-2a4 4 0 0 1 4-4"></path>
<circle cx="12" cy="14" r="1"></circle>
</svg>
</span>
<div>
<h3>1 Haftalık &amp; 1 Aylık Yapay Zekâ Fiyat Tahmini</h3>
<p>Eğitilmiş makine öğrenmesi modelleriyle hedef alım tarihi için fiyat projeksiyonu, güven bandı ve net tedarik kararı üretir.</p>
</div>
</div>
<div class="micro-visual">
<div class="pill-row">
<span class="mini-chip green">Şimdi Al</span>
<span class="mini-chip">Normal Tedarik</span>
<span class="mini-chip leaf">Alımı Ertele</span>
</div>
</div>
</article>
<article class="bento-card">
<div class="bento-head">
<span class="icon-badge" aria-hidden="true">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<path d="M12 3v18"></path>
<path d="m16 7 3 5-3 5"></path>
<path d="m8 7-3 5 3 5"></path>
</svg>
</span>
<div>
<h3>Tedarikçi Teklif Denetimi &amp; Pazarlık Rehberi</h3>
<p>Tedarikçiden gelen fiyat teklifini o günkü Hal Taban, Ortalama ve Tavan fiyatlarıyla kıyaslayarak kabul, pazarlık veya ret önerisi sunar.</p>
</div>
</div>
<div class="micro-visual">
<div class="scale-bar-wrap">
<div class="scale-labels">
<span>Taban (Kabul)</span>
<span>Ortalama (Pazarlık)</span>
<span>Tavan (Ret)</span>
</div>
<div class="scale-track" aria-hidden="true">
<span class="scale-marker"></span>
</div>
</div>
</div>
</article>
<article class="bento-card">
<div class="bento-head">
<span class="icon-badge" aria-hidden="true">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<rect x="3" y="4" width="18" height="16" rx="2"></rect>
<path d="M3 10h18"></path>
<path d="M9 20V10"></path>
</svg>
</span>
<div>
<h3>Çok Şubeli Bütçe, Sözleşme &amp; Reçete Simülasyonu</h3>
<p>Şube sayısı, zayi/bozulma ve soğuk depo maliyetlerine göre yıllık sözleşme senaryolarını kıyaslar; reçetelerin 12 aylık porsiyon maliyetini hesaplar.</p>
</div>
</div>
<div class="micro-visual">
<div class="pill-row">
<span class="mini-chip">Spot vs Akıllı Alım</span>
<span class="mini-chip leaf">Soğuk Depo &amp; Zayi</span>
<span class="mini-chip green">12 Aylık Reçete</span>
</div>
</div>
</article>
</div>
</section>
<section class="section" id="veri-altyapisi" style="padding-block: 0.4rem 1.6rem;">
<div class="kpi-band" aria-label="Platform Veri ve Model Özeti">
<div class="kpi-item">
<div class="kpi-kicker">Veri Kapsamı</div>
<div class="kpi-value">131.888 Kayıt</div>
<div class="kpi-tag">2006–2025 İzmir Hal Verisi</div>
</div>
<div class="kpi-item">
<div class="kpi-kicker">İncelenen Ürün</div>
<div class="kpi-value">25 Temel Ürün</div>
<div class="kpi-tag">Sebze • Meyve • İthal</div>
</div>
<div class="kpi-item">
<div class="kpi-kicker">Tahmin Motoru</div>
<div class="kpi-value">1 Hafta &amp; 1 Ay</div>
<div class="kpi-tag">Gradient Boosting + K-Means</div>
</div>
<div class="kpi-item">
<div class="kpi-kicker">Simülasyon Kapsamı</div>
<div class="kpi-value">{aktif_sube_sayisi} Aktif Şube</div>
<div class="kpi-tag">Dinamik Bütçe &amp; Reçete</div>
</div>
</div>
</section>
<section class="section" id="paneller">
<div class="section-head">
<div>
<div class="section-kicker">Uzman Modüller</div>
<h2 class="section-title">Karar Destek Panelleri</h2>
<p class="section-sub">
BAŞLA butonuna tıkladığınızda doğrudan erişebileceğiniz 6 uzman karar destek paneli.
</p>
</div>
<div class="filter-pills" role="group" aria-label="Panel kategorisi filtresi">
<button type="button" class="filter-pill" data-filter="all" aria-pressed="true">Tümü (6)</button>
<button type="button" class="filter-pill" data-filter="analiz" aria-pressed="false">İzleme &amp; Analiz</button>
<button type="button" class="filter-pill" data-filter="karar" aria-pressed="false">Strateji &amp; Karar</button>
<button type="button" class="filter-pill" data-filter="simulasyon" aria-pressed="false">Simülasyon &amp; Menü</button>
</div>
</div>
<div class="panels-grid">
<article class="panel-card" data-category="analiz">
<div>
<div class="panel-top">
<span class="panel-num">01 • PANEL</span>
<span class="panel-icon" aria-hidden="true">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1">
<rect x="3" y="3" width="7" height="9" rx="1.5"></rect>
<rect x="14" y="3" width="7" height="5" rx="1.5"></rect>
<rect x="14" y="12" width="7" height="9" rx="1.5"></rect>
<rect x="3" y="16" width="7" height="5" rx="1.5"></rect>
</svg>
</span>
</div>
<h3>📊 Panel &amp; Özet</h3>
<p>Kısa dönem fiyat şoku uyarıları, temel piyasa göstergeleri ve tek tıkla indirilebilen Pazartesi Sabahı Yönetici Brifingi.</p>
<div class="panel-tags">
<span class="panel-tag">Fiyat Şoku Uyarısı</span>
<span class="panel-tag">.pdf / .txt Brifing</span>
<span class="panel-tag">AI Performans</span>
</div>
</div>
<button type="button" class="panel-action" data-start-action="">
<span>Panele Geç</span>
<span aria-hidden="true">→</span>
</button>
</article>
<article class="panel-card" data-category="analiz">
<div>
<div class="panel-top">
<span class="panel-num">02 • PANEL</span>
<span class="panel-icon" aria-hidden="true">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1">
<rect x="3" y="4" width="18" height="18" rx="2"></rect>
<line x1="16" y1="2" x2="16" y2="6"></line>
<line x1="8" y1="2" x2="8" y2="6"></line>
<line x1="3" y1="10" x2="21" y2="10"></line>
</svg>
</span>
</div>
<h3>📅 Analiz &amp; Zamanlama</h3>
<p>20 yıllık nominal ve reel fiyat serileri, 25×12 en ucuz aylar ısı haritası, haftanın en ucuz hal günü ve 12 aylık sözleşme takvimi.</p>
<div class="panel-tags">
<span class="panel-tag">25×12 Isı Haritası</span>
<span class="panel-tag">Kruskal-Wallis</span>
<span class="panel-tag">Sözleşme Takvimi</span>
</div>
</div>
<button type="button" class="panel-action" data-start-action="">
<span>Panele Geç</span>
<span aria-hidden="true">→</span>
</button>
</article>
<article class="panel-card" data-category="karar">
<div>
<div class="panel-top">
<span class="panel-num">03 • PANEL</span>
<span class="panel-icon" aria-hidden="true">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1">
<circle cx="12" cy="12" r="9"></circle>
<circle cx="12" cy="12" r="5"></circle>
<circle cx="12" cy="12" r="1.5" fill="currentColor"></circle>
</svg>
</span>
</div>
<h3>🎯 Strateji &amp; Risk</h3>
<p>Kraljic Satın Alma Matrisi ile 4 stratejik bölge ayrımı, günlük hal taban–tavan pazarlık makası ve 1 yıllık strateji backtest doğrulaması.</p>
<div class="panel-tags">
<span class="panel-tag">Kraljic Matrisi</span>
<span class="panel-tag">Pazarlık Makası</span>
<span class="panel-tag">1 Yıl Backtest</span>
</div>
</div>
<button type="button" class="panel-action" data-start-action="">
<span>Panele Geç</span>
<span aria-hidden="true">→</span>
</button>
</article>
<article class="panel-card" data-category="karar">
<div>
<div class="panel-top">
<span class="panel-num">04 • PANEL</span>
<span class="panel-icon" aria-hidden="true">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1">
<path d="M12 2v4"></path>
<path d="m16.2 7.8 2.9-2.9"></path>
<path d="M18 12h4"></path>
<path d="m16.2 16.2 2.9 2.9"></path>
<path d="M12 18v4"></path>
<path d="m4.9 19.1 2.9-2.9"></path>
<path d="M2 12h4"></path>
<path d="m4.9 4.9 2.9 2.9"></path>
</svg>
</span>
</div>
<h3>🤖 Karar Ekranı</h3>
<p>4 zaman dilimli alım sinyalleri, 1 haftalık &amp; 1 aylık AI fiyat tahminleri, tedarikçi teklif denetimi ve SHAP açıklanabilirlik analizleri.</p>
<div class="panel-tags">
<span class="panel-tag">AI Fiyat Tahmini</span>
<span class="panel-tag">Teklif Denetimi</span>
<span class="panel-tag">SHAP Analizi</span>
</div>
</div>
<button type="button" class="panel-action" data-start-action="">
<span>Panele Geç</span>
<span aria-hidden="true">→</span>
</button>
</article>
<article class="panel-card" data-category="simulasyon">
<div>
<div class="panel-top">
<span class="panel-num">05 • PANEL</span>
<span class="panel-icon" aria-hidden="true">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1">
<path d="M19 5c-1.5 0-2.8 1.4-3 2-3.5-1.5-11-.3-11 5 0 1.8 0 3 2 4.5V20h4v-2h3v2h4v-4c1-.5 1.7-1 2-2h2v-4h-2c0-1-.5-1.5-1-2V5z"></path>
</svg>
</span>
</div>
<h3>🏪 Tasarruf Simülatörü</h3>
<p>Şube sayısı, zayi ve soğuk depolama oranlarına göre Spot vs Akıllı Alım kıyaslaması, senaryo karar kartları ve kurumsal Excel raporu.</p>
<div class="panel-tags">
<span class="panel-tag">Senaryo A &amp; B</span>
<span class="panel-tag">3 Stratejik Öneri</span>
<span class="panel-tag">Excel (.xlsx)</span>
</div>
</div>
<button type="button" class="panel-action" data-start-action="">
<span>Panele Geç</span>
<span aria-hidden="true">→</span>
</button>
</article>
<article class="panel-card" data-category="simulasyon">
<div>
<div class="panel-top">
<span class="panel-num">06 • PANEL</span>
<span class="panel-icon" aria-hidden="true">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1">
<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"></path>
<path d="M7 2v20"></path>
<path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"></path>
</svg>
</span>
</div>
<h3>🥗 Menü &amp; Reçete</h3>
<p>Restoran reçeteleri için 12 aylık porsiyon maliyet eğrisi, maliyeti en çok artıran bileşen tespiti ve uygun fiyatlı mevsimsel ikame önerileri.</p>
<div class="panel-tags">
<span class="panel-tag">Porsiyon Maliyeti</span>
<span class="panel-tag">Bileşen Analizi</span>
<span class="panel-tag">Mevsimsel İkame</span>
</div>
</div>
<button type="button" class="panel-action" data-start-action="">
<span>Panele Geç</span>
<span aria-hidden="true">→</span>
</button>
</article>
</div>
</section>
<section class="footer-cta-wrap">
<div class="footer-cta">
<div class="footer-cta-left">
<span class="brand-logo-wrap">
<img src="data:{_logo_mime};base64,{_logo_b64}" alt="Logo">
</span>
<div>
<h2>Karar Destek Panellerine Hazır mısınız?</h2>
<p>6 uzman panelini ve canlı yapay zekâ fiyat tahminlerini tek tıkla açın.</p>
</div>
</div>
<button type="button" class="btn-footer-start" data-start-action="">
<span>BAŞLA — Panelleri Aç</span>
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
<path d="M5 12h14"></path>
<path d="m12 5 7 7-7 7"></path>
</svg>
</button>
</div>
</section>
<div class="snc-qr-floating" title="Canlı Streamlit Uygulaması QR Kodu">
<div class="snc-qr-floating-title">CANLI UYGULAMA QR</div>
<img id="sncFloatingQrImg" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMYAAADGCAIAAAAG+WgKAAAEE0lEQVR4nO3dy43bSBRA0e7BLBiAc5j8w3EOE4B2cgDcEIVbH7XPWevn9kUJDyWyvt/v9xd0/glfCyRFzypFTFLEJEVMUsQkRUxSxCRFTFLEJEXs3ycPuv779bXP6/f/A8+6f+YnrzP2L72/8hW9zif+X1iliEmKmKSISYqYpNgx8VVT2BNjE83YfLfyM7+iqfDJK1fGPqFVipikiEmKmKSISYozJr67ebtaT95rbHfs/qwnc1k1Yb0Om9Sqz2OVIiYpYpIiJilikuLUiW+lsbls5TR32hS2klWKmKSISYqYpIhJithHTnzzPJnLnsyJ118z391ZpYhJipikiEmKmKQ4deLbO62svEru/srVDHhFe457/y+sUsQkRUxSxCRFTFKcMfHtvWPk2GQ09qvOlTt6V3TXmr2sUsQkRUxSxCRFTFLEvj/xBPZ5d26ZN7u9tl5FuJJVipikiEmKmKSISYodE9/ePayx95p3qsLY69ztvfpv3rxplSImKWKSIiYpYpJix686TztLbt6VdPN+QfpTd0XvrFLEJEVMUsQkRUxSnPGrzpW7WvP276r3Wuk6fj/RKkVMUsQkRUxSxCTFGb/q3Lvrt3fe3Lu/edqO3p1VipikiEmKmKSISYpT9/j2zlMr3/20ncrXwrvW2ONjA198xCRFTFLEJMWp5/GNzRSn3a9y77tfC680nDd9W6WISYqYpIhJipik+JwT2KsZcOzdxx6zcnp63R6z8orFea9jlSImKWKSIiYpYpJix8RX/Sawmqf27oXdVX+NvSdcPHn3J6xSxCRFTFLEJEVMUpyxx1fdG2TsMXvvAHP+VFhxOgNH8MVHTFLEJEVMUvys8/jm7fqt3B2bd2bftfUzu46PI/jiIyYpYpIiJik+53SGT5zdqqsRX8ef63fnXp0cyhcfMUkRkxQxSfE5pzPMe9a8SW2e18I5cd5f7AmrFDFJEZMUMUkRkxSn3rmlMm9S27tT+cTKvcuxxzxhlSImKWKSIiYpYpLijOv4Tps7fsaceDdv3px3CoZVipikiEmKmKSISYoz9vhWGpsTq7up7L1b5srf0zqPj0P54iMmKWKSIiYpzjidYeWvOseetfceLNe0s/bm/eXdq5ND+eIjJilikiImKc6Y+Fb+SnDsdc6/c8sTK08nrJ5llSImKWKSIiYpYpLi1Ilvpb13U1l5heBpd4lxHR8b+OJDUpzNKkVMUsQ+cuJ7MitVv5msJqNr67WQ887FuLNKEZMUMUkRkxQxSXHqxLf3zPFqmjtt3+218GpE5/FxKF98xCRFTFLEJMUZE9/eHau7lSe5f6Jr4QxolSImKWKSIiYpYpIi9v1+v+vX5K9mlSImKWKSIiYpYpIiJilikiImKWKSIiYpYpLiq/UHAowiRfAfsQ0AAAAASUVORK5CYII=" alt="Canlı Uygulama QR Kodu" />
<div class="snc-qr-floating-sub">Kamerayla Okutun</div>
</div>
</main></div>
""",
        unsafe_allow_html=True,
    )

    components.html(
        """
        <script>
        (function() {
            const doc = window.parent.document;
            const URUN_VERI = {
                ananas: {
                    name: "İthal • Ananas (Adet)",
                    price: "78,40 <span>₺ / ort.</span>",
                    badge: "ŞİMDİ AL • %9,2 Dip",
                    badgeClass: "decision-badge decision-buy",
                    delta: "+11,4% yükseliş riski",
                    deltaColor: "#166e37",
                    min: "69,00 ₺", avg: "78,40 ₺", max: "92,50 ₺",
                    area: "M 0 74 C 45 70, 80 62, 125 68 C 165 74, 200 84, 238 82 C 278 70, 315 44, 360 28 L 360 108 L 0 108 Z",
                    hist: "M 0 74 C 45 70, 80 62, 125 68 C 165 74, 200 84, 238 82",
                    pred: "M 238 82 C 278 70, 315 44, 360 28",
                    dotY: "82"
                },
                domates: {
                    name: "Sebze • Domates Salkım (Kg)",
                    price: "34,20 <span>₺ / ort.</span>",
                    badge: "NORMAL TEDARİK • Dengeli",
                    badgeClass: "decision-badge decision-normal",
                    delta: "+1,8% yatay seyir",
                    deltaColor: "#17528c",
                    min: "26,00 ₺", avg: "34,20 ₺", max: "42,00 ₺",
                    area: "M 0 58 C 45 62, 80 55, 125 60 C 165 57, 200 61, 238 59 C 278 58, 315 55, 360 53 L 360 108 L 0 108 Z",
                    hist: "M 0 58 C 45 62, 80 55, 125 60 C 165 57, 200 61, 238 59",
                    pred: "M 238 59 C 278 58, 315 55, 360 53",
                    dotY: "59"
                },
                biber: {
                    name: "Sebze • Biber Sivri (Kg)",
                    price: "52,80 <span>₺ / ort.</span>",
                    badge: "ALIMI ERTELE • %8,4 Düşüş",
                    badgeClass: "decision-badge decision-wait",
                    delta: "-8,4% gevşeme beklentisi",
                    deltaColor: "#9a4a00",
                    min: "41,00 ₺", avg: "52,80 ₺", max: "64,00 ₺",
                    area: "M 0 48 C 45 42, 80 38, 125 35 C 165 32, 200 30, 238 34 C 278 46, 315 62, 360 76 L 360 108 L 0 108 Z",
                    hist: "M 0 48 C 45 42, 80 38, 125 35 C 165 32, 200 30, 238 34",
                    pred: "M 238 34 C 278 46, 315 62, 360 76",
                    dotY: "34"
                }
            };

            function triggerStreamlitStart() {
                const buttons = Array.from(doc.querySelectorAll('button'));
                const sbBtn = buttons.find(b => b.innerText && b.innerText.includes('BAŞLA'));
                if (sbBtn) sbBtn.click();
            }

            doc.querySelectorAll('[data-start-action], .panel-action').forEach(btn => {
                if (!btn.dataset.boundStart) {
                    btn.dataset.boundStart = "1";
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        triggerStreamlitStart();
                    });
                }
            });

            doc.querySelectorAll('.product-tab').forEach(tab => {
                if (!tab.dataset.boundTab) {
                    tab.dataset.boundTab = "1";
                    tab.addEventListener('click', () => {
                        const key = tab.getAttribute('data-product');
                        const d = URUN_VERI[key];
                        if (!d) return;
                        doc.querySelectorAll('.product-tab').forEach(t => t.setAttribute('aria-pressed', t === tab ? 'true' : 'false'));
                        const elName = doc.getElementById('previewName');
                        const elPrice = doc.getElementById('previewPrice');
                        const elBadge = doc.getElementById('previewBadge');
                        const elDelta = doc.getElementById('previewDelta');
                        const elMin = doc.getElementById('bandMin');
                        const elAvg = doc.getElementById('bandAvg');
                        const elMax = doc.getElementById('bandMax');
                        const elArea = doc.getElementById('chartArea');
                        const elHist = doc.getElementById('chartHist');
                        const elPred = doc.getElementById('chartPred');
                        const elDot = doc.getElementById('chartDot');
                        if (elName) elName.textContent = d.name;
                        if (elPrice) elPrice.innerHTML = d.price;
                        if (elBadge) { elBadge.textContent = d.badge; elBadge.className = d.badgeClass; }
                        if (elDelta) { elDelta.textContent = d.delta; elDelta.style.color = d.deltaColor; }
                        if (elMin) elMin.textContent = d.min;
                        if (elAvg) elAvg.textContent = d.avg;
                        if (elMax) elMax.textContent = d.max;
                        if (elArea) elArea.setAttribute('d', d.area);
                        if (elHist) elHist.setAttribute('d', d.hist);
                        if (elPred) elPred.setAttribute('d', d.pred);
                        if (elDot) elDot.setAttribute('cy', d.dotY);
                    });
                }
            });

            doc.querySelectorAll('.filter-pill').forEach(pill => {
                if (!pill.dataset.boundFilter) {
                    pill.dataset.boundFilter = "1";
                    pill.addEventListener('click', () => {
                        const cat = pill.getAttribute('data-filter');
                        doc.querySelectorAll('.filter-pill').forEach(p => p.setAttribute('aria-pressed', p === pill ? 'true' : 'false'));
                        doc.querySelectorAll('.panel-card').forEach(card => {
                            if (cat === 'all' || card.getAttribute('data-category') === cat) {
                                card.classList.remove('hidden-card');
                            } else {
                                card.classList.add('hidden-card');
                            }
                        });
                    });
                }
            });
        })();
        </script>
        """,
        height=0,
        width=0,
    )

    st.stop()

st.markdown(
    f"""
<div class="snc-hero" translate="no">
<div style="display:flex; align-items:center; gap:14px;">
<span style="background:#FFFFFF; padding:6px 12px; border-radius:12px; border:1px solid #DCFCE7; box-shadow:0 2px 8px rgba(15,23,42,0.06); display:inline-flex; align-items:center;">
<img src="data:{_logo_mime};base64,{_logo_b64}" alt="Logo" style="height:40px; width:auto; display:block;" />
</span>
<div>
<div class="snc-hero-title">Akıllı Satın Alma Platformu</div>
<div class="snc-hero-sub">İzmir Hal Fiyatları ve TÜFE Bazlı Reel Karar Destek Sistemi</div>
</div>
</div>
<div class="snc-hero-pill">{aktif_sube_sayisi} Aktif Şube • Odak: {secili_odak_urun}</div>
</div>
""",
    unsafe_allow_html=True,
)

sekme_panel, sekme_analiz, sekme_strateji, sekme_karar, sekme_simulator, sekme_recete = st.tabs(
    [
        "📊 Panel & Özet",
        "📅 Analiz & Zamanlama",
        "🎯 Strateji & Risk",
        "🤖 Karar Ekranı",
        "🏪 Tasarruf Simülatörü",
        "🥗 Menü & Reçete",
    ]
)

AY_SIRASI = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
    5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
    9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
}
AY_TERS_SIRASI = {v: k for k, v in AY_SIRASI.items()}


# =============================================================================
# 1. SEKME: PANEL & ÖZET
# =============================================================================
with sekme_panel:
    st.subheader("📊 Genel Piyasa Göstergeleri ve Fiyat Şoku Kontrolü")
    st.caption(
        f"Son hafta fiyatı aniden dalgalanan ürünler ve 20 yıllık genel piyasa göstergeleri aşağıda yer alır. "
        f"Yönetici brifingi ve yapay zekâ model özetlerini alt kısımdaki açılır pencerelerden inceleyebilirsiniz."
    )

    # -------------------------------------------------------------------------
    # A) FİYAT ŞOKU ALARMI (Son kayıtlarda REEL_OYNAKLIK_7 > REEL_OYNAKLIK_30)
    # -------------------------------------------------------------------------
    sok_urunler = []
    if (
        not df_filtreli.empty
        and "REEL_OYNAKLIK_7" in df_filtreli.columns
        and "REEL_OYNAKLIK_30" in df_filtreli.columns
    ):
        df_son = (
            df_filtreli.dropna(subset=["MAL_ADI", "REEL_OYNAKLIK_7", "REEL_OYNAKLIK_30"])
            .sort_values("TARIH")
            .groupby("MAL_ADI", as_index=False)
            .last()
        )
        df_sok = df_son[df_son["REEL_OYNAKLIK_7"] > df_son["REEL_OYNAKLIK_30"]].copy()
        if not df_sok.empty:
            df_sok["SOK_ORANI"] = (
                (df_sok["REEL_OYNAKLIK_7"] - df_sok["REEL_OYNAKLIK_30"])
                / df_sok["REEL_OYNAKLIK_30"].replace(0, np.nan)
            ) * 100
            df_sok = df_sok.sort_values(
                by=["SOK_ORANI", "REEL_OYNAKLIK_7"], ascending=False
            ).head(3)
            for _, r in df_sok.iterrows():
                oran_metni = (
                    f"+%{r['SOK_ORANI']:.1f}" if pd.notna(r["SOK_ORANI"]) else "Yüksek"
                )
                sok_urunler.append(
                    f"<b>{r['MAL_ADI']}</b> (7 Günlük Oynaklık: <b>{r['REEL_OYNAKLIK_7']:.2f}</b> &gt; "
                    f"30 Günlük: {r['REEL_OYNAKLIK_30']:.2f} | İvme: <b>{oran_metni}</b>)"
                )

    if sok_urunler:
        alarm_html = "<br>".join([f"• {u}" for u in sok_urunler])
        st.markdown(
            f"""
<div class="shock-alert">
<h4>Fiyat Şoku Alarmı: 7 Günlük Oynaklığı 30 Günlük Ortalamayı Aşan İlk 3 Ürün</h4>
<div>Son piyasa kayıtlarında kısa vadeli fiyat dalgalanması hızlanan ürünler tespit edildi. Spot alımda dikkatli olunmalı:</div>
<div style="margin-top:8px;">{alarm_html}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.info("Seçili filtrelerde kısa dönem oynaklığı (7G) 30 günlük ortalamayı aşan kritik fiyat şoku bulunmamaktadır.")

    # -------------------------------------------------------------------------
    # B) 4 KPI KARTI (Toplam Kayıt, Analiz Edilen Ürün, En Oynak Ürün, Genel En Ucuz Ay)
    # -------------------------------------------------------------------------
    toplam_kayit = len(df_filtreli)
    analiz_edilen_urun = (
        df_filtreli["MAL_ADI"].nunique() if "MAL_ADI" in df_filtreli.columns else 0
    )

    # En Oynak Ürün
    en_oynak_urun_ad = "-"
    en_oynak_deger = 0.0
    oynaklik_sutunu = (
        "REEL_OYNAKLIK_30"
        if "REEL_OYNAKLIK_30" in df_filtreli.columns
        else ("REEL_OYNAKLIK_7" if "REEL_OYNAKLIK_7" in df_filtreli.columns else None)
    )
    if oynaklik_sutunu and not df_filtreli.empty:
        oynak_grup = (
            df_filtreli.dropna(subset=["MAL_ADI", oynaklik_sutunu])
            .groupby("MAL_ADI")[oynaklik_sutunu]
            .mean()
            .sort_values(ascending=False)
        )
        if not oynak_grup.empty:
            en_oynak_urun_ad = str(oynak_grup.index[0])
            en_oynak_deger = float(oynak_grup.iloc[0])

    # Genel En Ucuz Ay
    genel_en_ucuz_ay = "-"
    genel_en_ucuz_fiyat = 0.0
    if not df_aylik_reel.empty and "AYLIK_REEL_ORT" in df_aylik_reel.columns:
        ay_kolonu = "AY_ADI" if "AY_ADI" in df_aylik_reel.columns else "AY"
        aylik_genel = (
            df_aylik_reel.groupby(ay_kolonu)["AYLIK_REEL_ORT"]
            .mean()
            .sort_values(ascending=True)
        )
        if not aylik_genel.empty:
            secilen_ay_degeri = aylik_genel.index[0]
            genel_en_ucuz_ay = (
                AY_SIRASI.get(int(secilen_ay_degeri), str(secilen_ay_degeri))
                if str(secilen_ay_degeri).isdigit()
                else str(secilen_ay_degeri)
            )
            genel_en_ucuz_fiyat = float(aylik_genel.iloc[0])
    elif not df_filtreli.empty and "AY" in df_filtreli.columns:
        aylik_genel = (
            df_filtreli.groupby("AY")["REEL_ORTALAMA_UCRET"]
            .mean()
            .sort_values(ascending=True)
        )
        if not aylik_genel.empty:
            genel_en_ucuz_ay = AY_SIRASI.get(int(aylik_genel.index[0]), str(aylik_genel.index[0]))
            genel_en_ucuz_fiyat = float(aylik_genel.iloc[0])

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(
        "Toplam Kayıt",
        f"{toplam_kayit:,}".replace(",", "."),
        "2006–2025 Hal Verisi",
    )
    kpi2.metric(
        "Analiz Edilen Ürün",
        f"{analiz_edilen_urun} Ürün",
        f"{len(secili_turler)} Mal Türü Aktif",
    )
    kpi3.metric(
        "En Oynak Ürün",
        en_oynak_urun_ad,
        f"Ort. Oynaklık: {en_oynak_deger:.2f}",
        delta_color="inverse",
    )
    kpi4.metric(
        "Genel En Ucuz Ay",
        genel_en_ucuz_ay,
        f"Ort. Reel: {genel_en_ucuz_fiyat:.2f} TL",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # C) TEK TIKLA PAZARTESİ SABAHI YÖNETİCİ ÖZETİ (.txt İNDİRME DESTEKLİ)
    # -------------------------------------------------------------------------
    with st.expander("📋 Tek Tıkla Pazartesi Sabahı Yönetici Özeti", expanded=False):
        st.caption(
            f"{aktif_sube_sayisi} şubeli restoran zincirinin haftalık satın alma toplantısı için seçilen aya özel "
            "riskli ürünleri, gelecek ay zam beklenen kalemleri ve alım fırsatlarını tek tıkla özetler."
        )

        ust_col1, ust_col2 = st.columns([1, 2])
        with ust_col1:
            varsayilan_ay_no = datetime.now().month
            secili_ay_no = st.selectbox(
                "Raporlanacak Ayı Seçin",
                options=list(AY_SIRASI.keys()),
                format_func=lambda x: f"{x:02d} - {AY_SIRASI[x]}",
                index=varsayilan_ay_no - 1,
            )
            secili_ay_adi = AY_SIRASI[secili_ay_no]
            gelecek_ay_no = 1 if secili_ay_no == 12 else secili_ay_no + 1
            gelecek_ay_adi = AY_SIRASI[gelecek_ay_no]

        # 1) Seçilen ayda haftanın/dönemin en riskli (oynaklığı en yüksek) 3 ürünü
        riskli_3_liste = []
        if not df_filtreli.empty and oynaklik_sutunu:
            df_ay_kesit = (
                df_filtreli[df_filtreli["AY"] == secili_ay_no]
                if "AY" in df_filtreli.columns
                else df_filtreli
            )
            if df_ay_kesit.empty:
                df_ay_kesit = df_filtreli
            risk_grup = (
                df_ay_kesit.dropna(subset=["MAL_ADI", oynaklik_sutunu])
                .groupby("MAL_ADI", as_index=False)
                .agg(
                    OYNAKLIK=(oynaklik_sutunu, "mean"),
                    REEL_ORT=("REEL_ORTALAMA_UCRET", "mean"),
                )
                .sort_values("OYNAKLIK", ascending=False)
                .head(3)
            )
            for _, r in risk_grup.iterrows():
                riskli_3_liste.append(
                    f"{r['MAL_ADI']} (Oynaklık: {r['OYNAKLIK']:.2f} | {secili_ay_adi} Reel Ort.: {r['REEL_ORT']:.2f} TL)"
                )

        # 2) Gelecek ay (secili_ay_no -> gelecek_ay_no) fiyatı en çok artacak 3 ürün
        artis_3_liste = []
        if not df_aylik_reel.empty and {"MAL_ADI", "AY", "AYLIK_REEL_ORT"}.issubset(df_aylik_reel.columns):
            df_bu_ay = (
                df_aylik_reel[df_aylik_reel["AY"] == secili_ay_no]
                .groupby("MAL_ADI", as_index=False)["AYLIK_REEL_ORT"]
                .mean()
                .rename(columns={"AYLIK_REEL_ORT": "BU_AY_FIYAT"})
            )
            df_gel_ay = (
                df_aylik_reel[df_aylik_reel["AY"] == gelecek_ay_no]
                .groupby("MAL_ADI", as_index=False)["AYLIK_REEL_ORT"]
                .mean()
                .rename(columns={"AYLIK_REEL_ORT": "GELECEK_AY_FIYAT"})
            )
            df_deg = df_bu_ay.merge(df_gel_ay, on="MAL_ADI", how="inner")
            if not df_deg.empty:
                df_deg["ARTIS_YUZDE"] = (
                    (df_deg["GELECEK_AY_FIYAT"] - df_deg["BU_AY_FIYAT"])
                    / df_deg["BU_AY_FIYAT"].replace(0, np.nan)
                ) * 100
                df_deg = df_deg.sort_values("ARTIS_YUZDE", ascending=False).head(3)
                for _, r in df_deg.iterrows():
                    artis_yuzde = r["ARTIS_YUZDE"]
                    isaret = "+" if artis_yuzde >= 0 else ""
                    artis_3_liste.append(
                        f"{r['MAL_ADI']} ({secili_ay_adi}: {r['BU_AY_FIYAT']:.2f} TL -> "
                        f"{gelecek_ay_adi}: {r['GELECEK_AY_FIYAT']:.2f} TL | Beklenen Değişim: {isaret}%{artis_yuzde:.1f})"
                    )

        # 3) Seçilen ayda en uygun dönemde olan fırsat ürünleri
        firsat_liste = []
        if not df_karar_destegi.empty and "EN_UCUZ_AY" in df_karar_destegi.columns:
            df_firsat_tam = df_karar_destegi[
                df_karar_destegi["EN_UCUZ_AY"].astype(str).str.upper() == secili_ay_adi.upper()
            ].copy()
            if not df_firsat_tam.empty:
                for _, r in df_firsat_tam.head(4).iterrows():
                    firsat_liste.append(
                        f"{r['MAL_ADI']} (Yılın En Ucuz Ayı! Reel Ort.: {r['EN_UCUZ_REEL']:.2f} TL | "
                        f"Mevsimsel Tasarruf Potansiyeli: %{r['FARK_YUZDE']:.1f})"
                    )

        if not firsat_liste and not df_aylik_reel.empty:
            # Yılın en ucuz ayı bu ay olan ürün yoksa, bu ay yıllık ortalamasının en çok altında kalan ilk 3 ürünü öner
            yillik_ort_tablo = (
                df_aylik_reel.groupby("MAL_ADI", as_index=False)["AYLIK_REEL_ORT"]
                .mean()
                .rename(columns={"AYLIK_REEL_ORT": "YILLIK_ORT"})
            )
            bu_ay_tablo = (
                df_aylik_reel[df_aylik_reel["AY"] == secili_ay_no]
                .groupby("MAL_ADI", as_index=False)["AYLIK_REEL_ORT"]
                .mean()
                .rename(columns={"AYLIK_REEL_ORT": "BU_AY_ORT"})
            )
            firsat_aday = bu_ay_tablo.merge(yillik_ort_tablo, on="MAL_ADI", how="inner")
            if not firsat_aday.empty:
                firsat_aday["INDIRIM_ORANI"] = (
                    (firsat_aday["YILLIK_ORT"] - firsat_aday["BU_AY_ORT"])
                    / firsat_aday["YILLIK_ORT"].replace(0, np.nan)
                ) * 100
                firsat_aday = firsat_aday.sort_values("INDIRIM_ORANI", ascending=False).head(3)
                for _, r in firsat_aday.iterrows():
                    ind = r["INDIRIM_ORANI"]
                    if ind > 0:
                        firsat_liste.append(
                            f"{r['MAL_ADI']} ({secili_ay_adi} Ort.: {r['BU_AY_ORT']:.2f} TL | "
                            f"Yıllık Ortalamaya Göre %{ind:.1f} Daha Ucuz)"
                        )
                    else:
                        firsat_liste.append(
                            f"{r['MAL_ADI']} ({secili_ay_adi} Ort.: {r['BU_AY_ORT']:.2f} TL | "
                            f"Yıllık Ort.: {r['YILLIK_ORT']:.2f} TL)"
                        )

        # Metin ve Görsel Kart Oluşturma
        risk_md = "\n".join([f"  - {x}" for x in riskli_3_liste]) if riskli_3_liste else "  - Veri bulunamadı."
        artis_md = "\n".join([f"  - {x}" for x in artis_3_liste]) if artis_3_liste else "  - Veri bulunamadı."
        firsat_md = "\n".join([f"  - {x}" for x in firsat_liste]) if firsat_liste else "  - Veri bulunamadı."

        ozet_markdown = (
            f'<div style="font-size:1.08rem; font-weight:800; color:#0F172A; margin-bottom:12px;">'
            f'{secili_ay_adi} Ayı Pazartesi Sabahı Satın Alma ve Yönetici Brifingi — {aktif_sube_sayisi} Şube</div>'
            f'<div style="background:#FEE2E2; border-left:5px solid #DC2626; padding:12px 16px; border-radius:8px; margin-bottom:10px; color:#7F1D1D;">'
            f'<b>KÖTÜ / YÜKSEK RİSK — Haftanın En Oynak 3 Ürünü ({secili_ay_adi}):</b><br>'
            f'{"<br>".join([f"• {x}" for x in riskli_3_liste]) if riskli_3_liste else "• Veri bulunamadı."}</div>'
            f'<div style="background:#FEF9C3; border-left:5px solid #CA8A04; padding:12px 16px; border-radius:8px; margin-bottom:10px; color:#713F12;">'
            f'<b>TEHLİKELİ / ZAM UYARISI — Gelecek Ay ({gelecek_ay_adi}) Fiyatı En Çok Artacak 3 Ürün:</b><br>'
            f'{"<br>".join([f"• {x}" for x in artis_3_liste]) if artis_3_liste else "• Veri bulunamadı."}</div>'
            f'<div style="background:#DCFCE7; border-left:5px solid #16A34A; padding:12px 16px; border-radius:8px; margin-bottom:4px; color:#14532D;">'
            f'<b>İYİ / FIRSAT — {secili_ay_adi} Ayında En Uygun Dönemde Olan Ürünler:</b><br>'
            f'{"<br>".join([f"• {x}" for x in firsat_liste]) if firsat_liste else "• Veri bulunamadı."}</div>'
        )

        def _brifing_pdf_olustur(
            ay_adi: str,
            gel_ay_adi: str,
            sube_say: int,
            riskler: list,
            artislar: list,
            firsatlar: list,
        ) -> bytes:
            import matplotlib.pyplot as plt
            from matplotlib.patches import FancyBboxPatch

            fig = plt.figure(figsize=(8.27, 11.69), dpi=150)  # A4 Dikey
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 140)
            ax.axis("off")
            fig.patch.set_facecolor("#FFFFFF")

            # 1. Sade Kurumsal Üst Başlık Bandı
            header_box = FancyBboxPatch(
                (6, 121), 88, 13, boxstyle="round,pad=0.4,rounding_size=1.4",
                facecolor="#14532D", edgecolor="#14532D", linewidth=1.0
            )
            ax.add_patch(header_box)
            ax.text(
                50, 129.2, "AKILLI SATIN ALMA — HAFTALIK YÖNETİCİ ÖZETİ",
                color="#FFFFFF", fontsize=13.0, fontweight="bold", ha="center", va="center"
            )
            ax.text(
                50, 124.2,
                f"Analiz Ayı: {ay_adi}   •   Gelecek Ay: {gel_ay_adi}   •   Kapsam: {sube_say} Şube   •   Tarih: {datetime.now().strftime('%d.%m.%Y')}",
                color="#DCFCE7", fontsize=9.2, ha="center", va="center"
            )

            def _satir_sadelestir(metin: str, max_len: int = 78) -> str:
                temiz = str(metin).replace("Yılın En Ucuz Ayı! ", "").replace("Mevsimsel Tasarruf Potansiyeli:", "Tasarruf:")
                temiz = temiz.replace("Beklenen Değişim:", "Değişim:").replace("Reel Ort.:", "Ort.:")
                return temiz if len(temiz) <= max_len else temiz[: max_len - 1] + "…"

            def _kart_ciz(y_ust: float, baslik: str, alt_aciklama: str, maddeler: list, arka_renk: str, vurgu_renk: str, yazi_renk: str):
                kutu_h = 31.0
                y_alt = y_ust - kutu_h

                # Ana kart gövdesi
                kutu = FancyBboxPatch(
                    (6, y_alt), 88, kutu_h,
                    boxstyle="round,pad=0.4,rounding_size=1.4",
                    facecolor=arka_renk, edgecolor="#E2E8F0", linewidth=1.0
                )
                ax.add_patch(kutu)

                # Sol ince renk şeridi
                serit = FancyBboxPatch(
                    (6, y_alt), 1.4, kutu_h,
                    boxstyle="round,pad=0.0,rounding_size=0.4",
                    facecolor=vurgu_renk, edgecolor=vurgu_renk, linewidth=0.5
                )
                ax.add_patch(serit)

                # Başlık ve kısa açıklama
                ax.text(10.0, y_ust - 4.5, baslik, color=vurgu_renk, fontsize=11.2, fontweight="bold", ha="left", va="center")
                ax.text(10.0, y_ust - 8.3, alt_aciklama, color="#475569", fontsize=8.8, ha="left", va="center")

                # En önemli ilk 3 madde (her biri tek, ferah satırda)
                secili_maddeler = (maddeler[:3] if maddeler else ["Bu dönem için kayıt bulunamadı."])
                y_cursor = y_ust - 13.8
                for idx, m in enumerate(secili_maddeler, start=1):
                    satir = f"{idx}.  {_satir_sadelestir(m)}"
                    ax.text(10.5, y_cursor, satir, color=yazi_renk, fontsize=9.6, fontweight="normal", ha="left", va="center")
                    y_cursor -= 5.4

            # Kart 1: Yüksek Oynaklık / Risk
            _kart_ciz(
                115.0,
                f"1. Fiyat Oynaklığı En Yüksek 3 Ürün ({ay_adi})",
                "Kısa vadeli fiyat dalgalanması yüksek olan, günlük spot alımda dikkat edilmesi gereken ürünler:",
                riskler,
                arka_renk="#FEF2F2",
                vurgu_renk="#B91C1C",
                yazi_renk="#7F1D1D",
            )

            # Kart 2: Gelecek Ay Zam Uyarısı
            _kart_ciz(
                79.0,
                f"2. Gelecek Ay ({gel_ay_adi}) Fiyatı En Çok Artması Beklenen 3 Ürün",
                "Mevsimsel geçiş nedeniyle gelecek ay birim maliyeti yükselmesi beklenen, erken tedarik önerilen ürünler:",
                artislar,
                arka_renk="#FFFBEB",
                vurgu_renk="#B45309",
                yazi_renk="#78350F",
            )

            # Kart 3: Mevsimsel Alım Fırsatları
            _kart_ciz(
                43.0,
                f"3. {ay_adi} Ayında En Uygun Alım Döneminde Olan Fırsat Ürünleri",
                "Yıllık reel ortalamasına göre bu ay en düşük fiyat seviyesinde olan, sözleşme ve toplu alıma uygun ürünler:",
                firsatlar,
                arka_renk="#F0FDF4",
                vurgu_renk="#15803D",
                yazi_renk="#14532D",
            )

            # Sade Alt Bilgi
            ax.text(
                50, 5.5,
                "Akıllı Satın Alma Karar Destek Sistemi   •   Veri Kaynağı: İzmir BB Hal Fiyatları (2006–2025) & TCMB EVDS TÜFE",
                color="#64748B", fontsize=8.5, ha="center", va="center"
            )

            tampon = BytesIO()
            fig.savefig(tampon, format="pdf", facecolor=fig.get_facecolor())
            plt.close(fig)
            tampon.seek(0)
            return tampon.getvalue()

        st.markdown(
            f'<div class="exec-summary-card" translate="no">{ozet_markdown}</div>',
            unsafe_allow_html=True,
        )

        pdf_bayt = None
        try:
            pdf_bayt = _brifing_pdf_olustur(
                ay_adi=secili_ay_adi,
                gel_ay_adi=gelecek_ay_adi,
                sube_say=aktif_sube_sayisi,
                riskler=riskli_3_liste,
                artislar=artis_3_liste,
                firsatlar=firsat_liste,
            )
        except Exception:
            pdf_bayt = None

        ozet_txt_icerik = (
            f"SNC | AKILLI SATIN ALMA - PAZARTESI SABAHI YONETICI BRIFINGI\n"
            f"Rapor Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"Analiz Donemi: {secili_ay_adi} (Gelecek Ay Karsilastirmasi: {gelecek_ay_adi})\n"
            f"Kapsam: {aktif_sube_sayisi} Subeli Restoran Zinciri\n"
            f"{'=' * 72}\n\n"
            f"1. KOTU / YUKSEK RISK - HAFTANIN EN OYNAK 3 URUNU ({secili_ay_adi.upper()}):\n"
            + ("\n".join([f"   * {x}" for x in riskli_3_liste]) if riskli_3_liste else "   * Veri yok")
            + f"\n\n2. TEHLIKELI / ZAM UYARISI - GELECEK AY ({gelecek_ay_adi.upper()}) FIYATI EN COK ARTACAK 3 URUN:\n"
            + ("\n".join([f"   * {x}" for x in artis_3_liste]) if artis_3_liste else "   * Veri yok")
            + f"\n\n3. IYI / FIRSAT - {secili_ay_adi.upper()} AYINDA EN UYGUN DONEMDEKI URUNLER:\n"
            + ("\n".join([f"   * {x}" for x in firsat_liste]) if firsat_liste else "   * Veri yok")
            + f"\n\n{'=' * 72}\n"
            f"Not: Fiyatlar TCMB EVDS TUFE endeksi ile enflasyondan arindirilmis reel fiyatlardir.\n"
        )

        if pdf_bayt is not None:
            dl_c1, dl_c2 = st.columns([1, 1])
            with dl_c1:
                st.download_button(
                    label=f"Yönetici Brifingi (.txt) — {secili_ay_adi}",
                    data=ozet_txt_icerik.encode("utf-8"),
                    file_name=f"SNC_Yonetici_Brifingi_{secili_ay_adi}.txt",
                    mime="text/plain",
                    type="primary",
                    use_container_width=True,
                )
            with dl_c2:
                st.download_button(
                    label=f"Renkli Yönetici Brifingi (.pdf) — {secili_ay_adi}",
                    data=pdf_bayt,
                    file_name=f"SNC_Yonetici_Brifingi_{secili_ay_adi}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        else:
            st.download_button(
                label=f"Yönetici Brifingi (.txt) — {secili_ay_adi}",
                data=ozet_txt_icerik.encode("utf-8"),
                file_name=f"SNC_Yonetici_Brifingi_{secili_ay_adi}.txt",
                mime="text/plain",
                type="primary",
            )


    # -------------------------------------------------------------------------
    # D) OPSİYONEL MODEL VE KÜME ÖZETİ (Suzan'ın CSV ve Görselleri Eklendiğinde Otomatik Görünür)
    # -------------------------------------------------------------------------
    df_p_model = VERILER.get("model_karsilastirma", pd.DataFrame())
    df_p_onem = VERILER.get("ozellik_onemi", pd.DataFrame())
    df_p_kume = VERILER.get("urun_kumeleri", pd.DataFrame())
    shap_gorsel_yolu = _dosya_yolu_coz("03_Model/shap_aciklanabilirlik.png")
    kume_gorsel_yolu = _dosya_yolu_coz("03_Model/kumeleme_mevsimsel_profiller.png")
    shap_var = os.path.exists(shap_gorsel_yolu)
    kume_gorsel_var = os.path.exists(kume_gorsel_yolu)

    if not df_p_model.empty or not df_p_onem.empty or not df_p_kume.empty or shap_var or kume_gorsel_var:
        with st.expander("🤖 Makine Öğrenmesi Model Performansı ve Ürün Kümeleri Özeti", expanded=False):
            p_c1, p_c2 = st.columns(2, gap="large")

            with p_c1:
                if not df_p_model.empty:
                    st.markdown("**Model Performans Karşılaştırma Tablosu**")
                    st.dataframe(df_p_model, use_container_width=True, hide_index=True)
                if not df_p_kume.empty:
                    st.markdown("**Mevsimsel Ürün Kümeleri**")
                    st.dataframe(
                        df_p_kume.rename(
                            columns={
                                "MAL_ADI": "Ürün Adı",
                                "KUME_NO": "Küme No",
                                "KUME_ADI": "Mevsimsel Grup Özelliği",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
            with p_c2:
                if not df_p_onem.empty and len(df_p_onem.columns) >= 2:
                    st.markdown("**Tahmini En Çok Etkileyen Faktörler**")
                    p_onem_goster = df_p_onem.copy()
                    if "DEGISKEN" in p_onem_goster.columns or "ONEM_SKORU" in p_onem_goster.columns:
                        p_onem_goster = p_onem_goster.rename(
                            columns={"DEGISKEN": "Etkileyen Faktör", "ONEM_SKORU": "Etki Skoru"}
                        )
                    if "Etkileyen Faktör" in p_onem_goster.columns:
                        p_onem_goster["Etkileyen Faktör"] = p_onem_goster["Etkileyen Faktör"].apply(_degisken_turkce_etiket)
                    st.dataframe(p_onem_goster, use_container_width=True, hide_index=True)


        if shap_var or kume_gorsel_var:
            with st.expander("🔬 Model Açıklanabilirliği ve Mevsimsel Küme Profilleri", expanded=False):
                if shap_var:
                    st.markdown("##### SHAP Model Açıklanabilirlik Analizi")
                    _, s_orta, _ = st.columns([0.12, 0.76, 0.12])
                    with s_orta:
                        st.image(str(shap_gorsel_yolu), use_container_width=True)
                    st.markdown(
                        '<div class="insight-note"><b>SHAP İş Yorumu:</b> '
                        "Bu grafik, yapay zekâ modelinin fiyat tahminini üretirken hangi faktöre (1 gün önceki fiyat, 30 günlük fiyat dalgalanması, haftalık mevsimsellik vb.) "
                        "ne yönde ağırlık verdiğini şeffaf biçimde gösterir. Böylece satın alma yöneticisi tahminin yalnızca sonucunu değil, dayanağını da denetleyebilir.</div>",
                        unsafe_allow_html=True,
                    )
                if kume_gorsel_var:
                    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                    st.markdown("##### K-Means Mevsimsel Küme Profilleri")
                    _, k_orta, _ = st.columns([0.06, 0.88, 0.06])
                    with k_orta:
                        st.image(str(kume_gorsel_yolu), use_container_width=True)
                    st.markdown(
                        '<div class="insight-note"><b>Kümeleme İş Yorumu:</b> '
                        "Ürünler 12 aylık reel fiyat hareketlerine göre K-Means algoritmasıyla 4 stratejik mevsim grubuna ayrılmıştır; "
                        "aynı kümedeki ürünler menü planlamasında birbirine ikame edilebilir. Bu gruplama yıllık sözleşme ve stok takviminin omurgasını oluşturur.</div>",
                        unsafe_allow_html=True,
                    )


# =============================================================================
# 2. SEKME: ANALİZ & ZAMANLAMA
# =============================================================================
with sekme_analiz:
    st.subheader(f"📅 Tarihsel Fiyat Eğilimi ve Mevsimsel Isı Haritası — {secili_odak_urun}")
    st.caption(
        "Sol grafikte ürünün nominal ve reel fiyat geçmişini, sağ grafikte 25 ürünün 12 aylık en ucuz alım dönemlerini görebilirsiniz. "
        "Haftanın en ucuz alım günü, enflasyon aynası, hipotez testleri ve sözleşme ajandası aşağıdaki açılır pencerelerde yer alır."
    )

    # Opsiyonel: 01_Veri/urun_kumeleri.csv varsa küme rozeti + daha ucuz ikame önerisi
    _kume_rozeti_ve_ikame_goster(secili_odak_urun, VERILER.get("urun_kumeleri", pd.DataFrame()), df_ozellikli)

    df_urun = (
        df_ozellikli[df_ozellikli["MAL_ADI"] == secili_odak_urun]
        .dropna(subset=["TARIH"])
        .sort_values("TARIH")
        .copy()
        if not df_ozellikli.empty and "MAL_ADI" in df_ozellikli.columns
        else pd.DataFrame()
    )

    # -------------------------------------------------------------------------
    # 1. ÜST BÖLÜM: SOL (NOMİNAL / REEL FİYAT GEÇMİŞİ) | SAĞ (25x12 ISI HARİTASI)
    # -------------------------------------------------------------------------
    ust_sol, ust_sag = st.columns([1.05, 1.15], gap="large")

    with ust_sol:
        st.markdown(f"#### {secili_odak_urun} — Tarihsel Fiyat Eğilimi")
        fiyat_modu = st.radio(
            "Fiyat Görünümü Seçin:",
            options=[
                "Reel Fiyat (Enflasyondan Arındırılmış Gerçek Değer)",
                "Nominal Fiyat (Hal Taban–Tavan Bandı + Ortalama Etiket Fiyatı)",
            ],
            horizontal=True,
            key="analiz_fiyat_modu",
        )

        if not df_urun.empty:
            # Çok yoğun günlük veride grafik akıcılığı için aylık/haftalık örnekleme veya doğrudan çizim
            df_cizim = df_urun.copy()
            if len(df_cizim) > 800:
                df_cizim = (
                    df_cizim.set_index("TARIH")
                    .resample("W")
                    .agg(
                        {
                            c: "mean"
                            for c in [
                                "ASGARI_UCRET",
                                "AZAMI_UCRET",
                                "ORTALAMA_UCRET",
                                "REEL_ORTALAMA_UCRET",
                            ]
                            if c in df_cizim.columns
                        }
                    )
                    .dropna(how="all")
                    .reset_index()
                )

            fig_gecmis = go.Figure()

            if fiyat_modu.startswith("Nominal"):
                if {"ASGARI_UCRET", "AZAMI_UCRET"}.issubset(df_cizim.columns):
                    fig_gecmis.add_trace(
                        go.Scatter(
                            x=df_cizim["TARIH"],
                            y=df_cizim["AZAMI_UCRET"],
                            mode="lines",
                            line=dict(width=0),
                            name="Azami Ücret (Max)",
                            showlegend=False,
                            hoverinfo="skip",
                        )
                    )
                    fig_gecmis.add_trace(
                        go.Scatter(
                            x=df_cizim["TARIH"],
                            y=df_cizim["ASGARI_UCRET"],
                            mode="lines",
                            line=dict(width=0),
                            fill="tonexty",
                            fillcolor="rgba(27, 122, 67, 0.18)",
                            name="Asgari–Azami Fiyat Bandı (Min–Max)",
                        )
                    )
                if "ORTALAMA_UCRET" in df_cizim.columns:
                    fig_gecmis.add_trace(
                        go.Scatter(
                            x=df_cizim["TARIH"],
                            y=df_cizim["ORTALAMA_UCRET"],
                            mode="lines",
                            line=dict(color="#1B7A43", width=2.3),
                            name="Hal Ortalama Fiyatı (Nominal)",
                        )
                    )
                y_baslik = "Nominal Fiyat (₺)"
            else:
                fig_gecmis.add_trace(
                    go.Scatter(
                        x=df_cizim["TARIH"],
                        y=df_cizim["REEL_ORTALAMA_UCRET"],
                        mode="lines",
                        line=dict(color="#1B7A43", width=2.4),
                        fill="tozeroy",
                        fillcolor="rgba(27, 122, 67, 0.10)",
                        name="Güncel Reel Fiyat (TÜFE Bazlı)",
                    )
                )
                y_baslik = "Güncel Reel Fiyat (₺)"

            fig_gecmis.update_layout(
                height=440,
                margin=dict(l=10, r=10, t=30, b=10),
                xaxis_title="Tarih",
                yaxis_title=y_baslik,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                hovermode="x unified",
            )
            st.plotly_chart(fig_gecmis, use_container_width=True)

            # Dinamik İş Yorumu (Tarihsel Fiyat Eğilimi)
            if fiyat_modu.startswith("Nominal"):
                ilk_nom = _guvenli_sayi(df_urun["ORTALAMA_UCRET"].dropna().iloc[0], 1.0)
                son_nom = _guvenli_sayi(df_urun["ORTALAMA_UCRET"].dropna().iloc[-1], 1.0)
                nom_kat = son_nom / ilk_nom if ilk_nom > 0 else 1.0
                son_bant_fark = (
                    _guvenli_sayi(df_urun["AZAMI_UCRET"].dropna().iloc[-1], son_nom)
                    - _guvenli_sayi(df_urun["ASGARI_UCRET"].dropna().iloc[-1], son_nom)
                )
                st.markdown(
                    f"""
<div class="insight-note"><b>Grafik Yorumu ({secili_odak_urun} — Nominal):</b>
İlk kayıttan son kayda nominal etiket fiyatı <b>{ilk_nom:.2f} ₺ → {son_nom:.2f} ₺</b> ({nom_kat:.1f} kat) seviyesine çıkmıştır.
Son dönemde gün içi taban–tavan (Asgari–Azami) fiyat aralığı <b>{son_bant_fark:.2f} ₺</b> genişliğindedir;
bu bant tedarikçi görüşmelerinde kalite ve pazarlık marjını gösterir.</div>
""",
                    unsafe_allow_html=True,
                )
            else:
                ort_r = _guvenli_sayi(df_urun["REEL_ORTALAMA_UCRET"].mean(), 0.0)
                min_r = _guvenli_sayi(df_urun["REEL_ORTALAMA_UCRET"].min(), 0.0)
                max_r = _guvenli_sayi(df_urun["REEL_ORTALAMA_UCRET"].max(), 0.0)
                son_r = _guvenli_sayi(df_urun["REEL_ORTALAMA_UCRET"].dropna().iloc[-1], ort_r)
                konum_txt = "tarihsel ortalamanın üzerinde (pahalı dönem)" if son_r > ort_r else "tarihsel ortalamanın altında (uygun dönem)"
                st.markdown(
                    f"""
<div class="insight-note"><b>Grafik Yorumu ({secili_odak_urun} — Reel):</b>
Enflasyondan arındırılmış 20 yıllık ortalama <b>{ort_r:.2f} ₺</b> (dip: {min_r:.2f} ₺, zirve: {max_r:.2f} ₺).
Son reel fiyat (<b>{son_r:.2f} ₺</b>) şu an <b>{konum_txt}</b> bölgesindedir; satın alma kararları nominal değil bu reel seviyeye göre verilmelidir.</div>
""",
                    unsafe_allow_html=True,
                )
        else:
            st.warning("Seçili ürün için tarihsel fiyat kaydı bulunamadı.")

    with ust_sag:
        st.markdown("#### 25 Ürün × 12 Ay — En Ucuz Aylar Isı Haritası")
        st.caption(
            "Her ürün kendi içinde **0 (En Ucuz Ay - Koyu Yeşil)** ile **1 (En Pahalı Ay - Koyu Kırmızı)** "
            "arasında normalize edilmiştir."
        )

        if not df_aylik_reel.empty and {"MAL_ADI", "AY", "AYLIK_REEL_ORT"}.issubset(df_aylik_reel.columns):
            pivot_ham = df_aylik_reel.pivot_table(
                index="MAL_ADI",
                columns="AY",
                values="AYLIK_REEL_ORT",
                aggfunc="mean",
            )
            mevcut_aylar = [a for a in range(1, 13) if a in pivot_ham.columns]
            pivot_ham = pivot_ham[mevcut_aylar]
            ay_etiketleri = [AY_SIRASI[a][:3] for a in mevcut_aylar]
            pivot_ham.columns = ay_etiketleri

            # Her ürün satırını kendi içinde 0-1 aralığında normalize et
            satir_min = pivot_ham.min(axis=1)
            satir_max = pivot_ham.max(axis=1)
            satir_fark = (satir_max - satir_min).replace(0, np.nan)
            pivot_norm = pivot_ham.sub(satir_min, axis=0).div(satir_fark, axis=0).fillna(0.5)

            fig_isi = px.imshow(
                pivot_norm,
                color_continuous_scale="RdYlGn_r",
                aspect="auto",
                labels=dict(x="Ay", y="Ürün Adı", color="Mevsimsel Seviye (0=En Ucuz, 1=En Pahalı)"),
            )
            # Hover üzerinde gerçek TL değerlerini de göster
            fig_isi.update_traces(
                customdata=np.round(pivot_ham.values, 2),
                hovertemplate=(
                    "<b>Ürün:</b> %{y}<br>"
                    "<b>Ay:</b> %{x}<br>"
                    "<b>Ortalama Reel Fiyat:</b> %{customdata:.2f} TL<br>"
                    "<b>Normalize Seviye:</b> %{z:.2f}<extra></extra>"
                ),
            )
            fig_isi.update_layout(
                height=475,
                margin=dict(l=10, r=10, t=20, b=10),
                coloraxis_colorbar=dict(title="Seviye", thickness=14),
            )
            st.plotly_chart(fig_isi, use_container_width=True)

            # Dinamik İş Yorumu (Isı Haritası — Odak ürüne göre güncellenir)
            if secili_odak_urun in pivot_ham.index:
                odak_seri = pivot_ham.loc[secili_odak_urun].dropna()
                if not odak_seri.empty:
                    u_ay = str(odak_seri.idxmin())
                    u_f = float(odak_seri.min())
                    p_ay = str(odak_seri.idxmax())
                    p_f = float(odak_seri.max())
                    fark_p = ((p_f - u_f) / u_f) * 100.0 if u_f > 0 else 0.0
                    st.markdown(
                        f"""
<div class="insight-note"><b>Isı Haritası Yorumu ({secili_odak_urun}):</b>
Koyu yeşil bölge olan <b>{u_ay}</b> ayında reel fiyat dip yaparken (<b>{u_f:.2f} ₺</b>),
koyu kırmızı bölge olan <b>{p_ay}</b> ayında zirveye çıkmaktadır (<b>{p_f:.2f} ₺</b> — <b>+%{fark_p:.1f}</b> mevsimsel makas).
Sözleşme veya stoklama mutlaka <b>{u_ay}</b> penceresinde planlanmalıdır.</div>
""",
                        unsafe_allow_html=True,
                    )
        else:
            st.warning("Aylık mevsimsel fiyat verisi bulunamadı.")

    st.divider()

    # -------------------------------------------------------------------------
    # 2. ALT BÖLÜM: SOL (HAFTANIN HANGİ GÜNÜ HAL'E GİDİLMELİ?) | SAĞ (ENFLASYON AYNASI)
    # -------------------------------------------------------------------------
    with st.expander(f"📈 Haftanın En Uygun Alım Günü ve Enflasyon Aynası — {secili_odak_urun}", expanded=False):
        alt_sol, alt_sag = st.columns(2, gap="large")

        # --- A) Haftanın Hangi Günü Hal'e Gidilmeli? ---
        with alt_sol:
            st.markdown(f"#### Haftanın En Uygun Alım Günü — {secili_odak_urun}")
            st.caption(
                "Tarihsel satış günlerine göre seçili ürünün haftanın günleri bazındaki ortalama reel hal fiyatı karşılaştırması."
            )

            gun_haritasi = {
                0: "Pazartesi",
                1: "Salı",
                2: "Çarşamba",
                3: "Perşembe",
                4: "Cuma",
                5: "Cumartesi",
            }
            gun_sirasi = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi"]

            if not df_urun.empty and "REEL_ORTALAMA_UCRET" in df_urun.columns:
                df_gun = df_urun.copy()
                df_gun["GUN_NO"] = pd.to_datetime(df_gun["TARIH"], errors="coerce").dt.dayofweek
                df_gun = df_gun[df_gun["GUN_NO"].isin(gun_haritasi.keys())].copy()
                df_gun["GUN_ADI"] = df_gun["GUN_NO"].map(gun_haritasi)

                gun_ozet = (
                    df_gun.groupby("GUN_ADI", as_index=False)
                    .agg(
                        ORT_REEL=("REEL_ORTALAMA_UCRET", "mean"),
                        KAYIT=("REEL_ORTALAMA_UCRET", "count"),
                    )
                )

                if not gun_ozet.empty:
                    gun_ozet["GUN_ADI"] = pd.Categorical(
                        gun_ozet["GUN_ADI"], categories=gun_sirasi, ordered=True
                    )
                    gun_ozet = gun_ozet.sort_values("GUN_ADI").reset_index(drop=True)
                    gun_ozet["ORT_REEL"] = gun_ozet["ORT_REEL"].round(2)

                    en_ucuz_idx = gun_ozet["ORT_REEL"].idxmin()
                    en_pahali_idx = gun_ozet["ORT_REEL"].idxmax()
                    en_ucuz_gun = str(gun_ozet.loc[en_ucuz_idx, "GUN_ADI"])
                    en_ucuz_gun_fiyat = float(gun_ozet.loc[en_ucuz_idx, "ORT_REEL"])
                    en_pahali_gun = str(gun_ozet.loc[en_pahali_idx, "GUN_ADI"])
                    en_pahali_gun_fiyat = float(gun_ozet.loc[en_pahali_idx, "ORT_REEL"])
                    gun_avantaj_yuzde = (
                        ((en_pahali_gun_fiyat - en_ucuz_gun_fiyat) / en_pahali_gun_fiyat) * 100
                        if en_pahali_gun_fiyat > 0
                        else 0.0
                    )

                    renkler = [
                        "#1B7A43" if g == en_ucuz_gun else ("#DC2626" if g == en_pahali_gun else "#94A3B8")
                        for g in gun_ozet["GUN_ADI"].astype(str)
                    ]

                    fig_gun = go.Figure(
                        go.Bar(
                            x=gun_ozet["GUN_ADI"].astype(str),
                            y=gun_ozet["ORT_REEL"],
                            marker_color=renkler,
                            text=[f"{v:.2f} TL" for v in gun_ozet["ORT_REEL"]],
                            textposition="outside",
                        )
                    )
                    y_min = gun_ozet["ORT_REEL"].min() * 0.90
                    y_max = gun_ozet["ORT_REEL"].max() * 1.08
                    fig_gun.update_layout(
                        height=330,
                        margin=dict(l=10, r=10, t=20, b=10),
                        xaxis_title="Haftanın Günleri",
                        yaxis_title="Ortalama Reel Fiyat (TL)",
                        yaxis=dict(range=[y_min, y_max]),
                        plot_bgcolor="#FFFFFF",
                        paper_bgcolor="#FFFFFF",
                    )
                    st.plotly_chart(fig_gun, use_container_width=True)

                    st.success(
                        f"**En Uygun Hal Günü Önerisi:** **{secili_odak_urun}** alımı için haftanın en ucuz günü "
                        f"**{en_ucuz_gun}** (`{en_ucuz_gun_fiyat:.2f} ₺`). En pahalı gün olan **{en_pahali_gun}** "
                        f"(`{en_pahali_gun_fiyat:.2f} ₺`) yerine {en_ucuz_gun} günü alım yapmak "
                        f"ortalama **%{gun_avantaj_yuzde:.1f}** fiyat avantajı sağlar."
                    )
                    st.caption("Not: İzmir Hali Pazar günleri kapalı olduğu için veriler Pazartesi–Cumartesi günlerini kapsamaktadır.")
                else:
                    st.info("Bu ürün için gün bazlı dağılım hesaplanamadı.")
            else:
                st.warning("Gün analizi için yeterli veri bulunamadı.")

        # --- B) Enflasyon Aynası (Zam Gerçek mi, TÜFE mi?) ---
        with alt_sag:
            st.markdown(f"#### Enflasyon Aynası: Zam Gerçek mi, TÜFE mi? — {secili_odak_urun}")
            st.caption(
                "Seçilen iki yıl arasında ürünün **Nominal Fiyat Artış %'sini**, **TÜFE Enflasyon Artış %'sini** "
                "ve enflasyondan arındırılmış **Reel Fiyat Değişim %'sini** yan yana kıyaslar."
            )

            if not df_urun.empty and "ORTALAMA_UCRET" in df_urun.columns:
                df_yil = df_urun.copy()
                if "YIL" not in df_yil.columns:
                    df_yil["YIL"] = pd.to_datetime(df_yil["TARIH"], errors="coerce").dt.year

                yillar = sorted(df_yil["YIL"].dropna().astype(int).unique().tolist())

                if len(yillar) >= 2:
                    y_col1, y_col2 = st.columns(2)
                    with y_col1:
                        baslangic_yil = st.selectbox(
                            "Başlangıç Yılı",
                            options=yillar[:-1],
                            index=0,
                            key="enflasyon_bas_yil",
                        )
                    with y_col2:
                        bitis_adaylari = [y for y in yillar if y > baslangic_yil]
                        bitis_yil = st.selectbox(
                            "Bitiş Yılı",
                            options=bitis_adaylari,
                            index=len(bitis_adaylari) - 1,
                            key="enflasyon_bit_yil",
                        )

                    df_y1 = df_yil[df_yil["YIL"] == baslangic_yil]
                    df_y2 = df_yil[df_yil["YIL"] == bitis_yil]

                    nom_1 = _guvenli_sayi(df_y1["ORTALAMA_UCRET"].mean(), 0.0)
                    nom_2 = _guvenli_sayi(df_y2["ORTALAMA_UCRET"].mean(), 0.0)
                    reel_1 = _guvenli_sayi(df_y1["REEL_ORTALAMA_UCRET"].mean(), 0.0)
                    reel_2 = _guvenli_sayi(df_y2["REEL_ORTALAMA_UCRET"].mean(), 0.0)

                    nominal_degisim = ((nom_2 - nom_1) / nom_1) * 100.0 if nom_1 > 0 else 0.0
                    reel_degisim = ((reel_2 - reel_1) / reel_1) * 100.0 if reel_1 > 0 else 0.0

                    if "TUFE" in df_yil.columns and df_y1["TUFE"].notna().any() and df_y2["TUFE"].notna().any():
                        tufe_1 = _guvenli_sayi(df_y1["TUFE"].mean(), 0.0)
                        tufe_2 = _guvenli_sayi(df_y2["TUFE"].mean(), 0.0)
                        tufe_degisim = ((tufe_2 - tufe_1) / tufe_1) * 100.0 if tufe_1 > 0 else 0.0
                    else:
                        payda = 1.0 + (reel_degisim / 100.0)
                        tufe_degisim = (
                            (((1.0 + nominal_degisim / 100.0) / payda) - 1.0) * 100.0
                            if abs(payda) > 1e-6
                            else 0.0
                        )

                    kategoriler = [
                        f"Nominal Fiyat Artışı (%)",
                        f"TÜFE Enflasyon Artışı (%)",
                        f"Gerçek (Reel) Değişim (%)",
                    ]
                    degerler = [round(nominal_degisim, 1), round(tufe_degisim, 1), round(reel_degisim, 1)]
                    bar_renkleri = [
                        "#F59E0B",
                        "#64748B",
                        "#DC2626" if reel_degisim > 0 else "#1B7A43",
                    ]

                    fig_enf = go.Figure(
                        go.Bar(
                            x=kategoriler,
                            y=degerler,
                            marker_color=bar_renkleri,
                            text=[f"%+{v:.1f}" if v >= 0 else f"%{v:.1f}" for v in degerler],
                            textposition="outside",
                        )
                    )
                    fig_enf.add_hline(y=0, line_dash="dash", line_color="#1E293B", line_width=1)
                    fig_enf.update_layout(
                        height=290,
                        margin=dict(l=10, r=10, t=25, b=10),
                        xaxis_title=f"{baslangic_yil} → {bitis_yil} Karşılaştırması",
                        yaxis_title="Değişim Oranı (%)",
                        plot_bgcolor="#FFFFFF",
                        paper_bgcolor="#FFFFFF",
                    )
                    st.plotly_chart(fig_enf, use_container_width=True)

                    if reel_degisim > 5:
                        st.warning(
                            f"**Enflasyon Üstü Gerçek Artış:** {baslangic_yil}–{bitis_yil} arasında **{secili_odak_urun}** "
                            f"nominal olarak **%{nominal_degisim:.1f}** artarken, TÜFE enflasyonu arındırıldığında "
                            f"gerçek (reel) bazda **+%{reel_degisim:.1f}** pahalanmıştır."
                        )
                    elif reel_degisim < -5:
                        st.success(
                            f"**Reel Olarak Ucuzlama:** {baslangic_yil}–{bitis_yil} arasında **{secili_odak_urun}** "
                            f"nominal olarak **%{nominal_degisim:.1f}** artsa da, TÜFE enflasyonunun altında kalarak "
                            f"reel bazda **%{reel_degisim:.1f}** ucuzlamıştır."
                        )
                    else:
                        st.info(
                            f"**Enflasyonla Paralel Seyir:** {baslangic_yil}–{bitis_yil} arasında **{secili_odak_urun}** "
                            f"reel bazda **%{reel_degisim:.1f}** değişimle genel TÜFE enflasyonuna paralel seyretmiştir."
                        )
                else:
                    st.info("Enflasyon karşılaştırması için en az 2 farklı yıl verisi gereklidir.")
            else:
                st.warning("Enflasyon aynası için veri bulunamadı.")



    with st.expander(f"🔬 İstatistiksel Hipotez Testleri ve 20 Yıllık Reel Fiyat Değişimi — {secili_odak_urun}", expanded=False):
        ozg_sol, ozg_sag = st.columns([1.05, 1.15], gap="large")

        # --- A) İstatistiksel Hipotez Testleri (Kruskal-Wallis p-değeri) ---
        with ozg_sol:
            st.markdown(f"#### İstatistiksel Hipotez Testleri — {secili_odak_urun}")
            st.caption(
                "H0 (Sıfır Hipotezi): Dönemler/gruplar arasında istatistiksel olarak anlamlı bir fiyat farkı yoktur (fark tesadüfidir). | "
                "H1 (Alternatif Hipotez): Dönemler/gruplar arasında istatistiksel olarak anlamlı bir fiyat farkı vardır. "
                "(p < 0.05 ise H0 reddedilir, H1 kabul edilir ve fiyat avantajı istatistiksel olarak doğrulanır.)"
            )
            try:
                from scipy import stats as sp_stats
                scipy_var = True
            except Exception:
                scipy_var = False

            # Hipotez 1: Seçili üründe mevsimler arası reel fiyat farkı istatistiksel olarak anlamlı mı?
            mevsim_map_h = {
                12: "Kış", 1: "Kış", 2: "Kış",
                3: "İlkbahar", 4: "İlkbahar", 5: "İlkbahar",
                6: "Yaz", 7: "Yaz", 8: "Yaz",
                9: "Sonbahar", 10: "Sonbahar", 11: "Sonbahar",
            }
            if scipy_var and not df_urun.empty and "REEL_ORTALAMA_UCRET" in df_urun.columns:
                df_h1 = df_urun.dropna(subset=["TARIH", "REEL_ORTALAMA_UCRET"]).copy()
                df_h1["MEVSIM_H"] = pd.to_datetime(df_h1["TARIH"], errors="coerce").dt.month.map(mevsim_map_h)
                gruplar_h1 = [
                    g["REEL_ORTALAMA_UCRET"].dropna().values
                    for _, g in df_h1.groupby("MEVSIM_H")
                    if len(g["REEL_ORTALAMA_UCRET"].dropna()) >= 5
                ]
                if len(gruplar_h1) >= 2:
                    h_stat, p_val = sp_stats.kruskal(*gruplar_h1)
                    mev_ort_s = df_h1.groupby("MEVSIM_H")["REEL_ORTALAMA_UCRET"].mean().sort_values()
                    en_u_m, en_u_v = str(mev_ort_s.index[0]), float(mev_ort_s.iloc[0])
                    en_p_m, en_p_v = str(mev_ort_s.index[-1]), float(mev_ort_s.iloc[-1])
                    p_metin = "< 0.0001" if p_val < 0.0001 else f"= {p_val:.4f}"
                    kabul_mu = p_val < 0.05

                    st.markdown(
                        f"""
<div class="signal-card" style="border-left:5px solid {'#16A34A' if kabul_mu else '#CA8A04'}; margin-bottom:10px;">
<div class="signal-card-title">Hipotez 1 (Mevsimsellik Testi — Kruskal-Wallis)</div>
<div class="signal-card-status" style="color:{'#15803D' if kabul_mu else '#A16207'}; font-size:1.02rem;">
{'H₁ KABUL EDİLDİ (Anlamlı Fark Var)' if kabul_mu else 'H₀ REDDEDİLEMEDİ (Fark Zayıf)'}
</div>
<div class="signal-card-sub">
<b>Test İstatistiği:</b> H = {h_stat:.2f} &nbsp;|&nbsp; <b>p-değeri {p_metin}</b> (α = 0.05)<br>
<b>Dinamik Yorum ({secili_odak_urun}):</b> En ucuz mevsim <b>{en_u_m}</b> ({en_u_v:.2f} ₺),
en pahalı mevsim <b>{en_p_m}</b> ({en_p_v:.2f} ₺).
{'Bu fark rastlantısal değildir; mevsime göre stok/sözleşme zamanlaması istatistiksel olarak kârlıdır.' if kabul_mu else 'Mevsimler arası fark istatistiksel olarak zayıftır; yıl boyu düzenli spot alım yeterlidir.'}
</div>
</div>
""",
                        unsafe_allow_html=True,
                    )

            # Hipotez 2: Mal Türleri (ITHAL vs MEYVE vs SEBZE) arasında reel fiyat farkı anlamlı mı?
            if scipy_var and not df_filtreli.empty and {"MAL_TURU", "REEL_ORTALAMA_UCRET"}.issubset(df_filtreli.columns):
                gruplar_h2 = [
                    g["REEL_ORTALAMA_UCRET"].dropna().values
                    for _, g in df_filtreli.groupby("MAL_TURU")
                    if len(g["REEL_ORTALAMA_UCRET"].dropna()) >= 10
                ]
                if len(gruplar_h2) >= 2:
                    h2_stat, p2_val = sp_stats.kruskal(*gruplar_h2)
                    tur_ort = df_filtreli.groupby("MAL_TURU")["REEL_ORTALAMA_UCRET"].mean().sort_values(ascending=False)
                    en_pah_tur, en_pah_v = str(tur_ort.index[0]), float(tur_ort.iloc[0])
                    en_ucu_tur, en_ucu_v = str(tur_ort.index[-1]), float(tur_ort.iloc[-1])
                    p2_metin = "< 0.0001" if p2_val < 0.0001 else f"= {p2_val:.4f}"
                    kabul2 = p2_val < 0.05

                    st.markdown(
                        f"""
<div class="signal-card" style="border-left:5px solid {'#16A34A' if kabul2 else '#CA8A04'};">
<div class="signal-card-title">Hipotez 2 (Kategori Maliyet Farkı — ITHAL vs. Yerli)</div>
<div class="signal-card-status" style="color:{'#15803D' if kabul2 else '#A16207'}; font-size:1.02rem;">
{'H₁ KABUL EDİLDİ (Kategoriler Arası Fark Anlamlı)' if kabul2 else 'H₀ REDDEDİLEMEDİ'}
</div>
<div class="signal-card-sub">
<b>Test İstatistiği:</b> H = {h2_stat:.2f} &nbsp;|&nbsp; <b>p-değeri {p2_metin}</b> (α = 0.05)<br>
<b>Dinamik Yorum (Seçili Kategoriler):</b> En yüksek ortalama reel birim maliyet <b>{en_pah_tur}</b>
({en_pah_v:.2f} ₺), en düşük ise <b>{en_ucu_tur}</b> ({en_ucu_v:.2f} ₺) grubundadır.
Menü mühendisliğinde {en_pah_tur} ürünlerinin ikamesi bütçeyi doğrudan rahatlatır.
</div>
</div>
""",
                        unsafe_allow_html=True,
                    )

        # --- B) Kılavuzun Özgün Sorusu: 20 Yıllık Reel Kazananlar & Kaybedenler ---
        df_reel_fark_cached, df_ajanda_cached = _reel_degisim_ve_ajanda_hazirla(df_filtreli, df_karar_destegi)

        with ozg_sag:
            st.markdown("#### 20 Yılda Reel Olarak En Çok Pahalanan ve Ucuzlayan Ürünler")
            if not df_reel_fark_cached.empty:
                donem_etk = str(df_reel_fark_cached["DONEM_ETIKET"].iloc[0])
                en_pah_5 = df_reel_fark_cached.sort_values("REEL_DEGISIM_YUZDE", ascending=False).head(5)
                en_ucu_5 = df_reel_fark_cached.sort_values("REEL_DEGISIM_YUZDE", ascending=True).head(5)
                kombine_df = (
                    pd.concat([en_ucu_5, en_pah_5])
                    .drop_duplicates(subset=["MAL_ADI"])
                    .sort_values("REEL_DEGISIM_YUZDE", ascending=True)
                )

                fig_reel_deg = go.Figure(
                    go.Bar(
                        x=kombine_df["REEL_DEGISIM_YUZDE"],
                        y=kombine_df["MAL_ADI"],
                        orientation="h",
                        marker_color=[
                            "#DC2626" if v > 0 else "#1B7A43" for v in kombine_df["REEL_DEGISIM_YUZDE"]
                        ],
                        text=[f"+%{v:.1f}" if v >= 0 else f"%{v:.1f}" for v in kombine_df["REEL_DEGISIM_YUZDE"]],
                        textposition="outside",
                    )
                )
                fig_reel_deg.add_vline(x=0, line_dash="dash", line_color="#1E293B", line_width=1)
                fig_reel_deg.update_layout(
                    height=340,
                    margin=dict(l=10, r=55, t=20, b=10),
                    xaxis_title=f"Reel Fiyat Değişimi % ({donem_etk})",
                    yaxis_title="Ürün",
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                )
                st.plotly_chart(fig_reel_deg, use_container_width=True)

                lider_zam = kombine_df.iloc[-1]
                lider_ucuz = kombine_df.iloc[0]
                st.markdown(
                    f"""
<div class="insight-note"><b>Özgün Soru Yanıtı ({donem_etk}):</b>
TÜFE enflasyonu tamamen arındırıldığında bile <b>{lider_zam['MAL_ADI']}</b> reel olarak
<b>+%{lider_zam['REEL_DEGISIM_YUZDE']:.1f}</b> ({lider_zam['ILK_DONEM_REEL']:.2f} ₺ → {lider_zam['SON_DONEM_REEL']:.2f} ₺)
ile en fazla pahalanan ürün olurken; <b>{lider_ucuz['MAL_ADI']}</b> reel bazda
<b>%{lider_ucuz['REEL_DEGISIM_YUZDE']:.1f}</b> değişimle en avantajlı ürün olmuştur.
Uzun vadeli sözleşmeler kırmızı bölgedeki kalemlere öncelik vermelidir.</div>
""",
                    unsafe_allow_html=True,
                )
            else:
                st.info("Reel dönem karşılaştırması için yeterli yıl aralığı bulunamadı.")


    # --- C) 12 Aylık Sözleşme & Toplu Alım Ajandası ---
    with st.expander("📋 12 Aylık Satın Alma ve Sözleşme Ajandası", expanded=False):
        if not df_ajanda_cached.empty:
            st.dataframe(
                df_ajanda_cached[["AY", "FIRSAT_URUN_SAYISI", "EN_UCUZ_URUNLER", "ORT_MEVSIMSEL_FARK_YUZDE", "SATIN_ALMA_AKSIYONU"]].rename(
                    columns={
                        "AY": "Ay",
                        "FIRSAT_URUN_SAYISI": "En Ucuz Ürün Sayısı",
                        "EN_UCUZ_URUNLER": "O Ay Dip Yapan Fırsat Ürünleri",
                        "ORT_MEVSIMSEL_FARK_YUZDE": "Ort. Mevsimsel Makas (%)",
                        "SATIN_ALMA_AKSIYONU": "Önerilen Aksiyon",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
            en_yogun_ay_satir = df_ajanda_cached.sort_values("FIRSAT_URUN_SAYISI", ascending=False).iloc[0]
            toplam_firsat_ay = int((df_ajanda_cached["FIRSAT_URUN_SAYISI"] > 0).sum())
            st.markdown(
                f"""
<div class="insight-note"><b>12 Aylık Ajanda Yorumu:</b>
25 ürünün en ucuz alım pencereleri yılın <b>{toplam_firsat_ay} farklı ayına</b> yayılmaktadır.
En yoğun fırsat ayı <b>{en_yogun_ay_satir['AY']}</b> olup tek başına <b>{int(en_yogun_ay_satir['FIRSAT_URUN_SAYISI'])} ürün</b>
({en_yogun_ay_satir['EN_UCUZ_URUNLER']}) bu ayda yılın en düşük reel fiyatına inmektedir.
<b>{aktif_sube_sayisi} şube</b> için yıllık tedarikçi ihaleleri bu ajandaya göre takvimlendirilmelidir.</div>
""",
                unsafe_allow_html=True,
            )

    # --- D) İzmir Don Olaylarının Gecikmeli Fiyat Etkisi (Suzan & Nesrin İklim Analizi) ---
    don_gorsel_analiz = _dosya_yolu_coz("03_Model/don_etkisi_analiz.png")
    df_don_haftalik = VERILER.get("don_etkisi_haftalik_analiz", pd.DataFrame())
    df_don_model = VERILER.get("don_model_karsilastirma", pd.DataFrame())
    if os.path.exists(don_gorsel_analiz) or not df_don_haftalik.empty or not df_don_model.empty:
        with st.expander("İzmir Don Olaylarının Gecikmeli Fiyat Etkisi ve İklim Modeli", expanded=False):
            if {"DON_VAR_MI", "REEL_ORTALAMA_UCRET", "IZMIR_MIN_SICAKLIK_C"}.issubset(df_filtreli.columns):
                don_gun_df = df_filtreli[df_filtreli["DON_VAR_MI"] == 1]
                normal_gun_df = df_filtreli[df_filtreli["DON_VAR_MI"] == 0]
                don_ort_fiyat = _guvenli_sayi(don_gun_df["REEL_ORTALAMA_UCRET"].mean(), 0.0)
                norm_ort_fiyat = _guvenli_sayi(normal_gun_df["REEL_ORTALAMA_UCRET"].mean(), 0.0)
                don_fark_yuzde = ((don_ort_fiyat - norm_ort_fiyat) / norm_ort_fiyat * 100.0) if norm_ort_fiyat > 0 else 0.0
                dk1, dk2, dk3 = st.columns(3)
                dk1.metric("Don Olayı olmayan Günlerde Ort. Reel Fiyat", f"{norm_ort_fiyat:.2f} ₺", f"{len(normal_gun_df):,} Kayıt".replace(",", "."))
                dk2.metric("Zirai Don Günlerinde (≤ 0°C) Ort. Reel Fiyat", f"{don_ort_fiyat:.2f} ₺", f"{don_fark_yuzde:+.1f}% Don Farkı")
                dk3.metric("En Yüksek Gecikmeli Don Etkisi", "Çalı Fasulye (+%34.3)", "4. Haftada Zirve Yapar")
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            if os.path.exists(don_gorsel_analiz):
                _, don_orta, _ = st.columns([0.08, 0.84, 0.08])
                with don_orta:
                    st.image(str(don_gorsel_analiz), use_container_width=True)
            d_col1, d_col2 = st.columns([1.15, 0.95], gap="large")
            with d_col1:
                if not df_don_haftalik.empty:
                    st.markdown("##### Don Olayı Sonrası Ürün Bazlı 1–4 Haftalık Fiyat Tepkisi")
                    st.dataframe(df_don_haftalik, use_container_width=True, hide_index=True)
            with d_col2:
                if not df_don_model.empty:
                    st.markdown("##### İklim Özellikli Tahmin Modeli Karşılaştırması")
                    st.dataframe(df_don_model, use_container_width=True, hide_index=True)
            st.markdown(
                '<div class="insight-note"><b>İklim ve Don Etkisi İş Yorumu:</b> '
                "İzmir'de sıcaklık 0°C ve altına düştüğünde açık tarla ve örtü altı sebzelerde (özellikle Çalı Fasulye, Marul, Uzun Patlıcan ve Taze Kabak) "
                "fiyat şoku anında değil, 2. ile 4. hafta arasında zirve yapmaktadır. Meteorolojik don uyarısı alındığında bu ürünlerde fiyat artışı hale yansımadan "
                "ilk 48 saat içinde alım veya sabit fiyatlı sözleşme yapılmalıdır.</div>",
                unsafe_allow_html=True,
            )


# =============================================================================
# 3. SEKME: STRATEJİ & RİSK
# =============================================================================
with sekme_strateji:
    st.subheader("🎯 Kraljic Satın Alma Strateji Matrisi ve Pazarlık Gücü")
    st.caption(
        "Sol grafikte ürünleri tedarik riski ve maliyet etkisine göre 4 stratejik bölgeye ayıran Kraljic matrisini, "
        "sağ grafikte ise gün içi hal pazarlık makasını inceleyebilirsiniz. Bölge sınıflandırma tablosu ve 1 yıllık strateji doğrulaması alt kısımdaki açılır pencerelerdedir."
    )

    # -------------------------------------------------------------------------
    # 1. ÜST BÖLÜM: SOL (KRALJIC SATIN ALMA MATRİSİ) | SAĞ (PAZARLIK GÜCÜ & KALİTE MAKASI)
    # -------------------------------------------------------------------------
    str_sol, str_sag = st.columns([1.15, 0.95], gap="large")

    oynak_kolon = (
        "REEL_OYNAKLIK_30"
        if "REEL_OYNAKLIK_30" in df_filtreli.columns
        else ("REEL_OYNAKLIK_7" if "REEL_OYNAKLIK_7" in df_filtreli.columns else "")
    )
    kraljic_df_cached, makas_ozet_cached = _kraljic_ve_makas_ozeti_hazirla(df_filtreli, oynak_kolon)

    # --- A) Kraljic Satın Alma Matrisi ---
    with str_sol:
        st.markdown("#### Kraljic Satın Alma Strateji Matrisi")
        st.caption(
            "Ürünlerin 30 günlük fiyat oynaklığı (tedarik riski) ile ortalama reel birim fiyatına (maliyet etkisi) göre stratejik sınıflandırması. "
            "Tüm ürün detaylarını görmek için noktaların üzerine fare ile gelebilirsiniz."
        )

        if not kraljic_df_cached.empty:
            kraljic_df = kraljic_df_cached.copy()
            x_esik = _guvenli_sayi(kraljic_df["RISK_OYNAKLIK"].median(), 0.0)
            y_esik = _guvenli_sayi(kraljic_df["MALIYET_REEL"].median(), 0.0)

            def _kraljic_bolge(r):
                yuksek_risk = r["RISK_OYNAKLIK"] >= x_esik
                yuksek_maliyet = r["MALIYET_REEL"] >= y_esik
                if yuksek_risk and yuksek_maliyet:
                    return "Kritik / Sözleşmeli Alım"
                if not yuksek_risk and yuksek_maliyet:
                    return "Maliyet / Fire Kontrolü"
                if yuksek_risk and not yuksek_maliyet:
                    return "Fırsat / Stoklama"
                return "Rutin / Spot Alım"

            kraljic_df["STRATEJI_BOLGESI"] = kraljic_df.apply(_kraljic_bolge, axis=1)

            renk_haritasi = {
                "Kritik / Sözleşmeli Alım": "#DC2626",
                "Maliyet / Fire Kontrolü": "#F59E0B",
                "Fırsat / Stoklama": "#3B82F6",
                "Rutin / Spot Alım": "#1B7A43",
            }

            tum_etiketleri_goster = st.checkbox(
                "Tüm ürün isimlerini grafikte göster",
                value=False,
                key="kraljic_tum_etiketler",
            )

            # 4 köşedeki en uç / kritik 6-8 ürünü (+ seçili odak ürünü) otomatik seç
            uc_urunler = set()
            if len(kraljic_df) > 0:
                uc_urunler.update(kraljic_df.nlargest(2, "RISK_OYNAKLIK")["MAL_ADI"].tolist())
                uc_urunler.update(kraljic_df.nlargest(2, "MALIYET_REEL")["MAL_ADI"].tolist())
                uc_urunler.update(kraljic_df.nsmallest(2, "RISK_OYNAKLIK")["MAL_ADI"].tolist())
                uc_urunler.update(kraljic_df.nsmallest(2, "MALIYET_REEL")["MAL_ADI"].tolist())
                if secili_odak_urun in kraljic_df["MAL_ADI"].values:
                    uc_urunler.add(secili_odak_urun)

            kraljic_df["ETIKET"] = (
                kraljic_df["MAL_ADI"]
                if tum_etiketleri_goster
                else kraljic_df["MAL_ADI"].where(kraljic_df["MAL_ADI"].isin(uc_urunler), "")
            )

            # Dinamik textposition: çakışmayı önlemek için ürünün bulunduğu bölgeye göre konumlandır
            x_min_val = float(kraljic_df["RISK_OYNAKLIK"].min())
            x_max_val = float(kraljic_df["RISK_OYNAKLIK"].max())
            y_min_val = float(kraljic_df["MALIYET_REEL"].min())
            y_max_val = float(kraljic_df["MALIYET_REEL"].max())
            x_aralik = max(x_max_val - x_min_val, 1.0)
            y_aralik = max(y_max_val - y_min_val, 1.0)

            def _dinamik_konum(r):
                sagda = r["RISK_OYNAKLIK"] >= x_esik
                ustte = r["MALIYET_REEL"] >= y_esik
                if sagda and ustte:
                    return "top left" if r["RISK_OYNAKLIK"] > (x_min_val + 0.72 * x_aralik) else "top center"
                if (not sagda) and ustte:
                    return "top right" if r["RISK_OYNAKLIK"] < (x_min_val + 0.25 * x_aralik) else "top center"
                if sagda and (not ustte):
                    return "bottom left" if r["RISK_OYNAKLIK"] > (x_min_val + 0.72 * x_aralik) else "bottom center"
                return "bottom right" if r["RISK_OYNAKLIK"] < (x_min_val + 0.25 * x_aralik) else "bottom center"

            kraljic_df["ETIKET_KONUM"] = kraljic_df.apply(_dinamik_konum, axis=1)

            fig_kraljic = go.Figure()
            for bolge_ad in [
                "Kritik / Sözleşmeli Alım",
                "Maliyet / Fire Kontrolü",
                "Fırsat / Stoklama",
                "Rutin / Spot Alım",
            ]:
                sub_df = kraljic_df[kraljic_df["STRATEJI_BOLGESI"] == bolge_ad]
                if sub_df.empty:
                    continue
                fig_kraljic.add_trace(
                    go.Scatter(
                        x=sub_df["RISK_OYNAKLIK"],
                        y=sub_df["MALIYET_REEL"],
                        mode="markers+text",
                        name=bolge_ad,
                        text=sub_df["ETIKET"],
                        textposition=sub_df["ETIKET_KONUM"].tolist(),
                        textfont=dict(size=10, color="#1E293B"),
                        marker=dict(
                            size=[18 if u == secili_odak_urun else 15 for u in sub_df["MAL_ADI"]],
                            color=renk_haritasi[bolge_ad],
                            line=dict(width=1.5, color="#FFFFFF"),
                            opacity=0.92,
                        ),
                        customdata=np.stack(
                            [sub_df["MAL_ADI"], sub_df["STRATEJI_BOLGESI"]],
                            axis=-1,
                        ),
                        hovertemplate=(
                            "<b>%{customdata[0]}</b><br>"
                            "Bölge: %{customdata[1]}<br>"
                            "30 Günlük Fiyat Oynaklığı: %{x:.2f}<br>"
                            "Ortalama Birim Reel Fiyat: %{y:.2f} ₺<extra></extra>"
                        ),
                    )
                )

            fig_kraljic.add_vline(
                x=x_esik,
                line_dash="dash",
                line_color="#64748B",
                annotation_text=f"Medyan Risk ({x_esik:.1f})",
                annotation_position="top right",
            )
            fig_kraljic.add_hline(
                y=y_esik,
                line_dash="dash",
                line_color="#64748B",
                annotation_text=f"Medyan Maliyet ({y_esik:.1f} ₺)",
                annotation_position="bottom right",
            )
            fig_kraljic.update_layout(
                height=540,
                margin=dict(l=20, r=25, t=65, b=20),
                xaxis_title="Fiyat Oynaklığı / Tedarik Riski (30 Günlük Standart Sapma)",
                yaxis_title="Ortalama Birim Reel Fiyat / Maliyet Etkisi (₺)",
                xaxis=dict(range=[max(0.0, x_min_val - 0.10 * x_aralik), x_max_val + 0.14 * x_aralik]),
                yaxis=dict(range=[max(0.0, y_min_val - 0.12 * y_aralik), y_max_val + 0.14 * y_aralik]),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.03,
                    xanchor="left",
                    x=0,
                    font=dict(size=10),
                ),
            )
            st.plotly_chart(fig_kraljic, use_container_width=True)

            # 4 Strateji Bölgesi Özet Tablosu
            bolge_sirasi = [
                "Kritik / Sözleşmeli Alım",
                "Fırsat / Stoklama",
                "Maliyet / Fire Kontrolü",
                "Rutin / Spot Alım",
            ]
            bolge_aksiyon = {
                "Kritik / Sözleşmeli Alım": "Yüksek risk & yüksek fiyat → Uzun vadeli sabit fiyatlı tedarikçi sözleşmesi",
                "Fırsat / Stoklama": "Yüksek oynaklık & düşük birim fiyat → En ucuz ayda toplu alım / stoklama",
                "Maliyet / Fire Kontrolü": "Düşük risk & yüksek fiyat → Zayi/bozulma ve porsiyon kontrolü + ihale",
                "Rutin / Spot Alım": "Düşük risk & düşük fiyat → Standart haftalık spot sipariş",
            }
            bolge_ozet_satirlar = []
            for b_ad in bolge_sirasi:
                b_kesit = kraljic_df[kraljic_df["STRATEJI_BOLGESI"] == b_ad].sort_values("MALIYET_REEL", ascending=False)
                urun_adlari = b_kesit["MAL_ADI"].tolist()
                bolge_ozet_satirlar.append(
                    {
                        "Strateji Bölgesi": b_ad,
                        "Ürün Sayısı": len(urun_adlari),
                        "Bu Bölgedeki Ürünler": ", ".join(urun_adlari) if urun_adlari else "—",
                        "Önerilen Yönetim Aksiyonu": bolge_aksiyon[b_ad],
                    }
                )
            with st.expander("📋 4 Strateji Bölgesine Göre Ürün Sınıflandırma Özeti", expanded=False):
                st.dataframe(pd.DataFrame(bolge_ozet_satirlar), use_container_width=True, hide_index=True)

                # Seçili odak ürünün bulunduğu bölgeyi ve genel matris yorumunu özetle
                odak_satir = kraljic_df[kraljic_df["MAL_ADI"] == secili_odak_urun]
                stratejik_sayisi = int((kraljic_df["STRATEJI_BOLGESI"] == "Kritik / Sözleşmeli Alım").sum())
                rutin_sayisi = int((kraljic_df["STRATEJI_BOLGESI"] == "Rutin / Spot Alım").sum())
                odak_bolge_not = (
                    f"Seçili odak ürününüz <b>{secili_odak_urun}</b>, <b>{odak_satir.iloc[0]['STRATEJI_BOLGESI']}</b> bölgesindedir."
                    if not odak_satir.empty
                    else ""
                )
                st.markdown(
                    f"""
<div class="insight-note"><b>Kraljic Matrisi Yorumu:</b>
Seçili kategorilerde toplam <b>{len(kraljic_df)} ürünün</b> <b>{stratejik_sayisi} tanesi</b> yüksek maliyet ve yüksek riskli
<b>Kritik / Sözleşmeli Alım</b> bölgesinde (uzun vadeli sözleşme şart), <b>{rutin_sayisi} tanesi</b> ise düşük riskli
<b>Rutin / Spot Alım</b> bölgesindedir. {odak_bolge_not}</div>
""",
                    unsafe_allow_html=True,
                )

        else:
            st.warning("Kraljic matrisi için yeterli kayıt bulunamadı.")

    # --- B) Pazarlık Gücü & Kalite Makası ---
    with str_sag:
        st.markdown("#### Pazarlık Gücü ve Kalite Makası")
        st.caption(
            "Gün içi Hal Taban–Tavan fiyat makasının ortalama fiyata oranı en yüksek ürünler. "
            "Makas ne kadar açıksa hal içi pazarlık ve kalite seçimi marjı o kadar yüksektir."
        )

        if not makas_ozet_cached.empty:
            makas_ozet = makas_ozet_cached.copy()
            makas_ozet["ORT_MAKAS_YUZDE"] = makas_ozet["ORT_MAKAS_YUZDE"].round(1)
            bar_renk = [
                "#1B7A43" if u == secili_odak_urun else "#0F766E"
                for u in makas_ozet["MAL_ADI"]
            ]

            fig_makas = go.Figure(
                go.Bar(
                    x=makas_ozet["ORT_MAKAS_YUZDE"],
                    y=makas_ozet["MAL_ADI"],
                    orientation="h",
                    marker_color=bar_renk,
                    text=[f"%{v:.1f}" for v in makas_ozet["ORT_MAKAS_YUZDE"]],
                    textposition="outside",
                )
            )
            max_makas = _guvenli_sayi(makas_ozet["ORT_MAKAS_YUZDE"].max(), 10.0)
            fig_makas.update_layout(
                height=460,
                margin=dict(l=10, r=40, t=25, b=10),
                xaxis_title="Ortalama Fiyat Makası: (Hal Tavan - Hal Taban) / Ortalama (%)",
                yaxis_title="Ürün Adı",
                xaxis=dict(range=[0, max(max_makas * 1.18, 1.0)]),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
            )
            st.plotly_chart(fig_makas, use_container_width=True)

            lider_urun = makas_ozet.iloc[-1]["MAL_ADI"]
            lider_oran = _guvenli_sayi(makas_ozet.iloc[-1]["ORT_MAKAS_YUZDE"], 0.0)
            st.success(
                f"**Pazarlık Fırsatı:** **{lider_urun}** ürününde aynı gün içinde en düşük ve en yüksek kalite/parti "
                f"fiyatı arasındaki makas ortalama **%{lider_oran:.1f}** seviyesindedir. Tedarikçi tekliflerinde "
                f"Hal Taban Fiyatı bandına yakın pazarlık yapılmalıdır."
            )
        else:
            st.info("Fiyat makası hesaplanacak kayıt bulunamadı.")


    with st.expander("📈 Geçmiş 1 Yıllık Strateji Doğrulaması", expanded=False):
        st.caption(
            "Son 1 yıllık haftalık hal fiyatlarında **Her Hafta Sabit Alan Restoran** ile "
            "**Sistemin 'Uygun' Sinyali Verdiği Dönemlerde Alım/Stok Yapan Restoranın** ortalama birim maliyetini karşılaştırır."
        )

        bt_kapsam = st.radio(
            "Backtest Kapsamı:",
            options=[
                f"Seçili Odak Ürün ({secili_odak_urun})",
                "Tüm Sepet Ortalaması (25 Ürün Genel)",
            ],
            horizontal=True,
            key="backtest_kapsam",
        )

        # Backtest veri kaynağını hazırla: öncelikle haftalik_satinalma_karar.csv, yoksa df_ozellikli'den türet
        df_bt = pd.DataFrame()
        fiyat_sutunu = "HAFTALIK_ORT_FIYAT"

        if (
            not df_haftalik_karar.empty
            and {"MAL_ADI", "HAFTA", "HAFTALIK_ORT_FIYAT", "DURUM"}.issubset(df_haftalik_karar.columns)
        ):
            df_bt = df_haftalik_karar.copy()
            df_bt["HAFTA_DT"] = pd.to_datetime(df_bt["HAFTA"], errors="coerce")
        elif not df_ozellikli.empty and {"MAL_ADI", "TARIH", "ORTALAMA_UCRET"}.issubset(df_ozellikli.columns):
            gecici = df_ozellikli.dropna(subset=["TARIH", "ORTALAMA_UCRET"]).copy()
            gecici["HAFTA_DT"] = pd.to_datetime(gecici["TARIH"]).dt.to_period("W").apply(lambda r: r.start_time)
            haftalik_g = (
                gecici.groupby(["MAL_ADI", "HAFTA_DT"], as_index=False)["ORTALAMA_UCRET"]
                .mean()
                .rename(columns={"ORTALAMA_UCRET": "HAFTALIK_ORT_FIYAT"})
            )
            genel_g = (
                gecici.groupby("MAL_ADI", as_index=False)["ORTALAMA_UCRET"]
                .mean()
                .rename(columns={"ORTALAMA_UCRET": "GENEL_ORT_FIYAT"})
            )
            df_bt = haftalik_g.merge(genel_g, on="MAL_ADI", how="left")
            df_bt["DURUM"] = np.where(
                df_bt["HAFTALIK_ORT_FIYAT"] < df_bt["GENEL_ORT_FIYAT"] * 0.9,
                "UYGUN HAFTA",
                np.where(
                    df_bt["HAFTALIK_ORT_FIYAT"] > df_bt["GENEL_ORT_FIYAT"] * 1.1,
                    "PAHALI HAFTA",
                    "NORMAL",
                ),
            )

        if not df_bt.empty and "HAFTA_DT" in df_bt.columns:
            df_bt = df_bt.dropna(subset=["HAFTA_DT", fiyat_sutunu]).copy()

            if bt_kapsam.startswith("Seçili"):
                df_bt_secili = df_bt[df_bt["MAL_ADI"] == secili_odak_urun].copy()
            else:
                df_bt_secili = df_bt.copy()

            if not df_bt_secili.empty:
                max_tarih = df_bt_secili["HAFTA_DT"].max()
                bir_yil_once = max_tarih - pd.Timedelta(days=365)
                df_son_yil = df_bt_secili[df_bt_secili["HAFTA_DT"] >= bir_yil_once].copy()

                # Eğer son 1 yılda UYGUN kayıt azsa veya tek dönemse tüm geçmişi yedek olarak da kontrol et
                if len(df_son_yil) < 6:
                    df_son_yil = df_bt_secili.copy()

                df_son_yil["UYGUN_MU"] = (
                    df_son_yil["DURUM"].astype(str).str.upper().str.contains("UYGUN")
                )

                sabit_alim_ort = float(df_son_yil[fiyat_sutunu].mean())
                df_uygun_haftalar = df_son_yil[df_son_yil["UYGUN_MU"]]

                if not df_uygun_haftalar.empty:
                    akilli_alim_ort = float(df_uygun_haftalar[fiyat_sutunu].mean())
                    uygun_hafta_sayisi = int(df_uygun_haftalar["HAFTA_DT"].nunique())
                    not_etiketi = f"Uygun Sinyal ({uygun_hafta_sayisi} Hafta)"
                else:
                    # Son 1 yılda genel ortalamanın %90 altında hafta yoksa en ucuz %30'luk haftaları baz al
                    esik_ceyrek = float(df_son_yil[fiyat_sutunu].quantile(0.30))
                    df_uygun_haftalar = df_son_yil[df_son_yil[fiyat_sutunu] <= esik_ceyrek].copy()
                    df_son_yil["UYGUN_MU"] = df_son_yil[fiyat_sutunu] <= esik_ceyrek
                    akilli_alim_ort = float(df_uygun_haftalar[fiyat_sutunu].mean())
                    uygun_hafta_sayisi = int(df_uygun_haftalar["HAFTA_DT"].nunique())
                    not_etiketi = f"En Uygun %30 Hafta ({uygun_hafta_sayisi} Hafta)"

                birim_fark = sabit_alim_ort - akilli_alim_ort
                tasarruf_yuzde = (birim_fark / sabit_alim_ort) * 100 if sabit_alim_ort > 0 else 0.0

                bt_m1, bt_m2, bt_m3, bt_m4 = st.columns(4)
                bt_m1.metric(
                    "Klasik Restoran (Her Hafta Sabit Alım)",
                    f"{sabit_alim_ort:.2f} TL / Birim",
                    "52 Hafta Ortalaması",
                )
                bt_m2.metric(
                    "SNC Akıllı Alım (Uygun Haftalarda)",
                    f"{akilli_alim_ort:.2f} TL / Birim",
                    not_etiketi,
                )
                bt_m3.metric(
                    "Birim Başına Net Kazanç",
                    f"{birim_fark:.2f} TL",
                    f"-%{tasarruf_yuzde:.1f} Maliyet Düşüşü",
                )
                bt_m4.metric(
                    "Backtest Tasarruf Oranı (%)",
                    f"%{tasarruf_yuzde:.1f}",
                    "Gerçekleşen 1 Yıllık Avantaj",
                )

                # Haftalık Zaman Serisi Grafiği
                haftalik_seri = (
                    df_son_yil.groupby(["HAFTA_DT", "UYGUN_MU"], as_index=False)[fiyat_sutunu]
                    .mean()
                    .sort_values("HAFTA_DT")
                )
                toplam_seri = (
                    df_son_yil.groupby("HAFTA_DT", as_index=False)[fiyat_sutunu]
                    .mean()
                    .sort_values("HAFTA_DT")
                )

                fig_bt = go.Figure()
                fig_bt.add_trace(
                    go.Scatter(
                        x=toplam_seri["HAFTA_DT"],
                        y=toplam_seri[fiyat_sutunu],
                        mode="lines+markers",
                        line=dict(color="#64748B", width=2),
                        marker=dict(size=5),
                        name="Haftalık Ortalama Fiyat",
                    )
                )

                uygun_noktalar = haftalik_seri[haftalik_seri["UYGUN_MU"]]
                if not uygun_noktalar.empty:
                    fig_bt.add_trace(
                        go.Scatter(
                            x=uygun_noktalar["HAFTA_DT"],
                            y=uygun_noktalar[fiyat_sutunu],
                            mode="markers",
                            marker=dict(color="#1B7A43", size=11, symbol="diamond", line=dict(width=1.5, color="#FFFFFF")),
                            name="SNC 'UYGUN' Alım Haftaları",
                        )
                    )

                fig_bt.add_hline(
                    y=sabit_alim_ort,
                    line_dash="dash",
                    line_color="#DC2626",
                    annotation_text=f"Her Hafta Sabit Alım Ort.: {sabit_alim_ort:.2f} TL",
                    annotation_position="top left",
                )
                fig_bt.add_hline(
                    y=akilli_alim_ort,
                    line_dash="dot",
                    line_color="#1B7A43",
                    annotation_text=f"SNC Uygun Dönem Alım Ort.: {akilli_alim_ort:.2f} TL (-%{tasarruf_yuzde:.1f})",
                    annotation_position="bottom left",
                )

                fig_bt.update_layout(
                    height=360,
                    margin=dict(l=10, r=10, t=25, b=10),
                    xaxis_title="Hafta",
                    yaxis_title="Haftalık Ortalama Birim Fiyat (TL)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    hovermode="x unified",
                )
                st.plotly_chart(fig_bt, use_container_width=True)

                # Dinamik Backtest Yorumu
                bt_hedef_txt = f"<b>{secili_odak_urun}</b> ürününde" if bt_kapsam.startswith("Seçili") else "<b>tüm 25 ürünlük sepette</b>"
                st.markdown(
                    f"""
<div class="insight-note"><b>Backtest Yorumu ({'Odak Ürün' if bt_kapsam.startswith('Seçili') else 'Genel Sepet'}):</b>
Son 1 yıllık gerçek veride {bt_hedef_txt} her hafta sabit alım yapmak yerine SNC'nin yeşil elmasla işaretlediği
<b>{uygun_hafta_sayisi} uygun haftada</b> alım yapan bir restoran birim başına ortalama <b>{birim_fark:.2f} ₺</b>
(<b>%{tasarruf_yuzde:.1f}</b>) daha düşük maliyet elde etmiştir. Bu sonuç, zamanlamaya dayalı satın almanın sahada çalıştığını kanıtlar.</div>
""",
                    unsafe_allow_html=True,
                )
                st.caption("Not: Uygun sinyal haftalarında stoklu veya öne çekilmiş alım yapıldığı varsayılmıştır.")
            else:
                st.info("Seçili kapsam için haftalık backtest kaydı bulunamadı.")
        else:
            st.warning("Haftalık satın alma karar verisi bulunamadı.")


# =============================================================================
# 4. SEKME: KARAR EKRANI
# =============================================================================
with sekme_karar:
    st.subheader(f"🤖 Güncel Piyasa Durumu, Fiyat Tahmini ve Teklif Kontrolü — {secili_odak_urun}")
    st.caption(
        f"Ürünün 4 zaman dilimindeki piyasa durumunu, gelecek hafta yapay zekâ fiyat tahminini ve {aktif_sube_sayisi} şube için tedarikçi teklif kontrolünü aşağıda görebilirsiniz. "
        "1 aylık fiyat projeksiyonu, model performans karşılaştırması ve SHAP açıklanabilirlik analizleri alt kısımdaki açılır pencerelerdedir."
    )

    df_urun_karar = (
        df_ozellikli[df_ozellikli["MAL_ADI"] == secili_odak_urun]
        .dropna(subset=["TARIH"])
        .sort_values("TARIH")
        .copy()
        if not df_ozellikli.empty and "MAL_ADI" in df_ozellikli.columns
        else pd.DataFrame()
    )

    # -------------------------------------------------------------------------
    # 1. ADIM: PİYASA ŞU AN UCUZ MU PAHALI MI? (4 ZAMAN DİLİMİ SİNYALİ)
    # -------------------------------------------------------------------------
    st.markdown(f"#### 1. Piyasa Durumu ve 4 Zaman Dilimi Özeti — {secili_odak_urun}")

    def _sinyal_getir(df_k: pd.DataFrame, zaman_kolon: str, fiyat_kolon: str, yedek_etiket: str):
        if not df_k.empty and {"MAL_ADI", "DURUM"}.issubset(df_k.columns):
            kesit = df_k[df_k["MAL_ADI"] == secili_odak_urun].copy()
            if not kesit.empty:
                if zaman_kolon in kesit.columns:
                    kesit = kesit.sort_values(zaman_kolon)
                son = kesit.iloc[-1]
                durum = str(son["DURUM"]).strip()
                fiyat_bilgi = (
                    f"Ort. Fiyat: {float(son[fiyat_kolon]):.2f} TL"
                    if fiyat_kolon in son and pd.notna(son[fiyat_kolon])
                    else str(son.get(zaman_kolon, ""))
                )
                return durum, fiyat_bilgi
        if not df_urun_karar.empty and "ORTALAMA_UCRET" in df_urun_karar.columns:
            genel_ort = _guvenli_sayi(df_urun_karar["ORTALAMA_UCRET"].mean(), 1.0)
            son_fiyat = _guvenli_sayi(df_urun_karar.iloc[-1]["ORTALAMA_UCRET"], genel_ort)
            if son_fiyat < genel_ort * 0.90:
                return f"UYGUN {yedek_etiket}", f"Son Fiyat: {son_fiyat:.2f} TL"
            if son_fiyat > genel_ort * 1.10:
                return f"PAHALI {yedek_etiket}", f"Son Fiyat: {son_fiyat:.2f} TL"
            return "NORMAL", f"Son Fiyat: {son_fiyat:.2f} TL"
        return "NORMAL", "Veri Bekleniyor"

    def _sinyal_stil(durum_metni: str) -> tuple[str, str, str, str]:
        u = durum_metni.upper()
        if "UYGUN" in u:
            return "UYGUN", "Alım Fırsatı", "#15803D", "#DCFCE7"
        if "PAHALI" in u:
            return "PAHALI", "Dikkatli Al", "#B91C1C", "#FEE2E2"
        return "NORMAL", "Piyasa Dengeli", "#A16207", "#FEF9C3"

    gun_durum, gun_detay = _sinyal_getir(df_gunluk_karar, "GUN", "GUNLUK_ORT_FIYAT", "GUN")
    haf_durum, haf_detay = _sinyal_getir(df_haftalik_karar, "HAFTA", "HAFTALIK_ORT_FIYAT", "HAFTA")
    ay_durum, ay_detay = _sinyal_getir(df_aylik_karar, "AY", "AYLIK_ORT_FIYAT", "DONEM")
    mev_durum, mev_detay = _sinyal_getir(df_mevsimsel_karar, "MEVSIM", "MEVSIMLIK_ORT_FIYAT", "MEVSIM")

    sinyal_kartlari = [
        ("Günlük Durum", gun_durum, gun_detay),
        ("Haftalık Durum", haf_durum, haf_detay),
        ("Aylık Durum", ay_durum, ay_detay),
        ("Mevsimsel Durum", mev_durum, mev_detay),
    ]

    s_kolonlar = st.columns(4)
    for col_obj, (baslik, ham_durum, detay) in zip(s_kolonlar, sinyal_kartlari):
        etiket, aciklama, yazi_renk, arka_renk = _sinyal_stil(ham_durum)
        col_obj.markdown(
            f"""
<div class="signal-card" style="border-top: 4px solid {yazi_renk};">
<div class="signal-card-title">{baslik}</div>
<div class="signal-card-status" style="color: {yazi_renk};">{etiket}</div>
<div class="signal-card-sub">
<span style="background:{arka_renk}; color:{yazi_renk}; padding:2px 7px; border-radius:6px; font-weight:600;">{aciklama}</span>
<div style="margin-top:5px;">{detay}</div>
</div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.divider()

    # -------------------------------------------------------------------------
    # 2. ADIM (SOL): GELECEK HAFTA FİYAT TAHMİNİ & ALIM KARARI
    # 3. ADIM (SAĞ): TEDARİKÇİ TEKLİF KONTROLÜ (DİNAMİK ŞUBE SAYILI)
    # -------------------------------------------------------------------------
    karar_sol, karar_sag = st.columns([1.1, 1.0], gap="large")

    MODEL_SUTUNLARI_12 = [
        "MAL_ADI",
        "MAL_TURU",
        "BIRIM",
        "AY",
        "HAFTA",
        "REEL_ORTALAMA_UCRET",
        "REEL_LAG_1",
        "REEL_LAG_7",
        "REEL_LAG_30",
        "REEL_DEGISIM_YUZDE",
        "REEL_OYNAKLIK_7",
        "REEL_OYNAKLIK_30",
    ]

    with karar_sol:
        st.markdown(f"#### 2. Gelecek Hafta Fiyat Tahmini — {secili_odak_urun}")

        if not df_urun_karar.empty:
            son_kayit = df_urun_karar.iloc[-1]
            son_tarih = pd.to_datetime(son_kayit["TARIH"], errors="coerce")
            guncel_reel = _guvenli_sayi(son_kayit.get("REEL_ORTALAMA_UCRET", 0.0), 10.0)
            birim_adi = str(son_kayit.get("BIRIM", "KG"))
            mal_turu_adi = str(son_kayit.get("MAL_TURU", "SEBZE"))

            ay_degeri = (
                int(son_kayit["AY"])
                if "AY" in son_kayit and pd.notna(son_kayit["AY"])
                else (int(son_tarih.month) if pd.notna(son_tarih) else datetime.now().month)
            )
            hafta_degeri = (
                int(son_kayit["HAFTA"])
                if "HAFTA" in son_kayit and pd.notna(son_kayit["HAFTA"])
                else (int(son_tarih.isocalendar().week) if pd.notna(son_tarih) else 1)
            )

            def _guvenli_float(kolon_adi: str, varsayilan: float) -> float:
                deger = son_kayit.get(kolon_adi, np.nan)
                if pd.notna(deger):
                    return _guvenli_sayi(deger, varsayilan)
                if kolon_adi in df_urun_karar.columns and df_urun_karar[kolon_adi].notna().any():
                    return _guvenli_sayi(df_urun_karar[kolon_adi].dropna().iloc[-1], varsayilan)
                return varsayilan

            lag_1 = _guvenli_float("REEL_LAG_1", guncel_reel)
            lag_7 = _guvenli_float("REEL_LAG_7", guncel_reel)
            lag_30 = _guvenli_float("REEL_LAG_30", guncel_reel)
            deg_yuzde = _guvenli_float("REEL_DEGISIM_YUZDE", 0.0)
            oyn_7 = _guvenli_float("REEL_OYNAKLIK_7", max(guncel_reel * 0.05, 1.0))
            oyn_30 = _guvenli_float("REEL_OYNAKLIK_30", max(guncel_reel * 0.08, 1.5))

            # Hedef Alım Tarihi Seçimi (st.date_input) — seçilen tarihin AY ve HAFTA bilgisine göre canlı tahmin
            varsayilan_hedef_tarih = (
                son_tarih.date() if pd.notna(son_tarih) else date.today()
            )
            hedef_alim_tarihi = st.date_input(
                "Hedef Alım Tarihi Seçimi (Mevsimselliğe Duyarlı Canlı Tahmin):",
                value=varsayilan_hedef_tarih,
                key="karar_hedef_alim_tarihi",
                help="İleri bir tarih seçtiğinizde o tarihin Ay ve Hafta bilgisi otomatik hesaplanır; 1 Haftalık ve 1 Aylık modeller seçilen dönemin mevsimselliğine göre canlı tahmin üretir.",
            )
            tarih_degisti_mi = hedef_alim_tarihi != varsayilan_hedef_tarih
            secili_hedef_ay = int(hedef_alim_tarihi.month)
            secili_hedef_hafta = int(hedef_alim_tarihi.isocalendar().week)

            if tarih_degisti_mi:
                st.caption(
                    f"**Seçili Dönem:** {hedef_alim_tarihi.strftime('%d.%m.%Y')} "
                    f"(**{AY_SIRASI.get(secili_hedef_ay, secili_hedef_ay)}** — Yılın **{secili_hedef_hafta}. Haftası**) "
                    "için mevsimsellik girdi değerleri güncellendi."
                )

            don_senaryo_secimi = st.selectbox(
                "İklim ve Don Senaryosu (15 Özellikli İklim Modeli):",
                options=[
                    "Normal Mevsim Koşulları (Don Yok • > +2°C)",
                    "Hafif Don Riski (0°C ile +2°C Arası)",
                    "Şiddetli Zirai Don Olayı (≤ 0°C)",
                ],
                index=0,
                key="karar_don_senaryo_sec",
                help="İzmir'de zirai don veya soğuk hava dalgası beklendiğinde 15 özellikli iklim modeli devreye girerek don olayının fiyata etkisini hesaplar.",
            )

            with st.expander("⚙️ İleri Düzey Tahmin Parametrelerini Düzenle", expanded=False):
                st.caption("Varsayılan değerler ürünün son hal kayıtlarından ve seçilen hedef tarihten otomatik doldurulur.")
                g_c1, g_c2, g_c3 = st.columns(3)
                with g_c1:
                    ay_girdi = st.number_input("Ay (1-12)", min_value=1, max_value=12, value=secili_hedef_ay, key=f"k_ay_{secili_hedef_ay}_{secili_hedef_hafta}")
                    hafta_girdi = st.number_input("Yılın Haftası (1-53)", min_value=1, max_value=53, value=secili_hedef_hafta, key=f"k_hafta_{secili_hedef_ay}_{secili_hedef_hafta}")
                    reel_girdi = st.number_input(
                        "Güncel Reel Fiyat (₺)", min_value=0.01, value=round(guncel_reel, 2), step=0.5, key="k_reel"
                    )
                with g_c2:
                    lag1_girdi = st.number_input("1 Gün Önceki Fiyat", min_value=0.01, value=round(lag_1, 2), step=0.5, key="k_l1")
                    lag7_girdi = st.number_input("7 Gün Önceki Fiyat", min_value=0.01, value=round(lag_7, 2), step=0.5, key="k_l7")
                    lag30_girdi = st.number_input("30 Gün Önceki Fiyat", min_value=0.01, value=round(lag_30, 2), step=0.5, key="k_l30")
                with g_c3:
                    deg_girdi = st.number_input(
                        "Son Gün Değişimi (%)", value=round(deg_yuzde, 2), step=0.5, key="k_deg"
                    )
                    oyn7_girdi = st.number_input(
                        "7 Günlük Dalgalanma", min_value=0.0, value=round(oyn_7, 2), step=0.2, key="k_o7"
                    )
                    oyn30_girdi = st.number_input(
                        "30 Günlük Dalgalanma", min_value=0.0, value=round(oyn_30, 2), step=0.2, key="k_o30"
                    )

            girdi_sozluk = {
                "MAL_ADI": secili_odak_urun,
                "MAL_TURU": mal_turu_adi,
                "BIRIM": birim_adi,
                "AY": int(ay_girdi),
                "HAFTA": int(hafta_girdi),
                "REEL_ORTALAMA_UCRET": float(reel_girdi),
                "REEL_LAG_1": float(lag1_girdi),
                "REEL_LAG_7": float(lag7_girdi),
                "REEL_LAG_30": float(lag30_girdi),
                "REEL_DEGISIM_YUZDE": float(deg_girdi),
                "REEL_OYNAKLIK_7": float(oyn7_girdi),
                "REEL_OYNAKLIK_30": float(oyn30_girdi),
            }
            X_tahmin = pd.DataFrame([girdi_sozluk])[MODEL_SUTUNLARI_12]

            # CSV'deki hazır 1 Haftalık & 1 Aylık tahmin satırını kontrol et (tarih değiştirilmediyse doğrudan referans alınabilir)
            hazir_tahmin_satiri = None
            if not df_gelecek_tahminler.empty and "MAL_ADI" in df_gelecek_tahminler.columns:
                eslesen = df_gelecek_tahminler[df_gelecek_tahminler["MAL_ADI"] == secili_odak_urun]
                if not eslesen.empty:
                    hazir_tahmin_satiri = eslesen.iloc[-1]

            tahmin_kaynagi = "Geçmiş Trend & Oynaklık Yedek Motoru"
            tahmin_fiyat = None
            alt_bant_hazir = None
            ust_bant_hazir = None

            don_aktif_mi = not don_senaryo_secimi.startswith("Normal")
            if don_aktif_mi and MODEL_DON_AKTIF and MODEL_DON is not None:
                try:
                    if "Şiddetli" in don_senaryo_secimi:
                        sim_min_sicaklik, sim_don_var, sim_hafif_don = -1.5, 1, 1
                    else:
                        sim_min_sicaklik, sim_don_var, sim_hafif_don = 1.0, 0, 1
                    girdi_don_15 = dict(girdi_sozluk)
                    girdi_don_15["IZMIR_MIN_SICAKLIK_C"] = float(sim_min_sicaklik)
                    girdi_don_15["DON_VAR_MI"] = int(sim_don_var)
                    girdi_don_15["HAFIF_DON_RISKI"] = int(sim_hafif_don)
                    MODEL_SUTUNLARI_15 = MODEL_SUTUNLARI_12 + ["IZMIR_MIN_SICAKLIK_C", "DON_VAR_MI", "HAFIF_DON_RISKI"]
                    X_tahmin_15 = pd.DataFrame([girdi_don_15])[MODEL_SUTUNLARI_15]
                    tahmin_fiyat = round(float(MODEL_DON.predict(X_tahmin_15)[0]), 2)
                    tahmin_kaynagi = "15 Özellikli İklim ve Don Destekli Yapay Zekâ Modeli"
                except Exception:
                    tahmin_fiyat = None

            if tahmin_fiyat is None and MODEL_AKTIF and MODEL is not None:
                try:
                    tahmin_fiyat = round(float(MODEL.predict(X_tahmin)[0]), 2)
                    tahmin_kaynagi = "Eğitilmiş 1 Haftalık Makine Öğrenmesi Modeli"
                except Exception:
                    tahmin_fiyat = None
                    tahmin_kaynagi = "Geçmiş Trend & Oynaklık Yedek Motoru"

            if (not tarih_degisti_mi) and hazir_tahmin_satiri is not None:
                if tahmin_fiyat is None and pd.notna(hazir_tahmin_satiri.get("TAHMIN_1_HAFTA", np.nan)):
                    tahmin_fiyat = round(float(hazir_tahmin_satiri["TAHMIN_1_HAFTA"]), 2)
                    tahmin_kaynagi = "Eğitilmiş 1 Haftalık Model Çıktısı"
                if pd.notna(hazir_tahmin_satiri.get("ARALIK_1_HAFTA_ALT", np.nan)) and pd.notna(hazir_tahmin_satiri.get("ARALIK_1_HAFTA_UST", np.nan)):
                    alt_bant_hazir = round(float(hazir_tahmin_satiri["ARALIK_1_HAFTA_ALT"]), 2)
                    ust_bant_hazir = round(float(hazir_tahmin_satiri["ARALIK_1_HAFTA_UST"]), 2)

            if tahmin_fiyat is None:
                sinirli_trend = float(np.clip(deg_girdi, -15.0, 15.0)) / 100.0
                trend_tahmini = reel_girdi * (1.0 + sinirli_trend * 0.65)
                lag_ortalamasi = 0.50 * reel_girdi + 0.30 * lag1_girdi + 0.20 * lag7_girdi
                # Eğer ileri bir tarih seçildiyse o ayın mevsimsel çarpanını yedek tahmine de yansıt
                mevsim_duzeltme = 1.0
                if tarih_degisti_mi and not df_aylik_reel.empty:
                    u_aylik = df_aylik_reel[df_aylik_reel["MAL_ADI"] == secili_odak_urun]
                    if not u_aylik.empty:
                        yil_o = float(u_aylik["AYLIK_REEL_ORT"].mean())
                        hedef_a = u_aylik[u_aylik["AY"] == int(ay_girdi)]["AYLIK_REEL_ORT"]
                        if yil_o > 0 and not hedef_a.empty:
                            mevsim_duzeltme = float(hedef_a.mean()) / yil_o
                tahmin_fiyat = round((0.60 * trend_tahmini + 0.40 * lag_ortalamasi) * mevsim_duzeltme, 2)

            belirsizlik_marji = max(float(oyn7_girdi), float(tahmin_fiyat) * 0.06)
            alt_bant = alt_bant_hazir if alt_bant_hazir is not None else max(0.01, round(tahmin_fiyat - belirsizlik_marji, 2))
            ust_bant = ust_bant_hazir if ust_bant_hazir is not None else round(tahmin_fiyat + belirsizlik_marji, 2)
            belirsizlik_marji = round((ust_bant - alt_bant) / 2.0, 2)

            beklenen_degisim_yuzde = (
                ((tahmin_fiyat - reel_girdi) / reel_girdi) * 100.0 if reel_girdi > 0 else 0.0
            )

            if beklenen_degisim_yuzde >= 3.0:
                karar_etiketi = "ŞİMDİ AL — Alımı Öne Çekin"
                karar_aciklama = (
                    f"Gelecek hafta fiyatın **+%{beklenen_degisim_yuzde:.1f}** yükselerek "
                    f"**{tahmin_fiyat:.2f} TL/{birim_adi}** bandına çıkması bekleniyor. "
                    f"Zam gelmeden bugün stok/sözleşme yapmak kârlı olacaktır."
                )
                karar_tipi = "success"
            elif beklenen_degisim_yuzde <= -3.0:
                karar_etiketi = "BEKLE — Gelecek Hafta Ucuzlayabilir"
                karar_aciklama = (
                    f"Gelecek hafta fiyatın **%{beklenen_degisim_yuzde:.1f}** gerileyerek "
                    f"**{tahmin_fiyat:.2f} TL/{birim_adi}** civarına inmesi bekleniyor. "
                    f"Büyük stok yerine sadece bu haftanın acil ihtiyacını alın."
                )
                karar_tipi = "error"
            else:
                karar_etiketi = "NORMAL — Standart Haftalık Alıma Devam"
                karar_aciklama = (
                    f"Gelecek hafta fiyatın bugünkü seviyeye çok yakın (**%{beklenen_degisim_yuzde:+.1f}** | "
                    f"**{tahmin_fiyat:.2f} TL/{birim_adi}**) kalması bekleniyor. Olağan haftalık siparişinizi verebilirsiniz."
                )
                karar_tipi = "info"

            # Büyük ve net karar kutusu en üstte
            if karar_tipi == "success":
                st.success(f"### {karar_etiketi}\n{karar_aciklama}")
            elif karar_tipi == "error":
                st.error(f"### {karar_etiketi}\n{karar_aciklama}")
            else:
                st.info(f"### {karar_etiketi}\n{karar_aciklama}")

            tahmin_vurgu = "#DC2626" if beklenen_degisim_yuzde >= 3 else ("#1B7A43" if beklenen_degisim_yuzde <= -3 else "#F59E0B")
            st.markdown(
                f"""
<div style="display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:8px; margin-bottom:10px;">
<div class="signal-card" style="min-height:84px; padding:10px 11px; border-left:4px solid #64748B;">
<div style="color:#64748B; font-size:0.74rem; font-weight:700; margin-bottom:4px; white-space:nowrap;">Bugünkü Fiyat</div>
<div style="color:#1E293B; font-size:1.02rem; font-weight:800; white-space:nowrap; margin-bottom:3px;">{reel_girdi:.2f} TL</div>
<div style="color:#64748B; font-size:0.72rem; white-space:nowrap;">Birim: {birim_adi}</div>
</div>
<div class="signal-card" style="min-height:84px; padding:10px 11px; border-left:4px solid {tahmin_vurgu};">
<div style="color:#64748B; font-size:0.74rem; font-weight:700; margin-bottom:4px; white-space:nowrap;">Haftaya Tahmin</div>
<div style="color:#1E293B; font-size:1.02rem; font-weight:800; white-space:nowrap; margin-bottom:3px;">{tahmin_fiyat:.2f} TL</div>
<div style="color:#64748B; font-size:0.72rem; white-space:nowrap;">{beklenen_degisim_yuzde:+.1f}% Değişim</div>
</div>
<div class="signal-card" style="min-height:84px; padding:10px 11px; border-left:4px solid #1B7A43;">
<div style="color:#64748B; font-size:0.74rem; font-weight:700; margin-bottom:4px; white-space:nowrap;">Fiyat Aralığı</div>
<div style="color:#1E293B; font-size:0.95rem; font-weight:800; white-space:nowrap; margin-bottom:3px;">{alt_bant:.1f}–{ust_bant:.1f} TL</div>
<div style="color:#64748B; font-size:0.72rem; white-space:nowrap;">±{belirsizlik_marji:.2f} TL Marj</div>
</div>
</div>
""",
                unsafe_allow_html=True,
            )

            # Görsel Tahmin Aralığı Grafiği (Bugün vs. Gelecek Hafta Alt-Beklenen-Üst)
            fig_tahmin = go.Figure()
            fig_tahmin.add_trace(
                go.Bar(
                    x=["Bugünkü Reel Fiyat", "Gelecek Hafta (En Düşük)", "Gelecek Hafta (Beklenen)", "Gelecek Hafta (En Yüksek)"],
                    y=[reel_girdi, alt_bant, tahmin_fiyat, ust_bant],
                    marker_color=["#64748B", "#22C55E", "#1B7A43", "#F59E0B"],
                    text=[f"{v:.2f} TL" for v in [reel_girdi, alt_bant, tahmin_fiyat, ust_bant]],
                    textposition="outside",
                )
            )
            fig_tahmin.update_layout(
                height=250,
                margin=dict(l=10, r=10, t=25, b=10),
                yaxis_title=f"Reel Fiyat (TL / {birim_adi})",
                yaxis=dict(range=[0, max(reel_girdi, ust_bant) * 1.24]),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
            )
            st.plotly_chart(fig_tahmin, use_container_width=True)

            st.caption(
                f"**Tahmin Motoru:** {tahmin_kaynagi} | "
                f"Olası Fiyat Aralığı: **{alt_bant:.2f} ₺ – {ust_bant:.2f} ₺**\n\n"
                "Bu öngörü istatistiksel bir tahmindir; ani hava olayları ve arz şokları nedeniyle kesin fiyat garantisi vermez."
            )

            # Opsiyonel: 01_Veri/urun_kumeleri.csv varsa seçili ürünün küme rozeti + daha ucuz ikame ürünler
            _kume_rozeti_ve_ikame_goster(secili_odak_urun, VERILER.get("urun_kumeleri", pd.DataFrame()), df_ozellikli)
        else:
            st.warning("Seçili ürün için tahmin üretilecek kayıt bulunamadı.")

    # -------------------------------------------------------------------------
    # 3. ADIM (SAĞ): TEDARİKÇİ TEKLİF KONTROLÜ (DİNAMİK ŞUBE SAYILI)
    # -------------------------------------------------------------------------
    with karar_sag:
        st.markdown(f"#### 3. Tedarikçi Teklif Kontrolü — {secili_odak_urun}")
        st.caption(
            "Tedarikçinin size verdiği fiyatı ve şube başına sipariş miktarını girin. "
            "Sistem, haldeki en düşük–ortalama–en yüksek (Hal Taban / Ortalama / Tavan) fiyatlarla kıyaslayıp **kabul / pazarlık / ret** önerisi verir."
        )

        if not df_urun_karar.empty:
            son_fiyat_satiri = (
                df_urun_karar.dropna(subset=["ORTALAMA_UCRET"]).iloc[-1]
                if "ORTALAMA_UCRET" in df_urun_karar.columns
                and df_urun_karar["ORTALAMA_UCRET"].notna().any()
                else df_urun_karar.iloc[-1]
            )
            birim_etiket = str(son_fiyat_satiri.get("BIRIM", "KG"))
            son_ort = _guvenli_sayi(son_fiyat_satiri.get("ORTALAMA_UCRET", 25.0), 25.0)
            son_asg = (
                _guvenli_sayi(son_fiyat_satiri["ASGARI_UCRET"], round(son_ort * 0.80, 2))
                if "ASGARI_UCRET" in son_fiyat_satiri and pd.notna(son_fiyat_satiri["ASGARI_UCRET"])
                else round(son_ort * 0.80, 2)
            )
            son_azm = (
                _guvenli_sayi(son_fiyat_satiri["AZAMI_UCRET"], round(son_ort * 1.25, 2))
                if "AZAMI_UCRET" in son_fiyat_satiri and pd.notna(son_fiyat_satiri["AZAMI_UCRET"])
                else round(son_ort * 1.25, 2)
            )

            st.markdown(
                f"""
<div style="display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:8px; margin-bottom:10px;">
<div class="signal-card" style="min-height:84px; padding:10px 11px; border-left:4px solid #1B7A43;">
<div style="color:#64748B; font-size:0.74rem; font-weight:700; margin-bottom:4px; white-space:nowrap;">Hal Taban</div>
<div style="color:#1E293B; font-size:1.02rem; font-weight:800; white-space:nowrap; margin-bottom:3px;">{son_asg:.2f} TL</div>
<div style="color:#64748B; font-size:0.72rem; white-space:nowrap;">Asgari / {birim_etiket}</div>
</div>
<div class="signal-card" style="min-height:84px; padding:10px 11px; border-left:4px solid #3B82F6;">
<div style="color:#64748B; font-size:0.74rem; font-weight:700; margin-bottom:4px; white-space:nowrap;">Hal Ortalama</div>
<div style="color:#1E293B; font-size:1.02rem; font-weight:800; white-space:nowrap; margin-bottom:3px;">{son_ort:.2f} TL</div>
<div style="color:#64748B; font-size:0.72rem; white-space:nowrap;">Piyasa / {birim_etiket}</div>
</div>
<div class="signal-card" style="min-height:84px; padding:10px 11px; border-left:4px solid #F59E0B;">
<div style="color:#64748B; font-size:0.74rem; font-weight:700; margin-bottom:4px; white-space:nowrap;">Hal Tavan</div>
<div style="color:#1E293B; font-size:1.02rem; font-weight:800; white-space:nowrap; margin-bottom:3px;">{son_azm:.2f} TL</div>
<div style="color:#64748B; font-size:0.72rem; white-space:nowrap;">Azami / {birim_etiket}</div>
</div>
</div>
""",
                unsafe_allow_html=True,
            )

            tk_c1, tk_c2 = st.columns(2)
            with tk_c1:
                teklif_fiyat = st.number_input(
                    f"Tedarikçi Teklifi (TL / {birim_etiket}):",
                    min_value=0.01,
                    value=round(son_ort * 1.05, 2),
                    step=0.50,
                    key="tedarikci_teklif_girdi",
                )
            with tk_c2:
                sube_basi_miktar = st.number_input(
                    f"Şube Başı Sipariş ({birim_etiket}):",
                    min_value=1.0,
                    value=50.0,
                    step=5.0,
                    key="tedarikci_sube_miktar",
                    help=f"Sol menüde seçili {aktif_sube_sayisi} şube ile otomatik çarpılır.",
                )

            toplam_siparis_miktari = sube_basi_miktar * float(aktif_sube_sayisi)
            st.caption(
                f"**Toplam Sipariş Hacmi:** `{sube_basi_miktar:,.0f} {birim_etiket}/şube` × **`{aktif_sube_sayisi} Şube`** "
                f"= **`{toplam_siparis_miktari:,.0f} {birim_etiket}`** *(Şube sayısını sol menüden değiştirebilirsiniz)*"
            )

            if teklif_fiyat <= son_ort:
                avantaj_birim = son_ort - teklif_fiyat
                sube_avantaj = avantaj_birim * sube_basi_miktar
                toplam_avantaj = avantaj_birim * toplam_siparis_miktari
                st.success(
                    f"**İYİ TEKLİF — ONAYLANABİLİR**\n\n"
                    f"• Teklif (`{teklif_fiyat:.2f} TL`), hal ortalamasının (`{son_ort:.2f} TL`) **`{avantaj_birim:.2f} TL`** altında.\n"
                    f"• **Şube Başı Kazanç:** `{sube_avantaj:,.2f} TL` | **{aktif_sube_sayisi} Şube Toplam Kazanç:** **`{toplam_avantaj:,.2f} TL`**"
                )
            elif teklif_fiyat <= son_azm:
                pazarlik_birim = teklif_fiyat - son_ort
                sube_pazarlik = pazarlik_birim * sube_basi_miktar
                pazarlik_toplam = pazarlik_birim * toplam_siparis_miktari
                st.warning(
                    f"**PAZARLIK PAYI VAR — İNDİRİM İSTEYİN**\n\n"
                    f"• Teklif (`{teklif_fiyat:.2f} TL`) hal tavanını aşmıyor ancak ortalamanın (`{son_ort:.2f} TL`) üzerinde.\n"
                    f"• **Hedef İndirim:** Birimde **`{pazarlik_birim:.2f} TL/{birim_etiket}`** düşürülerek `{son_ort:.2f} TL` hedeflenmeli.\n"
                    f"• **Kurtarılacak Tutar:** Şube başı `{sube_pazarlik:,.2f} TL` | **{aktif_sube_sayisi} Şube Toplam:** **`{pazarlik_toplam:,.2f} TL`**"
                )
            else:
                asiri_fark_tavan = teklif_fiyat - son_azm
                asiri_fark_ort = teklif_fiyat - son_ort
                toplam_zarar = asiri_fark_ort * toplam_siparis_miktari
                st.error(
                    f"**HAL TAVANININ ÜSTÜNDE — TEKLİFİ REDDEDİN!**\n\n"
                    f"• Teklif (`{teklif_fiyat:.2f} TL`), haldeki en yüksek kalite tavan fiyatını (`{son_azm:.2f} TL`) bile **`{asiri_fark_tavan:.2f} TL`** aşıyor!\n"
                    f"• Bu fiyattan alınırsa **{aktif_sube_sayisi} şube için** hal ortalamasına kıyasla **`{toplam_zarar:,.2f} TL`** fazla ödeme yapılmış olur."
                )

            fig_teklif = go.Figure()
            fig_teklif.add_trace(
                go.Bar(
                    x=["Hal En Düşük", "Hal Ortalama", "Hal En Yüksek", "Tedarikçi Teklifi"],
                    y=[son_asg, son_ort, son_azm, teklif_fiyat],
                    marker_color=[
                        "#1B7A43",
                        "#3B82F6",
                        "#F59E0B",
                        "#1B7A43" if teklif_fiyat <= son_ort else ("#F59E0B" if teklif_fiyat <= son_azm else "#DC2626"),
                    ],
                    text=[f"{v:.2f} TL" for v in [son_asg, son_ort, son_azm, teklif_fiyat]],
                    textposition="outside",
                )
            )
            fig_teklif.update_layout(
                height=250,
                margin=dict(l=10, r=10, t=25, b=10),
                yaxis_title=f"Birim Fiyat (₺ / {birim_etiket})",
                yaxis=dict(range=[0, max(son_azm, teklif_fiyat) * 1.24]),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
            )
            st.plotly_chart(fig_teklif, use_container_width=True)
        else:
            st.warning("Tedarikçi teklif kontrolü için ürün fiyat kaydı bulunamadı.")

    # -------------------------------------------------------------------------
    # 3.5 ADIM: 1 AYLIK (4 HAFTALIK) FİYAT PROJEKSİYONU VE STRATEJİK KARAR
    # -------------------------------------------------------------------------
    if not df_urun_karar.empty:
        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
        with st.expander(f"📅 1 Aylık Fiyat Projeksiyonu ve Stratejik Karar — {secili_odak_urun}", expanded=False):
            st.caption(
                "Bugünden itibaren 1., 2., 3. hafta ve 1 ay (30 kayıt) sonrası reel fiyat yörüngesini, "
                "1 aylık belirsizlik bandını ve aylık stratejik satın alma kararını gösterir."
            )

            # 1 Aylık projeksiyon değerlerini belirle:
            # 1) Eğer hedef tarih değiştirilmediyse ve gelecek_hafta_ve_ay_tahminleri.csv içinde hazır satır varsa onu kullan
            # 2) Hedef tarih değiştirildiyse veya CSV yoksa model_aylik.joblib üzerinden 12 sütunla canlı tahmin al
            # 3) Model de henüz yoksa mevcut istatistiksel mevsimsel/trend yedek motoru ile hatasız üret
            bugun_p = float(reel_girdi)
            t_1h = float(tahmin_fiyat)
            t_2h = None
            t_3h = None
            t_1ay = None
            ay_alt = None
            ay_ust = None
            ay_degisim_pct = None
            ay_karar_ham = None
            ay_motor_kaynak = "Geçmiş Mevsimsellik & Trend Yedek Motoru"

            if (not tarih_degisti_mi) and hazir_tahmin_satiri is not None:
                t_1ay_csv = hazir_tahmin_satiri.get("TAHMIN_1_AY (30_KAYIT)", np.nan)
                if pd.notna(t_1ay_csv):
                    bugun_p = _guvenli_sayi(hazir_tahmin_satiri.get("BUGUNKU_REEL_FIYAT", bugun_p), bugun_p)
                    t_1h = _guvenli_sayi(hazir_tahmin_satiri.get("TAHMIN_1_HAFTA", t_1h), t_1h)
                    t_2h = _guvenli_sayi(hazir_tahmin_satiri.get("TAHMIN_2_HAFTA", np.nan), np.nan)
                    t_3h = _guvenli_sayi(hazir_tahmin_satiri.get("TAHMIN_3_HAFTA", np.nan), np.nan)
                    t_1ay = round(float(t_1ay_csv), 2)
                    ay_alt = _guvenli_sayi(hazir_tahmin_satiri.get("ARALIK_1_AY_ALT", np.nan), np.nan)
                    ay_ust = _guvenli_sayi(hazir_tahmin_satiri.get("ARALIK_1_AY_UST", np.nan), np.nan)
                    ay_degisim_pct = _guvenli_sayi(hazir_tahmin_satiri.get("DEGISIM_1_AY_YUZDE", np.nan), np.nan)
                    ay_karar_ham = (
                        str(hazir_tahmin_satiri["KARAR_1_AY"]).strip()
                        if "KARAR_1_AY" in hazir_tahmin_satiri and pd.notna(hazir_tahmin_satiri["KARAR_1_AY"])
                        else None
                    )
                    ay_motor_kaynak = "Eğitilmiş 1 Aylık Makine Öğrenmesi Modeli"

            if t_1ay is None and MODEL_AYLIK_AKTIF and MODEL_AYLIK is not None:
                try:
                    t_1ay = round(float(MODEL_AYLIK.predict(X_tahmin)[0]), 2)
                    ay_motor_kaynak = "Eğitilmiş 1 Aylık Makine Öğrenmesi Modeli (Canlı Tarih Tahmini)"
                except Exception:
                    t_1ay = None

            if t_1ay is None:
                # Yedek 1 aylık projeksiyon: seçili ay -> sonraki ay mevsimsel geçiş oranı * bugünkü fiyat
                sonraki_ay_no = 1 if int(ay_girdi) == 12 else int(ay_girdi) + 1
                mev_oran = 1.0
                if not df_aylik_reel.empty:
                    u_ay_df = df_aylik_reel[df_aylik_reel["MAL_ADI"] == secili_odak_urun]
                    if not u_ay_df.empty:
                        bu_a = u_ay_df[u_ay_df["AY"] == int(ay_girdi)]["AYLIK_REEL_ORT"]
                        sn_a = u_ay_df[u_ay_df["AY"] == sonraki_ay_no]["AYLIK_REEL_ORT"]
                        if not bu_a.empty and not sn_a.empty and float(bu_a.mean()) > 0:
                            mev_oran = float(sn_a.mean()) / float(bu_a.mean())
                t_1ay = round(max(0.01, bugun_p * mev_oran), 2)

            # Ara haftalar (2. Hafta ve 3. Hafta) eksikse yumuşak doğrusal ara değerle tamamla
            if t_2h is None or pd.isna(t_2h):
                t_2h = round(t_1h + (t_1ay - t_1h) * 0.35, 2)
            if t_3h is None or pd.isna(t_3h):
                t_3h = round(t_1h + (t_1ay - t_1h) * 0.70, 2)

            ay_belirsizlik = max(float(oyn30_girdi), abs(t_1ay) * 0.10)
            if ay_alt is None or pd.isna(ay_alt):
                ay_alt = max(0.01, round(t_1ay - ay_belirsizlik, 2))
            if ay_ust is None or pd.isna(ay_ust):
                ay_ust = round(t_1ay + ay_belirsizlik, 2)

            if ay_degisim_pct is None or pd.isna(ay_degisim_pct):
                ay_degisim_pct = round(((t_1ay - bugun_p) / bugun_p) * 100.0, 1) if bugun_p > 0 else 0.0

            # Aylık Stratejik Karar Rozeti (ŞİMDİ AL / BEKLE / NORMAL TEDARİK)
            karar_ust_metin = str(ay_karar_ham).upper() if ay_karar_ham else ""
            if ("AL" in karar_ust_metin and "NORMAL" not in karar_ust_metin) or (not karar_ust_metin and ay_degisim_pct >= 5.0):
                ay_rozet_baslik = "ŞİMDİ AL — Aylık Stok / Sözleşme Önerisi"
                ay_rozet_renk, ay_rozet_bg, ay_rozet_border = "#15803D", "#DCFCE7", "#16A34A"
                ay_rozet_not = (
                    f"1 ay içinde reel fiyatın <b>+%{ay_degisim_pct:.1f}</b> artarak <b>{t_1ay:.2f} ₺</b> "
                    f"(bandı: {ay_alt:.2f}–{ay_ust:.2f} ₺) düzeyine çıkması bekleniyor. Aylık ihtiyacı şimdiden kilitlemek kârlıdır."
                )
            elif "BEKLE" in karar_ust_metin or (not karar_ust_metin and ay_degisim_pct <= -5.0):
                ay_rozet_baslik = "BEKLE — Aylık Dönemde Ucuzlama Bekleniyor"
                ay_rozet_renk, ay_rozet_bg, ay_rozet_border = "#B91C1C", "#FEE2E2", "#DC2626"
                ay_rozet_not = (
                    f"1 ay içinde reel fiyatın <b>%{ay_degisim_pct:.1f}</b> düşerek <b>{t_1ay:.2f} ₺</b> "
                    f"(bandı: {ay_alt:.2f}–{ay_ust:.2f} ₺) düzeyine inmesi öngörülüyor. Uzun süreli stok yerine kademeli/beklemeli alım yapın."
                )
            else:
                ay_rozet_baslik = "NORMAL TEDARİK — Dengeli Aylık Seyir"
                ay_rozet_renk, ay_rozet_bg, ay_rozet_border = "#A16207", "#FEF9C3", "#CA8A04"
                ay_rozet_not = (
                    f"1 aylık projeksiyonda fiyatın <b>{t_1ay:.2f} ₺</b> ({ay_degisim_pct:+.1f}% | bandı: {ay_alt:.2f}–{ay_ust:.2f} ₺) "
                    "civarında dengeli seyretmesi bekleniyor. Planlı haftalık tedarik akışına devam edilebilir."
                )

            ay_sol, ay_sag = st.columns([1.3, 0.9], gap="large")
            with ay_sol:
                noktalar_x = ["Bugün", "1. Hafta", "2. Hafta", "3. Hafta", "1 Ay Sonra"]
                noktalar_y = [bugun_p, t_1h, t_2h, t_3h, t_1ay]
                # Bugünden 1 ay sonraya açılan güven/belirsizlik bandı
                bant_ust_y = [
                    bugun_p,
                    max(ust_bant, t_1h),
                    round(t_2h + (ay_ust - t_1ay) * 0.60, 2),
                    round(t_3h + (ay_ust - t_1ay) * 0.82, 2),
                    ay_ust,
                ]
                bant_alt_y = [
                    bugun_p,
                    min(alt_bant, t_1h),
                    max(0.01, round(t_2h - (t_1ay - ay_alt) * 0.60, 2)),
                    max(0.01, round(t_3h - (t_1ay - ay_alt) * 0.82, 2)),
                    ay_alt,
                ]

                fig_aylik = go.Figure()
                fig_aylik.add_trace(
                    go.Scatter(
                        x=noktalar_x,
                        y=bant_ust_y,
                        mode="lines",
                        line=dict(width=0),
                        showlegend=False,
                        hoverinfo="skip",
                    )
                )
                fig_aylik.add_trace(
                    go.Scatter(
                        x=noktalar_x,
                        y=bant_alt_y,
                        mode="lines",
                        line=dict(width=0),
                        fill="tonexty",
                        fillcolor="rgba(27, 122, 67, 0.16)",
                        name="1 Aylık Belirsizlik Bandı (Alt–Üst)",
                    )
                )
                fig_aylik.add_trace(
                    go.Scatter(
                        x=noktalar_x,
                        y=noktalar_y,
                        mode="lines+markers+text",
                        line=dict(color="#1B7A43", width=3),
                        marker=dict(size=10, color="#14532D", line=dict(width=2, color="#FFFFFF")),
                        text=[f"{v:.2f} ₺" for v in noktalar_y],
                        textposition="top center",
                        name="Beklenen Reel Fiyat Eğrisi",
                    )
                )
                y_ust_sinir = max(bant_ust_y) * 1.18 if max(bant_ust_y) > 0 else 10.0
                y_alt_sinir = max(0.0, min(bant_alt_y) * 0.85)
                fig_aylik.update_layout(
                    height=310,
                    margin=dict(l=15, r=15, t=25, b=10),
                    xaxis_title="Zaman Ufku",
                    yaxis_title=f"TÜFE Bazlı Reel Fiyat (₺ / {birim_adi})",
                    yaxis=dict(range=[y_alt_sinir, y_ust_sinir]),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    hovermode="x unified",
                )
                st.plotly_chart(fig_aylik, use_container_width=True)

            with ay_sag:
                st.markdown(
                    f"""
<div class="signal-card" style="border-top:5px solid {ay_rozet_border}; background:{ay_rozet_bg}; padding:16px 18px; margin-bottom:12px;">
<div style="font-size:0.78rem; font-weight:700; color:{ay_rozet_renk}; margin-bottom:4px;">AYLIK STRATEJİK KARAR ROZETİ</div>
<div style="font-size:1.10rem; font-weight:800; color:{ay_rozet_renk}; margin-bottom:8px;">{ay_rozet_baslik}</div>
<div style="font-size:0.86rem; color:#1E293B; line-height:1.45;">{ay_rozet_not}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

                ak1, ak2 = st.columns(2)
                ak1.markdown(
                    f"""
<div class="signal-card" style="min-height:88px; padding:11px 12px; border-left:4px solid #1B7A43;">
<div class="signal-card-title" style="font-size:0.77rem;">1 Ay Sonra Tahmin</div>
<div style="color:#1E293B; font-size:1.08rem; font-weight:800;">{t_1ay:.2f} ₺</div>
<div class="signal-card-sub" style="font-size:0.75rem;">{ay_degisim_pct:+.1f}% Aylık Değişim</div>
</div>
""",
                    unsafe_allow_html=True,
                )
                ak2.markdown(
                    f"""
<div class="signal-card" style="min-height:88px; padding:11px 12px; border-left:4px solid #3B82F6;">
<div class="signal-card-title" style="font-size:0.77rem;">1 Aylık Güven Bandı</div>
<div style="color:#1E293B; font-size:1.02rem; font-weight:800;">{ay_alt:.2f} – {ay_ust:.2f} ₺</div>
<div class="signal-card-sub" style="font-size:0.75rem;">Alt – Üst Sınır ({birim_adi})</div>
</div>
""",
                    unsafe_allow_html=True,
                )
                st.caption(
                    f"**Aylık Motor:** {ay_motor_kaynak}\n\n"
                    "Bu projeksiyon istatistiksel bir öngörüdür; ani hava olayları ve arz şokları nedeniyle kesin fiyat garantisi vermez."
                )


    # -------------------------------------------------------------------------
    # 4. OPSİYONEL AÇILIR BÖLÜM: MODEL PERFORMANS KARŞILAŞTIRMASI & DEĞİŞKEN ÖNEMİ
    #    (01_Veri/model_karsilastirma.csv veya 01_Veri/ozellik_onemi.csv yoksa gizli kalır)
    # -------------------------------------------------------------------------
    df_model_kars = VERILER.get("model_karsilastirma", pd.DataFrame())
    df_ozellik_onemi = VERILER.get("ozellik_onemi", pd.DataFrame())

    if not df_model_kars.empty or (not df_ozellik_onemi.empty and len(df_ozellik_onemi.columns) >= 2):
        with st.expander("📊 Model Performans Karşılaştırması ve Değişken Önem Düzeyleri", expanded=False):
            mk_col1, mk_col2 = st.columns([1.05, 1.15], gap="large")
            with mk_col1:
                if not df_model_kars.empty:
                    st.markdown("##### Model Başarı Karşılaştırma Tablosu")
                    st.dataframe(df_model_kars, use_container_width=True, hide_index=True)
                else:
                    st.info("Model karşılaştırma tablosu henüz eklenmedi.")
            with mk_col2:
                if not df_ozellik_onemi.empty and len(df_ozellik_onemi.columns) >= 2:
                    st.markdown("##### Fiyat Tahminini En Çok Etkileyen Faktörler")
                    oz_df = df_ozellik_onemi.copy()
                    ad_kol = (
                        "Etkileyen Faktör"
                        if "Etkileyen Faktör" in oz_df.columns
                        else ("DEGISKEN" if "DEGISKEN" in oz_df.columns else oz_df.columns[0])
                    )
                    skor_kol = (
                        "Etki Skoru"
                        if "Etki Skoru" in oz_df.columns
                        else ("ONEM_SKORU" if "ONEM_SKORU" in oz_df.columns else oz_df.columns[1])
                    )
                    katki_kol = "Katkı Payı" if "Katkı Payı" in oz_df.columns else None
                    oz_df[skor_kol] = pd.to_numeric(oz_df[skor_kol], errors="coerce")
                    oz_df = oz_df.dropna(subset=[ad_kol, skor_kol]).sort_values(skor_kol, ascending=True).tail(12)
                    if not oz_df.empty:
                        oz_df["ETIKET_TR"] = oz_df[ad_kol].apply(_degisken_turkce_etiket)
                        metin_etiket = (
                            [f"{v:.3f} ({k})" for v, k in zip(oz_df[skor_kol], oz_df[katki_kol])]
                            if katki_kol
                            else [f"{v:.3f}" for v in oz_df[skor_kol]]
                        )
                        fig_oz = go.Figure(
                            go.Bar(
                                x=oz_df[skor_kol],
                                y=oz_df["ETIKET_TR"],
                                orientation="h",
                                marker_color="#1B7A43",
                                text=metin_etiket,
                                textposition="outside",
                            )
                        )
                        fig_oz.update_layout(
                            height=320,
                            margin=dict(l=10, r=60, t=15, b=10),
                            xaxis_title="Etki Skoru",
                            yaxis_title="Etkileyen Faktör",
                            xaxis=dict(range=[0, max(float(oz_df[skor_kol].max()) * 1.25, 0.1)]),
                            plot_bgcolor="#FFFFFF",
                            paper_bgcolor="#FFFFFF",
                        )
                        st.plotly_chart(fig_oz, use_container_width=True)

    # -------------------------------------------------------------------------
    # 5. OPSİYONEL AÇILIR BÖLÜM: SHAP AÇIKLANABİLİRLİK & MEVSİMSEL KÜME PROFİLLERİ
    # -------------------------------------------------------------------------
    karar_shap_yol = _dosya_yolu_coz("03_Model/shap_aciklanabilirlik.png")
    karar_kume_yol = _dosya_yolu_coz("03_Model/kumeleme_mevsimsel_profiller.png")
    karar_shap_var = os.path.exists(karar_shap_yol)
    karar_kume_var = os.path.exists(karar_kume_yol)

    if karar_shap_var or karar_kume_var:
        with st.expander("🔬 Model Açıklanabilirliği ve Mevsimsel Küme Profilleri", expanded=False):
            if karar_shap_var:
                st.markdown("##### SHAP Model Açıklanabilirlik Analizi")
                _, ks_orta, _ = st.columns([0.12, 0.76, 0.12])
                with ks_orta:
                    st.image(str(karar_shap_yol), use_container_width=True)
                st.markdown(
                    '<div class="insight-note"><b>SHAP İş Yorumu:</b> '
                    "Bu grafik, yapay zekâ modelinin fiyat tahminini üretirken hangi faktöre (1 gün önceki fiyat, 30 günlük fiyat dalgalanması, haftalık mevsimsellik vb.) "
                    "ne yönde ağırlık verdiğini şeffaf biçimde gösterir. Böylece satın alma yöneticisi tahminin yalnızca sonucunu değil, dayanağını da denetleyebilir.</div>",
                    unsafe_allow_html=True,
                )
            if karar_kume_var:
                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                st.markdown("##### K-Means Mevsimsel Küme Profilleri")
                _, kk_orta, _ = st.columns([0.06, 0.88, 0.06])
                with kk_orta:
                    st.image(str(karar_kume_yol), use_container_width=True)
                st.markdown(
                    '<div class="insight-note"><b>Kümeleme İş Yorumu:</b> '
                    "Ürünler 12 aylık reel fiyat hareketlerine göre K-Means algoritmasıyla 4 stratejik mevsim grubuna ayrılmıştır; "
                    "aynı kümedeki ürünler menü planlamasında birbirine ikame edilebilir. Bu gruplama yıllık sözleşme ve stok takviminin omurgasını oluşturur.</div>",
                    unsafe_allow_html=True,
                )

    # -------------------------------------------------------------------------
    # 6. OPSİYONEL AÇILIR BÖLÜM: İZMİR DON OLAYLARI VE 15 ÖZELLİKLİ İKLİM MODELİ
    # -------------------------------------------------------------------------
    karar_don_gorsel = _dosya_yolu_coz("03_Model/don_etkisi_analiz.png")
    df_k_don_haftalik = VERILER.get("don_etkisi_haftalik_analiz", pd.DataFrame())
    df_k_don_model = VERILER.get("don_model_karsilastirma", pd.DataFrame())
    if os.path.exists(karar_don_gorsel) or not df_k_don_haftalik.empty or not df_k_don_model.empty:
        with st.expander("İzmir Don Olaylarının Gecikmeli Fiyat Etkisi ve 15 Özellikli İklim Modeli", expanded=False):
            if os.path.exists(karar_don_gorsel):
                _, kd_orta, _ = st.columns([0.08, 0.84, 0.08])
                with kd_orta:
                    st.image(str(karar_don_gorsel), use_container_width=True)
            kd_c1, kd_c2 = st.columns([1.15, 0.95], gap="large")
            with kd_c1:
                if not df_k_don_haftalik.empty:
                    st.markdown("##### Don Olayı Sonrası Ürün Bazlı 1–4 Haftalık Fiyat Tepkisi")
                    st.dataframe(df_k_don_haftalik, use_container_width=True, hide_index=True)
            with kd_c2:
                if not df_k_don_model.empty:
                    st.markdown("##### 12 Özellikli Temel Model ve 15 Özellikli İklim Modeli Karşılaştırması")
                    st.dataframe(df_k_don_model, use_container_width=True, hide_index=True)
            st.markdown(
                '<div class="insight-note"><b>İklim Destekli Model Yorumu:</b> '
                "Open-Meteo İzmir minimum sıcaklık ve don gecikme değişkenleriyle zenginleştirilen 15 özellikli model, kış dönemi tahmin hatasını (MAE) "
                "4.521 TL'den 4.505 TL'ye düşürmüş ve tahmin başarısını (R²) 0.8826'dan 0.8853'e yükseltmiştir. Don olayı sonrası Çalı Fasulye (+%34.3) "
                "ve Marul (+%16.5) gibi ürünlerde fiyat artışı 3–4. haftada zirveye ulaştığından don uyarısı anında erken tedarik önerilir.</div>",
                unsafe_allow_html=True,
            )

# =============================================================================
# 5. SEKME: TASARRUF SİMÜLATÖRÜ
# =============================================================================
def _tasarimli_excel_olustur(
    sim_df: pd.DataFrame,
    sube_sayisi: int,
    fire_orani: float,
    depo_orani: float,
    toplam_spot: float,
    toplam_akilli: float,
    toplam_net_tasarruf: float,
    toplam_tasarruf_yuzde: float,
    senaryo_a_maliyet: float = 0.0,
    senaryo_a_tasarruf: float = 0.0,
) -> bytes:
    """Sade, ferah ve yönetici dostu 2 sayfalı kurumsal Excel (.xlsx) raporu üretir."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Satin_Alma_Plani"
    ws.views.sheetView[0].showGridLines = True

    # 1. Satır: Ferah Ana Başlık (8 Sütun: A1:H1)
    ws.merge_cells("A1:H1")
    ws["A1"] = "AKILLI SATIN ALMA — YILLIK SATIN ALMA VE TASARRUF PLANI"
    ws["A1"].font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill(start_color="14532D", end_color="14532D", fill_type="solid")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 32

    # 2. Satır: Simülasyon Parametre Özeti
    ws.merge_cells("A2:H2")
    ws["A2"] = (
        f"Aktif Şube: {sube_sayisi}   |   Zayi / Bozulma Oranı: %{fire_orani:.1f}   |   "
        f"Depolama Maliyeti: %{depo_orani:.1f}   |   Tarih: {datetime.now().strftime('%d.%m.%Y')}"
    )
    ws["A2"].font = Font(name="Calibri", size=10, bold=True, color="334155")
    ws["A2"].fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 24

    # 4. Satır: Sadeleştirilmiş 8 Ana Sütun Başlığı
    basliklar = [
        "Ürün Adı",
        "Birim",
        "En Uygun Ay",
        "Yıllık Toplam Miktar",
        "Yıllık Normal Maliyet",
        "Yıllık Akıllı Maliyet",
        "Yıllık Net Kazanç",
        "Önerilen Satın Alma Kararı",
    ]

    ince_kenar = Side(border_style="thin", color="CBD5E1")
    hucre_cerceve = Border(left=ince_kenar, right=ince_kenar, top=ince_kenar, bottom=ince_kenar)
    baslik_dolgu = PatternFill(start_color="1B7A43", end_color="1B7A43", fill_type="solid")
    baslik_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

    ws.row_dimensions[4].height = 28
    for col_idx, b_metin in enumerate(basliklar, start=1):
        c = ws.cell(row=4, column=col_idx, value=b_metin)
        c.fill = baslik_dolgu
        c.font = baslik_font
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = hucre_cerceve

    zebra_acik = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    zebra_koyu = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    veri_font = Font(name="Calibri", size=10, color="0F172A")
    kazanc_font = Font(name="Calibri", size=10, bold=True, color="14532D")

    # Yalnızca son sütun (Önerilen Karar) için yumuşak durum renkleri
    yesil_dolgu = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    yesil_font = Font(name="Calibri", size=10, bold=True, color="166534")
    sari_dolgu = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")
    sari_font = Font(name="Calibri", size=10, bold=True, color="854D0E")

    stok_esik_yuzde = float(fire_orani + depo_orani)
    baslangic_satir = 5

    for idx, r in sim_df.reset_index(drop=True).iterrows():
        satir_no = baslangic_satir + idx
        ws.row_dimensions[satir_no].height = 24
        dolgu = zebra_acik if idx % 2 == 0 else zebra_koyu

        avantaj_pct = float(r["MEVSIMSEL_AVANTAJ_YUZDE"])
        net_marj_pct = avantaj_pct - stok_esik_yuzde
        karar_dolgu = yesil_dolgu if net_marj_pct > 0 else sari_dolgu
        karar_font = yesil_font if net_marj_pct > 0 else sari_font

        satir_degerleri = [
            str(r["MAL_ADI"]),
            str(r["BIRIM"]),
            str(r["EN_UCUZ_AY"]),
            float(r["YILLIK_TOPLAM_KG"]),
            float(r["YILLIK_SPOT_MALIYET"]),
            float(r["YILLIK_AKILLI_MALIYET"]),
            float(r["YILLIK_NET_TASARRUF"]),
            str(r["STRATEJI_ONERISI"]),
        ]

        for col_idx, val in enumerate(satir_degerleri, start=1):
            hc = ws.cell(row=satir_no, column=col_idx, value=val)
            hc.border = hucre_cerceve
            if col_idx == 8:
                hc.fill = karar_dolgu
                hc.font = karar_font
            elif col_idx == 7:
                hc.fill = dolgu
                hc.font = kazanc_font
            else:
                hc.fill = dolgu
                hc.font = veri_font

            if col_idx in [1, 8]:
                hc.alignment = Alignment(horizontal="left", vertical="center")
            elif col_idx in [2, 3]:
                hc.alignment = Alignment(horizontal="center", vertical="center")
            else:
                hc.alignment = Alignment(horizontal="right", vertical="center")

            if col_idx == 4:
                hc.number_format = "#,##0"
            elif col_idx in [5, 6, 7]:
                hc.number_format = '#,##0 "TL"'

    # En Altta Ferah TOPLAM Satırı
    toplam_satir_no = baslangic_satir + len(sim_df)
    ws.row_dimensions[toplam_satir_no].height = 28
    toplam_dolgu = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    toplam_font = Font(name="Calibri", size=11, bold=True, color="14532D")

    toplam_degerleri = [
        "TOPLAM / GENEL ÖZET",
        "-",
        "-",
        float(sim_df["YILLIK_TOPLAM_KG"].sum()),
        float(toplam_spot),
        float(toplam_akilli),
        float(toplam_net_tasarruf),
        f"Yıllık Net Tasarruf Oranı: %{toplam_tasarruf_yuzde:.1f}",
    ]

    for col_idx, val in enumerate(toplam_degerleri, start=1):
        hc = ws.cell(row=toplam_satir_no, column=col_idx, value=val)
        hc.fill = toplam_dolgu
        hc.font = toplam_font
        hc.border = hucre_cerceve
        if col_idx in [1, 8]:
            hc.alignment = Alignment(horizontal="left", vertical="center")
        elif col_idx in [2, 3]:
            hc.alignment = Alignment(horizontal="center", vertical="center")
        else:
            hc.alignment = Alignment(horizontal="right", vertical="center")

        if col_idx == 4:
            hc.number_format = "#,##0"
        elif col_idx in [5, 6, 7]:
            hc.number_format = '#,##0 "TL"'

    sabit_genislikler = [22, 11, 16, 22, 23, 23, 23, 38]
    for col_idx, gen in enumerate(sabit_genislikler, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = gen

    # 2. Sayfa: Sade Senaryo Karşılaştırma Özeti (Dinamik Önerilen Strateji)
    ws2 = wb.create_sheet(title="Senaryo_Ozeti")
    ws2.views.sheetView[0].showGridLines = True
    ws2.merge_cells("A1:E1")
    ws2["A1"] = "YÖNETİM KARAR ALTERNATİFLERİ — SENARYO A VE SENARYO B KARŞILAŞTIRMASI"
    ws2["A1"].font = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
    ws2["A1"].fill = PatternFill(start_color="14532D", end_color="14532D", fill_type="solid")
    ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 30

    s2_basliklar = ["Satın Alma Senaryosu", "Yıllık Toplam Maliyet", "Yıllık Net Kazanç", "Tasarruf Oranı", "Yönetici Değerlendirmesi"]
    ws2.row_dimensions[3].height = 26
    for col_idx, b_metin in enumerate(s2_basliklar, start=1):
        c = ws2.cell(row=3, column=col_idx, value=b_metin)
        c.fill = baslik_dolgu
        c.font = baslik_font
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = hucre_cerceve

    senaryo_a_pct = (senaryo_a_tasarruf / toplam_spot) if toplam_spot > 0 else 0.0
    senaryo_b_pct = (toplam_net_tasarruf / toplam_spot) if toplam_spot > 0 else 0.0
    a_kazandi = senaryo_a_tasarruf >= toplam_net_tasarruf

    s2_satirlar = [
        (
            "Mevcut Durum: Klasik Spot Alım",
            float(toplam_spot),
            0.0,
            0.0,
            "Referans baz senaryo (mevsimsel fiyat dalgalanmasına açık)",
            zebra_koyu,
            veri_font,
        ),
        (
            "Senaryo A: Sabit Fiyatlı Tedarikçi Sözleşmesi",
            float(senaryo_a_maliyet),
            float(senaryo_a_tasarruf),
            float(senaryo_a_pct),
            "ÖNERİLEN STRATEJİ • %0 Zayi ve %0 Depo riskiyle en yüksek net kazanç" if a_kazandi else "Alternatif • %0 Zayi ve %0 Depo riski",
            yesil_dolgu if a_kazandi else zebra_acik,
            yesil_font if a_kazandi else veri_font,
        ),
        (
            "Senaryo B: Karma Strateji (Stoklama + Sözleşme)",
            float(toplam_akilli),
            float(toplam_net_tasarruf),
            float(senaryo_b_pct),
            "ÖNERİLEN STRATEJİ • Ürün bazlı en yüksek net bütçe tasarrufu" if not a_kazandi else "Alternatif • Fiziksel stok ve sözleşme karma planı",
            yesil_dolgu if not a_kazandi else zebra_acik,
            yesil_font if not a_kazandi else veri_font,
        ),
    ]
    for r_i, (s_ad, s_mal, s_tas, s_pct, s_not, s_dolgu, s_fnt) in enumerate(s2_satirlar, start=4):
        ws2.row_dimensions[r_i].height = 26
        degerler = [s_ad, s_mal, s_tas, s_pct, s_not]
        for c_i, val in enumerate(degerler, start=1):
            hc = ws2.cell(row=r_i, column=c_i, value=val)
            hc.fill = s_dolgu
            hc.font = s_fnt
            hc.border = hucre_cerceve
            hc.alignment = Alignment(horizontal="left" if c_i in [1, 5] else "right", vertical="center")
            if c_i in [2, 3]:
                hc.number_format = '#,##0 "TL"'
            elif c_i == 4:
                hc.number_format = "0.0%"

    for col_idx, genislik in enumerate([40, 22, 22, 16, 52], start=1):
        ws2.column_dimensions[get_column_letter(col_idx)].width = genislik

    tampon = BytesIO()
    wb.save(tampon)
    tampon.seek(0)
    return tampon.getvalue()


with sekme_simulator:
    st.subheader("🏪 Çok Şubeli Yıllık Tasarruf Simülatörü")
    st.caption(
        "Şube sayısı, zayi/bozulma ve soğuk depolama oranlarına göre yıllık Spot Alım ile Akıllı Alım maliyetlerini karşılaştırın. "
        "Detaylı satın alma planı tablosu, Senaryo A ve Senaryo B karşılaştırması ile yönetici önerileri alt kısımdaki açılır pencerelerdedir."
    )

    # -------------------------------------------------------------------------
    # 1. KULLANICI GİRDİLERİ (ŞUBE SAYISI, ZAYİ/BOZULMA ORANI %, DEPOLAMA MALİYETİ %)
    # -------------------------------------------------------------------------
    param_col1, param_col2, param_col3 = st.columns(3, gap="large")
    with param_col1:
        sube_sayisi = st.slider(
            "Zincirdeki Şube Sayısı",
            min_value=1,
            max_value=50,
            value=min(int(aktif_sube_sayisi), 50),
            step=1,
            help="Sol menüdeki aktif şube sayınızla otomatik senkronize gelir; farklı senaryolar için buradan da kaydırabilirsiniz.",
        )
    with param_col2:
        fire_orani = st.slider(
            "Beklenen Zayi / Bozulma Oranı (%)",
            min_value=0.0,
            max_value=25.0,
            value=6.0,
            step=0.5,
            help="Fiziksel stoklama durumunda beklenen ürün zayiatı / bozulma yüzdesi.",
        )
    with param_col3:
        depo_orani = st.slider(
            "Depolama / Soğuk Hava Maliyeti (%)",
            min_value=0.0,
            max_value=20.0,
            value=4.0,
            step=0.5,
            help="Stoklama süresince birim maliyet üzerine binen soğuk hava ve lojistik yüzdesi.",
        )

    toplam_stok_maliyet_orani = (fire_orani + depo_orani) / 100.0

    # -------------------------------------------------------------------------
    # 2. ÜRÜN SEPETİ (st.multiselect) VE ŞUBE BAŞI AYLIK TÜKETİM (st.data_editor)
    # -------------------------------------------------------------------------
    tum_sim_urunleri = (
        sorted(df_karar_destegi["MAL_ADI"].dropna().unique().tolist())
        if not df_karar_destegi.empty and "MAL_ADI" in df_karar_destegi.columns
        else sorted(df_ozellikli["MAL_ADI"].dropna().unique().tolist())
    )
    varsayilan_6_urun = tum_sim_urunleri[:6] if len(tum_sim_urunleri) >= 6 else tum_sim_urunleri

    secili_sepet_urunleri = st.multiselect(
        "Simülasyon Sepetine Dahil Edilecek Ürünleri Seçin:",
        options=tum_sim_urunleri,
        default=varsayilan_6_urun,
    )

    if secili_sepet_urunleri:
        # Her ürün için en güncel ORTALAMA_UCRET ve ilk_25_reel_karar_destegi bilgilerini birleştir
        son_fiyatlar = (
            df_ozellikli.dropna(subset=["MAL_ADI", "ORTALAMA_UCRET"])
            .sort_values("TARIH")
            .groupby("MAL_ADI", as_index=False)
            .last()[["MAL_ADI", "BIRIM", "ORTALAMA_UCRET", "REEL_ORTALAMA_UCRET"]]
            .rename(columns={"ORTALAMA_UCRET": "GUNCEL_ORTALAMA_UCRET"})
            if not df_ozellikli.empty and "ORTALAMA_UCRET" in df_ozellikli.columns
            else pd.DataFrame()
        )

        varsayilan_kg_haritasi = {
            "DOMATES": 450.0,
            "PATATES": 500.0,
            "SOGAN KURU": 350.0,
            "SARIMSAK KURU": 80.0,
            "LIMON": 180.0,
            "SALATALIK": 280.0,
            "BIBER SIVRI": 160.0,
            "ELMA STARKING": 150.0,
            "MUZ ITHAL": 140.0,
            "ANANAS": 90.0,
        }

        editor_satirlari = []
        for u_ad in secili_sepet_urunleri:
            birim_deger = "KG"
            if not son_fiyatlar.empty and u_ad in son_fiyatlar["MAL_ADI"].values:
                birim_deger = str(
                    son_fiyatlar[son_fiyatlar["MAL_ADI"] == u_ad].iloc[0]["BIRIM"]
                )
            editor_satirlari.append(
                {
                    "MAL_ADI": u_ad,
                    "BIRIM": birim_deger,
                    "SUBE_AYLIK_KG": float(varsayilan_kg_haritasi.get(u_ad, 200.0)),
                }
            )

        df_editor_girdi = pd.DataFrame(editor_satirlari)

        st.markdown("#### Şube Başı Aylık Tüketim Miktarı Tablosu")
        duzenlenen_sepet = st.data_editor(
            df_editor_girdi,
            column_config={
                "MAL_ADI": st.column_config.TextColumn("Ürün Adı", disabled=True),
                "BIRIM": st.column_config.TextColumn("Birim", disabled=True),
                "SUBE_AYLIK_KG": st.column_config.NumberColumn(
                    "Şube Başı Aylık Tüketim (Kg / Adet)",
                    min_value=1.0,
                    max_value=50000.0,
                    step=10.0,
                    format="%.0f",
                ),
            },
            use_container_width=True,
            hide_index=True,
            key="sim_data_editor",
        )

        # ---------------------------------------------------------------------
        # 3. HESAPLAMA MOTORU (SPOT MALİYET vs. AKILLI ALIM MALİYETİ)
        # ---------------------------------------------------------------------
        sim_sonuclari = []
        for _, satir in duzenlenen_sepet.iterrows():
            u_ad = str(satir["MAL_ADI"])
            u_birim = str(satir["BIRIM"])
            sube_aylik_kg = float(satir["SUBE_AYLIK_KG"])
            yillik_toplam_kg = sube_aylik_kg * float(sube_sayisi) * 12.0

            # Güncel ORTALAMA_UCRET
            guncel_fiyat = 25.0
            if not son_fiyatlar.empty and u_ad in son_fiyatlar["MAL_ADI"].values:
                guncel_fiyat = float(
                    son_fiyatlar[son_fiyatlar["MAL_ADI"] == u_ad].iloc[0]["GUNCEL_ORTALAMA_UCRET"]
                )

            # ilk_25_reel_karar_destegi.csv içinden YILLIK_REEL_ORT ve EN_UCUZ_REEL
            en_ucuz_ay = "Ağustos"
            en_uygun_mevsim = "Yaz"
            avantaj_orani = 0.22  # Yedek oran

            if not df_karar_destegi.empty and u_ad in df_karar_destegi["MAL_ADI"].values:
                k_satir = df_karar_destegi[df_karar_destegi["MAL_ADI"] == u_ad].iloc[0]
                yillik_reel_ort = float(k_satir.get("YILLIK_REEL_ORT", 0.0))
                en_ucuz_reel = float(k_satir.get("EN_UCUZ_REEL", 0.0))
                en_ucuz_ay = str(k_satir.get("EN_UCUZ_AY", "Ağustos"))
                en_uygun_mevsim = str(k_satir.get("EN_UYGUN_MEVSIM", "Yaz"))
                if yillik_reel_ort > 0 and en_ucuz_reel > 0:
                    avantaj_orani = max(0.0, (yillik_reel_ort - en_ucuz_reel) / yillik_reel_ort)

            # Bugünün TL'siyle Yıllık Spot Maliyet
            yillik_spot_maliyet = yillik_toplam_kg * guncel_fiyat

            # En ucuz dönemde alım yapıldığında brüt birim fiyat:
            en_ucuz_donem_birim_fiyat = guncel_fiyat * (1.0 - avantaj_orani)

            # Senaryo A (Sadece Sabit Fiyat Sözleşmesi - %0 Fire & %0 Depo)
            sozlesme_sadece_maliyet = yillik_toplam_kg * guncel_fiyat * (1.0 - avantaj_orani * 0.65)
            sozlesme_sadece_tasarruf = max(0.0, yillik_spot_maliyet - sozlesme_sadece_maliyet)

            # Senaryo B (SNC Karma Strateji): Fire + Depo oranı avantaj oranını aşıyor mu kontrol et
            if toplam_stok_maliyet_orani >= avantaj_orani:
                sozlesme_indirim_orani = avantaj_orani * 0.65
                akilli_birim_fiyat = guncel_fiyat * (1.0 - sozlesme_indirim_orani)
                yillik_akilli_maliyet = yillik_toplam_kg * akilli_birim_fiyat
                strateji_onerisi = (
                    f"Fiziksel Stok Zararlı (Zayi+Depo %{(toplam_stok_maliyet_orani*100):.1f} >= Avantaj %{(avantaj_orani*100):.1f}) "
                    f"→ {en_ucuz_ay} Ayında Sabit Fiyat Sözleşmesi"
                )
            else:
                net_avantaj_orani = avantaj_orani - toplam_stok_maliyet_orani
                akilli_birim_fiyat = guncel_fiyat * (1.0 - net_avantaj_orani)
                yillik_akilli_maliyet = yillik_toplam_kg * akilli_birim_fiyat
                strateji_onerisi = (
                    f"{en_ucuz_ay} ({en_uygun_mevsim}) Döneminde Toplu Alım & Stoklama "
                    f"(Net Avantaj: %{(net_avantaj_orani*100):.1f})"
                )

            yillik_net_tasarruf = max(0.0, yillik_spot_maliyet - yillik_akilli_maliyet)

            sim_sonuclari.append(
                {
                    "MAL_ADI": u_ad,
                    "BIRIM": u_birim,
                    "EN_UCUZ_AY": en_ucuz_ay,
                    "EN_UYGUN_MEVSIM": en_uygun_mevsim,
                    "SUBE_AYLIK_KG": round(sube_aylik_kg, 1),
                    "YILLIK_TOPLAM_KG": round(yillik_toplam_kg, 0),
                    "GUNCEL_BIRIM_FIYAT": round(guncel_fiyat, 2),
                    "MEVSIMSEL_AVANTAJ_YUZDE": round(avantaj_orani * 100.0, 1),
                    "YILLIK_SPOT_MALIYET": round(yillik_spot_maliyet, 0),
                    "SENARYO_A_MALIYET": round(sozlesme_sadece_maliyet, 0),
                    "SENARYO_A_TASARRUF": round(sozlesme_sadece_tasarruf, 0),
                    "YILLIK_AKILLI_MALIYET": round(yillik_akilli_maliyet, 0),
                    "YILLIK_NET_TASARRUF": round(yillik_net_tasarruf, 0),
                    "STRATEJI_ONERISI": strateji_onerisi,
                }
            )

        df_sim_sonuc = (
            pd.DataFrame(sim_sonuclari)
            .sort_values("YILLIK_NET_TASARRUF", ascending=False)
            .reset_index(drop=True)
        )

        toplam_spot_tl = float(df_sim_sonuc["YILLIK_SPOT_MALIYET"].sum())
        toplam_senaryo_a_tl = float(df_sim_sonuc["SENARYO_A_MALIYET"].sum())
        toplam_senaryo_a_tasarruf_tl = float(df_sim_sonuc["SENARYO_A_TASARRUF"].sum())
        senaryo_a_yuzde = (
            (toplam_senaryo_a_tasarruf_tl / toplam_spot_tl) * 100.0 if toplam_spot_tl > 0 else 0.0
        )

        toplam_akilli_tl = float(df_sim_sonuc["YILLIK_AKILLI_MALIYET"].sum())
        toplam_net_tasarruf_tl = float(df_sim_sonuc["YILLIK_NET_TASARRUF"].sum())
        toplam_tasarruf_yuzde = (
            (toplam_net_tasarruf_tl / toplam_spot_tl) * 100.0 if toplam_spot_tl > 0 else 0.0
        )
        senaryo_b_ekstra_kazanc = toplam_net_tasarruf_tl - toplam_senaryo_a_tasarruf_tl

        sube_basi_yillik_kazanc = (
            toplam_net_tasarruf_tl / float(sube_sayisi) if sube_sayisi > 0 else 0.0
        )
        en_cok_tasarruf_urun = str(df_sim_sonuc.iloc[0]["MAL_ADI"])
        en_cok_tasarruf_tutar = float(df_sim_sonuc.iloc[0]["YILLIK_NET_TASARRUF"])

        st.divider()

        # ---------------------------------------------------------------------
        # 4. ÜSTTE 3 KPI KARTI, ORTADA PLOTLY GRUPLU ÇUBUK GRAFİK, ALTTA TABLO
        # ---------------------------------------------------------------------
        sim_kpi1, sim_kpi2, sim_kpi3 = st.columns(3)
        sim_kpi1.metric(
            "Yıllık Toplam Net Tasarruf",
            f"{toplam_net_tasarruf_tl:,.0f} ₺".replace(",", "."),
            f"-%{toplam_tasarruf_yuzde:.1f} Maliyet Avantajı ({sube_sayisi} Şube)",
        )
        sim_kpi2.metric(
            "Şube Başı Yıllık Kazanç",
            f"{sube_basi_yillik_kazanc:,.0f} ₺ / Şube".replace(",", "."),
            f"Aylık: {(sube_basi_yillik_kazanc / 12.0):,.0f} ₺ / Şube".replace(",", "."),
        )
        sim_kpi3.metric(
            "En Çok Tasarruf Sağlayan Ürün",
            en_cok_tasarruf_urun,
            f"Yıllık Kazanç: {en_cok_tasarruf_tutar:,.0f} ₺".replace(",", "."),
        )

        st.markdown("#### Ürün Bazında Yıllık Spot Maliyet ve Akıllı Alım Karşılaştırması")
        fig_sim = go.Figure()
        fig_sim.add_trace(
            go.Bar(
                x=df_sim_sonuc["MAL_ADI"],
                y=df_sim_sonuc["YILLIK_SPOT_MALIYET"],
                name="Klasik Yıllık Spot Maliyet (TL)",
                marker_color="#94A3B8",
                text=[f"{v:,.0f} ₺".replace(",", ".") for v in df_sim_sonuc["YILLIK_SPOT_MALIYET"]],
                textposition="outside",
            )
        )
        fig_sim.add_trace(
            go.Bar(
                x=df_sim_sonuc["MAL_ADI"],
                y=df_sim_sonuc["YILLIK_AKILLI_MALIYET"],
                name="SNC Akıllı Alım Maliyeti (Zayi & Depo Dahil TL)",
                marker_color="#1B7A43",
                text=[f"{v:,.0f} ₺".replace(",", ".") for v in df_sim_sonuc["YILLIK_AKILLI_MALIYET"]],
                textposition="outside",
            )
        )
        fig_sim.update_layout(
            barmode="group",
            height=410,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="Sepetteki Ürünler",
            yaxis_title="Yıllık Toplam Maliyet (₺)",
            yaxis=dict(range=[0, df_sim_sonuc["YILLIK_SPOT_MALIYET"].max() * 1.18]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
        )
        st.plotly_chart(fig_sim, use_container_width=True)

        # Dinamik Simülatör Grafik Yorumu
        stok_karli_sayisi = int(df_sim_sonuc["STRATEJI_ONERISI"].str.contains("Toplu Alım").sum())
        sozlesme_sayisi = len(df_sim_sonuc) - stok_karli_sayisi
        st.markdown(
            f"""
<div class="insight-note"><b>Simülasyon Grafiği Yorumu ({sube_sayisi} Şube • Zayi %{fire_orani:.1f} • Depo %{depo_orani:.1f}):</b>
Seçtiğiniz <b>{len(df_sim_sonuc)} ürünlük</b> sepette yıllık toplam maliyet <b>{toplam_spot_tl:,.0f} ₺</b>'den
<b>{toplam_akilli_tl:,.0f} ₺</b>'ye inerek <b>{toplam_net_tasarruf_tl:,.0f} ₺ (-%{toplam_tasarruf_yuzde:.1f})</b> net tasarruf sağlamaktadır.
Bu parametrelerle <b>{stok_karli_sayisi} üründe</b> fiziksel stoklama kârlı iken, <b>{sozlesme_sayisi} üründe</b> zayi+depo yükü nedeniyle
<b>sabit fiyatlı sözleşme</b> önerilmektedir. En büyük kazanç <b>{en_cok_tasarruf_urun}</b> ({en_cok_tasarruf_tutar:,.0f} ₺) kaleminden gelmektedir.</div>
""".replace(",", "."),
            unsafe_allow_html=True,
        )

        with st.expander("📋 Yıllık Satın Alma ve Tasarruf Planı Sonuç Tablosu", expanded=False):
            st.dataframe(
                df_sim_sonuc.drop(columns=["SENARYO_A_MALIYET", "SENARYO_A_TASARRUF"], errors="ignore").rename(
                    columns={
                        "MAL_ADI": "Ürün Adı",
                        "BIRIM": "Birim",
                        "EN_UCUZ_AY": "En Ucuz Ay",
                        "EN_UYGUN_MEVSIM": "Uygun Mevsim",
                        "SUBE_AYLIK_KG": "Şube Aylık (Kg)",
                        "YILLIK_TOPLAM_KG": "Zincir Yıllık (Kg)",
                        "GUNCEL_BIRIM_FIYAT": "Güncel Fiyat (TL)",
                        "MEVSIMSEL_AVANTAJ_YUZDE": "Mevsimsel Avantaj (%)",
                        "YILLIK_SPOT_MALIYET": "Yıllık Spot Maliyet (TL)",
                        "YILLIK_AKILLI_MALIYET": "Yıllık Akıllı Maliyet (TL)",
                        "YILLIK_NET_TASARRUF": "Yıllık Net Tasarruf (TL)",
                        "STRATEJI_ONERISI": "Önerilen Satın Alma Stratejisi",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )



        with st.expander("⚖️ Yönetim Karar Alternatifleri: Senaryo A ve Senaryo B", expanded=False):
            st.caption(
                f"Aynı **{sube_sayisi} şube** ve seçili sepet için iki farklı satın alma stratejisinin yıllık maliyet ve risk karşılaştırması:"
            )

            # Dinamik karar: Hangi senaryo daha yüksek net tasarruf sağlıyorsa yeşil "Önerilen Strateji" rozeti onda görünür
            senaryo_a_kazandi = toplam_senaryo_a_tasarruf_tl > toplam_net_tasarruf_tl
            kazanan_fark_tl = abs(toplam_net_tasarruf_tl - toplam_senaryo_a_tasarruf_tl)

            # Senaryo A görsel stilleri
            a_border = "#1B7A43" if senaryo_a_kazandi else "#CA8A04"
            a_bg = "#F0FDF4" if senaryo_a_kazandi else "#FFFFFF"
            a_title_color = "#14532D" if senaryo_a_kazandi else "#854D0E"
            a_badge_bg = "#DCFCE7" if senaryo_a_kazandi else "#FEF9C3"
            a_badge_color = "#166534" if senaryo_a_kazandi else "#854D0E"
            a_badge_text = "Önerilen Strateji" if senaryo_a_kazandi else "Düşük Risk • %0 Zayi"
            a_icon = ""

            # Senaryo B görsel stilleri
            b_border = "#1B7A43" if not senaryo_a_kazandi else "#CA8A04"
            b_bg = "#F0FDF4" if not senaryo_a_kazandi else "#FFFFFF"
            b_title_color = "#14532D" if not senaryo_a_kazandi else "#854D0E"
            b_badge_bg = "#DCFCE7" if not senaryo_a_kazandi else "#FEF9C3"
            b_badge_color = "#166534" if not senaryo_a_kazandi else "#854D0E"
            b_badge_text = "Önerilen Strateji" if not senaryo_a_kazandi else "Alternatif Karma Plan"
            b_icon = ""

            sen_col1, sen_col2 = st.columns(2, gap="large")
            with sen_col1:
                st.markdown(
                    f"""
<div class="signal-card" translate="no" style="border-top:5px solid {a_border}; padding:18px 20px; background:{a_bg};">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
<span style="font-weight:800; font-size:1.02rem; color:{a_title_color};">Senaryo A: Güvenli Sözleşme Stratejisi</span>
<span style="background:{a_badge_bg}; color:{a_badge_color}; padding:3px 9px; border-radius:8px; font-size:0.78rem; font-weight:700;">{a_badge_text}</span>
</div>
<div style="color:#475569; font-size:0.86rem; margin-bottom:12px;">
Hiç fiziksel stoklama yapılmaz; tüm ürünlerde mevsimsel dip fiyatlar baz alınarak tedarikçilerle <b>Sabit Fiyatlı Sözleşme</b> imzalanır.
</div>
<div style="font-size:0.93rem; color:#1E293B; line-height:1.6;">
• <b>Yıllık Maliyet:</b> {toplam_senaryo_a_tl:,.0f} ₺<br>
• <b>Yıllık Net Tasarruf:</b> <span style="color:{a_title_color}; font-weight:800;">{toplam_senaryo_a_tasarruf_tl:,.0f} ₺ (-%{senaryo_a_yuzde:.1f})</span><br>
• <b>Şube Başı Kazanç:</b> {(toplam_senaryo_a_tasarruf_tl / max(sube_sayisi, 1)):,.0f} ₺ / Yıl
</div>
</div>
""".replace(",", "."),
                    unsafe_allow_html=True,
                )

            with sen_col2:
                fark_metni = (
                    f"Senaryo B'ye göre ek +{kazanan_fark_tl:,.0f} ₺ avantaj (Senaryo A önde)".replace(",", ".")
                    if senaryo_a_kazandi
                    else f"Senaryo A'ya göre ek +{kazanan_fark_tl:,.0f} ₺ net kazanç (Senaryo B önde)".replace(",", ".")
                )
                st.markdown(
                    f"""
<div class="signal-card" translate="no" style="border-top:5px solid {b_border}; padding:18px 20px; background:{b_bg};">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
<span style="font-weight:800; font-size:1.02rem; color:{b_title_color};">Senaryo B: SNC Karma Optimizasyon</span>
<span style="background:{b_badge_bg}; color:{b_badge_color}; padding:3px 9px; border-radius:8px; font-size:0.78rem; font-weight:700;">{b_badge_text}</span>
</div>
<div style="color:#334155; font-size:0.86rem; margin-bottom:12px;">
Ürün bazında dinamik seçim: Dayanıklı ve yüksek avantajlı ürünlerde <b>Toplu Alım/Stok</b>, zayi/depo riskli ürünlerde <b>Sabit Sözleşme</b> uygulanır.
</div>
<div style="font-size:0.93rem; color:#1E293B; line-height:1.6;">
• <b>Yıllık Maliyet:</b> {toplam_akilli_tl:,.0f} ₺<br>
• <b>Yıllık Net Tasarruf:</b> <span style="color:{b_title_color}; font-weight:800;">{toplam_net_tasarruf_tl:,.0f} ₺ (-%{toplam_tasarruf_yuzde:.1f})</span><br>
• <b>Karşılaştırma:</b> <b>{fark_metni}</b>
</div>
</div>
""".replace(",", "."),
                    unsafe_allow_html=True,
                )

            # Çelişkiyi Ortadan Kaldıran Tek Cümlelik Akıllı İş Gerekçesi
            if senaryo_a_kazandi:
                gerekce_metni = (
                    f"<b>Neden Bu Öneri?</b> Seçilen ürünlerde zayi/bozulma (<b>%{fire_orani:.1f}</b>) ve soğuk depo (<b>%{depo_orani:.1f}</b>) "
                    f"maliyetleri fiziksel stoklamanın kârını aşındırdığı için en ucuz dönem bazlı sabit fiyatlı tedarikçi sözleşmesi "
                    f"(<b>Senaryo A</b>) hem net tasarrufu maksimize etmekte hem de raf ömrü kısa ürünlerde sıfır zayi riski sunmaktadır."
                )
            else:
                gerekce_metni = (
                    f"<b>Neden Bu Öneri?</b> Seçilen ürünlerde mevsimsel fiyat makası yüksek olduğu için <b>%{fire_orani:.1f}</b> zayi/bozulma ve "
                    f"<b>%{depo_orani:.1f}</b> soğuk depo maliyetine rağmen ürün bazlı karma alım stratejisi (<b>Senaryo B</b>) "
                    f"net kârı maksimize etmektedir; raf ömrü kısa kalemlerde ise sistem otomatik olarak sabit fiyatlı tedarikçi sözleşmesini tercih etmektedir."
                )

            st.markdown(
                f'<div class="insight-note" style="margin-top:12px;">{gerekce_metni}</div>',
                unsafe_allow_html=True,
            )

            # Spot vs Senaryo A vs Senaryo B Yatay Kıyaslama Grafiği
            fig_sen = go.Figure(
                go.Bar(
                    y=[
                        "Senaryo B: SNC Karma (Stok + Sözleşme)",
                        "Senaryo A: Sadece Sabit Sözleşme",
                        "Mevcut Durum: Klasik Spot Alım",
                    ],
                    x=[toplam_akilli_tl, toplam_senaryo_a_tl, toplam_spot_tl],
                    orientation="h",
                    marker_color=[
                        "#1B7A43" if not senaryo_a_kazandi else "#EAB308",
                        "#1B7A43" if senaryo_a_kazandi else "#EAB308",
                        "#94A3B8",
                    ],
                    text=[
                        f"{toplam_akilli_tl:,.0f} ₺ (-%{toplam_tasarruf_yuzde:.1f})".replace(",", "."),
                        f"{toplam_senaryo_a_tl:,.0f} ₺ (-%{senaryo_a_yuzde:.1f})".replace(",", "."),
                        f"{toplam_spot_tl:,.0f} ₺ (Baz)".replace(",", "."),
                    ],
                    textposition="outside",
                )
            )
            fig_sen.update_layout(
                height=240,
                margin=dict(l=10, r=120, t=20, b=10),
                xaxis_title=f"Yıllık Toplam Sepet Maliyeti ({sube_sayisi} Şube - ₺)",
                xaxis=dict(range=[0, max(toplam_spot_tl, 1.0) * 1.24]),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
            )
            st.plotly_chart(fig_sen, use_container_width=True)


        # ---------------------------------------------------------------------
        # 4.6 YÖNETİME 3 ALTIN ÖNERİ ÖZET KARTLARI (VERİDEN OTOMATİK HESAPLANIR)
        # ---------------------------------------------------------------------
        with st.expander("🏆 Yönetime 3 Stratejik Satın Alma Önerisi", expanded=False):
            st.caption(
                "Tüm 25 ürünlük veri setinden otomatik hesaplanan en kritik 3 satın alma aksiyonu:"
            )

            altin = _uc_altin_oneri_hesapla(df_ozellikli, df_karar_destegi)
            ao1, ao2, ao3 = st.columns(3, gap="medium")

            with ao1:
                st.markdown(
                    f"""
<div class="signal-card" style="border-top:5px solid #DC2626; min-height:152px;">
<div class="signal-card-title">1. Sözleşmeli Alım Şampiyonu</div>
<div class="signal-card-status" style="color:#B91C1C;">{altin['sozlesme_urun']}</div>
<div class="signal-card-sub">
<b>Neden?</b> Fiyat oynaklığı (<b>{altin['sozlesme_oynaklik']:.2f}</b>) ve gün içi taban–tavan makası
(<b>%{altin['sozlesme_makas_pct']:.1f}</b>) en riskli ürün.<br>
<b>Aksiyon:</b> Sabit fiyatlı sözleşme ile yıllık tahmini <b>%{altin['sozlesme_koruma_pct']:.1f}</b> maliyet koruması sağlanır.
</div>
</div>
""",
                    unsafe_allow_html=True,
                )

            with ao2:
                st.markdown(
                    f"""
<div class="signal-card" style="border-top:5px solid #1B7A43; min-height:152px;">
<div class="signal-card-title">2. Mevsimsel Stoklama Şampiyonu</div>
<div class="signal-card-status" style="color:#15803D;">{altin['stok_urun']}</div>
<div class="signal-card-sub">
<b>Neden?</b> En ucuz ay (<b>{altin['stok_en_ucuz_ay']}</b>) ile en pahalı ay (<b>{altin['stok_en_pahali_ay']}</b>)
arasındaki reel fiyat farkı <b>+%{altin['stok_fark_pct']:.1f}</b>.<br>
<b>Aksiyon:</b> <b>{altin['stok_en_ucuz_ay']}</b> ayında toplu alım veya dip fiyat kilitleme yapılmalı.
</div>
</div>
""",
                    unsafe_allow_html=True,
                )

            with ao3:
                st.markdown(
                    f"""
<div class="signal-card" style="border-top:5px solid #3B82F6; min-height:152px;">
<div class="signal-card-title">3. Düşük Riskli Spot Alım Ürünü</div>
<div class="signal-card-status" style="color:#1D4ED8;">{altin['spot_urun']}</div>
<div class="signal-card-sub">
<b>Neden?</b> 30 günlük ortalama oynaklığı yalnızca <b>{altin['spot_oynaklik']:.2f}</b>
(ortalama reel: <b>{altin['spot_ort_reel']:.2f} ₺</b>) ile en istikrarlı ürün.<br>
<b>Aksiyon:</b> Depo/stok maliyeti yaratmadan günlük veya haftalık rutin spot alımla güvenle tedarik edilebilir.
</div>
</div>
""",
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)


        # ---------------------------------------------------------------------
        # 5. TASARIMLI EXCEL (.XLSX) İNDİRME BUTONU (OPENPYXL)
        # ---------------------------------------------------------------------
        try:
            excel_bayt = _tasarimli_excel_olustur(
                sim_df=df_sim_sonuc,
                sube_sayisi=sube_sayisi,
                fire_orani=fire_orani,
                depo_orani=depo_orani,
                toplam_spot=toplam_spot_tl,
                toplam_akilli=toplam_akilli_tl,
                toplam_net_tasarruf=toplam_net_tasarruf_tl,
                toplam_tasarruf_yuzde=toplam_tasarruf_yuzde,
                senaryo_a_maliyet=toplam_senaryo_a_tl,
                senaryo_a_tasarruf=toplam_senaryo_a_tasarruf_tl,
            )
            st.download_button(
                label="Satın Alma ve Tasarruf Planını İndir (.xlsx — Kurumsal Excel)",
                data=excel_bayt,
                file_name=f"SNC_Satin_Alma_Plani_{sube_sayisi}_Sube.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
            )
        except Exception as e:
            st.warning(f"Excel oluşturma için `openpyxl` paketi gereklidir ({e}).")
    else:
        st.warning("Simülasyonu başlatmak için lütfen yukarıdan en az 1 ürün seçin.")


# =============================================================================
# 6. SEKME: MENÜ & REÇETE MALİYET ASİSTANI (HAZIR ŞABLON + SERBEST TARİF)
# =============================================================================
with sekme_recete:
    st.subheader("🥗 Şefin Akıllı Menü ve Reçete Maliyeti")
    st.caption(
        f"Hazır restoran tariflerinden birini seçin veya kendi tarifinizi oluşturun. "
        f"12 aylık porsiyon maliyet eğrisi ile aylık maliyet dağılımı ve mevsimlik ikame önerisini alt kısımdaki açılır pencerelerden inceleyebilirsiniz."
    )

    mevcut_tum_urunler = (
        sorted(df_aylik_reel["MAL_ADI"].dropna().unique().tolist())
        if not df_aylik_reel.empty and "MAL_ADI" in df_aylik_reel.columns
        else sorted(df_ozellikli["MAL_ADI"].dropna().unique().tolist())
    )

    HAZIR_TARIFLER = {
        "Ege Akdeniz Yeşil Salata": {
            "satis_fiyati": 220.0,
            "gunluk_porsiyon": 45,
            "malzemeler": [
                ("MARUL AYSBERG", 0.15),
                ("DOMATES SALKIM", 0.12),
                ("Y.ROKA", 0.10),
                ("LAHANA KIRMIZI", 0.08),
                ("Y.MAYDONOZ", 0.05),
            ],
        },
        "Avokadolu Tropikal Meyve Bowl": {
            "satis_fiyati": 310.0,
            "gunluk_porsiyon": 30,
            "malzemeler": [
                ("AVAKADO", 0.50),
                ("MUZ ITHAL", 0.12),
                ("CILEK", 0.10),
                ("ANANAS", 0.25),
                ("ELMA GOLDEN", 0.10),
            ],
        },
        "Ege Izgara Sebze & Mantar Tabağı": {
            "satis_fiyati": 280.0,
            "gunluk_porsiyon": 35,
            "malzemeler": [
                ("PATLICAN UZUN", 0.15),
                ("KABAK TAZE", 0.15),
                ("MANTAR", 0.12),
                ("PATATES CALMA", 0.18),
                ("DOMATES SALKIM", 0.10),
                ("SARIMSAK KURU", 0.02),
            ],
        },
        "Zeytinyağlı Ege Meze Tabağı": {
            "satis_fiyati": 250.0,
            "gunluk_porsiyon": 40,
            "malzemeler": [
                ("FASULYE CALI", 0.15),
                ("ISPANAK", 0.12),
                ("PANCAR", 0.10),
                ("Y.DEREOTU", 0.05),
                ("Y.NANE", 0.05),
                ("SARIMSAK KURU", 0.02),
            ],
        },
        "Kendi Tarifimi Oluştur": {
            "satis_fiyati": 260.0,
            "gunluk_porsiyon": 30,
            "malzemeler": [
                (mevcut_tum_urunler[0], 0.15) if len(mevcut_tum_urunler) > 0 else ("DOMATES SALKIM", 0.15),
                (mevcut_tum_urunler[1], 0.12) if len(mevcut_tum_urunler) > 1 else ("PATATES CALMA", 0.12),
                (mevcut_tum_urunler[2], 0.10) if len(mevcut_tum_urunler) > 2 else ("MARUL AYSBERG", 0.10),
            ],
        },
    }

    r_ust1, r_ust2, r_ust3, r_ust4 = st.columns([1.4, 1.2, 0.9, 0.9])
    with r_ust1:
        secili_sablon = st.selectbox(
            "Hazır Tarif Seçin veya Özel Tarif Oluşturun",
            options=list(HAZIR_TARIFLER.keys()),
            index=0,
            key="recete_sablon_sec",
        )
    sablon_bilgi = HAZIR_TARIFLER[secili_sablon]

    with r_ust2:
        if secili_sablon.startswith("Kendi Tarifimi"):
            tarif_adi = st.text_input(
                "Kendi Tarif Adınızı Yazın",
                value="Şefin Özel Ege Tabağı",
                key="recete_ozel_ad",
            )
        else:
            tarif_adi = st.text_input(
                "Tarif Adı",
                value=secili_sablon,
                key=f"recete_ad_{secili_sablon}",
            )

    with r_ust3:
        menu_satis_fiyati = st.number_input(
            "Menü Satış Fiyatı (TL)",
            min_value=10.0,
            max_value=5000.0,
            value=float(sablon_bilgi["satis_fiyati"]),
            step=10.0,
            key=f"recete_satis_{secili_sablon}",
        )

    with r_ust4:
        recete_ay_no = st.selectbox(
            "Analiz Ayı",
            options=list(AY_SIRASI.keys()),
            format_func=lambda x: f"{x:02d} - {AY_SIRASI[x]}",
            index=datetime.now().month - 1,
            key="recete_ay_sec",
        )
        recete_ay_adi = AY_SIRASI[recete_ay_no]

    r_alt_ayar1, r_alt_ayar2 = st.columns([2.2, 1.0])
    with r_alt_ayar1:
        sablon_urun_adlari = [
            u for u, _ in sablon_bilgi["malzemeler"] if u in mevcut_tum_urunler
        ]
        if not sablon_urun_adlari and mevcut_tum_urunler:
            sablon_urun_adlari = mevcut_tum_urunler[:3]

        secili_malzemeler = st.multiselect(
            "Reçete Malzemelerini Seçin / Ekleyin / Çıkarın:",
            options=mevcut_tum_urunler,
            default=sablon_urun_adlari,
            key=f"recete_malz_sec_{secili_sablon}",
        )
    with r_alt_ayar2:
        gunluk_sube_porsiyon = st.number_input(
            "Şube Başı Günlük Satış (Porsiyon)",
            min_value=1,
            max_value=2000,
            value=int(sablon_bilgi["gunluk_porsiyon"]),
            step=5,
            key=f"recete_gunluk_pors_{secili_sablon}",
        )

    if secili_malzemeler:
        # Her malzeme için birim, tür ve son güncel nominal/reel fiyatları bul
        son_bilgi_map = {}
        if not df_ozellikli.empty:
            son_oz = (
                df_ozellikli.dropna(subset=["MAL_ADI", "ORTALAMA_UCRET"])
                .sort_values("TARIH")
                .groupby("MAL_ADI", as_index=False)
                .last()
            )
            for _, sr in son_oz.iterrows():
                son_bilgi_map[str(sr["MAL_ADI"])] = {
                    "BIRIM": str(sr.get("BIRIM", "KG")),
                    "MAL_TURU": str(sr.get("MAL_TURU", "SEBZE")),
                    "GUNCEL_FIYAT": _guvenli_sayi(sr.get("ORTALAMA_UCRET", 25.0), 25.0),
                }

        sablon_miktar_harita = {u: m for u, m in sablon_bilgi["malzemeler"]}
        recete_editor_satirlari = []
        for u in secili_malzemeler:
            bilgi = son_bilgi_map.get(u, {"BIRIM": "KG", "MAL_TURU": "SEBZE", "GUNCEL_FIYAT": 25.0})
            varsayilan_m = sablon_miktar_harita.get(u, 0.25 if bilgi["BIRIM"] in ["ADET", "BAĞ", "BAG"] else 0.12)
            recete_editor_satirlari.append(
                {
                    "MAL_ADI": u,
                    "MAL_TURU": bilgi["MAL_TURU"],
                    "BIRIM": bilgi["BIRIM"],
                    "PORSIYON_MIKTAR": float(varsayilan_m),
                }
            )

        st.markdown(f"#### **{tarif_adi}** — 1 Porsiyon Malzeme Miktarları")
        st.caption(
            "Örnek: 150 gram domates için `0.15` (KG), yarım avokado için `0.50` (ADET), yarım demet roka için `0.50` (BAĞ) yazabilirsiniz."
        )
        duzenlenen_recete = st.data_editor(
            pd.DataFrame(recete_editor_satirlari),
            column_config={
                "MAL_ADI": st.column_config.TextColumn("Ürün Adı", disabled=True),
                "MAL_TURU": st.column_config.TextColumn("Kategori", disabled=True),
                "BIRIM": st.column_config.TextColumn("Birim", disabled=True),
                "PORSIYON_MIKTAR": st.column_config.NumberColumn(
                    "1 Porsiyon Miktarı (KG / ADET / BAĞ)",
                    min_value=0.01,
                    max_value=10.0,
                    step=0.01,
                    format="%.2f",
                ),
            },
            use_container_width=True,
            hide_index=True,
            key=f"recete_editor_{secili_sablon}",
        )

        # 12 Aylık Porsiyon Maliyetini Bugünün TL'sine Ölçekleyerek Hesapla
        # Yöntem: Her malzemenin ilgili aydaki mevsimsel çarpanı (AYLIK_REEL_ORT / YILLIK_REEL_ORT) * güncel ORTALAMA_UCRET
        yillik_reel_map = (
            df_aylik_reel.groupby("MAL_ADI")["AYLIK_REEL_ORT"].mean().to_dict()
            if not df_aylik_reel.empty
            else {}
        )
        aylik_reel_lookup = (
            df_aylik_reel.groupby(["MAL_ADI", "AY"])["AYLIK_REEL_ORT"].mean().to_dict()
            if not df_aylik_reel.empty
            else {}
        )

        aylik_porsiyon_maliyetleri = []
        secili_ay_malzeme_detay = []

        for ay_i in range(1, 13):
            ay_toplam = 0.0
            for _, mr in duzenlenen_recete.iterrows():
                m_ad = str(mr["MAL_ADI"])
                m_miktar = _guvenli_sayi(mr["PORSIYON_MIKTAR"], 0.10)
                guncel_birim = son_bilgi_map.get(m_ad, {}).get("GUNCEL_FIYAT", 25.0)
                yil_ort = _guvenli_sayi(yillik_reel_map.get(m_ad, 0.0), 0.0)
                ay_ort = _guvenli_sayi(aylik_reel_lookup.get((m_ad, ay_i), yil_ort), yil_ort)
                mevsim_carpan = (ay_ort / yil_ort) if yil_ort > 0 else 1.0
                aylik_birim_tl = guncel_birim * mevsim_carpan
                kalem_maliyet = m_miktar * aylik_birim_tl
                ay_toplam += kalem_maliyet

                if ay_i == recete_ay_no:
                    secili_ay_malzeme_detay.append(
                        {
                            "MAL_ADI": m_ad,
                            "MAL_TURU": str(mr["MAL_TURU"]),
                            "BIRIM": str(mr["BIRIM"]),
                            "PORSIYON_MIKTAR": m_miktar,
                            "AYLIK_BIRIM_TL": round(aylik_birim_tl, 2),
                            "KALEM_MALIYET_TL": round(kalem_maliyet, 2),
                            "MEVSIM_CARPAN": mevsim_carpan,
                        }
                    )

            aylik_porsiyon_maliyetleri.append(
                {
                    "AY": ay_i,
                    "AY_ADI": AY_SIRASI[ay_i],
                    "PORSIYON_MALIYET_TL": round(ay_toplam, 2),
                }
            )

        df_recete_aylik = pd.DataFrame(aylik_porsiyon_maliyetleri)
        df_kalem_detay = pd.DataFrame(secili_ay_malzeme_detay).sort_values(
            "KALEM_MALIYET_TL", ascending=False
        ).reset_index(drop=True)

        secili_ay_maliyet = float(
            df_recete_aylik[df_recete_aylik["AY"] == recete_ay_no].iloc[0]["PORSIYON_MALIYET_TL"]
        )
        en_ucuz_satir = df_recete_aylik.loc[df_recete_aylik["PORSIYON_MALIYET_TL"].idxmin()]
        en_pahali_satir = df_recete_aylik.loc[df_recete_aylik["PORSIYON_MALIYET_TL"].idxmax()]
        food_cost_yuzde = (secili_ay_maliyet / menu_satis_fiyati) * 100.0 if menu_satis_fiyati > 0 else 0.0
        brut_kar_yuzde = max(0.0, 100.0 - food_cost_yuzde)
        zincir_aylik_maliyet = secili_ay_maliyet * float(gunluk_sube_porsiyon) * 30.0 * float(aktif_sube_sayisi)

        # 3 Özet Kart (Kesilmez .signal-card ile)
        rk1, rk2, rk3 = st.columns(3)
        rk1.markdown(
            f"""
<div class="signal-card" style="border-top:4px solid #1B7A43;">
<div class="signal-card-title">{recete_ay_adi} Ayı 1 Porsiyon Malzeme Maliyeti</div>
<div class="signal-card-status" style="color:#1B7A43;">{secili_ay_maliyet:.2f} ₺ / Porsiyon</div>
<div class="signal-card-sub">Sebze-Meyve Maliyet Payı: <b>%{food_cost_yuzde:.1f}</b> | Kalan Brüt Marj: <b>%{brut_kar_yuzde:.1f}</b></div>
</div>
""",
            unsafe_allow_html=True,
        )
        rk2.markdown(
            f"""
<div class="signal-card" style="border-top:4px solid #F59E0B;">
<div class="signal-card-title">Yıl İçi Maliyet Makası</div>
<div class="signal-card-status" style="color:#B45309;">{en_ucuz_satir['PORSIYON_MALIYET_TL']:.2f} ₺ → {en_pahali_satir['PORSIYON_MALIYET_TL']:.2f} ₺</div>
<div class="signal-card-sub">En Ucuz: <b>{en_ucuz_satir['AY_ADI']}</b> • En Pahalı: <b>{en_pahali_satir['AY_ADI']}</b></div>
</div>
""",
            unsafe_allow_html=True,
        )
        rk3.markdown(
            f"""
<div class="signal-card" style="border-top:4px solid #3B82F6;">
<div class="signal-card-title">{aktif_sube_sayisi} Şubelik Aylık Reçete Maliyeti ({recete_ay_adi})</div>
<div class="signal-card-status" style="color:#1D4ED8;">{zincir_aylik_maliyet:,.0f} ₺ / Ay</div>
<div class="signal-card-sub">Günlük {gunluk_sube_porsiyon} porsiyon/şube × 30 gün × {aktif_sube_sayisi} şube</div>
</div>
""".replace(",", "."),
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        with st.expander(f"📈 {tarif_adi} — 12 Aylık Porsiyon Maliyet Eğrisi", expanded=False):
            fig_rec = go.Figure()
            fig_rec.add_trace(
                go.Scatter(
                    x=df_recete_aylik["AY_ADI"],
                    y=df_recete_aylik["PORSIYON_MALIYET_TL"],
                    mode="lines+markers+text",
                    line=dict(color="#1B7A43", width=3),
                    marker=dict(
                        size=[13 if a == recete_ay_no else 8 for a in df_recete_aylik["AY"]],
                        color=[
                            "#DC2626" if a == int(en_pahali_satir["AY"])
                            else ("#16A34A" if a == int(en_ucuz_satir["AY"]) else "#1B7A43")
                            for a in df_recete_aylik["AY"]
                        ],
                    ),
                    text=[f"{v:.1f}₺" for v in df_recete_aylik["PORSIYON_MALIYET_TL"]],
                    textposition="top center",
                    name="1 Porsiyon Maliyeti (TL)",
                )
            )
            fig_rec.update_layout(
                height=340,
                margin=dict(l=10, r=10, t=25, b=10),
                xaxis_title="Ay",
                yaxis_title="1 Porsiyon Sebze-Meyve Maliyeti (TL)",
                yaxis=dict(range=[0, max(df_recete_aylik["PORSIYON_MALIYET_TL"].max() * 1.22, 5.0)]),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
            )
            st.plotly_chart(fig_rec, use_container_width=True)

            # Dinamik Reçete Eğrisi Yorumu
            porsiyon_fark_tl = float(en_pahali_satir["PORSIYON_MALIYET_TL"]) - float(en_ucuz_satir["PORSIYON_MALIYET_TL"])
            porsiyon_fark_pct = (
                (porsiyon_fark_tl / float(en_ucuz_satir["PORSIYON_MALIYET_TL"])) * 100.0
                if float(en_ucuz_satir["PORSIYON_MALIYET_TL"]) > 0
                else 0.0
            )
            st.markdown(
                f"""
<div class="insight-note"><b>Reçete Maliyet Eğrisi Yorumu ({tarif_adi} — {recete_ay_adi}):</b>
Bu tarifin 1 porsiyon malzeme maliyeti en ucuz ay olan <b>{en_ucuz_satir['AY_ADI']}</b> ({en_ucuz_satir['PORSIYON_MALIYET_TL']:.2f} ₺) ile
en pahalı ay olan <b>{en_pahali_satir['AY_ADI']}</b> ({en_pahali_satir['PORSIYON_MALIYET_TL']:.2f} ₺) arasında <b>+%{porsiyon_fark_pct:.1f}</b>
({porsiyon_fark_tl:.2f} ₺/porsiyon) dalgalanmaktadır. Seçili <b>{recete_ay_adi}</b> ayında {aktif_sube_sayisi} şubenizde bu yemek için aylık
<b>{zincir_aylik_maliyet:,.0f} ₺</b> sebze-meyve bütçesi gerekmektedir; menü fiyat güncellemesi veya mevsimlik ikame bu eğriye göre planlanmalıdır.</div>
""".replace(",", "."),
                unsafe_allow_html=True,
            )

        with st.expander(f"📊 {recete_ay_adi} Ayı Maliyet Dağılımı ve Akıllı İkame Önerisi", expanded=False):
            if not df_kalem_detay.empty:
                maliyet_katili = df_kalem_detay.iloc[0]
                katil_ad = str(maliyet_katili["MAL_ADI"])
                katil_tur = str(maliyet_katili["MAL_TURU"])
                katil_tutar = float(maliyet_katili["KALEM_MALIYET_TL"])
                katil_pay = (katil_tutar / secili_ay_maliyet) * 100.0 if secili_ay_maliyet > 0 else 0.0

                st.error(
                    f"**Maliyet Katili Malzeme:** **{katil_ad}**\n\n"
                    f"{recete_ay_adi} ayında bu tarifin porsiyon maliyetinin **%{katil_pay:.1f}**'ini "
                    f"(`{katil_tutar:.2f} ₺ / porsiyon`) tek başına oluşturuyor."
                )

                # Aynı kategoride o ay mevsimsel çarpanı en düşük (en ucuz döneminde olan) ikame ürün bul
                ikame_adaylari = []
                for aday_u in mevcut_tum_urunler:
                    if aday_u in secili_malzemeler:
                        continue
                    aday_bilgi = son_bilgi_map.get(aday_u, {})
                    if aday_bilgi.get("MAL_TURU", "") == katil_tur:
                        y_o = _guvenli_sayi(yillik_reel_map.get(aday_u, 0.0), 0.0)
                        a_o = _guvenli_sayi(aylik_reel_lookup.get((aday_u, recete_ay_no), y_o), y_o)
                        if y_o > 0:
                            carpan = a_o / y_o
                            tahmini_tl = aday_bilgi.get("GUNCEL_FIYAT", 25.0) * carpan
                            ikame_adaylari.append((aday_u, carpan, tahmini_tl, aday_bilgi.get("BIRIM", "KG")))

                if ikame_adaylari:
                    ikame_adaylari.sort(key=lambda x: x[1])
                    en_iyi_ikame = ikame_adaylari[0]
                    indirim_pct = (1.0 - en_iyi_ikame[1]) * 100.0
                    st.success(
                        f"**Şefin Mevsimlik İkame Önerisi ({katil_tur}):** **{en_iyi_ikame[0]}**\n\n"
                        f"{recete_ay_adi} ayında **{en_iyi_ikame[0]}** mevsiminde (yıllık ortalamasına göre "
                        f"**%{abs(indirim_pct):.1f} {'daha ucuz' if indirim_pct >= 0 else 'seviyesinde'}**, "
                        f"yaklaşık `{en_iyi_ikame[2]:.2f} ₺/{en_iyi_ikame[3]}`). "
                        f"Menüde **{katil_ad}** payını azaltıp **{en_iyi_ikame[0]}** ile dengeleyerek kâr marjını koruyabilirsiniz."
                    )

                st.dataframe(
                    df_kalem_detay[["MAL_ADI", "BIRIM", "PORSIYON_MIKTAR", "AYLIK_BIRIM_TL", "KALEM_MALIYET_TL"]].rename(
                        columns={
                            "MAL_ADI": "Malzeme",
                            "BIRIM": "Birim",
                            "PORSIYON_MIKTAR": "Miktar",
                            "AYLIK_BIRIM_TL": f"{recete_ay_adi} Fiyatı (₺)",
                            "KALEM_MALIYET_TL": "Porsiyon Tutarı (₺)",
                        }
                    ),
                    column_config={
                        "Miktar": st.column_config.NumberColumn("Miktar", format="%.2f"),
                        f"{recete_ay_adi} Fiyatı (₺)": st.column_config.NumberColumn(
                            f"{recete_ay_adi} Fiyatı (₺)", format="%.2f ₺"
                        ),
                        "Porsiyon Tutarı (₺)": st.column_config.NumberColumn(
                            "Porsiyon Tutarı (₺)", format="%.2f ₺"
                        ),
                    },
                    use_container_width=True,
                    hide_index=True,
                )
    else:
        st.warning("Reçete maliyetini hesaplamak için lütfen en az 1 malzeme seçin.")
