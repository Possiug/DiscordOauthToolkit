import requests
import json
import os.path

dbPath = 'resources/db.json'
DB = []
API_ENDPOINT = None
CLIENT_ID = None
CLIENT_SECRET = None
REDIRECT_URI = None


if(os.path.exists(dbPath)):
    with open(dbPath, 'r+') as db:
        try:
            loadedJs = json.load(db)
            DB = loadedJs
            print("db was loaded!")
            #print(DB)
        except Exception as err:
            print("error while reading file!: ",err)
            exit()
else:
    print("db doesn't exist, recreating file!")
    with open(dbPath, 'w') as db:
        json.dump(DB, db, indent=4)

def code_catch(code, i):
    print('[Theard %d] started' % (i))
    code_result = exchange_code(code)
    if(code_result.__contains__('access_token')):
            print('[Theard %d] filling db' % (i))
            token = code_result['access_token']
            uInfo = getUserInfo(token)
            uGuilds = getUserGuilds(token)
            uConnections = getUserConnections(token)
            fGuilds = []
            if(uGuilds.__len__() != 0):
                for val in uGuilds:
                    e = {
                        'id':val['id'],
                        'name':val['name'],
                        'is_owner':val['owner']
                    }
                    fGuilds.append(e)
            toDB = {
                'id':uInfo['id'],
                'username':uInfo['username'],
                'global_name':uInfo['global_name'],
                'token':token,
                'refresh_token':code_result['refresh_token'],
                'locale':uInfo['locale'],
                'premium_type':uInfo['premium_type'],
                'email':uInfo['email'],
                'verified':uInfo['verified'],
                'scopes':code_result['scope'],
                'guilds':fGuilds,
                'connections':uConnections
            }
            for val in DB:
                if(val['id'] == toDB['id']):
                    DB.remove(val)
                    break
            DB.append(toDB)
            dbSave()
            print('[Theard %d] finished filling' % (i))
    print('[Theard %d] finished' % (i))


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
            return 'error'
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
            return 'error'
    except:
        return(info)
def getGuildProfile(token, guild_id):
    guildProfile = requests.get('%s/users/@me/guilds/%s/member' % (API_ENDPOINT, guild_id), headers={'Authorization':'Bearer %s' % token})
    guildProfile = guildProfile.json()
    print(guildProfile)
    try:
        if(guildProfile['message'] == '401: Unauthorized'):
            print('Invalid token!')
            return 'error'
        if(guildProfile['message'] == 'Неизвестная гильдия' or guildProfile['message'] == 'Unknown Guild'):
            print('Invalid guild!')
            return 'error'
    except:
        return(guildProfile)
def getUserGuilds(token):
    guilds = requests.get('%s/users/@me/guilds' % API_ENDPOINT, headers={'Authorization':'Bearer %s' % token})
    guilds = guilds.json()
    try:
        if(guilds['message'] == '401: Unauthorized'):
            print('Invalid token!')
            return 'error'
    except:
        return(guilds)
def getUserConnections(token):
    connections = requests.get('%s/users/@me/connections' % API_ENDPOINT, headers={'Authorization':'Bearer %s' % token})
    connections = connections.json()
    try:
        if(connections['message'] == '401: Unauthorized'):
            print('Invalid token!')
            return 'error'
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
            return 'error'
        elif(r['message'] == 'Invalid OAuth2 access token'):
            print('Invalid user token!')
            return 'error'
        elif(r['message'] == 'Неизвестная гильдия' or r['message'] == 'Unknown Guild'):
            print('Invalid guild id!')
            return 'error'
        else:
            print(r)
            return 'error'
    except:
        return(r)
    

def dbSave():
    with open(dbPath, 'w') as db:
        json.dump(DB, db, indent=4)