import psycopg2
import os
import time as tm
import pytz
from datetime import datetime, date, time
import time
import cloudinary
import urllib.request
import requests
import numpy as np
import cv2
import pytz
from datetime import datetime

CONTRATO=os.environ.get("CONTRATO")
URL_API=os.environ.get("URL_API")
maximo_dias_acumular=int(os.environ.get("DIAS_ACUMULAR"))
connlocal = None
connheroku = None
cursorheroku=None
cursorlocal=None
listaUsuariosServidor=[]
listaUsuariosLocal=[]
listaHuellasServidor=[]
listahuellaslocal=[]
listaempleadosseguricel=[]
total=0
etapa=0
fechahoy=None
fechaayer=None
diasacumulados=[]
nroCaptahuellasConHuella=0
nroCaptahuellasSinHuella=0
captahuella_actual=0
DIRECTORIO=os.environ.get("DIRECTORIO", "media/personas")

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
        
        while True:

            if etapa==0:
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
                            try:
                                listaLogsServidor.index(interaccion)
                            except ValueError:
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
                    print("fallo en la etapa 0")
                etapa=1

            if etapa==1:
                try:
                    cursorlocal.execute('SELECT cedula FROM web_usuarios')
                    usuarios_local= cursorlocal.fetchall()

                    request_json = requests.get(url=f'{URL_API}obtenerusuariosapi/{CONTRATO}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                    usuariosServidor=[]
                    empleados_seguricel=[]
                    for consultajson in request_json:
                        tuplaUsuarioIndividual=(consultajson['cedula'],consultajson['telegram_id'],)
                        usuariosServidor.append(tuplaUsuarioIndividual)
                        if consultajson['contrato'] == 'SEGURICEL':
                            empleados_seguricel.append(tuplaUsuarioIndividual)

                    nro_usu_local = len(usuarios_local)
                    nro_usu_servidor = len(usuariosServidor)
                
                    #cuando se va a eliminar un usuario
                    if nro_usu_local > nro_usu_servidor:

                        for usuario in usuariosServidor:
                            cedula=usuario[0]
                            try:
                                listaUsuariosServidor.index(cedula)
                            except ValueError:
                                listaUsuariosServidor.append(cedula)
                        
                        for usuario in usuarios_local:
                            cedula=usuario[0]
                            try:
                                listaUsuariosLocal.index(cedula)
                            except ValueError:
                                listaUsuariosLocal.append(cedula)

                        for usuario in listaUsuariosLocal:
                            try:
                                listaUsuariosServidor.index(usuario)
                            except ValueError:
                                cursorlocal.execute('SELECT id_suprema FROM web_huellas where cedula=%s', (usuario,))
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
                                                peticion = urllib.request.urlopen(url=f'{captahuella}/quitar/{id_suprema_hex}', timeout=3)
                                                if peticion.getcode() == 200:
                                                    nroCaptahuellasSinHuella=nroCaptahuellasSinHuella+1
                                            except:
                                                print(f"fallo al conectar con la esp8266 con la ip:{captahuella}")
                                    if nroCaptahuellasSinHuella == captahuella_actual:
                                        cursorlocal.execute('DELETE FROM web_huellas WHERE id_suprema=%s', (id_suprema,))
                                        connlocal.commit()
                                        HuellasBorradas=HuellasBorradas+1
                                if HuellasBorradas == HuellasPorBorrar:
                                    cursorlocal.execute('DELETE FROM web_usuarios WHERE cedula=%s', (usuario,))
                                    cursorlocal.execute('DELETE FROM web_fotos WHERE cedula_id=%s', (usuario,))
                                    cursorlocal.execute('DELETE FROM web_horariospermitidos WHERE cedula_id=%s', (usuario,))
                                    connlocal.commit()
                        #listaUsuariosServidor=[]
                        listaUsuariosLocal=[]

                    # cuando se va a agregar usuarios
                    if nro_usu_servidor > nro_usu_local:

                        for usuario in usuariosServidor:
                            cedula=usuario[0]
                            try:
                                listaUsuariosServidor.index(cedula)
                            except ValueError:
                                listaUsuariosServidor.append(cedula)
                        
                        for usuario in usuarios_local:
                            cedula=usuario[0]
                            try:
                                listaUsuariosLocal.index(cedula)
                            except ValueError:
                                listaUsuariosLocal.append(cedula)

                        for usuario in listaUsuariosServidor:
                            try:
                                listaUsuariosLocal.index(usuario)
                            except ValueError:
                                
                                request_json = requests.get(url=f'{URL_API}usuarioindividualapi/{CONTRATO}/{usuario}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                                usuariosServidor=[]
                                for consultajson in request_json:
                                    tuplaUsuarioIndividual=(consultajson['cedula'],consultajson['nombre'],)
                                    usuariosServidor.append(tuplaUsuarioIndividual)
                                cedula=usuariosServidor[0][0]
                                nombre=usuariosServidor[0][1]
                                cursorlocal.execute('''INSERT INTO web_usuarios (cedula, nombre)
                                VALUES (%s, %s)''', (cedula, nombre))
                                connlocal.commit()
                        #listaUsuariosServidor=[]
                        listaUsuariosLocal=[]
                except requests.exceptions.ConnectionError:
                    print("fallo en la etapa 1")
                etapa=2

            if etapa==2:

                cursorlocal.execute('SELECT cedula, telegram_id FROM web_usuarios')
                usuarios_local= cursorlocal.fetchall()

                # request_json = requests.get(url=f'{URL_API}obtenerusuariosapi/{CONTRATO}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                # usuariosServidor=[]
                # for consultajson in request_json:
                #     try:
                #         listaUsuariosServidor.index(consultajson['cedula'])
                #     except ValueError:
                #         listaUsuariosServidor.append(consultajson['cedula'])

                for usuario in usuarios_local:
                    cedula=usuario[0]
                    try:
                        listausuarioslocal.index(cedula)
                    except ValueError:
                        listausuarioslocal.append(cedula)
                
                if len(listausuarioslocal) == len(listaUsuariosServidor):
                

                    for usuario in listausuarioslocal:
                        cursorlocal.execute('SELECT * FROM web_fotos where cedula_id=%s', (usuario,))
                        fotos_local= cursorlocal.fetchall()
                        try:
                            request_json = requests.get(url=f'{URL_API}obtenerfotosapi/{usuario}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                            listaFotosServidor=[]
                            for consultajson in request_json:
                                tuplaFotoIndividual=(int(consultajson['id']),consultajson['foto'],int(consultajson['estado']),consultajson['cedula'],)
                                listaFotosServidor.append(tuplaFotoIndividual)

                            #identificar fotos que no fueron aprobadas
                            #debido a que no funcionan para el reconocimiento

                            for fotolocal in fotos_local:
                                estado=fotolocal[2]
                                id=fotolocal[0]
                                foto=fotolocal[1]
                                if estado==2:
                                    requests.put(url=f'{URL_API}cambiarestadofotosapi/{id}/2', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                                if estado==1:
                                    requests.put(url=f'{URL_API}cambiarestadofotosapi/{id}/1', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                                    
                            #eliminar fotos de la base de datos local que no esten en la base de datos de heroku
                            if len(fotos_local) > len(listaFotosServidor):
                                for fotolocal in fotos_local:
                                    id=fotolocal[0]
                                    foto=fotolocal[1]
                                    try:
                                        listaFotosServidor.index(fotolocal)
                                    except ValueError:
                                        cursorlocal.execute('DELETE FROM web_fotos where id=%s', (id,))
                                        connlocal.commit()
                                        os.remove(f'{foto}.jpg')


                            #agregar fotos que no estan en la base de datos local pero que si estan en la de heroku
                            if len(fotos_local) < len(listaFotosServidor):
                                for fotoServidor in listaFotosServidor:
                                    try:
                                        fotos_local.index(fotoServidor)
                                    except ValueError:
                                        id=fotoServidor[0]
                                        foto=fotoServidor[1]
                                        estado=fotoServidor[2]
                                        cedula=fotoServidor[3]
                                        cursorlocal.execute('''INSERT INTO web_fotos (id, foto, estado, cedula_id)
                                        VALUES (%s, %s, %s, %s);''', (id, foto, estado, cedula))
                                        connlocal.commit()
                                        url = cloudinary.utils.cloudinary_url(foto)
                                        url=url[0]
                                        imagenurl = urllib.request.urlopen (url) #abrimos el URL
                                        imagenarray = np.array(bytearray(imagenurl.read()),dtype=np.uint8)
                                        fotovisible = cv2.imdecode (imagenarray,-1)
                                        cv2.imwrite(f"{foto}.jpg",fotovisible)
                            
                        except requests.exceptions.ConnectionError:
                            print("fallo en la etapa 2")
                etapa=3

            if etapa==3:
                try:
                    # cursorlocal.execute('SELECT * FROM web_usuarios')
                    # usuarios_local= cursorlocal.fetchall()

                    # request_json = requests.get(url=f'{URL_API}obtenerusuariosapi/{CONTRATO}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                    # usuariosServidor=[]
                    # for consultajson in request_json:
                    #     tuplaUsuarioIndividual=(consultajson['cedula'],)
                    #     usuariosServidor.append(tuplaUsuarioIndividual)

                    if len(usuariosServidor) == len(usuarios_local):
                        # for usuario in usuarios_local:
                        #     cedula=usuario[0]
                        #     try:
                        #         listaUsuariosLocal.index(cedula)
                        #     except ValueError:
                        #         listaUsuariosLocal.append(cedula)
                        
                        for usuario in listaUsuariosLocal:

                            request_json = requests.get(url=f'{URL_API}obtenerhorariosapi/{CONTRATO}/{usuario}', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                            horariosServidor=[]
                            for consultajson in request_json:
                                entradaObjetohora=time.fromisoformat(consultajson['entrada'])
                                salidaObjetohora=time.fromisoformat(consultajson['salida'])
                                TuplaHorarioIndividual=(entradaObjetohora,salidaObjetohora,consultajson['cedula'],consultajson['dia'],)
                                horariosServidor.append(TuplaHorarioIndividual)
                            
                            cursorlocal.execute('SELECT * FROM web_horariospermitidos WHERE cedula_id=%s',(usuario,))
                            horariosLocal= cursorlocal.fetchall()

                            if len(horariosServidor) > 0 and len(horariosServidor) > len(horariosLocal):
                                for horario in horariosServidor:
                                    try:
                                        horariosLocal.index(horario)
                                    except ValueError:
                                        entrada=horario[0]
                                        salida=horario[1]
                                        cedula=horario[2]
                                        dia=horario[3]
                                        cursorlocal.execute('''INSERT INTO web_horariospermitidos (entrada, salida, cedula_id, dia)
                                        VALUES (%s, %s, %s, %s);''', (entrada, salida, cedula, dia))
                                        connlocal.commit()

                            if len(horariosLocal) > len(horariosServidor):
                                for horariosLocaliterar in horariosLocal:
                                    try:
                                        horariosServidor.index(horariosLocaliterar)
                                    except ValueError:
                                        entrada=horariosLocaliterar[0]
                                        salida=horariosLocaliterar[1]
                                        cedula=horariosLocaliterar[2]
                                        dia=horariosLocaliterar[3]
                                        cursorlocal.execute('DELETE FROM web_horariospermitidos WHERE entrada=%s AND salida=%s AND cedula_id=%s AND dia=%s',(entrada, salida, cedula, dia))
                                        connlocal.commit()
                        horariosLocal=[]
                        horariosServidor=[]
                        #listaUsuariosServidor=[]
                        #listaUsuariosLocal=[]
                except requests.exceptions.ConnectionError:
                    print("fallo en la etapa 3")
                etapa=4

            if etapa==4:
                try:
                    # cursorlocal.execute('SELECT cedula, telegram_id FROM web_usuarios')
                    # usuarios_local= cursorlocal.fetchall()

                    # request_json = requests.get(url=f'{URL_API}obtenerusuariosapi/{CONTRATO}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                    # usuariosServidor=[]
                    # for consultajson in request_json:
                    #     tuplaUsuarioIndividual=(consultajson['cedula'],consultajson['telegram_id'],)
                    #     usuariosServidor.append(tuplaUsuarioIndividual)
                    
                    nro_usu_local = len(usuarios_local)
                    nro_usu_servidor = len(usuariosServidor)
                
                    if nro_usu_servidor == nro_usu_local:
                        for usuario in usuariosServidor:
                            try:
                                usuarios_local.index(usuario)
                            except ValueError:
                                cedula=usuario[0]
                                telegram_id=usuario[1]
                                cursorlocal.execute("UPDATE web_usuarios SET telegram_id=%s WHERE cedula=%s", (telegram_id,cedula))
                                connlocal.commit()
                except requests.exceptions.ConnectionError:
                    print("fallo en la etapa 4")
                etapa=5

            if etapa==5:
                try:
                    cursorlocal.execute('SELECT dispositivo, descripcion, estado, acceso FROM web_dispositivos')
                    dispositivos_local= cursorlocal.fetchall()

                    request_json = requests.get(url=f'{URL_API}obtenerdispositivosapi/{CONTRATO}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                    dispositivosServidor=[]
                    for consultajson in request_json:
                        tuplaDispositivoIndividual=(consultajson['dispositivo'],consultajson['descripcion'], consultajson['estado'], consultajson['acceso'],)
                        dispositivosServidor.append(tuplaDispositivoIndividual)

                    if len(dispositivosServidor) != len(dispositivos_local):
                        request_json = requests.delete(url=f'{URL_API}eliminartodosdispositivosapi/{CONTRATO}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                        if request_json.status_code == 200:

                            request_json = requests.get(url=f'{URL_API}obtenerdispositivosapi/{CONTRATO}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                            dispositivosServidor=[]
                            for consultajson in request_json:
                                tuplaDispositivoIndividual=(consultajson['dispositivo'],consultajson['descripcion'], consultajson['estado'], consultajson['acceso'],)
                                dispositivosServidor.append(tuplaDispositivoIndividual)

                            for dispositivolocal in dispositivos_local:
                                try:
                                    dispositivosServidor.index(dispositivolocal)
                                except ValueError:
                                    tz = pytz.timezone('America/Caracas')
                                    caracas_now = datetime.now(tz)
                                    fecha=str(caracas_now)[:10]
                                    hora=str(caracas_now)[11:19]
                                    dispositivo=dispositivolocal[0]
                                    descripcion=dispositivolocal[1]
                                    estado=dispositivolocal[2]
                                    acceso=dispositivolocal[3]
                                    agregarDispositivoJson = {
                                        "dispositivo": dispositivo,
                                        "descripcion": descripcion,
                                        "estado": estado,
                                        "contrato": CONTRATO,
                                        "acceso": acceso,
                                        "fecha": fecha,
                                        "hora": hora
                                    }
                                    requests.post(url=f'{URL_API}registrardispositivosapi/', 
                                    json=agregarDispositivoJson, auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                    else:
                        for dispositivolocal in dispositivos_local:
                            try:
                                dispositivosServidor.index(dispositivolocal)
                            except ValueError:
                                tz = pytz.timezone('America/Caracas')
                                caracas_now = datetime.now(tz)
                                fecha=str(caracas_now)[:10]
                                hora=str(caracas_now)[11:19]
                                dispositivo=dispositivolocal[0]
                                descripcion=dispositivolocal[1]
                                estado=dispositivolocal[2]
                                requests.put(url=f'{URL_API}actualizardispositivosapi/{CONTRATO}/{dispositivo[7:]}/{estado}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                except requests.exceptions.ConnectionError:
                    print("fallo en la etapa 5")   
                etapa=6
            
            if etapa==6:
                try:
                    # cursorlocal.execute('SELECT * FROM web_usuarios')
                    # usuarios_local= cursorlocal.fetchall()

                    # request_json = requests.get(url=f'{URL_API}obtenerusuariosapi/{CONTRATO}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                    # usuariosServidor=[]
                    # empleados_seguricel=[]
                    # for consultajson in request_json:
                    #     tuplaUsuarioIndividual=(consultajson['cedula'],)
                    #     if consultajson['contrato'] == 'SEGURICEL':
                    #         empleados_seguricel.append(tuplaUsuarioIndividual)
                    #     usuariosServidor.append(tuplaUsuarioIndividual)
                    
                    # for usuario in usuarios_local:
                    #     cedula=usuario[0]
                    #     try:
                    #         listaUsuariosLocal.index(cedula)
                    #     except ValueError:
                    #         listaUsuariosLocal.append(cedula)

                    # for usuario in usuariosServidor:
                    #     cedula=usuario[0]
                    #     try:
                    #         listaUsuariosServidor.index(cedula)
                    #     except ValueError:
                    #         listaUsuariosServidor.append(cedula)
                    
                    for empleado_seguricel in empleados_seguricel:
                        cedula=empleado_seguricel[0]
                        try:
                            listaempleadosseguricel.index(cedula)
                        except ValueError:
                            listaempleadosseguricel.append(cedula)
                    
                    if len(usuarios_local) == len(usuariosServidor):

                        for usuario_local in listaUsuariosLocal:
                            cursorlocal.execute('SELECT template, id_suprema FROM web_huellas where cedula=%s', (usuario_local,))
                            huellas_local= cursorlocal.fetchall()

                            request_json = requests.get(url=f'{URL_API}obtenerhuellasapi/{usuario_local}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                            huellasServidor=[]
                            for consultajson in request_json:
                                tuplaHuellaIndividual=(consultajson['template'],consultajson['id_suprema'],)
                                huellasServidor.append(tuplaHuellaIndividual)

                            nro_huellas_local = len(huellas_local)
                            nro_huellas_servidor = len(huellasServidor)
                            #cuando se van a eliminar huellas
                            if nro_huellas_local > nro_huellas_servidor:

                                for usuario in huellasServidor:
                                    template=usuario[0]
                                    try:
                                        listaHuellasServidor.index(template)
                                    except ValueError:
                                        listaHuellasServidor.append(template)
                                
                                for usuario in huellas_local:
                                    template=usuario[0]
                                    try:
                                        listahuellaslocal.index(template)
                                    except ValueError:
                                        listahuellaslocal.append(template)

                                for templateEnLista in listahuellaslocal:
                                    try:
                                        listaHuellasServidor.index(templateEnLista)
                                    except ValueError:
                                        nroCaptahuellasSinHuella=0
                                        captahuella_actual=0
                                        cursorlocal.execute('SELECT id_suprema FROM web_huellas where template=%s', (templateEnLista,))
                                        huella_local= cursorlocal.fetchall()
                                        id_suprema = huella_local[0][0]
                                        id_suprema_hex = (id_suprema).to_bytes(4, byteorder='big').hex()
                                        id_suprema_hex = id_suprema_hex[6:]+id_suprema_hex[4:6]+id_suprema_hex[2:4]+id_suprema_hex[0:2]
                                        for captahuella in captahuellas:
                                            if captahuella:
                                                captahuella_actual=captahuella_actual+1
                                                try:
                                                    peticion = urllib.request.urlopen(url=f'{captahuella}/quitar/{id_suprema_hex}', timeout=3)
                                                    if peticion.getcode() == 200:
                                                        nroCaptahuellasSinHuella=nroCaptahuellasSinHuella+1
                                                except:
                                                    print(f"fallo al conectar con la esp8266 con la ip:{captahuella}")
                                        if nroCaptahuellasSinHuella == captahuella_actual:
                                            cursorlocal.execute('DELETE FROM web_huellas WHERE template=%s', (templateEnLista,))
                                            connlocal.commit()
                                listaHuellasServidor=[]
                                listahuellaslocal=[]

                            # cuando se van a agregar huellas
                            if nro_huellas_servidor > nro_huellas_local:

                                for usuario in huellasServidor:
                                    template=usuario[0]
                                    try:
                                        listaHuellasServidor.index(template)
                                    except ValueError:
                                        listaHuellasServidor.append(template)
                                
                                for usuario in huellas_local:
                                    template=usuario[0]
                                    try:
                                        listahuellaslocal.index(template)
                                    except ValueError:
                                        listahuellaslocal.append(template)

                                for templateEnLista in listaHuellasServidor:
                                    try:
                                        listahuellaslocal.index(templateEnLista)
                                    except ValueError:
                                        request_json = requests.get(url=f'{URL_API}obtenerhuellasportemplateapi/{templateEnLista}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                                        # huellaServidor=[]
                                        for consultajson in request_json:
                                            # tuplaHuellaIndividual=(consultajson['id_suprema'],consultajson['cedula'],consultajson['template'],)
                                            # huellaServidor.append(tuplaHuellaIndividual)
                                            id_suprema=consultajson['id_suprema']
                                            cedula=consultajson['cedula']
                                            template=consultajson['template']
                                            dedo=consultajson['dedo']
                                            mano=consultajson['mano']
                                        # id_suprema=huellaServidor[0][0]
                                        # cedula=huellaServidor[0][1]
                                        # template=huellaServidor[0][2]
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
                                                    peticion = urllib.request.urlopen(url=f'{captahuella}/anadir/{id_suprema_hex}/{template}0A', timeout=3)
                                                    if peticion.getcode() == 200:
                                                        nroCaptahuellasConHuella=nroCaptahuellasConHuella+1
                                                except:
                                                    print(f"fallo al conectar con la esp8266 con la ip:{captahuella}")
                                        if nroCaptahuellasConHuella == captahuella_actual and captahuella_actual != 0:
                                            cursorlocal.execute('''INSERT INTO web_huellas (id_suprema, cedula, template)
                                            VALUES (%s, %s, %s)''', (id_suprema, cedula, template))
                                            connlocal.commit()
                                        elif captahuella_actual != nroCaptahuellasConHuella and nroCaptahuellasConHuella != 0:
                                            for captahuella in captahuellas:
                                                try:
                                                    peticion = urllib.request.urlopen(url=f'{captahuella}/quitar/{id_suprema_hex}', timeout=3)
                                                    if peticion.getcode() == 200:
                                                        pass
                                                except:
                                                    print(f"fallo al conectar con la esp8266 con la ip:{captahuella}")
                                listaHuellasServidor=[]
                                listahuellaslocal=[]
                    listaUsuariosServidor=[]
                    listaUsuariosLocal=[]
                    listaempleadosseguricel=[]
                except requests.exceptions.ConnectionError:
                    print("fallo en la etapa 6")
                etapa=7

            if etapa==7:
                try:
                    cursorlocal.execute('SELECT epc, cedula FROM web_tagsrfid')
                    tags_local= cursorlocal.fetchall()

                    request_json = requests.get(url=f'{URL_API}obtenertagsrfidapi/{CONTRATO}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                    tagsServidor=[]
                    for consultajson in request_json:
                        tuplaTagIndividual=(consultajson['epc'],consultajson['cedula'],)
                        tagsServidor.append(tuplaTagIndividual)

                    nro_tags_local = len(tags_local)
                    nro_tags_servidor = len(tagsServidor)

                    if nro_tags_servidor > nro_tags_local:
                        for tagServidor in tagsServidor:
                            try:
                                tags_local.index(tagServidor)
                            except ValueError:
                                epc=tagServidor[0]
                                cedula=tagServidor[1]
                                cursorlocal.execute('''INSERT INTO web_tagsrfid (epc, cedula)
                                VALUES (%s, %s);''', (epc, cedula))
                                connlocal.commit()

                    if nro_tags_local > nro_tags_servidor:
                        for taglocaliterar in tags_local:
                            try:
                                tagsServidor.index(taglocaliterar)
                            except ValueError:
                                epc=taglocaliterar[0]
                                cedula=taglocaliterar[1]
                                cursorlocal.execute('DELETE FROM web_tagsrfid WHERE epc=%s AND cedula=%s',(epc, cedula))
                                connlocal.commit()
                except requests.exceptions.ConnectionError:
                    print("fallo en la etapa 7")
                etapa=8

            if etapa==8:
                cursorlocal.execute('SELECT id, estado FROM solicitud_aperturas')
                aperturas_local= cursorlocal.fetchall()
                if aperturas_local:
                    for aperturalocal in aperturas_local:
                        if aperturalocal[1] == 1:
                            idapertura=aperturalocal[0]
                            try:
                                request_json = requests.delete(url=f'{URL_API}eliminarsolicitudesaperturaapi/{idapertura}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                                if request_json.status_code == 200 or request_json.status_code == 500:
                                    cursorlocal.execute('DELETE FROM solicitud_aperturas WHERE id=%s', (idapertura,))
                                    connlocal.commit()
                            except requests.exceptions.ConnectionError:
                                print("fallo en la etapa 8")
                etapa=0

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
