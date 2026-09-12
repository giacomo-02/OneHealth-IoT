"""
Dashboard OneHealth Puglia -- Streamlit
Universita' del Salento

Grafica e funzionalita' invariate rispetto alla versione originale.
L'accesso ai dati non avviene piu' direttamente su MongoDB, ma tramite
l'API REST FastAPI (vedi api_client.py) collegata a PostgreSQL/SQLAlchemy.
Imposta l'indirizzo del backend con la variabile d'ambiente API_BASE_URL
(default: http://localhost:8000).

Avvio:
  streamlit run dashboard.py
"""

import json as _json
import math
import numpy as np
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

import api_client as api

try:
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")

# ---------------------------------------------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="OneHealth Puglia",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORI_GRAV = {
    "alta":  "#e74c3c",
    "media": "#f39c12",
    "bassa": "#2ecc71",
}

COLORI_CLASS = {
    "Eccellente":  "#2ecc71",
    "Buona":       "#3498db",
    "Sufficiente": "#f39c12",
    "Scarsa":      "#e74c3c",
}

NOMI_PROVINCE = {
    "FG": "Foggia", "BT": "BAT", "BA": "Bari",
    "BR": "Brindisi", "TA": "Taranto", "LE": "Lecce",
}

PROVINCE_LIST = ["FG", "BT", "BA", "BR", "TA", "LE"]


# ---------------------------------------------------------------------------
# ACCESSO DATI: ora tramite l'API FastAPI (api_client.py) invece di MongoDB
# diretto. Vedi api_client.py per l'implementazione delle chiamate REST
# verso il backend PostgreSQL/SQLAlchemy.
# ---------------------------------------------------------------------------
# GEOCODING (Nominatim / OpenStreetMap)
# ---------------------------------------------------------------------------
def geocodifica_nominatim(testo):
    q   = urllib.parse.quote(testo + ", Puglia, Italia")
    url = (f"https://nominatim.openstreetmap.org/search"
           f"?q={q}&format=json&limit=1&countrycodes=it")
    req = urllib.request.Request(url, headers={"User-Agent": "OneHealth-Puglia/1.0"})
    with urllib.request.urlopen(req, timeout=8) as r:
        data = _json.loads(r.read())
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", "")
    return None, None, ""


# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("OneHealth Puglia")
    st.caption("Monitoraggio qualita' idrica costiera")
    st.divider()

    refresh_sec = st.selectbox(
        "Auto-refresh (boe)",
        options=[5, 10, 30, 60],
        index=2,
        format_func=lambda x: f"ogni {x} secondi",
    )
    ore_storia = st.selectbox(
        "Finestra temporale",
        options=[1, 6, 24, 72],
        index=1,
        format_func=lambda x: f"ultime {x} ore",
    )
    province_sel = st.multiselect(
        "Province (boe)",
        options=PROVINCE_LIST,
        default=PROVINCE_LIST,
        format_func=lambda x: f"{x} — {NOMI_PROVINCE[x]}",
    )
    tipo_sel = st.multiselect(
        "Tipo boa",
        options=["fissa", "deriva"],
        default=["fissa", "deriva"],
    )
    st.divider()
    st.caption("Soglie: D.Lgs 116/2008 + WHO")


# ---------------------------------------------------------------------------
# FUNZIONI BOE
# ---------------------------------------------------------------------------
def carica_dati_boe(ore, province, tipi):
    return api.carica_dati_boe(ore, province, tipi)


def docs_to_df(docs):
    if not docs:
        return pd.DataFrame()
    df_raw = pd.DataFrame(docs)
    df_raw["timestamp"] = pd.to_datetime(df_raw["timestamp"])
    sensori_flat = pd.json_normalize(df_raw["sensori"].tolist())
    return pd.concat(
        [df_raw.drop(columns=["sensori", "alert"], errors="ignore"), sensori_flat],
        axis=1,
    )


def downsample_grafici(df, punti_per_boa=50, finestra_min=60):
    """Prepara i dati per i grafici SENZA toccare il database (lo storico resta tutto).
    - mostra solo la finestra recente (ultimi `finestra_min` minuti): i dati vecchi
      restano su MongoDB ma non appesantiscono i grafici;
    - riduce a ~punti_per_boa punti per boa (bucket adattivo) -> redraw leggero,
      niente flash bianco anche col database pieno di giorni di dati."""
    if df.empty or "timestamp" not in df.columns or "id_boa" not in df.columns:
        return df
    d = df.sort_values("timestamp").copy()
    if finestra_min:
        taglio = d["timestamp"].max() - pd.Timedelta(minutes=finestra_min)
        d = d[d["timestamp"] >= taglio]
    span = (d["timestamp"].max() - d["timestamp"].min()).total_seconds()
    if span <= 0:
        return d
    bucket_sec = max(10, int(span / punti_per_boa))
    d["_bucket"] = d["timestamp"].dt.floor(f"{bucket_sec}s")
    d = d.drop_duplicates(subset=["id_boa", "_bucket"], keep="last")
    return d.drop(columns="_bucket").sort_values("timestamp")


def carica_ultime_boe(tipo_boa=None):
    return api.carica_ultime_boe(tipo_boa)


# ---------------------------------------------------------------------------
# FUNZIONI ARPA
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def anni_disponibili_arpa():
    return api.anni_disponibili_arpa()


def carica_dati_arpa(province=None, anno=None):
    return api.carica_dati_arpa(province, anno)


def arpa_riepilogo_province(docs):
    prov_rows = {}
    for doc in docs:
        p = doc.get("provincia", "?")
        if p not in prov_rows:
            prov_rows[p] = {"Punti": 0, "Eccellente": 0, "Buona": 0, "Sufficiente": 0, "Scarsa": 0, "Alert": 0}
        prov_rows[p]["Punti"] += 1
        cls = doc.get("classificazione", "")
        if cls in prov_rows[p]:
            prov_rows[p][cls] += 1
        if doc.get("ha_alert"):
            prov_rows[p]["Alert"] += 1
    return prov_rows


