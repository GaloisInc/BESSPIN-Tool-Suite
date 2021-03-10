#!/usr/bin/python3
import json
from graphviz import Digraph
import os

parser_path = '../../lando' # TODO: put lando.sh in your path

filename = './events'
print(f"Parsing {filename}.lando!")
cmd = parser_path + '/lando.sh -f ' + filename + '.lando'
res = os.system(cmd)
if res != 0:
    print("{} failed".format(cmd))
    exit(1)
print(f"Parsing {filename}.lando OK!")

filename = './scenarios'
print(f"Parsing {filename}.lando!")
cmd = parser_path + '/lando.sh -f ' + filename + '.lando'
res = os.system(cmd)
if res != 0:
    print("{} failed".format(cmd))
    exit(1)
print(f"Parsing {filename}.lando OK!")

filename = './besspin_cyberphys'
print(f"Parsing {filename}.lando!")
cmd = parser_path + '/lando.sh -f ' + filename + '.lando'
res = os.system(cmd)
if res != 0:
    print("{} failed".format(cmd))
    exit(1)
print(f"Parsing {filename}.lando OK!")

# read file
with open(filename + '.json', 'r') as myfile:
    data=myfile.read()

# parse file
obj = json.loads(data)
dot = Digraph(comment='The Round Table')

for elem in obj['elements']:
    if elem['type'] == "com.galois.besspin.lando.ssl.ast.RawSystem":
        node_shape = 'box'
    elif elem['type'] == "com.galois.besspin.lando.ssl.ast.RawSubsystem":
        node_shape = 'ellipse'
    else:
        node_shape = 'hexagon'

    name = elem.get('abbrevName')
    if name is None:
        name = elem['name']
    dot.node(name, elem['name'],shape=node_shape)

for elem in obj['relationShips']['_containsRelations']:
    dot.edge(elem['parent'],elem['name'])
    
for elem in obj['relationShips']['_clientRelations']:
    dot.edge(elem['client'],elem['provider'],style="dashed")

for elem in obj['relationShips']['_inheritRelations']:
    dot.edge(elem['base'],elem['name'],style="dotted")

# Implicit relations?
#for elem in obj['relationShips']['_implicitContainsRelations']:
#    parent = [x for x in obj['elements'] if x['uid']==elem['parentUid']][0]
#    child = [x for x in obj['elements'] if x['uid']==elem['uid']][0]
#    dot.edge(parent['name'],child['name'])

dot.render(filename, view=True)
os.system('mv ' + filename + ' ' + filename + '.dot')
