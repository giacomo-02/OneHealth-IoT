# edge

## Description

The `edge` folder contains the IoT component of the OneHealth-IoT system. It represents the software running on the marine buoys and handles the generation, analysis, and publication of water quality data.

In this project, buoy behavior is simulated through Python scripts that generate environmental measurements, compute a local water quality indication, and send the data via the MQTT protocol.

## Component Flow

1. Buoy configurations are loaded from `boe_config.py`.
2. Sensor measurements are generated via `sensor_generator.py`.
3. Environmental parameters are analyzed locally via `water_quality.py`.
4. The buoy's full data payload is published via MQTT to the HiveMQ broker.
5. The `cloud` component receives the published data and stores it in the system.

## File Structure

- `main.py` — Entry point of the component, managing the buoys' main loop.
- `boe_config.py` — Configuration of the simulated buoys and their geographic information.
- `sensor_generator.py` — Generation of simulated environmental sensor values.
- `water_quality.py` — Local analysis of water quality parameters.
- `mqtt_publisher.py` — Handles data publishing via the MQTT protocol.
- `update_boe_config.py` — Utility for updating the buoy configuration.

## Technologies Used

- Python
- MQTT
- HiveMQ Broker
- Paho MQTT Client
- Raspberry Pi (edge device simulation)
