import psycopg2
import os
import time
connlocal = None
cursorlocal=None
total=0

SERVIDOR_LOCAL=os.environ.get('URL_SERVIDOR')

######################################
#############ACCESOS###################
#######################################
acceso1=os.environ.get('URL_ACCESO1')
acceso2=os.environ.get('URL_ACCESO2')
acceso3=os.environ.get('URL_ACCESO3')
acceso4=os.environ.get('URL_ACCESO4')
acceso5=os.environ.get('URL_ACCESO5')
acceso6=os.environ.get('URL_ACCESO6')
acceso7=os.environ.get('URL_ACCESO7')
acceso8=os.environ.get('URL_ACCESO8')
acceso9=os.environ.get('URL_ACCESO9')
acceso10=os.environ.get('URL_ACCESO10')
acceso11=os.environ.get('URL_ACCESO11')
acceso12=os.environ.get('URL_ACCESO12')
acceso13=os.environ.get('URL_ACCESO13')
acceso14=os.environ.get('URL_ACCESO14')
acceso15=os.environ.get('URL_ACCESO15')
acceso16=os.environ.get('URL_ACCESO16')
acceso17=os.environ.get('URL_ACCESO17')
acceso18=os.environ.get('URL_ACCESO18')
acceso19=os.environ.get('URL_ACCESO19')
acceso20=os.environ.get('URL_ACCESO20')

descripcion_acceso1=os.environ.get('RAZON_ACCESO1')
descripcion_acceso2=os.environ.get('RAZON_ACCESO2')
descripcion_acceso3=os.environ.get('RAZON_ACCESO3')
descripcion_acceso4=os.environ.get('RAZON_ACCESO4')
descripcion_acceso5=os.environ.get('RAZON_ACCESO5')
descripcion_acceso6=os.environ.get('RAZON_ACCESO6')
descripcion_acceso7=os.environ.get('RAZON_ACCESO7')
descripcion_acceso8=os.environ.get('RAZON_ACCESO8')
descripcion_acceso9=os.environ.get('RAZON_ACCESO9')
descripcion_acceso10=os.environ.get('RAZON_ACCESO10')
descripcion_acceso11=os.environ.get('RAZON_ACCESO11')
descripcion_acceso12=os.environ.get('RAZON_ACCESO12')
descripcion_acceso13=os.environ.get('RAZON_ACCESO13')
descripcion_acceso14=os.environ.get('RAZON_ACCESO14')
descripcion_acceso15=os.environ.get('RAZON_ACCESO15')
descripcion_acceso16=os.environ.get('RAZON_ACCESO16')
descripcion_acceso17=os.environ.get('RAZON_ACCESO17')
descripcion_acceso18=os.environ.get('RAZON_ACCESO18')
descripcion_acceso19=os.environ.get('RAZON_ACCESO19')
descripcion_acceso20=os.environ.get('RAZON_ACCESO20')

######################################
#############CAMARAS###################
#######################################

camara1=os.environ.get('URL_CAMARA1')
camara2=os.environ.get('URL_CAMARA2')
camara3=os.environ.get('URL_CAMARA3')
camara4=os.environ.get('URL_CAMARA4')
camara5=os.environ.get('URL_CAMARA5')
camara6=os.environ.get('URL_CAMARA6')
camara7=os.environ.get('URL_CAMARA7')
camara8=os.environ.get('URL_CAMARA8')
camara9=os.environ.get('URL_CAMARA9')
camara10=os.environ.get('URL_CAMARA10')
camara11=os.environ.get('URL_CAMARA11')
camara12=os.environ.get('URL_CAMARA12')
camara13=os.environ.get('URL_CAMARA13')
camara14=os.environ.get('URL_CAMARA14')
camara15=os.environ.get('URL_CAMARA15')
camara16=os.environ.get('URL_CAMARA16')
camara17=os.environ.get('URL_CAMARA17')
camara18=os.environ.get('URL_CAMARA18')
camara19=os.environ.get('URL_CAMARA19')
camara20=os.environ.get('URL_CAMARA20')

