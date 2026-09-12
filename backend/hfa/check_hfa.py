import json
from collections import Counter


FILE = "hfa_clean.json"


with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


print("Totale record:", len(data))


# =========================
# Indicatori
# =========================

print("\nIndicatori:")

indicators = Counter(
    (
        d["indicator"]["name"],
        d["indicator"]["category"]
    )
    for d in data
)

for i, count in indicators.items():
    print(i, "->", count)


# =========================
# Province
# =========================

print("\nProvince:")

provinces = Counter(
    d["territory"]["province"]
    for d in data
)

for p, count in provinces.items():
    print(p, "->", count)


# =========================
# Anni
# =========================

print("\nAnni presenti:")

years = sorted(
    set(
        d["year"]
        for d in data
    )
)

print(years)


# =========================
# Valori anomali
# =========================

print("\nControllo valori:")

bad = []

for d in data:

    if d["value"] < 0:
        bad.append(d)

    if d["value"] > 100000:
        bad.append(d)


print(
    "Valori anomali:",
    len(bad)
)


# =========================
# Duplicati
# =========================

print("\nDuplicati:")


keys = set()
duplicates = []


for d in data:

    key = (
        d["indicator"]["name"],
        d["indicator"]["category"],
        d["territory"]["province"],
        d["year"],
        d["sex"]
    )


    if key in keys:
        duplicates.append(d)

    keys.add(key)



print(
    "Duplicati trovati:",
    len(duplicates)
)
