from backend.database import SessionLocal
from backend.models.water_model import WaterDevice

from edge.boe_config import BOE


def update_boe():

    db = SessionLocal()

    try:

        for boa in BOE:

            device = (
                db.query(WaterDevice)
                .filter(
                    WaterDevice.device_id == boa["id"]
                )
                .first()
            )

            if device:

                device.nome = boa["nome"]
                device.comune = boa["comune"]
                device.provincia = boa["provincia"]
                device.zona = boa.get(
                    "zona",
                    "Costa Puglia"
                )
                device.tipo = boa["tipo"]
                device.lat = boa["lat"]
                device.lon = boa["lon"]

                print(
                    f"Aggiornata {boa['id']} -> {boa['tipo']}"
                )


            else:

                device = WaterDevice(

                    device_id=boa["id"],
                    nome=boa["nome"],
                    comune=boa["comune"],
                    provincia=boa["provincia"],
                    zona=boa.get(
                        "zona",
                        "Costa Puglia"
                    ),
                    tipo=boa["tipo"],
                    lat=boa["lat"],
                    lon=boa["lon"]

                )

                db.add(device)

                print(
                    f"Inserita {boa['id']} -> {boa['tipo']}"
                )


        db.commit()


    finally:

        db.close()



if __name__ == "__main__":
    update_boe()
