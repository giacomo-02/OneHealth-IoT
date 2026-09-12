from datetime import datetime
from typing import Optional

from backend.schemas.base_schema import BaseSchema



class SegnalazioneDoc(BaseSchema):

    id: int

    timestamp: datetime

    tipo: Optional[str] = None

    descrizione: Optional[str] = None

    gravita: Optional[str] = None

    stato: str = "nuova"

    nome: Optional[str] = None

    latitudine: Optional[float] = None

    longitudine: Optional[float] = None

    posizione_testo: Optional[str] = None

    accuratezza_m: Optional[float] = None

    foto: Optional[str] = None



class AggiornaStatoBody(BaseSchema):

    stato: str



class AggiornaPosizioneBody(BaseSchema):

    latitudine: float

    longitudine: float

    accuratezza_m: Optional[float] = None
