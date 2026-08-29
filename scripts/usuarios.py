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
    usuarios_api_json = requests.get(url=f'{URL_API}obtenerusuariosapi/{CONTRATO}/', auth=(API_AUTH_USER, API_AUTH_PASSWORD), timeout=3).json()

    usuarios_api = []
    for consultajson in usuarios_api_json:
        tuplaUsuarioIndividual = (
            consultajson['id'],
            consultajson['cedula'],
            consultajson['nombre'],
            consultajson['rfid'],
            consultajson['numero_telefonico'],
            consultajson['rol'],
        )
        usuarios_api.append(tuplaUsuarioIndividual)

    connlocal = psycopg2.connect(
        database=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT")
    )
    cursorlocal = connlocal.cursor()

    for id_usuario, cedula, nombre, rfid, numero_telefonico, rol in usuarios_api:
        cursorlocal.execute('''
            INSERT INTO perfiles_mobile (id, cedula, nombre, rfid, numero_telefonico, rol)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                cedula = EXCLUDED.cedula,
                nombre = EXCLUDED.nombre,
                rfid = EXCLUDED.rfid,
                numero_telefonico = EXCLUDED.numero_telefonico,
                rol = EXCLUDED.rol
        ''', (id_usuario, cedula, nombre, rfid, numero_telefonico, rol))

    ids_api = tuple(usuario[0] for usuario in usuarios_api)
    if ids_api:
        cursorlocal.execute('DELETE FROM perfiles_mobile WHERE id NOT IN %s', (ids_api,))
    else:
        cursorlocal.execute('DELETE FROM perfiles_mobile')

    connlocal.commit()

except requests.exceptions.ConnectionError:
    print("fallo consultando api de usuarios")
except (Exception, psycopg2.Error) as e:
    print(f"{e} - fallo total en los usuarios")
finally:
    if connlocal:
        cursorlocal.close()
        connlocal.close()
