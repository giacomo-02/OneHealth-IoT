from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
)

from backend.database import Base



class Segnalazione(Base):

    __tablename__ = "segnalazioni"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    timestamp = Column(
        DateTime,
        nullable=False,
        index=True
    )


    tipo = Column(String)


    descrizione = Column(String)


    gravita = Column(
        String,
        index=True
    )


    stato = Column(
        String,
        default="nuova",
        index=True
    )


    nome = Column(String)


    latitudine = Column(Float)


    longitudine = Column(Float)


    posizione_testo = Column(String)


    accuratezza_m = Column(Float)


    foto = Column(String)
