from sqlalchemy import Column, Float, Integer, String

from backend.database import Base


class DatoSanitario(Base):

    __tablename__ = "dati_sanitari"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    tipologia = Column(
        String,
        nullable=False,
        index=True
    )


    patologia = Column(
        String,
        nullable=False,
        index=True
    )


    sesso = Column(
        String,
        nullable=False
    )


    anno = Column(
        Integer,
        nullable=False,
        index=True
    )


    provincia = Column(
        String,
        nullable=False,
        index=True
    )


    provincia_nome = Column(
        String,
        nullable=False
    )


    valore = Column(
        Float,
        nullable=True
    )
