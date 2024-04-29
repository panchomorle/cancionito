from dotenv import load_dotenv # type: ignore
import os 

load_dotenv()

token = os.environ['TOKEN']

whatsapp_token = os.environ['WHATSAPP_TOKEN']

whatsapp_url = os.environ['WHATSAPP_URL']