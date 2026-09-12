BOE = [

    # ===== FOGGIA / GARGANO =====
    # bbox = (lat_min, lat_max, lon_min, lon_max): zona di mare entro cui la boa puo' derivare
    # Gargano nord: la costa guarda a nord, "al largo" = aumentare latitudine
    {"id": "BOA_FG1", "nome": "Boa Rodi Garganico",       "comune": "Rodi Garganico",       "provincia": "FG",
     "lat": 41.990, "lon": 16.010, "tipo": "deriva",
     "vel_lat_base": -0.002, "vel_lon_base": -0.001,
     "bbox": (41.85, 42.20, 15.85, 16.50)},

    {"id": "BOA_FG2", "nome": "Boa Peschici",              "comune": "Peschici",             "provincia": "FG",
     "lat": 42.020, "lon": 16.150, "tipo": "deriva",
     "vel_lat_base": -0.001, "vel_lon_base": +0.002,
     "bbox": (41.90, 42.25, 16.00, 16.70)},

    # Gargano est: la costa guarda a est, "al largo" = aumentare longitudine
    {"id": "BOA_FG3", "nome": "Boa Vieste",                "comune": "Vieste",               "provincia": "FG",
     "lat": 41.875, "lon": 16.340, "tipo": "deriva",
     "vel_lat_base": -0.003, "vel_lon_base": 0.0,
     "bbox": (41.70, 42.05, 16.20, 16.90)},

    {"id": "BOA_FG4", "nome": "Boa Manfredonia",           "comune": "Manfredonia",          "provincia": "FG",
     "lat": 41.608, "lon": 15.960, "tipo": "fissa"},

    # ===== BAT =====
    # Costa Adriatica: la costa guarda a est, "al largo" = aumentare longitudine (~0.12 deg = 10 km)
    {"id": "BOA_BT1", "nome": "Boa Margherita di Savoia",  "comune": "Margherita di Savoia", "provincia": "BT",
     "lat": 41.372, "lon": 16.280, "tipo": "deriva",
     "vel_lat_base": -0.003, "vel_lon_base": +0.001,
     "bbox": (41.15, 41.65, 16.12, 16.70)},

    {"id": "BOA_BT2", "nome": "Boa Barletta",              "comune": "Barletta",             "provincia": "BT",
     "lat": 41.317, "lon": 16.330, "tipo": "fissa"},

    {"id": "BOA_BT3", "nome": "Boa Trani",                 "comune": "Trani",                "provincia": "BT",
     "lat": 41.277, "lon": 16.550, "tipo": "deriva",
     "vel_lat_base": -0.004, "vel_lon_base": 0.0,
     "bbox": (41.10, 41.55, 16.40, 16.95)},

    # ===== BARI =====
    {"id": "BOA_BA1", "nome": "Boa Molfetta",              "comune": "Molfetta",             "provincia": "BA",
     "lat": 41.200, "lon": 16.740, "tipo": "deriva",
     "vel_lat_base": -0.004, "vel_lon_base": -0.001,
     "bbox": (41.00, 41.45, 16.60, 17.10)},

    {"id": "BOA_BA2", "nome": "Boa Bari Porto",            "comune": "Bari",                 "provincia": "BA",
     "lat": 41.127, "lon": 16.920, "tipo": "fissa"},

    {"id": "BOA_BA3", "nome": "Boa Polignano a Mare",      "comune": "Polignano a Mare",     "provincia": "BA",
     "lat": 40.993, "lon": 17.360, "tipo": "deriva",
     "vel_lat_base": -0.003, "vel_lon_base": 0.0,
     "bbox": (40.80, 41.20, 17.20, 17.75)},

    {"id": "BOA_BA4", "nome": "Boa Monopoli",              "comune": "Monopoli",             "provincia": "BA",
     "lat": 40.954, "lon": 17.440, "tipo": "deriva",
     "vel_lat_base": -0.003, "vel_lon_base": +0.001,
     "bbox": (40.75, 41.15, 17.28, 17.80)},

    # ===== BRINDISI =====
    {"id": "BOA_BR1", "nome": "Boa Torre Canne",            "comune": "Fasano",               "provincia": "BR",
     "lat": 40.832, "lon": 17.640, "tipo": "deriva",
     "vel_lat_base": -0.002, "vel_lon_base": +0.001,
     "bbox": (40.65, 41.00, 17.52, 17.95)},

    # Villanova di Ostuni: paese costiero a ~40.785,17.601; mare a est/nord-est.
    # Boa al largo ~8-9 km ENE dal paese (punto verificato in mare, non su terraferma).
    {"id": "BOA_BR2", "nome": "Boa Villanova di Ostuni",   "comune": "Ostuni",               "provincia": "BR",
     "lat": 40.800, "lon": 17.700, "tipo": "deriva",
     "vel_lat_base": -0.002, "vel_lon_base": +0.002,
     "bbox": (40.60, 40.95, 17.66, 18.15)},

    {"id": "BOA_BR3", "nome": "Boa Brindisi Costa",        "comune": "Brindisi",             "provincia": "BR",
     "lat": 40.530, "lon": 18.080, "tipo": "fissa"},   # Adriatico, 6 km al largo (evita Punta della Contessa)

    # ===== TARANTO =====
    # Golfo di Taranto: la costa guarda a sud, "al largo" = diminuire latitudine
    {"id": "BOA_TA1", "nome": "Boa Castellaneta Marina",   "comune": "Castellaneta",         "provincia": "TA",
     "lat": 40.280, "lon": 17.020, "tipo": "deriva",
     "vel_lat_base": +0.001, "vel_lon_base": -0.002,
     "bbox": (40.10, 40.43, 16.70, 17.35)},

    {"id": "BOA_TA2", "nome": "Boa Taranto Mar Grande",    "comune": "Taranto",              "provincia": "TA",
     "lat": 40.438, "lon": 17.148, "tipo": "fissa"},   # centro Mar Grande

    {"id": "BOA_TA3", "nome": "Boa Lido Silvana",           "comune": "Pulsano",              "provincia": "TA",
     "lat": 40.250, "lon": 17.400, "tipo": "fissa"},   # Golfo di Taranto, 10 km a sud di Lido Silvana

    # Ionica centrale: tra Gallipoli e prov. Brindisi, correnti verso nord-est
    {"id": "BOA_TA4", "nome": "Boa Torre Colimena",         "comune": "Manduria",             "provincia": "TA",
     "lat": 40.192, "lon": 17.625, "tipo": "deriva",
     "vel_lat_base": +0.001, "vel_lon_base": +0.002,
     "bbox": (40.00, 40.42, 17.40, 17.98)},

    # ===== LECCE / SALENTO =====
    {"id": "BOA_LE1", "nome": "Boa Porto Cesareo",         "comune": "Porto Cesareo",        "provincia": "LE",
     "lat": 40.245, "lon": 17.862, "tipo": "fissa"},

    {"id": "BOA_LE1D", "nome": "Boa Porto Cesareo largo",  "comune": "Porto Cesareo",        "provincia": "LE",
     "lat": 40.195, "lon": 17.770, "tipo": "deriva",
     "vel_lat_base": +0.001, "vel_lon_base": +0.001,
     "bbox": (40.00, 40.42, 17.55, 18.05)},

    # Tacco adriatico: costa guarda a est, "al largo" = aumentare longitudine
    {"id": "BOA_LE2", "nome": "Boa Torre dell'Orso",       "comune": "Melendugno",           "provincia": "LE",
     "lat": 40.271, "lon": 18.600, "tipo": "deriva",
     "vel_lat_base": -0.002, "vel_lon_base": +0.001,
     "bbox": (40.10, 40.50, 18.46, 18.95)},

    {"id": "BOA_LE3", "nome": "Boa Otranto",               "comune": "Otranto",              "provincia": "LE",
     "lat": 40.145, "lon": 18.660, "tipo": "deriva",
     "vel_lat_base": -0.003, "vel_lon_base": +0.003,
     "bbox": (39.95, 40.30, 18.50, 19.00)},

    {"id": "BOA_LE4", "nome": "Boa Castro Marina",         "comune": "Castro",               "provincia": "LE",
     "lat": 39.995, "lon": 18.570, "tipo": "deriva",
     "vel_lat_base": -0.002, "vel_lon_base": +0.001,
     "bbox": (39.85, 40.15, 18.43, 18.95)},

    # Punta Leuca: punta estrema, "al largo" = andare a sud del promontorio
    {"id": "BOA_LE5", "nome": "Boa Santa Maria di Leuca",  "comune": "Castrignano del Capo", "provincia": "LE",
     "lat": 39.700, "lon": 18.400, "tipo": "deriva",
     "vel_lat_base": +0.001, "vel_lon_base": -0.003,
     "bbox": (39.55, 39.82, 18.20, 18.70)},

    # Costa ionica: la costa guarda a sud, "al largo" = diminuire latitudine
    {"id": "BOA_LE6", "nome": "Boa Torre San Giovanni",    "comune": "Ugento",               "provincia": "LE",
     "lat": 39.790, "lon": 18.050, "tipo": "deriva",
     "vel_lat_base": +0.002, "vel_lon_base": -0.002,
     "bbox": (39.65, 39.95, 17.80, 18.25)},

    {"id": "BOA_LE7", "nome": "Boa Gallipoli",             "comune": "Gallipoli",            "provincia": "LE",
     "lat": 40.042, "lon": 17.952, "tipo": "fissa"},

    {"id": "BOA_LE7D", "nome": "Boa Gallipoli largo",      "comune": "Gallipoli",            "provincia": "LE",
     "lat": 40.005, "lon": 17.870, "tipo": "deriva",
     "vel_lat_base": +0.001, "vel_lon_base": -0.001,
     "bbox": (39.82, 40.18, 17.68, 18.08)},

    {"id": "BOA_LE8", "nome": "Boa Nardò Costa",           "comune": "Nardo'",               "provincia": "LE",
     "lat": 40.150, "lon": 17.830, "tipo": "fissa"},   # Ionico, tra Porto Cesareo e Gallipoli

    {"id": "BOA_LE9", "nome": "Boa Santa Cesarea Terme",   "comune": "Santa Cesarea Terme",  "provincia": "LE",
     "lat": 40.030, "lon": 18.570, "tipo": "fissa"},   # Adriatico, canale d'Otranto

    {"id": "BOA_LE10", "nome": "Boa Tricase Porto",        "comune": "Tricase",              "provincia": "LE",
     "lat": 39.920, "lon": 18.492, "tipo": "fissa"},   # Adriatico, tacco sud

    {"id": "BOA_LE11", "nome": "Boa Torre San Giovanni",   "comune": "Ugento",               "provincia": "LE",
     "lat": 39.848, "lon": 17.975, "tipo": "fissa"},   # Ionico, costa di Ugento tra Torre San Giovanni e Pescoluse

    {"id": "BOA_LE12", "nome": "Boa Santa Maria di Leuca", "comune": "Castrignano del Capo", "provincia": "LE",
     "lat": 39.796, "lon": 18.358, "tipo": "fissa"},   # Capo di Leuca, punta estrema del Salento

    {"id": "BOA_LE13", "nome": "Boa Otranto Costa",        "comune": "Otranto",              "provincia": "LE",
     "lat": 40.148, "lon": 18.510, "tipo": "fissa"},   # Adriatico, davanti al porto di Otranto

    {"id": "BOA_LE14", "nome": "Boa San Cataldo",          "comune": "Lecce",                "provincia": "LE",
     "lat": 40.378, "lon": 18.330, "tipo": "fissa"},   # Adriatico, al largo della marina di Lecce

]
