import requests
import os.path
import socket
import logging
from configparser import ConfigParser
from flask import Flask, render_template, request
from threading import Thread
import oauth as worker
app = Flask(__name__)
flasLogger = logging.getLogger('werkzeug')
flasLogger.setLevel(logging.ERROR)
config = ConfigParser()
configPath = 'resources/config.ini'
dbPath = 'resources/db.json'

Threads = []

DB = []

try:    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    LOCAL_IP = s.getsockname()[0]
    EXTERNAL_IP = requests.get('https://api.ipify.org').content.decode('utf8')
    s.close()
except Exception as err:
    print('Error while getting ips! Exiting! Error: ', err)
    print('Error while getting ips! Check your internet connection! Exiting!')
    exit()

if(os.path.exists(configPath)):
    print('config file exist')
    config.read(configPath)
else:
    print('config file doesn\'t exist! creating, you have to enter some values!')
    a = input("Discord client id: ")
    b = input("Discord client secret: ")
    while(True):
        c = input("Discord api url(https://discord.com/api/v10): ")
        if(c == ''):
            c = 'https://discord.com/api/v10'
            break
        if(c.startswith("https://discord.com/api/")):
            break
        else:
            print('incorrect url')
    while(True):
        d = input("Port(3000) 1024-32766: ")
        if(d == ''):
            d = 3000
        try:
            ret = int(d)
            if(ret>=1024 and ret<=32767):
                break
            else:
                print("incorrect port number! pls enter number in 1024-32766")
        except ValueError:
            print('You have not entered a number!')
    while(True):
        e = input('redirect url *generated exactly for you*(%s): ' % 'http://%s:' % EXTERNAL_IP)
        if(e == ''):
            e = 'http://%s:' % EXTERNAL_IP
            break
        if(e.startswith('http')):
            break
        else:
            print('incorrect url! please enter http(https) url!')
    while(True):
        f = input("Url path(/api/auth/discord/redirect): ")
        if(f == ''):
            f = "/api/auth/discord/redirect"
            break
        if(f == '/'):
            print('incorrect path! must be more then just "/"')
        elif(f.startswith('/')):
            break
        else:
            print('incorrect path! must start with /')
    
    config['discord'] = {'client_id': a,
                         'client_secret': b,
                         'api': c}
    config['grabber'] = {'port': d,
                         'redirect_uri': e,
                         'grabber_url_args': f}
    
    print('writing config file in %s' % configPath)
    with open(configPath, 'w') as conf:
        config.write(conf)
        print('writed config file in %s' % configPath)



worker.DB = DB

API_ENDPOINT = config['discord']['api']
CLIENT_ID = config['discord']['client_id']
CLIENT_SECRET = config['discord']['client_secret']
PORT = config['grabber']['port']
URL_ARGS = config['grabber']['grabber_url_args']
REDIRECT_URI = config['grabber']['redirect_uri'] + PORT + URL_ARGS

worker.API_ENDPOINT = API_ENDPOINT
worker.CLIENT_ID = CLIENT_ID
worker.CLIENT_SECRET = CLIENT_SECRET
worker.REDIRECT_URI = REDIRECT_URI

@app.route("/")
def home():
    return render_template('home.html')

@app.route(URL_ARGS)
async def login():
    if (request.args.__contains__('code')):
        code = request.args['code']
        i = Threads.__len__()
        t = Thread(target=worker.code_catch, args=(code, i,), daemon=True)
        Threads.append(t)
        Threads[i].start()
        return 'hi!'

if __name__ == "__main__":
    app.run(debug = False, port=PORT,host=LOCAL_IP)