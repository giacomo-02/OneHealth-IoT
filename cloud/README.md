# cloud

## Description

The `cloud` folder contains the component responsible for receiving data from the simulated IoT buoys.

It implements an MQTT Subscriber that connects to the HiveMQ broker, subscribes to the buoys' topics, and collects the water quality measurements.

## Features

- Connection to the public HiveMQ MQTT broker.
- Subscription to the IoT buoys' topics.
- Reception of environmental data published by the edge.
- Decoding of received messages.
- Sending data to the backend for storage in the PostgreSQL database.

## Component Flow

1. The IoT buoys publish data via the MQTT protocol.
2. The subscriber receives messages from the HiveMQ broker.
3. The data is processed and sent to the backend.
4. The backend stores the information in the PostgreSQL database.

## File Structure

- `subscriber.py` — Implements the MQTT subscriber client: handles the connection to the broker, topic subscription, and reception of messages from the buoys.

## Technologies Used

- Python
- MQTT
- HiveMQ Broker
- Paho MQTT Client
