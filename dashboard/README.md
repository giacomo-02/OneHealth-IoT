
########################DESCRIZIONE DEL COMPONENTE############################

La cartella dashboard contiene il componente di visualizzazione del sistema
OneHealth IoT.

La dashboard è sviluppata tramite Streamlit e permette di visualizzare,
consultare e analizzare i dati raccolti dal sistema, integrando informazioni
ambientali provenienti dalle boe IoT, dati ARPA sulla qualità delle acque e dati
sanitari HFA/ISTAT.


########################FUNZIONALITÀ DEL COMPONENTE############################

La dashboard permette di:

- Visualizzare le misurazioni ambientali ricevute dalle boe IoT.
- Consultare lo storico dei dati relativi alla qualità dell'acqua.
- Visualizzare i dati ARPA relativi alla balneazione.
- Analizzare i dati sanitari territoriali.
- Mostrare possibili correlazioni tra dati ambientali e sanitari.
- Visualizzare le segnalazioni degli utenti.


########################FLUSSO DEL COMPONENTE#################################

Il funzionamento della dashboard è il seguente:

1. La dashboard effettua richieste REST verso il backend FastAPI.
2. Il backend recupera i dati dal database PostgreSQL.
3. I dati vengono elaborati e visualizzati tramite componenti Streamlit.
4. I risultati possono essere utilizzati per analisi ambientali e sanitarie.


########################STRUTTURA DEI FILE####################################

dashboard.py  -> Punto di ingresso dell'applicazione Streamlit. Gestisce l'interfaccia grafica e la visualizzazione dei dati.

api_client.py -> Modulo per la comunicazione con le API REST del backend.


########################TECNOLOGIE UTILIZZATE#################################

- Python
- Streamlit
- Pandas
- Plotly
- Streamlit-Folium
- REST API


########################REPOSITORY DEL COMPONENTE##############################

Repository:
INSERIRE_LINK_GITHUB


########################COLLEGAMENTO CON GLI ALTRI COMPONENTI##################

La dashboard comunica con il backend tramite API REST:

dashboard/
        |
        | REST API
        ▼
backend FastAPI
        |
        ▼
PostgreSQL Database
