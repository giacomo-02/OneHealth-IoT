from fastapi import APIRouter, Depends

from backend.database import SessionLocal

from backend.services.boa_service import (
    get_all_devices,
    get_latest_measurement,
    get_history,
    get_latest_boe,
    get_measurements
)



router = APIRouter(
    prefix="/boe",
    tags=["boe"]
)



def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



@router.get("/")
def list_boe(
    db = Depends(get_db)
):

    devices = get_all_devices(db)


    return [

        {
            "id": d.device_id,
            "nome": d.nome,
            "comune": d.comune,
            "provincia": d.provincia,
            "zona": d.zona,
            "lat": d.lat,
            "lon": d.lon
        }

        for d in devices

    ]




@router.get("/ultime")
def ultime_boe(
    tipo_boa: str | None = None,
    db = Depends(get_db)
):

    return get_latest_boe(
        db,
        tipo_boa
    )


@router.get("/misurazioni")
def misurazioni(
    ore: int = 24,
    province: list[str] | None = None,
    tipi: list[str] | None = None,
    db = Depends(get_db)
):


    docs = get_measurements(
        db,
        ore,
        province,
        tipi
    )


    return {

        "docs": docs,

        "tot_db":
            len(docs),

        "n_alert":
            sum(
                1
                for d in docs
                if d["ha_alert"]
            ),

        "fallback": False

    }


@router.get("/{device_id}/latest")
def latest(
    device_id: str,
    db = Depends(get_db)
):

    measurement = get_latest_measurement(
        db,
        device_id
    )


    if measurement is None:

        return {
            "error":
            "nessuna misura trovata"
        }



    return {

        "device_id":
            measurement.device_id,

        "timestamp":
            measurement.timestamp,

        "wqi":
            measurement.wqi,

        "status":
            measurement.status,

        "ph":
            measurement.ph,

        "temperature":
            measurement.temperature,

        "turbidity":
            measurement.turbidity,

        "ecoli":
            measurement.ecoli

    }





@router.get("/{device_id}/history")
def history(
    device_id: str,
    db = Depends(get_db)
):

    measurements = get_history(
        db,
        device_id
    )


    return [

        {

            "timestamp": m.timestamp,

            "wqi": m.wqi,

            "status": m.status

        }

        for m in measurements

    ]
