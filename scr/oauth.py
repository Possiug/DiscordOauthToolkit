import requests
import json

API_ENDPOINT = None
CLIENT_ID = None
CLIENT_SECRET = None
PORT = None
URL_ARGS =None
REDIRECT_URI = None


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
async def refresh_token(refresh_token):
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
async def getUserInfo(token):
    info = requests.get('%s/users/@me' % API_ENDPOINT, headers={'Authorization':'Bearer %s' % token})
    info = info.json()
    try:
        if(info['message'] == '401: Unauthorized'):
            print('Invalid token!')
            return 'error'
    except:
        return(info)
async def getGuildProfile(token, guild_id):
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
async def getUserGuilds(token):
    guilds = requests.get('%s/users/@me/guilds' % API_ENDPOINT, headers={'Authorization':'Bearer %s' % token})
    guilds = guilds.json()
    try:
        if(guilds['message'] == '401: Unauthorized'):
            print('Invalid token!')
            return 'error'
    except:
        return(guilds)
async def getUserConnections(token):
    connections = requests.get('%s/users/@me/connections' % API_ENDPOINT, headers={'Authorization':'Bearer %s' % token})
    connections = connections.json()
    try:
        if(connections['message'] == '401: Unauthorized'):
            print('Invalid token!')
            return 'error'
    except:
        return(connections)
async def joinGuild(token, user_id, bot_token, guild_id):
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