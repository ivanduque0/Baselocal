import psycopg2
import cv2
import numpy as np
import psycopg2
import os
import tflite_runtime.interpreter as tflite
import time
import urllib.request

tflite_interpreter = tflite.Interpreter("modelospoofinglite")
tflite_interpreter.allocate_tensors()
total=0
conn = None
spoofing = 0
nospoofing = 0
spoofingdb = 0
nospoofingdb = 0
URL_CAMARA = os.environ.get("URL_CAMARA")
URL_SNAPSHOOT = f"{URL_CAMARA}:8080/?action=snapshot"

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


nro_camaras_dict= { camara1:"1", 
                camara2:"2", 
                camara3:"3", 
                camara4:"4",
                camara5:"5", 
                camara6:"6", 
                camara7:"7", 
                camara8:"8",
                camara9:"9", 
                camara10:"10", 
                camara11:"11", 
                camara12:"12", 
                camara13:"13", 
                camara14:"14", 
                camara15:"15", 
                camara16:"16", 
                camara17:"17", 
                camara18:"18", 
                camara19:"19", 
                camara20:"20"
                    }

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
        conn.autocommit = False
        cursor = conn.cursor()

        while True:
            cursor.execute('SELECT * FROM sensor WHERE nro_camara=%s', (nro_camaras_dict[URL_CAMARA],))
            sensor_onoff = cursor.fetchall()
            if sensor_onoff[0][0] == 1:
                imagenurl = urllib.request.urlopen (URL_SNAPSHOOT) #abrimos el URL
                imagenarray = np.array(bytearray(imagenurl.read()),dtype=np.uint8)
                video = cv2.imdecode (imagenarray,-1)
                alto, ancho, _ = video.shape
                K = np.float32([[1,0,100],[0,1,100]])
                video2 = cv2.warpAffine(video, K, (ancho+200,alto+200))
                alto2, ancho2, _ = video2.shape
                K = cv2.getRotationMatrix2D((ancho2 // 2, alto2 // 2), 90, 1)
                video2 = cv2.warpAffine(video2, K, (alto2,ancho2))
                K = np.float32([[1,0,-160],[0,1,-41]])
                video = cv2.warpAffine(video2, K, (alto, ancho))
                video = cv2.flip(video, 0)
                video = cv2.cvtColor(video, cv2.COLOR_BGR2GRAY)
                video = video.reshape(-1, 240, 360, 1)
                video = video.astype(np.float32)

                #codigo donde se usa tensorflow lite
                input_details = tflite_interpreter.get_input_details()
                output_details = tflite_interpreter.get_output_details()
                tflite_interpreter.resize_tensor_input(input_details[0]['index'], (1, 240, 360, 1))
                tflite_interpreter.resize_tensor_input(output_details[0]['index'], (1, 2))
                tflite_interpreter.allocate_tensors()
                tflite_interpreter.set_tensor(input_details[0]['index'], video)
                # Run inference
                tflite_interpreter.invoke()
                # Get prediction results
                tflite_model_predictions = tflite_interpreter.get_tensor(output_details[0]['index'])
                #print("Prediction results shape:", tflite_model_predictions.shape)
                #print(tflite_model_predictions)
                spoofing = tflite_model_predictions[0][0]
                nospoofing = tflite_model_predictions[0][1]
                if spoofing!=spoofingdb or nospoofing != nospoofingdb:
                    cursor.execute('UPDATE antisp SET spoofing=%s,nospoofing=%s WHERE nro_camara=%s', (str(spoofing),str(nospoofing),nro_camaras_dict[URL_CAMARA]))
                    conn.commit()
                    cursor.execute('SELECT * FROM antisp WHERE nro_camara=%s', (nro_camaras_dict[URL_CAMARA],))
                    consulta = cursor.fetchall()
                    spoofingdb = consulta[0][0]
                    nospoofingdb = consulta[0][1]        
            
    except (Exception, psycopg2.Error) as error:
        print("fallo en hacer las consultas")
        total=0
        spoofing = 0
        nospoofing = 0
        spoofingdb = 0
        nospoofingdb = 0
    
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("se ha cerrado la conexion a la base de datos")
            total=0
            spoofing = 0
            nospoofing = 0
            spoofingdb = 0
            nospoofingdb = 0
