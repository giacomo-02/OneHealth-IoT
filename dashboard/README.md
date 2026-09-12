# dashboard

## Description

The `dashboard` folder contains the visualization component of the OneHealth-IoT system.

It is built with Streamlit and allows visualizing, browsing, and analyzing the data collected by the system, combining environmental information from the IoT buoys, ARPA water quality data, and HFA/ISTAT health data.

## Features

- Visualization of environmental measurements received from the IoT buoys.
- Browsing the historical water quality data.
- Visualization of ARPA bathing water data.
- Analysis of regional health data.
- Identification of possible correlations between environmental and health data.
- Visualization of user reports.

## Component Flow

1. The dashboard makes REST requests to the FastAPI backend.
2. The backend retrieves data from the PostgreSQL database.
3. The data is processed and displayed through Streamlit components.
4. The results can be used for environmental and health analysis.

In short: dashboard -> REST request -> FastAPI backend -> SQLAlchemy query -> PostgreSQL

## File Structure

- `dashboard.py` — Entry point of the Streamlit application: handles the UI and data visualization.
- `api_client.py` — Module for communicating with the backend's REST API.

## Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- Streamlit-Folium
- REST API
