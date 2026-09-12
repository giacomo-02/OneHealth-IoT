import time
import board
import adafruit_dht


DHT_PIN = board.D17

dht = adafruit_dht.DHT11(DHT_PIN)


print("Test DHT11")
print("CTRL+C per terminare")


try:
    while True:

        try:
            temperatura = dht.temperature
            umidita = dht.humidity

            print("----------------")
            print(f"Temperatura: {temperatura} °C")
            print(f"Umidità: {umidita} %")

        except RuntimeError as e:
            print("Errore lettura DHT11:", e)

        time.sleep(3)


except KeyboardInterrupt:
    print("\nTerminato")

finally:
    dht.exit()
