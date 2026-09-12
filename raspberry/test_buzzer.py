from gpiozero import Buzzer
from time import sleep

BUZZER_PIN = 26

buzzer = Buzzer(
    BUZZER_PIN,
    active_high=False
)

try:
    print("Buzzer ON")

    buzzer.on()
    sleep(3)

    print("Buzzer OFF")

    buzzer.off()

finally:
    buzzer.close()
