######################## SETUP E AVVIO DEL PROGETTO ########################

Questa guida descrive tutti i passaggi necessari per installare, configurare
ed eseguire il progetto OneHealth IoT su una nuova macchina.



######################## CREAZIONE AMBIENTE VIRTUALE ########################

Dalla cartella principale del progetto:

python3 -m venv venv


Attivazione ambiente virtuale:

Linux/macOS:

source venv/bin/activate



######################## INSTALLAZIONE DIPENDENZE ############################

Con ambiente virtuale attivo:

pip install -r requirements.txt



######################## CONFIGURAZIONE DATABASE #############################

Creare il database PostgreSQL:

CREATE DATABASE onehealth;


Configurare le credenziali di accesso nel file:

backend/database.py


Creazione automatica delle tabelle:

python backend/main.py


Importazione dataset storici:

Dataset ARPA qualità acqua:

python backend/arpa/import_database.py


Dataset sanitario HFA ISTAT:

python backend/hfa/import_database.py



######################## AVVIO DEI COMPONENTI ###############################


1) BACKEND FASTAPI

Dalla root del progetto:

uvicorn backend.main:app --host 0.0.0.0 --port 8000


Documentazione API:

http://localhost:8000/docs



2) CLOUD MQTT SUBSCRIBER

In un nuovo terminale:

source venv/bin/activate

python cloud/subscriber.py


Il componente riceve i dati pubblicati dalle boe IoT tramite MQTT
e li salva nel database PostgreSQL.



3) EDGE - SIMULAZIONE BOE IoT

In un nuovo terminale:

source venv/bin/activate

python edge/main.py


Il componente genera dati ambientali simulati e li pubblica sul broker MQTT.


Topic utilizzato:

onehealth/water/{id_boa}



4) DASHBOARD

In un nuovo terminale:

source venv/bin/activate

streamlit run dashboard/dashboard.py


Dashboard disponibile:

http://localhost:8501



5) MOBILE APP SEGNALAZIONI

In un nuovo terminale:

source venv/bin/activate

python mobile_app/segnalazioni_app.py


Applicazione disponibile:

http://localhost:8080



############################## TEST #########################################

I test principali del progetto si trovano nella cartella:

tests/


Esecuzione test:

python tests/test_database.py

python tests/test_api.py

python tests/test_imports.py

python tests/test_mqtt.py



############################ ARRESTO SISTEMA ################################

Terminare manualmente i processi avviati:

- Uvicorn backend
- Subscriber MQTT
- Edge simulator
- Streamlit dashboard
- Flask mobile app
