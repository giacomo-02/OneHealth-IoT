import time
from datetime import datetime

from boe_config import BOE
from sensor_generator import generate_measurements
from water_quality import analyze_water
from mqtt_publisher import publish
import boe_movement



def calculate_risk(boa):

    provincia = boa.get(
        "provincia",
        ""
    )


    # zone industriali / portuali simulate
    high_risk = [
        "Taranto",
        "Brindisi",
        "Manfredonia"
    ]


    if provincia in high_risk:
        return 0.7


    return 0.1



while True:


    # Missioni attive lette una volta per ciclo (per muovere le boe assegnate)
    missioni = boe_movement.carica_missioni_attive()


    for BOA in BOE:


        # Posizione aggiornata: verso il target se in missione, altrimenti base
        pos_lat, pos_lon = boe_movement.posizione_corrente(
            BOA,
            missioni
        )


        risk = calculate_risk(
            BOA
        )


        measurements = generate_measurements(
            risk=risk,
            zona=BOA.get(
                "zona",
                "Costa Puglia"
            )
        )


        analysis = analyze_water(
            measurements
        )


        data = {

            "device": {

                "id": BOA["id"],

                "nome": BOA["nome"],

                "comune": BOA["comune"],

                "provincia": BOA["provincia"],

                "zona": BOA.get(
                    "zona",
                    "Costa Puglia"
                ),

                "tipo": BOA.get(
                    "tipo",
                    "fissa"
                ),

                "lat": pos_lat,

                "lon": pos_lon

            },


            "timestamp":
                datetime.now().isoformat(),


            "measurements":
                measurements,


            "analysis":
                analysis
        }



        print(
            BOA["id"],
            BOA["nome"],
            "risk=",
            risk,
            analysis
        )



        publish(

            f"onehealth/water/{BOA['id']}",

            data

        )


    time.sleep(10)
