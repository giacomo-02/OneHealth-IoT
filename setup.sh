#!/bin/bash

set -e


PROJECT_NAME="IoT_Project"
VENV_DIR="venv"

DB_NAME="iot_project"
DB_USER="user1"
DB_PASSWORD="user1"


echo "===================================="
echo " OneHealth IoT - Setup iniziale"
echo "===================================="


# ------------------------------------
# Python
# ------------------------------------

echo "[1/8] Controllo Python..."

if ! command -v python3 &> /dev/null
then
    echo "Python3 non trovato"
    exit 1
fi

python3 --version



# ------------------------------------
# Venv
# ------------------------------------

echo
echo "[2/8] Ambiente virtuale"


if ! dpkg -l | grep -q python3-venv
then
    sudo apt update
    sudo apt install -y python3-venv
fi


if [ ! -d "$VENV_DIR" ]
then
    python3 -m venv $VENV_DIR
fi



# ------------------------------------
# Dipendenze
# ------------------------------------

echo
echo "[3/8] Installazione dipendenze"


source $VENV_DIR/bin/activate


pip install --upgrade pip

pip install -r requirements.txt



# ------------------------------------
# PostgreSQL
# ------------------------------------

echo
echo "[4/8] Configurazione PostgreSQL"


if ! command -v psql &> /dev/null
then
    echo "PostgreSQL non installato"
    exit 1
fi



echo "Eliminazione database precedente..."

sudo -u postgres psql <<EOF

DROP DATABASE IF EXISTS $DB_NAME;

DROP ROLE IF EXISTS $DB_USER;


CREATE USER $DB_USER 
WITH PASSWORD '$DB_PASSWORD';


CREATE DATABASE $DB_NAME 
OWNER $DB_USER;


GRANT ALL PRIVILEGES 
ON DATABASE $DB_NAME 
TO $DB_USER;

EOF



# ------------------------------------
# Creazione tabelle
# ------------------------------------

echo
echo "[5/8] Creazione tabelle"


python <<EOF

from backend.database import Base, engine

# importa tutti i modelli
from backend.models import *

print("Creo tabelle...")

Base.metadata.create_all(bind=engine)

print("Database inizializzato")

EOF



# ------------------------------------
# Verifica
# ------------------------------------

echo
echo "[6/8] Verifica database"


PGPASSWORD=$DB_PASSWORD psql \
-h localhost \
-U $DB_USER \
-d $DB_NAME \
-c "\dt"



echo
echo "[7/8] Import dataset"


read -p "Importare ARPA e HFA? (y/n): " risposta


if [ "$risposta" = "y" ]
then

    python -m backend.hfa.import_database

    python -m backend.arpa.import_database

else

    echo "Importazione saltata"

fi



echo
echo "[8/8] Setup completato"


echo
echo "Avvio backend:"
echo
echo "source venv/bin/activate"
echo "uvicorn backend.main:app --reload"
