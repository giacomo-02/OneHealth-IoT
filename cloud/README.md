
########################DESCRIZIONE DEL COMPONENTE############################

La cartella cloud contiene il componente responsabile della ricezione dei dati
provenienti dalle boe IoT simulate.

Il componente implementa un MQTT Subscriber che si collega al broker HiveMQ,
sottoscrive i topic delle boe e acquisisce le misurazioni relative alla qualità
dell'acqua.


########################FUNZIONALITÀ DEL COMPONENTE############################

Il componente cloud permette di:

- Collegarsi al broker MQTT pubblico HiveMQ.
- Sottoscrivere i topic relativi alle boe IoT.
- Ricevere i dati ambientali pubblicati dall'edge.
- Decodificare i messaggi ricevuti.
- Inviare i dati al backend per il salvataggio nel database PostgreSQL.


########################FLUSSO DEL COMPONENTE#################################

Il funzionamento del componente cloud è il seguente:

1. Le boe IoT pubblicano i dati tramite protocollo MQTT.
2. Il subscriber riceve i messaggi dal broker HiveMQ.
3. I dati vengono elaborati e inviati al backend.
4. Il backend salva le informazioni nel database PostgreSQL.


########################STRUTTURA DEI FILE####################################

subscriber.py -> Implementa il client MQTT subscriber. Gestisce la connessione al broker,
                 la sottoscrizione ai topic e la ricezione dei messaggi provenienti dalle boe.


########################TECNOLOGIE UTILIZZATE#################################

- Python
- MQTT
- HiveMQ Broker
- Paho MQTT Client


########################REPOSITORY DEL COMPONENTE##############################

Repository:
INSERIRE_LINK_GITHUB

