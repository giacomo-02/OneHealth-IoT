import pandas as pd
from datetime import datetime

from backend.database import SessionLocal
from backend.models.arpa_model import ArpaMisurazione


CSV_PATH = "backend/arpa/dataset_balneazione.csv"


PROV_MAP = {
    "Foggia": "FG",
    "Bari": "BA",
    "Brindisi": "BR",
    "Taranto": "TA",
    "Lecce": "LE",
    "Barletta-Andria-Trani": "BT",
    "BAT": "BT",
}


# ---------------------------------------------------------
# CLASSIFICAZIONE D.Lgs 116/2008
# ---------------------------------------------------------

def classifica(ecoli, enterococchi):

    if ecoli is None or enterococchi is None:
        return None

    if ecoli <= 100 and enterococchi <= 40:
        return "Eccellente"

    if ecoli <= 250 and enterococchi <= 100:
        return "Buona"

    if ecoli <= 500 and enterococchi <= 200:
        return "Sufficiente"

    return "Scarsa"



# ---------------------------------------------------------
# ALERT
# ---------------------------------------------------------

def genera_alert(ecoli, enterococchi):

    alerts = []


    if ecoli is not None:

        if ecoli > 500:
            alerts.append(
                f"CRITICO:ecoli>{ecoli}"
            )

        elif ecoli > 250:
            alerts.append(
                f"ALLERTA:ecoli>{ecoli}"
            )


    if enterococchi is not None:

        if enterococchi > 200:
            alerts.append(
                f"CRITICO:enterococchi>{enterococchi}"
            )

        elif enterococchi > 100:
            alerts.append(
                f"ALLERTA:enterococchi>{enterococchi}"
            )


    return alerts



# ---------------------------------------------------------
# CONVERSIONI
# ---------------------------------------------------------

def parse_float(value):

    if value is None:
        return None

    try:

        return float(
            str(value)
            .replace(",", ".")
            .strip()
        )

    except:

        return None



# ---------------------------------------------------------
# IMPORT
# ---------------------------------------------------------

def import_arpa():


    df = pd.read_csv(
        CSV_PATH,
        sep=";",
        encoding="utf-8",
        dtype=str
    )


    print(
        "Record CSV:",
        len(df)
    )


    db = SessionLocal()


    inserted = 0


    try:


        for _, row in df.iterrows():


            try:


                timestamp = datetime.strptime(
                    row["data"].strip(),
                    "%Y-%m-%d"
                )


                ecoli = parse_float(
                    row["escherichia_coli"]
                )


                enterococchi = parse_float(
                    row["enterococchi"]
                )


                alert = genera_alert(
                    ecoli,
                    enterococchi
                )


                classificazione = classifica(
                    ecoli,
                    enterococchi
                )


                provincia_originale = (
                    row["provincia"]
                    .strip()
                )


                provincia = PROV_MAP.get(
                    provincia_originale,
                    provincia_originale[:2].upper()
                )


                obj = ArpaMisurazione(


                    timestamp=timestamp,


                    codice=row["area_balneazione"].strip(),


                    provincia=provincia,


                    comune=row["comune"].strip(),


                    denominazione=row["denominazione"].strip(),


                    latitudine=parse_float(
                        row["Y"]
                    ),


                    longitudine=parse_float(
                        row["X"]
                    ),


                    ecoli_ufc_100ml=ecoli,


                    enterococchi_ufc_100ml=enterococchi,


                    alert=alert,


                    ha_alert=len(alert) > 0,


                    classificazione=classificazione

                )


                db.add(obj)


                inserted += 1



            except Exception as e:

                print(
                    "Errore riga:",
                    e
                )



        db.commit()



    finally:

        db.close()



    print(
        "Inseriti:",
        inserted
    )




if __name__ == "__main__":

    import_arpa()
