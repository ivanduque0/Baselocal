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
    vehiculos_api_json = requests.get(url=f'{URL_API}vervehiculoscontratoapi/{CONTRATO}/', auth=(API_AUTH_USER, API_AUTH_PASSWORD), timeout=3).json()

    vehiculos_api = []
    for consultajson in vehiculos_api_json:
        tag = consultajson.get('tag')
        tag_id = tag['id'] if tag else None
        tuplaVehiculoIndividual = (consultajson['id'], consultajson['usuario'], tag_id)
        vehiculos_api.append(tuplaVehiculoIndividual)

    connlocal = psycopg2.connect(
        database=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT")
    )
    cursorlocal = connlocal.cursor()

    for id_vehiculo, usuario_id, tag_id in vehiculos_api:
        cursorlocal.execute('''
            INSERT INTO vehiculos_informacion (id, usuario_id, tag_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                usuario_id = EXCLUDED.usuario_id,
                tag_id = EXCLUDED.tag_id
        ''', (id_vehiculo, usuario_id, tag_id))

    ids_api = tuple(vehiculo[0] for vehiculo in vehiculos_api)
    if ids_api:
        cursorlocal.execute('DELETE FROM vehiculos_informacion WHERE id NOT IN %s', (ids_api,))
    else:
        cursorlocal.execute('DELETE FROM vehiculos_informacion')

    connlocal.commit()

except requests.exceptions.ConnectionError:
    print("fallo consultando api de vehiculos")
except (Exception, psycopg2.Error) as e:
    print(f"{e} - fallo total en los vehiculos")
finally:
    if connlocal:
        cursorlocal.close()
        connlocal.close()
