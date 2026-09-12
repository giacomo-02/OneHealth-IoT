import pandas as pd

from backend.database import SessionLocal
from backend.models.sanitario_model import DatoSanitario

from backend.hfa.province import PROVINCE_MAP



CSV_PATH = "backend/hfa/hfa_dataset.csv"



def import_hfa():

    db = SessionLocal()


    df = pd.read_csv(
        CSV_PATH,
        sep=";"
    )


    print(
        "Record CSV:",
        len(df)
    )


    inseriti = 0


    for _, row in df.iterrows():

        provincia_nome = row["provincia"]

        codice = PROVINCE_MAP.get(
            provincia_nome
        )


        if not codice:
            print(
                "Provincia sconosciuta:",
                provincia_nome
            )
            continue


        record = DatoSanitario(

            provincia=codice,

            provincia_nome=provincia_nome,

            anno=int(row["anno"]),

            tipologia=row["tipologia"],

            patologia=row["patologia"],

            sesso=row["sesso"],

            valore=float(row["valore"])

        )


        db.add(record)

        inseriti += 1


    db.commit()

    db.close()


    print(
        "Inseriti:",
        inseriti
    )



if __name__ == "__main__":

    import_hfa()
