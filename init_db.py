import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

SQL = """
CREATE TABLE IF NOT EXISTS clima (
    id SERIAL PRIMARY KEY,
    cidade VARCHAR(100) NOT NULL,
    temperatura NUMERIC(5,2) NOT NULL,
    vento_kmh NUMERIC(6,2),
    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def main():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL não encontrada. Configure no Render/Environment.")

    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(SQL)
        conn.commit()
        print("Tabela 'clima' criada/confirmada com sucesso!")
    finally:
        conn.close()

if __name__ == "__main__":
    main()