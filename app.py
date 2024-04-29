from flask import Flask, request # type: ignore
import sett
import services

app = Flask(__name__)

@app.route('/bienvenido', methods=['GET'])
def bienvenido():
    return "Hola, me llamo cancionito!"

@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.token and challenge != None:
            return challenge
        else:
            return 'token incorrecto',403
    except Exception as e:
        return e,403

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        messages = value['messages'][0]
        number = messages['from']
        messageId = messages['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        ## text = messages['text']['body']
        #Lo extraigo a una funcion en services para manejar el type
        text = services.obtener_mensaje_whatsapp(messages)
        services.administrar_chatbot(text, number, messageId, name)

        return 'enviado'
    except Exception as e:
        return 'no enviado'+str(e)

if __name__ == '__main__':
    app.run()