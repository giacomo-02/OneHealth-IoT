
########################DESCRIZIONE DEL COMPONENTE############################

La cartella mobile_app contiene il componente dedicato alla raccolta delle
segnalazioni degli utenti relative a possibili anomalie ambientali.

L'applicazione è una web app mobile-first che permette ai cittadini di inviare
segnalazioni riguardanti la qualità delle acque, fornendo informazioni come
tipologia del problema, descrizione, posizione geografica e immagini.


########################FUNZIONALITÀ DEL COMPONENTE############################

L'applicazione permette di:

- Inviare segnalazioni relative a problemi ambientali.
- Rilevare automaticamente la posizione tramite GPS.
- Inserire una posizione manualmente.
- Specificare il tipo di anomalia osservata.
- Indicare il livello di gravità della segnalazione.
- Allegare immagini della situazione rilevata.
- Inviare i dati al backend per la memorizzazione.


########################FLUSSO DEL COMPONENTE#################################

Il funzionamento del componente mobile è il seguente:

1. L'utente compila il modulo di segnalazione.
2. L'applicazione raccoglie i dati inseriti e la posizione geografica.
3. La segnalazione viene inviata tramite API REST al backend.
4. Il backend salva la segnalazione nel database PostgreSQL.
5. La dashboard permette agli operatori di consultare e gestire le segnalazioni.


########################STRUTTURA DEI FILE####################################

segnalazioni_app.py -> Applicazione web mobile-first per la raccolta delle segnalazioni.
                       Gestisce l'interfaccia utente, l'acquisizione GPS, il caricamento 
                       delle foto e l'invio dei dati al backend.


########################TECNOLOGIE UTILIZZATE#################################

- Python
- Flask
- HTML/CSS/JavaScript
- GPS Geolocation API
- REST API
- PostgreSQL


########################REPOSITORY DEL COMPONENTE##############################

Repository:
INSERIRE_LINK_GITHUB

