from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import psycopg2
import os
import pytz
from datetime import datetime
import requests
import ipaddress

hostName = '0.0.0.0'
serverPort = 43157
conn = None
cursor = None
dias_semana = ("Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo")
ultimahora = datetime.strptime('23:59:59', '%H:%M:%S').time()
primerahora = datetime.strptime('00:00:00', '%H:%M:%S').time()
total=0

def ip_del_actuador(valor):
    # L74: dispositivos_informacion.dispositivo holds the actuator's IP; None if it is not an IPv4 (or is 0.0.0.0).
    try:
        ip = ipaddress.IPv4Address(valor or '')
    except ValueError:
        return None
    return None if ip.is_unspecified else str(ip)

def obtener_dispositivo_rfid(cursorf, dispositivo_id):
    # The antenna identifies the actuator it opens by dispositivos_informacion.id.
    # A non-numeric id would make Postgres raise and leave the transaction aborted.
    if not dispositivo_id.isdigit():
        return None
    cursorf.execute("SELECT dispositivo, descripcion, tipo_acceso, tipo_dispositivo, sistema FROM dispositivos_informacion WHERE id=%s AND apertura=true", (int(dispositivo_id),))
    fila = cursorf.fetchone()
    if not fila:
        return None
    # Without an IPv4 the actuator can't be called: same as no device, like the RFID server, which leaves it out of
    # its list (S10). The first column becomes the bare IP; the URL is built where it is called.
    ip = ip_del_actuador(fila[0])
    return (ip,) + tuple(fila[1:]) if ip else None

def sentido_de(dispositivo, descripcion_apertura):
    # S12 (L56): the direction belongs to the antenna (inside or outside the gate), so its URL segment wins when it
    # is a valid direction; otherwise the relay's tipo_acceso.
    if descripcion_apertura in ('entrada', 'salida'):
        return descripcion_apertura
    if dispositivo and dispositivo[2] in ('entrada', 'salida'):
        return dispositivo[2]
    return None

def registrar_log(cursorf, connf, tag_idf, tag_codigof, fechaf, horaf, dispositivo_id, dispositivo, descripcion_apertura, resultado, motivo):
    # S12 fields: acceso_id is the relay's dispositivos_informacion.id (null without a relay),
    # acceso_nombre its descripcion at this moment.
    acceso_id = int(dispositivo_id) if dispositivo else None
    acceso_nombre = dispositivo[1] if dispositivo else None
    tipo_dispositivo = dispositivo[3] if dispositivo else None
    cursorf.execute('''INSERT INTO logs_rfid (tag_id, tag_codigo, fecha, hora, acceso_id, acceso_nombre, sentido, resultado, motivo, tipo_dispositivo)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);''', (tag_idf, tag_codigof, fechaf, horaf, acceso_id, acceso_nombre,
                                                         sentido_de(dispositivo, descripcion_apertura), resultado, motivo, tipo_dispositivo))
    connf.commit()

def aperturaconcedidarfid(tag_idf, fechaf, horaf, cursorf, connf, dispositivo_id, descripcion_apertura, tag_codigof=None):
    dispositivo = obtener_dispositivo_rfid(cursorf, dispositivo_id)
    if not dispositivo:
        print(f"DEBUG: no se encontro dispositivo de apertura con id={dispositivo_id}")
    resultado, motivo = ('abierto', None) if dispositivo else ('fallido', 'sin_dispositivo')
    try:
        if dispositivo:
            requests.get(url=f'http://{dispositivo[0]}/on', timeout=3)
    except Exception as error_http:
        print(f"fallo en peticion http a http://{dispositivo[0]}/on: {error_http}")
        resultado, motivo = 'fallido', 'sin_respuesta'
    finally:
        registrar_log(cursorf, connf, tag_idf, tag_codigof, fechaf, horaf, dispositivo_id, dispositivo, descripcion_apertura, resultado, motivo)

