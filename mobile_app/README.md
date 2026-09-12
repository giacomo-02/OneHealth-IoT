# mobile_app

## Description

The `mobile_app` folder contains the component dedicated to collecting user reports of possible environmental anomalies.

The application is a mobile-first web app that lets citizens submit reports about water quality, providing information such as the type of issue, a description, geographic location, and images.

## Features

- Submitting reports about environmental issues.
- Automatic location detection via GPS.
- Manual location entry.
- Specifying the type of anomaly observed.
- Indicating the severity level of the report.
- Attaching images of the observed situation.
- Sending the data to the backend for storage.

## Component Flow

1. The user fills out the report form.
2. The application collects the entered data and the geographic location.
3. The report is sent to the backend via REST API.
4. The backend stores the report in the PostgreSQL database.
5. The dashboard lets operators review and manage the reports.

## File Structure

- `segnalazioni_app.py` — Mobile-first web application for collecting reports: handles the user interface, GPS acquisition, photo upload, and sending data to the backend.

## Technologies Used

- Python
- Flask
- HTML/CSS/JavaScript
- GPS Geolocation API
- REST API
- PostgreSQL
