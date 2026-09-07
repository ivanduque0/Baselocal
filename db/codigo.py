import psycopg2
import os
import time
connlocal = None
cursorlocal = None

while True:
    try:
        connlocal = psycopg2.connect(
            database=os.environ.get("POSTGRES_DB"),
            user=os.environ.get("POSTGRES_USER"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            host=os.environ.get("POSTGRES_HOST"),
            port=os.environ.get("POSTGRES_PORT")
        )
        cursorlocal = connlocal.cursor()

        cursorlocal.execute('CREATE TABLE IF NOT EXISTS perfiles_mobile (id BIGINT PRIMARY KEY, cedula varchar(150), nombre varchar(150), rfid boolean, numero_telefonico varchar(150), rol varchar(150))')
        # cursorlocal.execute('CREATE TABLE IF NOT EXISTS logs_usuarios (id BIGINT, nombre varchar(150), fecha date, hora time without time zone, razon varchar(150), contrato varchar(150), cedula varchar(150), unidad integer, contrato_id integer)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS horarios_horarioseinvitaciones (id BIGINT PRIMARY KEY, fecha_entrada DATE, fecha_salida DATE, dia varchar(20), entrada time without time zone, salida time without time zone, cedula varchar(255), acompanantes INTEGER, contrato_id BIGINT, usuario_id BIGINT, uso_entrada BOOLEAN DEFAULT FALSE, uso_salida BOOLEAN DEFAULT FALSE)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS dispositivos_informacion (id BIGINT PRIMARY KEY, dispositivo varchar(150), descripcion varchar(150), acceso varchar(150), tipo_dispositivo varchar(150), sistema varchar(150), tipo_acceso varchar(150), apertura BOOLEAN DEFAULT FALSE)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS vehiculos_informacion (id BIGINT PRIMARY KEY, usuario_id BIGINT, tag_id BIGINT)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS vehiculos_tags_rfid (id BIGINT PRIMARY KEY, epc text, activo BOOLEAN DEFAULT TRUE)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS logs_rfid (tag_id BIGINT, fecha DATE, hora time without time zone, razon varchar(150), tipo_acceso varchar(150), tipo_dispositivo varchar(150), denegado BOOLEAN DEFAULT FALSE)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS ultimas_actualizaciones (tabla varchar(150) PRIMARY KEY, fecha_hora TIMESTAMP)')
        connlocal.commit()
        print("tablas creadas correctamente")
        break
    except (Exception, psycopg2.Error) as error:
        print("fallo en hacer las consultas, reintentando en 5 segundos:", error)
        time.sleep(5)
    finally:
        if connlocal:
            cursorlocal.close()
            connlocal.close()
            print("se ha cerrado la conexion a la base de datos")

