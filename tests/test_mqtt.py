import json

import paho.mqtt.client as mqtt


BROKER = "broker.hivemq.com"

TOPIC = "onehealth/test"


def on_connect(client, userdata, flags, reason_code, properties=None):

    print("Connesso")

    client.publish(

        TOPIC,

        json.dumps({"test": True})

    )

    client.disconnect()


client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect

client.connect(

    BROKER,

    1883

)

client.loop_forever()

print("OK - MQTT")
