from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import psycopg2
import os
import pytz
from datetime import datetime
import urllib.request

hostName = '0.0.0.0'
serverPort = 43157
conn = None
cursor = None
dias_semana = ("Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo")
ultimahora = datetime.strptime('23:59:59', '%H:%M:%S').time()
primerahora = datetime.strptime('00:00:00', '%H:%M:%S').time()
total=0
CONTRATO=os.environ.get("CONTRATO")

razon1=os.environ.get("RAZON_TELEFONO1")
razon2=os.environ.get("RAZON_TELEFONO2")
razon3=os.environ.get("RAZON_TELEFONO3")
razon4=os.environ.get("RAZON_TELEFONO4")
razon5=os.environ.get("RAZON_TELEFONO5")
razon6=os.environ.get("RAZON_TELEFONO6")
razon7=os.environ.get("RAZON_TELEFONO7")
razon8=os.environ.get("RAZON_TELEFONO8")
razon9=os.environ.get("RAZON_TELEFONO9")
razon10=os.environ.get("RAZON_TELEFONO10")
razon11=os.environ.get("RAZON_TELEFONO11")
razon12=os.environ.get("RAZON_TELEFONO12")
razon13=os.environ.get("RAZON_TELEFONO13")
razon14=os.environ.get("RAZON_TELEFONO14")
razon15=os.environ.get("RAZON_TELEFONO15")
razon16=os.environ.get("RAZON_TELEFONO16")
razon17=os.environ.get("RAZON_TELEFONO17")
razon18=os.environ.get("RAZON_TELEFONO18")
razon19=os.environ.get("RAZON_TELEFONO19")
razon20=os.environ.get("RAZON_TELEFONO20")


razonhuella1=os.environ.get("RAZON_CAPTAHUELLA1")
razonhuella2=os.environ.get("RAZON_CAPTAHUELLA2")
razonhuella3=os.environ.get("RAZON_CAPTAHUELLA3")
razonhuella4=os.environ.get("RAZON_CAPTAHUELLA4")
razonhuella5=os.environ.get("RAZON_CAPTAHUELLA5")
razonhuella6=os.environ.get("RAZON_CAPTAHUELLA6")
razonhuella7=os.environ.get("RAZON_CAPTAHUELLA7")
razonhuella8=os.environ.get("RAZON_CAPTAHUELLA8")
razonhuella9=os.environ.get("RAZON_CAPTAHUELLA9")
razonhuella10=os.environ.get("RAZON_CAPTAHUELLA10")
razonhuella11=os.environ.get("RAZON_CAPTAHUELLA11")
razonhuella12=os.environ.get("RAZON_CAPTAHUELLA12")
razonhuella13=os.environ.get("RAZON_CAPTAHUELLA13")
razonhuella14=os.environ.get("RAZON_CAPTAHUELLA14")
razonhuella15=os.environ.get("RAZON_CAPTAHUELLA15")
razonhuella16=os.environ.get("RAZON_CAPTAHUELLA16")
razonhuella17=os.environ.get("RAZON_CAPTAHUELLA17")
razonhuella18=os.environ.get("RAZON_CAPTAHUELLA18")
razonhuella19=os.environ.get("RAZON_CAPTAHUELLA19")
razonhuella20=os.environ.get("RAZON_CAPTAHUELLA20")

razonrfid1=os.environ.get("RAZON_RFID1")
razonrfid2=os.environ.get("RAZON_RFID2")
razonrfid3=os.environ.get("RAZON_RFID3")
razonrfid4=os.environ.get("RAZON_RFID4")
razonrfid5=os.environ.get("RAZON_RFID5")
razonrfid6=os.environ.get("RAZON_RFID6")
razonrfid7=os.environ.get("RAZON_RFID7")
razonrfid8=os.environ.get("RAZON_RFID8")
razonrfid9=os.environ.get("RAZON_RFID9")
razonrfid10=os.environ.get("RAZON_RFID10")
razonrfid11=os.environ.get("RAZON_RFID11")
razonrfid12=os.environ.get("RAZON_RFID12")
razonrfid13=os.environ.get("RAZON_RFID13")
razonrfid14=os.environ.get("RAZON_RFID14")
razonrfid15=os.environ.get("RAZON_RFID15")
razonrfid16=os.environ.get("RAZON_RFID16")
razonrfid17=os.environ.get("RAZON_RFID17")
razonrfid18=os.environ.get("RAZON_RFID18")
razonrfid19=os.environ.get("RAZON_RFID19")
razonrfid20=os.environ.get("RAZON_RFID20")

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

