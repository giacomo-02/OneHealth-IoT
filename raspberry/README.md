# raspberry

## Description

This component represents the Raspberry Pi device used for local collection of environmental data.

The Raspberry Pi integrates physical sensors for monitoring water and ambient temperature, along with actuators to provide local feedback on water quality status.

## Features

- Reading from the DS18B20 water temperature sensor.
- Reading ambient temperature and humidity via DHT11.
- Managing the KY-016 RGB LED to indicate water quality status.
- Managing the buzzer for alarm signals.
- Local status evaluation via simulated thresholds.

## File Structure

- `boa_raspberry.py` — Main script: integrates the sensors and actuators on the real device.
- `test_buzzer.py` — Test for the alarm buzzer.
- `test_dht11.py` — Test for the DHT11 temperature and humidity sensor.
- `test_rgb.py` — Test for the KY-016 RGB LED.
- `test_temperature.py` — Test for the DS18B20 water temperature sensor.
- `requirements.txt` — List of Python dependencies required on the device.

## Technologies Used

- Raspberry Pi
- Python
- DS18B20
- DHT11
- KY-016 RGB LED
- Buzzer
- GPIO Zero
- Adafruit CircuitPython
