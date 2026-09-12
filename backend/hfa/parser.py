#!/usr/bin/env python3

import csv
import glob
import os
import re
import sys
import unicodedata


YEAR_MIN, YEAR_MAX = 1980, 2025


TITLE_PATTERNS = [
    re.compile(
        r'^Tasso\s+std\s+(?P<tipologia>\S+)\s+(?P<patologia>.+?)\s+(?P<sesso>[MF])\s*$',
        re.IGNORECASE
    ),
    re.compile(
        r'^Tasso\s+(?P<tipologia>\S+)\s+std\s+(?P<patologia>.+?)\s+(?P<sesso>[MF])\s*$',
        re.IGNORECASE
    ),
]


def clean_text(s: str) -> str:
    if s is None:
        return ""

    s = str(s).strip()
    return unicodedata.normalize("NFKC", s)


def parse_title(title_line):
    title_line = title_line.strip()

    for pattern in TITLE_PATTERNS:
        m = pattern.match(title_line)

        if m:
            return (
                clean_text(m.group("tipologia")),
                clean_text(m.group("patologia")),
                m.group("sesso").strip().upper(),
            )

    raise ValueError(
        f"Impossibile interpretare il titolo: {title_line!r}"
    )


def find_year_columns(header_cells):
    year_cols = {}

    for idx, cell in enumerate(header_cells):
        cell = cell.strip()

        if re.fullmatch(r"\d{4}", cell):
            year = int(cell)

            if YEAR_MIN <= year <= YEAR_MAX:
                year_cols[idx] = year

    return year_cols


def parse_value(raw):
    raw = raw.strip()

    if not raw:
        return None

    normalized = (
        raw
        .replace(",", ".")
        .replace(" ", "")
    )

    try:
        return float(normalized)

    except ValueError:
        return None


def parse_file(filepath):

    with open(filepath, encoding="latin-1") as fh:
        lines = fh.readlines()


    if len(lines) < 2:
        raise ValueError(
            f"File {filepath} troppo corto"
        )


    tipologia, patologia, sesso = parse_title(lines[0])


    header_cells = (
        lines[1]
        .rstrip("\n")
        .split("\t")
    )


    year_cols = find_year_columns(header_cells)


    rows = []


    for line in lines[2:]:

        if not line.strip():
            continue


        cells = (
            line
            .rstrip("\n")
            .split("\t")
        )


        if len(cells) < 2:
            continue


        provincia = clean_text(cells[1])


        if not provincia:
            continue


        for col_idx, year in year_cols.items():

            if col_idx >= len(cells):
                continue


            value = parse_value(
                cells[col_idx]
            )


            if value is None:
                continue


            rows.append(
                {
                    "provincia": provincia,
                    "anno": year,
                    "tipologia": tipologia,
                    "patologia": patologia,
                    "sesso": sesso,
                    "valore": value
                }
            )


    return rows



def remove_duplicates(rows):

    unique_rows = []
    seen = set()


    for row in rows:

        key = (
            row["provincia"],
            row["anno"],
            row["tipologia"],
            row["patologia"],
            row["sesso"],
            row["valore"]
        )


        if key not in seen:

            seen.add(key)
            unique_rows.append(row)


    return unique_rows



def build_dataset(input_dir, output_csv):

    txt_files = sorted(
        glob.glob(
            os.path.join(
                input_dir,
                "*.txt"
            )
        )
    )


    all_rows = []


    for filepath in txt_files:

        try:

            rows = parse_file(filepath)

            all_rows.extend(rows)

            print(
                f"OK {os.path.basename(filepath)} -> {len(rows)} righe"
            )


        except Exception as e:

            print(
                f"[SKIP] {filepath}: {e}"
            )



    print(
        f"\nRecord prima della pulizia: {len(all_rows)}"
    )


    clean_rows = remove_duplicates(all_rows)


    print(
        f"Duplicati rimossi: {len(all_rows)-len(clean_rows)}"
    )


    fieldnames = [
        "provincia",
        "anno",
        "tipologia",
        "patologia",
        "sesso",
        "valore"
    ]



    with open(
        output_csv,
        "w",
        newline="",
        encoding="utf-8"
    ) as out:

        writer = csv.DictWriter(
            out,
            fieldnames=fieldnames,
            delimiter=";"
        )


        writer.writeheader()

        writer.writerows(clean_rows)



    print(
        f"\n✔ Creato dataset pulito: {len(clean_rows)} righe"
    )



if __name__ == "__main__":

    input_dir = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "hfa"
    )


    output_csv = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "hfa_dataset.csv"
    )


    build_dataset(
        input_dir,
        output_csv
    )