# ---------------------------------------------------------------------------
# FRAGMENT BOE (si aggiorna in automatico)
# ---------------------------------------------------------------------------
@st.fragment(run_every=refresh_sec)
def sezione_live():
    try:
        docs, tot_db, n_alert, fallback = carica_dati_boe(ore_storia, province_sel, tipo_sel)
    except Exception as e:
        st.error(f"API non raggiungibile: {e}")
        return

    df = docs_to_df(docs)

    st.caption(f"Aggiornamento: {datetime.now().strftime('%H:%M:%S')} | refresh ogni {refresh_sec}s")
    if fallback:
        st.warning(
            f"⏳ Nessuna lettura nelle ultime {ore_storia}h — mostro le ultime "
            f"{len(docs)} letture disponibili. (Controlla che il simulatore sia attivo.)"
        )
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Totale nel DB",         f"{tot_db:,}")
    k2.metric(f"Ultime {ore_storia}h", f"{len(docs):,}")
    k3.metric("Alert nel periodo",     f"{n_alert:,}")
    if not df.empty:
        cnts = df["classificazione"].value_counts()
        k4.metric("Eccellente / Buona",   f"{cnts.get('Eccellente',0)} / {cnts.get('Buona',0)}")
        k5.metric("Sufficiente / Scarsa", f"{cnts.get('Sufficiente',0)} / {cnts.get('Scarsa',0)}")

    st.divider()
    col_feed, col_chart = st.columns([1, 2])

    with col_feed:
        st.subheader("Feed in arrivo")
        if not df.empty:
            cols_show = ["timestamp", "id_boa", "comune", "classificazione",
                         "ph", "temperatura_c", "ecoli_ufc_100ml",
                         "enterococchi_ufc_100ml", "clorofilla_a_ug_l"]
            cols_show = [c for c in cols_show if c in df.columns]
            display = df[cols_show].head(35).copy()
            display["timestamp"] = display["timestamp"].dt.strftime("%H:%M:%S")
            col_labels = {"timestamp": "Ora", "id_boa": "Boa", "comune": "Comune",
                          "classificazione": "Qualita'", "ph": "pH", "temperatura_c": "T°C",
                          "ecoli_ufc_100ml": "E.coli", "enterococchi_ufc_100ml": "Entero.",
                          "clorofilla_a_ug_l": "Cloro."}
            display.columns = [col_labels[c] for c in cols_show]

            st.dataframe(display, use_container_width=True, height=420)
        else:
            st.info("Nessun dato. Avvia il simulatore.")

    with col_chart:
        if not df.empty:
            df_plot = downsample_grafici(df)

            fig = px.line(df_plot, x="timestamp", y="ph", color="provincia",
                          title="pH nel tempo", height=260,
                          labels={"ph": "pH", "timestamp": "", "provincia": "Prov."},
                          color_discrete_sequence=px.colors.qualitative.Set2)
            fig.add_hline(y=7.5, line_dash="dash", line_color="orange")
            fig.add_hline(y=8.5, line_dash="dash", line_color="orange")
            fig.update_yaxes(range=[7.4, 8.7])
            fig.update_layout(margin=dict(t=35, b=5, l=0, r=0), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_plot, x="timestamp", y="ossigeno_disciolto_mg_l", color="provincia",
                          title="Ossigeno disciolto (mg/L)", height=260,
                          labels={"ossigeno_disciolto_mg_l": "O2", "timestamp": "", "provincia": "Prov."},
                          color_discrete_sequence=px.colors.qualitative.Set2)
            fig.add_hline(y=7.0, line_dash="dash", line_color="orange")
            fig.update_yaxes(range=[5, 10.5])
            fig.update_layout(margin=dict(t=35, b=5, l=0, r=0), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_plot, x="timestamp", y="ecoli_ufc_100ml", color="provincia",
                          title="E.coli (UFC/100mL)", height=260,
                          labels={"ecoli_ufc_100ml": "E.coli", "timestamp": "", "provincia": "Prov."},
                          color_discrete_sequence=px.colors.qualitative.Set2)
            fig.add_hline(y=200,  line_dash="dash", line_color="orange")
            fig.add_hline(y=1000, line_dash="dash", line_color="red")
            fig.update_yaxes(range=[0, 1100])
            fig.update_layout(margin=dict(t=35, b=5, l=0, r=0), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            if "enterococchi_ufc_100ml" in df_plot.columns:
                fig = px.line(df_plot, x="timestamp", y="enterococchi_ufc_100ml", color="provincia",
                              title="Enterococchi (UFC/100mL)", height=260,
                              labels={"enterococchi_ufc_100ml": "Entero.", "timestamp": "", "provincia": "Prov."},
                              color_discrete_sequence=px.colors.qualitative.Set1)
                fig.add_hline(y=100, line_dash="dash", line_color="orange")
                fig.add_hline(y=200, line_dash="dash", line_color="red")
                fig.update_yaxes(range=[0, 220])
                fig.update_layout(margin=dict(t=35, b=5, l=0, r=0), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Parametri ambientali aggiuntivi")
    if not df.empty:
        df_plot2 = downsample_grafici(df)

        def grafico(col, campo, titolo, label, soglie, palette, y_range=None):
            if campo not in df_plot2.columns:
                return
            with col:
                fig = px.line(df_plot2, x="timestamp", y=campo, color="provincia",
                              title=titolo, height=300,
                              labels={campo: label, "timestamp": "", "provincia": "Prov."},
                              color_discrete_sequence=palette)
                for livello, colore in soglie:
                    fig.add_hline(y=livello, line_dash="dash", line_color=colore)
                if y_range is not None:
                    fig.update_yaxes(range=y_range)   # asse fisso: niente salto all'aggiornamento
                fig.update_layout(margin=dict(t=35, b=5, l=0, r=0), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        pal_fis  = px.colors.qualitative.Set2
        pal_nut  = px.colors.qualitative.Pastel
        pal_met  = px.colors.qualitative.Dark2
        pal_red  = px.colors.qualitative.Vivid

        st.caption("Parametri fisici")
        r1a, r1b, r1c = st.columns(3)
        grafico(r1a, "temperatura_c",       "Temperatura (°C)",         "T°C",   [(26,"orange"),(30,"red")],   pal_fis, y_range=[19, 25])
        grafico(r1b, "torbidita_ntu",       "Torbidità (NTU)",          "NTU",   [(15,"orange"),(50,"red")],   pal_fis, y_range=[0, 20])
        grafico(r1c, "conducibilita_ms_cm", "Conducibilità (mS/cm)",    "mS/cm", [],                           pal_fis, y_range=[42, 60])

        st.caption("Nutrienti")
        r2a, r2b, r2c = st.columns(3)
        grafico(r2a, "nitrati_mg_l",    "Nitrati (mg/L)",     "NO3",  [(25,"orange"),(50,"red")],  pal_nut)
        grafico(r2b, "fosfati_mg_l",    "Fosfati (mg/L)",     "PO4",  [(0.5,"orange"),(2,"red")],  pal_nut)
        grafico(r2c, "clorofilla_a_ug_l","Clorofilla-a (µg/L)","Cloro.",[(10,"orange"),(30,"red")],pal_nut)

        st.caption("Metalli pesanti")
        r3a, r3b, r3c = st.columns(3)
        grafico(r3a, "piombo_ug_l",   "Piombo (µg/L)",   "Pb", [(10,"orange"),(25,"red")],  pal_met)
        grafico(r3b, "mercurio_ug_l", "Mercurio (µg/L)", "Hg", [(1.0,"orange"),(3.0,"red")], pal_met)
        grafico(r3c, "arsenico_ug_l", "Arsenico (µg/L)", "As", [(5.0,"orange"),(10,"red")],  pal_met)

        st.caption("Metalli pesanti / Redox")
        r4a, r4b, _ = st.columns(3)
        grafico(r4a, "cadmio_ug_l", "Cadmio (µg/L)",          "Cd",     [(0.5,"orange"),(2.0,"red")], pal_red)
        grafico(r4b, "orp_mv",      "ORP — Potenziale Redox (mV)", "mV", [(150,"orange"),(100,"red")], pal_red)


# ---------------------------------------------------------------------------
# TITOLO + TAB
# ---------------------------------------------------------------------------
st.title("OneHealth Puglia — Qualita' Idrica Costiera")

@st.fragment(run_every=30)
def badge_segnalazioni():
    try:
        n = api.conta_segnalazioni_nuove()
        if n > 0:
            st.markdown(
                f'<div style="display:flex;justify-content:flex-end;margin-bottom:6px;">'
                f'<span style="background:#e74c3c;color:white;border-radius:20px;'
                f'padding:5px 14px;font-size:14px;font-weight:700;'
                f'box-shadow:0 2px 6px rgba(231,76,60,0.4);">'
                f'🔔 {n} nuov{"a" if n==1 else "e"} segnalazion{"e" if n==1 else "i"}'
                f'</span></div>',
                unsafe_allow_html=True,
            )
    except Exception:
        pass

badge_segnalazioni()

try:
    _n = api.conta_segnalazioni_nuove()
    _label_seg = f"Segnalazioni  🔴 {_n}" if _n > 0 else "Segnalazioni"
except Exception:
    _label_seg = "Segnalazioni"

@st.fragment(run_every=15)
def sezione_criticita():
    st.divider()
    st.subheader("⚠️ Criticità rilevate")
    st.caption(
        "Alert generati al superamento delle soglie sui parametri (E.coli, "
        "enterococchi, metalli pesanti, nitrati), con posizione, data/ora e tipo."
    )
    try:
        alerts = api.alerts_recenti(limit=300)
    except Exception as e:
        st.caption(f"Storico criticità non disponibile: {e}")
        return

    # Notifica dei nuovi alert comparsi dall'ultimo controllo
    _max_id = max((a.get("id", 0) for a in alerts), default=0)
    _last = st.session_state.get("_last_alert_id")
    if _last is None:
        st.session_state["_last_alert_id"] = _max_id
    elif _max_id > _last:
        nuovi = [a for a in alerts if a.get("id", 0) > _last]
        for a in nuovi[:5]:
            icona = "🔴" if a.get("livello") == "critico" else "🟠"
            st.toast(f"{icona} {a.get('nome_boa','')}: {a.get('parametri','')}", icon="⚠️")
        st.session_state["_last_alert_id"] = _max_id

    n_crit = sum(1 for a in alerts if a.get("livello") == "critico")
    n_all  = sum(1 for a in alerts if a.get("livello") == "allerta")
    c1, c2, c3 = st.columns(3)
    c1.metric("Criticità totali", f"{len(alerts):,}")
    c2.metric("🔴 Critiche", f"{n_crit:,}")
    c3.metric("🟠 Allerte", f"{n_all:,}")

    if not alerts:
        st.info("Nessuna criticità registrata.")
        return

    righe = []
    for a in alerts:
        ts = a.get("timestamp")
        righe.append({
            "Data":      ts.strftime("%d/%m/%Y") if ts else "",
            "Ora":       ts.strftime("%H:%M:%S") if ts else "",
            "Livello":   "🔴 Critico" if a.get("livello") == "critico" else "🟠 Allerta",
            "Boa":       a.get("nome_boa", ""),
            "Comune":    a.get("comune", ""),
            "Criticità": a.get("parametri", ""),
            "Lat":       round(a["latitudine"], 4) if a.get("latitudine") is not None else None,
            "Lon":       round(a["longitudine"], 4) if a.get("longitudine") is not None else None,
        })
    st.dataframe(pd.DataFrame(righe), use_container_width=True, hide_index=True, height=360)


tab_boe, tab_arpa, tab_san, tab_seg, tab_ai = st.tabs([
    "Boe GPS (live)", "ARPA Balneazione", "Dati Sanitari", _label_seg, "Analisi AI",
])


# ===========================================================================
# TAB 1 — BOE GPS
# ===========================================================================
with tab_boe:
    sezione_live()

    st.divider()

    col_titolo, col_btn = st.columns([5, 1])
    col_titolo.subheader("Posizione boe (ultima lettura)")
    aggiorna_mappa = col_btn.button("Aggiorna mappa", use_container_width=True)

    if "ultime_boe" not in st.session_state or aggiorna_mappa:
        try:
            st.session_state["ultime_boe"] = carica_ultime_boe()
        except Exception:
            st.session_state["ultime_boe"] = []

    ultime = st.session_state.get("ultime_boe", [])
    col_map, col_info = st.columns([3, 2])

    with col_map:
        _mc = st.session_state.get("boe_map_center", [40.6, 17.0])
        _mz = st.session_state.get("boe_map_zoom", 7)
        m = folium.Map(location=_mc, zoom_start=_mz, tiles="CartoDB positron")
        m._id = "onehealthboemap"

        for doc in ultime:
            lat = doc.get("latitudine")
            lon = doc.get("longitudine")
            if not lat or not lon:
                continue
            cls      = doc.get("classificazione", "")
            sensori  = doc.get("sensori", {})
            alerts   = doc.get("alert", [])
            colore   = COLORI_CLASS.get(cls, "#95a5a6")
            tipo_boa = doc.get("tipo_boa", "fissa")

            if tipo_boa == "fissa":
                icon_html = (
                    f'<div style="width:18px;height:18px;border-radius:50%;'
                    f'background:{colore};border:2px solid rgba(255,255,255,0.85);'
                    f'box-shadow:1px 1px 4px rgba(0,0,0,0.35);"></div>'
                )
            else:
                icon_html = (
                    f'<div style="width:18px;height:18px;border-radius:50%;'
                    f'background:{colore};border:2px solid rgba(255,255,255,0.85);'
                    f'box-shadow:1px 1px 4px rgba(0,0,0,0.35);'
                    f'display:flex;align-items:center;justify-content:center;">'
                    f'<div style="width:6px;height:6px;border-radius:50%;'
                    f'background:white;opacity:0.95;"></div></div>'
                )

            popup_html = f"""
            <div style='font-family:sans-serif;font-size:12px;min-width:210px'>
                <b>{doc.get('nome_boa','')}</b><br>
                {doc.get('comune','')} ({doc.get('provincia','')})<br>
                <i>Tipo: {doc.get('tipo_boa','')}</i>
                <hr style='margin:4px 0'>
                pH: <b>{sensori.get('ph','—')}</b> &nbsp;|&nbsp;
                T: <b>{sensori.get('temperatura_c','—')}°C</b><br>
                O2: <b>{sensori.get('ossigeno_disciolto_mg_l','—')} mg/L</b> &nbsp;|&nbsp;
                Cond.: <b>{sensori.get('conducibilita_ms_cm','—')} mS/cm</b><br>
                <hr style='margin:4px 0'>
                E.coli: <b>{sensori.get('ecoli_ufc_100ml','—')} UFC/100mL</b><br>
                Enterococchi: <b>{sensori.get('enterococchi_ufc_100ml','—')} UFC/100mL</b><br>
                Nitrati: <b>{sensori.get('nitrati_mg_l','—')} mg/L</b> &nbsp;|&nbsp;
                Fosfati: <b>{sensori.get('fosfati_mg_l','—')} mg/L</b><br>
                Clorofilla-a: <b>{sensori.get('clorofilla_a_ug_l','—')} µg/L</b><br>
                Piombo: <b>{sensori.get('piombo_ug_l','—')} µg/L</b> &nbsp;|&nbsp;
                Mercurio: <b>{sensori.get('mercurio_ug_l','—')} µg/L</b><br>
                Arsenico: <b>{sensori.get('arsenico_ug_l','—')} µg/L</b> &nbsp;|&nbsp;
                Cadmio: <b>{sensori.get('cadmio_ug_l','—')} µg/L</b><br>
                ORP: <b>{sensori.get('orp_mv','—')} mV</b>
                <hr style='margin:4px 0'>
                Qualita': <b style='color:{colore}'>{cls}</b><br>
                {'<br>'.join(f'⚠️ {a}' for a in alerts) if alerts else 'Nessun alert'}
                <hr style='margin:4px 0'>
                <span style='color:#64748b'>📍 {lat:.5f}, {lon:.5f}</span>
            </div>
            """
            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(html=icon_html, icon_size=(18, 18), icon_anchor=(9, 9)),
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=f"{doc.get('id_boa','')} — {cls}",
            ).add_to(m)

        legenda = """
        <div style="position:fixed;bottom:20px;left:20px;z-index:1000;
                    background-color:#ffffff!important;color:#1f2937!important;
                    color-scheme:light;padding:10px 14px;border-radius:8px;font-size:12px;
                    box-shadow:2px 2px 8px rgba(0,0,0,0.25);font-family:sans-serif">
            <b style="color:#1f2937!important">Classificazione D.Lgs 116/2008</b><br>
            <span style="color:#2ecc71!important;font-size:16px">&#9679;</span>
            <span style="color:#1f2937!important">Eccellente</span><br>
            <span style="color:#3498db!important;font-size:16px">&#9679;</span>
            <span style="color:#1f2937!important">Buona</span><br>
            <span style="color:#f39c12!important;font-size:16px">&#9679;</span>
            <span style="color:#1f2937!important">Sufficiente</span><br>
            <span style="color:#e74c3c!important;font-size:16px">&#9679;</span>
            <span style="color:#1f2937!important">Scarsa</span><br>
            <hr style="margin:5px 0">
            <b style="color:#1f2937!important">Tipo boa</b><br>
            <span style="display:inline-block;width:14px;height:14px;border-radius:50%;
                         background:#888;border:2px solid rgba(255,255,255,0.85);
                         vertical-align:middle;margin-right:4px"></span>
            <span style="color:#1f2937!important">Fissa</span><br>
            <span style="display:inline-block;width:14px;height:14px;border-radius:50%;
                         background:#888;border:2px solid rgba(255,255,255,0.85);
                         vertical-align:middle;margin-right:4px;position:relative">
              <span style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                           width:4px;height:4px;border-radius:50%;background:white;
                           display:block"></span>
            </span>
            <span style="color:#1f2937!important">Deriva</span>
        </div>"""
        m.get_root().html.add_child(folium.Element(legenda))

        _map_out = st_folium(m, height=440, use_container_width=True,
                             returned_objects=["center", "zoom"],
                             key="boe_live_map")

        if _map_out:
            if _map_out.get("center"):
                st.session_state["boe_map_center"] = [
                    _map_out["center"]["lat"],
                    _map_out["center"]["lng"],
                ]
            if _map_out.get("zoom") is not None:
                st.session_state["boe_map_zoom"] = _map_out["zoom"]

    with col_info:
        st.caption("Clicca su un pallino per i dettagli della boa.")
        if not ultime:
            st.info("Nessun dato. Avvia il simulatore e clicca 'Aggiorna mappa'.")

    sezione_criticita()


# ===========================================================================
# TAB 2 — ARPA BALNEAZIONE
# ===========================================================================
with tab_arpa:
    st.subheader("Punti di monitoraggio ARPA Puglia — Acque di balneazione")
    st.caption("Fonte: ARPA Puglia | D.Lgs 116/2008 | Parametri: E.coli + Enterococchi intestinali")

    # Filtri
    try:
        _anni_arpa = anni_disponibili_arpa()
    except Exception:
        _anni_arpa = []
    _opzioni_anno = ["Tutti (ultima lettura)"] + [str(a) for a in _anni_arpa]

    col_f1, col_f2, col_f3 = st.columns([3, 2, 1])
    with col_f1:
        prov_arpa = st.multiselect(
            "Filtra province",
            options=PROVINCE_LIST,
            default=PROVINCE_LIST,
            format_func=lambda x: f"{x} — {NOMI_PROVINCE[x]}",
            key="prov_arpa",
        )
    with col_f2:
        anno_arpa_sel = st.selectbox(
            "Anno", options=_opzioni_anno, index=0, key="anno_arpa",
        )
    with col_f3:
        aggiorna_arpa = st.button("Aggiorna", use_container_width=True, key="btn_arpa")

    _anno_q = None if anno_arpa_sel.startswith("Tutti") else int(anno_arpa_sel)

    # Ricarica se cambia l'anno o si preme Aggiorna
    if ("arpa_docs" not in st.session_state
            or aggiorna_arpa
            or st.session_state.get("arpa_anno_corrente") != anno_arpa_sel):
        try:
            arpa_docs, arpa_tot, arpa_n_alert = carica_dati_arpa(prov_arpa, _anno_q)
            st.session_state["arpa_docs"]    = arpa_docs
            st.session_state["arpa_tot"]     = arpa_tot
            st.session_state["arpa_n_alert"] = arpa_n_alert
            st.session_state["arpa_anno_corrente"] = anno_arpa_sel
        except Exception as e:
            st.error(f"API non raggiungibile: {e}")
            st.session_state["arpa_docs"]    = []
            st.session_state["arpa_tot"]     = 0
            st.session_state["arpa_n_alert"] = 0

    if _anno_q:
        st.caption(f"Mostrando l'ultima misurazione di ogni punto nel **{_anno_q}**.")
    else:
        st.caption("Mostrando l'ultima misurazione disponibile di ogni punto (tutti gli anni).")

    arpa_docs    = st.session_state.get("arpa_docs", [])
    arpa_tot     = st.session_state.get("arpa_tot", 0)
    arpa_n_alert = st.session_state.get("arpa_n_alert", 0)

    # Filtra localmente per provincia (per evitare riquery al cambio filtro)
    docs_vis = [d for d in arpa_docs if not prov_arpa or d.get("provincia") in prov_arpa]

    # KPI
    cnts_a = {"Eccellente": 0, "Buona": 0, "Sufficiente": 0, "Scarsa": 0}
    for d in docs_vis:
        cls = d.get("classificazione", "")
        if cls in cnts_a:
            cnts_a[cls] += 1

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Punti monitorati",     f"{len(docs_vis):,}")
    k2.metric("Eccellente",           f"{cnts_a['Eccellente']:,}")
    k3.metric("Buona",                f"{cnts_a['Buona']:,}")
    k4.metric("Sufficiente / Scarsa", f"{cnts_a['Sufficiente']} / {cnts_a['Scarsa']}")
    k5.metric("Punti con alert",      f"{sum(1 for d in docs_vis if d.get('ha_alert')):,}")

    st.divider()
    col_mappa, col_tabella = st.columns([3, 2])

    # Mappa ARPA
    with col_mappa:
        m2 = folium.Map(location=[40.6, 17.0], zoom_start=7, tiles="CartoDB positron")

        for doc in docs_vis:
            lat = doc.get("latitudine")
            lon = doc.get("longitudine")
            if not lat or not lon:
                continue
            cls     = doc.get("classificazione", "")
            colore  = COLORI_CLASS.get(cls, "#95a5a6")
            sensori = doc.get("sensori", {})
            alerts  = doc.get("alert", [])

            popup_html = f"""
            <div style='font-family:sans-serif;font-size:12px;min-width:190px'>
                <b>{doc.get('denominazione','')}</b><br>
                {doc.get('comune','')} ({doc.get('provincia','')})<br>
                <i>{doc.get('codice','')}</i>
                <hr style='margin:4px 0'>
                E.coli: <b>{sensori.get('ecoli_ufc_100ml','—')} UFC/100mL</b><br>
                Enterococchi: <b>{sensori.get('enterococchi_ufc_100ml','—')} UFC/100mL</b>
                <hr style='margin:4px 0'>
                Qualita': <b style='color:{colore}'>{cls}</b><br>
                {'<br>'.join(f'[!] {a}' for a in alerts) if alerts else 'Nessun alert'}
            </div>
            """
            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                color=colore,
                fill=True,
                fill_color=colore,
                fill_opacity=0.80,
                popup=folium.Popup(popup_html, max_width=240),
                tooltip=f"{doc.get('comune','')} — {cls}",
            ).add_to(m2)

        legenda2 = """
        <div style="position:fixed;bottom:20px;left:20px;z-index:1000;
                    background-color:#ffffff!important;color:#1f2937!important;
                    color-scheme:light;padding:10px 14px;border-radius:8px;font-size:12px;
                    box-shadow:2px 2px 8px rgba(0,0,0,0.25);font-family:sans-serif">
            <b style="color:#1f2937!important">ARPA — D.Lgs 116/2008</b><br>
            <span style="color:#2ecc71!important;font-size:16px">&#9679;</span>
            <span style="color:#1f2937!important">Eccellente</span><br>
            <span style="color:#3498db!important;font-size:16px">&#9679;</span>
            <span style="color:#1f2937!important">Buona</span><br>
            <span style="color:#f39c12!important;font-size:16px">&#9679;</span>
            <span style="color:#1f2937!important">Sufficiente</span><br>
            <span style="color:#e74c3c!important;font-size:16px">&#9679;</span>
            <span style="color:#1f2937!important">Scarsa</span>
        </div>"""
        m2.get_root().html.add_child(folium.Element(legenda2))
        st_folium(m2, height=460, use_container_width=True)

    # Tabella per provincia + alert
    with col_tabella:
        st.subheader("Riepilogo per provincia")
        prov_rows = arpa_riepilogo_province(docs_vis)
        if prov_rows:
            df_prov = pd.DataFrame(
                sorted(prov_rows.items(), key=lambda x: x[0]),
                columns=["Provincia", "dati"]
            )
            df_prov = pd.DataFrame([
                {"Prov.": p, **v} for p, v in sorted(prov_rows.items())
            ])
            st.dataframe(df_prov.set_index("Prov."), use_container_width=True)

        st.divider()
        st.subheader("Punti con alert")
        alert_docs = [d for d in docs_vis if d.get("ha_alert")]
        if alert_docs:
            df_alert = pd.DataFrame([{
                "Comune":   d.get("comune", ""),
                "Prov.":    d.get("provincia", ""),
                "Stazione": d.get("denominazione", ""),
                "E.coli":   d.get("sensori", {}).get("ecoli_ufc_100ml", ""),
                "Entero.":  d.get("sensori", {}).get("enterococchi_ufc_100ml", ""),
                "Classe":   d.get("classificazione", ""),
            } for d in alert_docs])

            st.dataframe(df_alert, use_container_width=True, height=300)
        else:
            st.success("Nessun punto con alert nel set filtrato.")


# ===========================================================================
# TAB 3 — DATI SANITARI
# ===========================================================================
LABEL_TIPO_SAN = {
    "dimissioni": {"titolo": "Dimissioni ospedaliere", "asse_y": "Tasso dimissioni (x 100.000 ab.)"},
    "mortalita":  {"titolo": "Mortalità",              "asse_y": "Tasso mortalità (x 100.000 ab.)"},
}

with tab_san:
    st.subheader("Dati Sanitari — Health for All (Istat)")
    st.caption("Tassi per 100.000 abitanti | Province pugliesi | 1999-2024")

    col_fs1, col_fs2, col_fs3, col_fs4 = st.columns([2, 3, 2, 1])
    with col_fs1:
        tipo_san = st.radio(
            "Tipologia",
            options=["dimissioni", "mortalita"],
            format_func=lambda x: LABEL_TIPO_SAN[x]["titolo"],
            horizontal=True,
            key="tipo_san_radio",
        )
    with col_fs2:
        try:
            if "san_patologie" not in st.session_state:
                st.session_state["san_patologie"] = sorted(
                    api.patologie_sanitarie()
                )
            _pat_opts = st.session_state["san_patologie"]
        except Exception:
            _pat_opts = []
        pat_san = st.selectbox(
            "Patologia",
            options=_pat_opts or ["—"],
            format_func=lambda x: x.capitalize(),
            key="pat_san_sel",
        )
    with col_fs3:
        sesso_san = st.radio(
            "Sesso",
            options=["M+F", "M", "F"],
            format_func=lambda x: {"M+F": "M+F (media)", "M": "Maschi", "F": "Femmine"}[x],
            horizontal=True,
            key="sesso_san_radio",
        )
    with col_fs4:
        aggiorna_san = st.button("Aggiorna", use_container_width=True, key="btn_san")

    lbl = LABEL_TIPO_SAN[tipo_san]
    cache_key = f"sanitari_{tipo_san}_{pat_san}"
    if cache_key not in st.session_state or aggiorna_san:
        try:
            st.session_state[cache_key] = api.dati_sanitari(tipo_san, pat_san)
        except Exception as e:
            st.error(f"API non raggiungibile: {e}")
            st.session_state[cache_key] = []

    san_docs = st.session_state.get(cache_key, [])

    if not san_docs:
        st.info("Nessun dato. Importa il dataset con:  python3 sanitari.py hfa_dataset.csv --clear")
    else:
        df_san = pd.DataFrame(san_docs)

        if sesso_san == "M+F":
            df_prov = (
                df_san.groupby(["anno", "provincia", "provincia_nome"], as_index=False)
                ["valore"].mean()
            )
        else:
            df_prov = df_san[df_san["sesso"] == sesso_san]

        _sesso_lbl = {"M+F": "M+F (media)", "M": "maschi", "F": "femmine"}[sesso_san]

        # Grafico andamento storico
        fig = px.line(
            df_prov, x="anno", y="valore", color="provincia_nome",
            title=f"{lbl['titolo']} — {pat_san} ({_sesso_lbl})",
            labels={"valore": lbl["asse_y"], "anno": "Anno", "provincia_nome": "Provincia"},
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Set1,
        )
        fig.add_vrect(x0=2020, x1=2021, fillcolor="gray", opacity=0.15,
                      annotation_text="COVID-19", annotation_position="top left")
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        # Confronto M vs F per l'anno più recente
        anno_max = int(df_san["anno"].max())
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            df_latest = df_prov[df_prov["anno"] == anno_max].sort_values("valore", ascending=False)
            fig2 = px.bar(
                df_latest, x="provincia_nome", y="valore", color="provincia_nome",
                title=f"Confronto province — {anno_max} ({_sesso_lbl})",
                labels={"valore": lbl["asse_y"], "provincia_nome": "Provincia"},
                color_discrete_sequence=px.colors.qualitative.Set2,
                text_auto=".2f",
            )
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        with col_g2:
            df_mf = df_san[df_san["anno"] == anno_max]
            fig3 = px.bar(
                df_mf, x="provincia_nome", y="valore", color="sesso",
                barmode="group",
                title=f"Maschi vs Femmine — {anno_max}",
                labels={"valore": lbl["asse_y"], "provincia_nome": "Provincia", "sesso": "Sesso"},
                color_discrete_map={"M": "#3498db", "F": "#e74c3c"},
                text_auto=".1f",
            )
            st.plotly_chart(fig3, use_container_width=True)

        # Tabella riepilogo
        st.subheader("Tabella dati completa")
        df_pivot = df_prov.pivot_table(
            index="anno", columns="provincia_nome", values="valore"
        ).sort_index(ascending=False)
        st.dataframe(df_pivot.round(2), use_container_width=True, height=350)


# ===========================================================================
# TAB 4 — SEGNALAZIONI UTENTI
# ===========================================================================
@st.fragment(run_every=30)
def sezione_segnalazioni():
    st.subheader("Segnalazioni utenti — Acque contaminate")
    st.caption("Segnalazioni inviate dai cittadini tramite l'app mobile")

    # Pannello missioni boe
    try:
        _miss_att = api.missioni_attive()
        _miss_ok = api.missioni_completate_count()
        if _miss_att:
            righe = []
            for m in _miss_att:
                if m["stato"] == "attiva":
                    righe.append(
                        f"🚢 **{m['nome_boa']}** in rotta verso segnalazione"
                        f" ({m['target_lat']:.4f}, {m['target_lon']:.4f})"
                        f" [{m.get('distanza_km', '?')} km]"
                    )
                else:
                    righe.append(
                        f"🔄 **{m['nome_boa']}** ritorno alla posizione base"
                    )
            st.info("  |  ".join(righe))
        if _miss_ok:
            st.success(f"✅ {_miss_ok} missione/i completate con ritorno a base")
    except Exception:
        pass

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_stato = st.multiselect(
            "Stato",
            options=["nuova", "presa_in_carico", "chiusa"],
            default=["nuova", "presa_in_carico"],
            key="seg_stato",
        )
    with col_f2:
        filtro_grav = st.multiselect(
            "Gravità",
            options=["alta", "media", "bassa"],
            default=["alta", "media", "bassa"],
            key="seg_grav",
        )
    try:
        seg_docs = api.lista_segnalazioni(stati=filtro_stato, limit=300)
    except Exception as e:
        st.error(f"API non raggiungibile: {e}")
        seg_docs = []

    seg_vis = [d for d in seg_docs if not filtro_grav or d.get("gravita") in filtro_grav]

    # KPI
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Totale",          f"{len(seg_docs):,}")
    k2.metric("Nuove",           f"{sum(1 for d in seg_docs if d.get('stato')=='nuova'):,}")
    k3.metric("Prese in carico", f"{sum(1 for d in seg_docs if d.get('stato')=='presa_in_carico'):,}")
    k4.metric("Chiuse",          f"{sum(1 for d in seg_docs if d.get('stato')=='chiusa'):,}")

    st.divider()

    if not seg_vis:
        st.info("Nessuna segnalazione con i filtri selezionati.")
    else:
        col_map, col_list = st.columns([3, 2])

        with col_map:
            m3 = folium.Map(location=[40.3, 17.5], zoom_start=7, tiles="CartoDB positron")
            for doc in seg_vis:
                lat = doc.get("latitudine")
                lon = doc.get("longitudine")
                if not lat or not lon:
                    continue
                grav   = doc.get("gravita") or "bassa"
                colore = COLORI_GRAV.get(grav, "#95a5a6")
                ts     = doc.get("timestamp")
                ts_str = ts.strftime("%d/%m/%Y %H:%M") if ts else "—"
                popup_html = f"""
                <div style='font-family:sans-serif;font-size:12px;min-width:180px'>
                    <b>{doc.get('tipo','')}</b><br>
                    Gravità: <b>{grav}</b> &nbsp;|&nbsp; {ts_str}<br>
                    <hr style='margin:4px 0'>
                    {doc.get('descrizione','') or 'Nessuna descrizione'}<br>
                    {'<i>' + doc.get('nome','') + '</i>' if doc.get('nome') else ''}
                </div>"""
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=9,
                    color=colore,
                    fill=True,
                    fill_color=colore,
                    fill_opacity=0.85,
                    popup=folium.Popup(popup_html, max_width=220),
                    tooltip=f"{doc.get('tipo','')} — {grav}",
                ).add_to(m3)

            legenda3 = """
            <div style="position:fixed;bottom:20px;left:20px;z-index:1000;
                        background-color:#ffffff!important;color:#1f2937!important;
                        color-scheme:light;padding:10px 14px;border-radius:8px;font-size:12px;
                        box-shadow:2px 2px 8px rgba(0,0,0,0.25);font-family:sans-serif">
                <b style="color:#1f2937!important">Gravità segnalazione</b><br>
                <span style="color:#e74c3c!important;font-size:16px">&#9679;</span>
                <span style="color:#1f2937!important">Alta</span><br>
                <span style="color:#f39c12!important;font-size:16px">&#9679;</span>
                <span style="color:#1f2937!important">Media</span><br>
                <span style="color:#2ecc71!important;font-size:16px">&#9679;</span>
                <span style="color:#1f2937!important">Bassa</span>
            </div>"""
            m3.get_root().html.add_child(folium.Element(legenda3))
            st_folium(m3, height=440, use_container_width=True)

        with col_list:
            st.subheader(f"Dettagli ({len(seg_vis)})")
            GRAV_EMOJI  = {"alta": "🔴", "media": "🟡", "bassa": "🟢"}
            STATO_EMOJI = {"nuova": "🆕", "presa_in_carico": "👁️", "chiusa": "✅"}
            for doc in seg_vis:
                ts     = doc.get("timestamp")
                ts_str = ts.strftime("%d/%m %H:%M") if ts else "—"
                grav   = doc.get("gravita", "")
                tipo   = doc.get("tipo", "—")
                stato  = doc.get("stato", "nuova")
                ge     = GRAV_EMOJI.get(grav, "⚪")
                se     = STATO_EMOJI.get(stato, "")
                with st.expander(f"{ge} {ts_str} — {tipo}"):
                    st.write(f"**Stato:** {se} {stato.replace('_', ' ')}")
                    if grav:
                        st.write(f"**Gravità:** {grav}")
                    if doc.get("descrizione"):
                        st.write(f"**Descrizione:** {doc['descrizione']}")
                    if doc.get("nome"):
                        st.write(f"**Segnalato da:** {doc['nome']}")
                    if doc.get("posizione_testo"):
                        st.write(f"**Posizione indicata:** {doc['posizione_testo']}")
                        if not doc.get("latitudine"):
                            _did_geo = doc.get("_id")
                            if _did_geo and stato != "chiusa":
                                if st.button("📍 Geocodifica posizione",
                                             key=f"geo_{_did_geo}",
                                             use_container_width=True):
                                    try:
                                        g_lat, g_lon, g_name = geocodifica_nominatim(
                                            doc["posizione_testo"]
                                        )
                                        if g_lat:
                                            # Sposta le coordinate verso il mare:
                                            # calcola direzione verso la boa più vicina
                                            # (tutte in mare) e trasla dell'80% della distanza
                                            try:
                                                _boe_pos = [
                                                    {"lat": d["latitudine"], "lon": d["longitudine"]}
                                                    for d in api.carica_ultime_boe()
                                                    if d.get("latitudine") and d.get("longitudine")
                                                ]
                                                if _boe_pos:
                                                    _pv = min(_boe_pos, key=lambda b: math.sqrt(
                                                        (b["lat"] - g_lat) ** 2 +
                                                        (b["lon"] - g_lon) ** 2))
                                                    _dlat = _pv["lat"] - g_lat
                                                    _dlon = _pv["lon"] - g_lon
                                                    _dist = math.sqrt(_dlat**2 + _dlon**2)
                                                    if _dist > 0.005:
                                                        _step = min(_dist * 0.2, 0.02)
                                                        g_lat = round(g_lat + (_dlat / _dist) * _step, 6)
                                                        g_lon = round(g_lon + (_dlon / _dist) * _step, 6)
                                            except Exception:
                                                pass
                                            api.aggiorna_posizione_segnalazione(
                                                _did_geo, g_lat, g_lon, accuratezza_m=None
                                            )
                                            st.success(f"📍 Coordinate trovate: {g_lat:.5f}, {g_lon:.5f}")
                                            if g_name:
                                                st.caption(g_name)
                                            st.rerun(scope="fragment")
                                        else:
                                            st.warning("Posizione non trovata. Prova a essere più specifico.")
                                    except Exception as ex:
                                        st.error(f"Errore geocoding: {ex}")
                    if doc.get("latitudine"):
                        acc = doc.get("accuratezza_m", "?") or "geocodificato"
                        st.write(f"**GPS:** {doc['latitudine']:.5f}, {doc['longitudine']:.5f}  (±{acc}m)")
                        _did = doc.get("_id")
                        if _did and stato != "chiusa":
                            if st.button("🚢 Guida boa più vicina", key=f"miss_{_did}",
                                         use_container_width=True):
                                t_lat, t_lon = doc["latitudine"], doc["longitudine"]
                                try:
                                    _ultime_deriva = api.carica_ultime_boe(tipo_boa="deriva")
                                    boe_live = [
                                        {"_id": d["id_boa"], "lat": d["latitudine"],
                                         "lon": d["longitudine"], "nome": d.get("nome_boa")}
                                        for d in _ultime_deriva
                                        if d.get("latitudine") and d.get("longitudine")
                                    ]
                                    if boe_live:
                                        pv = min(boe_live, key=lambda b: math.sqrt(
                                            (b["lat"] - t_lat) ** 2 + (b["lon"] - t_lon) ** 2))
                                        # Sea-offset: sposta il target verso la boa quel tanto
                                        # che basta per stare in mare, restando vicino alla costa.
                                        # Regola: almeno 0.02° (~2.2 km) dal punto segnalato,
                                        # al più 35% della distanza o 0.045° (~5 km).
                                        # La boa comunque non supera mai la propria bbox di mare
                                        # (clamp nell'edge), quindi non finisce sulla terraferma.
                                        _od = math.sqrt((pv["lat"] - t_lat)**2 + (pv["lon"] - t_lon)**2)
                                        if _od > 0.005:
                                            _os = max(min(_od * 0.35, 0.045), 0.02)
                                            _os = min(_os, _od * 0.9)
                                            t_lat = round(t_lat + ((pv["lat"] - t_lat) / _od) * _os, 6)
                                            t_lon = round(t_lon + ((pv["lon"] - t_lon) / _od) * _os, 6)
                                        dist_km = math.sqrt(
                                            ((pv["lat"] - t_lat) * 111) ** 2 +
                                            ((pv["lon"] - t_lon) * 111
                                             * math.cos(math.radians(t_lat))) ** 2
                                        )
                                        api.crea_missione(
                                            id_boa=pv["_id"],
                                            nome_boa=pv["nome"],
                                            target_lat=t_lat,
                                            target_lon=t_lon,
                                            segnalazione_id=_did,
                                            distanza_km=round(dist_km, 1),
                                        )
                                        st.success(
                                            f"🚢 Missione assegnata a **{pv['nome']}**"
                                            f" — distanza: {dist_km:.1f} km"
                                        )
                                        st.rerun(scope="fragment")
                                    else:
                                        st.warning("Nessuna boa a deriva con dati recenti.")
                                except Exception as ex:
                                    st.error(f"Errore assegnazione missione: {ex}")
                    if doc.get("foto"):
                        foto_path = os.path.join(UPLOAD_DIR, doc["foto"])
                        if os.path.exists(foto_path):
                            st.image(foto_path, use_container_width=True)
                        else:
                            st.caption("Foto non disponibile sul server.")

                    # Pulsanti gestione stato
                    doc_id = doc.get("_id")
                    if doc_id and stato != "chiusa":
                        st.divider()
                        b1, b2 = st.columns(2)
                        if stato == "nuova":
                            if b1.button("👁️ Prendi in carico", key=f"pic_{doc_id}", use_container_width=True):
                                api.aggiorna_stato_segnalazione(doc_id, "presa_in_carico")
                                st.rerun(scope="fragment")
                        if b2.button("✅ Chiudi", key=f"close_{doc_id}", use_container_width=True):
                            api.aggiorna_stato_segnalazione(doc_id, "chiusa")
                            # Annulla missioni attive e di ritorno collegate a questa segnalazione
                            api.annulla_missioni_per_segnalazione(doc_id)
                            st.rerun(scope="fragment")


