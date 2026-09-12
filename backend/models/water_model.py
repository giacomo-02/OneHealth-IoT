from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class WaterDevice(Base):

    __tablename__ = "water_devices"

    id = Column(Integer, primary_key=True, index=True)

    device_id = Column(String, unique=True, index=True, nullable=False)

    nome = Column(String)

    comune = Column(String)

    provincia = Column(String)

    zona = Column(String)

    lat = Column(Float)

    lon = Column(Float)

    tipo = Column(String)

    measurements = relationship(
        "WaterMeasurement",
        back_populates="device"
    )



class WaterMeasurement(Base):

    __tablename__ = "water_measurements"

    id = Column(Integer, primary_key=True)

    device_id = Column(
        String,
        ForeignKey("water_devices.device_id")
    )

    timestamp = Column(DateTime)

    # Parametri fisici
    ph = Column(Float)

    temperature = Column(Float)

    turbidity = Column(Float)

    conductivity = Column(Float)

    dissolved_oxygen = Column(Float)


    # Nutrienti
    nitrates = Column(Float)

    phosphates = Column(Float)

    chlorophyll_a = Column(Float)


    # Microbiologia
    ecoli = Column(Integer)

    enterococci = Column(Integer)


    # Metalli pesanti
    arsenic = Column(Float)

    lead = Column(Float)

    mercury = Column(Float)

    cadmium = Column(Float)


    # Chimica
    chlorine = Column(Float)

    orp = Column(Float)


    # Indici
    wqi = Column(Float)

    status = Column(String)


    device = relationship(
        "WaterDevice",
        back_populates="measurements"
    )



class WaterAlert(Base):

    __tablename__ = "water_alerts"

    id = Column(
        Integer,
        primary_key=True
    )

    device_id = Column(String, index=True)

    nome_boa = Column(String)

    comune = Column(String)

    provincia = Column(String)

    latitudine = Column(Float)

    longitudine = Column(Float)

    timestamp = Column(DateTime, index=True)

    livello = Column(String)          # "allerta" | "critico"

    parametri = Column(String)        # quali criticita' (es. "E.coli 1200 UFC/100mL")

    classificazione = Column(String)  # stato WQI al momento dell'alert

    wqi = Column(Float)
