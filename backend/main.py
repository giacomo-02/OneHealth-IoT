"""
Entry point API OneHealth Puglia.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import (
    Base,
    engine
)


# Import necessario per registrare le tabelle SQLAlchemy
from backend.models import (
    ArpaMisurazione,
    DatoSanitario,
    Segnalazione,
    Missione,
)


from backend.routes import (
    boe_routes,
    arpa_routes,
    sanitari_routes,
    segnalazioni_routes,
    missioni_routes,
    alerts_routes,
)


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="OneHealth Puglia API"
)


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*:8080",
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    boe_routes.router
)

app.include_router(
    arpa_routes.router
)

app.include_router(
    sanitari_routes.router
)

app.include_router(
    segnalazioni_routes.router
)

app.include_router(
    missioni_routes.router
)

app.include_router(
    alerts_routes.router
)


@app.get("/health")
def health():
    return {
        "status": "ok"
    }
