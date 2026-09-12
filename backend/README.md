
########################DESCRIZIONE DEL COMPONENTE############################

La cartella backend contiene il componente server-side del sistema OneHealth IoT.

Il backend è sviluppato tramite FastAPI e rappresenta il punto centrale di accesso
ai dati raccolti dal sistema. Si occupa della gestione delle API REST, della
comunicazione con il database PostgreSQL, della gestione dei modelli dati e
dell'integrazione delle informazioni ambientali e sanitarie.


########################FUNZIONALITÀ DEL COMPONENTE############################

Il backend fornisce le seguenti funzionalità principali:

- Gestione delle misurazioni provenienti dalle boe IoT.
- Accesso ai dati ambientali ARPA relativi alla qualità delle acque.
- Accesso ai dati sanitari HFA/ISTAT.
- Gestione delle segnalazioni inviate dagli utenti.
- Gestione delle missioni operative.
- Esposizione di API REST utilizzate dalla dashboard e dall'applicazione mobile.


########################FLUSSO DEL COMPONENTE#################################

Il funzionamento del componente backend è il seguente:

1. Il subscriber MQTT riceve i dati pubblicati dalle boe IoT.
2. I dati vengono salvati nel database PostgreSQL.
3. FastAPI espone endpoint REST per interrogare e modificare le informazioni.
4. Dashboard e applicazione mobile utilizzano le API per accedere ai dati.


########################STRUTTURA DEI FILE####################################

main.py     -> Punto di ingresso dell'applicazione FastAPI e registrazione delle API.
database.py -> Configurazione della connessione al database PostgreSQL.
models      -> Modelli SQLAlchemy che rappresentano le tabelle del database.
schemas     -> Schemi Pydantic utilizzati per validazione e risposta delle API.
routes      -> Endpoint REST suddivisi per dominio applicativo.
services    -> Logica applicativa e servizi di supporto.
arpa        -> Importazione e gestione del dataset ARPA relativo alla balneazione.
hfa         -> Importazione e gestione dei dati sanitari Health For All (ISTAT).


########################TECNOLOGIE UTILIZZATE#################################

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- Pandas


########################REPOSITORY DEL COMPONENTE##############################

Repository:
INSERIRE_LINK_GITHUB
