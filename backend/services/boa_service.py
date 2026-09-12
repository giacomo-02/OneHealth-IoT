from backend.models.water_model import (
    WaterDevice,
    WaterMeasurement
)

from datetime import datetime, timedelta


def get_all_devices(db):

    return (
        db.query(WaterDevice)
        .all()
    )



def get_latest_measurement(
    db,
    device_id
):

    return (
        db.query(WaterMeasurement)
        .filter(
            WaterMeasurement.device_id == device_id
        )
        .order_by(
            WaterMeasurement.timestamp.desc()
        )
        .first()
    )



def get_history(
    db,
    device_id
):

    return (
        db.query(WaterMeasurement)
        .filter(
            WaterMeasurement.device_id == device_id
        )
        .order_by(
            WaterMeasurement.timestamp.asc()
        )
        .all()
    )



def get_latest_boe(db, tipo_boa=None):

    query = db.query(WaterDevice)

    # Filtro per tipo ("fissa" / "deriva"): serve alla dashboard per
    # assegnare le missioni SOLO alle boe a deriva.
    if tipo_boa:
        query = query.filter(
            WaterDevice.tipo == tipo_boa
        )

    devices = query.all()

    result = []


    for device in devices:

        measurement = (
            db.query(WaterMeasurement)
            .filter(
                WaterMeasurement.device_id ==
                device.device_id
            )
            .order_by(
                WaterMeasurement.timestamp.desc()
            )
            .first()
        )


        if measurement is None:
            continue


        result.append({

            "timestamp":
                measurement.timestamp.isoformat(),


            "id_boa":
                device.device_id,


            "nome_boa":
                device.nome,


            "comune":
                device.comune,


            "provincia":
                device.provincia,


            "tipo_boa":
                device.tipo,


            "latitudine":
                device.lat,


            "longitudine":
                device.lon,


            "sensori":{

                "ph":
                    measurement.ph,

                "temperatura_c":
                    measurement.temperature,

                "torbidita_ntu":
                    measurement.turbidity,

                "conducibilita_ms_cm":
                    measurement.conductivity,

                "ossigeno_disciolto_mg_l":
                    measurement.dissolved_oxygen,

                "nitrati_mg_l":
                    measurement.nitrates,

                "ecoli_ufc_100ml":
                    measurement.ecoli,

                "enterococchi_ufc_100ml":
                    measurement.enterococci,

                "piombo_ug_l":
                    measurement.lead,

                "mercurio_ug_l":
                    measurement.mercury,

                "arsenico_ug_l":
                    measurement.arsenic,

                "cadmio_ug_l":
                    measurement.cadmium,

                "cloro_mg_l":
                    measurement.chlorine,

                "orp_mv":
                    measurement.orp,

                "fosfati_mg_l":
                    getattr(
                        measurement,
                        "phosphates",
                        None
                    ),

                "clorofilla_a_ug_l":
                    getattr(
                        measurement,
                        "chlorophyll_a",
                        None
                    )
            },


            "alert":[],

            "ha_alert":False,


            "classificazione":
                measurement.status

        })


    return result




def get_measurements(
    db,
    ore=None,
    province=None,
    tipi=None
):


    query = (
        db.query(
            WaterMeasurement,
            WaterDevice
        )
        .join(
            WaterDevice,
            WaterMeasurement.device_id ==
            WaterDevice.device_id
        )
    )


    if ore:

        limite = datetime.now() - timedelta(hours=ore)

        query = query.filter(
            WaterMeasurement.timestamp >= limite
        )


    if province:

        query = query.filter(
            WaterDevice.provincia.in_(province)
        )


    if tipi:

        query = query.filter(
            WaterDevice.tipo.in_(tipi)
        )



    rows = (
        query
        .order_by(
            WaterMeasurement.timestamp.desc()
        )
        .all()
    )


    docs = []


    for measurement, device in rows:


        docs.append({

            "timestamp":
                measurement.timestamp.isoformat(),


            "id_boa":
                device.device_id,


            "nome_boa":
                device.nome,


            "comune":
                device.comune,


            "provincia":
                device.provincia,


            "tipo_boa":
                device.tipo,


            "latitudine":
                device.lat,


            "longitudine":
                device.lon,


            "sensori":{

                "ph":
                    measurement.ph,

                "temperatura_c":
                    measurement.temperature,

                "torbidita_ntu":
                    measurement.turbidity,

                "conducibilita_ms_cm":
                    measurement.conductivity,

                "ossigeno_disciolto_mg_l":
                    measurement.dissolved_oxygen,

                "nitrati_mg_l":
                    measurement.nitrates,

                "ecoli_ufc_100ml":
                    measurement.ecoli,

                "enterococchi_ufc_100ml":
                    measurement.enterococci,

                "piombo_ug_l":
                    measurement.lead,

                "mercurio_ug_l":
                    measurement.mercury,

                "arsenico_ug_l":
                    measurement.arsenic,

                "cadmio_ug_l":
                    measurement.cadmium,

                "cloro_mg_l":
                    measurement.chlorine,

                "orp_mv":
                    measurement.orp,

                "fosfati_mg_l":
                    getattr(
                        measurement,
                        "phosphates",
                        None
                    ),

                "clorofilla_a_ug_l":
                    getattr(
                        measurement,
                        "chlorophyll_a",
                        None
                    )
            },


            "alert":[],

            "ha_alert":False,


            "classificazione":
                measurement.status

        })


    return docs
