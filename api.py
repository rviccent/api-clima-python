from flask import Flask, jsonify, request, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
import os

DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'vendas'
DB_USER = 'postgres'
DB_PASSWORD = '21081979Ad'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

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