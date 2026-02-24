import os
from flask import Flask, jsonify, request, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def init_db():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clima (
                    id SERIAL PRIMARY KEY,
                    cidade VARCHAR(100) NOT NULL,
                    temperatura NUMERIC(5,2) NOT NULL,
                    vento_kmh NUMERIC(6,2),
                    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
    finally:
        conn.close()


DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    # Produção (Render)
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)

    # Local
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "vendas"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "")
    )

# chama automaticamente ao iniciar
init_db()
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/clima/ultimos")
def ultimos():
    n = int(request.args.get("n", 10))
    if n < 1:
        n = 1
    if n > 500:
        n = 500

    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, cidade, temperatura, vento_kmh, data_coleta
                FROM clima
                ORDER BY data_coleta DESC
                LIMIT %s
                """,
                (n,)
            )
            rows = cur.fetchall()
            return jsonify(rows)
    finally:
        conn.close()

@app.get("/clima/resumo")
def resumo():
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_registros,
                    ROUND(AVG(temperatura)::numeric, 2) AS media_temp,
                    MIN(temperatura) AS menor_temp,
                    MAX(temperatura) AS maior_temp
                FROM clima    
            """)
            row = cur.fetchone()
            return jsonify(row)
    finally:
        conn.close()

@app.get("/")
def dashboard():
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Resumo
            cur.execute("""
                SELECT
                    COUNT(*) AS total_registros,
                    ROUND(AVG(temperatura)::numeric, 2) AS media_temp,
                    MIN(temperatura) AS menor_temp,
                    MAX(temperatura) AS maior_temp
                FROM clima
            """)
            resumo = cur.fetchone()

            # Últimos 5
            cur.execute("""
                SELECT data_coleta, temperatura, vento_kmh
                FROM clima
                ORDER BY data_coleta DESC
                LIMIT 5
            """)
            ultimos = cur.fetchall()

        # ✅ retorno fora do "with" é OK (os dados já foram buscados)
        return render_template("dashboard.html", resumo=resumo, ultimos=ultimos)

    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)