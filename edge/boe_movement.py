"""
Movimento delle boe: missioni verso un target e ritorno alla base.

Ogni boa parte dalla sua posizione di configurazione (base). Quando la
dashboard crea una missione, la boa assegnata si muove verso il target un po'
a ogni ciclo; raggiunto il target (o il bordo della propria zona di mare)
passa allo stato "ritorno" e rientra alla base. La posizione resta sempre
dentro la bbox della boa (zona di mare), cosi' la boa non finisce mai sulla
terraferma.
"""

import math
import os
import random

import requests

from boe_config import BOE


API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)


STEP = 0.010       # spostamento massimo per ciclo (~1,1 km): movimento graduale
                   #   e visibile sulla mappa (una missione di ~9 km richiede
                   #   ~8-9 cicli, cosi' si segue cliccando "Aggiorna mappa")

SOGLIA = 0.006     # distanza per considerare il target "raggiunto" (~0.7 km)


# Deriva lenta delle boe "deriva" quando non hanno missioni
DRIFT_NOISE = 0.006   # ampiezza casuale del vagabondaggio per ciclo (~0.6 km)

DRIFT_PULL = 0.04     # richiamo verso la base: tiene la boa al largo (~5-6 km max)


# Stato in memoria: posizione corrente, base e zona di mare di ogni boa
_POSIZIONE = {}

_BASE = {}

_BBOX = {}


for _b in BOE:

    _POSIZIONE[_b["id"]] = [_b["lat"], _b["lon"]]

    _BASE[_b["id"]] = (_b["lat"], _b["lon"])

    if _b.get("bbox"):

        _BBOX[_b["id"]] = _b["bbox"]



def _dist(a, b):

    return math.sqrt(
        (a[0] - b[0]) ** 2
        + (a[1] - b[1]) ** 2
    )



def _passo(cur, target):
    """Sposta cur verso target di al piu' STEP gradi."""

    d = _dist(cur, target)

    if d <= STEP or d == 0:
        return [target[0], target[1]]

    fr = STEP / d

    return [
        cur[0] + (target[0] - cur[0]) * fr,
        cur[1] + (target[1] - cur[1]) * fr
    ]



def _clamp_bbox(bid, lat, lon):
    """Mantiene la posizione dentro la zona di mare della boa (se definita)."""

    bbox = _BBOX.get(bid)

    if not bbox:
        return lat, lon

    lat_min, lat_max, lon_min, lon_max = bbox

    lat = min(max(lat, lat_min), lat_max)

    lon = min(max(lon, lon_min), lon_max)

    return lat, lon



def carica_missioni_attive():
    """Ritorna {id_boa: missione} per le missioni attive o in ritorno."""

    try:

        r = requests.get(
            f"{API_URL}/missioni/attive",
            timeout=5
        )

        r.raise_for_status()

        return {
            m["id_boa"]: m
            for m in r.json()
        }

    except Exception as e:

        print("Missioni non raggiungibili:", e)

        return {}



def _imposta_stato(id_boa, stato):

    try:

        requests.patch(
            f"{API_URL}/missioni/{id_boa}/stato",
            params={"stato": stato},
            timeout=5
        )

    except Exception as e:

        print("Aggiornamento stato missione fallito:", e)



def posizione_corrente(boa, missioni):
    """Calcola la nuova posizione (lat, lon) della boa in base alla missione
    corrente (se presente) e gestisce le transizioni di stato.
    Solo le boe a deriva si muovono: le boe fisse restano ancorate anche se
    ricevessero per errore una missione."""

    bid = boa["id"]

    cur = _POSIZIONE[bid]

    e_deriva = boa.get("tipo") == "deriva"

    # Le boe fisse non si spostano mai
    miss = missioni.get(bid) if e_deriva else None


    if miss and miss.get("stato") == "attiva":

        target = (miss["target_lat"], miss["target_lon"])

        nuovo = _passo(cur, target)

        nuovo = list(_clamp_bbox(bid, nuovo[0], nuovo[1]))

        # target raggiunto oppure bloccato dal bordo della zona di mare
        if _dist(nuovo, target) < SOGLIA or _dist(nuovo, cur) < 0.0005:
            _imposta_stato(bid, "ritorno")

        _POSIZIONE[bid] = nuovo


    elif miss and miss.get("stato") == "ritorno":

        base = _BASE[bid]

        nuovo = _passo(cur, base)

        if _dist(nuovo, base) < SOGLIA:
            nuovo = [base[0], base[1]]
            _imposta_stato(bid, "completata")

        _POSIZIONE[bid] = nuovo


    else:

        # Nessuna missione: le boe a deriva vagano lentamente attorno alla base
        # (posta al largo) con un richiamo verso di essa, cosi' restano sempre
        # a distanza di sicurezza dalla costa. Le boe fisse non si muovono.
        if e_deriva:

            base = _BASE[bid]

            nl = (
                cur[0]
                + random.uniform(-DRIFT_NOISE, DRIFT_NOISE)
                - DRIFT_PULL * (cur[0] - base[0])
            )

            no = (
                cur[1]
                + random.uniform(-DRIFT_NOISE, DRIFT_NOISE)
                - DRIFT_PULL * (cur[1] - base[1])
            )

            nl, no = _clamp_bbox(bid, nl, no)

            _POSIZIONE[bid] = [nl, no]


    return _POSIZIONE[bid][0], _POSIZIONE[bid][1]
