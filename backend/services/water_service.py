from datetime import datetime

from backend.models.water_model import (
    WaterDevice,
    WaterMeasurement,
    WaterAlert
)


# Soglie per parametro: (nome, unita, soglia_allerta, soglia_critico)
SOGLIE_ALERT = {
    "ecoli":        ("E.coli",       "UFC/100mL", 200, 500),
    "enterococci":  ("Enterococchi", "UFC/100mL", 100, 200),
    "lead":         ("Piombo",       "µg/L",      10,  25),
    "mercury":      ("Mercurio",     "µg/L",      1.0, 3.0),
    "arsenic":      ("Arsenico",     "µg/L",      5.0, 10.0),
    "cadmium":      ("Cadmio",       "µg/L",      0.5, 2.0),
    "nitrates":     ("Nitrati",      "mg/L",      25,  50),
}

_SEVERITA = {None: 0, "allerta": 1, "critico": 2}


def valuta_criticita(valori):
    """Ritorna (livello, descrizione) valutando i parametri contro le soglie.
    livello None = nessuna criticita'."""
    livello = None
    voci = []
    for campo, (nome, unita, s_all, s_crit) in SOGLIE_ALERT.items():
        v = valori.get(campo)
        if v is None:
            continue
        if v > s_crit:
            voci.append(f"{nome} {v} {unita} (critico)")
            livello = "critico"
        elif v > s_all:
            voci.append(f"{nome} {v} {unita}")
            if livello != "critico":
                livello = "allerta"
    return livello, "; ".join(voci)


def _valori_da_measurement(m):
    """Estrae i parametri rilevanti da un record WaterMeasurement (per confronto)."""
    return {
        "ecoli":       m.ecoli,
        "enterococci": m.enterococci,
        "lead":        m.lead,
        "mercury":     m.mercury,
        "arsenic":     m.arsenic,
        "cadmium":     m.cadmium,
        "nitrates":    m.nitrates,
    }


def save_water_data(db, data):

    device = data["device"]

    existing = (
        db.query(WaterDevice)
        .filter(
            WaterDevice.device_id == device["id"]
        )
        .first()
    )


    if existing is None:

        existing = WaterDevice(

            device_id=device["id"],

            nome=device["nome"],

            comune=device["comune"],

            provincia=device["provincia"],

            zona=device["zona"],

            tipo=device["tipo"],

            lat=device["lat"],

            lon=device["lon"]

        )

        db.add(existing)


    else:

        existing.nome = device["nome"]
        existing.comune = device["comune"]
        existing.provincia = device["provincia"]
        existing.zona = device["zona"]
        existing.tipo = device["tipo"]
        existing.lat = device["lat"]
        existing.lon = device["lon"]


    db.commit()


    measurements = data["measurements"]

    analysis = data["analysis"]


    # Livello di criticita' della lettura PRECEDENTE (per rilevare il peggioramento)
    prec = (
        db.query(WaterMeasurement)
        .filter(WaterMeasurement.device_id == device["id"])
        .order_by(WaterMeasurement.timestamp.desc())
        .first()
    )

    livello_prec, _ = valuta_criticita(_valori_da_measurement(prec)) if prec else (None, "")


    record = WaterMeasurement(

        device_id=device["id"],


        timestamp=datetime.fromisoformat(
            data["timestamp"]
        ),


        ph=measurements["ph"],

        temperature=measurements["temperature"],

        turbidity=measurements["turbidity"],

        conductivity=measurements["conductivity"],

        dissolved_oxygen=measurements["dissolved_oxygen"],


        nitrates=measurements["nitrates"],

        phosphates=measurements["phosphates"],

        chlorophyll_a=measurements["chlorophyll_a"],


        ecoli=measurements["ecoli"],

        enterococci=measurements["enterococci"],


        arsenic=measurements["arsenic"],

        lead=measurements["lead"],

        mercury=measurements["mercury"],

        cadmium=measurements["cadmium"],


        chlorine=measurements["chlorine"],

        orp=measurements["orp"],


        wqi=analysis["wqi"],

        status=analysis["status"]

    )


    db.add(record)

    db.commit()

    db.refresh(record)


    # Alert SOLO al cambio di stato in peggio (normale->allerta, ->critico, allerta->critico)
    livello_cur, descr_cur = valuta_criticita(measurements)

    if _SEVERITA[livello_cur] > _SEVERITA[livello_prec]:

        alert = WaterAlert(

            device_id=device["id"],

            nome_boa=device["nome"],

            comune=device["comune"],

            provincia=device["provincia"],

            latitudine=device["lat"],

            longitudine=device["lon"],

            timestamp=record.timestamp,

            livello=livello_cur,

            parametri=descr_cur,

            classificazione=analysis["status"],

            wqi=analysis["wqi"]

        )

        db.add(alert)

        db.commit()


    return record
