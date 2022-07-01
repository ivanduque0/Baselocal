import psycopg2
import os
import subprocess
import time

CONTRATO=os.environ.get("CONTRATO")
connlocal = None
connheroku = None
cursorheroku=None
cursorlocal=None
total=0

while True:
    
    t1=time.perf_counter()
    while total<=5:
        t2=time.perf_counter()
        total=t2-t1
    total=0
    try:
        
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
            t2=time.perf_counter()
            total=t2-t1

            if total>3:

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
