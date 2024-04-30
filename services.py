import requests # type: ignore
import sett
import json

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

def enviar_mensaje_whatsapp(data):
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

def administrar_chatbot(text, number, messageId, name):
    text = text.lower() ##mensaje que envió el usuario
    canciones = [] #lista de IMAGENES de canciones a enviar
    el_texto_tiene_canciones = False #asumo que por defecto el usuario no pide canciones

    posibles_saludos=['hola', 'alo', 'hi', 'hello', 'ola', 'buenas', 'buen día', 'buen dia']
    if any(saludo in text for saludo in posibles_saludos):
        data = text_message(number, "¡Hola! Mi nombre es CancioNito🎵. Pedime una canción o una lista de canciones separadas por saltos de línea :D")
        enviar_mensaje_whatsapp(data)
        data = text_message(number,"Por ahora solo tengo las siguientes canciones:\n-Padre amado\n-Tengo paz\n-Jesucristo basta\nPedime la que quieras!💫")
        enviar_mensaje_whatsapp(data)
    else:
        ##CARGO EL JSON DE LA BDD
        posibles_canciones = {
            "Padre amado":"https://imgv2-2-f.scribdassets.com/img/document/281897126/original/5ae918e126/1713539600?v=1",
            "Tengo paz":"https://imgv2-1-f.scribdassets.com/img/document/325877359/original/706763de2c/1712197720?v=1",
            "Jesucristo basta":"https://imgv2-2-f.scribdassets.com/img/document/467744741/original/88d82f751d/1710639242?v=1"
        }
        #SEPARO EL TEXTO POR ESPACIOS PARA VER SI SON CANCIONES
        texto_separado = text.split("\n")
        #COMPRUEBO QUE EL TEXTO SEAN CANCIONES
        for texto in texto_separado: #itero sobre las canciones del usuario
            coincidence = False
            for nombre, imagen in posibles_canciones.items():
                if texto == nombre.lower():
                    tupla = imagen,True #creo una tupla con la IMAGEN indicando que fue encontrada
                    canciones.append(tupla) #guardo la tupla para la cancion encontrada
                    coincidence = True
                    break
            if coincidence:
                el_texto_tiene_canciones = True
            else: #si el texto del usuario no coincidió con ninguna canción de la bdd
                tupla = texto, False #creo una tupla con el TITULO indicando que NO fue encontrado
                canciones.append(tupla) #guardo la tupla de la cancion no encontrada

        #FUNCIONALIDAD PRINCIPAL = SI HAY CANCIONES, MANDO IMAGEN.
        if el_texto_tiene_canciones:
            for cancion, encontrada in canciones:
                if encontrada:
                    data = image_message(number, cancion) #notar que acá cancion viene de "imagen", que es una URL
                else: #notar que acá cancion viene de "texto", un string con el nombre de la cancion.
                    data = text_message(number, f'No se encontraron coincidencias para "{cancion}" prueba escribirla de otra forma!')

                enviar_mensaje_whatsapp(data)
        else:
            data = text_message(number, "No entendí :C intentá escribir el nombre de algún corito o alabanza porfis")
            enviar_mensaje_whatsapp(data) 
