from gpiozero import LED
from time import sleep


RED_PIN = 21
GREEN_PIN = 20
BLUE_PIN = 16


red = LED(RED_PIN)
green = LED(GREEN_PIN)
blue = LED(BLUE_PIN)


def verde():
    red.off()
    green.on()
    blue.off()


def giallo():
    red.on()
    green.on()
    blue.off()


def rosso():
    red.on()
    green.off()
    blue.off()


print("==============================")
print("Test KY-016 Stati WQI")
print("CTRL+C per terminare")
print("==============================")


try:
    while True:

        print("QUALITA BUONA - VERDE")
        verde()
        sleep(3)

        print("ATTENZIONE - GIALLO")
        giallo()
        sleep(3)

        print("ALLARME - ROSSO")
        rosso()
        sleep(3)


except KeyboardInterrupt:
    print("\nTerminato")


finally:
    red.close()
    green.close()
    blue.close()
