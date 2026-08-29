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
    horarios_api_json = requests.get(url=f'{URL_API}obtenerhorariosapi/{CONTRATO}/', auth=(API_AUTH_USER, API_AUTH_PASSWORD), timeout=3).json()

    horarios_api = []
    for consultajson in horarios_api_json:
        tuplaHorarioIndividual = (
            consultajson['id'],
            consultajson['fecha_entrada'],
            consultajson['fecha_salida'],
            consultajson['dia'],
            consultajson['entrada'],
            consultajson['salida'],
            consultajson['cedula'],
            consultajson['acompanantes'],
            consultajson['contrato'],
            consultajson['usuario'],
            consultajson['uso_entrada'],
            consultajson['uso_salida'],
        )
        horarios_api.append(tuplaHorarioIndividual)

    connlocal = psycopg2.connect(
        database=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT")
    )
    cursorlocal = connlocal.cursor()

    for (id_horario, fecha_entrada, fecha_salida, dia, entrada, salida, cedula,
         acompanantes, contrato_id, usuario_id,
         uso_entrada, uso_salida) in horarios_api:
        cursorlocal.execute('''
            INSERT INTO horarios_horarioseinvitaciones
                (id, fecha_entrada, fecha_salida, dia, entrada, salida, cedula, acompanantes, contrato_id, usuario_id, uso_entrada, uso_salida)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                fecha_entrada = EXCLUDED.fecha_entrada,
                fecha_salida = EXCLUDED.fecha_salida,
                dia = EXCLUDED.dia,
                entrada = EXCLUDED.entrada,
                salida = EXCLUDED.salida,
                cedula = EXCLUDED.cedula,
                acompanantes = EXCLUDED.acompanantes,
                contrato_id = EXCLUDED.contrato_id,
                usuario_id = EXCLUDED.usuario_id,
                uso_entrada = EXCLUDED.uso_entrada,
                uso_salida = EXCLUDED.uso_salida
        ''', (id_horario, fecha_entrada, fecha_salida, dia, entrada, salida, cedula,
              acompanantes, contrato_id, usuario_id,
              uso_entrada, uso_salida))

    ids_api = tuple(horario[0] for horario in horarios_api)
    if ids_api:
        cursorlocal.execute('DELETE FROM horarios_horarioseinvitaciones WHERE id NOT IN %s', (ids_api,))
    else:
        cursorlocal.execute('DELETE FROM horarios_horarioseinvitaciones')

    connlocal.commit()

except requests.exceptions.ConnectionError:
    print("fallo consultando api de horarios")
except (Exception, psycopg2.Error) as e:
    print(f"{e} - fallo total en los horarios")
finally:
    if connlocal:
        cursorlocal.close()
        connlocal.close()
