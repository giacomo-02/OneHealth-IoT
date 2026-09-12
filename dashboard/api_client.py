"""
Client per l'API OneHealth Puglia (FastAPI + PostgreSQL).

Sostituisce l'accesso diretto a MongoDB (pymongo) della dashboard originale.
Ogni funzione qui restituisce dati nella STESSA forma dei documenti Mongo
originali (liste di dict, con "sensori" annidato, "_id" come stringa, ecc.)
in modo che il resto di dashboard.py non debba cambiare logica: cambia solo
la fonte dei dati.

Imposta la variabile d'ambiente API_BASE_URL con l'indirizzo del backend,
es. http://localhost:8000 (default).
"""
import os
from datetime import datetime
from typing import List, Optional

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
_TIMEOUT = 10


def _parse_dt(value):
    if value is None or isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


# La dashboard originale (grafica/legenda mappa, colori, sezione AI) si
# aspetta il campo "classificazione" con questi 4 valori esatti in italiano.
# Se il TUO backend restituisce etichette diverse (es. la nomenclatura
# inglese della direttiva UE sulle acque di balneazione: Excellent/Good/
# Sufficient/Poor, o altre varianti di maiuscole/minuscole), qui vengono
# tradotte cosi' che mappa, legenda e sezione AI restino identiche
# all'originale senza dover cambiare dashboard.py.
# Se il tuo backend usa altre etichette ancora, aggiungi qui le chiavi
# mancanti (in minuscolo).
_MAPPA_CLASSIFICAZIONE = {
    "eccellente": "Eccellente", "excellent": "Eccellente",
    "buona": "Buona", "buono": "Buona", "good": "Buona",
    "sufficiente": "Sufficiente", "sufficient": "Sufficiente",
    "scarsa": "Scarsa", "scarso": "Scarsa", "poor": "Scarsa", "bad": "Scarsa",
}


def _normalizza_classificazione(doc: dict) -> dict:
    cls = doc.get("classificazione")
    if cls:
        doc["classificazione"] = _MAPPA_CLASSIFICAZIONE.get(str(cls).strip().lower(), cls)
    return doc


def _with_datetime(doc: dict) -> dict:
    if doc.get("timestamp") is not None:
        doc["timestamp"] = _parse_dt(doc["timestamp"])
    _normalizza_classificazione(doc)
    return doc


def _get(path: str, params: Optional[dict] = None):
    r = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


def _patch(path: str, json: Optional[dict] = None):
    r = requests.patch(f"{API_BASE_URL}{path}", json=json, timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


def _post(path: str, json: Optional[dict] = None):
    r = requests.post(f"{API_BASE_URL}{path}", json=json, timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# BOE
# ---------------------------------------------------------------------------
def carica_dati_boe(ore: int, province: List[str], tipi: List[str]):
    """Sostituisce carica_dati_boe(): ritorna (docs, tot_db, n_alert, fallback)."""
    params = {"ore": ore}
    if province:
        params["province"] = province
    if tipi:
        params["tipi"] = tipi
    data = _get("/boe/misurazioni", params=params)
    docs = [_with_datetime(d) for d in data["docs"]]
    return docs, data["tot_db"], data["n_alert"], data["fallback"]


def carica_ultime_boe(tipo_boa: Optional[str] = None):
    """Sostituisce carica_ultime_boe(): ultima lettura per ogni boa."""
    params = {"tipo_boa": tipo_boa} if tipo_boa else None
    docs = _get("/boe/ultime", params=params)
    return [_with_datetime(d) for d in docs]


# ---------------------------------------------------------------------------
# ARPA
# ---------------------------------------------------------------------------
def anni_disponibili_arpa():
    return _get("/arpa/anni")


def carica_dati_arpa(province: Optional[List[str]] = None, anno: Optional[int] = None):
    """Sostituisce carica_dati_arpa(): ritorna (docs, tot, n_alert)."""
    params = {}
    if province:
        params["province"] = province
    if anno:
        params["anno"] = anno
    data = _get("/arpa/misurazioni", params=params)
    docs = [_with_datetime(d) for d in data["docs"]]
    return docs, data["tot"], data["n_alert"]


def arpa_aggregato_provincia_anno():
    """E.coli/Enterococchi medi ARPA per provincia-anno (Sezione E Analisi AI)."""
    return _get("/arpa/aggregato-provincia-anno")


# ---------------------------------------------------------------------------
# DATI SANITARI
# ---------------------------------------------------------------------------
def patologie_sanitarie():
    return _get("/sanitari/patologie")


def dati_sanitari(tipologia: str, patologia: str, ordina_desc: bool = False):
    return _get(
        "/sanitari/dati",
        params={"tipologia": tipologia, "patologia": patologia, "ordina_desc": ordina_desc},
    )


# ---------------------------------------------------------------------------
# SEGNALAZIONI
# ---------------------------------------------------------------------------
def conta_segnalazioni_nuove() -> int:
    return _get("/segnalazioni/nuove-count")


def lista_segnalazioni(stati: Optional[List[str]] = None, limit: int = 300):
    params = {"limit": limit}
    if stati:
        params["stati"] = stati
    docs = _get("/segnalazioni", params=params)
    out = []
    for d in docs:
        # La dashboard usa "_id" (forma Mongo); il backend REST espone "id".
        if "_id" not in d and d.get("id") is not None:
            d["_id"] = str(d["id"])
        out.append(_with_datetime(d))
    return out


def aggiorna_stato_segnalazione(segnalazione_id, stato: str):
    return _patch(f"/segnalazioni/{segnalazione_id}/stato", json={"stato": stato})


def aggiorna_posizione_segnalazione(segnalazione_id, lat: float, lon: float, accuratezza_m=None):
    return _patch(
        f"/segnalazioni/{segnalazione_id}/posizione",
        json={"latitudine": lat, "longitudine": lon, "accuratezza_m": accuratezza_m},
    )


# ---------------------------------------------------------------------------
# MISSIONI
# ---------------------------------------------------------------------------
def missioni_attive():
    docs = _get("/missioni/attive")
    return [_with_datetime(d) for d in docs]


def missioni_completate_count() -> int:
    return _get("/missioni/completate-count")


def crea_missione(id_boa, nome_boa, target_lat, target_lon, segnalazione_id=None, distanza_km=None):
    return _post(
        "/missioni",
        json={
            "id_boa": id_boa,
            "nome_boa": nome_boa,
            "target_lat": target_lat,
            "target_lon": target_lon,
            "segnalazione_id": int(segnalazione_id) if segnalazione_id is not None else None,
            "distanza_km": distanza_km,
        },
    )


def annulla_missioni_per_segnalazione(segnalazione_id):
    return _post(f"/missioni/annulla-per-segnalazione/{segnalazione_id}")


# ---------------------------------------------------------------------------
# ALERTS / CRITICITÀ
# ---------------------------------------------------------------------------
def alerts_recenti(limit: int = 300, livello: Optional[str] = None):
    params = {"limit": limit}
    if livello:
        params["livello"] = livello
    docs = _get("/alerts", params=params)
    return [_with_datetime(d) for d in docs]


def alerts_count() -> int:
    return _get("/alerts/count")
