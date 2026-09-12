from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import extract, func
from sqlalchemy.orm import Session


from backend.database import get_db

from backend.models import ArpaMisurazione

from backend.schemas import (
    ArpaMisurazioniResponse,
    ArpaAggregatoRow
)


router = APIRouter(
    prefix="/arpa",
    tags=["arpa"]
)



def _row_to_doc(r: ArpaMisurazione):

    return {

        "timestamp": r.timestamp,

        "codice": r.codice,

        "provincia": r.provincia,

        "comune": r.comune,

        "denominazione": r.denominazione,

        "latitudine": r.latitudine,

        "longitudine": r.longitudine,


        "sensori": {

            "ecoli_ufc_100ml":
                r.ecoli_ufc_100ml,

            "enterococchi_ufc_100ml":
                r.enterococchi_ufc_100ml

        },


        "alert": r.alert or [],

        "ha_alert": bool(r.ha_alert),

        "classificazione": r.classificazione

    }



@router.get(
    "/anni",
    response_model=List[int]
)
def anni_disponibili(
    db: Session = Depends(get_db)
):

    rows = (

        db.query(
            extract(
                "year",
                ArpaMisurazione.timestamp
            ).label("anno")
        )

        .distinct()

        .all()

    )


    return sorted(
        {
            int(r.anno)
            for r in rows
            if r.anno is not None
        },
        reverse=True
    )



@router.get(
    "/misurazioni",
    response_model=ArpaMisurazioniResponse
)
def get_misurazioni(

    province: Optional[List[str]] = Query(None),

    anno: Optional[int] = Query(None),

    db: Session = Depends(get_db)

):

    q = db.query(
        ArpaMisurazione
    )


    if province:

        q = q.filter(
            ArpaMisurazione.provincia.in_(province)
        )


    if anno:

        q = q.filter(
            ArpaMisurazione.timestamp >= datetime(anno,1,1),
            ArpaMisurazione.timestamp < datetime(anno+1,1,1)
        )


    totale = q.count()



    sub = (

        q.with_entities(

            ArpaMisurazione.codice,

            func.max(
                ArpaMisurazione.timestamp
            ).label("max_ts")

        )

        .group_by(
            ArpaMisurazione.codice
        )

        .subquery()

    )



    rows = (

        db.query(
            ArpaMisurazione
        )

        .join(

            sub,

            (ArpaMisurazione.codice == sub.c.codice)

            &

            (
                ArpaMisurazione.timestamp
                ==
                sub.c.max_ts
            )

        )

        .all()

    )


    return {

        "docs":[
            _row_to_doc(r)
            for r in rows
        ],

        "tot": totale,

        "n_alert":
            sum(
                1
                for r in rows
                if r.ha_alert
            )

    }




@router.get(
    "/aggregato-provincia-anno",
    response_model=List[ArpaAggregatoRow]
)
def aggregato_provincia_anno(

    db: Session = Depends(get_db)

):

    anno_col = extract(
        "year",
        ArpaMisurazione.timestamp
    )


    rows = (

        db.query(

            ArpaMisurazione.provincia,

            anno_col.label("anno"),

            func.avg(
                ArpaMisurazione.ecoli_ufc_100ml
            ).label("ecoli_medio"),


            func.avg(
                ArpaMisurazione.enterococchi_ufc_100ml
            ).label("entero_medio"),


            func.count(
                ArpaMisurazione.id
            ).label("n_campioni")

        )

        .group_by(

            ArpaMisurazione.provincia,

            anno_col

        )

        .all()

    )


    return [

        {

            "provincia": r.provincia,

            "anno": int(r.anno),

            "ecoli_medio": r.ecoli_medio,

            "entero_medio": r.entero_medio,

            "n_campioni": r.n_campioni

        }

        for r in rows

    ]