descripcion_camara1=os.environ.get('RAZON_CAM1')
descripcion_camara2=os.environ.get('RAZON_CAM2')
descripcion_camara3=os.environ.get('RAZON_CAM3')
descripcion_camara4=os.environ.get('RAZON_CAM4')
descripcion_camara5=os.environ.get('RAZON_CAM5')
descripcion_camara6=os.environ.get('RAZON_CAM6')
descripcion_camara7=os.environ.get('RAZON_CAM7')
descripcion_camara8=os.environ.get('RAZON_CAM8')
descripcion_camara9=os.environ.get('RAZON_CAM9')
descripcion_camara10=os.environ.get('RAZON_CAM10')
descripcion_camara11=os.environ.get('RAZON_CAM11')
descripcion_camara12=os.environ.get('RAZON_CAM12')
descripcion_camara13=os.environ.get('RAZON_CAM13')
descripcion_camara14=os.environ.get('RAZON_CAM14')
descripcion_camara15=os.environ.get('RAZON_CAM15')
descripcion_camara16=os.environ.get('RAZON_CAM16')
descripcion_camara17=os.environ.get('RAZON_CAM17')
descripcion_camara18=os.environ.get('RAZON_CAM18')
descripcion_camara19=os.environ.get('RAZON_CAM19')
descripcion_camara20=os.environ.get('RAZON_CAM20')


######################################
#############CAPTAHUELLAS#############
#######################################

captahuella1=os.environ.get('URL_CAPTAHUELLA1')
captahuella2=os.environ.get('URL_CAPTAHUELLA2')
captahuella3=os.environ.get('URL_CAPTAHUELLA3')
captahuella4=os.environ.get('URL_CAPTAHUELLA4')
captahuella5=os.environ.get('URL_CAPTAHUELLA5')
captahuella6=os.environ.get('URL_CAPTAHUELLA6')
captahuella7=os.environ.get('URL_CAPTAHUELLA7')
captahuella8=os.environ.get('URL_CAPTAHUELLA8')
captahuella9=os.environ.get('URL_CAPTAHUELLA9')
captahuella10=os.environ.get('URL_CAPTAHUELLA10')
captahuella11=os.environ.get('URL_CAPTAHUELLA11')
captahuella12=os.environ.get('URL_CAPTAHUELLA12')
captahuella13=os.environ.get('URL_CAPTAHUELLA13')
captahuella14=os.environ.get('URL_CAPTAHUELLA14')
captahuella15=os.environ.get('URL_CAPTAHUELLA15')
captahuella16=os.environ.get('URL_CAPTAHUELLA16')
captahuella17=os.environ.get('URL_CAPTAHUELLA17')
captahuella18=os.environ.get('URL_CAPTAHUELLA18')
captahuella19=os.environ.get('URL_CAPTAHUELLA19')
captahuella20=os.environ.get('URL_CAPTAHUELLA20')

descripcion_captahuella1=os.environ.get('RAZON_CAPTAHUELLA1')
descripcion_captahuella2=os.environ.get('RAZON_CAPTAHUELLA2')
descripcion_captahuella3=os.environ.get('RAZON_CAPTAHUELLA3')
descripcion_captahuella4=os.environ.get('RAZON_CAPTAHUELLA4')
descripcion_captahuella5=os.environ.get('RAZON_CAPTAHUELLA5')
descripcion_captahuella6=os.environ.get('RAZON_CAPTAHUELLA6')
descripcion_captahuella7=os.environ.get('RAZON_CAPTAHUELLA7')
descripcion_captahuella8=os.environ.get('RAZON_CAPTAHUELLA8')
descripcion_captahuella9=os.environ.get('RAZON_CAPTAHUELLA9')
descripcion_captahuella10=os.environ.get('RAZON_CAPTAHUELLA10')
descripcion_captahuella11=os.environ.get('RAZON_CAPTAHUELLA11')
descripcion_captahuella12=os.environ.get('RAZON_CAPTAHUELLA12')
descripcion_captahuella13=os.environ.get('RAZON_CAPTAHUELLA13')
descripcion_captahuella14=os.environ.get('RAZON_CAPTAHUELLA14')
descripcion_captahuella15=os.environ.get('RAZON_CAPTAHUELLA15')
descripcion_captahuella16=os.environ.get('RAZON_CAPTAHUELLA16')
descripcion_captahuella17=os.environ.get('RAZON_CAPTAHUELLA17')
descripcion_captahuella18=os.environ.get('RAZON_CAPTAHUELLA18')
descripcion_captahuella19=os.environ.get('RAZON_CAPTAHUELLA19')
descripcion_captahuella20=os.environ.get('RAZON_CAPTAHUELLA20')

######################################
################RFID###################
#######################################

