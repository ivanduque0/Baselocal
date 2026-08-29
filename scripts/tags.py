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
    tags_api_json = requests.get(url=f'{URL_API}vertagscontratoapi/{CONTRATO}/', auth=(API_AUTH_USER, API_AUTH_PASSWORD), timeout=3).json()

    tags_api = []
    for consultajson in tags_api_json:
        tuplaTagIndividual = (consultajson['id'], consultajson['epc'], consultajson.get('activo', True))
        tags_api.append(tuplaTagIndividual)

    connlocal = psycopg2.connect(
        database=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT")
    )
    cursorlocal = connlocal.cursor()

    for id_tag, epc, activo in tags_api:
        cursorlocal.execute('''
            INSERT INTO vehiculos_tags_rfid (id, epc, activo)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                epc = EXCLUDED.epc,
                activo = EXCLUDED.activo
        ''', (id_tag, epc, activo))

    ids_api = tuple(tag[0] for tag in tags_api)
    if ids_api:
        cursorlocal.execute('DELETE FROM vehiculos_tags_rfid WHERE id NOT IN %s', (ids_api,))
    else:
        cursorlocal.execute('DELETE FROM vehiculos_tags_rfid')

    connlocal.commit()

except requests.exceptions.ConnectionError:
    print("fallo consultando api de tags")
except (Exception, psycopg2.Error) as e:
    print(f"{e} - fallo total en los tags")
finally:
    if connlocal:
        cursorlocal.close()
        connlocal.close()
