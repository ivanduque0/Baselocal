from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import psycopg2
import os
import pytz
from datetime import datetime
import urllib.request

hostName = '0.0.0.0'
serverPort = 43157

dias_semana = ("Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo")
ultimahora = datetime.strptime('23:59:59', '%H:%M:%S').time()
primerahora = datetime.strptime('00:00:00', '%H:%M:%S').time()
total=0
CONTRATO=os.environ.get("CONTRATO")

razon1=os.environ.get("RAZON_BOT1")
razon2=os.environ.get("RAZON_BOT2")
razon3=os.environ.get("RAZON_BOT3")
razon4=os.environ.get("RAZON_BOT4")
razonhuella1=os.environ.get("RAZON_CAPTAHUELLA1")
razonhuella2=os.environ.get("RAZON_CAPTAHUELLA2")
razonhuella3=os.environ.get("RAZON_CAPTAHUELLA3")
razonhuella4=os.environ.get("RAZON_CAPTAHUELLA4")
acceso1=os.environ.get('URL_ACCESO1')
acceso2=os.environ.get('URL_ACCESO2')
acceso3=os.environ.get('URL_ACCESO3')
acceso4=os.environ.get('URL_ACCESO4')

accesodict = {'1':acceso1, '2':acceso2, '3':acceso3, '4':acceso4}
razondict = {'1':razon1, '2':razon2, '3':razon3, '4':razon4}
razondicthuellas = {'1':razonhuella1, '2':razonhuella2, '3':razonhuella3, '4':razonhuella4}
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
            print(id_usuario)
            print(acceso_solicitud)

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