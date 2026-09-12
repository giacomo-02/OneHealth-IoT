
########################DESCRIZIONE DEL COMPONENTE############################

La cartella tests contiene gli script utilizzati per verificare il corretto
funzionamento dei principali componenti del sistema OneHealth IoT.


########################FUNZIONALITÀ DEL COMPONENTE############################

I test permettono di verificare:

- Connessione al database PostgreSQL.
- Disponibilità delle API REST FastAPI.
- Corretto caricamento dei moduli Python.
- Comunicazione MQTT con il broker.


########################STRUTTURA DEI FILE####################################

test_database.py -> Verifica la connessione al database PostgreSQL.

test_api.py      -> Verifica la disponibilità degli endpoint REST principali.

test_imports.py  -> Controlla che i moduli del progetto siano importabili correttamente.

test_mqtt.py     -> Verifica la comunicazione MQTT.


########################TECNOLOGIE UTILIZZATE#################################

- Python
- Requests
- SQLAlchemy
- MQTT
