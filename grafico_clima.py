import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = "vendas"
DB_USER = "postgres"
DB_PASSWORD = "21081979Ad"

def carregar_dados(limite=200):
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    try:
        df = pd.read_sql(
            """
            SELECT data_coleta, temperatura
            FROM clima
            ORDER BY data_coleta ASC
            LIMIT %s
            """,
            conn,
            params=(limite,)
        )
        return df
    finally:
        conn.close()

def main():
    df = carregar_dados()
    if df.empty:
        print("Sem dados ainda.")
        return

    df["data_coleta"] = pd.to_datetime(df["data_coleta"])

    plt.figure()
    plt.plot(df["data_coleta"], df["temperatura"])
    plt.xlabel("Data/Hora")
    plt.ylabel("Temperatura (ºC)")
    plt.title("Temperatura - São José dos Campos")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()