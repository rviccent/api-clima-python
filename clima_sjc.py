import datetime
import requests
import psycopg2

print("Script iniciou")

CIDADE = "São José dos Campos"

LAT = -23.2237
LON = -45.9009

API_URL = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true"

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "vendas"
DB_USER = "postgres"
DB_PASSWORD = "21081979Ad"

def buscar_clima():
    resposta = requests.get(API_URL)
    dados = resposta.json()
    temperatura = dados["current_weather"]["temperature"]
    vento = dados["current_weather"]["windspeed"]
    return temperatura, vento

def salvar_no_banco(temp, vento):
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO clima (cidade, temperatura, vento_kmh) VALUES (%s, %s, %s)",
        (CIDADE, temp, vento)
    )

    conn.commit()
    cursor.close()
    conn.close()

def main():
    temp, vento = buscar_clima()
    salvar_no_banco(temp, vento)
    print("Clima salvo com sucesso!")

if __name__ == "__main__":
    main()
