import json

with open('test.json', 'r') as jsfile:
    test = json.load(jsfile)
    print(test)
    

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