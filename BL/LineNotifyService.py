import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = 'https://notify-api.line.me/api/notify'
token = os.environ.get('TOKEN')
headers = {'content-type': 'application/x-www-form-urlencoded',
           'Authorization': 'Bearer '+str(token)}

def SendLineNotify(msg):
    r = requests.post(url, headers=headers, data={'message': msg})
    print(r.text)
    return r.text