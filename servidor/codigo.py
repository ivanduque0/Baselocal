from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import psycopg2
import os
import pytz
from datetime import datetime
import requests

hostName = '0.0.0.0'
serverPort = 43157
conn = None
cursor = None
dias_semana = ("Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo")
ultimahora = datetime.strptime('23:59:59', '%H:%M:%S').time()
primerahora = datetime.strptime('00:00:00', '%H:%M:%S').time()
total=0

def obtener_dispositivo_rfid(cursorf, acceso):
    cursorf.execute("SELECT dispositivo, descripcion, tipo_acceso, tipo_dispositivo, sistema FROM dispositivos_informacion WHERE acceso=%s AND sistema='rfid'", (acceso,))
    return cursorf.fetchone()

def aperturaconcedidarfid(tag_idf, fechaf, horaf, cursorf, connf, acceso):
    dispositivo = obtener_dispositivo_rfid(cursorf, acceso)
    tipo_acceso = dispositivo[2] if dispositivo else None
    tipo_dispositivo = dispositivo[3] if dispositivo else None
    razon = f'{dispositivo[1]}({dispositivo[4]})-{tipo_acceso}' if dispositivo else None
    try:
        if dispositivo:
            requests.get(url=f'{dispositivo[0]}/onrh', timeout=3)
    except:
        print("fallo en peticion http")
        razon = f'fallo_{razon}'
    finally:
        cursorf.execute('''INSERT INTO logs_rfid (tag_id, fecha, hora, razon, tipo_acceso, tipo_dispositivo)
        VALUES (%s, %s, %s, %s, %s, %s);''', (tag_idf, fechaf, horaf, razon, tipo_acceso, tipo_dispositivo))
        connf.commit()

