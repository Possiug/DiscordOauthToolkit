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
currentUser = None
while(True):
    command = input('~: ')
    cwa = command.split(' ')
    cmd = cwa[0]
    match(cmd):
        case 'help':
            print('Command list:\n\thelp - show this list\n\tdebug [off|on] control theards debug\n\tdb [length|show|gbName|gbId] - work with DB\n\tuser [set|clean|show|update|guildProfile|joinGuild] working with users and oauth methods\n\tall [update|joinGuild] working with all users in DB\n\tfunction [updateInfo] works directly with functions(FOR PRO ONLY!)')
        case 'debug':
            if(cwa.__len__() == 2):
                match(cwa[1]):
                    case 'off':
                        worker.debug = False
                        print('Debug info now is turned off')
                    case 'on':
                        worker.debug = True
                        print('Debug info now is turned on')
                    case _:
                        print('Arg "%s" isn\'t %s\'s arg!' % (cwa[1], cmd))  
            else:
                print('Incorrect args amount! Use "help"')
        case 'db':
            if(cwa.__len__() ==2):
                match(cwa[1]):
                    case 'length':
                        print(worker.DB.__len__())
                    case 'show':
                        print(worker.DB)    
                    case _:
                        print('Arg "%s" isn\'t %s\'s arg!' % (cwa[1], cmd))
            elif(cwa.__len__() == 3):
                match(cwa[1]):
                    case 'gbName':
                        worker.dbWorker.show(worker.dbWorker.getByName(cwa[2]))
                    case 'gbId':
                        worker.dbWorker.show(worker.dbWorker.getById(cwa[2]))                    
                    case _:
                        print('Arg "%s" isn\'t %s\'s arg!' % (cwa[1], cmd))        
            else:
                print('Incorrect args amount! Use "help"')
        case 'user':
            if(cwa.__len__() == 2):
                match(cwa[1]):
                    case 'show':
                        if(currentUser == None):
                            print('User wasn\'t setted!')
                        else:
                            worker.dbWorker.show(worker.dbWorker.getById(currentUser))
                    case 'clean':
                        currentUser = None
                        print('user cleaned')
                    case 'update':
                        if(currentUser == None):
                            print('User wasn\'t setted!')
                        else:
                            i = Threads.__len__()
                            Threads.append(Thread(target=worker.UpdateInfo, args=(worker.dbWorker.getById(currentUser)['refresh_token'], i,), daemon=True))
                            Threads[i].start()
                            Threads[i].join()
                    case _:
                        print('Arg "%s" isn\'t %s\'s arg!' % (cwa[1], cmd))     
            elif(cwa.__len__() == 4):
                match(cwa[1]):
                    case 'joinGuild':
                        if(currentUser == None):
                            print('User wasn\'t setted!')
                        else:
                            worker.Joiner(cwa[3],cwa[2],currentUser)
            elif(cwa.__len__() == 3):
                match(cwa[1]):
                    case 'set':
                        if(not worker.dbWorker.getById(cwa[2])):
                            currentUser = None
                            print('no users with this id in DB!')
                        else:
                            currentUser = cwa[2]
                    case 'guildProfile':
                        if(currentUser == None):
                            print('User wasn\'t setted!')
                        else:
                            userFull = worker.dbWorker.getById(currentUser)
                            worker.dbWorker.show(worker.GetGuildProfile(userFull['token'], cwa[2]))      
                    case _:
                        print('Arg "%s" isn\'t %s\'s arg!' % (cwa[1], cmd))        
            else:
                print('Incorrect args amount! Use "help"')
        case 'all':
            if(cwa.__len__() == 2):
                match(cwa[1]):
                    case 'update':
                        i = Threads.__len__()
                        Threads.append(Thread(target=worker.UpdateAll, args=(i,), daemon=True))
                        Threads[i].start()
                        Threads[i].join()   
                    case _:
                        print('Arg "%s" isn\'t %s\'s arg!' % (cwa[1], cmd))     
            elif(cwa.__len__() == 4):
                match(cwa[1]):
                    case 'joinGuild':
                        worker.Joiner(cwa[3],cwa[2],-1)
                    case _:
                        print('Arg "%s" isn\'t %s\'s arg!' % (cwa[1], cmd))
            else:
                print('Incorrect args amount! Use "help"')
        case 'function':
            if(cwa.__len__() == 3):
                match(cwa[1]):
                    case 'updateInfo':
                        print('Getting info by refresh token')
                        worker.UpdateInfo(cwa[2], 0)
                    case _:
                        print('Arg "%s" isn\'t %s\'s arg!' % (cwa[1], cmd))
            else:
                print('Incorrect args amount! Use "help"')
        case _:
            print('Command not found! use "help" for list of commands')