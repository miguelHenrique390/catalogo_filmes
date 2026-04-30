import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_conection():
    try:
        if os.getenv("DB_HOST") == "localhost":
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                sslmode ="disable",
                channel_binding="disable"
            )

            return conn
        else:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                sslmode=os.getenv("DB_SSLMODE"),
                channel_binding=os.getenv("DB_CHANNEL_BINDING")
            )
            return conn
    except Exception as ex:
        print(f'Erro ao conectar ao banco de dadsos: {ex}')
        return None

