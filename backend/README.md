# backend

## Description

The `backend` folder contains the server-side component of the OneHealth-IoT system.

It is built with FastAPI and serves as the central access point for the data collected by the system. It handles the REST API, communication with the PostgreSQL database, data model management, and the integration of environmental and health information.

## Features

- Managing measurements coming from the IoT buoys.
- Access to ARPA environmental data on water quality.
- Access to HFA/ISTAT health data.
- Managing reports submitted by users.
- Managing operational missions.
- Exposing the REST API used by the dashboard and the mobile application.

## Component Flow

1. The MQTT subscriber receives data published by the IoT buoys.
2. The data is stored in the PostgreSQL database.
3. FastAPI exposes REST endpoints for querying and modifying the information.
4. The dashboard and mobile application use the API to access the data.

## File Structure

- `main.py` — Entry point of the FastAPI application and API registration.
- `database.py` — Configuration of the PostgreSQL database connection.
- `models/` — SQLAlchemy models representing the database tables.
- `schemas/` — Pydantic schemas used for API validation and responses.
- `routes/` — REST endpoints organized by application domain.
- `services/` — Application logic and supporting services.
- `arpa/` — Import and management of the ARPA bathing water dataset.
- `hfa/` — Import and management of the Health For All (ISTAT) health data.

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- Pandas
