import time
import psycopg2
import os
import pytz
from datetime import datetime
import urllib.request
import requests
# import requests # PARA USAR CUANDO SE USE UN SERVIDOR LOCAL
dias_semana = ("Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo")
ultimahora = datetime.strptime('23:59:59', '%H:%M:%S').time()
primerahora = datetime.strptime('00:00:00', '%H:%M:%S').time()
total=0
CONTRATO=os.environ.get("CONTRATO")
URL = os.environ.get("URL")


razon1=os.environ.get("RAZON_BOT1")
razon2=os.environ.get("RAZON_BOT2")
razon3=os.environ.get("RAZON_BOT3")
razon4=os.environ.get("RAZON_BOT4")
acceso1=os.environ.get('URL_ACCESO1')
acceso2=os.environ.get('URL_ACCESO2')
acceso3=os.environ.get('URL_ACCESO3')
acceso4=os.environ.get('URL_ACCESO4')

accesodict = {'1':acceso1, '2':acceso2, '3':acceso3, '4':acceso4}

# pulseaqui = [
#     'pulse aqui',
#     'pulse aqui',
#     'pulse aqui',
#     'pulse aqui',
#     'pulse aqui',
#     'pulse aqui',
#     'pulse aqui',
#     'pulse aqui',
#     'pulse aqui',
#     'pulse aqui',
#     'pulse aqui',
    
# ]

# keyboard = Keyboa(items=pulseaqui)

def aperturaconcedida(nombref, fechaf, horaf, razonf, contratof, cedulaf, cursorf, connf, acceso):
    
    try:
        urllib.request.urlopen(f'{accesodict[acceso]}/on')
        cursorf.execute('''INSERT INTO web_interacciones (nombre, fecha, hora, razon, contrato, cedula_id)
        VALUES (%s, %s, %s, %s, %s, %s);''', (nombref, fechaf, horaf, razonf, contratof, cedulaf))
        #cursorf.execute('''UPDATE led SET onoff=1 WHERE onoff=0;''')
        connf.commit()
    except:
        cursorf.execute('''INSERT INTO web_interacciones (nombre, fecha, hora, razon, contrato, cedula_id)
        VALUES (%s, %s, %s, %s, %s, %s);''', (nombref, fechaf, horaf, f'fallo_{razonf}', contratof, cedulaf))
        #cursorf.execute('''UPDATE led SET onoff=1 WHERE onoff=0;''')
        connf.commit()
    finally:
        pass
	
    # EN CASO DE USAR UN SERVIDOR LOCAL COMUN Y QUERER ACTIVAR CON SOLO UN ESP8266 EN CAMPO Y VARIOS ESP01, SE DEBE USAR ESTO
    # url = "http://tesis-reconocimiento-facial.herokuapp.com/apertura/"
    # dataa = {'contrato': CONTRATO, 'acceso': acceso}
    # requests.post(url, data=dataa)
    # r = requests.get('http://tesis-reconocimiento-facial.herokuapp.com/apertura$
    # jsonget = r.json()[0]
    # contrato = jsonget['contrato']
    # acceso = jsonget['acceso']
    # while contrato != CONTRATO or acceso == 'no':
    #     requests.post(url, data=dataa)
    #     r = requests.get('http://tesis-reconocimiento-facial.herokuapp.com/aper$
    #     jsonget = r.json()[0]
    #     contrato = jsonget['contrato']
    #     acceso = jsonget['acceso']
    # dataa = {'contrato': 'no', 'acceso': 'no'}
    # requests.post(url, data=dataa)
		     

def aperturadenegada(cursorf, connf, acceso):
    # cursorf.execute('''UPDATE led SET onoff=2 WHERE onoff=0;''')
    # connf.commit()
    try:
        urllib.request.urlopen(f'{accesodict[acceso]}/off')
    except:
        print("fallo en peticion http")
    finally:
        pass  

