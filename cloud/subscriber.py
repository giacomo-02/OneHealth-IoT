import json
import paho.mqtt.client as mqtt



from backend.database import SessionLocal

from backend.services.water_service import save_water_data




BROKER = "broker.hivemq.com"

PORT = 1883


TOPIC = "onehealth/water/#"





def on_message(
    client,
    userdata,
    msg
):


    try:


        data = json.loads(
            msg.payload.decode()
        )


        print("\nRicevuto:")
        print(data)



        db = SessionLocal()


        try:

            save_water_data(
                db,
                data
            )


            print(
                "✔ Salvato database"
            )


        finally:

            db.close()



    except Exception as e:

        print(
            "Errore:",
            e
        )





client = mqtt.Client()


client.on_message = on_message



client.connect(
    BROKER,
    PORT
)



client.subscribe(
    TOPIC
)


print(
    "Subscriber attivo..."
)


client.loop_forever()
