from typing import Optional

from fastapi import APIRouter, Depends, Query

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database import get_db

from backend.models.water_model import WaterAlert


router = APIRouter(
    prefix="/alerts",
    tags=["alerts"]
)


def _row_to_doc(a: WaterAlert):

    return {

        "id": a.id,

        "device_id": a.device_id,

        "nome_boa": a.nome_boa,

        "comune": a.comune,

        "provincia": a.provincia,

        "latitudine": a.latitudine,

        "longitudine": a.longitudine,

        "timestamp": a.timestamp.isoformat() if a.timestamp else None,

        "livello": a.livello,

        "parametri": a.parametri,

        "classificazione": a.classificazione,

        "wqi": a.wqi

    }


@router.get("")
def lista_alerts(

    limit: int = Query(300, le=2000),

    livello: Optional[str] = Query(None),

    db: Session = Depends(get_db)

):
    """Storico delle criticita', dal piu' recente. Filtrabile per livello."""

    query = db.query(WaterAlert)

    if livello:
        query = query.filter(WaterAlert.livello == livello)

    rows = (
        query
        .order_by(WaterAlert.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [_row_to_doc(a) for a in rows]


@router.get("/count")
def conta_alerts(
    db: Session = Depends(get_db)
):
    """Numero totale di criticita' registrate."""

    return (
        db.query(func.count(WaterAlert.id)).scalar()
        or 0
    )
