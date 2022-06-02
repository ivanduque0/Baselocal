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
while True:
    
    t11=time.perf_counter()
    while total<=5:
        t22=time.perf_counter()
        total=t22-t11
    total=0

    try:
        conn = psycopg2.connect(
            database=os.environ.get("DATABASE"), 
            user=os.environ.get("USER"), 
            password=os.environ.get("PASSWORD"), 
            host=os.environ.get("HOST"), 
            port=os.environ.get("PORT")
        )
        conn.autocommit = False
        cursor = conn.cursor()

        while True:
            cursor.execute('SELECT * FROM sensor')
            sensor_onoff = cursor.fetchall()
            if sensor_onoff[0][0] == 1:
                url = os.environ.get("HOSTSNAPSHOOT")
                imagenurl = urllib.request.urlopen (url) #abrimos el URL
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
                print(tflite_model_predictions)
                spoofing = tflite_model_predictions[0][0]
                nospoofing = tflite_model_predictions[0][1]
                if spoofing!=spoofingdb or nospoofing != nospoofingdb:
                    cursor.execute('UPDATE antisp SET spoofing=%s,nospoofing=%s', (str(spoofing),str(nospoofing)))
                    conn.commit()
                    cursor.execute('SELECT * FROM antisp')
                    consulta = cursor.fetchall()
                    spoofingdb = consulta[0][0]
                    nospoofingdb = consulta[0][1]
                
    except (Exception, psycopg2.Error) as error:
        #print("fallo en hacer las consultas")
        total=0
        spoofing = 0
        nospoofing = 0
        spoofingdb = 0
        nospoofingdb = 0
    
    finally:
        if conn:
            cursor.close()
            conn.close()
            #print("se ha cerrado la conexion a la base de datos")
            total=0
            spoofing = 0
            nospoofing = 0
            spoofingdb = 0
            nospoofingdb = 0