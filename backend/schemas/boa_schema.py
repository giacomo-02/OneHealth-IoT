from datetime import datetime
from typing import List, Optional

from backend.schemas.base_schema import BaseSchema



class SensoriBoa(BaseSchema):
    ph: Optional[float] = None
    temperatura_c: Optional[float] = None
    torbidita_ntu: Optional[float] = None
    conducibilita_ms_cm: Optional[float] = None
    ossigeno_disciolto_mg_l: Optional[float] = None
    ecoli_ufc_100ml: Optional[float] = None
    enterococchi_ufc_100ml: Optional[float] = None
    clorofilla_a_ug_l: Optional[float] = None
    nitrati_mg_l: Optional[float] = None
    fosfati_mg_l: Optional[float] = None
    piombo_ug_l: Optional[float] = None
    mercurio_ug_l: Optional[float] = None
    arsenico_ug_l: Optional[float] = None
    cadmio_ug_l: Optional[float] = None
    orp_mv: Optional[float] = None



class BoaDoc(BaseSchema):

    timestamp: datetime

    id_boa: str

    nome_boa: Optional[str] = None

    comune: Optional[str] = None

    provincia: Optional[str] = None

    tipo_boa: Optional[str] = None

    latitudine: Optional[float] = None

    longitudine: Optional[float] = None


    sensori: SensoriBoa


    alert: List[str] = []

    ha_alert: bool = False

    classificazione: Optional[str] = None



class BoeMisurazioniResponse(BaseSchema):

    docs: List[BoaDoc]

    tot_db: int

    n_alert: int

    fallback: bool