rfid1=os.environ.get('URL_RFID1')
rfid2=os.environ.get('URL_RFID2')
rfid3=os.environ.get('URL_RFID3')
rfid4=os.environ.get('URL_RFID4')
rfid5=os.environ.get('URL_RFID5')
rfid6=os.environ.get('URL_RFID6')
rfid7=os.environ.get('URL_RFID7')
rfid8=os.environ.get('URL_RFID8')
rfid9=os.environ.get('URL_RFID9')
rfid10=os.environ.get('URL_RFID10')
rfid11=os.environ.get('URL_RFID11')
rfid12=os.environ.get('URL_RFID12')
rfid13=os.environ.get('URL_RFID13')
rfid14=os.environ.get('URL_RFID14')
rfid15=os.environ.get('URL_RFID15')
rfid16=os.environ.get('URL_RFID16')
rfid17=os.environ.get('URL_RFID17')
rfid18=os.environ.get('URL_RFID18')
rfid19=os.environ.get('URL_RFID19')
rfid20=os.environ.get('URL_RFID20')

descripcion_rfid1=os.environ.get('RAZON_RFID1')
descripcion_rfid2=os.environ.get('RAZON_RFID2')
descripcion_rfid3=os.environ.get('RAZON_RFID3')
descripcion_rfid4=os.environ.get('RAZON_RFID4')
descripcion_rfid5=os.environ.get('RAZON_RFID5')
descripcion_rfid6=os.environ.get('RAZON_RFID6')
descripcion_rfid7=os.environ.get('RAZON_RFID7')
descripcion_rfid8=os.environ.get('RAZON_RFID8')
descripcion_rfid9=os.environ.get('RAZON_RFID9')
descripcion_rfid10=os.environ.get('RAZON_RFID10')
descripcion_rfid11=os.environ.get('RAZON_RFID11')
descripcion_rfid12=os.environ.get('RAZON_RFID12')
descripcion_rfid13=os.environ.get('RAZON_RFID13')
descripcion_rfid14=os.environ.get('RAZON_RFID14')
descripcion_rfid15=os.environ.get('RAZON_RFID15')
descripcion_rfid16=os.environ.get('RAZON_RFID16')
descripcion_rfid17=os.environ.get('RAZON_RFID17')
descripcion_rfid18=os.environ.get('RAZON_RFID18')
descripcion_rfid19=os.environ.get('RAZON_RFID19')
descripcion_rfid20=os.environ.get('RAZON_RFID20')

dispositivos=[camara1, camara2, camara3, camara4, camara5,
              camara6, camara7, camara8, camara9, camara10,
              camara11, camara12, camara13, camara14, camara15,
              camara16, camara17, camara18, camara19, camara20,
              captahuella1, captahuella2, captahuella3, captahuella4, captahuella5,
              captahuella6, captahuella7, captahuella8, captahuella9, captahuella10,
              captahuella11, captahuella12, captahuella3, captahuella14, captahuella15,
              captahuella16, captahuella17, captahuella18, captahuella19, captahuella20,
              rfid1, rfid2, rfid3, rfid4, rfid5,
              rfid6, rfid7, rfid8, rfid9, rfid10,
              rfid11, rfid12, rfid13, rfid14, rfid15,
              rfid16, rfid17, rfid18, rfid19, rfid20,
              SERVIDOR_LOCAL
             ]

