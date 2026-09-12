
########################DESCRIZIONE DEL COMPONENTE############################

La cartella edge contiene il componente IoT del sistema OneHealth IoT.
Rappresenta il software eseguito sulle boe marine e si occupa della generazione,
analisi e pubblicazione dei dati relativi alla qualità dell'acqua.

Nel progetto sviluppato il comportamento delle boe viene simulato tramite script
Python che generano misurazioni ambientali, calcolano un'indicazione locale sulla
qualità dell'acqua e inviano i dati tramite protocollo MQTT.


########################FLUSSO DEL COMPONENTE#################################

Il funzionamento del componente edge è il seguente:

1. Vengono caricate le configurazioni delle boe dal file boe_config.py.
2. Vengono generate le misurazioni dei sensori tramite sensor_generator.py.
3. I parametri ambientali vengono analizzati localmente tramite water_quality.py.
4. I dati completi della boa vengono pubblicati tramite MQTT verso il broker HiveMQ.
5. Il componente cloud riceve i dati pubblicati e li salva nel sistema.


########################STRUTTURA DEI FILE####################################

main.py              -> Punto di ingresso del componente e gestione del ciclo principale delle boe.
boe_config.py        -> Configurazione delle boe simulate e delle relative informazioni geografiche.
sensor_generator.py  -> Generazione dei valori simulati dei sensori ambientali.
water_quality.py     -> Analisi locale dei parametri della qualità dell'acqua.
mqtt_publisher.py    -> Gestione della pubblicazione dei dati tramite protocollo MQTT.
update_boe_config.py -> Utility per aggiornare la configurazione delle boe.


########################TECNOLOGIE UTILIZZATE#################################

- Python
- MQTT
- HiveMQ Broker
- Paho MQTT Client
- Raspberry Pi (simulazione dispositivo edge)


########################REPOSITORY DEL COMPONENTE##############################

Repository:
INSERIRE_LINK_GITHUB
