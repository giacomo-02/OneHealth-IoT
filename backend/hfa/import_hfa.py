import pandas as pd


def load_hfa(csv_path):
    df = pd.read_csv(csv_path)

    data = []

    for _, row in df.iterrows():
        data.append({
            "provincia": row["provincia"],
            "anno": int(row["anno"]),
            "tipo": row["tipo"],
            "patologia": row["patologia"],
            "sesso": row["sesso"],
            "valore": float(row["valore"])
        })

    return data
