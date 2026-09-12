from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend import models
from backend import schemas
from backend.database import get_db


router = APIRouter(
    prefix="/sanitari",
    tags=["sanitari"]
)


def normalizza_tipologia(tipologia: str):

    mapping = {
        "mortalita": "mortalità",
        "mortalità": "mortalità",
        "dimissioni": "dimissioni"
    }

    return mapping.get(
        tipologia,
        tipologia
    )



def _row_to_doc(r: models.DatoSanitario) -> dict:

    return {
        "tipologia": r.tipologia,
        "patologia": r.patologia,
        "sesso": r.sesso,
        "anno": r.anno,
        "provincia": r.provincia,
        "provincia_nome": r.provincia_nome,
        "valore": r.valore,
    }



@router.get(
    "/patologie",
    response_model=List[str]
)
def patologie_disponibili(
    db: Session = Depends(get_db)
):

    rows = (
        db.query(
            models.DatoSanitario.patologia
        )
        .distinct()
        .all()
    )

    return sorted(
        {
            r[0]
            for r in rows
            if r[0]
        }
    )



@router.get(
    "/dati",
    response_model=List[schemas.DatoSanitarioDoc]
)
def dati_sanitari(
    tipologia: str = Query(...),
    patologia: str = Query(...),
    ordina_desc: bool = Query(False),
    db: Session = Depends(get_db)
):

    tipologia_db = normalizza_tipologia(
        tipologia
    )


    q = (
        db.query(
            models.DatoSanitario
        )
        .filter(
            models.DatoSanitario.tipologia == tipologia_db,
            models.DatoSanitario.patologia == patologia
        )
    )


    if ordina_desc:
        q = q.order_by(
            models.DatoSanitario.anno.desc()
        )
    else:
        q = q.order_by(
            models.DatoSanitario.anno.asc()
        )


    return [
        _row_to_doc(r)
        for r in q.all()
    ]
