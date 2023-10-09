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
    print('config file doesn\'t exist! creating you have to enter some values!')
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
    r = r.json()
    try:
        if(r['error'] == 'invalid_grant'):
            print('error while exchanging codes: ', r['error_description'])
    except:
        return r

def refresh_token(refresh_token):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)
    r = r.json()
    try:
        if(r['error'] == 'invalid_grant'):
            print('error while refreshing token: invalid refresh_token!')
    except:
        return r


def getUserInfo(token):
    info = requests.get('%s/users/@me' % API_ENDPOINT, headers={'Authorization':'Bearer %s' % token})
    info = info.json()
    try:
        if(info['message'] == '401: Unauthorized'):
            print('Invalid token!')
    except:
        return(info)

def getGuildProfile(token, guild_id):
    guildProfile = requests.get('%s/users/@me/guilds/%s/member' % (API_ENDPOINT, guild_id), headers={'Authorization':'Bearer %s' % token})
    guildProfile = guildProfile.json()
    print(guildProfile)
    try:
        if(guildProfile['message'] == '401: Unauthorized'):
            print('Invalid token!')
        if(guildProfile['message'] == 'Неизвестная гильдия' or guildProfile['message'] == 'Unknown Guild'):
            print('Invalid guild!')
    except:
        return(guildProfile)

def getUserGuilds(token):
    guilds = requests.get('%s/users/@me/guilds' % API_ENDPOINT, headers={'Authorization':'Bearer %s' % token})
    guilds = guilds.json()
    try:
        if(guilds['message'] == '401: Unauthorized'):
            print('Invalid token!')
    except:
        return(guilds)
    
def getUserConnections(token):
    connections = requests.get('%s/users/@me/connections' % API_ENDPOINT, headers={'Authorization':'Bearer %s' % token})
    connections = connections.json()
    try:
        if(connections['message'] == '401: Unauthorized'):
            print('Invalid token!')
    except:
        return(connections)

def joinGuild(token, user_id, bot_token, guild_id):
    data = {'access_token': token}
    data = json.dumps(data)
    headers = {
        'Authorization':'Bot %s' % bot_token,
        'Content-Type': "application/json",
    }
    r = requests.put('%s/guilds/%s/members/%s' % (API_ENDPOINT, guild_id, user_id), data=data, headers=headers)
    r = r.json()
    try:
        if(r['message'] == '401: Unauthorized'):
            print('Invalid bot token!')
        elif(r['message'] == 'Invalid OAuth2 access token'):
            print('Invalid user token!')
        elif(r['message'] == 'Неизвестная гильдия' or r['message'] == 'Unknown Guild'):
            print('Invalid guild id!')
        else:
            print(r)
    except:
        return(r)

if __name__ == "__main__":
    app.run(debug = False, port=PORT,host=LOCAL_IP)