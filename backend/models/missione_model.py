from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    DateTime,
    String,
)

from backend.database import Base



class Missione(Base):

    __tablename__ = "missioni"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    id_boa = Column(
        String,
        nullable=False,
        index=True
    )


    nome_boa = Column(String)


    target_lat = Column(Float)


    target_lon = Column(Float)


    segnalazione_id = Column(
        Integer,
        ForeignKey(
            "segnalazioni.id"
        ),
        nullable=True
    )


    stato = Column(
        String,
        default="attiva",
        index=True
    )


    timestamp = Column(
        DateTime,
        nullable=False,
        index=True
    )


    distanza_km = Column(Float)
