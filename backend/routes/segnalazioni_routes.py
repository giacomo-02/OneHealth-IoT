import os
import uuid

from datetime import datetime
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    File,
    Form
)

from sqlalchemy import func
from sqlalchemy.orm import Session

from PIL import Image, ImageOps

from backend.database import get_db

from backend.models import Segnalazione

from backend.schemas import (
    SegnalazioneDoc,
    AggiornaStatoBody,
    AggiornaPosizioneBody
)


router = APIRouter(
    prefix="/segnalazioni",
    tags=["segnalazioni"]
)


UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)



def _row_to_doc(r: Segnalazione):

    return {

        "_id": str(r.id),

        "id": r.id,

        "timestamp": r.timestamp,

        "tipo": r.tipo,

        "descrizione": r.descrizione,

        "gravita": r.gravita,

        "stato": r.stato,

        "nome": r.nome,

        "latitudine": r.latitudine,

        "longitudine": r.longitudine,

        "posizione_testo": r.posizione_testo,

        "accuratezza_m": r.accuratezza_m,

        "foto": r.foto

    }



# =====================================================
# CREAZIONE DA APP MOBILE
# =====================================================

@router.post(
    "/invia"
)
async def crea_segnalazione_mobile(

    tipo: str = Form(...),

    descrizione: str = Form(None),

    gravita: str = Form(None),

    nome: str = Form(None),

    posizione_testo: str = Form(None),

    lat: str = Form(None),

    lon: str = Form(None),

    acc: str = Form(None),

    foto: UploadFile = File(None),

    db: Session = Depends(get_db)

):


    foto_nome = None


    if foto and foto.filename:


        foto_nome = (
            uuid.uuid4().hex
            +
            ".jpg"
        )


        path = os.path.join(
            UPLOAD_DIR,
            foto_nome
        )


        img = Image.open(
            foto.file
        )


        img = ImageOps.exif_transpose(
            img
        )


        img = img.convert(
            "RGB"
        )


        img.save(
            path,
            "JPEG",
            quality=85
        )



    nuova = Segnalazione(

        timestamp=datetime.now(),

        tipo=tipo,

        descrizione=descrizione,

        gravita=gravita,

        stato="nuova",

        nome=nome,

        posizione_testo=posizione_testo,

        foto=foto_nome

    )


    # Priorità alla località scritta a mano: se l'utente ha compilato il campo
    # testo, quella ha la precedenza e il GPS NON viene usato come posizione
    # operativa (l'operatore geocodifica il testo dalla dashboard, con offset
    # verso il mare). Il GPS diventa posizione solo se il testo è vuoto.
    testo_presente = bool(posizione_testo and posizione_testo.strip())

    if not testo_presente:

        if lat:

            nuova.latitudine = float(lat)


        if lon:

            nuova.longitudine = float(lon)


        if acc:

            nuova.accuratezza_m = float(acc)



    db.add(nuova)

    db.commit()

    db.refresh(nuova)



    return {

        "ok": True,

        "id": nuova.id

    }





# =====================================================
# API USATE DALLA DASHBOARD
# =====================================================


@router.get(
    "/nuove-count",
    response_model=int
)
def conta_nuove(
    db: Session = Depends(get_db)
):

    return (

        db.query(
            func.count(Segnalazione.id)
        )

        .filter(
            Segnalazione.stato == "nuova"
        )

        .scalar()

        or 0

    )



@router.get(
    "",
    response_model=List[SegnalazioneDoc]
)
def lista_segnalazioni(

    stati: Optional[List[str]] = Query(None),

    limit: int = Query(300, le=1000),

    db: Session = Depends(get_db)

):


    query = db.query(
        Segnalazione
    )


    if stati:

        query = query.filter(
            Segnalazione.stato.in_(stati)
        )


    query = (

        query

        .order_by(
            Segnalazione.timestamp.desc()
        )

        .limit(limit)

    )


    return [

        _row_to_doc(r)

        for r in query.all()

    ]



@router.patch(
    "/{segnalazione_id}/stato"
)
def aggiorna_stato(

    segnalazione_id: int,

    body: AggiornaStatoBody,

    db: Session = Depends(get_db)

):

    seg = (

        db.query(
            Segnalazione
        )

        .filter(
            Segnalazione.id == segnalazione_id
        )

        .first()

    )


    if not seg:

        raise HTTPException(
            status_code=404,
            detail="Segnalazione non trovata"
        )


    seg.stato = body.stato

    db.commit()


    return {
        "ok": True
    }




@router.patch(
    "/{segnalazione_id}/posizione"
)
def aggiorna_posizione(

    segnalazione_id: int,

    body: AggiornaPosizioneBody,

    db: Session = Depends(get_db)

):

    seg = (

        db.query(
            Segnalazione
        )

        .filter(
            Segnalazione.id == segnalazione_id
        )

        .first()

    )


    if not seg:

        raise HTTPException(
            status_code=404,
            detail="Segnalazione non trovata"
        )


    seg.latitudine = body.latitudine

    seg.longitudine = body.longitudine

    seg.accuratezza_m = body.accuratezza_m


    db.commit()


    return {
        "ok": True
    }
