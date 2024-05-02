import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sett
import services

myscope = ['https://spreadsheets.google.com/feeds', 
                'https://www.googleapis.com/auth/drive']
crededentials = ServiceAccountCredentials.from_json_keyfile_dict(sett.cancionito_credentials, myscope)

def get_client():
    client =gspread.authorize(crededentials)
    return client

def call():
    client = get_client()

    #open the file
    mysheet = client.open("BDD_Cancionito").sheet1

    matriz_valores = mysheet.get_all_values() #devuelve una lista de filas (representadas como listas de columnas)
    #                   le quito caracteres no alfanumericos y le quito los espacios de atras y adelante
    diccionario =  dict((services.normalizar_string(fila[0]),fila[1]) for fila in matriz_valores) #transformo matriz Nx2 en dict

    return diccionario