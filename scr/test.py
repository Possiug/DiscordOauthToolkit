import json
try:
    with open('test.json', 'x+') as jsfile:
        to_json = {'users':["aaa"]}
    try:
       json.load(jsfile)['users']
    except Exception as err:
        print("bad", err)
        exit()
    jsfile.seek(0)
    json.dump(to_json, jsfile, indent=4)
except:
    pass
    print('all bad')
    #print(users)
    

'''
users.append('bbbbb')

a = ['1', '2', '3']
b = ['a', 'b', 'c']

for val in a:
    print(val,b[a.index(val)])

to_jsonEX = {'users':users}


with open('test.json') as jsfile:
    print(json.load(jsfile))
'''