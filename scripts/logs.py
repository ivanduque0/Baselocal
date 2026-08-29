import os
import psycopg2
import requests

CONTRATO=os.environ.get("CONTRATO")
URL_API=os.environ.get("URL_API")
API_AUTH_USER=os.environ.get("API_AUTH_USER")
API_AUTH_PASSWORD=os.environ.get("API_AUTH_PASSWORD")

connlocal = None
cursorlocal = None

try:
    connlocal = psycopg2.connect(
        database=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT")
    )
    cursorlocal = connlocal.cursor()

    # logica de sincronizacion de logs (pendiente)

    connlocal.commit()

except requests.exceptions.ConnectionError:
    print("fallo consultando api de logs")
except (Exception, psycopg2.Error) as e:
    print(f"{e} - fallo total en los logs")
finally:
    if connlocal:
        cursorlocal.close()
        connlocal.close()
