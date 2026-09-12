from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy import func

from sqlalchemy.orm import Session


from backend.database import get_db

from backend.models import Missione

from backend.schemas import (
    MissioneDoc,
    NuovaMissioneBody
)



router = APIRouter(
    prefix="/missioni",
    tags=["missioni"]
)



def _row_to_doc(r: Missione):

    return {

        "id": r.id,

        "id_boa": r.id_boa,

        "nome_boa": r.nome_boa,

        "target_lat": r.target_lat,

        "target_lon": r.target_lon,

        "segnalazione_id": r.segnalazione_id,

        "stato": r.stato,

        "timestamp": r.timestamp,

        "distanza_km": r.distanza_km

    }



@router.get(
    "/attive",
    response_model=List[MissioneDoc]
)
def missioni_attive(

    db: Session = Depends(get_db)

):

    rows = (

        db.query(
            Missione
        )

        .filter(

            Missione.stato.in_(
                [
                    "attiva",
                    "ritorno"
                ]
            )

        )

        .all()

    )


    return [
        _row_to_doc(r)
        for r in rows
    ]



@router.get(
    "/completate-count",
    response_model=int
)
def missioni_completate_count(

    db: Session = Depends(get_db)

):

    return (

        db.query(
            func.count(Missione.id)
        )

        .filter(
            Missione.stato == "completata"
        )

        .scalar()

        or 0

    )



@router.post(
    "",
    response_model=MissioneDoc
)
def crea_missione(

    body: NuovaMissioneBody,

    db: Session = Depends(get_db)

):

    db.query(Missione).filter(

        Missione.id_boa == body.id_boa,

        Missione.stato == "attiva"

    ).delete(
        synchronize_session=False
    )


    nuova = Missione(

        id_boa=body.id_boa,

        nome_boa=body.nome_boa,

        target_lat=body.target_lat,

        target_lon=body.target_lon,

        segnalazione_id=body.segnalazione_id,

        stato="attiva",

        timestamp=datetime.now(),

        distanza_km=body.distanza_km

    )


    db.add(nuova)

    db.commit()

    db.refresh(nuova)


    return _row_to_doc(nuova)



@router.patch(
    "/{id_boa}/stato"
)
def aggiorna_stato_missione(

    id_boa: str,

    stato: str = Query(...),

    db: Session = Depends(get_db)

):
    """Aggiorna lo stato della missione in corso di una boa.
    Usato dall'edge per: attiva -> ritorno (target raggiunto) -> completata (base)."""

    miss = (

        db.query(Missione)

        .filter(

            Missione.id_boa == id_boa,

            Missione.stato.in_(
                [
                    "attiva",
                    "ritorno"
                ]
            )

        )

        .order_by(
            Missione.timestamp.desc()
        )

        .first()

    )


    if not miss:

        raise HTTPException(
            status_code=404,
            detail="Missione in corso non trovata"
        )


    miss.stato = stato

    db.commit()


    return {
        "ok": True,
        "id_boa": id_boa,
        "stato": stato
    }



@router.post(
    "/annulla-per-segnalazione/{segnalazione_id}"
)
def annulla_per_segnalazione(

    segnalazione_id: int,

    db: Session = Depends(get_db)

):

    boe_ids = [

        r.id_boa

        for r in (

            db.query(
                Missione.id_boa
            )

            .filter(

                Missione.segnalazione_id == segnalazione_id,

                Missione.stato == "attiva"

            )

            .all()

        )

    ]


    if boe_ids:

        (

            db.query(Missione)

            .filter(

                Missione.id_boa.in_(boe_ids),

                Missione.stato.in_(
                    [
                        "attiva",
                        "ritorno"
                    ]
                )

            )

            .update(

                {
                    "stato": "annullata"
                },

                synchronize_session=False

            )

        )


        db.commit()



    return {

        "ok": True,

        "boe_annullate": boe_ids

    }
