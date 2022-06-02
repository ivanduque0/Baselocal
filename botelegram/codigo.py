import telebot
import time
import psycopg2
import os
import pytz
from datetime import datetime
from keyboa import Keyboa

dias_semana = ("Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo")
ultimahora = datetime.strptime('23:59:59', '%H:%M:%S').time()
primerahora = datetime.strptime('00:00:00', '%H:%M:%S').time()
token=os.environ.get("TOKEN_BOT")
bot = telebot.TeleBot(token, parse_mode=None)
razon=os.environ.get("RAZON_BOT")
total=0
CONTRATO=os.environ.get("CONTRATO")
puertas = [
    'entrada principal', 
    'porton vehicular',
    'puerta trasera'
]
keyboard = Keyboa(items=puertas)


def aperturaconcedida(nombref, fechaf, horaf, razonf, contratof, cedulaf, cursorf,connf):
    cursorf.execute('''INSERT INTO web_interacciones (nombre, fecha, hora, razon, contrato, cedula_id)
    VALUES (%s, %s, %s, %s, %s, %s);''', (nombref, fechaf, horaf, razonf, contratof, cedulaf))
    cursorf.execute('''UPDATE led SET onoff=1 WHERE onoff=0;''')
    connf.commit()


def aperturadenegada(cursorf, connf):
    cursorf.execute('''UPDATE led SET onoff=2 WHERE onoff=0;''')
    connf.commit()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    message.text
    chatid = message.from_user.id
    bot.reply_to(message, f"Bienvenido, su ID es es: {chatid}")
    bot.send_message(chat_id=chatid,text='Que acceso desea usar?', reply_markup=keyboard())


@bot.callback_query_handler(func=lambda call: True)
def manejador_seleccion(call):

    if call.data == 'entrada principal':
        #print('accionar')
        diasusuario = []
        cantidaddias = 0
        contadoraux = 0
        orden = 'abrir entrada principal'
        chat_id = call.message.chat.id
        #print(orden)
        #print(chat_id)
        #print(message)

        cursor.execute("SELECT * FROM web_usuarios where telegram_id='%s'", (chat_id,))
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
                    if dia==diahoy and cantidaddias==1:
                        hora=str(caracas_now)[11:19]
                        horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                        fecha=str(caracas_now)[:10]
                        etapadia=1
                        if entrada<salida:
                            if horahoy >= entrada and horahoy <= salida:
                                #print('entrada concedida')
                                aperturaconcedida(nombre, fecha, horahoy, razon, CONTRATO, cedula, cursor,conn)
                                etapadiaapertura=1
                            else:
                                aperturadenegada(cursor, conn)
                                #print('fuera de horario')
                        if entrada>salida:
                            if (horahoy>=entrada and horahoy <=ultimahora) or (horahoy>=primerahora and horahoy <= salida):
                                #print('entrada concedida')
                                aperturaconcedida(nombre, fecha, horahoy, razon, CONTRATO, cedula, cursor,conn)
                                etapadiaapertura=1
                            else:
                                aperturadenegada(cursor, conn)
                                #print('fuera de horario')
                    elif dia==diahoy and cantidaddias>1:
                        hora=str(caracas_now)[11:19]
                        horahoy = datetime.strptime(hora, '%H:%M:%S').time()
                        fecha=str(caracas_now)[:10]
                        etapadia=1
                        if entrada<salida:
                            if horahoy >= entrada and horahoy <= salida:
                                #print('entrada concedida')
                                aperturaconcedida(nombre, fecha, horahoy, razon, CONTRATO, cedula, cursor,conn)
                                etapadiaapertura=1
                                contadoraux=0
                            else:
                                contadoraux = contadoraux+1
                                if contadoraux == cantidaddias:
                                    aperturadenegada(cursor, conn)
                                    contadoraux=0
                        if entrada>salida:
                            if (horahoy>=entrada and horahoy <=ultimahora) or (horahoy>=primerahora and horahoy <= salida):
                                #print('entrada concedida')
                                aperturaconcedida(nombre, fecha, horahoy, razon, CONTRATO, cedula, cursor,conn)
                                etapadiaapertura=1
                                contadoraux=0
                            else:
                                contadoraux = contadoraux+1
                                if contadoraux == cantidaddias:
                                    aperturadenegada(cursor, conn)
                                    contadoraux=0
                                #print('fuera de horario')
                if etapadia==0 and etapadiaapertura==0:
                    aperturadenegada(cursor, conn)
                    #print('Dia no permitido')
            if horarios_permitidos == []:
                aperturadenegada(cursor, conn) 
                #print('este usuario no tiene horarios establecidos')
            diasusuario=[]    
            
        else:
            aperturadenegada(cursor, conn) 
            

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
        cursor = conn.cursor()

        bot.infinity_polling()


    except (Exception, psycopg2.Error) as error:
        print("fallo en hacer las consultas")
        total=0

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("se ha cerrado la conexion a la base de datos")
            total=0


