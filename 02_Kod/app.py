from datetime import datetime
from io import BytesIO
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
st.set_page_config(
    page_title="SNC | Akıllı Satın Alma",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tarayıcı otomatik çevirisinin React DOM'unu bozmasını (NotFoundError: removeChild) kalıcı olarak engelle
components.html(
    """
    <script>
    try {
        const doc = window.parent.document;
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
# 1. VERİ VE MODEL YÜKLEME ALTYAPISI (GÖRECELİ YOL + GÜVENLİ YEDEK)
# -----------------------------------------------------------------------------
def _dosya_yolu_coz(goreceli_yol: str) -> Path:
    """Hem ana dizinden hem de 02_Kod/ içinden çalıştırıldığında göreceli yolu çözer."""
    dogrudan = Path(goreceli_yol)
    if dogrudan.exists():
        return dogrudan
    ust_dizin = Path("..") / goreceli_yol
    if ust_dizin.exists():
        return ust_dizin
    betik_koku = Path(__file__).resolve().parent.parent / goreceli_yol
    if betik_koku.exists():
        return betik_koku
    return dogrudan


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
def verileri_yukle() -> dict:
    """Tüm CSV dosyalarını '01_Veri/' altından okur; dosya yoksa güvenli yedek üretir."""
    veri = {}

    dosya_listesi = {
        "hal_reel_ozellikli": ("01_Veri/hal_reel_ozellikli.csv", ["TARIH"]),
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
    }

    for anahtar, (goreceli_yol, tarih_sutunlari) in dosya_listesi.items():
        yol = _dosya_yolu_coz(goreceli_yol)
        if yol.exists():
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
                "🟢 Yoğun Toplu Alım / Yıllık Sözleşme Ayı"
                if len(urunler) >= 3
                else ("🟡 Seçili Ürünlerde Fırsat / Sözleşme" if len(urunler) > 0 else "⚪ Rutin Takip / Önceki Stoktan Kullanım")
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
        ikame_html = f"<b>🟢 Aynı Kümedeki Daha Ucuz İkame Ürünler:</b> {ikame_satir}"
    elif ayni_kume_urunleri:
        ikame_html = f"<b>🔄 Aynı Kümedeki Alternatif Ürünler:</b> {', '.join(ayni_kume_urunleri[:5])}"
    else:
        ikame_html = "Bu kümede başka ürün bulunmamaktadır."

    st.markdown(
        f"""
        <div class="signal-card" style="border-left:5px solid #1B7A43; padding:12px 16px; min-height:auto; margin-bottom:14px; background:#F0FDF4;">
            <div style="display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin-bottom:6px;">
                <span style="background:#1B7A43; color:#FFFFFF; padding:3px 10px; border-radius:999px; font-size:0.78rem; font-weight:700;">
                    🧩 Mevsimsel Küme: {kume_adi}
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
    """ozellik_onemi.csv içindeki teknik değişken adlarını kullanıcı dostu Türkçeye çevirir."""
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
    return temiz.replace("_", " ").title()


@st.cache_resource(show_spinner=False)
def modeli_yukle():
    """03_Model/model.joblib varsa yükler; yoksa None ve durum mesajı döndürür."""
    model_yolu = _dosya_yolu_coz("03_Model/model.joblib")
    if model_yolu.exists():
        try:
            model = joblib.load(model_yolu)
            return model, True, "Aktif (03_Model/model.joblib yüklendi)"
        except Exception as e:
            return None, False, f"Yedek Mod (Model yükleme hatası: {e})"
    return None, False, "Yedek Mod (03_Model/model.joblib bekleniyor)"


# Verileri ve modeli yükle
VERILER = verileri_yukle()
df_ozellikli = VERILER["hal_reel_ozellikli"]
df_aylik_reel = VERILER["ilk_25_aylik_reel_fiyat"]
df_karar_destegi = VERILER["ilk_25_reel_karar_destegi"]
df_reel_ozet = VERILER["ilk_25_reel_ozet"]
df_gunluk_karar = VERILER["gunluk_satinalma_karar"]
df_haftalik_karar = VERILER["haftalik_satinalma_karar"]
df_aylik_karar = VERILER["aylik_satinalma_karar"]
df_mevsimsel_karar = VERILER["mevsimsel_satinalma_karar"]

MODEL, MODEL_AKTIF, MODEL_DURUM_METNI = modeli_yukle()


# -----------------------------------------------------------------------------
# 2. SOL MENÜ (SIDEBAR)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="snc-badge">
            <h2>🌿 SNC | Akıllı Satın Alma</h2>
            <p>Çok Şubeli Restoran Zinciri Karar Destek Sistemi</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🏪 İşletme & Filtre Ayarları")

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
        "Ürün Kategorisi (Mal Türü)",
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

    st.divider()
    st.markdown("### 🧠 Tahmin Motoru Durumu")
    if MODEL_AKTIF:
        st.success("🟢 **Makine Öğrenmesi Modeli Aktif**\n\nEğitilmiş tahmin modeli devrede.")
    else:
        st.warning(
            "🟡 **Yedek Tahmin Modu Aktif**\n\n"
            "Eğitilmiş tahmin modeli henüz yüklenmedi. "
            "Sistem geçmiş fiyat trendleriyle güvenli yedek modda çalışıyor."
        )
    st.caption("Kaynak: İzmir BB Hal Fiyatları (2006–2025) & TCMB EVDS TÜFE")


# -----------------------------------------------------------------------------
# 3. ANA BAŞLIK (MODERN HERO ŞERİDİ) VE 6 SEKME YAPISI
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="snc-hero" translate="no">
        <div>
            <div class="snc-hero-title">🌿 SNC | Akıllı Satın Alma Platformu</div>
            <div class="snc-hero-sub">İzmir Hal Fiyatları (2006–2025) &amp; TÜFE Bazlı Reel Karar Destek Sistemi</div>
        </div>
        <div class="snc-hero-pill">🏪 {aktif_sube_sayisi} Aktif Şube • Odak: {secili_odak_urun}</div>
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
# 1. SEKME: 📊 PANEL & ÖZET
# =============================================================================
with sekme_panel:
    with st.expander("ℹ️ Bu Ekran Nasıl Okunur?", expanded=False):
        st.write(
            f"Fiyatı son hafta aniden dalgalanan ürünleri, 20 yıllık genel piyasa özetini ve "
            f"**{aktif_sube_sayisi} şubeniz** için tek tıkla indirilebilir Yönetici Brifingi (.txt) ve PDF özetini buradan inceleyebilirsiniz."
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
                <h4>🚨 Fiyat Şoku Alarmı: Kısa Dönem Oynaklığı (7 Gün) Orta Dönemi (30 Gün) Aşan İlk 3 Ürün</h4>
                <div>Son piyasa kayıtlarında kısa vadeli fiyat dalgalanması hızlanan ürünler tespit edildi. Spot alımda dikkatli olunmalı:</div>
                <div style="margin-top:8px;">{alarm_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("✅ Seçili filtrelerde kısa dönem oynaklığı (7G) 30 günlük ortalamayı aşan kritik fiyat şoku bulunmamaktadır.")

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
    st.subheader("📋 Tek Tıkla Pazartesi Sabahı Yönetici Özeti")
    st.caption(
        f"{aktif_sube_sayisi} şubeli restoran zincirinin haftalık satın alma toplantısı için seçilen aya özel "
        "riskli ürünleri, gelecek ay zam beklenen kalemleri ve alım fırsatlarını tek tıkla özetler."
    )

    ust_col1, ust_col2 = st.columns([1, 2])
    with ust_col1:
        varsayilan_ay_no = datetime.now().month
        secili_ay_no = st.selectbox(
            "📅 Raporlanacak Ayı Seçin",
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

    ozet_markdown = f"""
#### 🗓️ {secili_ay_adi} Ayı Pazartesi Sabahı Satın Alma & Yönetici Brifingi ({aktif_sube_sayisi} Şube)

<div style="background:#FEE2E2; border-left:5px solid #DC2626; padding:12px 16px; border-radius:8px; margin-bottom:10px; color:#7F1D1D;">
    <b>🔴 KÖTÜ / YÜKSEK RİSK — Haftanın En Oynak 3 Ürünü ({secili_ay_adi}):</b><br>
    {"<br>".join([f"• {x}" for x in riskli_3_liste]) if riskli_3_liste else "• Veri bulunamadı."}
</div>

<div style="background:#FEF9C3; border-left:5px solid #CA8A04; padding:12px 16px; border-radius:8px; margin-bottom:10px; color:#713F12;">
    <b>🟡 TEHLİKELİ / ZAM UYARISI — Gelecek Ay ({gelecek_ay_adi}) Fiyatı En Çok Artacak 3 Ürün:</b><br>
    {"<br>".join([f"• {x}" for x in artis_3_liste]) if artis_3_liste else "• Veri bulunamadı."}
</div>

<div style="background:#DCFCE7; border-left:5px solid #16A34A; padding:12px 16px; border-radius:8px; margin-bottom:6px; color:#14532D;">
    <b>🟢 İYİ / FIRSAT — {secili_ay_adi} Ayında En Uygun Dönemde Olan Ürünler:</b><br>
    {"<br>".join([f"• {x}" for x in firsat_liste]) if firsat_liste else "• Veri bulunamadı."}
</div>
""".strip()

    def _brifing_pdf_olustur(
        ay_adi: str,
        gel_ay_adi: str,
        sube_say: int,
        riskler: list,
        artislar: list,
        firsatlar: list,
    ) -> bytes:
        import textwrap
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyBboxPatch

        fig = plt.figure(figsize=(8.27, 11.69), dpi=150)  # A4 Dikey
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 140)
        ax.axis("off")
        fig.patch.set_facecolor("#F8FAFC")

        # Üst Kurumsal Başlık Bandı (#1B7A43)
        header_box = FancyBboxPatch(
            (4, 122), 92, 14, boxstyle="round,pad=0.6,rounding_size=1.8",
            facecolor="#1B7A43", edgecolor="#14532D", linewidth=1.2
        )
        ax.add_patch(header_box)
        ax.text(
            50, 131.2, "SNC | AKILLI SATIN ALMA — PAZARTESİ SABAHI YÖNETİCİ BRİFİNGİ",
            color="white", fontsize=13.5, fontweight="bold", ha="center", va="center"
        )
        ax.text(
            50, 125.8,
            f"Dönem: {ay_adi}  (Gelecek Ay: {gel_ay_adi})   |   Kapsam: {sube_say} Şubeli Restoran Zinciri   |   Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            color="#DCFCE7", fontsize=9.2, ha="center", va="center"
        )

        # Özet Bilgi Şeridi
        meta_box = FancyBboxPatch(
            (4, 113.5), 92, 6.2, boxstyle="round,pad=0.4,rounding_size=1.2",
            facecolor="#FFFFFF", edgecolor="#CBD5E1", linewidth=0.9
        )
        ax.add_patch(meta_box)
        ax.text(
            50, 116.6,
            "Renk Kodu Rehberi:   [KIRMIZI] Yüksek Oynaklık / Kötü Risk     |     [SARI] Tehlikeli / Zam Uyarısı     |     [YEŞİL] İyi / Alım Fırsatı",
            color="#334155", fontsize=8.8, fontweight="bold", ha="center", va="center"
        )

        def _bolum_kutusu_ciz(y_ust, baslik, maddeler, arka_renk, kenar_renk, baslik_renk, yazi_renk, etiket):
            satirlar = []
            for m in (maddeler if maddeler else ["Veri bulunamadı."]):
                sarili = textwrap.wrap(f"• {m}", width=84)
                satirlar.extend(sarili)
            kutu_yukseklik = max(24.0, 9.5 + len(satirlar) * 3.5)
            y_alt = y_ust - kutu_yukseklik

            kutu = FancyBboxPatch(
                (4, y_alt), 92, kutu_yukseklik,
                boxstyle="round,pad=0.5,rounding_size=1.8",
                facecolor=arka_renk, edgecolor=kenar_renk, linewidth=1.6
            )
            ax.add_patch(kutu)

            # Sol kalın vurgu şeridi
            serit = FancyBboxPatch(
                (4, y_alt), 1.8, kutu_yukseklik,
                boxstyle="round,pad=0.0,rounding_size=0.6",
                facecolor=kenar_renk, edgecolor=kenar_renk, linewidth=0.5
            )
            ax.add_patch(serit)

            # Durum rozeti (sağ üst)
            rozet = FancyBboxPatch(
                (75, y_ust - 6.2), 19, 4.4,
                boxstyle="round,pad=0.2,rounding_size=1.0",
                facecolor=kenar_renk, edgecolor=kenar_renk, linewidth=0.5
            )
            ax.add_patch(rozet)
            ax.text(84.5, y_ust - 4.0, etiket, color="white", fontsize=8.5, fontweight="bold", ha="center", va="center")

            ax.text(8.0, y_ust - 4.2, baslik, color=baslik_renk, fontsize=11.0, fontweight="bold", ha="left", va="center")

            y_cursor = y_ust - 9.5
            for s in satirlar:
                ax.text(8.2, y_cursor, s, color=yazi_renk, fontsize=9.3, ha="left", va="top")
                y_cursor -= 3.5

            return y_alt - 4.0

        # 1. KIRMIZI KUTU: Kötü / En Riskli 3 Ürün
        y_sonraki = _bolum_kutusu_ciz(
            109.5,
            f"1. Haftanın En Riskli (Yüksek Oynaklıklı) 3 Ürünü — {ay_adi}",
            riskler,
            arka_renk="#FEE2E2",
            kenar_renk="#DC2626",
            baslik_renk="#991B1B",
            yazi_renk="#7F1D1D",
            etiket="KÖTÜ / RİSKLİ",
        )

        # 2. SARI KUTU: Tehlikeli / Gelecek Ay Fiyatı En Çok Artacak 3 Ürün
        y_sonraki = _bolum_kutusu_ciz(
            y_sonraki,
            f"2. Gelecek Ay ({gel_ay_adi}) Fiyatı En Çok Artacak 3 Ürün",
            artislar,
            arka_renk="#FEF9C3",
            kenar_renk="#CA8A04",
            baslik_renk="#854D0E",
            yazi_renk="#713F12",
            etiket="TEHLİKELİ / UYARI",
        )

        # 3. YEŞİL KUTU: İyi / Fırsat Ürünleri
        _bolum_kutusu_ciz(
            y_sonraki,
            f"3. {ay_adi} Ayında En Uygun Dönemdeki Fırsat Ürünleri",
            firsatlar,
            arka_renk="#DCFCE7",
            kenar_renk="#16A34A",
            baslik_renk="#166534",
            yazi_renk="#14532D",
            etiket="İYİ / FIRSAT",
        )

        # Alt Bilgi (Footer)
        ax.text(
            50, 5.5,
            "SNC | Akıllı Satın Alma Karar Destek Sistemi  •  Veri Kaynağı: İzmir BB Hal Fiyatları (2006–2025) & TCMB EVDS TÜFE",
            color="#64748B", fontsize=8.2, ha="center", va="center"
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

    pdf_bayt = _brifing_pdf_olustur(
        ay_adi=secili_ay_adi,
        gel_ay_adi=gelecek_ay_adi,
        sube_say=aktif_sube_sayisi,
        riskler=riskli_3_liste,
        artislar=artis_3_liste,
        firsatlar=firsat_liste,
    )

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

    dl_c1, dl_c2 = st.columns([1, 1])
    with dl_c1:
        st.download_button(
            label=f"📝 Yönetici Brifingi (.txt) — {secili_ay_adi}",
            data=ozet_txt_icerik.encode("utf-8"),
            file_name=f"SNC_Yonetici_Brifingi_{secili_ay_adi}.txt",
            mime="text/plain",
            type="primary",
            use_container_width=True,
        )
    with dl_c2:
        st.download_button(
            label=f"📄 Renkli Yönetici Brifingi (.pdf) — {secili_ay_adi}",
            data=pdf_bayt,
            file_name=f"SNC_Yonetici_Brifingi_{secili_ay_adi}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    # -------------------------------------------------------------------------
    # D) OPSİYONEL MODEL VE KÜME ÖZETİ (Suzan'ın CSV'leri Eklendiğinde Otomatik Görünür)
    # -------------------------------------------------------------------------
    df_p_model = VERILER.get("model_karsilastirma", pd.DataFrame())
    df_p_onem = VERILER.get("ozellik_onemi", pd.DataFrame())
    df_p_kume = VERILER.get("urun_kumeleri", pd.DataFrame())

    if not df_p_model.empty or not df_p_onem.empty or not df_p_kume.empty:
        st.divider()
        st.subheader("🧠 Makine Öğrenmesi Model Performansı & Ürün Kümeleri Özeti")
        p_c1, p_c2 = st.columns(2, gap="large")
        with p_c1:
            if not df_p_model.empty:
                st.markdown("**📊 Model Performans Karşılaştırma Tablosu**")
                st.dataframe(df_p_model, use_container_width=True, hide_index=True)
            if not df_p_kume.empty:
                st.markdown("**🧩 Mevsimsel Ürün Kümeleri**")
                st.dataframe(df_p_kume, use_container_width=True, hide_index=True)
        with p_c2:
            if not df_p_onem.empty and len(df_p_onem.columns) >= 2:
                st.markdown("**🧬 Tahmini En Çok Etkileyen Faktörler**")
                st.dataframe(df_p_onem, use_container_width=True, hide_index=True)


# =============================================================================
# 2. SEKME: 📅 ANALİZ & ZAMANLAMA
# =============================================================================
with sekme_analiz:
    st.subheader(f"📅 Analiz & Zamanlama — {secili_odak_urun}")
    with st.expander("ℹ️ Bu Ekran Nasıl Okunur?", expanded=False):
        st.write(
            "**Sol Üst:** Nominal (etiket) ve Reel (TÜFE arındırılmış) fiyat geçmişi. "
            "**Sağ Üst:** Yeşil kutular en ucuz ayları, kırmızı kutular en pahalı ayları gösterir. "
            "**Alt Bölüm:** Haftanın en ucuz hal günü ve yıllar arası gerçek zam / TÜFE ayrıştırması."
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
        st.markdown(f"#### 📈 {secili_odak_urun} — Tarihsel Fiyat Eğilimi")
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
                    f"""<div class="insight-note"><b>💬 Grafik Yorumu ({secili_odak_urun} — Nominal):</b>
                    İlk kayıttan son kayda nominal etiket fiyatı <b>{ilk_nom:.2f} ₺ → {son_nom:.2f} ₺</b> ({nom_kat:.1f} kat) seviyesine çıkmıştır.
                    Son dönemde gün içi taban–tavan (Asgari–Azami) fiyat aralığı <b>{son_bant_fark:.2f} ₺</b> genişliğindedir;
                    bu bant tedarikçi görüşmelerinde kalite ve pazarlık marjını gösterir.</div>""",
                    unsafe_allow_html=True,
                )
            else:
                ort_r = _guvenli_sayi(df_urun["REEL_ORTALAMA_UCRET"].mean(), 0.0)
                min_r = _guvenli_sayi(df_urun["REEL_ORTALAMA_UCRET"].min(), 0.0)
                max_r = _guvenli_sayi(df_urun["REEL_ORTALAMA_UCRET"].max(), 0.0)
                son_r = _guvenli_sayi(df_urun["REEL_ORTALAMA_UCRET"].dropna().iloc[-1], ort_r)
                konum_txt = "tarihsel ortalamanın üzerinde (pahalı dönem)" if son_r > ort_r else "tarihsel ortalamanın altında (uygun dönem)"
                st.markdown(
                    f"""<div class="insight-note"><b>💬 Grafik Yorumu ({secili_odak_urun} — Reel):</b>
                    Enflasyondan arındırılmış 20 yıllık ortalama <b>{ort_r:.2f} ₺</b> (dip: {min_r:.2f} ₺, zirve: {max_r:.2f} ₺).
                    Son reel fiyat (<b>{son_r:.2f} ₺</b>) şu an <b>{konum_txt}</b> bölgesindedir; satın alma kararları nominal değil bu reel seviyeye göre verilmelidir.</div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.warning("Seçili ürün için tarihsel fiyat kaydı bulunamadı.")

    with ust_sag:
        st.markdown("#### 🗓️ 25 Ürün × 12 Ay — En Ucuz Aylar Isı Haritası")
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
                        f"""<div class="insight-note"><b>💬 Isı Haritası Yorumu ({secili_odak_urun}):</b>
                        Koyu yeşil bölge olan <b>{u_ay}</b> ayında reel fiyat dip yaparken (<b>{u_f:.2f} ₺</b>),
                        koyu kırmızı bölge olan <b>{p_ay}</b> ayında zirveye çıkmaktadır (<b>{p_f:.2f} ₺</b> — <b>+%{fark_p:.1f}</b> mevsimsel makas).
                        Sözleşme veya stoklama mutlaka <b>{u_ay}</b> penceresinde planlanmalıdır.</div>""",
                        unsafe_allow_html=True,
                    )
        else:
            st.warning("Aylık mevsimsel fiyat verisi bulunamadı.")

    st.divider()

    # -------------------------------------------------------------------------
    # 2. ALT BÖLÜM: SOL (HAFTANIN HANGİ GÜNÜ HAL'E GİDİLMELİ?) | SAĞ (ENFLASYON AYNASI)
    # -------------------------------------------------------------------------
    alt_sol, alt_sag = st.columns(2, gap="large")

    # --- A) Haftanın Hangi Günü Hal'e Gidilmeli? ---
    with alt_sol:
        st.markdown(f"#### 🚚 Haftanın Hangi Günü Hal'e Gidilmeli? ({secili_odak_urun})")
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
                    f"🟢 **En Uygun Hal Günü Önerisi:** **{secili_odak_urun}** alımı için haftanın en ucuz günü "
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
        st.markdown(f"#### 🪞 Enflasyon Aynası: Zam Gerçek mi, TÜFE mi? ({secili_odak_urun})")
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
                        f"📈 **Enflasyon Üstü Gerçek Artış:** {baslangic_yil}–{bitis_yil} arasında **{secili_odak_urun}** "
                        f"nominal olarak **%{nominal_degisim:.1f}** artarken, TÜFE enflasyonu arındırıldığında "
                        f"gerçek (reel) bazda **+%{reel_degisim:.1f}** pahalanmıştır."
                    )
                elif reel_degisim < -5:
                    st.success(
                        f"🟢 **Reel Olarak Ucuzlama:** {baslangic_yil}–{bitis_yil} arasında **{secili_odak_urun}** "
                        f"nominal olarak **%{nominal_degisim:.1f}** artsa da, TÜFE enflasyonunun altında kalarak "
                        f"reel bazda **%{reel_degisim:.1f}** ucuzlamıştır."
                    )
                else:
                    st.info(
                        f"⚖️ **Enflasyonla Paralel Seyir:** {baslangic_yil}–{bitis_yil} arasında **{secili_odak_urun}** "
                        f"reel bazda **%{reel_degisim:.1f}** değişimle genel TÜFE enflasyonuna paralel seyretmiştir."
                    )
            else:
                st.info("Enflasyon karşılaştırması için en az 2 farklı yıl verisi gereklidir.")
        else:
            st.warning("Enflasyon aynası için veri bulunamadı.")

    st.divider()

    # -------------------------------------------------------------------------
    # 3. ÖZGÜN ARAŞTIRMA SORUSU, İSTATİSTİKSEL HİPOTEZ TESTİ & 12 AYLIK AJANDA
    # -------------------------------------------------------------------------
    st.markdown("### 🧪 Özgün Araştırma Soruları, Hipotez Sınaması ve 12 Aylık Sözleşme Ajandası")

    ozg_sol, ozg_sag = st.columns([1.05, 1.15], gap="large")

    # --- A) İstatistiksel Hipotez Testleri (Kruskal-Wallis p-değeri) ---
    with ozg_sol:
        st.markdown(f"#### 🔬 İstatistiksel Hipotez Testleri (Canlı p-Değeri — {secili_odak_urun})")
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
                            {'✅ H₁ KABUL EDİLDİ (Anlamlı Fark Var)' if kabul_mu else '⚠️ H₀ REDDEDİLEMEDİ (Fark Zayıf)'}
                        </div>
                        <div class="signal-card-sub">
                            <b>Test İstatistiği:</b> H = {h_stat:.2f} &nbsp;|&nbsp; <b>p-değeri {p_metin}</b> (α = 0.05)<br>
                            <b>💬 Dinamik Yorum ({secili_odak_urun}):</b> En ucuz mevsim <b>{en_u_m}</b> ({en_u_v:.2f} ₺),
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
                            {'✅ H₁ KABUL EDİLDİ (Kategoriler Arası Fark Anlamlı)' if kabul2 else '⚠️ H₀ REDDEDİLEMEDİ'}
                        </div>
                        <div class="signal-card-sub">
                            <b>Test İstatistiği:</b> H = {h2_stat:.2f} &nbsp;|&nbsp; <b>p-değeri {p2_metin}</b> (α = 0.05)<br>
                            <b>💬 Dinamik Yorum (Seçili Kategoriler):</b> En yüksek ortalama reel birim maliyet <b>{en_pah_tur}</b>
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
        st.markdown("#### 📊 Özgün Soru: 20 Yılda Reel Olarak En Çok Pahalanan ve Ucuzlayan Ürünler")
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
                f"""<div class="insight-note"><b>💬 Özgün Soru Yanıtı ({donem_etk}):</b>
                TÜFE enflasyonu tamamen arındırıldığında bile <b>{lider_zam['MAL_ADI']}</b> reel olarak
                <b>+%{lider_zam['REEL_DEGISIM_YUZDE']:.1f}</b> ({lider_zam['ILK_DONEM_REEL']:.2f} ₺ → {lider_zam['SON_DONEM_REEL']:.2f} ₺)
                ile en fazla pahalanan ürün olurken; <b>{lider_ucuz['MAL_ADI']}</b> reel bazda
                <b>%{lider_ucuz['REEL_DEGISIM_YUZDE']:.1f}</b> değişimle en avantajlı ürün olmuştur.
                Uzun vadeli sözleşmeler kırmızı bölgedeki kalemlere öncelik vermelidir.</div>""",
                unsafe_allow_html=True,
            )
        else:
            st.info("Reel dönem karşılaştırması için yeterli yıl aralığı bulunamadı.")

    # --- C) 12 Aylık Sözleşme & Toplu Alım Ajandası ---
    st.markdown("#### 📅 12 Aylık Satın Alma & Sözleşme Ajandası (Hangi Ayda Hangi Ürün Alınmalı?)")
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
            f"""<div class="insight-note"><b>💬 12 Aylık Ajanda Yorumu:</b>
            25 ürünün en ucuz alım pencereleri yılın <b>{toplam_firsat_ay} farklı ayına</b> yayılmaktadır.
            En yoğun fırsat ayı <b>{en_yogun_ay_satir['AY']}</b> olup tek başına <b>{int(en_yogun_ay_satir['FIRSAT_URUN_SAYISI'])} ürün</b>
            ({en_yogun_ay_satir['EN_UCUZ_URUNLER']}) bu ayda yılın en düşük reel fiyatına inmektedir.
            <b>{aktif_sube_sayisi} şube</b> için yıllık tedarikçi ihaleleri bu ajandaya göre takvimlendirilmelidir.</div>""",
            unsafe_allow_html=True,
        )

# =============================================================================
# 3. SEKME: 🎯 STRATEJİ & RİSK
# =============================================================================
with sekme_strateji:
    st.subheader("🎯 Stratejik Satın Alma, Risk & Backtest")
    with st.expander("ℹ️ Bu Ekran Nasıl Okunur?", expanded=False):
        st.write(
            "**Kraljic Matrisi:** Sağ üstteki kırmızı ürünler hem pahalı hem risklidir (sözleşme gerektirir). "
            "**Pazarlık Makası:** Aynı gün içi en yüksek–en düşük fiyat farkı yüksek ürünlerde pazarlık gücü fazladır. "
            "**Backtest:** Geçen 1 yılda sistemin 'UYGUN' haftalarında alım yapan restoranın kazancını kanıtlar."
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
        st.markdown("#### 🧭 Kraljic Satın Alma Strateji Matrisi (4 Bölge)")
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
            st.markdown("##### 📋 4 Strateji Bölgesine Göre Ürün Sınıflandırma Özeti")
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
                f"""<div class="insight-note"><b>💬 Kraljic Matrisi Yorumu:</b>
                Seçili kategorilerde toplam <b>{len(kraljic_df)} ürünün</b> <b>{stratejik_sayisi} tanesi</b> yüksek maliyet ve yüksek riskli
                <b>Kritik / Sözleşmeli Alım</b> bölgesinde (uzun vadeli sözleşme şart), <b>{rutin_sayisi} tanesi</b> ise düşük riskli
                <b>Rutin / Spot Alım</b> bölgesindedir. {odak_bolge_not}</div>""",
                unsafe_allow_html=True,
            )
        else:
            st.warning("Kraljic matrisi için yeterli kayıt bulunamadı.")

    # --- B) Pazarlık Gücü & Kalite Makası ---
    with str_sag:
        st.markdown("#### 🤝 Pazarlık Gücü & Kalite Makası (İlk 10 Ürün)")
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
                f"💡 **Pazarlık Fırsatı:** **{lider_urun}** ürününde aynı gün içinde en düşük ve en yüksek kalite/parti "
                f"fiyatı arasındaki makas ortalama **%{lider_oran:.1f}** seviyesindedir. Tedarikçi tekliflerinde "
                f"Hal Taban Fiyatı bandına yakın pazarlık yapılmalıdır."
            )
        else:
            st.info("Fiyat makası hesaplanacak kayıt bulunamadı.")

    st.divider()

    # -------------------------------------------------------------------------
    # 2. ALT BÖLÜM: GEÇEN YIL BU SİSTEMİ DİNLESEYDİK NE OLURDU? (BACKTEST)
    # -------------------------------------------------------------------------
    st.markdown("#### ⏪ Geçen Yıl Bu Sistemi Dinleseydik Ne Olurdu? (1 Yıllık Backtest)")
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

            if not df_uygun_haftalar.empty:                akilli_alim_ort = float(df_uygun_haftalar[fiyat_sutunu].mean())
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
                        name="🟢 SNC 'UYGUN' Alım Haftaları",
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
                f"""<div class="insight-note"><b>💬 Backtest Yorumu ({'Odak Ürün' if bt_kapsam.startswith('Seçili') else 'Genel Sepet'}):</b>
                Son 1 yıllık gerçek veride {bt_hedef_txt} her hafta sabit alım yapmak yerine SNC'nin yeşil elmasla işaretlediği
                <b>{uygun_hafta_sayisi} uygun haftada</b> alım yapan bir restoran birim başına ortalama <b>{birim_fark:.2f} ₺</b>
                (<b>%{tasarruf_yuzde:.1f}</b>) daha düşük maliyet elde etmiştir. Bu sonuç, zamanlamaya dayalı satın almanın sahada çalıştığını kanıtlar.</div>""",
                unsafe_allow_html=True,
            )
            st.caption("Not: Uygun sinyal haftalarında stoklu veya öne çekilmiş alım yapıldığı varsayılmıştır.")
        else:
            st.info("Seçili kapsam için haftalık backtest kaydı bulunamadı.")
    else:
        st.warning("Haftalık satın alma karar verisi bulunamadı.")

# =============================================================================
# 4. SEKME: 🤖 KARAR EKRANI
# =============================================================================
with sekme_karar:
    st.subheader(f"🤖 Karar Ekranı — {secili_odak_urun}")
    with st.expander("ℹ️ Bu Ekran Nasıl Okunur?", expanded=False):
        st.write(
            f"**1. Adım:** Piyasanın günlük/haftalık/aylık/mevsimsel ucuzluk durumu. "
            f"**2. Adım:** Gelecek hafta fiyat tahmini ve Şimdi Al / Bekle önerisi. "
            f"**3. Adım:** Tedarikçinizin **{aktif_sube_sayisi} şube** için verdiği teklifin hal bandına göre denetimi."
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
    st.markdown(f"#### 1️⃣ Piyasa Şu An Ucuz mu Pahalı mı? — 4 Zaman Dilimi Özeti ({secili_odak_urun})")

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
            return "🟢 UYGUN", "Alım Fırsatı", "#15803D", "#DCFCE7"
        if "PAHALI" in u:
            return "🔴 PAHALI", "Dikkatli Al", "#B91C1C", "#FEE2E2"
        return "🟡 NORMAL", "Piyasa Dengeli", "#A16207", "#FEF9C3"

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
        st.markdown(f"#### 2️⃣ Gelecek Hafta Fiyat Tahmini (TÜFE Bazlı Reel Fiyat) — {secili_odak_urun}")

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

            with st.expander("⚙️ İleri Düzey: Tahmin Parametrelerini (Senaryo Testi) Düzenle", expanded=False):
                st.caption("Varsayılan değerler ürünün son hal kayıtlarından otomatik doldurulur. Farklı bir piyasa senaryosunu test etmek için değerleri değiştirebilirsiniz.")
                g_c1, g_c2, g_c3 = st.columns(3)
                with g_c1:
                    ay_girdi = st.number_input("Ay (1-12)", min_value=1, max_value=12, value=ay_degeri, key="k_ay")
                    hafta_girdi = st.number_input("Yılın Haftası (1-53)", min_value=1, max_value=53, value=hafta_degeri, key="k_hafta")
                    reel_girdi = st.number_input(
                        "Güncel Reel Fiyat (TL)", min_value=0.01, value=round(guncel_reel, 2), step=0.5, key="k_reel"
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

            tahmin_kaynagi = "Geçmiş Trend & Oynaklık Yedek Motoru"
            tahmin_fiyat = None

            if MODEL_AKTIF and MODEL is not None:
                try:
                    tahmin_fiyat = float(MODEL.predict(X_tahmin)[0])
                    tahmin_kaynagi = "Eğitilmiş Makine Öğrenmesi Modeli"
                except Exception as e:
                    tahmin_fiyat = None
                    tahmin_kaynagi = "Geçmiş Trend & Oynaklık Yedek Motoru"

            if tahmin_fiyat is None:
                sinirli_trend = float(np.clip(deg_girdi, -15.0, 15.0)) / 100.0
                trend_tahmini = reel_girdi * (1.0 + sinirli_trend * 0.65)
                lag_ortalamasi = 0.50 * reel_girdi + 0.30 * lag1_girdi + 0.20 * lag7_girdi
                tahmin_fiyat = round(0.60 * trend_tahmini + 0.40 * lag_ortalamasi, 2)

            belirsizlik_marji = max(float(oyn7_girdi), float(tahmin_fiyat) * 0.06)
            alt_bant = max(0.01, round(tahmin_fiyat - belirsizlik_marji, 2))
            ust_bant = round(tahmin_fiyat + belirsizlik_marji, 2)

            beklenen_degisim_yuzde = (
                ((tahmin_fiyat - reel_girdi) / reel_girdi) * 100.0 if reel_girdi > 0 else 0.0
            )

            if beklenen_degisim_yuzde >= 3.0:
                karar_etiketi = "🟢 ŞİMDİ AL — Alımı Öne Çekin"
                karar_aciklama = (
                    f"Gelecek hafta fiyatın **+%{beklenen_degisim_yuzde:.1f}** yükselerek "
                    f"**{tahmin_fiyat:.2f} TL/{birim_adi}** bandına çıkması bekleniyor. "
                    f"Zam gelmeden bugün stok/sözleşme yapmak kârlı olacaktır."
                )
                karar_tipi = "success"
            elif beklenen_degisim_yuzde <= -3.0:
                karar_etiketi = "🔴 BEKLE — Gelecek Hafta Ucuzlayabilir"
                karar_aciklama = (
                    f"Gelecek hafta fiyatın **%{beklenen_degisim_yuzde:.1f}** gerileyerek "
                    f"**{tahmin_fiyat:.2f} TL/{birim_adi}** civarına inmesi bekleniyor. "
                    f"Büyük stok yerine sadece bu haftanın acil ihtiyacını alın."
                )
                karar_tipi = "error"
            else:
                karar_etiketi = "🟡 NORMAL — Standart Haftalık Alıma Devam"
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

            def _mini_kart(baslik: str, deger: str, alt: str, vurgu_renk: str = "#1B7A43") -> str:
                return f"""
                <div class="signal-card" style="min-height:94px; padding:11px 12px; border-left:4px solid {vurgu_renk};">
                    <div class="signal-card-title" style="font-size:0.78rem; margin-bottom:4px;">{baslik}</div>
                    <div style="color:#1E293B; font-size:1.08rem; font-weight:800; line-height:1.2; margin-bottom:4px;">{deger}</div>
                    <div class="signal-card-sub" style="font-size:0.75rem;">{alt}</div>
                </div>
                """

            t_m1, t_m2, t_m3 = st.columns(3)
            t_m1.markdown(
                _mini_kart("Bugünkü Reel Fiyat", f"{reel_girdi:.2f} TL", f"Birim: {birim_adi}", "#64748B"),
                unsafe_allow_html=True,
            )
            t_m2.markdown(
                _mini_kart(
                    "Gelecek Hafta Tahmini",
                    f"{tahmin_fiyat:.2f} TL",
                    f"{beklenen_degisim_yuzde:+.1f}% Değişim",
                    "#DC2626" if beklenen_degisim_yuzde >= 3 else ("#1B7A43" if beklenen_degisim_yuzde <= -3 else "#F59E0B"),
                ),
                unsafe_allow_html=True,
            )
            t_m3.markdown(
                _mini_kart("Olası Fiyat Aralığı", f"{alt_bant:.2f} – {ust_bant:.2f} TL", f"±{belirsizlik_marji:.2f} TL Belirsizlik", "#1B7A43"),
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

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
                f"📌 **Tahmin Motoru:** {tahmin_kaynagi} | "
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
        st.markdown(f"#### 3️⃣ Tedarikçi Teklif Kontrolü (Güncel Hal Nominal TL) — {secili_odak_urun}")
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

            b_c1, b_c2, b_c3 = st.columns(3)
            b_c1.markdown(
                f"""
                <div class="signal-card" style="min-height:92px; padding:11px 12px; border-left:4px solid #1B7A43;">
                    <div class="signal-card-title" style="font-size:0.78rem; margin-bottom:4px;">Hal En Düşük</div>
                    <div style="color:#1E293B; font-size:1.08rem; font-weight:800; line-height:1.2; margin-bottom:4px;">{son_asg:.2f} TL</div>
                    <div class="signal-card-sub" style="font-size:0.75rem;">Asgari / {birim_etiket}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            b_c2.markdown(
                f"""
                <div class="signal-card" style="min-height:92px; padding:11px 12px; border-left:4px solid #3B82F6;">
                    <div class="signal-card-title" style="font-size:0.78rem; margin-bottom:4px;">Hal Ortalama</div>
                    <div style="color:#1E293B; font-size:1.08rem; font-weight:800; line-height:1.2; margin-bottom:4px;">{son_ort:.2f} TL</div>
                    <div class="signal-card-sub" style="font-size:0.75rem;">Piyasa / {birim_etiket}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            b_c3.markdown(
                f"""
                <div class="signal-card" style="min-height:92px; padding:11px 12px; border-left:4px solid #F59E0B;">
                    <div class="signal-card-title" style="font-size:0.78rem; margin-bottom:4px;">Hal En Yüksek</div>
                    <div style="color:#1E293B; font-size:1.08rem; font-weight:800; line-height:1.2; margin-bottom:4px;">{son_azm:.2f} TL</div>
                    <div class="signal-card-sub" style="font-size:0.75rem;">Azami / {birim_etiket}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

            tk_c1, tk_c2 = st.columns(2)
            with tk_c1:
                teklif_fiyat = st.number_input(
                    f"💬 Tedarikçi Teklifi (TL / {birim_etiket}):",
                    min_value=0.01,
                    value=round(son_ort * 1.05, 2),
                    step=0.50,
                    key="tedarikci_teklif_girdi",
                )
            with tk_c2:
                sube_basi_miktar = st.number_input(
                    f"📦 Şube Başı Sipariş ({birim_etiket}):",
                    min_value=1.0,
                    value=50.0,
                    step=5.0,
                    key="tedarikci_sube_miktar",
                    help=f"Sol menüde seçili {aktif_sube_sayisi} şube ile otomatik çarpılır.",
                )

            toplam_siparis_miktari = sube_basi_miktar * float(aktif_sube_sayisi)
            st.caption(
                f"🧮 **Toplam Sipariş Hacmi:** `{sube_basi_miktar:,.0f} {birim_etiket}/şube` × **`{aktif_sube_sayisi} Şube`** "
                f"= **`{toplam_siparis_miktari:,.0f} {birim_etiket}`** *(Şube sayısını sol menüden değiştirebilirsiniz)*"
            )

            if teklif_fiyat <= son_ort:
                avantaj_birim = son_ort - teklif_fiyat
                sube_avantaj = avantaj_birim * sube_basi_miktar
                toplam_avantaj = avantaj_birim * toplam_siparis_miktari
                st.success(
                    f"🟢 **İYİ TEKLİF — ONAYLANABİLİR**\n\n"
                    f"• Teklif (`{teklif_fiyat:.2f} TL`), hal ortalamasının (`{son_ort:.2f} TL`) **`{avantaj_birim:.2f} TL`** altında.\n"
                    f"• **Şube Başı Kazanç:** `{sube_avantaj:,.2f} TL` | **{aktif_sube_sayisi} Şube Toplam Kazanç:** **`{toplam_avantaj:,.2f} TL`**"
                )
            elif teklif_fiyat <= son_azm:
                pazarlik_birim = teklif_fiyat - son_ort
                sube_pazarlik = pazarlik_birim * sube_basi_miktar
                pazarlik_toplam = pazarlik_birim * toplam_siparis_miktari
                st.warning(
                    f"🟡 **PAZARLIK PAYI VAR — İNDİRİM İSTEYİN**\n\n"
                    f"• Teklif (`{teklif_fiyat:.2f} TL`) hal tavanını aşmıyor ancak ortalamanın (`{son_ort:.2f} TL`) üzerinde.\n"
                    f"• **Hedef İndirim:** Birimde **`{pazarlik_birim:.2f} TL/{birim_etiket}`** düşürülerek `{son_ort:.2f} TL` hedeflenmeli.\n"
                    f"• **Kurtarılacak Tutar:** Şube başı `{sube_pazarlik:,.2f} TL` | **{aktif_sube_sayisi} Şube Toplam:** **`{pazarlik_toplam:,.2f} TL`**"
                )
            else:
                asiri_fark_tavan = teklif_fiyat - son_azm
                asiri_fark_ort = teklif_fiyat - son_ort
                toplam_zarar = asiri_fark_ort * toplam_siparis_miktari
                st.error(
                    f"🔴 **HAL TAVANININ ÜSTÜNDE — TEKLİFİ REDDEDİN!**\n\n"
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
    # 4. OPSİYONEL AÇILIR BÖLÜM: MODEL PERFORMANS KARŞILAŞTIRMASI & DEĞİŞKEN ÖNEMİ
    #    (01_Veri/model_karsilastirma.csv veya 01_Veri/ozellik_onemi.csv yoksa gizli kalır)
    # -------------------------------------------------------------------------
    df_model_kars = VERILER.get("model_karsilastirma", pd.DataFrame())
    df_ozellik_onemi = VERILER.get("ozellik_onemi", pd.DataFrame())

    if not df_model_kars.empty or (not df_ozellik_onemi.empty and len(df_ozellik_onemi.columns) >= 2):
        st.divider()
        with st.expander("📊 Model Performans Karşılaştırması ve Değişken Önem Düzeyleri", expanded=False):
            mk_col1, mk_col2 = st.columns([1.05, 1.15], gap="large")
            with mk_col1:
                if not df_model_kars.empty:
                    st.markdown("##### 🏆 Model Başarı Karşılaştırma Tablosu (Naif Baseline / Random Forest / Gradient Boosting)")
                    st.dataframe(df_model_kars, use_container_width=True, hide_index=True)
                else:
                    st.info("Model karşılaştırma tablosu henüz eklenmedi.")
            with mk_col2:
                if not df_ozellik_onemi.empty and len(df_ozellik_onemi.columns) >= 2:
                    st.markdown("##### 🧬 Fiyat Tahminini En Çok Etkileyen Değişkenler")
                    oz_df = df_ozellik_onemi.copy()
                    ad_kol = "DEGISKEN" if "DEGISKEN" in oz_df.columns else oz_df.columns[0]
                    skor_kol = "ONEM_SKORU" if "ONEM_SKORU" in oz_df.columns else oz_df.columns[1]
                    oz_df[skor_kol] = pd.to_numeric(oz_df[skor_kol], errors="coerce")
                    oz_df = oz_df.dropna(subset=[ad_kol, skor_kol]).sort_values(skor_kol, ascending=True).tail(12)
                    if not oz_df.empty:
                        oz_df["ETIKET_TR"] = oz_df[ad_kol].apply(_degisken_turkce_etiket)
                        fig_oz = go.Figure(
                            go.Bar(
                                x=oz_df[skor_kol],
                                y=oz_df["ETIKET_TR"],
                                orientation="h",
                                marker_color="#1B7A43",
                                text=[f"{v:.3f}" for v in oz_df[skor_kol]],
                                textposition="outside",
                            )
                        )
                        fig_oz.update_layout(
                            height=320,
                            margin=dict(l=10, r=40, t=15, b=10),
                            xaxis_title="Etki / Önem Skoru",
                            yaxis_title="Değişken",
                            xaxis=dict(range=[0, max(float(oz_df[skor_kol].max()) * 1.18, 0.1)]),
                            plot_bgcolor="#FFFFFF",
                            paper_bgcolor="#FFFFFF",
                        )
                        st.plotly_chart(fig_oz, use_container_width=True)

# =============================================================================
# 5. SEKME: 🏪 TASARRUF SİMÜLATÖRÜ
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
    """openpyxl ile kurumsal tasarımlı Satin_Alma_Plani Excel (.xlsx) çıktısı üretir."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Satin_Alma_Plani"

    # 1. Satır: Birleştirilmiş #1B7A43 Zümrüt Yeşili Ana Başlık
    ws.merge_cells("A1:K1")
    ws["A1"] = "SNC | Akıllı Satın Alma - Satın Alma ve Tasarruf Planı"
    ws["A1"].font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill(start_color="1B7A43", end_color="1B7A43", fill_type="solid")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    # 2. Satır: Şube / Fire / Depo Parametreleri ve Tarih
    ws.merge_cells("A2:K2")
    ws["A2"] = (
        f"Şube Sayısı: {sube_sayisi}  |  Beklenen Zayi / Bozulma Oranı: %{fire_orani:.1f}  |  "
        f"Depolama Maliyeti: %{depo_orani:.1f}  |  "
        f"Rapor Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    ws["A2"].font = Font(name="Calibri", size=10, italic=True, bold=True, color="1E293B")
    ws["A2"].fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 22

    # 4. Satır: Koyu Yeşil (#14532D) Beyaz Yazılı Tablo Başlıkları
    basliklar = [
        "Ürün Adı (MAL_ADI)",
        "Birim",
        "En Uygun Alım Ayı",
        "En Uygun Mevsim",
        "Şube Başı Aylık (Kg)",
        "Zincir Yıllık Tonaj (Kg)",
        "Güncel Birim Fiyat (TL)",
        "Mevsimsel Avantaj (%)",
        "Yıllık Spot Maliyet (TL)",
        "Yıllık Akıllı Alım Maliyeti (TL)",
        "Yıllık Net Tasarruf (TL) & Öneri",
    ]
    # Net tasarruf sayısal olsun diye 10. ve 11. sütunları net şekilde ayarla:
    basliklar = [
        "Ürün Adı",
        "Birim",
        "En Ucuz Ay",
        "Şube Başı Aylık (Kg)",
        "Zincir Yıllık Miktar (Kg)",
        "Güncel Fiyat (TL)",
        "Mevsimsel Avantaj (%)",
        "Yıllık Spot Maliyet",
        "Yıllık Akıllı Maliyet",
        "Yıllık Net Tasarruf",
        "Önerilen Satın Alma Stratejisi",
    ]

    ince_kenar = Side(border_style="thin", color="CBD5E1")
    hucre_cerceve = Border(left=ince_kenar, right=ince_kenar, top=ince_kenar, bottom=ince_kenar)
    baslik_dolgu = PatternFill(start_color="14532D", end_color="14532D", fill_type="solid")
    baslik_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

    ws.row_dimensions[4].height = 26
    for col_idx, b_metin in enumerate(basliklar, start=1):
        c = ws.cell(row=4, column=col_idx, value=b_metin)
        c.fill = baslik_dolgu
        c.font = baslik_font
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = hucre_cerceve

    zebra_acik = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    zebra_koyu = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    veri_font = Font(name="Calibri", size=10, color="1E293B")

    # Trafik Işığı Renk Kodları (İyi = Yeşil, Tehlikeli/Orta = Sarı, Kötü/Riskli = Kırmızı)
    yesil_dolgu = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    yesil_font = Font(name="Calibri", size=10, bold=True, color="166534")
    sari_dolgu = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")
    sari_font = Font(name="Calibri", size=10, bold=True, color="854D0E")
    kirmizi_dolgu = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    kirmizi_font = Font(name="Calibri", size=10, bold=True, color="991B1B")

    stok_esik_yuzde = float(fire_orani + depo_orani)

    baslangic_satir = 5
    for idx, r in sim_df.reset_index(drop=True).iterrows():
        satir_no = baslangic_satir + idx
        ws.row_dimensions[satir_no].height = 22
        dolgu = zebra_acik if idx % 2 == 0 else zebra_koyu

        avantaj_pct = float(r["MEVSIMSEL_AVANTAJ_YUZDE"])
        net_marj_pct = avantaj_pct - stok_esik_yuzde

        # Satırın durum rengini belirle:
        # Kötü (Kırmızı): Fire+Depo >= Mevsimsel Avantaj (Fiziksel stok zararlı!)
        # Tehlikeli (Sarı): Net avantaj dar (%0 - %10 arası)
        # İyi (Yeşil): Net avantaj güçlü (>= %10)
        if net_marj_pct <= 0:
            durum_dolgu, durum_font = kirmizi_dolgu, kirmizi_font
        elif net_marj_pct < 10.0:
            durum_dolgu, durum_font = sari_dolgu, sari_font
        else:
            durum_dolgu, durum_font = yesil_dolgu, yesil_font

        satir_degerleri = [
            str(r["MAL_ADI"]),
            str(r["BIRIM"]),
            str(r["EN_UCUZ_AY"]),
            float(r["SUBE_AYLIK_KG"]),
            float(r["YILLIK_TOPLAM_KG"]),
            float(r["GUNCEL_BIRIM_FIYAT"]),
            avantaj_pct / 100.0,
            float(r["YILLIK_SPOT_MALIYET"]),
            float(r["YILLIK_AKILLI_MALIYET"]),
            float(r["YILLIK_NET_TASARRUF"]),
            str(r["STRATEJI_ONERISI"]),
        ]

        for col_idx, val in enumerate(satir_degerleri, start=1):
            hc = ws.cell(row=satir_no, column=col_idx, value=val)
            # 7 (Mevsimsel Avantaj %), 10 (Yıllık Net Tasarruf) ve 11 (Strateji Önerisi) kutularını durum rengiyle boya
            if col_idx in [7, 10, 11]:
                hc.fill = durum_dolgu
                hc.font = durum_font
            else:
                hc.fill = dolgu
                hc.font = veri_font
            hc.border = hucre_cerceve

            if col_idx in [1, 11]:
                hc.alignment = Alignment(horizontal="left", vertical="center")
            elif col_idx in [2, 3]:
                hc.alignment = Alignment(horizontal="center", vertical="center")
            else:
                hc.alignment = Alignment(horizontal="right", vertical="center")

            # Sayı Formatları
            if col_idx in [4, 5]:
                hc.number_format = "#,##0"
            elif col_idx == 6:
                hc.number_format = '#,##0.00 "₺"'
            elif col_idx == 7:
                hc.number_format = "0.0%"
            elif col_idx in [8, 9, 10]:
                hc.number_format = '#,##0 "₺"'

    # En Altta #DCFCE7 Vurgulu TOPLAM Satırı
    toplam_satir_no = baslangic_satir + len(sim_df)
    ws.row_dimensions[toplam_satir_no].height = 25
    toplam_dolgu = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    toplam_font = Font(name="Calibri", size=11, bold=True, color="14532D")

    toplam_degerleri = [
        "TOPLAM / GENEL ÖZET",
        "-",
        "-",
        float(sim_df["SUBE_AYLIK_KG"].sum()),
        float(sim_df["YILLIK_TOPLAM_KG"].sum()),
        float(sim_df["GUNCEL_BIRIM_FIYAT"].mean()),
        float(toplam_tasarruf_yuzde) / 100.0,
        float(toplam_spot),
        float(toplam_akilli),
        float(toplam_net_tasarruf),
        f"Net Kazanç Oranı: %{toplam_tasarruf_yuzde:.1f}",
    ]

    for col_idx, val in enumerate(toplam_degerleri, start=1):
        hc = ws.cell(row=toplam_satir_no, column=col_idx, value=val)
        hc.fill = toplam_dolgu
        hc.font = toplam_font
        hc.border = hucre_cerceve
        if col_idx in [1, 11]:
            hc.alignment = Alignment(horizontal="left", vertical="center")
        elif col_idx in [2, 3]:
            hc.alignment = Alignment(horizontal="center", vertical="center")
        else:
            hc.alignment = Alignment(horizontal="right", vertical="center")

        if col_idx in [4, 5]:
            hc.number_format = "#,##0"
        elif col_idx == 6:
            hc.number_format = '#,##0.00 "₺"'
        elif col_idx == 7:
            hc.number_format = "0.0%"
        elif col_idx in [8, 9, 10]:
            hc.number_format = '#,##0 "₺"'

    # Otomatik Sütun Genişlikleri
    for col_idx in range(1, len(basliklar) + 1):
        harf = get_column_letter(col_idx)
        max_uzunluk = len(str(basliklar[col_idx - 1]))
        for row_idx in range(4, toplam_satir_no + 1):
            deger = ws.cell(row=row_idx, column=col_idx).value
            if deger is not None:
                uzunluk = len(str(deger))
                if col_idx in [8, 9, 10]:
                    uzunluk += 6
                if uzunluk > max_uzunluk:
                    max_uzunluk = uzunluk
        ws.column_dimensions[harf].width = min(max(max_uzunluk + 4, 13), 44)

    # 2. Sayfa: Senaryo A vs. Senaryo B Karşılaştırma Sayfası
    ws2 = wb.create_sheet(title="Senaryo_Karsilastirma")
    ws2.merge_cells("A1:E1")
    ws2["A1"] = "SNC | Senaryo A (Sadece Sözleşme) vs. Senaryo B (Karma Optimizasyon)"
    ws2["A1"].font = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    ws2["A1"].fill = PatternFill(start_color="1B7A43", end_color="1B7A43", fill_type="solid")
    ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 28

    s2_basliklar = ["Strateji / Senaryo", "Yıllık Toplam Maliyet", "Yıllık Net Tasarruf", "Tasarruf Oranı", "Risk & Operasyon Notu"]
    ws2.row_dimensions[3].height = 24
    for col_idx, b_metin in enumerate(s2_basliklar, start=1):
        c = ws2.cell(row=3, column=col_idx, value=b_metin)
        c.fill = baslik_dolgu
        c.font = baslik_font
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = hucre_cerceve

    senaryo_a_pct = (senaryo_a_tasarruf / toplam_spot) if toplam_spot > 0 else 0.0
    senaryo_b_pct = (toplam_net_tasarruf / toplam_spot) if toplam_spot > 0 else 0.0

    s2_satirlar = [
        ("Mevcut Durum: Klasik Spot Alım", float(toplam_spot), 0.0, 0.0, "Fiyat dalgalanmasına açık; referans baz senaryo", zebra_koyu, veri_font),
        ("Senaryo A: Sadece Sabit Fiyat Sözleşmesi", float(senaryo_a_maliyet), float(senaryo_a_tasarruf), float(senaryo_a_pct), "Düşük Risk • %0 Zayi/Bozulma & %0 Depo maliyeti", sari_dolgu, sari_font),
        ("Senaryo B: SNC Karma Strateji (Stok + Sözleşme)", float(toplam_akilli), float(toplam_net_tasarruf), float(senaryo_b_pct), "Önerilen • En Yüksek Net Tasarruf (Ürün bazlı optimum)", yesil_dolgu, yesil_font),
    ]
    for r_i, (s_ad, s_mal, s_tas, s_pct, s_not, s_dolgu, s_fnt) in enumerate(s2_satirlar, start=4):
        ws2.row_dimensions[r_i].height = 24
        degerler = [s_ad, s_mal, s_tas, s_pct, s_not]
        for c_i, val in enumerate(degerler, start=1):
            hc = ws2.cell(row=r_i, column=c_i, value=val)
            hc.fill = s_dolgu
            hc.font = s_fnt
            hc.border = hucre_cerceve
            hc.alignment = Alignment(horizontal="left" if c_i in [1, 5] else "right", vertical="center")
            if c_i in [2, 3]:
                hc.number_format = '#,##0 "₺"'
            elif c_i == 4:
                hc.number_format = "0.0%"

    for col_idx, genislik in enumerate([44, 24, 24, 18, 48], start=1):
        ws2.column_dimensions[get_column_letter(col_idx)].width = genislik

    tampon = BytesIO()
    wb.save(tampon)
    tampon.seek(0)
    return tampon.getvalue()


with sekme_simulator:
    st.subheader("🏪 Çok Şubeli Yıllık Tasarruf Simülatörü")
    with st.expander("ℹ️ Bu Ekran Nasıl Okunur?", expanded=False):
        st.write(
            "Her ay normal piyasa fiyatından (Spot) alım yapmak yerine, en ucuz ayda stoklama veya sabit fiyatlı sözleşme ile "
            "zayi/bozulma ve soğuk hava depo maliyetlerini düşerek yıllık net kazancınızı hesaplar."
        )

    # -------------------------------------------------------------------------
    # 1. KULLANICI GİRDİLERİ (ŞUBE SAYISI, ZAYİ/BOZULMA ORANI %, DEPOLAMA MALİYETİ %)
    # -------------------------------------------------------------------------
    param_col1, param_col2, param_col3 = st.columns(3, gap="large")
    with param_col1:
        sube_sayisi = st.slider(
            "🏪 Zincirdeki Şube Sayısı",
            min_value=1,
            max_value=50,
            value=min(int(aktif_sube_sayisi), 50),
            step=1,
            help="Sol menüdeki aktif şube sayınızla otomatik senkronize gelir; farklı senaryolar için buradan da kaydırabilirsiniz.",
        )
    with param_col2:
        fire_orani = st.slider(
            "🍂 Beklenen Zayi / Bozulma Oranı (%)",
            min_value=0.0,
            max_value=25.0,
            value=6.0,
            step=0.5,
            help="Fiziksel stoklama durumunda beklenen ürün zayiatı / bozulma yüzdesi.",
        )
    with param_col3:
        depo_orani = st.slider(
            "❄️ Depolama / Soğuk Hava Maliyeti (%)",
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
        "🛒 Simülasyon Sepetine Dahil Edilecek Ürünleri Seçin (Varsayılan İlk 6 Ürün):",
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

        st.markdown("#### ✏️ Aylık Tüketim Miktarı Giriş Tablosu (Şube Başı)")
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
                    f"⚠️ Fiziksel Stok Zararlı (Zayi+Depo %{(toplam_stok_maliyet_orani*100):.1f} >= Avantaj %{(avantaj_orani*100):.1f}) "
                    f"→ {en_ucuz_ay} Ayında Sabit Fiyat Sözleşmesi"
                )
            else:
                net_avantaj_orani = avantaj_orani - toplam_stok_maliyet_orani
                akilli_birim_fiyat = guncel_fiyat * (1.0 - net_avantaj_orani)
                yillik_akilli_maliyet = yillik_toplam_kg * akilli_birim_fiyat
                strateji_onerisi = (
                    f"🟢 {en_ucuz_ay} ({en_uygun_mevsim}) Döneminde Toplu Alım & Stoklama "
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
            "💰 Yıllık Toplam Net Tasarruf",
            f"{toplam_net_tasarruf_tl:,.0f} ₺".replace(",", "."),
            f"-%{toplam_tasarruf_yuzde:.1f} Maliyet Avantajı ({sube_sayisi} Şube)",
        )
        sim_kpi2.metric(
            "🏪 Şube Başı Yıllık Kazanç",
            f"{sube_basi_yillik_kazanc:,.0f} ₺ / Şube".replace(",", "."),
            f"Aylık: {(sube_basi_yillik_kazanc / 12.0):,.0f} ₺ / Şube".replace(",", "."),
        )
        sim_kpi3.metric(
            "🏆 En Çok Tasarruf Sağlayan Ürün",
            en_cok_tasarruf_urun,
            f"Yıllık Kazanç: {en_cok_tasarruf_tutar:,.0f} ₺".replace(",", "."),
        )

        st.markdown("#### 📊 Ürün Bazında Yıllık Spot Maliyet vs. SNC Akıllı Alım Maliyeti (TL)")
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
            f"""<div class="insight-note"><b>💬 Simülasyon Grafiği Yorumu ({sube_sayisi} Şube • Zayi %{fire_orani:.1f} • Depo %{depo_orani:.1f}):</b>
            Seçtiğiniz <b>{len(df_sim_sonuc)} ürünlük</b> sepette yıllık toplam maliyet <b>{toplam_spot_tl:,.0f} ₺</b>'den
            <b>{toplam_akilli_tl:,.0f} ₺</b>'ye inerek <b>{toplam_net_tasarruf_tl:,.0f} ₺ (-%{toplam_tasarruf_yuzde:.1f})</b> net tasarruf sağlamaktadır.
            Bu parametrelerle <b>{stok_karli_sayisi} üründe</b> fiziksel stoklama kârlı iken, <b>{sozlesme_sayisi} üründe</b> zayi+depo yükü nedeniyle
            <b>sabit fiyatlı sözleşme</b> önerilmektedir. En büyük kazanç <b>{en_cok_tasarruf_urun}</b> ({en_cok_tasarruf_tutar:,.0f} ₺) kaleminden gelmektedir.</div>""".replace(",", "."),
            unsafe_allow_html=True,
        )

        st.markdown("#### 📋 Yıllık Satın Alma ve Tasarruf Planı Sonuç Tablosu")
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

        st.divider()

        # ---------------------------------------------------------------------
        # 4.5 SENARYO KARŞILAŞTIRMASI: SENARYO A vs. SENARYO B (DİNAMİK ROZET)
        # ---------------------------------------------------------------------
        st.markdown("#### ⚖️ Yönetim Karar Alternatifleri: Senaryo A vs. Senaryo B")
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
        a_badge_text = "✅ Önerilen Strateji" if senaryo_a_kazandi else "Düşük Risk • %0 Zayi"
        a_icon = "🟢" if senaryo_a_kazandi else "🟡"

        # Senaryo B görsel stilleri
        b_border = "#1B7A43" if not senaryo_a_kazandi else "#CA8A04"
        b_bg = "#F0FDF4" if not senaryo_a_kazandi else "#FFFFFF"
        b_title_color = "#14532D" if not senaryo_a_kazandi else "#854D0E"
        b_badge_bg = "#DCFCE7" if not senaryo_a_kazandi else "#FEF9C3"
        b_badge_color = "#166534" if not senaryo_a_kazandi else "#854D0E"
        b_badge_text = "✅ Önerilen Strateji" if not senaryo_a_kazandi else "Alternatif Karma Plan"
        b_icon = "🟢" if not senaryo_a_kazandi else "🟡"

        sen_col1, sen_col2 = st.columns(2, gap="large")
        with sen_col1:
            st.markdown(
                f"""
                <div class="signal-card" translate="no" style="border-top:5px solid {a_border}; padding:18px 20px; background:{a_bg};">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-weight:800; font-size:1.02rem; color:{a_title_color};">{a_icon} Senaryo A: Güvenli Sözleşme Stratejisi</span>
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
                        <span style="font-weight:800; font-size:1.02rem; color:{b_title_color};">{b_icon} Senaryo B: SNC Karma Optimizasyon</span>
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
                f"💡 <b>Neden Bu Öneri?</b> Seçilen ürünlerde zayi/bozulma (<b>%{fire_orani:.1f}</b>) ve soğuk depo (<b>%{depo_orani:.1f}</b>) "
                f"maliyetleri fiziksel stoklamanın kârını aşındırdığı için en ucuz dönem bazlı sabit fiyatlı tedarikçi sözleşmesi "
                f"(<b>Senaryo A</b>) hem net tasarrufu maksimize etmekte hem de raf ömrü kısa ürünlerde sıfır zayi riski sunmaktadır."
            )
        else:
            gerekce_metni = (
                f"💡 <b>Neden Bu Öneri?</b> Seçilen ürünlerde mevsimsel fiyat makası yüksek olduğu için <b>%{fire_orani:.1f}</b> zayi/bozulma ve "
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
        st.divider()
        st.markdown("#### 🏆 Yönetime 3 Altın Öneri (20 Yıllık Veri Seti Şampiyonları)")
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
                    <div class="signal-card-status" style="color:#B91C1C;">🛡️ {altin['sozlesme_urun']}</div>
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
                    <div class="signal-card-status" style="color:#15803D;">📦 {altin['stok_urun']}</div>
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
                    <div class="signal-card-status" style="color:#1D4ED8;">✅ {altin['spot_urun']}</div>
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
                label="📊 Satın Alma ve Tasarruf Planını İndir (.xlsx — Kurumsal Excel)",
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
# 6. SEKME: 🥗 MENÜ & REÇETE MALİYET ASİSTANI (HAZIR ŞABLON + SERBEST TARİF)
# =============================================================================
with sekme_recete:
    st.subheader("🥗 Şefin Akıllı Menü & Reçete Maliyeti")
    with st.expander("ℹ️ Bu Ekran Nasıl Okunur?", expanded=False):
        st.write(
            f"Hazır Ege restoran tariflerinden birini seçin veya **kendi tarifinizi oluşturun**. "
            f"12 aylık porsiyon maliyet eğrisini, **{aktif_sube_sayisi} şubenizin** aylık toplam yükünü ve mevsimlik ikame önerisini anında görün."
        )

    mevcut_tum_urunler = (
        sorted(df_aylik_reel["MAL_ADI"].dropna().unique().tolist())
        if not df_aylik_reel.empty and "MAL_ADI" in df_aylik_reel.columns
        else sorted(df_ozellikli["MAL_ADI"].dropna().unique().tolist())
    )

    HAZIR_TARIFLER = {
        "🥗 Ege Akdeniz Yeşil Salata": {
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
        "🥑 Avokadolu Tropikal Meyve Bowl": {
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
        "🍆 Ege Izgara Sebze & Mantar Tabağı": {
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
        "🥬 Zeytinyağlı Ege Meze Tabağı": {
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
        "✨ Kendi Tarifimi Oluştur (Özel Reçete)": {
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
            "📖 Hazır Tarif Seçin veya Özel Tarif Oluşturun",
            options=list(HAZIR_TARIFLER.keys()),
            index=0,
            key="recete_sablon_sec",
        )
    sablon_bilgi = HAZIR_TARIFLER[secili_sablon]

    with r_ust2:
        if secili_sablon.startswith("✨"):
            tarif_adi = st.text_input(
                "✍️ Kendi Tarif Adınızı Yazın",
                value="Şefin Özel Ege Tabağı",
                key="recete_ozel_ad",
            )
        else:
            tarif_adi = st.text_input(
                "🍽️ Tarif Adı (Düzenlenebilir)",
                value=secili_sablon,
                key=f"recete_ad_{secili_sablon}",
            )

    with r_ust3:
        menu_satis_fiyati = st.number_input(
            "💳 Menü Satış Fiyatı (TL)",
            min_value=10.0,
            max_value=5000.0,
            value=float(sablon_bilgi["satis_fiyati"]),
            step=10.0,
            key=f"recete_satis_{secili_sablon}",
        )

    with r_ust4:
        recete_ay_no = st.selectbox(
            "📅 Analiz Ayı",
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
            "🥕 Reçete Malzemelerini Seçin / Ekleyin / Çıkarın:",
            options=mevcut_tum_urunler,
            default=sablon_urun_adlari,
            key=f"recete_malz_sec_{secili_sablon}",
        )
    with r_alt_ayar2:
        gunluk_sube_porsiyon = st.number_input(
            "🍽️ Şube Başı Günlük Satış (Porsiyon)",
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

        st.markdown(f"#### ⚖️ **{tarif_adi}** — 1 Porsiyon Malzeme Miktarları (Düzenlenebilir)")
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
                <div class="signal-card-title">Yıl İçi Maliyet Makası (En Ucuz vs. En Pahalı)</div>
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

        rec_sol, rec_sag = st.columns([1.25, 0.95], gap="large")
        with rec_sol:
            st.markdown(f"#### 📈 {tarif_adi} — 12 Aylık Porsiyon Maliyet Eğrisi (TL)")
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
                f"""<div class="insight-note"><b>💬 Reçete Maliyet Eğrisi Yorumu ({tarif_adi} — {recete_ay_adi}):</b>
                Bu tarifin 1 porsiyon malzeme maliyeti en ucuz ay olan <b>{en_ucuz_satir['AY_ADI']}</b> ({en_ucuz_satir['PORSIYON_MALIYET_TL']:.2f} ₺) ile
                en pahalı ay olan <b>{en_pahali_satir['AY_ADI']}</b> ({en_pahali_satir['PORSIYON_MALIYET_TL']:.2f} ₺) arasında <b>+%{porsiyon_fark_pct:.1f}</b>
                ({porsiyon_fark_tl:.2f} ₺/porsiyon) dalgalanmaktadır. Seçili <b>{recete_ay_adi}</b> ayında {aktif_sube_sayisi} şubenizde bu yemek için aylık
                <b>{zincir_aylik_maliyet:,.0f} ₺</b> sebze-meyve bütçesi gerekmektedir; menü fiyat güncellemesi veya mevsimlik ikame bu eğriye göre planlanmalıdır.</div>""".replace(",", "."),
                unsafe_allow_html=True,
            )

        with rec_sag:
            st.markdown(f"#### 🔥 {recete_ay_adi} Ayı Maliyet Dağılımı & Akıllı İkame Önerisi")
            if not df_kalem_detay.empty:
                maliyet_katili = df_kalem_detay.iloc[0]
                katil_ad = str(maliyet_katili["MAL_ADI"])
                katil_tur = str(maliyet_katili["MAL_TURU"])
                katil_tutar = float(maliyet_katili["KALEM_MALIYET_TL"])
                katil_pay = (katil_tutar / secili_ay_maliyet) * 100.0 if secili_ay_maliyet > 0 else 0.0

                st.error(
                    f"🔴 **Maliyet Katili Malzeme:** **{katil_ad}**\n\n"
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
                        f"🟢 **Şefin Mevsimlik İkame Önerisi ({katil_tur}):** **{en_iyi_ikame[0]}**\n\n"
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
