from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    JSON,
    String,
)

from backend.database import Base



class ArpaMisurazione(Base):

    __tablename__ = "misurazioni_arpa"


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


    codice = Column(
        String,
        nullable=False,
        index=True
    )


    provincia = Column(
        String,
        index=True
    )


    comune = Column(String)


    denominazione = Column(String)


    latitudine = Column(Float)


    longitudine = Column(Float)


    ecoli_ufc_100ml = Column(Float)


    enterococchi_ufc_100ml = Column(Float)


    alert = Column(
        JSON,
        default=list
    )


    ha_alert = Column(
        Boolean,
        default=False,
        index=True
    )


    classificazione = Column(
        String,
        index=True
    )
