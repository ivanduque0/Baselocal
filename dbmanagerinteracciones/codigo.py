import psycopg2
import os
import subprocess
import time
import pytz
from datetime import datetime

CONTRATO=os.environ.get("CONTRATO")
connlocal = None
connheroku = None
cursorheroku=None
cursorlocal=None
total=0
fechahoy=None

while True:
    
    t1=time.perf_counter()
    while total<=5:
        t2=time.perf_counter()
        total=t2-t1
    total=0
    try:
        
        #con esto se apunta a la base de datos local
        connlocal = psycopg2.connect(
            database=os.environ.get("DATABASE"), 
            user=os.environ.get("USERDB"), 
            password=os.environ.get("PASSWORD"), 
            host=os.environ.get("HOST"), 
            port=os.environ.get("PORT")
        )
        cursorlocal = connlocal.cursor()
        
        conn_info = subprocess.run(["heroku", "config:get", "DATABASE_URL", "-a", 'tesis-reconocimiento-facial'], stdout = subprocess.PIPE)
        connuri = conn_info.stdout.decode('utf-8').strip()
        connheroku = psycopg2.connect(connuri)
        cursorheroku = connheroku.cursor()
        

        t1=time.perf_counter()
        while True:
            t2 = time.perf_counter()
            total = t2-t1
            tz = pytz.timezone('America/Caracas')
            caracas_now = datetime.now(tz)
            fechahoy=str(caracas_now)[:10]
            cursorlocal.execute('SELECT * FROM web_interacciones where contrato=%s and fecha=%s', (CONTRATO,fechahoy))
            interacciones_local= cursorlocal.fetchall()
            cursorheroku.execute('SELECT nombre, fecha, hora, razon, contrato, cedula_id FROM web_interacciones where contrato=%s and fecha=%s', (CONTRATO,fechahoy))
            interacciones_heroku= cursorheroku.fetchall()

            nro_int_local = len(interacciones_local)
            nro_int_heroku = len(interacciones_heroku)

            if nro_int_local > nro_int_heroku and total>1:

                

                for interaccion in interacciones_local:
                    try:
                        interacciones_heroku.index(interaccion)
                    except ValueError:
                        nombre=interaccion[0]
                        fecha=interaccion[1]
                        hora=interaccion[2]
                        razon=interaccion[3]
                        cedula=interaccion[5]
                        cursorheroku.execute('''INSERT INTO web_interacciones (nombre, fecha, hora, razon, contrato, cedula_id)
                        VALUES (%s, %s, %s, %s, %s, %s);''', (nombre, fecha, hora, razon, CONTRATO, cedula))
                        connheroku.commit()
                
                nombre=None
                fecha=None
                hora=None
                razon=None
                cedula=None
                total=0
                t1=time.perf_counter()

    except (Exception, psycopg2.Error) as error:
        #print("fallo en hacer las consultas")
        if connlocal:
            cursorlocal.close()
            connlocal.close()
        if connheroku:
            cursorheroku.close()
            connheroku.close()
    finally:
        if connlocal:
            cursorlocal.close()
            connlocal.close()
        if connheroku:
            cursorheroku.close()
            connheroku.close()
            #print("se ha cerrado la conexion a la base de datos")
