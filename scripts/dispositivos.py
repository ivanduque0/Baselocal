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
    dispositivos_api_json = requests.get(url=f'{URL_API}dispositivosapi/{CONTRATO}/', auth=(API_AUTH_USER, API_AUTH_PASSWORD), timeout=3).json()

    dispositivos_api = []
    for consultajson in dispositivos_api_json:
        tuplaDispositivoIndividual = (consultajson['id'], consultajson['dispositivo'], consultajson['descripcion'], consultajson['acceso'], consultajson.get('tipo_dispositivo'), consultajson.get('sistema'), consultajson.get('tipo_acceso'))
        dispositivos_api.append(tuplaDispositivoIndividual)

    connlocal = psycopg2.connect(
        database=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT")
    )
    cursorlocal = connlocal.cursor()

    for id_dispositivo, dispositivo, descripcion, acceso, tipo_dispositivo, sistema, tipo_acceso in dispositivos_api:
        cursorlocal.execute('''
            INSERT INTO dispositivos_informacion (id, dispositivo, descripcion, acceso, tipo_dispositivo, sistema, tipo_acceso)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                dispositivo = EXCLUDED.dispositivo,
                descripcion = EXCLUDED.descripcion,
                acceso = EXCLUDED.acceso,
                tipo_dispositivo = EXCLUDED.tipo_dispositivo,
                sistema = EXCLUDED.sistema,
                tipo_acceso = EXCLUDED.tipo_acceso
        ''', (id_dispositivo, dispositivo, descripcion, acceso, tipo_dispositivo, sistema, tipo_acceso))

    ids_api = tuple(dispositivo[0] for dispositivo in dispositivos_api)
    if ids_api:
        cursorlocal.execute('DELETE FROM dispositivos_informacion WHERE id NOT IN %s', (ids_api,))
    else:
        cursorlocal.execute('DELETE FROM dispositivos_informacion')

    connlocal.commit()

except requests.exceptions.ConnectionError:
    print("fallo consultando api de dispositivos")
except (Exception, psycopg2.Error) as e:
    print(f"{e} - fallo total en los dispositivos")
finally:
    if connlocal:
        cursorlocal.close()
        connlocal.close()