dispositivos_dict= {camara1:descripcion_camara1, 
                    camara2:descripcion_camara2, 
                    camara3:descripcion_camara3, 
                    camara4:descripcion_camara4,
                    camara5:descripcion_camara5, 
                    camara6:descripcion_camara6, 
                    camara7:descripcion_camara7, 
                    camara8:descripcion_camara8,
                    camara9:descripcion_camara9, 
                    camara10:descripcion_camara10, 
                    camara11:descripcion_camara11, 
                    camara12:descripcion_camara12, 
                    camara13:descripcion_camara13, 
                    camara14:descripcion_camara14, 
                    camara15:descripcion_camara15, 
                    camara16:descripcion_camara16, 
                    camara17:descripcion_camara17, 
                    camara18:descripcion_camara18, 
                    camara19:descripcion_camara19, 
                    camara20:descripcion_camara20, 
                    captahuella1:descripcion_captahuella1, 
                    captahuella2:descripcion_captahuella2, 
                    captahuella3:descripcion_captahuella3, 
                    captahuella4:descripcion_captahuella4, 
                    captahuella5:descripcion_captahuella5,
                    captahuella6:descripcion_captahuella6, 
                    captahuella7:descripcion_captahuella7, 
                    captahuella8:descripcion_captahuella8, 
                    captahuella9:descripcion_captahuella9, 
                    captahuella10:descripcion_captahuella10,
                    captahuella11:descripcion_captahuella11, 
                    captahuella12:descripcion_captahuella12, 
                    captahuella13:descripcion_captahuella13, 
                    captahuella14:descripcion_captahuella14, 
                    captahuella15:descripcion_captahuella15,
                    captahuella16:descripcion_captahuella16, 
                    captahuella17:descripcion_captahuella17, 
                    captahuella18:descripcion_captahuella18, 
                    captahuella19:descripcion_captahuella19, 
                    captahuella20:descripcion_captahuella20,
                    rfid1:descripcion_rfid1, 
                    rfid2:descripcion_rfid2,
                    rfid3:descripcion_rfid3,
                    rfid4:descripcion_rfid4,
                    rfid5:descripcion_rfid5,
                    rfid6:descripcion_rfid6, 
                    rfid7:descripcion_rfid7,
                    rfid8:descripcion_rfid8,
                    rfid9:descripcion_rfid9,
                    rfid10:descripcion_rfid10,
                    rfid11:descripcion_rfid11, 
                    rfid12:descripcion_rfid12,
                    rfid13:descripcion_rfid13,
                    rfid14:descripcion_rfid14,
                    rfid15:descripcion_rfid15,
                    rfid16:descripcion_rfid16, 
                    rfid17:descripcion_rfid17,
                    rfid18:descripcion_rfid18,
                    rfid19:descripcion_rfid19,
                    rfid20:descripcion_rfid20,
                    SERVIDOR_LOCAL:'SERVIDOR LOCAL'
                    }

accesos_dispositivos=[acceso1, acceso2, acceso3, acceso4,
                      acceso5, acceso6, acceso7, acceso8,
                      acceso9, acceso10, acceso11, acceso12,
                      acceso13, acceso14, acceso15, acceso16,
                      acceso17, acceso18, acceso19, acceso20]

accesos_dispositivos_dict ={acceso1:descripcion_acceso1, 
                            acceso2:descripcion_acceso2, 
                            acceso3:descripcion_acceso3, 
                            acceso4:descripcion_acceso4,
                            acceso5:descripcion_acceso5, 
                            acceso6:descripcion_acceso6, 
                            acceso7:descripcion_acceso7, 
                            acceso8:descripcion_acceso8,
                            acceso9:descripcion_acceso9, 
                            acceso10:descripcion_acceso10, 
                            acceso11:descripcion_acceso11, 
                            acceso12:descripcion_acceso12,
                            acceso13:descripcion_acceso13, 
                            acceso14:descripcion_acceso14, 
                            acceso15:descripcion_acceso15, 
                            acceso16:descripcion_acceso16,
                            acceso17:descripcion_acceso17, 
                            acceso18:descripcion_acceso18, 
                            acceso19:descripcion_acceso19, 
                            acceso20:descripcion_acceso20
                            }

