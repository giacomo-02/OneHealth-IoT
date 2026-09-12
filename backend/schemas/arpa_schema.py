from datetime import datetime
from typing import List, Optional

from backend.schemas.base_schema import BaseSchema



class SensoriArpa(BaseSchema):

    ecoli_ufc_100ml: Optional[float] = None

    enterococchi_ufc_100ml: Optional[float] = None



class ArpaDoc(BaseSchema):

    timestamp: datetime

    codice: str

    provincia: Optional[str] = None

    comune: Optional[str] = None

    denominazione: Optional[str] = None

    latitudine: Optional[float] = None

    longitudine: Optional[float] = None

    sensori: SensoriArpa

    alert: List[str] = []

    ha_alert: bool = False

    classificazione: Optional[str] = None



class ArpaMisurazioniResponse(BaseSchema):

    docs: List[ArpaDoc]

    tot: int

    n_alert: int



class ArpaAggregatoRow(BaseSchema):

    provincia: str

    anno: int

    ecoli_medio: Optional[float] = None

    entero_medio: Optional[float] = None

    n_campioni: int
