import psycopg2
import os
import time as tm
import pytz
from datetime import datetime, date, time
import cloudinary
import requests
import numpy as np
import cv2

CONTRATO=os.environ.get("CONTRATO")
URL_API=os.environ.get("URL_API")
maximo_dias_acumular=int(os.environ.get("DIAS_ACUMULAR"))
connlocal = None
cursorlocal=None
listaHuellasServidor=[]
listahuellaslocal=[]
listaempleadosseguricel=[]
total=0
fechahoy=None
fechaayer=None
dias_acumulados=[]
nroCaptahuellasConHuella=0
nroCaptahuellasSinHuella=0
captahuella_actual=0
DIRECTORIO=os.environ.get("DIRECTORIO", "media/personas")
cambiarEstadoFotos=True
BorrarPeticionesListas=True
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

captahuellas=[captahuella1, captahuella2, captahuella3, captahuella4, captahuella5,
              captahuella6, captahuella7, captahuella8, captahuella9, captahuella10,
              captahuella11, captahuella12, captahuella13, captahuella14, captahuella15,
              captahuella16, captahuella17, captahuella18, captahuella19, captahuella20, 
              ]
if not os.path.exists(DIRECTORIO): 
    os.makedirs(DIRECTORIO)

cloudinary.config( 
    cloud_name = os.environ.get("CLOUD_NAME"), 
    api_key = os.environ.get("API_KEY"), 
    api_secret = os.environ.get("API_SECRET"),
    secure = True
)
while True:
    
    t1=tm.perf_counter()
    while total<=5:
        t2=tm.perf_counter()
        total=t2-t1
    total=0
    t1=0
    t2=0
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
        
        t1_cambios=tm.perf_counter()
        t1_log=tm.perf_counter()
        while True:
            t2_cambios=tm.perf_counter()
            t2_log=tm.perf_counter()
            total_cambios=t2_cambios-t1_cambios
            total_log=t2_log-t1_log


            if total_cambios > TIEMPO_CAMBIOS:
                request_json = requests.get(url=f'{URL_API}vercambiosapi/{CONTRATO}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                for consultajson in request_json:
                    idCambio=consultajson['id']
                    tablaCambiada=consultajson['tabla']
                    cedulaUsuario=consultajson['cedula']

                    # print(f'idCambio:{idCambio}')
                    # print(f'tablaCambiada:{tablaCambiada}')
                    # print(f'cedulaUsuario:{cedulaUsuario}')

                    if tablaCambiada == 'Usuarios':
                        try:
                            try:
                                banderaUsuario=True
                                cursorlocal.execute('SELECT cedula, nombre, telegram_id, internet, wifi, captahuella, rfid, facial FROM web_usuarios WHERE cedula=%s',(cedulaUsuario,))
                                usuario_local= cursorlocal.fetchall()

                                request_json_usuario = requests.get(url=f'{URL_API}usuarioindividualapi/{CONTRATO}/{cedulaUsuario}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()
                                usuarioLocal=len(usuario_local)
                                usuarioServidor=len(request_json_usuario)
                                if usuarioLocal and not usuarioServidor:
                                    cursorlocal.execute('SELECT id_suprema FROM web_huellas where cedula=%s', (cedulaUsuario,))
                                    huellas_local= cursorlocal.fetchall()
                                    HuellasPorBorrar=len(huellas_local)
                                    HuellasBorradas=0
                                    nroCaptahuellasSinHuella=0
                                    captahuella_actual=0
                                    for huella_local in huellas_local:
                                        id_suprema = huella_local[0]
                                        id_suprema_hex = (id_suprema).to_bytes(4, byteorder='big').hex()
                                        id_suprema_hex = id_suprema_hex[6:]+id_suprema_hex[4:6]+id_suprema_hex[2:4]+id_suprema_hex[0:2]
                                        for captahuella in captahuellas:
                                            if captahuella:
                                                captahuella_actual=captahuella_actual+1
                                                try:
                                                    requests.get(url=f'{captahuella}/quitar/{id_suprema_hex}', timeout=3)
                                                    nroCaptahuellasSinHuella=nroCaptahuellasSinHuella+1
                                                except:
                                                    print(f"fallo al conectar con la esp8266 con la ip:{captahuella}")
                                                    banderaUsuario=False
                                        if nroCaptahuellasSinHuella == captahuella_actual:
                                            cursorlocal.execute('DELETE FROM web_huellas WHERE id_suprema=%s', (id_suprema,))
                                            connlocal.commit()
                                            HuellasBorradas=HuellasBorradas+1
                                    if HuellasBorradas == HuellasPorBorrar:
                                        cursorlocal.execute('DELETE FROM web_usuarios WHERE cedula=%s', (cedulaUsuario,))
                                        cursorlocal.execute('DELETE FROM web_horariospermitidos WHERE cedula_id=%s', (cedulaUsuario,))
                                        connlocal.commit()
                                elif not usuarioLocal and usuarioServidor: 
                                    for consultajson in request_json_usuario:
                                        cedula=consultajson['cedula']
                                        nombre=consultajson['nombre']
                                        telegram_id=consultajson['telegram_id']
                                        internet=consultajson['telefonoInternet']
                                        wifi=consultajson['telefonoWifi']
                                        captahuella=consultajson['captahuella']
                                        rfid=consultajson['rfid']
                                        facial=consultajson['reconocimientoFacial']
                                    cursorlocal.execute('''INSERT INTO web_usuarios (cedula, nombre, telegram_id, internet, wifi, captahuella, rfid, facial)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (cedula, nombre, telegram_id, internet, wifi, captahuella, rfid, facial))
                                    connlocal.commit()
                                elif usuarioLocal and usuarioServidor:
                                    for consultajson in request_json_usuario:
                                        cedula=consultajson['cedula']
                                        telegram_id=consultajson['telegram_id']
                                        internet=consultajson['telefonoInternet']
                                        wifi=consultajson['telefonoWifi']
                                        captahuella=consultajson['captahuella']
                                        rfid=consultajson['rfid']
                                        facial=consultajson['reconocimientoFacial']
                                    cursorlocal.execute("UPDATE web_usuarios SET telegram_id=%s, internet=%s, wifi=%s, captahuella=%s, rfid=%s, facial=%s WHERE cedula=%s", (telegram_id,internet,wifi,captahuella,rfid,facial,cedula))
                                    connlocal.commit()
                            except requests.exceptions.ConnectionError:
                                print("fallo consultando api en usuarios")
                                banderaUsuario=False
                        except Exception as e:
                            print(f"{e} - fallo total usuarios")
                            banderaUsuario=False
                        if banderaUsuario:
                            requests.delete(url=f'{URL_API}eliminarcambioapi/{idCambio}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                    elif tablaCambiada == 'Horarios':
                        try:
                            try:
                                banderaHorario=True
                                request_json_horarios = requests.get(url=f'{URL_API}obtenerhorariosindividualapi/{CONTRATO}/{cedulaUsuario}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()
                                        
                                horariosServidor=[]
                                for consultajson in request_json_horarios:
                                    entradaObjetohora=time.fromisoformat(consultajson['entrada'])
                                    salidaObjetohora=time.fromisoformat(consultajson['salida'])
                                    TuplaHorarioIndividual=(entradaObjetohora,salidaObjetohora,consultajson['cedula'],consultajson['dia'],)
                                    horariosServidor.append(TuplaHorarioIndividual)
                                
                                cursorlocal.execute('SELECT * FROM web_horariospermitidos WHERE cedula_id=%s',(cedulaUsuario,))
                                horariosLocal= cursorlocal.fetchall()

                                for horario in horariosServidor:
                                    if not horario in horariosLocal:
                                        entrada=horario[0]
                                        salida=horario[1]
                                        cedula=horario[2]
                                        dia=horario[3]
                                        cursorlocal.execute('''INSERT INTO web_horariospermitidos (entrada, salida, cedula_id, dia)
                                        VALUES (%s, %s, %s, %s);''', (entrada, salida, cedula, dia))
                                        connlocal.commit()

                                for horariosLocaliterar in horariosLocal:
                                    if not horariosLocaliterar in horariosServidor:
                                        entrada=horariosLocaliterar[0]
                                        salida=horariosLocaliterar[1]
                                        cedula=horariosLocaliterar[2]
                                        dia=horariosLocaliterar[3]
                                        cursorlocal.execute('DELETE FROM web_horariospermitidos WHERE entrada=%s AND salida=%s AND cedula_id=%s AND dia=%s',(entrada, salida, cedula, dia))
                                        connlocal.commit()
                            except requests.exceptions.ConnectionError:
                                print("fallo consultando api en horarios")
                                banderaHorario=False
                        except Exception as e:
                            print(f"{e} - fallo total horarios")
                            banderaHorario=False
                        if banderaHorario:
                            requests.delete(url=f'{URL_API}eliminarcambioapi/{idCambio}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                    elif tablaCambiada == 'Huellas':
                        try:
                            try:
                                banderaHuella = True
                                cursorlocal.execute('SELECT template, id_suprema, cedula FROM web_huellas where cedula=%s', (cedulaUsuario,))
                                huellas_local= cursorlocal.fetchall()

                                request_json = requests.get(url=f'{URL_API}obtenerhuellasapi/{cedulaUsuario}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                                huellasServidor=[]
                                for consultajson in request_json:
                                    tuplaHuellaIndividual=(consultajson['template'], consultajson['id_suprema'], consultajson['cedula'],)
                                    huellasServidor.append(tuplaHuellaIndividual)

                                for huella in huellas_local:
                                    if not huella in huellasServidor:
                                        nroCaptahuellasSinHuella=0
                                        captahuella_actual=0
                                        template=huella[0]
                                        id_suprema = huella[1]
                                        id_suprema_hex = (id_suprema).to_bytes(4, byteorder='big').hex()
                                        id_suprema_hex = id_suprema_hex[6:]+id_suprema_hex[4:6]+id_suprema_hex[2:4]+id_suprema_hex[0:2]
                                        for captahuella in captahuellas:
                                            if captahuella:
                                                captahuella_actual=captahuella_actual+1
                                                try:
                                                    requests.get(url=f'{captahuella}/quitar/{id_suprema_hex}', timeout=3)
                                                    nroCaptahuellasSinHuella=nroCaptahuellasSinHuella+1
                                                except:
                                                    print(f"fallo al conectar con la esp8266 con la ip:{captahuella}")  
                                        if nroCaptahuellasSinHuella == captahuella_actual:
                                            cursorlocal.execute('DELETE FROM web_huellas WHERE template=%s', (template,))
                                            connlocal.commit()
                                        else:
                                            banderaHuella = False  

                                for huella in huellasServidor:
                                    if not huella in huellas_local:
                                        id_suprema=huella[1]
                                        cedula=huella[2]
                                        template=huella[0]
                                        nroCaptahuellasConHuella=0
                                        captahuella_actual=0
                                        IdSupremaContador=0 #esto lo uso para ver si hay id de suprema disponibles
                                        if not id_suprema:
                                            cursorlocal.execute('SELECT id_suprema FROM web_huellas ORDER BY id_suprema ASC')
                                            ids_suprema_local= cursorlocal.fetchall()
                                            nro_ids_suprema_local=len(ids_suprema_local)
                                            if not ids_suprema_local:
                                                id_suprema = 1
                                                if not cedula in listaempleadosseguricel:
                                                    requests.put(url=f'{URL_API}agregaridsupremaportemplateapi/{template}/{id_suprema}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                                            else:
                                                for id_suprema_local in ids_suprema_local:
                                                    IdSupremaContador=IdSupremaContador+1
                                                    if not id_suprema_local[0] == IdSupremaContador:
                                                        id_suprema=IdSupremaContador
                                                        if not cedula in listaempleadosseguricel:
                                                            requests.put(url=f'{URL_API}agregaridsupremaportemplateapi/{template}/{id_suprema}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                                                        break
                                                if nro_ids_suprema_local == IdSupremaContador:
                                                    id_suprema=IdSupremaContador+1
                                                    if not cedula in listaempleadosseguricel:
                                                        requests.put(url=f'{URL_API}agregaridsupremaportemplateapi/{template}/{id_suprema}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                                        id_suprema_hex = (id_suprema).to_bytes(4, byteorder='big').hex()
                                        id_suprema_hex = id_suprema_hex[6:]+id_suprema_hex[4:6]+id_suprema_hex[2:4]+id_suprema_hex[0:2]
                                        for captahuella in captahuellas:
                                            if captahuella:
                                                captahuella_actual=captahuella_actual+1
                                                try:
                                                    requests.get(url=f'{captahuella}/anadir/{id_suprema_hex}/{template}0A', timeout=3)
                                                    nroCaptahuellasConHuella=nroCaptahuellasConHuella+1
                                                except:
                                                    print(f"fallo al conectar con la esp8266 con la ip:{captahuella}")
                                        if nroCaptahuellasConHuella == captahuella_actual and captahuella_actual != 0:
                                            cursorlocal.execute('''INSERT INTO web_huellas (id_suprema, cedula, template)
                                            VALUES (%s, %s, %s)''', (id_suprema, cedula, template))
                                            connlocal.commit()
                                        elif captahuella_actual != nroCaptahuellasConHuella and nroCaptahuellasConHuella != 0:
                                            banderaHuella = False  
                                            for captahuella in captahuellas:
                                                try:
                                                    requests.get(url=f'{captahuella}/quitar/{id_suprema_hex}', timeout=3)
                                                except:
                                                    print(f"fallo al conectar con la esp8266 con la ip:{captahuella}")
                            except requests.exceptions.ConnectionError:
                                print("fallo consultando api en huellas")
                                banderaHuella=False
                        except Exception as e:
                            print(f"{e} - fallo total huellas")
                            banderaHuella=False
                        if banderaHuella:
                            requests.delete(url=f'{URL_API}eliminarcambioapi/{idCambio}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                    elif tablaCambiada == 'Tags':
                        try:
                            try:
                                banderaTag=True
                                cursorlocal.execute('SELECT epc, cedula FROM web_tagsrfid WHERE cedula=%s', (cedulaUsuario,))
                                tags_local= cursorlocal.fetchall()
                                
                                request_json = requests.get(url=f'{URL_API}obtenertagsrfidindividualapi/{CONTRATO}/{cedulaUsuario}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()
                                tagsServidor=[]
                                for consultajson in request_json:
                                    tuplaTagIndividual=(consultajson['epc'],consultajson['cedula'],)
                                    tagsServidor.append(tuplaTagIndividual)

                                nro_tags_local = len(tags_local)
                                nro_tags_servidor = len(tagsServidor)

                                for tagServidor in tagsServidor:
                                    if not tagServidor in tags_local:
                                        epc=tagServidor[0]
                                        cedula=tagServidor[1]
                                        cursorlocal.execute('''INSERT INTO web_tagsrfid (epc, cedula)
                                        VALUES (%s, %s);''', (epc, cedula))
                                        connlocal.commit()

                                for taglocaliterar in tags_local:
                                    if not taglocaliterar in tagsServidor:
                                        epc=taglocaliterar[0]
                                        cedula=taglocaliterar[1]
                                        cursorlocal.execute('DELETE FROM web_tagsrfid WHERE epc=%s AND cedula=%s',(epc, cedula))
                                        connlocal.commit()
                            except requests.exceptions.ConnectionError:
                                print("fallo consultando api en tags")
                                banderaTag=False
                        except Exception as e:
                            print(f"{e} - fallo total tags")
                            banderaTag=False
                        if banderaTag:
                            requests.delete(url=f'{URL_API}eliminarcambioapi/{idCambio}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                    elif tablaCambiada == 'Fotos':
                        try:
                            try:
                                banderaFoto=True
                                cursorlocal.execute('SELECT * FROM web_fotos where cedula_id=%s', (cedulaUsuario,))
                                fotos_local= cursorlocal.fetchall()
                                request_json = requests.get(url=f'{URL_API}obtenerfotosapi/{cedulaUsuario}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()
                                listaFotosServidor=[]
                                for consultajson in request_json:
                                    rutaFotoSinProcesar = consultajson['foto'][8:].split('/')
                                    rutaFotoProcesada = f"{rutaFotoSinProcesar[-3]}/{rutaFotoSinProcesar[-2]}/{rutaFotoSinProcesar[-1]}"
                                    tuplaFotoIndividual=(int(consultajson['id']),rutaFotoProcesada,int(consultajson['estado']),consultajson['cedula'],)
                                    listaFotosServidor.append(tuplaFotoIndividual)
                                      
                                #eliminar fotos de la base de datos local que no esten en la base de datos de heroku
                                for fotolocal in fotos_local:
                                    id=fotolocal[0]
                                    foto=fotolocal[1]
                                    # try:
                                    #     listaFotosServidor.index(fotolocal)
                                    # except ValueError:
                                    if not fotolocal in listaFotosServidor
                                        try:
                                            os.remove(f'{foto}.jpg')
                                            cursorlocal.execute('DELETE FROM web_fotos where id=%s', (id,))
                                            connlocal.commit()
                                        except Exception as e:
                                            print(f"{e} - fallo borrando foto: {foto}")
                                            banderaFoto=False

                                #agregar fotos que no estan en la base de datos local pero que si estan en la de heroku
                                for fotoServidor in listaFotosServidor:
                                    # try:
                                    #     fotos_local.index(fotoServidor)
                                    # except ValueError:
                                    if not fotoServidor in fotos_local
                                        id=fotoServidor[0]
                                        foto=fotoServidor[1]
                                        estado=fotoServidor[2]
                                        cedula=fotoServidor[3]
                                        try:
                                            urlFoto = cloudinary.utils.cloudinary_url(foto)
                                            urlFoto=urlFoto[0]
                                            #imagenurl = urllib.request.urlopen (url) #abrimos el URL
                                            imagenurl = requests.get(url=urlFoto, timeout=3)
                                            imagenarray = np.array(bytearray(imagenurl.read()),dtype=np.uint8)
                                            fotovisible = cv2.imdecode (imagenarray,-1)
                                            cv2.imwrite(f"{foto}.jpg",fotovisible)
                                            cursorlocal.execute('''INSERT INTO web_fotos (id, foto, estado, cedula_id)
                                            VALUES (%s, %s, %s, %s);''', (id, foto, estado, cedula))
                                            connlocal.commit()
                                        except Exception as e:
                                            print(f"{e} - fallo trayendo foto del usuario: {cedula}")
                                            banderaFoto=False
                            except requests.exceptions.ConnectionError:
                                print("fallo consultando api de fotos")
                                banderaFoto=False
                        except Exception as e:
                            print(f"{e} - fallo total fotos")
                            banderaFoto=False
                        if banderaFoto:
                            requests.delete(url=f'{URL_API}eliminarcambioapi/{idCambio}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                    else:
                        requests.delete(url=f'{URL_API}eliminarcambioapi/{idCambio}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                t1_cambios=tm.perf_counter()
            
            if total_log > TIEMPO_LOG:
                try:
                    tz = pytz.timezone('America/Caracas')
                    caracas_now = datetime.now(tz)
                    fechahoy=str(caracas_now)[:10]

                    if fechahoy != fechaayer:
                        fechaayer=fechahoy
                        tupla_fecha_hoy=(fechahoy,)
                        cursorlocal.execute('SELECT fecha FROM dias_acumulados')
                        dias_acumulados= cursorlocal.fetchall()
                        nro_dias_acumulados=len(dias_acumulados)

                        if nro_dias_acumulados >= maximo_dias_acumular:
                            cursorlocal.execute('DELETE FROM web_interacciones *')
                            cursorlocal.execute('DELETE FROM dias_acumulados *')
                            connlocal.commit()
                            
                        if not tupla_fecha_hoy in dias_acumulados:
                            cursorlocal.execute('''INSERT INTO dias_acumulados (fecha)
                            VALUES (%s);''', (fechahoy,))
                            connlocal.commit()

                    try:
                        cursorlocal.execute('SELECT * FROM web_interacciones where contrato=%s and fecha=%s', (CONTRATO,fechahoy))
                        interacciones_local= cursorlocal.fetchall()
                    
                        request_json = requests.get(url=f'{URL_API}obtenerinteraccionesapi/{CONTRATO}/{fechahoy}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                        listaLogsServidor=[]
                        for consultajson in request_json:
                            objetofecha= date.fromisoformat(consultajson['fecha'])
                            objetohora=time.fromisoformat(consultajson['hora'])
                            tuplaLogIndividual=(consultajson['nombre'],objetofecha,objetohora,consultajson['razon'],consultajson['contrato'],consultajson['cedula'])
                            listaLogsServidor.append(tuplaLogIndividual)

                        nro_int_local = len(interacciones_local)
                        nro_int_servidor = len(listaLogsServidor)

                        if nro_int_local != nro_int_servidor:

                            for interaccion in interacciones_local:
                                if not interaccion in listaLogsServidor:
                                    nombre=interaccion[0]
                                    fecha=interaccion[1]
                                    hora=interaccion[2]
                                    razon=interaccion[3]
                                    cedula=interaccion[5]
                                    anadirLogJson = {
                                        "nombre": nombre,
                                        "fecha": fecha.isoformat(),
                                        "hora": hora.isoformat(),
                                        "razon": razon,
                                        "contrato": CONTRATO,
                                        "cedula": cedula
                                    }
                                    requests.post(url=f'{URL_API}registrarinteraccionesapi/', 
                                    json=anadirLogJson, auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                            
                            nombre=None
                            fecha=None
                            hora=None
                            razon=None
                            cedula=None
                    except requests.exceptions.ConnectionError:
                        print("fallo consultando api de logs")
                except Exception as e:
                    print(f"{e} - fallo total al subir Log")
                BorrarPeticionesListas=True
                t1_log=tm.perf_counter()

            if BorrarPeticionesListas:
                try:
                    cursorlocal.execute('SELECT id, estado, peticionInternet, feedback FROM solicitud_aperturas')
                    aperturas_local= cursorlocal.fetchall()
                    if aperturas_local:
                        for aperturalocal in aperturas_local:
                            if aperturalocal[1] == 1:
                                idapertura=aperturalocal[0]
                                peticionDesdeInternet=aperturalocal[2]
                                feedbackPeticion=aperturalocal[3]
                                if peticionDesdeInternet and feedbackPeticion:
                                    try:
                                        request_json = requests.delete(url=f'{URL_API}eliminarsolicitudesaperturaapi/{idapertura}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                                        if request_json.status_code == 200 or request_json.status_code == 500:
                                            cursorlocal.execute('DELETE FROM solicitud_aperturas WHERE id=%s', (idapertura,))
                                            connlocal.commit()
                                    except requests.exceptions.ConnectionError:
                                        print("fallo consultando api de peticiones de aperturas")
                                elif not peticionDesdeInternet:# and feedbackPeticion:
                                    cursorlocal.execute('DELETE FROM solicitud_aperturas WHERE id=%s', (idapertura,))
                                    connlocal.commit()
                    BorrarPeticionesListas=False
                    cambiarEstadoFotos=True
                except Exception as e:
                    print(f"{e} - fallo total eliminando peticiones de aperturas")
            
            if cambiarEstadoFotos:
                try:
                    #identificar fotos que no fueron aprobadas
                    #debido a que no funcionan para el reconocimiento
                    cursorlocal.execute('SELECT * FROM web_fotos')
                    fotosLocal= cursorlocal.fetchall()
                    for fotolocal in fotosLocal:
                        estado=fotolocal[2]
                        id=fotolocal[0]
                        foto=fotolocal[1]
                        if estado==2:
                            requests.put(url=f'{URL_API}cambiarestadofotosapi/{id}/2', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                        if estado==1:
                            requests.put(url=f'{URL_API}cambiarestadofotosapi/{id}/1', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                    cambiarEstadoFotos=False
                except Exception as e:
                    print(f"{e} - fallo total cambiando estados de fotos")           

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
            