def aperturadenegada(cursorf, connf, acceso, tag_idf=None, razon=None, epc=None):
    if razon:
        print(f'{epc} - {razon}')
    if tag_idf is None:
        return
    dispositivo = obtener_dispositivo_rfid(cursorf, acceso)
    tipo_acceso = dispositivo[2] if dispositivo else None
    tipo_dispositivo = dispositivo[3] if dispositivo else None
    razon_completa = f'DENEGADO {dispositivo[1]}({dispositivo[4]})-{razon}' if dispositivo else f'DENEGADO {razon}'
    try:
        if dispositivo:
            requests.get(url=f'{dispositivo[0]}/off', timeout=3)
    except:
        print("fallo en peticion http")
    finally:
        if razon and tipo_acceso:
            tz = pytz.timezone('America/Caracas')
            caracas_now = datetime.now(tz)
            hora=str(caracas_now)[11:19]
            horahoy = datetime.strptime(hora, '%H:%M:%S').time()
            fecha=str(caracas_now)[:10]
            cursorf.execute('''INSERT INTO logs_rfid (tag_id, fecha, hora, razon, tipo_acceso, tipo_dispositivo, denegado)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE);''', (tag_idf, fecha, horahoy, razon_completa, tipo_acceso, tipo_dispositivo))
            connf.commit()

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/seguricel_wifi_activo":
            self.send_response(200)
            self.send_header("Content-type", "utf-8")
            self.end_headers()

    def do_POST(self):
        peticion=self.path[1::].split("/")

        if len(peticion) == 2 and peticion[1] == "noregistrado":
            acceso_solicitud, _ = peticion
            aperturadenegada(cursor, conn, acceso_solicitud)

        if len(peticion) == 3 and peticion[2] == "seguricel_rfid_activo":
            self.send_response(200)
            self.send_header("Content-type", "utf-8")
            self.end_headers()
            epc, acceso_solicitud, _ = peticion
            diasusuario = []
            etapadia=0
            etapadiaapertura=0
            cantidaddias = 0
            contadoraux = 0
            cursor.execute("SELECT id, activo FROM vehiculos_tags_rfid where epc=%s", (epc,))
            datostag_rfid = cursor.fetchall()
            #print(datostag_rfid)

            if len(datostag_rfid)==0:
                aperturadenegada(cursor, conn, acceso_solicitud, None, 'tag no encontrado')
            elif datostag_rfid[0][1] != True:
                aperturadenegada(cursor, conn, acceso_solicitud, datostag_rfid[0][0], 'tag inactivo', epc)
            else:
                tag_id = datostag_rfid[0][0]
                cursor.execute("SELECT usuario_id FROM vehiculos_informacion where tag_id=%s", (tag_id,))
                datosusuario_rfid = cursor.fetchall()
                if len(datosusuario_rfid)!=0:
                    cursor.execute("SELECT rfid, rol FROM perfiles_mobile where id=%s", (datosusuario_rfid[0][0],))
                    datosUsuario = cursor.fetchall()
                    permisoAperturaRFID = datosUsuario[0][0]
                    rol = datosUsuario[0][1]
                    if permisoAperturaRFID != True:
                        aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'usuario sin permiso', epc)
                    elif rol == 'Propietario':
                        tz = pytz.timezone('America/Caracas')
                        caracas_now = datetime.now(tz)
                        hora=str(caracas_now)[11:19]
                        horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                        fecha=str(caracas_now)[:10]
                        aperturaconcedidarfid(tag_id, fecha, horahoy, cursor, conn, acceso_solicitud)
                    else:
                        cursor.execute('SELECT entrada, salida, dia FROM horarios_horarioseinvitaciones where usuario_id=%s', (datosusuario_rfid[0][0],))
                        horarios_permitidos = cursor.fetchall()
                        if horarios_permitidos == []:
                            aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'fuera de horario', epc)
                        else:
                            tz = pytz.timezone('America/Caracas')
                            caracas_now = datetime.now(tz)
                            dia = caracas_now.weekday()
                            diahoy = dias_semana[dia]
                            for entrada, salida, dia in horarios_permitidos:
                                diasusuario.append(dia)
                            cantidaddias = diasusuario.count(dia)
                            for entrada, salida, dia in horarios_permitidos:
                                if 'Siempre' in diasusuario:
                                    hora=str(caracas_now)[11:19]
                                    horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                                    fecha=str(caracas_now)[:10]
                                    etapadia=1
                                    aperturaconcedidarfid(tag_id, fecha, horahoy, cursor, conn, acceso_solicitud)
                                    etapadiaapertura=1
                                elif dia==diahoy and cantidaddias==1:
                                    hora=str(caracas_now)[11:19]
                                    horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                                    fecha=str(caracas_now)[:10]
                                    etapadia=1
                                    if entrada<salida:
                                        if horahoy >= entrada and horahoy <= salida:
                                            #print('entrada concedida')
                                            aperturaconcedidarfid(tag_id, fecha, horahoy, cursor, conn, acceso_solicitud)
                                            etapadiaapertura=1
                                        else:
                                            aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'fuera de horario', epc)
                                            #print('fuera de horario')
                                    if entrada>salida:
                                        if (horahoy>=entrada and horahoy <=ultimahora) or (horahoy>=primerahora and horahoy <= salida):
                                            #print('entrada concedida')
                                            aperturaconcedidarfid(tag_id, fecha, horahoy, cursor, conn, acceso_solicitud)
                                            etapadiaapertura=1
                                        else:
                                            aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'fuera de horario', epc)
                                            #print('fuera de horario')
                                elif dia==diahoy and cantidaddias>1:
                                    hora=str(caracas_now)[11:19]
                                    horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                                    fecha=str(caracas_now)[:10]
                                    etapadia=1
                                    if entrada<salida:
                                        if horahoy >= entrada and horahoy <= salida:
                                            #print('entrada concedida')
                                            aperturaconcedidarfid(tag_id, fecha, horahoy, cursor, conn, acceso_solicitud)
                                            etapadiaapertura=1
                                            contadoraux=0
                                        else:
                                            contadoraux = contadoraux+1
                                            if contadoraux == cantidaddias:
                                                aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'fuera de horario', epc)
                                                contadoraux=0
                                    if entrada>salida:
                                        if (horahoy>=entrada and horahoy <=ultimahora) or (horahoy>=primerahora and horahoy <= salida):
                                            #print('entrada concedida')
                                            aperturaconcedidarfid(tag_id, fecha, horahoy, cursor, conn, acceso_solicitud)
                                            etapadiaapertura=1
                                            contadoraux=0
                                        else:
                                            contadoraux = contadoraux+1
                                            if contadoraux == cantidaddias:
                                                aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'fuera de horario', epc)
                                                contadoraux=0
                                            #print('fuera de horario')
                            if etapadia==0 and etapadiaapertura==0:
                                aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'fuera de horario', epc)
                                #print('Dia no permitido')
                    diasusuario=[]
                else:
                    tz = pytz.timezone('America/Caracas')
                    caracas_now = datetime.now(tz)
                    hora=str(caracas_now)[11:19]
                    horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                    fecha=str(caracas_now)[:10]
                    aperturaconcedidarfid(tag_id, fecha, horahoy, cursor, conn, acceso_solicitud)


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
                database=os.environ.get("POSTGRES_DB"),
                user=os.environ.get("POSTGRES_USER"),
                password=os.environ.get("POSTGRES_PASSWORD"),
                host=os.environ.get("POSTGRES_HOST"),
                port=os.environ.get("POSTGRES_PORT")
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
