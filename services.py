import requests # type: ignore
import sett
import json
import google_sheets
import regex #para eliminar caracteres no alfanuméricos
import random as r

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
            print("se envió"+str(data))
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

#--------funcion que permite enviar canción entera si tiene más de 1 pág-----------
def enviar_cancion(number, url): 
    URLS = url.split(" ") #genero un array separando por espacios
    if isinstance(URLS, list): #si el campo 'URLS' era una lista (la cancion tiene mas de 1 pág)
        for each in URLS:
            data = image_message(number, each)
            enviar_mensaje_whatsapp(data)
    else:
        data = image_message(number, url)
        enviar_mensaje_whatsapp(data)

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

def normalizar_array(array: list):
    array_normalizado = []
    for text in array:
        array_normalizado.append(normalizar_string(text))
    return array_normalizado

def elegir_random(posibles_canciones: dict):
    lista_titulos = list(posibles_canciones.keys())
    indice = r.randint(0, len(posibles_canciones)-1)
    return lista_titulos[indice]

def administrar_chatbot(text, number, messageId, name):
    texto = normalizar_string(text) ##sin Special Characters y en lower
    canciones = [] #lista de IMAGENES de canciones encontradas a enviar
    posibles_canciones = {} #BASE DE DATOS JSON
    el_texto_tiene_canciones = False #asumo que por defecto el usuario no pide canciones

    posibles_saludos=['hola', 'alo', 'hi', 'hello', 'ola', 'buenas', 'buen dia', 'buenos dias', 'good morning', 'how are you', 'como estas', 'que tal']
    if any(saludo in texto for saludo in posibles_saludos):
        posibles_canciones = google_sheets.call() if not posibles_canciones else posibles_canciones
        sugerencias=""
        sugerencias =''.join("\n"+elegir_random(posibles_canciones) for _ in range(3))
        data = text_message(number, f"¡Hola! Mi nombre es CancioNito🎵. Pedime una canción o una lista de canciones separadas de esta forma: {sugerencias}")
        enviar_mensaje_whatsapp(data)
        data = text_message(number,'Podés pedirme cualquier canción del coritario Hossanna o escribir "random" para una canción aleatoria!💫')
        enviar_mensaje_whatsapp(data)
    elif "random" in texto:
        #-----llamo a la BDD solo si el array sigue vacio (posibles_canciones = {})
        posibles_canciones = google_sheets.call() if not posibles_canciones else posibles_canciones
        clave = elegir_random(posibles_canciones) #elijo una clave random de la bdd
        valor = posibles_canciones[clave] #extraigo su valor
        #text_message(number,'Mi desarrollador (Juampi) todavía no me programó para hacer esto :\'C')
        enviar_cancion(number, valor) #envio la imagen random
    else: #---------------------------MOTOR PRINCIPAL: CHECKEO DE CANCIONES-----------------------
        ##CARGO EL JSON DE LA BDD: key=Title value=URL
        posibles_canciones = google_sheets.call() if not posibles_canciones else posibles_canciones
        #SEPARO EL TEXTO DEL USUARIO POR SALTOS DE LINEA PARA VER SI SON CANCIONES
        texto_separado = normalizar_array(text.split("\n")) #array de canciones pedidas por el usuario
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

        #--------FUNCIONALIDAD DE ENVIO DE CANCIONES = SI HAY CANCIONES, MANDO IMAGEN.
        if el_texto_tiene_canciones:
            for cancion, encontrada in canciones:
                if encontrada:
                    enviar_cancion(number, cancion) #notar que acá cancion viene de "imagen", que es una URL
                else: #notar que acá cancion viene de "texto", un string con el nombre de la cancion.
                    data = text_message(number, f'No se encontraron coincidencias para "{cancion}" prueba escribirla de otra forma!')
                    enviar_mensaje_whatsapp(data)
        else:
            data = text_message(number, "No entendí :C intentá escribir el nombre de algún corito o alabanza porfis")
            enviar_mensaje_whatsapp(data)