with tab_seg:
    sezione_segnalazioni()


# ===========================================================================
# TAB 5 — ANALISI AI
# ===========================================================================
_SENSORI_AI = [
    "ph", "torbidita_ntu", "temperatura_c", "conducibilita_ms_cm",
    "ossigeno_disciolto_mg_l", "ecoli_ufc_100ml", "enterococchi_ufc_100ml",
    "clorofilla_a_ug_l", "nitrati_mg_l", "fosfati_mg_l",
    "piombo_ug_l", "mercurio_ug_l", "arsenico_ug_l", "cadmio_ug_l", "orp_mv",
]
_LABEL_AI = {
    "ph": "pH", "torbidita_ntu": "Torbidità", "temperatura_c": "T°C",
    "conducibilita_ms_cm": "Conduc.", "ossigeno_disciolto_mg_l": "O₂ disc.",
    "ecoli_ufc_100ml": "E.coli", "enterococchi_ufc_100ml": "Enteroc.",
    "clorofilla_a_ug_l": "Cloro.-a", "nitrati_mg_l": "Nitrati",
    "fosfati_mg_l": "Fosfati", "piombo_ug_l": "Piombo",
    "mercurio_ug_l": "Mercurio", "arsenico_ug_l": "Arsenico",
    "cadmio_ug_l": "Cadmio", "orp_mv": "ORP",
}
_FEATURES_ML = [
    "ph", "torbidita_ntu", "temperatura_c", "ecoli_ufc_100ml",
    "enterococchi_ufc_100ml", "ossigeno_disciolto_mg_l",
    "nitrati_mg_l", "fosfati_mg_l", "clorofilla_a_ug_l", "conducibilita_ms_cm",
]
_RISCHIO_MAP = {
    "Eccellente": "Basso", "Buona": "Basso",
    "Sufficiente": "Medio", "Scarsa": "Alto",
}

