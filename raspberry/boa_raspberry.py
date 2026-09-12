#!/usr/bin/env python3

import time
import board
import adafruit_dht

from gpiozero import LED, Buzzer


# =====================================================
# CONFIGURAZIONE SENSORI
# =====================================================

# DS18B20
SENSOR_ID = "28-0517b1be15ff"
SENSOR_PATH = f"/sys/bus/w1/devices/{SENSOR_ID}/w1_slave"


# DHT11
DHT_PIN = board.D17


# KY-016 RGB
RED_PIN = 21
GREEN_PIN = 20
BLUE_PIN = 16


# Buzzer
BUZZER_PIN = 26


# =====================================================
# INIZIALIZZAZIONE
# =====================================================

dht = adafruit_dht.DHT11(DHT_PIN)

red = LED(RED_PIN)
green = LED(GREEN_PIN)
blue = LED(BLUE_PIN)

buzzer = Buzzer(
    BUZZER_PIN,
    active_high=False
)


# =====================================================
# LETTURA DS18B20
# =====================================================

def read_ds18b20():

    try:

        with open(SENSOR_PATH, "r") as file:
            lines = file.readlines()


        if len(lines) < 2:
            return None


        # controllo CRC
        if "YES" not in lines[0]:
            return None


        if "t=" not in lines[1]:
            return None


        temp_string = lines[1].split("t=")[1]

        temperature = float(temp_string) / 1000.0


        return temperature


    except Exception as e:

        print("Errore DS18B20:", e)
        return None



# =====================================================
# RGB
# =====================================================

def rgb_off():

    red.off()
    green.off()
    blue.off()



def set_rgb(color):

    rgb_off()


    if color == "GREEN":

        green.on()


    elif color == "YELLOW":

        red.on()
        green.on()


    elif color == "RED":

        red.on()



# =====================================================
# BUZZER
# =====================================================

def set_alarm(active):

    if active:

        buzzer.on()

    else:

        buzzer.off()



# =====================================================
# LOGICA QUALITA'
# =====================================================

def evaluate_status(temp):

    if temp is None:

        return "UNKNOWN"


    # simulazione WQI
    if temp < 25:

        return "GREEN"


    elif temp < 30:

        return "YELLOW"


    else:

        return "RED"



# =====================================================
# MAIN
# =====================================================

print("==============================")
print("Simulazione boa IoT")
print("DS18B20 + DHT11 + RGB + BUZZER")
print("CTRL+C per terminare")
print("==============================")


last_water_temperature = None


try:


    while True:


        # -----------------------------
        # Temperatura acqua DS18B20
        # -----------------------------

        new_temperature = read_ds18b20()


        if new_temperature is not None:

            last_water_temperature = new_temperature


        water_temperature = last_water_temperature


        time.sleep(0.2)



        # -----------------------------
        # DHT11
        # -----------------------------

        try:

            air_temperature = dht.temperature
            humidity = dht.humidity


        except RuntimeError:

            air_temperature = None
            humidity = None



        # -----------------------------
        # Stato sistema
        # -----------------------------

        status = evaluate_status(water_temperature)



        if status == "GREEN":

            set_rgb("GREEN")
            set_alarm(False)



        elif status == "YELLOW":

            set_rgb("YELLOW")
            set_alarm(False)



        elif status == "RED":

            set_rgb("RED")
            set_alarm(True)



        else:

            set_rgb("YELLOW")
            set_alarm(False)



        # -----------------------------
        # Output
        # -----------------------------

        print("------------------------------")


        if water_temperature is not None:

            print(
                f"Temperatura acqua: "
                f"{water_temperature:.2f} °C"
            )

        else:

            print(
                "Temperatura acqua non disponibile"
            )



        if air_temperature is not None:

            print(
                f"Temperatura ambiente: "
                f"{air_temperature:.1f} °C"
            )


        if humidity is not None:

            print(
                f"Umidità: {humidity:.0f}%"
            )


        print(
            f"Stato WQI simulato: {status}"
        )



        if status == "RED":

            print(
                "!!! ALLARME TEMPERATURA !!!"
            )


        print("------------------------------")


        time.sleep(3)



except KeyboardInterrupt:

    print("\nSistema terminato")



finally:


    dht.exit()

    red.close()
    green.close()
    blue.close()

    buzzer.close()
