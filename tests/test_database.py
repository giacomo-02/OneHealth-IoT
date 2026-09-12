from sqlalchemy import create_engine
from sqlalchemy import text

DATABASE_URL = (
    "postgresql+psycopg2://user1:user1@localhost/iot_project"
)

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("OK - Connessione PostgreSQL riuscita")

except Exception as e:
    print("ERRORE")
    print(e)
