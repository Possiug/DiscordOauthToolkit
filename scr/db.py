import os.path
import json


dbPath = 'resources/db.json'
DB = []

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

def GetParmFromAll(parm):
    toReturn = []
    try:
        for val in DB:
            toReturn.append(val[parm])
        return toReturn 
    except Exception as err:
        print('error while parm getting!')
        return False

def getByName(name):
    for val in DB:
        if(val['username'] == name):
            return val
    return False        
def getById(id):
    for val in DB:
        if(val['id'] == id):
            return val
    return False   

def checkRepeat(check):
    for val in DB:
        if(val['id'] == check):
            return val
    return False
def show(element):
    print(json.dumps(element, indent=2))
def delete(element):
    try:
        DB.remove(element)
    except Exception as err:
        print('Error in db module while removing! err: ',err)
def add(element):
    DB.append(element)
    dbSave()
def dbSave():
    with open(dbPath, 'w') as db:
        json.dump(DB, db, indent=4)
