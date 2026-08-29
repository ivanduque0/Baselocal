import os
import subprocess
import psycopg2
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

TABLAS = [
    {"tabla": "dispositivos_informacion", "horas_env": "HORAS_ACTUALIZAR_DISPOSITIVOS", "script": "/app/dispositivos.py"},
    {"tabla": "perfiles_mobile", "horas_env": "HORAS_ACTUALIZAR_USUARIOS", "script": "/app/usuarios.py"},
    {"tabla": "horarios_horarioseinvitaciones", "horas_env": "HORAS_ACTUALIZAR_HORARIOS", "script": "/app/horarios.py"},
    {"tabla": "vehiculos_informacion", "horas_env": "HORAS_ACTUALIZAR_VEHICULOS_INFORMACION", "script": "/app/vehiculos.py"},
    {"tabla": "vehiculos_tags_rfid", "horas_env": "HORAS_ACTUALIZAR_VEHICULOS_TAGS_RFID", "script": "/app/tags.py"},
]


def actualizar_tablas():
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

        for tabla_info in TABLAS:
            tabla = tabla_info["tabla"]
            horas = int(os.environ.get(tabla_info["horas_env"], 24))

            cursorlocal.execute('SELECT fecha_hora FROM ultimas_actualizaciones WHERE tabla=%s', (tabla,))
            fila = cursorlocal.fetchone()

            debe_actualizar = True
            if fila and fila[0]:
                horas_transcurridas = (datetime.now() - fila[0]).total_seconds() / 3600
                debe_actualizar = horas_transcurridas >= horas

            if not debe_actualizar:
                continue

            if tabla_info["script"]:
                print(f"actualizando {tabla}")
                subprocess.run(["python3", tabla_info["script"]])

            cursorlocal.execute('''
                INSERT INTO ultimas_actualizaciones (tabla, fecha_hora)
                VALUES (%s, %s)
                ON CONFLICT (tabla) DO UPDATE SET fecha_hora = EXCLUDED.fecha_hora
            ''', (tabla, datetime.now()))
            connlocal.commit()

    except (Exception, psycopg2.Error) as error:
        print(f"{error} - fallo en update_db")
    finally:
        if connlocal:
            cursorlocal.close()
            connlocal.close()


scheduler = BlockingScheduler()
scheduler.add_job(actualizar_tablas, 'cron', minute='*/30')

actualizar_tablas()
scheduler.start()
