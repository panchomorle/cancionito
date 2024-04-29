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

def enviar_mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer '+whatsapp_token}
        
        response = requests.post(whatsapp_url, headers=headers, data=data)
        if response.status_code == 200:
            return 'mensaje enviado'
        else:
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

def image(number, url):
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
    list = []

    if 'hola' in text:
        data = text_message(number, "Hola! Mi nombre es Cancionito.")
    else:
        data = text_message(number, "No entendí lo que quisiste decir, lo siento!")
    enviar_mensaje_whatsapp(data)