accesodict = {'1':acceso1, '2':acceso2, '3':acceso3, '4':acceso4, '5':acceso5,
                '6':acceso6, '7':acceso7, '8':acceso8, '9':acceso9, '10':acceso10,
                '11':acceso11, '12':acceso12, '13':acceso13, '14':acceso14, '15':acceso15,
                '16':acceso16, '17':acceso17, '18':acceso18, '19':acceso19, '20':acceso20
                }
razondict = {'1':razon1, '2':razon2, '3':razon3, '4':razon4, '5':razon5,
            '6':razon6, '7':razon7, '8':razon8, '9':razon9, '10':razon10,
            '11':razon11, '12':razon12, '13':razon13, '14':razon14, '15':razon15,
                '16':razon16, '17':razon17, '18':razon18, '19':razon19, '20':razon20}

razondicthuellas = {'1':razonhuella1, '2':razonhuella2, '3':razonhuella3, '4':razonhuella4,  '5':razonhuella5,
                    '6':razonhuella6, '7':razonhuella7, '8':razonhuella8, '9':razonhuella9,  '10':razonhuella10,
                    '11':razonhuella11, '12':razonhuella12, '13':razonhuella13, '14':razonhuella14, '15':razonhuella15,
                    '16':razonhuella16, '17':razonhuella17, '18':razonhuella18, '19':razonhuella19, '20':razonhuella20}

razondictrfids = {'1':razonrfid1, '2':razonrfid2, '3':razonrfid3, '4':razonrfid4, '5':razonrfid5,
                    '6':razonrfid6, '7':razonrfid7, '8':razonrfid8, '9':razonrfid9, '10':razonrfid10,
                    '11':razonrfid11, '12':razonrfid12, '13':razonrfid13, '14':razonrfid14, '15':razonrfid15,
                    '16':razonrfid16, '17':razonrfid17, '18':razonrfid18, '19':razonrfid19, '20':razonrfid20}

def aperturaconcedida(nombref, fechaf, horaf, contratof, cedulaf, cursorf, connf, acceso):

    try:
        if accesodict[acceso]:
            urllib.request.urlopen(url=f'{accesodict[acceso]}/on', timeout=3)
            cursorf.execute('''INSERT INTO web_interacciones (nombre, fecha, hora, razon, contrato, cedula_id)
            VALUES (%s, %s, %s, %s, %s, %s);''', (nombref, fechaf, horaf, razondict[acceso], contratof, cedulaf))
            #cursorf.execute('''UPDATE led SET onoff=1 WHERE onoff=0;''')
            connf.commit()
    except:
        cursorf.execute('''INSERT INTO web_interacciones (nombre, fecha, hora, razon, contrato, cedula_id)
        VALUES (%s, %s, %s, %s, %s, %s);''', (nombref, fechaf, horaf, f'fallo_{razondict[acceso]}', contratof, cedulaf))
        #cursorf.execute('''UPDATE led SET onoff=1 WHERE onoff=0;''')
        connf.commit()
    finally:
        pass

def aperturaconcedidahuella(nombref, fechaf, horaf, contratof, cedulaf, cursorf, connf, acceso):

    try:
        if accesodict[acceso]:
            urllib.request.urlopen(url=f'{accesodict[acceso]}/on', timeout=3)
            cursorf.execute('''INSERT INTO web_interacciones (nombre, fecha, hora, razon, contrato, cedula_id)
            VALUES (%s, %s, %s, %s, %s, %s);''', (nombref, fechaf, horaf, razondicthuellas[acceso], contratof, cedulaf))
            #cursorf.execute('''UPDATE led SET onoff=1 WHERE onoff=0;''')
            connf.commit()
    except:
        cursorf.execute('''INSERT INTO web_interacciones (nombre, fecha, hora, razon, contrato, cedula_id)
        VALUES (%s, %s, %s, %s, %s, %s);''', (nombref, fechaf, horaf, f'fallo_{razondicthuellas[acceso]}', contratof, cedulaf))
        #cursorf.execute('''UPDATE led SET onoff=1 WHERE onoff=0;''')
        connf.commit()
    finally:
        pass

