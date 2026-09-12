from typing import Optional

from backend.schemas.base_schema import BaseSchema



class DatoSanitarioDoc(BaseSchema):

    tipologia: str

    patologia: str

    sesso: str

    anno: int

    provincia: str

    provincia_nome: str

    valore: Optional[float] = None
