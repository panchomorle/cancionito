import requests # type: ignore
import sett
import json
import google_sheets
import asyncio #para manejar asincronías
import regex #para eliminar caracteres no alfanuméricos

def obtener_mensaje_whatsapp(message):
    if 'type' not in message :
        text = 'mensaje no reconocido'

    typeMessage = message['type']
    if typeMessage == 'text':
        text = message['text']['body']

    return text

def filtrar_number(number):
    if number[0:3] == "549": 
        car = "54"
        num = number[3:]
        number = (car+num)
    return number

async def enviar_mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Access-Control-Allow-Origin': '*',
                   'Authorization': 'Bearer '+whatsapp_token}
        
        response = requests.post(url=whatsapp_url, headers=headers, data=data)
        if response.status_code == 200:
            return 'mensaje enviado'
        else:
            print("El status code es: "+str(response.status_code))
            print("El mensaje era: "+str(data))
            return 'mensaje no enviado', response.status_code
    except Exception as e:
        return e,403
    

def text_message(number, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def image_message(number, url):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "image",
            "image": {
                "link": url
            }
        }
    )
    return data

def normalizar_string(text: str):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    texto_lower = text.lower() #convierto todo a minusculas
    for a, b in replacements: #reemplazo los 'a' de la tupla por los 'b' de la tupla
        texto_lower = texto_lower.replace(a, b)
    texto_limpio = regex.sub(r'[^\w\s\n]', '', texto_lower) #quito los no alfanuméricos con regex
    
    texto_normalizado = texto_limpio.strip() #acá le quito los espacios de atrás y adelante
    return texto_normalizado


async def administrar_chatbot(text, number, messageId, name):
    texto = normalizar_string(text) ##mensaje que envió el usuario
    canciones = [] #lista de IMAGENES de canciones a enviar
    el_texto_tiene_canciones = False #asumo que por defecto el usuario no pide canciones

    posibles_saludos=['hola', 'alo', 'hi', 'hello', 'ola', 'buenas', 'buen dia', 'buenos dias', 'good morning', 'how are you', 'como estas', 'que tal']
    if any(saludo in text for saludo in posibles_saludos):
        data = text_message(number, "¡Hola! Mi nombre es CancioNito🎵. Pedime una canción o una lista de canciones separadas por saltos de línea :D")
        await enviar_mensaje_whatsapp(data)
        data = text_message(number,'Podés pedirme cualquier canción del coritario Hossanna o escribir "random" para una canción aleatoria!💫')
        await enviar_mensaje_whatsapp(data)
    elif "random" in text:
        data = text_message(number,'Mi desarrollador (Juampi) todavía no me programó para hacer esto :\'C')
        await enviar_mensaje_whatsapp(data)
    else:
        ##CARGO EL JSON DE LA BDD: key=Title value=URL
        posibles_canciones = google_sheets.call()
        #SEPARO EL TEXTO DEL USUARIO POR SALTOS DE LINEA PARA VER SI SON CANCIONES
        print(texto)
        texto_separado = texto.split("\n") #array de canciones pedidas por el usuario
        print(texto_separado)
            #COMPRUEBO QUE CADA LINEA SEA UNA CANCION VÁLIDA:
        for txt in texto_separado: #itero sobre las canciones del usuario
            coincidence = False
            for nombre, imagen in posibles_canciones.items():
                if txt == nombre:
                    tupla = imagen,True #creo una tupla con la IMAGEN indicando que fue encontrada
                    canciones.append(tupla) #guardo la tupla para la cancion encontrada
                    coincidence = True
                    break
            if coincidence:
                el_texto_tiene_canciones = True
            else: #si el texto del usuario no coincidió con ninguna canción de la bdd
                tupla = txt, False #creo una tupla con el TITULO indicando que NO fue encontrado
                canciones.append(tupla) #guardo la tupla de la cancion no encontrada

        #FUNCIONALIDAD PRINCIPAL = SI HAY CANCIONES, MANDO IMAGEN.
        if el_texto_tiene_canciones:
            for cancion, encontrada in canciones:
                if encontrada:
                    c = cancion.split(" ") #genero un array separando por espacios
                    if isinstance(c, list): #si el campo 'canción' era una lista (la cancion tiene mas de 1 pág)
                        for each in c:
                            data = image_message(number, each)
                            await enviar_mensaje_whatsapp(data)
                    else:
                        data = image_message(number, cancion) #notar que acá cancion viene de "imagen", que es una URL
                        await enviar_mensaje_whatsapp(data)
                    #print(data)
                else: #notar que acá cancion viene de "texto", un string con el nombre de la cancion.
                    data = text_message(number, f'No se encontraron coincidencias para "{cancion}" prueba escribirla de otra forma!')
                    await enviar_mensaje_whatsapp(data)
        else:
            data = text_message(number, "No entendí :C intentá escribir el nombre de algún corito o alabanza porfis")
            await enviar_mensaje_whatsapp(data)