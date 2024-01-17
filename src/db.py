import os.path
import json


DBPath = 'resources/db.json'
errDBPath = 'resources/errdb.json'
DB = []

if(os.path.exists(DBPath)):
    with open(DBPath, 'r+') as db:
        try:
            DB = json.load(db)
            print("db was loaded!")
        except Exception as err:
            print("error while reading file!: ",err)
            db.close()
            exit()
        db.close()
else:
    print(f"{DBPath} doesn't exist, recreating file!")
    with open(DBPath, 'w') as db:
        json.dump(DB, db, indent=4)
        db.close()
#
if(os.path.exists(errDBPath)):
    with open(errDBPath, 'r+') as errdb:
        loadedJson = []
        loadedJson = json.load(errdb)
        if(loadedJson.__len__() > 0): print(f'Found profiles with errors in: {errDBPath}\n you can delete them!', )     
        errdb.close()
else:
    print(f"{errDBPath} doesn't exist, recreating file!")
    with open(errDBPath, 'w') as errdb:
        json.dump([], errdb, indent=4)
        errdb.close()

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
        dbSave()
    except Exception as err:
        print('Error in db module while removing! err: ',err)
def add(element):
    DB.append(element)
    dbSave()
def dbSave():
    with open(DBPath, 'w') as db:
        json.dump(DB, db, indent=4)
        db.close()
def errDB(element):
    errProfiles = []
    with open(errDBPath, 'r') as errdb:
        errProfiles = json.load(errdb)
    errProfiles.append(element)
    with open(errDBPath, 'w') as errdb:
        json.dump(errProfiles, errdb, indent=4)
        errdb.close()