while True:
    
    t11=time.perf_counter()
    while total<=5:
        t22=time.perf_counter()
        total=t22-t11
    total=0

    try:

        conn = psycopg2.connect(
            database=os.environ.get("DATABASE"), 
            user=os.environ.get("USERDB"), 
            password=os.environ.get("PASSWORD"), 
            host=os.environ.get("HOST"), 
            port=os.environ.get("PORT")
        )
        cursor = conn.cursor()

        while True:

            resp = requests.get(url=URL)
            aperturas_solicitadas = resp.json()
            if len(aperturas_solicitadas):
                tz = pytz.timezone('America/Caracas')
                caracas_now = datetime.now(tz)
                hora=str(caracas_now)[11:19]
                fecha=str(caracas_now)[:10]
                #A PARTIR DE AQUI DEBO HACER QE SE COMPARE LA HORA Y FECHA ACTUAL
                #CON LA HORA Y FECHA QUE FUE ENVIADA LA SOLICITUD, NO DEBE SER DE UN DIA DISTINTO
                #, DEBE SER A LA MISMA HORA Y NO DEBE TENER MUCHOS MINUTOS DE DIFERENCIA
                for apertura in aperturas_solicitadas:
                    #print(dt['contrato'])
                    if apertura['contrato'] == CONTRATO:
                        solicitud_id=apertura['id']
                        cursor.execute('SELECT * FROM solicitud_aperturas WHERE id=%s',(solicitud_id,))
                        aperturas_local_existente= cursor.fetchall()
                        if not aperturas_local_existente:
                            id_usuario = apertura['id_usuario']
                            solicitud_acceso=apertura['acceso']
                            cursor.execute('''INSERT INTO solicitud_aperturas (id, id_usuario, acceso, estado)
                                VALUES (%s, %s, %s, %s)''', (solicitud_id, id_usuario, solicitud_acceso, 0))
                            conn.commit()

            cursor.execute('SELECT id, id_usuario, acceso, estado FROM solicitud_aperturas')
            aperturas_local= cursor.fetchall()

            for aperturalocal in aperturas_local:
                estado_solicitud=aperturalocal[3]
                #si es igual a 0 es porque aun no ha sido procesada la solicitud
                #de apertura
                if estado_solicitud == 0:
                    diasusuario = []
                    etapadia=0
                    etapadiaapertura=0
                    cantidaddias = 0
                    contadoraux = 0
                    id_usuario = aperturalocal[1]
                    acceso_solicitud=aperturalocal[2]
                    id_solicitud=aperturalocal[0]
                    cursor.execute("SELECT * FROM web_usuarios where telegram_id='%s'", (id_usuario,))
                    datosusuario = cursor.fetchall()
                    #print(datosusuario)
                    if len(datosusuario)!=0:
                        cedula=datosusuario[0][0]
                        nombre=datosusuario[0][1]
                        cursor.execute('SELECT * FROM web_horariospermitidos where cedula_id=%s', (cedula,))
                        horarios_permitidos = cursor.fetchall()
                        if horarios_permitidos != []:
                            tz = pytz.timezone('America/Caracas')
                            caracas_now = datetime.now(tz)
                            dia = caracas_now.weekday()
                            diahoy = dias_semana[dia]
                            for entrada, salida, _, dia in horarios_permitidos:
                                diasusuario.append(dia)
                            cantidaddias = diasusuario.count(dia)
                            for entrada, salida, _, dia in horarios_permitidos:
                                if 'Siempre' in diasusuario:
                                    hora=str(caracas_now)[11:19]
                                    horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                                    fecha=str(caracas_now)[:10]
                                    etapadia=1
                                    aperturaconcedida(nombre, fecha, horahoy, razon1, CONTRATO, cedula, cursor, conn, acceso_solicitud)
                                    etapadiaapertura=1
                                elif dia==diahoy and cantidaddias==1:
                                    hora=str(caracas_now)[11:19]
                                    horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                                    fecha=str(caracas_now)[:10]
                                    etapadia=1
                                    if entrada<salida:
                                        if horahoy >= entrada and horahoy <= salida:
                                            #print('entrada concedida')
                                            aperturaconcedida(nombre, fecha, horahoy, razon1, CONTRATO, cedula, cursor, conn, acceso_solicitud)
                                            etapadiaapertura=1
                                        else:
                                            aperturadenegada(cursor, conn, acceso_solicitud)
                                            #print('fuera de horario')
                                    if entrada>salida:
                                        if (horahoy>=entrada and horahoy <=ultimahora) or (horahoy>=primerahora and horahoy <= salida):
                                            #print('entrada concedida')
                                            aperturaconcedida(nombre, fecha, horahoy, razon1, CONTRATO, cedula, cursor, conn, acceso_solicitud)
                                            etapadiaapertura=1
                                        else:
                                            aperturadenegada(cursor, conn, acceso_solicitud)
                                            #print('fuera de horario')
                                elif dia==diahoy and cantidaddias>1:
                                    hora=str(caracas_now)[11:19]
                                    horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                                    fecha=str(caracas_now)[:10]
                                    etapadia=1
                                    if entrada<salida:
                                        if horahoy >= entrada and horahoy <= salida:
                                            #print('entrada concedida')
                                            aperturaconcedida(nombre, fecha, horahoy, razon1, CONTRATO, cedula, cursor, conn, acceso_solicitud)
                                            etapadiaapertura=1
                                            contadoraux=0
                                        else:
                                            contadoraux = contadoraux+1
                                            if contadoraux == cantidaddias:
                                                aperturadenegada(cursor, conn, acceso_solicitud)
                                                contadoraux=0
                                    if entrada>salida:
                                        if (horahoy>=entrada and horahoy <=ultimahora) or (horahoy>=primerahora and horahoy <= salida):
                                            #print('entrada concedida')
                                            aperturaconcedida(nombre, fecha, horahoy, razon1, CONTRATO, cedula, cursor, conn, acceso_solicitud)
                                            etapadiaapertura=1
                                            contadoraux=0
                                        else:
                                            contadoraux = contadoraux+1
                                            if contadoraux == cantidaddias:
                                                aperturadenegada(cursor, conn, acceso_solicitud)
                                                contadoraux=0
                                            #print('fuera de horario')
                            if etapadia==0 and etapadiaapertura==0:
                                aperturadenegada(cursor, conn, acceso_solicitud)
                                #print('Dia no permitido')
                        if horarios_permitidos == []:
                            aperturadenegada(cursor, conn, acceso_solicitud) 
                            #print('este usuario no tiene horarios establecidos')
                        diasusuario=[]
                    else:
                        aperturadenegada(cursor, conn, acceso_solicitud) 
                    cursor.execute('UPDATE solicitud_aperturas SET estado=%s WHERE id=%s;', 
                            (1, id_solicitud))
                    conn.commit()
    
        


    except (Exception, psycopg2.Error) as error:
        print("fallo en hacer las consultas")
        total=0

    finally:
        print("se ha cerrado la conexion a la base de datos")
        if conn:
            cursor.close()
            conn.close()
            total=0


