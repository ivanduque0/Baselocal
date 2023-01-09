import psycopg2
import os
import time as tm
import pytz
from datetime import datetime, date, time
import requests
CONTRATO=os.environ.get("CONTRATO")
URL_API=os.environ.get("URL_API")
connlocal = None
cursorlocal=None
listaempleadosseguricel=[]
consultarTodo=True
consultaUsuarios=False
consultaHorarios=False
consultaHuellas=False
consultaTags=False
consultaFotos=False
total=0

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

        if not consultaUsuarios and consultarTodo:
            try:
                try:
                    cursorlocal.execute('SELECT cedula, nombre, telegram_id, internet, wifi, captahuella, rfid, facial FROM web_usuarios')
                    usuarios_local= cursorlocal.fetchall()

                    request_json = requests.get(url=f'{URL_API}obtenerusuariosapi/{CONTRATO}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                    usuariosServidor=[]
                    empleados_seguricel=[]
                    for consultajson in request_json:
                        tuplaUsuarioIndividual=(consultajson['cedula'],consultajson['nombre'],consultajson['telegram_id'], consultajson['telefonoInternet'], consultajson['telefonoWifi'], consultajson['captahuella'], consultajson['rfid'], consultajson['reconocimientoFacial'],)
                        usuariosServidor.append(tuplaUsuarioIndividual)
                        if consultajson['contrato'] == 'SEGURICEL':
                            empleados_seguricel.append(tuplaUsuarioIndividual)

                    nro_usu_local = len(usuarios_local)
                    nro_usu_servidor = len(usuariosServidor)

                    print(f'usuarios en local: {nro_usu_local}')
                    print(f'usuarios en servidor: {nro_usu_servidor}')
                    
                    if nro_usu_local!=nro_usu_servidor:
                        #cuando se va a eliminar un usuario
                        if nro_usu_local > nro_usu_servidor:

                            contador=0
                            for usuario in usuarios_local:
                                contador=contador+1
                                print(contador)
                                print(usuario)
                                # try:
                                #     usuariosServidor.index(usuario)
                                # except ValueError:
                                if not usuario in usuariosServidor:
                                    cedula=usuario[0]
                                    cursorlocal.execute('SELECT id_suprema FROM web_huellas where cedula=%s', (cedula,))
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
                                                    peticion = requests.get(url=f'{captahuella}/quitar/{id_suprema_hex}', timeout=3)
                                                    if peticion.status_code == 200:
                                                        nroCaptahuellasSinHuella=nroCaptahuellasSinHuella+1
                                                except:
                                                    print(f"fallo al conectar con la esp8266 con la ip:{captahuella}")
                                        if nroCaptahuellasSinHuella == captahuella_actual:
                                            cursorlocal.execute('DELETE FROM web_huellas WHERE id_suprema=%s', (id_suprema,))
                                            connlocal.commit()
                                            HuellasBorradas=HuellasBorradas+1
                                    if HuellasBorradas == HuellasPorBorrar:
                                        cursorlocal.execute('DELETE FROM web_usuarios WHERE cedula=%s', (cedula,))
                                        cursorlocal.execute('DELETE FROM web_horariospermitidos WHERE cedula_id=%s', (cedula,))
                                        connlocal.commit()

                        # cuando se va a agregar usuarios
                        if nro_usu_servidor > nro_usu_local:

                            contador=0
                            for usuario in usuariosServidor:
                                contador=contador+1
                                print(contador)
                                print(usuario)
                                # try:
                                #     usuarios_local.index(usuario)
                                # except ValueError:
                                if not usuario in usuarios_local:
                                    cedula=usuario[0]
                                    nombre=usuario[1]
                                    telegram_id=usuario[2]
                                    internet=usuario[3]
                                    wifi=usuario[4]
                                    captahuella=usuario[5]
                                    rfid=usuario[6]
                                    facial=usuario[7]
                                    cursorlocal.execute('''INSERT INTO web_usuarios (cedula, nombre, telegram_id, internet, wifi, captahuella, rfid, facial)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (cedula, nombre, telegram_id, internet, wifi, captahuella, rfid, facial))
                                    connlocal.commit()
                            #listaUsuariosServidor=[]
                            #listaUsuariosLocal=[]
                        cursorlocal.execute('SELECT cedula, nombre, telegram_id, internet, wifi, captahuella, rfid, facial FROM web_usuarios')
                        usuarios_local= cursorlocal.fetchall()
                        nro_usu_local = len(usuarios_local)
                        if nro_usu_local == nro_usu_servidor:
                            consultaUsuarios=True
                    else:
                        consultaUsuarios=True
                        print(f'consultaUsuarios: {consultaUsuarios}')
                except requests.exceptions.ConnectionError:
                    print("fallo consultando api en la etapa de usuarios")
            except Exception as e:
                print(f"{e} - fallo total etapa de usuarios")

        if consultaUsuarios and consultarTodo:
            try:
                try:
                    cursorlocal.execute('SELECT cedula, telegram_id, internet, wifi, captahuella, rfid, facial FROM web_usuarios')
                    usuarios_local= cursorlocal.fetchall()

                    request_json = requests.get(url=f'{URL_API}obtenerhorariosapi/{CONTRATO}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()
                    
                    horariosServidor=[]
                    for consultajson in request_json:
                        entradaObjetohora=time.fromisoformat(consultajson['entrada'])
                        salidaObjetohora=time.fromisoformat(consultajson['salida'])
                        TuplaHorarioIndividual=(entradaObjetohora,salidaObjetohora,consultajson['cedula'],consultajson['dia'],)
                        horariosServidor.append(TuplaHorarioIndividual)
                    
                    cursorlocal.execute('SELECT * FROM web_horariospermitidos')
                    horariosLocal= cursorlocal.fetchall()

                    print(f'horarios en local: {len(horariosLocal)}')
                    print(f'horarios en servidor: {len(horariosServidor)}')

                    contador=0
                    for horario in horariosServidor:
                        contador=contador+1
                        print(contador)
                        #print(horario)
                        # try:
                        #     horariosLocal.index(horario)
                        # except ValueError:
                        if not horario in horariosLocal:
                            entrada=horario[0]
                            salida=horario[1]
                            cedula=horario[2]
                            dia=horario[3]
                            cursorlocal.execute('''INSERT INTO web_horariospermitidos (entrada, salida, cedula_id, dia)
                            VALUES (%s, %s, %s, %s);''', (entrada, salida, cedula, dia))
                            connlocal.commit()

                    contador=0
                    for horariosLocaliterar in horariosLocal:
                        contador=contador+1
                        print(contador)
                        #print(horariosLocaliterar)
                        # try:
                        #     horariosServidor.index(horariosLocaliterar)
                        # except ValueError:
                        if not horariosLocaliterar in horariosServidor:
                            entrada=horariosLocaliterar[0]
                            salida=horariosLocaliterar[1]
                            cedula=horariosLocaliterar[2]
                            dia=horariosLocaliterar[3]
                            cursorlocal.execute('DELETE FROM web_horariospermitidos WHERE entrada=%s AND salida=%s AND cedula_id=%s AND dia=%s',(entrada, salida, cedula, dia))
                            connlocal.commit()

                    cursorlocal.execute('SELECT * FROM web_horariospermitidos')
                    horariosLocal= cursorlocal.fetchall()
                    if len(horariosLocal) == len(horariosServidor):
                        consultaHorarios=True
                        print(f'consultaHorarios: {consultaHorarios}')
                    horariosLocal=[]
                    horariosServidor=[]
                except requests.exceptions.ConnectionError:
                    print("fallo consultando api en la etapa de horarios")
            except Exception as e:
                print(f"{e} - fallo total etapa de horarios")

        if consultaHorarios and consultarTodo:
            try:
                try:
                    listaempleadosseguricel=[]
                    for empleado_seguricel in empleados_seguricel:
                        cedula=empleado_seguricel[0]
                        # try:
                        #     listaempleadosseguricel.index(cedula)
                        # except ValueError:
                        if not cedula in listaempleadosseguricel:
                            listaempleadosseguricel.append(cedula)
                    banderaHuellas=True

                    cursorlocal.execute('SELECT template, id_suprema, cedula FROM web_huellas')
                    huellas_local= cursorlocal.fetchall()

                    request_json = requests.get(url=f'{URL_API}obtenerhuellascontratoapi/{CONTRATO}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()

                    huellasServidor=[]
                    idsSupremaOcupados=[]
                    for consultajson in request_json:
                        tuplaHuellaIndividual=(consultajson['template'],consultajson['id_suprema'],consultajson['cedula'])
                        huellasServidor.append(tuplaHuellaIndividual)
                        if consultajson['id_suprema']:
                            idsSupremaOcupados.append(consultajson['id_suprema'])

                    nro_huellas_local = len(huellas_local)
                    nro_huellas_servidor = len(huellasServidor)

                    print(f'huellas en local: {nro_huellas_local}')
                    print(f'huellas en servidor: {nro_huellas_servidor}')

                    #cuando se van a eliminar huellas
                    if nro_huellas_local > nro_huellas_servidor:
                        contador=0
                        for huella in huellas_local:
                            contador=contador+1
                            print(contador)
                            #print(huella)
                            # try:
                            #     huellasServidor.index(huella)
                            # except ValueError:
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
                                    banderaHuellas=False
                        listaHuellasServidor=[]
                        listahuellaslocal=[]

                    # cuando se van a agregar huellas
                    
                    if nro_huellas_servidor > nro_huellas_local:
                        contador=0
                        for huella in huellasServidor:
                            template_local=[]
                            if huella[2] in listaempleadosseguricel:
                                cursorlocal.execute('SELECT cedula FROM web_huellas WHERE template=%s',(huella[0],))
                                template_local= cursorlocal.fetchall()
                            if not template_local:
                                contador=contador+1
                                print(contador)
                                #print(huella)
                                idsSupremaOcupados.sort()
                                # try:
                                #     huellas_local.index(huella)
                                # except ValueError:
                                if not huella in huellas_local:
                                    template=huella[0]
                                    id_suprema=huella[1]
                                    cedula=huella[2]
                                    nroCaptahuellasConHuella=0
                                    captahuella_actual=0
                                    IdSupremaContador=0 #esto lo uso para ver si hay id de suprema disponibles
                                    if not id_suprema:
                                        # cursorlocal.execute('SELECT id_suprema FROM web_huellas ORDER BY id_suprema ASC')
                                        # ids_suprema_local= cursorlocal.fetchall()
                                        nro_ids_suprema_ocupados=len(idsSupremaOcupados)
                                        if not idsSupremaOcupados:
                                            id_suprema = 1
                                            if not cedula in listaempleadosseguricel:
                                                requests.put(url=f'{URL_API}agregaridsupremaportemplateapi/{template}/{id_suprema}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                                        else:
                                            for id_suprema_ocupado in idsSupremaOcupados:
                                                IdSupremaContador=IdSupremaContador+1
                                                if not id_suprema_ocupado == IdSupremaContador:
                                                    id_suprema=IdSupremaContador
                                                    if not cedula in listaempleadosseguricel:
                                                        requests.put(url=f'{URL_API}agregaridsupremaportemplateapi/{template}/{id_suprema}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3)
                                                    break
                                            if nro_ids_suprema_ocupados == IdSupremaContador:
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
                                            except Exception as e:
                                                print(f"{e} - fallo al conectar con la esp8266 con la ip:{captahuella}")
                                    if nroCaptahuellasConHuella == captahuella_actual and captahuella_actual != 0:
                                        cursorlocal.execute('''INSERT INTO web_huellas (id_suprema, cedula, template)
                                        VALUES (%s, %s, %s)''', (id_suprema, cedula, template))
                                        connlocal.commit()
                                        idsSupremaOcupados.append(id_suprema)
                                    elif captahuella_actual != nroCaptahuellasConHuella and nroCaptahuellasConHuella != 0:
                                        banderaHuellas=False
                                        for captahuella in captahuellas:
                                            if captahuella:
                                                try:
                                                    peticion = requests.get(url=f'{captahuella}/quitar/{id_suprema_hex}', timeout=3)
                                                except Exception as e:
                                                    print(f" {e} - fallo al conectar con la esp8266 con la ip:{captahuella}")
                        listaHuellasServidor=[]
                        listahuellaslocal=[]
                    print(f'banderahuella: {banderaHuellas}')
                    if banderaHuellas:
                        consultaHuellas=True 
                        print(f'consultaHuellas: {consultaHuellas}')      
                    listaUsuariosServidor=[]
                    listaUsuariosLocal=[]
                    listaempleadosseguricel=[]
                except requests.exceptions.ConnectionError:
                    print("fallo consultando api en la etapa 3")
            except Exception as e:
                print(f"{e} - fallo total etapa3")
            
        if consultaHuellas and consultarTodo:
            try:
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

                    print(f'tags en local: {nro_tags_local}')
                    print(f'tags en servidor: {nro_tags_servidor}')

                    contador=0
                    for tagServidor in tagsServidor:
                        contador=contador+1
                        print(contador)
                        print(tagServidor)
                        # try:
                        #     tags_local.index(tagServidor)
                        # except ValueError:
                        if not tagServidor in tags_local:
                            epc=tagServidor[0]
                            cedula=tagServidor[1]
                            cursorlocal.execute('''INSERT INTO web_tagsrfid (epc, cedula)
                            VALUES (%s, %s);''', (epc, cedula))
                            connlocal.commit()

                    contador=0
                    for taglocaliterar in tags_local:
                        contador=contador+1
                        print(contador)
                        print(taglocaliterar)
                        # try:
                        #     tagsServidor.index(taglocaliterar)
                        # except ValueError:
                        if not taglocaliterar in tagsServidor:
                            epc=taglocaliterar[0]
                            cedula=taglocaliterar[1]
                            cursorlocal.execute('DELETE FROM web_tagsrfid WHERE epc=%s AND cedula=%s',(epc, cedula))
                            connlocal.commit()

                    cursorlocal.execute('SELECT epc, cedula FROM web_tagsrfid')
                    tags_local= cursorlocal.fetchall()
                    
                    nro_tags_local = len(tags_local)

                    if nro_tags_local == nro_tags_servidor:
                        consultaTags=True
                        print(f'consultaTags: {consultaTags}')

                except requests.exceptions.ConnectionError:
                    print("fallo consultando api en la etapa 4")
            except Exception as e:
                print(f"{e} - fallo total etapa4")

        if consultaTags and consultarTodo:
            try:
                cursorlocal.execute('SELECT * FROM web_fotos')
                fotos_local= cursorlocal.fetchall()
                try:
                    request_json = requests.get(url=f'{URL_API}obtenerfotoscontratoapi/{CONTRATO}/', auth=('BaseLocal_access', 'S3gur1c3l_local@'), timeout=3).json()
                    listaFotosServidor=[]
                    for consultajson in request_json:
                        rutaFotoSinProcesar = consultajson['foto'][8:].split('/')
                        rutaFotoProcesada = f"{rutaFotoSinProcesar[-3]}/{rutaFotoSinProcesar[-2]}/{rutaFotoSinProcesar[-1]}"
                        tuplaFotoIndividual=(int(consultajson['id']),rutaFotoProcesada,int(consultajson['estado']),consultajson['cedula'],)
                        listaFotosServidor.append(tuplaFotoIndividual)
                            
                    nro_fotos_local = len(fotos_local)
                    nro_fotos_servidor = len(listaFotosServidor)

                    print(f'fotos en local: {nro_fotos_local}')
                    print(f'fotos en servidor: {nro_fotos_servidor}')
                    #eliminar fotos de la base de datos local que no esten en la base de datos de heroku
                    contador=0
                    for fotolocal in fotos_local:
                        contador=contador+1
                        print(contador)
                        print(fotolocal)
                        # try:
                        #     listaFotosServidor.index(fotolocal)
                        # except ValueError:
                        if not fotolocal in listaFotosServidor:
                            try:
                                id=fotolocal[0]
                                foto=fotolocal[1]
                                os.remove(f'{foto}.jpg')
                                cursorlocal.execute('DELETE FROM web_fotos where id=%s', (id,))
                                connlocal.commit()
                            except Exception as e:
                                print(f"{e} - fallo borrando foto del usuario: {fotolocal[3]}")

                    #agregar fotos que no estan en la base de datos local pero que si estan en la de heroku
                    contador=0
                    for fotoServidor in listaFotosServidor:
                        # try:
                        #     fotos_local.index(fotoServidor)
                        # except ValueError:
                        contador=contador+1
                        print(contador)
                        print(fotoServidor)
                        if not fotoServidor in fotos_local:
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
                    
                    cursorlocal.execute('SELECT * FROM web_fotos')
                    fotos_local= cursorlocal.fetchall()
                    nro_fotos_local = len(fotos_local)
                    if nro_fotos_local == nro_fotos_servidor:
                        consultaFotos=True
                except requests.exceptions.ConnectionError:
                    print("fallo consultando api de fotos")
            except Exception as e:
                print(f"{e} - fallo total fotos")

        if consultaUsuarios and consultaFotos and consultaHorarios and consultaHuellas and consultaTags and consultarTodo:
            consultarTodo=False
            consultaUsuarios=False
            consultaHorarios=False
            consultaHuellas=False
            consultaTags=False
            consultaFotos=False
            break
            
        # print(f'consultarTodo: {consultarTodo}')
        # print(f'consultaUsuarios: {consultaUsuarios}')
        # print(f'consultaHorarios: {consultaHorarios}')
        # print(f'consultaHuellas: {consultaHuellas}')
        # print(f'consultaTags: {consultaTags}')
        # print(f'consultaFotos: {consultaFotos}')

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
            
