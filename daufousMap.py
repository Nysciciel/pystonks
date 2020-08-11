import requests
import json
from daubotData import translator, zaaps

def getIndices(x, y, direction, world = 0):
    site = "https://dofus-map.com/huntTool/getData.php?x="+str(x)+"&y="+str(y)
    site += "&direction="+direction+"&world="+str(world)+"&language=fr"
    r = requests.post(site)
    return json.loads(r.text)["hints"]

def getIndiceDist(indice, x, y, direction, world = 0):
    hints = getIndices(x, y, direction, world)
    index = list(translator.keys())[list(translator.values()).index(indice)]
    for dic in hints:
        if str(dic['n']) == index:
            return dic['d']
    return None

def getIndiceCoord(indice, x, y, direction, world = 0):
    hints = getIndices(x, y, direction, world)
    index = list(translator.keys())[list(translator.values()).index(indice)]
    for dic in hints:
        if str(dic['n']) == index:
            return (dic['x'],dic['y'])
    return None

def getIndiceAnswers(x, y, direction, world = 0):
    hints = getIndices(x, y, direction, world)
    res = []
    for dic in hints:
        res.append(translator[str(dic['n'])])
    return res

def zaapName(x,y):
    return zaaps[(x,y)]


def closestZaapCoord(x,y):
    minDist = float('inf')
    minCoord = None
    for coord in zaaps.keys():
        dist = abs(x-coord[0]) + abs(y-coord[1])
        if dist < minDist:
            minCoord = coord
            minDist = dist
    return minCoord
