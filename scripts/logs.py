import os
import psycopg2
import requests

CONTRATO=os.environ.get("CONTRATO")
URL_API=os.environ.get("URL_API")
API_AUTH_USER=os.environ.get("API_AUTH_USER")
API_AUTH_PASSWORD=os.environ.get("API_AUTH_PASSWORD")
TAMANO_BATCH = 100

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

    cursorlocal.execute('''
        SELECT ctid, tag_id, fecha, hora, razon, tipo_acceso, tipo_dispositivo, denegado
        FROM logs_rfid
        ORDER BY fecha, hora
    ''')
    pendientes = cursorlocal.fetchall()

    for inicio in range(0, len(pendientes), TAMANO_BATCH):
        lote = pendientes[inicio:inicio + TAMANO_BATCH]
        lote_json = [
            {
                'tag_id': tag_id,
                'fecha': fecha.isoformat(),
                'hora': hora.isoformat(),
                'razon': razon,
                'tipo_acceso': tipo_acceso,
                'tipo_dispositivo': tipo_dispositivo,
                'denegado': denegado,
            }
            for _, tag_id, fecha, hora, razon, tipo_acceso, tipo_dispositivo, denegado in lote
        ]

        try:
            requests.post(
                url=f'{URL_API}registrarlogsrfidapi/{CONTRATO}/',
                auth=(API_AUTH_USER, API_AUTH_PASSWORD),
                json=lote_json,
                timeout=20
            ).raise_for_status()
        except requests.exceptions.ConnectionError:
            print("fallo consultando api de logs, se detiene el envio")
            break
        except requests.exceptions.RequestException as e:
            print(f"{e} - fallo enviando un batch de logs, se reintentara en la siguiente ejecucion")
            continue

        ctids_lote = tuple(fila[0] for fila in lote)
        placeholders = ', '.join(['%s'] * len(ctids_lote))
        cursorlocal.execute(f'DELETE FROM logs_rfid WHERE ctid IN ({placeholders})', ctids_lote)
        connlocal.commit()

except (Exception, psycopg2.Error) as e:
    print(f"{e} - fallo total en los logs")
    if connlocal:
        connlocal.rollback()
finally:
    if connlocal:
        cursorlocal.close()
        connlocal.close()
