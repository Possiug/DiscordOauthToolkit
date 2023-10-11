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
        Add(val, i)


def Add(refresh_tokens, i):
    refresh_tokens = refresh_tokens.split(',')
    for refresh_token in refresh_tokens:
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
            print('[JoinGuild] Invalid bot token!')
            return 'error'
        elif(r['message'] == 'Invalid OAuth2 access token'):
            print('[JoinGuild] Invalid user token!')
            return 'error'
        elif(r['message'] == 'Неизвестная гильдия' or r['message'] == 'Unknown Guild'):
            print('[JoinGuild] Invalid guild id!')
            return 'error'
        elif(r['message'] == 'Missing Permissions'):
            print('[JoinGuild] Bot isn\' on server!')
            return 'error'
        else:
            print('[JoinGuild]' + r)
            return 'error'
    except:
        return r

def GetUsers():
    output = []
    print('User amoun: %s' % dbWorker.DB.__len__())
    for e in dbWorker.DB:
        toO = {
            'username': e['username'],
            'global_name': e['global_name'],
            'id': e['id']
        }
        output.append(toO)
    dbWorker.show(output)
def Update(user_ids):
    if(user_ids == '-1'):
        refresh_tokens = dbWorker.GetParmFromAll('refresh_token')
        for refresh in refresh_tokens:
            Add(refresh, 0)
            time.sleep(1.0)
        return
    user_ids = user_ids.split(',')
    refresh_tokens = []
    for id in user_ids:
        user = dbWorker.getById(id)
        if(not user):
            print('No user with given id[%s] found in db!' % (id))
            continue
        Add(user['refresh_token'], 0)
        time.sleep(1.0)
def Joiner(bot_token, guild_ids, user_ids):
    guild_ids = guild_ids.split(',')
    user_ids = user_ids.split(',')
    if(user_ids == -1):
        for val in dbWorker.DB:
            time.sleep(0.5)
            for id in guild_ids:
                time.sleep(0.5)
                result = JoinGuild(val['token'], val['id'], bot_token, id)
                if(result == 'error'):
                    print('error while adding user[%s] to guild[%s]!' % (val['id'], id))
                else:
                    print('added user[%s] to a guild[%s]' % (val['id'], id))
    else:
        for user in user_ids:
            time.sleep(0.5)
            for id in guild_ids:
                time.sleep(0.5)
                result = JoinGuild(dbWorker.getById(user)['token'], user, bot_token, id)
                if(result == 'error'):
                    print('error while adding user[%s] to guild[%s]!' % (user, id))
                else:
                    print('added user[%s] to a guild[%s]' % (user, id))

