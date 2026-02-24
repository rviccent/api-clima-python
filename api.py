import os
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

# ---------------- FLASK ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

# ---------------- DATABASE ----------------
DATABASE_URL = os.getenv("DATABASE_URL")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "vendas")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

def get_conn():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clima (
                    id SERIAL PRIMARY KEY,
                    cidade VARCHAR(100),
                    temperatura NUMERIC(5,2),
                    vento_kmh NUMERIC(6,2),
                    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
    finally:
        conn.close()

init_db()

# ---------------- API CLIMA ----------------
def fetch_clima_sjc():
    lat, lon = -23.1896, -45.8841

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,wind_speed_10m"
        "&timezone=America%2FSao_Paulo"
    )

    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()

    return {
        "cidade": "São José dos Campos",
        "temperatura": float(data["current"]["temperature_2m"]),
        "vento_kmh": float(data["current"]["wind_speed_10m"])
    }

# ---------------- ROTAS ----------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/clima/coletar")
def coletar():
    info = fetch_clima_sjc()

    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO clima (cidade, temperatura, vento_kmh)
                VALUES (%s, %s, %s)
                RETURNING *
            """, (info["cidade"], info["temperatura"], info["vento_kmh"]))
            row = cur.fetchone()
            conn.commit()
            return jsonify(row)
    finally:
        conn.close()

@app.get("/clima/ultimos")
def ultimos():
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT *
                FROM clima
                ORDER BY data_coleta DESC
                LIMIT 5
            """)
            rows = cur.fetchall()
            return jsonify(rows)
    finally:
        conn.close()

@app.get("/clima/resumo")
def resumo():
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
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
            cur.execute("""
                SELECT
                    COUNT(*) AS total_registros,
                    ROUND(AVG(temperatura)::numeric, 2) AS media_temp,
                    MIN(temperatura) AS menor_temp,
                    MAX(temperatura) AS maior_temp
                FROM clima
            """)
            resumo = cur.fetchone()

            cur.execute("""
                SELECT *
                FROM clima
                ORDER BY data_coleta DESC
                LIMIT 5
            """)
            ultimos = cur.fetchall()

            return render_template("dashboard.html",
                                   resumo=resumo,
                                   ultimos=ultimos)
    finally:
        conn.close()