with tab_ai:
    st.subheader("Analisi AI — Qualità Idrica & Salute")
    st.caption(
        "Sezione A: correlazioni statistiche multi-parametro | "
        "Sezione B: modello predittivo RandomForest (scikit-learn)"
    )

    # -----------------------------------------------------------------------
    # SEZIONE A: CORRELAZIONI
    # -----------------------------------------------------------------------
    st.markdown("### A — Correlazioni Statistiche")

    col_a1, col_a2 = st.columns([3, 1])
    with col_a1:
        ore_ai_corr = st.selectbox(
            "Finestra dati",
            options=[6, 24, 72, 168], index=2,
            format_func=lambda x: f"ultime {x} ore",
            key="ai_ore_corr",
        )
    with col_a2:
        btn_corr = st.button("Calcola correlazioni", use_container_width=True, key="btn_corr")

    if "ai_corr_df" not in st.session_state or btn_corr:
        try:
            _docs_c, _, _, _ = carica_dati_boe(ore_ai_corr, PROVINCE_LIST, ["fissa", "deriva"])
            st.session_state["ai_corr_df"] = docs_to_df(_docs_c)
        except Exception as _e_c:
            st.error(f"API non raggiungibile: {_e_c}")
            st.session_state["ai_corr_df"] = pd.DataFrame()

    df_ai_c = st.session_state.get("ai_corr_df", pd.DataFrame())

    if df_ai_c.empty:
        st.info("Nessun dato. Avvia il simulatore e clicca 'Calcola correlazioni'.")
    else:
        cols_num_c = [c for c in _SENSORI_AI if c in df_ai_c.columns]

        if len(cols_num_c) < 3:
            st.warning("Troppo pochi parametri numerici per la matrice di correlazione.")
        else:
            df_num_c = df_ai_c[cols_num_c].apply(pd.to_numeric, errors="coerce").dropna(
                thresh=max(1, len(cols_num_c) // 2)
            )
            corr_c    = df_num_c.corr()
            labels_ca = [_LABEL_AI.get(c, c) for c in cols_num_c]

            fig_heat = px.imshow(
                corr_c.values,
                x=labels_ca, y=labels_ca,
                color_continuous_scale="RdBu_r",
                zmin=-1, zmax=1,
                text_auto=".2f",
                aspect="auto",
                title=f"Matrice di correlazione Pearson — {len(df_num_c):,} letture boe",
            )
            fig_heat.update_layout(
                height=540,
                margin=dict(l=0, r=0, t=40, b=0),
                xaxis=dict(tickangle=-40, tickfont=dict(size=10)),
                yaxis=dict(tickfont=dict(size=10)),
                coloraxis_colorbar=dict(title="r"),
            )
            st.plotly_chart(fig_heat, use_container_width=True)

            pairs_c = []
            for _ii, _c1 in enumerate(cols_num_c):
                for _jj, _c2 in enumerate(cols_num_c):
                    if _jj <= _ii:
                        continue
                    _rv = corr_c.loc[_c1, _c2]
                    if abs(_rv) > 0.3:
                        pairs_c.append({
                            "Parametro A": _LABEL_AI.get(_c1, _c1),
                            "Parametro B": _LABEL_AI.get(_c2, _c2),
                            "r (Pearson)": round(float(_rv), 3),
                            "Intensità":   "Forte" if abs(_rv) > 0.7 else "Moderata",
                        })
            if pairs_c:
                df_pairs_c = pd.DataFrame(pairs_c).sort_values(
                    "r (Pearson)", key=abs, ascending=False
                )
                st.markdown("**Correlazioni significative (|r| > 0.3):**")
                st.dataframe(df_pairs_c, use_container_width=True, hide_index=True, height=230)

        st.divider()
        st.markdown("**Correlazione E.coli medio (per provincia) vs Dimissioni ospedaliere**")
        st.caption(
            "Analisi esplorativa: qualità idrica media delle boe per provincia "
            "vs indicatore sanitario provinciale (anno più recente disponibile)."
        )
        try:
            if "ecoli_ufc_100ml" in df_ai_c.columns and "provincia" in df_ai_c.columns:
                df_prov_c = (
                    df_ai_c.groupby("provincia")["ecoli_ufc_100ml"]
                    .mean().reset_index()
                    .rename(columns={"ecoli_ufc_100ml": "ecoli_medio"})
                )
                _san_c = api.dati_sanitari(
                    "dimissioni", "malattie apparato digerente", ordina_desc=True
                )
                if _san_c:
                    df_san_c  = pd.DataFrame(_san_c)
                    anno_ref  = int(df_san_c["anno"].max())
                    df_san_c  = df_san_c[df_san_c["anno"] == anno_ref]
                    # media M/F per provincia
                    df_san_c  = df_san_c.groupby(
                        ["provincia", "provincia_nome"], as_index=False
                    )["valore"].mean()
                    df_join_c = df_prov_c.merge(
                        df_san_c[["provincia", "valore", "provincia_nome"]],
                        on="provincia", how="inner",
                    ).dropna()
                    if len(df_join_c) >= 3:
                        r_val_c = df_join_c["ecoli_medio"].corr(df_join_c["valore"])
                        fig_sc  = px.scatter(
                            df_join_c,
                            x="ecoli_medio", y="valore", text="provincia_nome",
                            color_discrete_sequence=["#3498db"],
                            labels={
                                "ecoli_medio": "E.coli medio boe (UFC/100mL)",
                                "valore":      f"Dimissioni/100k ab. ({anno_ref})",
                            },
                            title=f"E.coli medio per provincia vs Dimissioni — r = {r_val_c:.2f}",
                        )
                        _xs_c = np.linspace(
                            df_join_c["ecoli_medio"].min(),
                            df_join_c["ecoli_medio"].max(), 60
                        )
                        _m_c, _b_c = np.polyfit(
                            df_join_c["ecoli_medio"].values,
                            df_join_c["valore"].values, 1
                        )
                        fig_sc.add_scatter(
                            x=_xs_c, y=_m_c * _xs_c + _b_c, mode="lines",
                            line={"color": "red", "dash": "dash"},
                            name="Regressione", showlegend=False,
                        )
                        fig_sc.update_traces(
                            textposition="top center", marker_size=10,
                            selector=dict(mode="markers+text"),
                        )
                        fig_sc.update_layout(height=380)
                        st.plotly_chart(fig_sc, use_container_width=True)
                        _int_c = (
                            "forte" if abs(r_val_c) > 0.7
                            else ("moderata" if abs(r_val_c) > 0.4 else "debole")
                        )
                        _dir_c = "positiva" if r_val_c > 0 else "negativa"
                        st.caption(
                            f"Correlazione {_int_c} {_dir_c} (r = {r_val_c:.2f}). "
                            f"Con dati storici pluriennali la significatività statistica aumenterebbe."
                        )
                    else:
                        st.caption("Province comuni insufficienti tra boe e dati sanitari.")
                else:
                    st.caption("Dati sanitari non disponibili. Importa con: `python3 sanitari.py ...`")
        except Exception as _e_sc:
            st.caption(f"Correlazione idrica-sanitaria non disponibile: {_e_sc}")

    st.divider()

    # -----------------------------------------------------------------------
    # SEZIONE B: PREDIZIONE RISCHIO
    # -----------------------------------------------------------------------
    st.markdown("### B — Predizione Rischio Sanitario (RandomForest)")

    if not SKLEARN_OK:
        st.error("scikit-learn non installato. Esegui: `pip install scikit-learn`")
    else:
        col_b1, col_b2 = st.columns([3, 1])
        with col_b1:
            ore_train = st.selectbox(
                "Dati per addestramento",
                options=[24, 72, 168], index=1,
                format_func=lambda x: f"ultime {x} ore",
                key="ai_ore_train",
            )
        with col_b2:
            btn_train = st.button("Addestra modello", use_container_width=True, key="btn_train")

        if btn_train:
            with st.spinner("Addestramento RandomForest in corso..."):
                try:
                    _docs_t, _, _, _ = carica_dati_boe(ore_train, PROVINCE_LIST, ["fissa", "deriva"])
                    _df_t   = docs_to_df(_docs_t)
                    _feat_t = [f for f in _FEATURES_ML if f in _df_t.columns]
                    _df_ml  = _df_t[_feat_t + ["classificazione"]].copy()
                    for _fc in _feat_t:
                        _df_ml[_fc] = pd.to_numeric(_df_ml[_fc], errors="coerce")
                    _df_ml["rischio"] = _df_ml["classificazione"].map(_RISCHIO_MAP)
                    _df_ml = _df_ml.dropna()

                    if len(_df_ml) < 30:
                        st.warning(
                            f"Campioni insufficienti ({len(_df_ml)} < 30). "
                            f"Allarga la finestra temporale."
                        )
                    else:
                        _X_t = np.array(_df_ml[_feat_t].values.tolist(), dtype=np.float64)
                        _y_t = list(_df_ml["rischio"].values)
                        _Xtr, _Xte, _ytr, _yte = train_test_split(
                            _X_t, _y_t, test_size=0.25, random_state=42
                        )
                        _clf_t = RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=1)
                        _clf_t.fit(_Xtr, _ytr)
                        _acc_t = accuracy_score(_yte, _clf_t.predict(_Xte))
                        st.session_state.update({
                            "ai_model":    _clf_t,
                            "ai_features": _feat_t,
                            "ai_accuracy": _acc_t,
                        })
                        st.success(
                            f"Modello addestrato — {len(_Xtr):,} train / {len(_Xte):,} test"
                            f" | Accuracy: **{_acc_t:.1%}**"
                        )
                except Exception as _et:
                    st.error(f"Errore addestramento: {_et}")

        if "ai_model" not in st.session_state:
            st.info("Clicca 'Addestra modello' per addestrare il classificatore di rischio.")
        else:
            _clf_p  = st.session_state["ai_model"]
            _feat_p = st.session_state["ai_features"]
            _acc_p  = st.session_state["ai_accuracy"]

            col_r1, col_r2 = st.columns(2)

            with col_r1:
                _df_fi = pd.DataFrame({
                    "Feature":    [_LABEL_AI.get(f, f) for f in _feat_p],
                    "Importanza": _clf_p.feature_importances_,
                }).sort_values("Importanza", ascending=True)
                fig_fi = px.bar(
                    _df_fi, x="Importanza", y="Feature", orientation="h",
                    title=f"Feature importance — Accuracy {_acc_p:.1%}",
                    color="Importanza",
                    color_continuous_scale="Blues",
                )
                fig_fi.update_layout(
                    height=420, showlegend=False,
                    margin=dict(l=0, r=0, t=40, b=0),
                    coloraxis_showscale=False,
                )
                st.plotly_chart(fig_fi, use_container_width=True)

            with col_r2:
                st.markdown("**Rischio corrente per boa (ultima lettura)**")
                try:
                    _ultime_p = carica_ultime_boe()
                    _righe_p  = []
                    for _doc_p in _ultime_p:
                        _s_p   = _doc_p.get("sensori", {})
                        _row_p = {f: _s_p.get(f) for f in _feat_p}
                        if sum(v is not None for v in _row_p.values()) < len(_feat_p) // 2:
                            continue
                        _X1 = np.array([[float(_row_p.get(f) or 0.0) for f in _feat_p]])
                        _rp  = _clf_p.predict(_X1)[0]
                        _pr  = _clf_p.predict_proba(_X1)[0]
                        _righe_p.append({
                            "Boa":      _doc_p.get("nome_boa", _doc_p.get("id_boa", "")),
                            "Comune":   _doc_p.get("comune", ""),
                            "Rischio":  _rp,
                            "Conf.":    f"{max(_pr):.0%}",
                            "Classif.": _doc_p.get("classificazione", ""),
                        })
                    if _righe_p:
                        _df_p = pd.DataFrame(_righe_p)
                        _EMOJI_R = {"Alto": "🔴", "Medio": "🟡", "Basso": "🟢"}
                        _df_p.insert(0, " ", _df_p["Rischio"].map(_EMOJI_R).fillna("⚪"))
                        st.dataframe(
                            _df_p,
                            use_container_width=True, height=340,
                        )
                        _n_alto_p = sum(1 for r in _righe_p if r["Rischio"] == "Alto")
                        if _n_alto_p:
                            st.error(f"{_n_alto_p} boa/e con rischio ALTO — intervento consigliato")
                        else:
                            st.success("Nessuna boa con rischio Alto al momento")
                    else:
                        st.info("Nessuna boa con dati recenti.")
                except Exception as _ep:
                    st.error(f"Errore predizione: {_ep}")

    st.divider()

    # -----------------------------------------------------------------------
    # SEZIONE C: ANOMALY DETECTION
    # -----------------------------------------------------------------------
    st.markdown("### C — Anomaly Detection (Isolation Forest)")

    if not SKLEARN_OK:
        st.error("scikit-learn non installato.")
    else:
        col_c1, col_c2, col_c3 = st.columns([2, 1, 1])
        with col_c1:
            ore_anom = st.selectbox(
                "Finestra dati",
                options=[6, 24, 72, 168], index=2,
                format_func=lambda x: f"ultime {x} ore",
                key="ai_ore_anom",
            )
        with col_c2:
            contam_pct = st.slider("% anomalie attese", 1, 15, 5, key="ai_contam")
        with col_c3:
            btn_anom = st.button("Rileva anomalie", use_container_width=True, key="btn_anom")

        if btn_anom:
            with st.spinner("Isolation Forest in esecuzione..."):
                try:
                    _docs_a, _, _, _ = carica_dati_boe(ore_anom, PROVINCE_LIST, ["fissa", "deriva"])
                    _df_a = docs_to_df(_docs_a)
                    _feat_a = [f for f in _SENSORI_AI if f in _df_a.columns]
                    _df_a_w = _df_a.copy()
                    for _fc_a in _feat_a:
                        _df_a_w[_fc_a] = pd.to_numeric(_df_a_w[_fc_a], errors="coerce")
                    _df_a_w = _df_a_w.dropna(
                        subset=_feat_a, thresh=max(1, len(_feat_a) // 2)
                    )
                    if len(_df_a_w) < 10:
                        st.warning("Dati insufficienti (< 10 campioni).")
                    else:
                        _X_a    = np.array(_df_a_w[_feat_a].fillna(0).values.tolist(), dtype=np.float64)
                        _sc_a   = StandardScaler()
                        _X_a_sc = _sc_a.fit_transform(_X_a)
                        _iso    = IsolationForest(contamination=contam_pct / 100.0,
                                                  random_state=42, n_jobs=1)
                        _pred_a   = _iso.fit_predict(_X_a_sc)
                        _scores_a = _iso.score_samples(_X_a_sc)
                        _df_a_w   = _df_a_w.copy()
                        _df_a_w["anomalia"] = (_pred_a == -1)
                        _df_a_w["score"]    = _scores_a
                        st.session_state["ai_anom_df"] = _df_a_w
                        _n_anom = int((_pred_a == -1).sum())
                        st.success(
                            f"Rilevate **{_n_anom}** anomalie su {len(_df_a_w):,} letture "
                            f"({_n_anom / len(_df_a_w):.1%})"
                        )
                except Exception as _e_a:
                    st.error(f"Errore anomaly detection: {_e_a}")

        if "ai_anom_df" in st.session_state:
            _df_vis_a   = st.session_state["ai_anom_df"].copy()
            _df_anom_ok = _df_vis_a[_df_vis_a["anomalia"]].sort_values("score")

            col_ca1, col_ca2 = st.columns(2)
            with col_ca1:
                if "ecoli_ufc_100ml" in _df_vis_a.columns and "timestamp" in _df_vis_a.columns:
                    _df_vis_a["Tipo"] = _df_vis_a["anomalia"].map(
                        {True: "Anomalia", False: "Normale"}
                    )
                    fig_anom = px.scatter(
                        _df_vis_a.sort_values("timestamp"),
                        x="timestamp", y="ecoli_ufc_100ml",
                        color="Tipo",
                        color_discrete_map={"Anomalia": "#e74c3c", "Normale": "#bdc3c7"},
                        title="E.coli nel tempo — anomalie evidenziate",
                        labels={"ecoli_ufc_100ml": "E.coli (UFC/100mL)", "timestamp": ""},
                        opacity=0.75,
                    )
                    fig_anom.update_traces(marker_size=5)
                    fig_anom.update_layout(height=360, margin=dict(t=40, b=0, l=0, r=0))
                    st.plotly_chart(fig_anom, use_container_width=True)

            with col_ca2:
                st.markdown("**Letture più anomale:**")
                _cols_a = ["timestamp", "id_boa", "comune",
                           "ecoli_ufc_100ml", "ph", "nitrati_mg_l", "classificazione"]
                _cols_a = [c for c in _cols_a if c in _df_anom_ok.columns]
                _disp_a = _df_anom_ok[_cols_a].head(20).copy()
                if "timestamp" in _disp_a.columns:
                    _disp_a["timestamp"] = (
                        pd.to_datetime(_disp_a["timestamp"]).dt.strftime("%d/%m %H:%M")
                    )
                st.dataframe(_disp_a, use_container_width=True, height=340, hide_index=True)

    st.divider()

    # -----------------------------------------------------------------------
    # SEZIONE E: CORRELAZIONE STORICA ARPA <-> SALUTE (dati reali)
    # -----------------------------------------------------------------------
    st.markdown("### E — Correlazione Storica ARPA ↔ Salute (dati reali)")
    st.caption(
        "Analisi OneHealth su dati reali: E.coli medio ARPA per provincia-anno "
        "vs incidenza patologie. Ogni punto = una provincia in un anno."
    )

    try:
        if "san_patologie" not in st.session_state:
            st.session_state["san_patologie"] = sorted(
                api.patologie_sanitarie()
            )
        _pat_opts_e = st.session_state["san_patologie"]
    except Exception:
        _pat_opts_e = []

    col_e1, col_e2, col_e3 = st.columns([3, 2, 1])
    with col_e1:
        _pat_e = st.selectbox(
            "Patologia sanitaria",
            options=_pat_opts_e or ["—"],
            format_func=lambda x: x.capitalize(),
            index=(_pat_opts_e.index("malattie apparato digerente")
                   if "malattie apparato digerente" in _pat_opts_e else 0),
            key="ai_pat_e",
        )
    with col_e2:
        _tipo_e = st.radio(
            "Tipologia", options=["dimissioni", "mortalita"],
            format_func=lambda x: {"dimissioni": "Dimissioni",
                                   "mortalita": "Mortalità"}[x],
            horizontal=True, key="ai_tipo_e",
        )
    with col_e3:
        _btn_e = st.button("Analizza", use_container_width=True, key="btn_ai_e")

    if _btn_e:
        with st.spinner("Aggregazione dati storici..."):
            try:
                # E.coli medio ARPA per provincia-anno
                _arpa_agg = api.arpa_aggregato_provincia_anno()
                _df_arpa_e = pd.DataFrame(_arpa_agg)

                # dati sanitari (media M/F) per provincia-anno
                _san_e = api.dati_sanitari(_tipo_e, _pat_e)
                _df_san_e = pd.DataFrame(_san_e)
                if not _df_san_e.empty:
                    _df_san_e = _df_san_e.groupby(
                        ["provincia", "provincia_nome", "anno"], as_index=False
                    )["valore"].mean()

                if _df_arpa_e.empty or _df_san_e.empty:
                    st.warning("Dati insufficienti per l'analisi.")
                    st.session_state.pop("ai_hist_join", None)
                else:
                    _df_join_e = _df_arpa_e.merge(
                        _df_san_e, on=["provincia", "anno"], how="inner"
                    ).dropna(subset=["ecoli_medio", "valore"])
                    st.session_state["ai_hist_join"] = _df_join_e
                    st.session_state["ai_hist_meta"] = (_pat_e, _tipo_e)
                    st.success(
                        f"{len(_df_join_e)} punti provincia-anno "
                        f"({_df_join_e['anno'].min()}-{_df_join_e['anno'].max()})"
                    )
            except Exception as _e_e:
                st.error(f"Errore analisi storica: {_e_e}")

    if "ai_hist_join" in st.session_state:
        _dj = st.session_state["ai_hist_join"]
        _pat_m, _tipo_m = st.session_state.get("ai_hist_meta", ("", ""))
        _tipo_lbl = {"dimissioni": "Dimissioni", "mortalita": "Mortalità"}.get(_tipo_m, _tipo_m)

        if len(_dj) >= 3:
            _r_e = _dj["ecoli_medio"].corr(_dj["valore"])

            col_ea, col_eb = st.columns([3, 2])
            with col_ea:
                fig_e = px.scatter(
                    _dj, x="ecoli_medio", y="valore",
                    color="provincia_nome", hover_data=["anno", "n_campioni"],
                    labels={
                        "ecoli_medio": "E.coli medio ARPA (UFC/100mL)",
                        "valore":      f"{_tipo_lbl} /100k ab.",
                        "provincia_nome": "Provincia",
                    },
                    title=f"E.coli ARPA vs {_tipo_lbl} — {_pat_m} | r = {_r_e:.2f}",
                    color_discrete_sequence=px.colors.qualitative.Set1,
                )
                # retta di regressione globale
                _xs_e = np.linspace(_dj["ecoli_medio"].min(),
                                    _dj["ecoli_medio"].max(), 60)
                _me, _be = np.polyfit(_dj["ecoli_medio"].values,
                                      _dj["valore"].values, 1)
                fig_e.add_scatter(
                    x=_xs_e, y=_me * _xs_e + _be, mode="lines",
                    line={"color": "black", "dash": "dash"},
                    name="Regressione", showlegend=True,
                )
                fig_e.update_traces(marker_size=9,
                                    selector=dict(mode="markers"))
                fig_e.update_layout(height=440)
                st.plotly_chart(fig_e, use_container_width=True)

            with col_eb:
                _int_e = ("forte" if abs(_r_e) > 0.7
                          else "moderata" if abs(_r_e) > 0.4
                          else "debole")
                _dir_e = "positiva" if _r_e > 0 else "negativa"
                st.metric("Correlazione r (Pearson)", f"{_r_e:.3f}")
                st.markdown(
                    f"Correlazione **{_int_e} {_dir_e}**.\n\n"
                    + ("Un E.coli più alto nelle acque si accompagna a "
                       f"tassi di {_tipo_lbl.lower()} più alti."
                       if _r_e > 0 else
                       "Relazione inversa tra i due indicatori.")
                )
                st.divider()
                # correlazione per provincia
                _rows_pe = []
                for _pn, _g in _dj.groupby("provincia_nome"):
                    if len(_g) >= 3:
                        _rp = _g["ecoli_medio"].corr(_g["valore"])
                        _rows_pe.append({"Provincia": _pn,
                                         "r": round(float(_rp), 2),
                                         "Anni": len(_g)})
                if _rows_pe:
                    st.markdown("**Correlazione per provincia:**")
                    st.dataframe(
                        pd.DataFrame(_rows_pe).sort_values("r", ascending=False),
                        use_container_width=True, hide_index=True,
                    )

            # andamento temporale doppio asse
            st.markdown("**Andamento temporale (media regionale)**")
            _df_reg = _dj.groupby("anno", as_index=False).agg(
                ecoli_medio=("ecoli_medio", "mean"),
                valore=("valore", "mean"),
            )
            from plotly.subplots import make_subplots
            import plotly.graph_objects as go
            fig_ts = make_subplots(specs=[[{"secondary_y": True}]])
            fig_ts.add_trace(
                go.Scatter(x=_df_reg["anno"], y=_df_reg["ecoli_medio"],
                           name="E.coli ARPA", line=dict(color="#3498db", width=3)),
                secondary_y=False,
            )
            fig_ts.add_trace(
                go.Scatter(x=_df_reg["anno"], y=_df_reg["valore"],
                           name=_tipo_lbl, line=dict(color="#e74c3c", width=3)),
                secondary_y=True,
            )
            fig_ts.update_yaxes(title_text="E.coli medio (UFC/100mL)",
                                secondary_y=False, color="#3498db")
            fig_ts.update_yaxes(title_text=f"{_tipo_lbl} /100k ab.",
                                secondary_y=True, color="#e74c3c")
            fig_ts.update_layout(height=340, hovermode="x unified",
                                 margin=dict(t=20, b=0, l=0, r=0))
            st.plotly_chart(fig_ts, use_container_width=True)
            st.caption(
                "Nota metodologica: correlazione ecologica (a livello provinciale). "
                "Indica associazione statistica, non causalità diretta."
            )
        else:
            st.info("Punti dati insufficienti per la correlazione.")