def aperturadenegada(cursorf, connf, dispositivo_id, tag_idf=None, motivo=None, epc=None, descripcion_apertura=None, tag_codigof=None):
    # motivo is the S12 code (tag_inactivo, sin_permiso_rfid, fuera_de_horario).
    if motivo:
        print(f'{epc} - {motivo}')
    if tag_idf is None:
        return
    dispositivo = obtener_dispositivo_rfid(cursorf, dispositivo_id)
    if not dispositivo:
        print(f"DEBUG: no se encontro dispositivo de apertura con id={dispositivo_id}")
    try:
        if dispositivo:
            requests.get(url=f'http://{dispositivo[0]}/off', timeout=3)
    except Exception as error_http:
        print(f"fallo en peticion http a http://{dispositivo[0]}/off: {error_http}")
    finally:
        tz = pytz.timezone('America/Caracas')
        caracas_now = datetime.now(tz)
        hora=str(caracas_now)[11:19]
        horahoy = datetime.strptime(hora, '%H:%M:%S').time()
        fecha=str(caracas_now)[:10]
        registrar_log(cursorf, connf, tag_idf, tag_codigof, fecha, horahoy, dispositivo_id, dispositivo, descripcion_apertura, 'denegado', motivo)

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/seguricel_wifi_activo":
            self.send_response(200)
            self.send_header("Content-type", "utf-8")
            self.end_headers()

    def do_POST(self):
        peticion=self.path[1::].split("/")

        # Routes: POST /{dispositivo_id}/noregistrado
        #         POST /{epc}/{dispositivo_id}/{descripcion}/seguricel_rfid_activo
        if len(peticion) == 2 and peticion[1] == "noregistrado":
            # Answer the antenna right away, as the ESP32 node does; nothing else happens for an unknown tag.
            self.send_response(200)
            self.send_header("Content-type", "utf-8")
            self.end_headers()
            acceso_solicitud, _ = peticion
            aperturadenegada(cursor, conn, acceso_solicitud)

        if len(peticion) == 4 and peticion[3] == "seguricel_rfid_activo":
            self.send_response(200)
            self.send_header("Content-type", "utf-8")
            self.end_headers()
            epc, acceso_solicitud, descripcion_apertura, _ = peticion
            diasusuario = []
            etapadia=0
            etapadiaapertura=0
            cantidaddias = 0
            contadoraux = 0
            cursor.execute("SELECT id, activo, codigo FROM vehiculos_tags_rfid where epc=%s", (epc,))
            datostag_rfid = cursor.fetchall()
            #print(datostag_rfid)

            if len(datostag_rfid)==0:
                aperturadenegada(cursor, conn, acceso_solicitud, None, 'tag_no_encontrado', None, descripcion_apertura)
            elif datostag_rfid[0][1] != True:
                aperturadenegada(cursor, conn, acceso_solicitud, datostag_rfid[0][0], 'tag_inactivo', epc, descripcion_apertura, tag_codigof=datostag_rfid[0][2])
            else:
                tag_id = datostag_rfid[0][0]
                tag_codigo = datostag_rfid[0][2]
                cursor.execute("SELECT usuario_id FROM vehiculos_informacion where tag_id=%s", (tag_id,))
                datosusuario_rfid = cursor.fetchall()
                if len(datosusuario_rfid)!=0:
                    cursor.execute("SELECT rfid, rol FROM perfiles_mobile where id=%s", (datosusuario_rfid[0][0],))
                    datosUsuario = cursor.fetchall()
                    permisoAperturaRFID = datosUsuario[0][0]
                    rol = datosUsuario[0][1]
                    if permisoAperturaRFID != True:
                        aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'sin_permiso_rfid', epc, descripcion_apertura, tag_codigof=tag_codigo)
                    elif rol == 'Propietario':
                        tz = pytz.timezone('America/Caracas')
                        caracas_now = datetime.now(tz)
                        hora=str(caracas_now)[11:19]
                        horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                        fecha=str(caracas_now)[:10]
                        aperturaconcedidarfid(tag_id, fecha, horahoy, cursor, conn, acceso_solicitud, descripcion_apertura, tag_codigof=tag_codigo)
                    else:
                        cursor.execute('SELECT entrada, salida, dia FROM horarios_horarioseinvitaciones where usuario_id=%s', (datosusuario_rfid[0][0],))
                        horarios_permitidos = cursor.fetchall()
                        if horarios_permitidos == []:
                            aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'fuera_de_horario', epc, descripcion_apertura, tag_codigof=tag_codigo)
                        else:
                            tz = pytz.timezone('America/Caracas')
                            caracas_now = datetime.now(tz)
                            dia = caracas_now.weekday()
                            diahoy = dias_semana[dia]
                            for entrada, salida, dia in horarios_permitidos:
                                diasusuario.append(dia)
                            cantidaddias = diasusuario.count(diahoy)
                            for entrada, salida, dia in horarios_permitidos:
                                if 'Siempre' in diasusuario:
                                    hora=str(caracas_now)[11:19]
                                    horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                                    fecha=str(caracas_now)[:10]
                                    etapadia=1
                                    aperturaconcedidarfid(tag_id, fecha, horahoy, cursor, conn, acceso_solicitud, descripcion_apertura, tag_codigof=tag_codigo)
                                    etapadiaapertura=1
                                    break
                                elif dia==diahoy and cantidaddias==1:
                                    hora=str(caracas_now)[11:19]
                                    horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                                    fecha=str(caracas_now)[:10]
                                    etapadia=1
                                    # entrada == salida is a loading error: it never matches (L14).
                                    if entrada==salida:
                                        aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'fuera_de_horario', epc, descripcion_apertura, tag_codigof=tag_codigo)
                                    if entrada<salida:
                                        if horahoy >= entrada and horahoy <= salida:
                                            #print('entrada concedida')
                                            aperturaconcedidarfid(tag_id, fecha, horahoy, cursor, conn, acceso_solicitud, descripcion_apertura, tag_codigof=tag_codigo)
                                            etapadiaapertura=1
                                        else:
                                            aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'fuera_de_horario', epc, descripcion_apertura, tag_codigof=tag_codigo)
                                            #print('fuera_de_horario')
                                    if entrada>salida:
                                        if (horahoy>=entrada and horahoy <=ultimahora) or (horahoy>=primerahora and horahoy <= salida):
                                            #print('entrada concedida')
                                            aperturaconcedidarfid(tag_id, fecha, horahoy, cursor, conn, acceso_solicitud, descripcion_apertura, tag_codigof=tag_codigo)
                                            etapadiaapertura=1
                                        else:
                                            aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'fuera_de_horario', epc, descripcion_apertura, tag_codigof=tag_codigo)
                                            #print('fuera_de_horario')
                                elif dia==diahoy and cantidaddias>1:
                                    hora=str(caracas_now)[11:19]
                                    horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                                    fecha=str(caracas_now)[:10]
                                    etapadia=1
                                    # entrada == salida never matches (L14): it counts as one more non-matching window.
                                    if entrada==salida:
                                        contadoraux = contadoraux+1
                                        if contadoraux == cantidaddias:
                                            aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'fuera_de_horario', epc, descripcion_apertura, tag_codigof=tag_codigo)
                                            contadoraux=0
                                    if entrada<salida:
                                        if horahoy >= entrada and horahoy <= salida:
                                            #print('entrada concedida')
                                            aperturaconcedidarfid(tag_id, fecha, horahoy, cursor, conn, acceso_solicitud, descripcion_apertura, tag_codigof=tag_codigo)
                                            etapadiaapertura=1
                                            contadoraux=0
                                            break
                                        else:
                                            contadoraux = contadoraux+1
                                            if contadoraux == cantidaddias:
                                                aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'fuera_de_horario', epc, descripcion_apertura, tag_codigof=tag_codigo)
                                                contadoraux=0
                                    if entrada>salida:
                                        if (horahoy>=entrada and horahoy <=ultimahora) or (horahoy>=primerahora and horahoy <= salida):
                                            #print('entrada concedida')
                                            aperturaconcedidarfid(tag_id, fecha, horahoy, cursor, conn, acceso_solicitud, descripcion_apertura, tag_codigof=tag_codigo)
                                            etapadiaapertura=1
                                            contadoraux=0
                                            break
                                        else:
                                            contadoraux = contadoraux+1
                                            if contadoraux == cantidaddias:
                                                aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'fuera_de_horario', epc, descripcion_apertura, tag_codigof=tag_codigo)
                                                contadoraux=0
                                            #print('fuera_de_horario')
                            if etapadia==0 and etapadiaapertura==0:
                                print(f"DEBUG: sin coincidencia de horario para tag_id={tag_id}, dia_hoy={diahoy}, horarios_permitidos={horarios_permitidos}")
                                aperturadenegada(cursor, conn, acceso_solicitud, tag_id, 'fuera_de_horario', epc, descripcion_apertura, tag_codigof=tag_codigo)
                                #print('Dia no permitido')
                    diasusuario=[]
                else:
                    tz = pytz.timezone('America/Caracas')
                    caracas_now = datetime.now(tz)
                    hora=str(caracas_now)[11:19]
                    horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                    fecha=str(caracas_now)[:10]
                    aperturaconcedidarfid(tag_id, fecha, horahoy, cursor, conn, acceso_solicitud, descripcion_apertura, tag_codigof=tag_codigo)


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
