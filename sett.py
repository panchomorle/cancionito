from dotenv import load_dotenv # type: ignore
import os 

load_dotenv()

token = os.environ['TOKEN']

whatsapp_token = os.environ['WHATSAPP_TOKEN']

whatsapp_url = os.environ['WHATSAPP_URL']

cancionito_credentials = {
    "type": "service_account",
    "project_id": "cancionitobd",
    "private_key_id": os.environ['PRIVATE_KEY_ID'],
    "private_key": os.environ['PRIVATE_KEY'],
    "client_email": "servicio-cancionito@cancionitobd.iam.gserviceaccount.com",
    "client_id": "107560905979064627923",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/servicio-cancionito%40cancionitobd.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}