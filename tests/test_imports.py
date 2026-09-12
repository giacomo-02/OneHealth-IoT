import os
import sys

# Rende importabile il pacchetto backend anche lanciando il test
# direttamente (python tests/test_imports.py), aggiungendo al path
# la cartella principale del progetto.
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


import backend.main

import backend.database

import backend.routes.arpa_routes

import backend.routes.boe_routes

import backend.routes.sanitari_routes

import backend.routes.segnalazioni_routes

import backend.routes.missioni_routes

import backend.routes.alerts_routes

print("OK - Tutti i moduli importati")
