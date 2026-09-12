#!/usr/bin/env python3

import time

SENSOR_ID = "28-0517b1be15ff"
SENSOR_PATH = f"/sys/bus/w1/devices/{SENSOR_ID}/w1_slave"


def read_temperature():
    try:
        with open(SENSOR_PATH, "r") as file:
            lines = file.readlines()

        # controllo CRC
        if "YES" not in lines[0]:
            return None

        # estrazione temperatura
        temp_string = lines[1].split("t=")[1]
        temperature = float(temp_string) / 1000.0

        return temperature

    except Exception as e:
        print(f"Errore lettura sensore: {e}")
        return None


print("Avvio lettura DS18B20...")
print("Premere CTRL+C per terminare\n")


try:
    while True:
        temperature = read_temperature()

        if temperature is not None:
            print(f"Temperatura: {temperature:.2f} °C")
        else:
            print("Lettura non valida")

        time.sleep(3)

except KeyboardInterrupt:
    print("\nLettura terminata manualmente.")
