import psycopg2
import os
import subprocess
import time
import cloudinary
import urllib.request
import numpy as np
import cv2

CONTRATO=os.environ.get("CONTRATO")
connlocal = None
connheroku = None
cursorheroku=None
cursorlocal=None
listausuariosheroku=[]
listausuarioslocal=[]
total=0
nro_int_local_old=0

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
            user=os.environ.get("USER"), 
            password=os.environ.get("PASSWORD"), 
            host=os.environ.get("HOST"), 
            port=os.environ.get("PORT")
        )
        cursorlocal = connlocal.cursor()
        
        conn_info = subprocess.run(["heroku", "config:get", "DATABASE_URL", "-a", 'tesis-reconocimiento-facial'], stdout = subprocess.PIPE)
        connuri = conn_info.stdout.decode('utf-8').strip()
        connheroku = psycopg2.connect(connuri)
        cursorheroku = connheroku.cursor()


        cursorlocal.execute('SELECT * FROM web_interacciones where contrato=%s', (CONTRATO,))
        interacciones_local= cursorlocal.fetchall()
        nro_int_local_old=len(interacciones_local)
        

        t1=time.perf_counter()
        while True:
            t2=time.perf_counter()
            total=t2-t1

            cursorlocal.execute('SELECT * FROM web_interacciones where contrato=%s', (CONTRATO,))
            interacciones_local= cursorlocal.fetchall()
            
            nro_int_local = len(interacciones_local)

            if nro_int_local > nro_int_local_old and total>1:

                diferencia_rango=nro_int_local-nro_int_local_old
                diferencia= list(range(diferencia_rango))
                interacciones_local = interacciones_local[::-1]

                for posicion in diferencia:

                    interaccion = interacciones_local[posicion]

                    nombre=interaccion[0]
                    fecha=interaccion[1]
                    hora=interaccion[2]
                    razon=interaccion[3]
                    cedula=interaccion[5]

                    cursorheroku.execute('''INSERT INTO web_interacciones (nombre, fecha, hora, razon, contrato, cedula_id)
                    VALUES (%s, %s, %s, %s, %s, %s);''', (nombre, fecha, hora, razon, CONTRATO, cedula))
                    connheroku.commit()
                
                cursorlocal.execute('SELECT * FROM web_interacciones where contrato=%s', (CONTRATO,))
                interacciones_local= cursorlocal.fetchall()
                nro_int_local_old = len(interacciones_local)
                diferencia=0
                diferencia_rango=0
                nombre=None
                fecha=None
                hora=None
                razon=None
                cedula=None
                total=0
                t1=time.perf_counter()

    except (Exception, psycopg2.Error) as error:
        print("fallo en hacer las consultas")
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
            print("se ha cerrado la conexion a la base de datos")
