import requests
import os.path
import socket
from configparser import ConfigParser
from flask import Flask, render_template, request
app = Flask(__name__)
config = ConfigParser()
configPath = 'config/config.ini'

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
LOCAL_IP = s.getsockname()[0]
EXTERNAL_IP = requests.get('https://api.ipify.org').content.decode('utf8')
s.close()

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
PORT = config['grabber']['port']
URL_ARGS = config['grabber']['grabber_url_args']

@app.route("/")
def home():
    return render_template('home.html')

@app.route(URL_ARGS)
def redirect():
    code = request.args['code']
    return code


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
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    app.run(debug = False, port=PORT,host=LOCAL_IP)