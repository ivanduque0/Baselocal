import psycopg2
import os
import time
connlocal = None
cursorlocal=None
total=0

######################################
#############ACCESOS###################
#######################################
acceso1=os.environ.get('URL_ACCESO1')
acceso2=os.environ.get('URL_ACCESO2')
acceso3=os.environ.get('URL_ACCESO3')
acceso4=os.environ.get('URL_ACCESO4')

descripcion_acceso1=os.environ.get('RAZON_BOT1')
descripcion_acceso2=os.environ.get('RAZON_BOT2')
descripcion_acceso3=os.environ.get('RAZON_BOT3')
descripcion_acceso4=os.environ.get('RAZON_BOT4')

######################################
#############CAMARAS###################
#######################################

camara1=os.environ.get('URL_CAMARA1')
camara2=os.environ.get('URL_CAMARA2')
camara3=os.environ.get('URL_CAMARA3')
camara4=os.environ.get('URL_CAMARA4')
# camara5=os.environ.get('URL_CAMARA5')
# camara6=os.environ.get('URL_CAMARA6')
# camara7=os.environ.get('URL_CAMARA7')
# camara8=os.environ.get('URL_CAMARA8')

descripcion_camara1=os.environ.get('RAZON_CAM1')
descripcion_camara2=os.environ.get('RAZON_CAM2')
descripcion_camara3=os.environ.get('RAZON_CAM3')
descripcion_camara4=os.environ.get('RAZON_CAM4')
# descripcion_camara5=os.environ.get('RAZON_CAM5')
# descripcion_camara6=os.environ.get('RAZON_CAM6')
# descripcion_camara7=os.environ.get('RAZON_CAM7')
# descripcion_camara8=os.environ.get('RAZON_CAM8')

dispositivos=[acceso1, acceso2, acceso3, acceso4, 
              camara1, camara2, camara3, camara4,
            #   camara5, camara6, camara7, camara7
              ]

dispositivos_dict ={acceso1:descripcion_acceso1, 
                    acceso2:descripcion_acceso2, 
                    acceso3:descripcion_acceso3, 
                    acceso4:descripcion_acceso4, 
                    camara1:descripcion_camara1, 
                    camara2:descripcion_camara2, 
                    camara3:descripcion_camara3, 
                    camara4:descripcion_camara4, 
                    # camara5:descripcion_camara5, 
                    # camara6:descripcion_camara6, 
                    # camara7:descripcion_camara7, 
                    # camara8:descripcion_camara8,
                    }

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


        cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_usuarios (cedula varchar(150), nombre varchar(150), telegram_id varchar(150), contrato_id varchar(150))')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_interacciones (nombre varchar(150), fecha date, hora time without time zone, razon varchar(150), contrato varchar(150), cedula_id varchar(150))')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_horariospermitidos (entrada time without time zone, salida time without time zone, cedula_id varchar(150), dia varchar(180))')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_fotos (id integer, foto varchar(150), estado integer, cedula_id varchar(150))')
        # cursorlocal.execute('CREATE TABLE IF NOT EXISTS led (onoff integer, acceso integer)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS dias_acumulados (fecha varchar(150))')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS sensor (onoff integer, acceso integer)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS antisp (spoofing integer, acceso integer)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS cargar_fotos (cargar integer)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_dispositivos (dispositivo varchar(150), descripcion varchar(150), estado varchar(150))')
        connlocal.commit()
        # cursorlocal.execute('SELECT*FROM led')
        # tablaled= cursorlocal.fetchall()
        cursorlocal.execute('SELECT*FROM sensor')
        tablasensor= cursorlocal.fetchall()
        cursorlocal.execute('SELECT*FROM antisp')
        tablaantisp= cursorlocal.fetchall()
        cursorlocal.execute('SELECT*FROM cargar_fotos')
        tablacargar= cursorlocal.fetchall()
        cursorlocal.execute('SELECT*FROM web_dispositivos')
        tabladispositivos= cursorlocal.fetchall()

        # if len(tablaled) < 1:
        #     cursorlocal.execute('INSERT INTO led values(0,1)')
        #     connlocal.commit()
        #     cursorlocal.execute('INSERT INTO led values(0,2)')
        #     connlocal.commit()
        #     cursorlocal.execute('INSERT INTO led values(0,3)')
        #     connlocal.commit()
        #     cursorlocal.execute('INSERT INTO led values(0,4)')
        #     connlocal.commit()

        if len(tabladispositivos) < 1:
            for dispositivo in dispositivos:
                if dispositivo:
                    descripcion = dispositivos_dict[dispositivo]
                    estado = '0'
                    cursorlocal.execute('INSERT INTO web_dispositivos values(%s, %s, %s)',(dispositivo, descripcion, estado))
                    connlocal.commit()

        if len(tablacargar) < 1:
            cursorlocal.execute('INSERT INTO cargar_fotos values(0)')
            connlocal.commit()

        if len(tablasensor) < 1:
            cursorlocal.execute('INSERT INTO sensor values(0,1)')
            connlocal.commit()
            cursorlocal.execute('INSERT INTO sensor values(0,2)')
            connlocal.commit()
            cursorlocal.execute('INSERT INTO sensor values(0,3)')
            connlocal.commit()
            cursorlocal.execute('INSERT INTO sensor values(0,4)')
            connlocal.commit()
        if len(tablaantisp) < 1:
            cursorlocal.execute('INSERT INTO antisp values(0,1)')
            connlocal.commit()
            cursorlocal.execute('INSERT INTO antisp values(0,2)')
            connlocal.commit()
            cursorlocal.execute('INSERT INTO antisp values(0,3)')
            connlocal.commit()
            cursorlocal.execute('INSERT INTO antisp values(0,4)')
            connlocal.commit()

    except (Exception, psycopg2.Error) as error:
        print("fallo en hacer las consultas")
        if connlocal:
            cursorlocal.close()
            connlocal.close()

    finally:
        print("se ha cerrado la conexion a la base de datos")
        if connlocal:
            cursorlocal.close()
            connlocal.close()
        break
    
