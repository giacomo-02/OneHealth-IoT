
########################DESCRIZIONE DEL PROGETTO################################

La correlazione tra l'incidenza di alcune patologie sul territorio e l'inquinamento dello stesso 
può fornire a enti locali e pubbliche amministrazioni gli strumenti giusti per pianificare interventi a
breve e lungo termine. Questo progetto mette in relazione la qualità dell'acqua (mare e coste della 
Puglia) con l'incidenza di patologie gastrointestinali e patologie legate alla presenza di metalli pesanti,
 incrociando dati ambientali e dati sanitari.



#######################FLUSSO PRINCIPALE DEI DATI###############################

Il flusso principale dei dati è il seguente:

1. Le boe IoT generano dati relativi alla qualità dell'acqua.
2. I dati vengono pubblicati tramite protocollo MQTT verso un broker pubblico HiveMQ.
3. Il componente cloud sottoscrive i topic MQTT e salva le informazioni ricevute nel database PostgreSQL.
4. Il backend FastAPI espone API REST per l'accesso ai dati ambientali, sanitari e alle segnalazioni degli utenti.
5. Il database PostgreSQL mantiene lo storico delle informazioni raccolte.
6. La dashboard permette la visualizzazione e l'analisi dei dati.
7. L'applicazione mobile permette agli utenti di inviare segnalazioni relative a possibili anomalie ambientali.

########################ARCHITETTURA DEL PROGETTO################################
                         MQTT
┌──────────────┐  ─────────────────▶  ┌──────────────┐
│              │                      │              │
│    edge/     │                      │    HiveMQ    │
│              │                      │ MQTT Broker  │
│ Simulazione  │                      │              │
│   boe IoT    │                      └──────┬───────┘
│              │                             │
└──────────────┘                             │ MQTT Subscribe
                                             │
                                             ▼
                                    ┌────────────────┐
                                    │                │
                                    │    cloud/      │
                                    │                │
                                    │ MQTT Subscriber│
                                    │                │
                                    └───────┬────────┘
                                            │
                                            │ SQLAlchemy
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │                 │
                                   │   PostgreSQL    │
                                   │    Database     │
                                   │                 │
                                   └────────┬────────┘
                                            │
                                            │ SQLAlchemy
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │                 │
                                   │    backend/     │
                                   │                 │
                                   │ FastAPI REST API│
                                   │                 │
                                   └────────┬────────┘
                                            │
                         REST API           │           REST API
                    ┌───────────────────────┴───────────────────────┐
                    │                                               │
                    ▼                                               ▼

          ┌─────────────────┐                         ┌─────────────────┐
          │                 │                         │                 │
          │  dashboard/     │                         │  mobile_app/    │
          │                 │                         │                 │
          │ Streamlit       │                         │ Segnalazioni    │
          │ Visualizzazione │                         │ utenti          │
          │ Analisi dati AI │                         │ GPS + foto      │
          │                 │                         │                 │
          └─────────────────┘                         └─────────────────┘

        ┌──────────────────────────────────────────────┐
        │                                              │
        │              Dataset storici                 │
        │                                              │
        │ backend/arpa/                                │
        │  - Import dati ARPA Puglia                   │
        │                                              │
        │ backend/hfa/                                 │
        │  - Import dati sanitari HFA/ISTAT            │
        │                                              │
        └──────────────────────────────────────────────┘

        ┌──────────────────────────────────────────────┐
        │                    tests/                    │
        │                                              │
        │ - Test API REST                              │
        │ - Test connessione database                  │
        │ - Test MQTT                                  │
        │ - Test import moduli                         │
        └──────────────────────────────────────────────┘

#########################STRUTTURA DELLE REPOSITORY#############################

backend    -> API REST FastAPI, gestione database, modelli e integrazione dataset

edge       -> Simulazione delle boe IoT e pubblicazione MQTT

cloud      -> Subscriber MQTT per acquisizione dati ambientali

dashboard  -> Dashboard Streamlit per visualizzazione e analisi

mobile_app -> Applicazione web per raccolta segnalazioni utenti

tests      -> Test automatici del sistema


##########################TECNOLOGIE UTILIZZATE#################################

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- MQTT
- HiveMQ Broker
- Streamlit
- Pandas
- Scikit-learn
- Flask
- Raspberry Pi (simulazione edge)

