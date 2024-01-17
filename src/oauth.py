import requests
import json
import time
import db as dbWorker

API_ENDPOINT = None
CLIENT_ID = None
CLIENT_SECRET = None
REDIRECT_URI = None
BOT_TOKEN = None

debug = True
output = True

def Code_catch(code, i):
    if(debug):print('\n[Theard %d] started' % (i))
    code_result = Exchange_code(code)
    if(code_result.__contains__('access_token')):
            if(debug):print('\n[Theard %d] filling db' % (i))
            data = DataGetter(code_result)
            repeat = dbWorker.checkRepeat(data['id'])
            if(repeat):
                dbWorker.delete(repeat)
            dbWorker.add(data)
            if(debug):print('\n[Theard %d] finished filling' % (i))
    if(debug):print('\n[Theard %d] finished' % (i))


def Add(refresh_tokens, id = 'from_CLI', i = 0):
    refresh_tokens = refresh_tokens.split(',')
    for refresh_token in refresh_tokens:
        code_result = Refresh_token(refresh_token)
        if(code_result.__contains__('access_token')):
            if(debug):print('\n[Theard %d] filling db! User[%s]' % (i, id))
            toDB = DataGetter(code_result)
            repeat = dbWorker.checkRepeat(toDB['id'])
            if(repeat):
                dbWorker.delete(repeat)
            dbWorker.add(toDB)
            if(debug):print('\n[Theard %d] finished filling! User[%s]' % (i, id))
        else:
            if(output):print('\n[Theard %d] error while getting user info ftom discord! DB profile dumped to errDB.json' % (i))
            dbWorker.errDB(dbWorker.getById(toDB['id']))
            dbWorker.delete(dbWorker.getById(toDB['id']))
        toDB = None
    if(debug):print('\n[Theard %d] finished' % (i))

def DataGetter(code_result):
    token = code_result['access_token']
    uInfo = GetUserInfo(token)
    uGuilds = GetUserGuilds(token)  
    uGuilds = [] if uGuilds == 'error' else uGuilds
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
    info = {
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
    return info

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
            if(output):print('error while exchanging codes: ', r['error_description'])
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
            if(output):print('error while refreshing token: invalid refresh_token!')
        return 'ERROR'
    except:
        if(r.__contains__('refresh_token')):
            if(output):print(r['refresh_token'])
        else:
            print('SMT WRONG IN Func Refresh_token')
        return r
def GetUserInfo(token):
    info = requests.get('%s/users/@me' % API_ENDPOINT, headers={'Authorization':'Bearer %s' % token})
    info = info.json()
    try:
        if(info['message'] == '401: Unauthorized'):
            if(output):print('Invalid token!')
            return 'error'
    except:
        return(info)
def GetGuildProfile(token, guild_id):
    guildProfile = requests.get('%s/users/@me/guilds/%s/member' % (API_ENDPOINT, guild_id), headers={'Authorization':'Bearer %s' % token})
    guildProfile = guildProfile.json()
    try:
        if(guildProfile['message'] == '401: Unauthorized'):
            if(output):print('Invalid token!')
            return 'error'
        if(guildProfile['message'] == 'Неизвестная гильдия' or guildProfile['message'] == 'Unknown Guild'):
            if(output):print('Invalid guild!')
            return 'error'
    except:
        return(guildProfile)
def GetUserGuilds(token):
    guilds = requests.get('%s/users/@me/guilds' % API_ENDPOINT, headers={'Authorization':'Bearer %s' % token})
    guilds = guilds.json()
    try:
        if(guilds['message'] == '401: Unauthorized'):
            if(output):print('Invalid token!')
            return 'error'
        if(guilds['code'] == 40002):
            if(output):print('Inverified account!')
            return 'error'
    except:
        return(guilds)
def GetUserConnections(token):
    connections = requests.get('%s/users/@me/connections' % API_ENDPOINT, headers={'Authorization':'Bearer %s' % token})
    connections = connections.json()
    try:
        if(connections['message'] == '401: Unauthorized'):
            if(output):print('Invalid token!')
            return 'error'
    except:
        return(connections)
def JoinGuild(token, user_id, guild_id):
    data = {'access_token': token}
    data = json.dumps(data)
    headers = {
        'Authorization':'Bot %s' % BOT_TOKEN,
        'Content-Type': "application/json",
    }
    r = requests.put('%s/guilds/%s/members/%s' % (API_ENDPOINT, guild_id, user_id), data=data, headers=headers)
    try:
        r = r.json()
        if(r['message'] == '401: Unauthorized'):
            if(output):print('[JoinGuild] Invalid bot token!')
            return 'error'
        elif(r['message'] == 'Invalid OAuth2 access token'):
            if(output):print('[JoinGuild] Invalid user token!')
            return 'error'
        elif(r['message'] == 'Неизвестная гильдия' or r['message'] == 'Unknown Guild'):
            if(output):print('[JoinGuild] Invalid guild id!')
            return 'error'
        elif(r['message'] == 'Missing Permissions'):
            if(output):print('[JoinGuild] Bot isn\' on server!')
            return 'error'
        else:
            if(output):print('[JoinGuild]' + r)
            return 'error'
    except:
        return r

def GetUsers():
    output = []
    if(output):print('User amount: %s' % dbWorker.DB.__len__())
    for e in dbWorker.DB:
        print(f'\t{e.get('username')}[{e.get('id')}]\tGlobalName: {e.get('global_name')}\tguilds: {e.get('guilds').__len__()}\temail[verified:{e.get('verified')}]: {e.get('email')}\n')
def Update(user_ids):
    if(user_ids == '-1'):
        refresh_tokens = dbWorker.GetParmFromAll('refresh_token')
        users_ids = dbWorker.GetParmFromAll('id')
        for i in range(0, refresh_tokens.__len__()):
            Add(refresh_tokens[i],users_ids[i], 0)
            time.sleep(1.0)
        return
    user_ids = user_ids.split(',')
    refresh_tokens = []
    for id in user_ids:
        user = dbWorker.getById(id)
        if(not user):
            if(output):print('No user with given id[%s] found in db!' % (id))
            continue
        Add(user['refresh_token'], id, 0)
        time.sleep(1.0)
def Joiner(guild_ids, user_ids):
    guild_ids = guild_ids.split(',')
    if(user_ids == "-1"):
        for val in dbWorker.DB:
            time.sleep(0.5)
            for id in guild_ids:
                time.sleep(0.5)
                result = JoinGuild(val['token'], val['id'], id)
                if(result == 'error'):
                    if(output):print('error while adding user[%s] to guild[%s]!' % (val['id'], id))
                else:
                    if(output):print('added user[%s] to a guild[%s]' % (val['id'], id))
    else:
        user_ids = user_ids.split(',')
        for user in user_ids:
            time.sleep(0.5)
            for id in guild_ids:
                time.sleep(0.5)
                try:
                    result = JoinGuild(dbWorker.getById(user)['token'], user, id)
                    if(result == 'error'):
                        if(output):print('error while adding user[%s] to guild[%s]!' % (user, id))
                    else:
                        if(output):print('added user[%s] to a guild[%s]' % (user, id))
                except Exception as err:
                    print('error in Joiner()',err)
