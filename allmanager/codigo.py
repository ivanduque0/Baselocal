import psycopg2
import os
import subprocess
import time
import cloudinary
import urllib.request
import numpy as np
import cv2
import pytz
from datetime import datetime

CONTRATO=os.environ.get("CONTRATO")
maximo_dias_acumular=int(os.environ.get("DIAS_ACUMULAR"))
connlocal = None
connheroku = None
cursorheroku=None
cursorlocal=None
listausuarioslocal=[]
listausuariosheroku=[]
diaslocal=[]
diasheroku=[]
total=0
fechahoy=None
fechaayer=None
diasacumulados=[]
etapa=0
DIRECTORIO=os.environ.get("DIRECTORIO", "media/personas")

if not os.path.exists(DIRECTORIO): 
    os.makedirs(DIRECTORIO)

cloudinary.config( 
    cloud_name = os.environ.get("CLOUD_NAME"), 
    api_key = os.environ.get("API_KEY"), 
    api_secret = os.environ.get("API_SECRET"),
    secure = True
)

while True:
    total=0
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

            if etapa==0:
                tz = pytz.timezone('America/Caracas')
                caracas_now = datetime.now(tz)
                fechahoy=str(caracas_now)[:10]

                if fechahoy != fechaayer:
                    fechaayer=fechahoy
                    tupla_fecha_hoy=(fechahoy,)
                    cursorlocal.execute('SELECT fecha FROM dias_acumulados')
                    dias_acumulados= cursorlocal.fetchall()
                    nro_dias_acumulados=len(dias_acumulados)

                    if nro_dias_acumulados >= maximo_dias_acumular:
                        cursorlocal.execute('DELETE FROM web_interacciones *')
                        cursorlocal.execute('DELETE FROM dias_acumulados *')
                        connlocal.commit()
                        
                    if not tupla_fecha_hoy in dias_acumulados:
                        cursorlocal.execute('''INSERT INTO dias_acumulados (fecha)
                        VALUES (%s);''', (fechahoy,))
                        connlocal.commit()
                
                cursorlocal.execute('SELECT * FROM web_interacciones where contrato=%s and fecha=%s', (CONTRATO,fechahoy))
                interacciones_local= cursorlocal.fetchall()
                cursorheroku.execute('SELECT nombre, fecha, hora, razon, contrato, cedula_id FROM web_interacciones where contrato=%s and fecha=%s', (CONTRATO,fechahoy))
                interacciones_heroku= cursorheroku.fetchall()

                nro_int_local = len(interacciones_local)
                nro_int_heroku = len(interacciones_heroku)

                if nro_int_local != nro_int_heroku:

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
                etapa=1

            if etapa==1:

                cursorlocal.execute('SELECT * FROM web_usuarios where contrato_id=%s', (CONTRATO,))
                usuarios_local= cursorlocal.fetchall()

                cursorheroku.execute('SELECT * FROM web_usuarios where contrato_id=%s', (CONTRATO,))
                usuarios_heroku= cursorheroku.fetchall()
                
                for usuario in usuarios_local:
                    cedula=usuario[0]
                    try:
                        listausuarioslocal.index(cedula)
                    except ValueError:
                        listausuarioslocal.append(cedula)

                for usuario in usuarios_heroku:
                    cedula=usuario[0]
                    try:
                        listausuariosheroku.index(cedula)
                    except ValueError:
                        listausuariosheroku.append(cedula)
                
                if len(usuarios_local) == len(usuarios_heroku):
                

                    for usuario in listausuarioslocal:
                        cursorlocal.execute('SELECT * FROM web_fotos where cedula_id=%s', (usuario,))
                        fotos_local= cursorlocal.fetchall()
                        cursorheroku.execute('SELECT * FROM web_fotos where cedula_id=%s', (usuario,))
                        fotos_heroku= cursorheroku.fetchall()

                        #eliminar fotos no validadas de forma local

                        for fotolocal in fotos_local:
                            estado=fotolocal[2]
                            id=fotolocal[0]
                            foto=fotolocal[1]
                            if estado==2:
                                cursorheroku.execute('UPDATE web_fotos SET estado=2 WHERE id=%s', (id,))
                                connheroku.commit()
                            if estado==1:
                                cursorheroku.execute('UPDATE web_fotos SET estado=1 WHERE id=%s', (id,))
                                connheroku.commit()
                                
                        #eliminar fotos de la base de datos local que no esten en la base de datos de heroku
                        if len(fotos_local) > len(fotos_heroku):
                            for fotolocal in fotos_local:
                                id=fotolocal[0]
                                foto=fotolocal[1]
                                try:
                                    fotos_heroku.index(fotolocal)
                                except ValueError:
                                    cursorlocal.execute('DELETE FROM web_fotos where id=%s', (id,))
                                    connlocal.commit()
                                    os.remove(f'{foto}.jpg')


                        #agregar fotos que no estan en la base de datos local pero que si estan en la de heroku
                        if len(fotos_local) < len(fotos_heroku):
                            for fotoheroku in fotos_heroku:
                                try:
                                    fotos_local.index(fotoheroku)
                                except ValueError:
                                    id=fotoheroku[0]
                                    foto=fotoheroku[1]
                                    estado=fotoheroku[2]
                                    cedula=fotoheroku[3]
                                    cursorlocal.execute('''INSERT INTO web_fotos (id, foto, estado, cedula_id)
                                    VALUES (%s, %s, %s, %s);''', (id, foto, estado, cedula))
                                    connlocal.commit()
                                    url = cloudinary.utils.cloudinary_url(foto)
                                    url=url[0]
                                    imagenurl = urllib.request.urlopen (url) #abrimos el URL
                                    imagenarray = np.array(bytearray(imagenurl.read()),dtype=np.uint8)
                                    fotovisible = cv2.imdecode (imagenarray,-1)
                                    cv2.imwrite(f"{foto}.jpg",fotovisible)
                    listausuariosheroku=[]
                    listausuarioslocal=[]
                etapa=2

            if etapa==2:

                cursorlocal.execute('SELECT * FROM web_usuarios where contrato_id=%s', (CONTRATO,))
                usuarios_local= cursorlocal.fetchall()

                cursorheroku.execute('SELECT * FROM web_usuarios where contrato_id=%s', (CONTRATO,))
                usuarios_heroku= cursorheroku.fetchall()


                for usuario in usuarios_local:
                    cedula=usuario[0]
                    try:
                        listausuarioslocal.index(cedula)
                    except ValueError:
                        listausuarioslocal.append(cedula)
                
                for usuario in listausuarioslocal:
                    cursorheroku.execute('SELECT entrada, salida, cedula_id, dia FROM web_horariospermitidos WHERE cedula_id=%s',(usuario,))
                    diasheroku= cursorheroku.fetchall()
                    
                    cursorlocal.execute('SELECT * FROM web_horariospermitidos WHERE cedula_id=%s',(usuario,))
                    diaslocal= cursorlocal.fetchall()

                    if len(diasheroku) > 0 and len(diasheroku) > len(diaslocal):
                        for diasherokuiterar in diasheroku:
                            try:
                                diaslocal.index(diasherokuiterar)
                            except ValueError:
                                entrada=diasherokuiterar[0]
                                salida=diasherokuiterar[1]
                                cedula=diasherokuiterar[2]
                                dia=diasherokuiterar[3]
                                cursorlocal.execute('''INSERT INTO web_horariospermitidos (entrada, salida, cedula_id, dia)
                                VALUES (%s, %s, %s, %s);''', (entrada, salida, cedula, dia))
                                connlocal.commit()

                    if len(diaslocal) > len(diasheroku):
                        for diaslocaliterar in diaslocal:
                            try:
                                diasheroku.index(diaslocaliterar)
                            except ValueError:
                                entrada=diaslocaliterar[0]
                                salida=diaslocaliterar[1]
                                cedula=diaslocaliterar[2]
                                dia=diaslocaliterar[3]
                                cursorlocal.execute('DELETE FROM web_horariospermitidos WHERE entrada=%s AND salida=%s AND cedula_id=%s AND dia=%s',(entrada, salida, cedula, dia))
                                connlocal.commit()
                diaslocal=[]
                diasheroku=[]
                listausuariosheroku=[]
                listausuarioslocal=[]
                etapa=3

            if etapa==3:

                cursorlocal.execute('SELECT * FROM web_usuarios where contrato_id=%s', (CONTRATO,))
                usuarios_local= cursorlocal.fetchall()

                cursorheroku.execute('SELECT * FROM web_usuarios where contrato_id=%s', (CONTRATO,))
                usuarios_heroku= cursorheroku.fetchall()
                
                nro_usu_local = len(usuarios_local)
                nro_usu_heroku = len(usuarios_heroku)
            
                if nro_usu_heroku == nro_usu_local:
                    for usuario in usuarios_heroku:
                        try:
                            usuarios_local.index(usuario)
                        except ValueError:
                            cedula=usuario[0]
                            telegram_id=usuario[2]
                            cursorlocal.execute("UPDATE web_usuarios SET telegram_id=%s WHERE cedula=%s", (telegram_id,cedula))
                            connlocal.commit()
                etapa=4

            if etapa==4:

                cursorlocal.execute('SELECT * FROM web_usuarios where contrato_id=%s', (CONTRATO,))
                usuarios_local= cursorlocal.fetchall()

                cursorheroku.execute('SELECT * FROM web_usuarios where contrato_id=%s', (CONTRATO,))
                usuarios_heroku= cursorheroku.fetchall()

                nro_usu_local = len(usuarios_local)
                nro_usu_heroku = len(usuarios_heroku)
            
                #cuando se va a eliminar un usuario
                if nro_usu_local > nro_usu_heroku:

                    for usuario in usuarios_heroku:
                        cedula=usuario[0]
                        try:
                            listausuariosheroku.index(cedula)
                        except ValueError:
                            listausuariosheroku.append(cedula)
                    
                    for usuario in usuarios_local:
                        cedula=usuario[0]
                        try:
                            listausuarioslocal.index(cedula)
                        except ValueError:
                            listausuarioslocal.append(cedula)

                    for usuario in listausuarioslocal:
                        try:
                            listausuariosheroku.index(usuario)
                        except ValueError:
                            cursorlocal.execute('DELETE FROM web_usuarios WHERE cedula=%s', (usuario,))
                            cursorlocal.execute('DELETE FROM web_fotos WHERE cedula_id=%s', (usuario,))
                            cursorlocal.execute('DELETE FROM web_horariospermitidos WHERE cedula_id=%s', (usuario,))
                            connlocal.commit()
                    listausuariosheroku=[]
                    listausuarioslocal=[]

                # cuando se va a agregar usuarios
                if nro_usu_heroku > nro_usu_local:

                    for usuario in usuarios_heroku:
                        cedula=usuario[0]
                        try:
                            listausuariosheroku.index(cedula)
                        except ValueError:
                            listausuariosheroku.append(cedula)
                    
                    for usuario in usuarios_local:
                        cedula=usuario[0]
                        try:
                            listausuarioslocal.index(cedula)
                        except ValueError:
                            listausuarioslocal.append(cedula)

                    for usuario in listausuariosheroku:
                        try:
                            listausuarioslocal.index(usuario)
                        except ValueError:
                            cursorheroku.execute('SELECT * FROM web_usuarios where cedula=%s', (usuario,))
                            usuario_heroku= cursorheroku.fetchall()
                            cedula=usuario_heroku[0][0]
                            nombre=usuario_heroku[0][1]
                            cursorlocal.execute('''INSERT INTO web_usuarios (cedula, nombre, contrato_id)
                            VALUES (%s, %s, %s)''', (cedula, nombre, CONTRATO))
                            connlocal.commit()
                    listausuariosheroku=[]
                    listausuarioslocal=[]
                etapa=0

    except (Exception, psycopg2.Error) as error:
        print("fallo en hacer las consultas")
        if connlocal:
            cursorlocal.close()
            connlocal.close()
        if connheroku:
            cursorheroku.close()
            connheroku.close()
    finally:
        print("se ha cerrado la conexion a la base de datos")
        if connlocal:
            cursorlocal.close()
            connlocal.close()
        if connheroku:
            cursorheroku.close()
            connheroku.close()
