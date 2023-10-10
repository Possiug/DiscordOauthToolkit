import requests
import json
import time
import db as dbWorker

API_ENDPOINT = None
CLIENT_ID = None
CLIENT_SECRET = None
REDIRECT_URI = None

debug = True

def Code_catch(code, i):
    if(debug):print('\n[Theard %d] started' % (i))
    code_result = Exchange_code(code)
    if(code_result.__contains__('access_token')):
            if(debug):print('\n[Theard %d] filling db' % (i))
            toDB = DataGetter(code_result)
            repeat = dbWorker.checkRepeat(toDB['id'])
            if(repeat):
                dbWorker.delete(repeat)
            dbWorker.add(toDB)
            if(debug):print('\n[Theard %d] finished filling' % (i))
    if(debug):print('\n[Theard %d] finished' % (i))

def UpdateAll(i):
    for val in dbWorker.GetParmFromAll('refresh_token'):
        time.sleep(1.0)
        UpdateInfo(val, i)


def UpdateInfo(refresh_token, i):
    code_result = Refresh_token(refresh_token)
    if(code_result.__contains__('access_token')):
            if(debug):print('\n[Theard %d] filling db' % (i))
            toDB = DataGetter(code_result)
            repeat = dbWorker.checkRepeat(toDB['id'])
            if(repeat):
                dbWorker.delete(repeat)
            dbWorker.add(toDB)
            if(debug):print('\n[Theard %d] finished filling' % (i))
    if(debug):print('\n[Theard %d] finished' % (i))

def DataGetter(code_result):
    token = code_result['access_token']
    uInfo = GetUserInfo(token)
    uGuilds = GetUserGuilds(token)
    uConnections = GetUserConnections(token)
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
    return toDB

def Exchange_code(code):
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
def Refresh_token(refresh_token):
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
        return 'ERROR'
    except:
        return r
def GetUserInfo(token):
    info = requests.get('%s/users/@me' % API_ENDPOINT, headers={'Authorization':'Bearer %s' % token})
    info = info.json()
    try:
        if(info['message'] == '401: Unauthorized'):
            print('Invalid token!')
            return 'error'
    except:
        return(info)
def GetGuildProfile(token, guild_id):
    guildProfile = requests.get('%s/users/@me/guilds/%s/member' % (API_ENDPOINT, guild_id), headers={'Authorization':'Bearer %s' % token})
    guildProfile = guildProfile.json()
    try:
        if(guildProfile['message'] == '401: Unauthorized'):
            print('Invalid token!')
            return 'error'
        if(guildProfile['message'] == 'Неизвестная гильдия' or guildProfile['message'] == 'Unknown Guild'):
            print('Invalid guild!')
            return 'error'
    except:
        return(guildProfile)
def GetUserGuilds(token):
    guilds = requests.get('%s/users/@me/guilds' % API_ENDPOINT, headers={'Authorization':'Bearer %s' % token})
    guilds = guilds.json()
    try:
        if(guilds['message'] == '401: Unauthorized'):
            print('Invalid token!')
            return 'error'
    except:
        return(guilds)
def GetUserConnections(token):
    connections = requests.get('%s/users/@me/connections' % API_ENDPOINT, headers={'Authorization':'Bearer %s' % token})
    connections = connections.json()
    try:
        if(connections['message'] == '401: Unauthorized'):
            print('Invalid token!')
            return 'error'
    except:
        return(connections)
def JoinGuild(token, user_id, bot_token, guild_id):
    data = {'access_token': token}
    data = json.dumps(data)
    headers = {
        'Authorization':'Bot %s' % bot_token,
        'Content-Type': "application/json",
    }
    r = requests.put('%s/guilds/%s/members/%s' % (API_ENDPOINT, guild_id, user_id), data=data, headers=headers)
    try:
        r = r.json()
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
        return 'error'

def AllJoin(bot_token,guild_id,i):
    for val in dbWorker.DB:
        time.sleep(1.0)
        JoinGuild(val['token'], val['id'], bot_token, guild_id)
