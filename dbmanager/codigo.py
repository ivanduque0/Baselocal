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
usuarios_faltantes_foto=[]
listausuariosheroku=[]
listausuarioslocal=[]
total=0
nro_int_local_old=0
siguiente=0 #esta variable se encargar de dar la orden de cuando se va a revisar la base de datos para agregar o eliminar los distintos datos
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
        
        #con esto se apunta a la base de datos en heroku
        conn_info = subprocess.run(["heroku", "config:get", "DATABASE_URL", "-a", 'tesis-reconocimiento-facial'], stdout = subprocess.PIPE)
        connuri = conn_info.stdout.decode('utf-8').strip()
        connheroku = psycopg2.connect(connuri)
        cursorheroku = connheroku.cursor()

        # cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_usuarios (cedula integer, nombre varchar(150), contrato_id varchar(150))')
        # cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_interacciones (nombre varchar(150), fecha date, hora time without time zone, razon varchar(150), contrato varchar(150), cedula_id integer)')
        # cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_horariospermitidos (entrada time without time zone, salida time without time zone, cedula_id integer, dia_id varchar(180))')
        # cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_fotos (foto varchar(150), cedula_id integer)')
        # connlocal.commit()

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

            if nro_int_local > nro_int_local_old:

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
                contrato=None
                cedula=None
                foto=None

            cursorlocal.execute('SELECT * FROM web_usuarios where contrato_id=%s', (CONTRATO,))
            usuarios_local= cursorlocal.fetchall()

            cursorheroku.execute('SELECT * FROM web_usuarios where contrato_id=%s', (CONTRATO,))
            usuarios_heroku= cursorheroku.fetchall()

            nro_usu_local = len(usuarios_local)
            nro_usu_heroku = len(usuarios_heroku)

            if total>5 and siguiente==0:
            
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
                cedula=None
                nombre=None
                listausuariosheroku=[]
                listausuarioslocal=[]
                siguiente=1
                total=0
                t1=time.perf_counter()

            #en esta parte se agrega o eliminan horarios de la base de datos local
            if total >5 and siguiente==1:

                for usuario in usuarios_local:
                    cedula=usuario[0]
                    try:
                        listausuarioslocal.index(cedula)
                    except ValueError:
                        listausuarioslocal.append(cedula)
                
                for usuario in listausuarioslocal:
                    cursorheroku.execute('SELECT entrada, salida, cedula_id, dia_id FROM web_horariospermitidos WHERE cedula_id=%s',(usuario,))
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
                                cursorlocal.execute('''INSERT INTO web_horariospermitidos (entrada, salida, cedula_id, dia_id)
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
                                cursorlocal.execute('DELETE FROM web_horariospermitidos WHERE entrada=%s AND salida=%s AND cedula_id=%s AND dia_id=%s',(entrada, salida, cedula, dia))
                                connlocal.commit()
                diaslocal=[]
                diasheroku=[]
                listausuariosheroku=[]
                listausuarioslocal=[]
                siguiente=2
                total=0
                t1=time.perf_counter()

            #En esta parte se se agregan o eliminan imagenes
            if total>5 and siguiente==2:
                
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
                    cursorlocal.execute('SELECT * FROM web_fotos where cedula_id=%s', (usuario,))
                    fotos_local= cursorlocal.fetchall()
                    if len(fotos_local) == 1:
                        foto=fotos_local[0][0]
                        cursorheroku.execute('SELECT * FROM web_fotos where cedula_id=%s', (usuario,))
                        foto_heroku= cursorheroku.fetchall()
                        if len(foto_heroku) == 0:
                            cursorlocal.execute('DELETE FROM web_fotos where cedula_id=%s', (usuario,))
                            connlocal.commit()
                            print(f'{foto}.jpg')
                            os.remove(f'{foto}.jpg')

                    if len(fotos_local) == 0:
                        cursorheroku.execute('SELECT * FROM web_fotos where cedula_id=%s', (usuario,))
                        foto_heroku= cursorheroku.fetchall()
                        if len(foto_heroku) == 1:
                            foto=foto_heroku[0][1]
                            cedula=foto_heroku[0][2]
                            cursorlocal.execute('''INSERT INTO web_fotos (foto, cedula_id)
                            VALUES (%s, %s);''', (foto, cedula))
                            connlocal.commit()
                            url = cloudinary.utils.cloudinary_url(foto)
                            url=url[0]
                            imagenurl = urllib.request.urlopen (url) #abrimos el URL
                            imagenarray = np.array(bytearray(imagenurl.read()),dtype=np.uint8)
                            fotovisible = cv2.imdecode (imagenarray,-1)
                            cv2.imwrite(f"{foto}.jpg",fotovisible)

                    
                total=0
                siguiente=0
                listausuariosheroku=[]
                listausuarioslocal=[]
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
