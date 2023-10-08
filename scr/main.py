import requests
import os.path
import socket
import json
from configparser import ConfigParser
from flask import Flask, render_template, request
app = Flask(__name__)
config = ConfigParser()
configPath = 'resources/config.ini'
dbPath = 'resources/db.json'

cTokens = []
cRefreshes = []

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
LOCAL_IP = s.getsockname()[0]
EXTERNAL_IP = requests.get('https://api.ipify.org').content.decode('utf8')
s.close()

if(os.path.exists(configPath)):
    print('config file exist')
    config.read(configPath)
else:
    print('config file doesn\'t exist')
    exit()

if(os.path.exists(dbPath)):
    with open(dbPath, 'r+') as db:
        try:
            loadedJs = json.load(db)
            cTokens =  loadedJs['tokens']
            cRefreshes = loadedJs['refreshes']
            print("db was loaded!")
            print(cTokens, cRefreshes)
        except Exception as err:
            print("error while reading file!: ",err)
            exit()
else:
    print("db doesn't exist, recreating file!")
    with open(dbPath, 'w') as db:
        json.dump({'tokens': cTokens, 'refreshes': cRefreshes}, db, indent=4)
    


API_ENDPOINT = config['discord']['api']
CLIENT_ID = config['discord']['client_id']
CLIENT_SECRET = config['discord']['client_secret']
PORT = config['grabber']['port']
URL_ARGS = config['grabber']['grabber_url_args']
REDIRECT_URI = config['grabber']['redirect_uri'] + PORT + URL_ARGS


@app.route("/")
def home():
    return render_template('home.html')

@app.route(URL_ARGS)
def login():
    if (request.args.__contains__('code')):
        code = request.args['code']
        return exchange_code(code)
    else:
        return 'hi!'
    

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
    if(r):
        r = r.json()
        return r
    
if __name__ == "__main__":
    app.run(debug = False, port=PORT,host=LOCAL_IP)