def aperturaconcedidarfid(nombref, fechaf, horaf, contratof, cedulaf, cursorf, connf, acceso):

    try:
        if accesodict[acceso]:
            urllib.request.urlopen(url=f'{accesodict[acceso]}/on', timeout=3)
            cursorf.execute('''INSERT INTO web_interacciones (nombre, fecha, hora, razon, contrato, cedula_id)
            VALUES (%s, %s, %s, %s, %s, %s);''', (nombref, fechaf, horaf, razondictrfids[acceso], contratof, cedulaf))
            #cursorf.execute('''UPDATE led SET onoff=1 WHERE onoff=0;''')
            connf.commit()
    except:
        cursorf.execute('''INSERT INTO web_interacciones (nombre, fecha, hora, razon, contrato, cedula_id)
        VALUES (%s, %s, %s, %s, %s, %s);''', (nombref, fechaf, horaf, f'fallo_{razondictrfids[acceso]}', contratof, cedulaf))
        #cursorf.execute('''UPDATE led SET onoff=1 WHERE onoff=0;''')
        connf.commit()
    finally:
        pass

def aperturadenegada(cursorf, connf, acceso):
    # cursorf.execute('''UPDATE led SET onoff=2 WHERE onoff=0;''')
    # connf.commit()
    try:
        urllib.request.urlopen(url=f'{accesodict[acceso]}/off', timeout=3)
    except:
        print("fallo en peticion http")
    finally:
        pass

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/seguricel_wifi_activo":
            self.send_response(200)
            self.send_header("Content-type", "utf-8")
            self.end_headers()
        # else:
        #     print("cerrado")
        #     webServer.shutdown()
        
        # peticion=self.path[1::].split("/")
        # print(f"peticion = {peticion}")
        # self.send_header("Content-type", "utf-8")
        # self.end_headers()
        #self.wfile.write(bytes(f"{self.path[1::]}", "utf-8"))

        

    def do_POST(self):
        peticion=self.path[1::].split("/")

        if len(peticion) == 2 and peticion[1] == "noregistrado":
            acceso_solicitud, _ = peticion
            aperturadenegada(cursor, conn, acceso_solicitud)

        if len(peticion) == 3 and peticion[2] == "seguricel_wifi_activo":
            self.send_response(200)
            self.send_header("Content-type", "utf-8")
            self.end_headers()
            # self.wfile.write(bytes(f"{self.path[1::]}", "utf-8"))

            id_usuario, acceso_solicitud, _ = peticion
            #print(id_usuario)
            #print(acceso_solicitud)

            diasusuario = []
            etapadia=0
            etapadiaapertura=0
            cantidaddias = 0
            contadoraux = 0
            cursor.execute("SELECT * FROM web_usuarios where telegram_id=%s", (id_usuario,))
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
                            aperturaconcedida(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
                            etapadiaapertura=1
                        elif dia==diahoy and cantidaddias==1:
                            hora=str(caracas_now)[11:19]
                            horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                            fecha=str(caracas_now)[:10]
                            etapadia=1
                            if entrada<salida:
                                if horahoy >= entrada and horahoy <= salida:
                                    #print('entrada concedida')
                                    aperturaconcedida(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
                                    etapadiaapertura=1
                                else:
                                    aperturadenegada(cursor, conn, acceso_solicitud)
                                    #print('fuera de horario')
                            if entrada>salida:
                                if (horahoy>=entrada and horahoy <=ultimahora) or (horahoy>=primerahora and horahoy <= salida):
                                    #print('entrada concedida')
                                    aperturaconcedida(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
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
                                    aperturaconcedida(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
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
                                    aperturaconcedida(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
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

        if len(peticion) == 3 and peticion[2] == "seguricel_bluetooth_activo":
            self.send_response(200)
            self.send_header("Content-type", "utf-8")
            self.end_headers()
            # self.wfile.write(bytes(f"{self.path[1::]}", "utf-8"))

            uuid_usuario, acceso_solicitud, _ = peticion
            #print(id_usuario)
            #print(acceso_solicitud)

            diasusuario = []
            etapadia=0
            etapadiaapertura=0
            cantidaddias = 0
            contadoraux = 0
            cursor.execute("SELECT * FROM web_usuarios where telegram_id=%s", (uuid_usuario,))
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
                            aperturaconcedida(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
                            etapadiaapertura=1
                        elif dia==diahoy and cantidaddias==1:
                            hora=str(caracas_now)[11:19]
                            horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                            fecha=str(caracas_now)[:10]
                            etapadia=1
                            if entrada<salida:
                                if horahoy >= entrada and horahoy <= salida:
                                    #print('entrada concedida')
                                    aperturaconcedida(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
                                    etapadiaapertura=1
                                else:
                                    aperturadenegada(cursor, conn, acceso_solicitud)
                                    #print('fuera de horario')
                            if entrada>salida:
                                if (horahoy>=entrada and horahoy <=ultimahora) or (horahoy>=primerahora and horahoy <= salida):
                                    #print('entrada concedida')
                                    aperturaconcedida(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
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
                                    aperturaconcedida(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
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
                                    aperturaconcedida(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
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

        if len(peticion) == 3 and peticion[2] == "seguricel_captahuella_activo":
            self.send_response(200)
            self.send_header("Content-type", "utf-8")
            self.end_headers()
            # self.wfile.write(bytes(f"{self.path[1::]}", "utf-8"))

            id_suprema, acceso_solicitud, _ = peticion
            id_suprema = id_suprema[6:]+id_suprema[4:6]+id_suprema[2:4]+id_suprema[0:2]
            id_suprema = int(id_suprema, 16)
            #print(id_suprema)
            #print(acceso_solicitud)

            diasusuario = []
            etapadia=0
            etapadiaapertura=0
            cantidaddias = 0
            contadoraux = 0
            cursor.execute("SELECT cedula FROM web_huellas where id_suprema=%s", (id_suprema,))
            datosusuario_huella = cursor.fetchall()
            #print(datosusuario)
            if len(datosusuario_huella)!=0:
                cursor.execute("SELECT * FROM web_usuarios where cedula=%s", (datosusuario_huella[0][0],))
                datosusuario = cursor.fetchall()
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
                            aperturaconcedidahuella(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
                            etapadiaapertura=1
                        elif dia==diahoy and cantidaddias==1:
                            hora=str(caracas_now)[11:19]
                            horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                            fecha=str(caracas_now)[:10]
                            etapadia=1
                            if entrada<salida:
                                if horahoy >= entrada and horahoy <= salida:
                                    #print('entrada concedida')
                                    aperturaconcedidahuella(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
                                    etapadiaapertura=1
                                else:
                                    aperturadenegada(cursor, conn, acceso_solicitud)
                                    #print('fuera de horario')
                            if entrada>salida:
                                if (horahoy>=entrada and horahoy <=ultimahora) or (horahoy>=primerahora and horahoy <= salida):
                                    #print('entrada concedida')
                                    aperturaconcedidahuella(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
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
                                    aperturaconcedidahuella(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
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
                                    aperturaconcedidahuella(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
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

        if len(peticion) == 3 and peticion[2] == "seguricel_rfid_activo":
            self.send_response(200)
            self.send_header("Content-type", "utf-8")
            self.end_headers()
            # self.wfile.write(bytes(f"{self.path[1::]}", "utf-8"))
            epc, acceso_solicitud, _ = peticion
            diasusuario = []
            etapadia=0
            etapadiaapertura=0
            cantidaddias = 0
            contadoraux = 0
            cursor.execute("SELECT cedula FROM web_tagsrfid where epc=%s", (epc,))
            datosusuario_rfid = cursor.fetchall()
            #print(datosusuario)
            if len(datosusuario_rfid)!=0:
                cursor.execute("SELECT * FROM web_usuarios where cedula=%s", (datosusuario_rfid[0][0],))
                datosusuario = cursor.fetchall()
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
                            aperturaconcedidarfid(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
                            etapadiaapertura=1
                        elif dia==diahoy and cantidaddias==1:
                            hora=str(caracas_now)[11:19]
                            horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                            fecha=str(caracas_now)[:10]
                            etapadia=1
                            if entrada<salida:
                                if horahoy >= entrada and horahoy <= salida:
                                    #print('entrada concedida')
                                    aperturaconcedidarfid(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
                                    etapadiaapertura=1
                                else:
                                    aperturadenegada(cursor, conn, acceso_solicitud)
                                    #print('fuera de horario')
                            if entrada>salida:
                                if (horahoy>=entrada and horahoy <=ultimahora) or (horahoy>=primerahora and horahoy <= salida):
                                    #print('entrada concedida')
                                    aperturaconcedidarfid(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
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
                                    aperturaconcedidarfid(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
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
                                    aperturaconcedidarfid(nombre, fecha, horahoy, CONTRATO, cedula, cursor, conn, acceso_solicitud)
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


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

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
            webServer.serve_forever()
            print("fallo server")
        except (Exception, psycopg2.Error, KeyboardInterrupt) as error:
            print("fallo en hacer las consultas")
            total=0
        finally:
            print("se ha cerrado la conexion a la base de datos")
            print("Server stopped.")
            if conn:
                cursor.close()
                conn.close()
                total=0
            webServer.server_close()