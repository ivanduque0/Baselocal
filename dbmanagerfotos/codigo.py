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
        
        conn_info = subprocess.run(["heroku", "config:get", "DATABASE_URL", "-a", 'tesis-reconocimiento-facial'], stdout = subprocess.PIPE)
        connuri = conn_info.stdout.decode('utf-8').strip()
        connheroku = psycopg2.connect(connuri)
        cursorheroku = connheroku.cursor()
        
        t1=time.perf_counter()
        while True:
            t2=time.perf_counter()
            total=t2-t1

            cursorlocal.execute('SELECT * FROM web_usuarios where contrato_id=%s', (CONTRATO,))
            usuarios_local= cursorlocal.fetchall()

            cursorheroku.execute('SELECT * FROM web_usuarios where contrato_id=%s', (CONTRATO,))
            usuarios_heroku= cursorheroku.fetchall()

            if total>3:
                
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