accesos_dict = {acceso1:"1", 
                acceso2:"2", 
                acceso3:"3", 
                acceso4:"4",
                acceso5:"5", 
                acceso6:"6", 
                acceso7:"7", 
                acceso8:"8",
                acceso9:"9", 
                acceso10:"10", 
                acceso11:"11", 
                acceso12:"12",
                acceso13:"13", 
                acceso14:"14", 
                acceso15:"15", 
                acceso16:"16",
                acceso17:"17", 
                acceso18:"18", 
                acceso19:"19", 
                acceso20:"20"
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

        cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_usuarios (cedula varchar(150), nombre varchar(150), telegram_id varchar(150), internet boolean, wifi boolean, captahuella boolean, rfid boolean, facial boolean)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_interacciones (nombre varchar(150), fecha date, hora time without time zone, razon varchar(150), contrato varchar(150), cedula_id varchar(150))')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_horariospermitidos (entrada time without time zone, salida time without time zone, cedula_id varchar(150), dia varchar(180))')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_fotos (id integer, foto varchar(150), estado integer, cedula_id varchar(150))')
        # cursorlocal.execute('CREATE TABLE IF NOT EXISTS led (onoff integer, acceso integer)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS dias_acumulados (fecha varchar(150))')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS sensor (onoff integer, nro_camara integer)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS antisp (spoofing integer, nro_camara integer)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS cargar_fotos (cargar integer)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_dispositivos (dispositivo varchar(150), descripcion varchar(150), estado varchar(150), acceso varchar(150))')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_huellas (id_suprema integer, cedula varchar(150), template text)')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS web_tagsrfid (epc text, cedula varchar(150))')
        cursorlocal.execute('CREATE TABLE IF NOT EXISTS solicitud_aperturas (id integer, id_usuario varchar(150), acceso varchar(150), estado integer, peticionInternet boolean, feedback boolean)')
        #cursorlocal.execute('CREATE TABLE IF NOT EXISTS led (onoff integer, acceso integer)')
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
        if len(tabladispositivos) < 1:
            for dispositivo in dispositivos:
                if dispositivo:
                    descripcion = dispositivos_dict[dispositivo]
                    if dispositivo == SERVIDOR_LOCAL:
                        estado = '1'
                    else:
                        estado = '0'
                    cursorlocal.execute('INSERT INTO web_dispositivos values(%s, %s, %s, %s)',(dispositivo, descripcion, estado, ""))
                    connlocal.commit()
            
            for dispositivoAcceso in accesos_dispositivos:
                if dispositivoAcceso:
                    descripcion = accesos_dispositivos_dict[dispositivoAcceso]
                    acceso = accesos_dict[dispositivoAcceso]
                    estado = '0'
                    cursorlocal.execute('INSERT INTO web_dispositivos values(%s, %s, %s, %s)',(dispositivoAcceso, descripcion, estado, acceso))
                    connlocal.commit()
        if len(tablacargar) < 1:
            cursorlocal.execute('INSERT INTO cargar_fotos values(0)')
            connlocal.commit()

        if len(tablasensor) < 1:
            cursorlocal.execute('INSERT INTO sensor values(0,1)')
            cursorlocal.execute('INSERT INTO sensor values(0,2)')
            cursorlocal.execute('INSERT INTO sensor values(0,3)')
            cursorlocal.execute('INSERT INTO sensor values(0,4)')
            cursorlocal.execute('INSERT INTO sensor values(0,5)')
            cursorlocal.execute('INSERT INTO sensor values(0,6)')
            cursorlocal.execute('INSERT INTO sensor values(0,7)')
            cursorlocal.execute('INSERT INTO sensor values(0,8)')
            cursorlocal.execute('INSERT INTO sensor values(0,9)')
            cursorlocal.execute('INSERT INTO sensor values(0,10)')
            cursorlocal.execute('INSERT INTO sensor values(0,11)')
            cursorlocal.execute('INSERT INTO sensor values(0,12)')
            cursorlocal.execute('INSERT INTO sensor values(0,13)')
            cursorlocal.execute('INSERT INTO sensor values(0,14)')
            cursorlocal.execute('INSERT INTO sensor values(0,15)')
            cursorlocal.execute('INSERT INTO sensor values(0,16)')
            cursorlocal.execute('INSERT INTO sensor values(0,17)')
            cursorlocal.execute('INSERT INTO sensor values(0,18)')
            cursorlocal.execute('INSERT INTO sensor values(0,19)')
            cursorlocal.execute('INSERT INTO sensor values(0,20)')
            connlocal.commit()
        if len(tablaantisp) < 1:
            cursorlocal.execute('INSERT INTO antisp values(0,1)')
            cursorlocal.execute('INSERT INTO antisp values(0,2)')
            cursorlocal.execute('INSERT INTO antisp values(0,3)')
            cursorlocal.execute('INSERT INTO antisp values(0,4)')
            cursorlocal.execute('INSERT INTO antisp values(0,5)')
            cursorlocal.execute('INSERT INTO antisp values(0,6)')
            cursorlocal.execute('INSERT INTO antisp values(0,7)')
            cursorlocal.execute('INSERT INTO antisp values(0,8)')
            cursorlocal.execute('INSERT INTO antisp values(0,9)')
            cursorlocal.execute('INSERT INTO antisp values(0,10)')
            cursorlocal.execute('INSERT INTO antisp values(0,11)')
            cursorlocal.execute('INSERT INTO antisp values(0,12)')
            cursorlocal.execute('INSERT INTO antisp values(0,13)')
            cursorlocal.execute('INSERT INTO antisp values(0,14)')
            cursorlocal.execute('INSERT INTO antisp values(0,15)')
            cursorlocal.execute('INSERT INTO antisp values(0,16)')
            cursorlocal.execute('INSERT INTO antisp values(0,17)')
            cursorlocal.execute('INSERT INTO antisp values(0,18)')
            cursorlocal.execute('INSERT INTO antisp values(0,19)')
            cursorlocal.execute('INSERT INTO antisp values(0,20)')
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
    
