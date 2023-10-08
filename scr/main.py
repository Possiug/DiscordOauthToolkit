import requests
import os.path
from configparser import ConfigParser
config = ConfigParser()
configPath = 'config/secrets.ini'
config.read(configPath)

if(os.path.exists(configPath)):
    print('file exist')
    config.read(configPath)
else:
    print('file doesn\'t exist')
    exit()

API_ENDPOINT = config['discord']['api']
CLIENT_ID = config['discord']['client_id']
CLIENT_SECRET = config['discord']['client_secret']
REDIRECT_URI = config['grabber']['redirect_uri'] + config['grabber']['port']    


config.read(configPath)
def exchange_code(code):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)