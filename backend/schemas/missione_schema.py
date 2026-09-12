from datetime import datetime
from typing import Optional

from backend.schemas.base_schema import BaseSchema



class MissioneDoc(BaseSchema):

    id: int

    id_boa: str

    nome_boa: Optional[str] = None

    target_lat: float

    target_lon: float

    segnalazione_id: Optional[int] = None

    stato: str

    timestamp: datetime

    distanza_km: Optional[float] = None



class NuovaMissioneBody(BaseSchema):

    id_boa: str

    nome_boa: Optional[str] = None

    target_lat: float

    target_lon: float

    segnalazione_id: Optional[int] = None

    distanza_km: Optional[float] = None
