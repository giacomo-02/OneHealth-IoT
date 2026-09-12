import json
import paho.mqtt.client as mqtt



BROKER = "broker.hivemq.com"

PORT = 1883



def publish(topic, data):

    client = mqtt.Client()

    client.connect(
        BROKER,
        PORT
    )


    payload = json.dumps(data)


    result = client.publish(
        topic,
        payload
    )

    print(
        "MQTT publish:",
        result.rc,
        topic
    )


    client.disconnect()
