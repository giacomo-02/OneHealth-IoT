# 🌊 OneHealth-IoT

**IoT-based monitoring of Puglia's coastal water quality, correlated with the incidence of health conditions in the area.**

![Python](https://img.shields.io/badge/Python-backend-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009485)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-database-316192)
![MQTT](https://img.shields.io/badge/MQTT-IoT-660066)
![Status](https://img.shields.io/badge/status-in%20development-yellow)

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Architecture](#-architecture)
- [Data Flow](#-data-flow)
- [Repository Structure](#-repository-structure)
- [Technologies Used](#-technologies-used)
- [Quick Start](#-quick-start)
- [Tests](#-tests)

---

## 🎯 Project Overview

The correlation between the environmental quality of an area and the incidence of certain health conditions can give local authorities and public administrations the tools they need to plan targeted interventions, both short and long term.

**OneHealth-IoT** correlates the quality of Puglia's marine and coastal waters with the incidence of:

- gastrointestinal conditions,
- conditions linked to the presence of heavy metals,

by cross-referencing environmental data collected through a network of IoT sensors with historical health data (ARPA, HFA/ISTAT).

## 🧱 Architecture

```
📡 edge/           IoT buoy simulation
      │
      │ MQTT publish
      ▼
📶 HiveMQ          Public MQTT broker
      │
      │ MQTT subscribe
      ▼
☁️  cloud/          MQTT subscriber
      │
      │ SQLAlchemy
      ▼
🗄️  PostgreSQL      Historical data store
      │
      │ SQLAlchemy
      ▼
⚙️  backend/        FastAPI REST API
      │
      ├─ REST API ─▶ 📊 dashboard/      Streamlit
      └─ REST API ─▶ 📱 mobile_app/     User reports
```

Historical datasets (`backend/arpa/`, `backend/hfa/`) are imported directly by the backend and used for correlation analysis.

## 🔄 Data Flow

1. The **IoT buoys** (simulated in `edge/`) generate water quality data.
2. Data is published via the **MQTT** protocol to a public **HiveMQ** broker.
3. The **cloud/** component subscribes to the MQTT topics and stores the received data in the **PostgreSQL** database.
4. The **FastAPI backend** exposes REST APIs for environmental, health, and user report data.
5. **PostgreSQL** keeps the full history of all collected data.
6. The **dashboard** (Streamlit) allows data visualization and analysis.
7. The **mobile app** lets users report possible environmental anomalies, with photos and GPS location.

## 📁 Repository Structure

- **`backend/`** — REST API built with FastAPI: models, schemas, routes, and services for environmental, health, and user report data. Includes import scripts for the ARPA and HFA historical datasets. See [backend/README.md](./backend/README.md).
- **`edge/`** — IoT buoy simulation: data generation and MQTT publishing. See [edge/README.md](./edge/README.md).
- **`cloud/`** — MQTT subscriber that stores the received data in the database. See [cloud/README.md](./cloud/README.md).
- **`dashboard/`** — Streamlit dashboard for data visualization and analysis. See [dashboard/README.md](./dashboard/README.md).
- **`mobile_app/`** — App for users to submit environmental anomaly reports. See [mobile_app/README.md](./mobile_app/README.md).
- **`raspberry/`** — Scripts for running the buoy on real hardware (Raspberry Pi). See [raspberry/README.md](./raspberry/README.md).
- **`tests/`** — Automated tests for the API, database, module imports, and MQTT. See [tests/README.md](./tests/README.md).

### Full folder tree

```
OneHealth-IoT/
├── backend/           # REST API, models, routes, services
│   ├── arpa/          # ARPA Puglia dataset and import scripts
│   └── hfa/           # HFA / ISTAT dataset and import scripts
├── cloud/             # MQTT Subscriber
├── dashboard/         # Streamlit dashboard
├── edge/              # IoT buoy simulation
├── mobile_app/        # User report app
├── raspberry/         # Real hardware scripts
├── tests/             # Automated tests
├── requirements.txt
├── setup.sh
└── SETUP.md
```

## 🧰 Technologies Used

- **Language:** Python
- **Backend & API:** FastAPI, SQLAlchemy
- **Database:** PostgreSQL
- **IoT Messaging:** MQTT, HiveMQ Broker
- **Dashboard & Analysis:** Streamlit, Pandas, Scikit-learn
- **Other Web Frameworks:** Flask
- **Edge Hardware:** Raspberry Pi (simulation and real deployment)

## 🚀 Quick Start

```bash
git clone https://github.com/giacomo-02/OneHealth-IoT.git
cd OneHealth-IoT
pip install -r requirements.txt
```

For full setup (database, environment variables, MQTT broker) see the **[SETUP.md](./SETUP.md)** guide.

## 🧪 Tests

```bash
pytest tests/
```

---

Each component also has its own README with further details — see the links in the [Repository Structure](#-repository-structure) section above.
