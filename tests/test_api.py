import requests

BASE = "http://127.0.0.1:8000"

endpoints = [

    "/health",

    "/boe/ultime",

    "/arpa/anni",

    "/sanitari/patologie",

    "/segnalazioni"

]

for ep in endpoints:

    try:

        r = requests.get(BASE + ep)

        print(
            ep,
            r.status_code
        )

    except Exception as e:

        print(
            ep,
            e
        )
