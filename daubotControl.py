from daubotIO import press,click,typeText,doubleClick,moveTo,locate,locateCenter,getDofusWindow,IOpause,hotkey
from time import time, sleep
from daubotImg import getRegion,getCoord,inHavreSac,hasChasse,getFlag,wordDiff,inFight,parseLocation
from random import randint

def clickOnZaap(window):
    click(600,370, window)
    if not attenteForImg("zaapMenu.jpg", window, 0.9, 10):
        raise NameError("Stuck trying to zaap")


def enterCouloirMalle(window, timeout = 10):
    click(941,421,window)
    start = time()
    while getRegion(parseLocation(window), window) != "La Malle aux Trésors":
        if time()-start > timeout:
            raise NameError("Can't enter malle hallway")

def enterSalleMalle(window):
    click(1433,480,window)
    if not attenteForImg("inMalle.jpg", window, 0.8, 10):
        raise NameError("Can't enter malle hall")

def takeChasse(window):
    click(1046,496,window)
    if not attenteForImg("menuChasseLvl.jpg", window, timeout = 10):
        raise NameError("Stuck strying to take chasse")
    click(1200,530,window)

def zaapTo(coord, destination, window):
    clickToEnterZaapDestination(window)
    typeText(destination, window)
    validateDestination(coord, window)

def waitForCoordChange(coord, timeout, window):
    g = getCoord(parseLocation(window), window)
    start = time()
    while coord == g:
        g = getCoord(parseLocation(window), window)
        if time()-start > timeout:
            return False
    print("Now in:", g)
    return True

def validateDestination(coord, window):
    doubleClick(937,319, window)
    waitForCoordChange(coord, 10, window)

def enterChat(window):
    click(500,1020,window)

def leaveChat(window):
    press('escape',window)
    clearMouse(window)

def clearchat(window):
    typeText("/clear", window)
    press("enter", window)

def clickToEnterZaapDestination(window):
    click(1109,236, window)

def attenteForImg(img, window, confidence = 0.7, timeout = float('inf')):
    r = None
    start = time()
    while r is None:
        r = locate(img,confidence,window)
        if time()-start > timeout:
            return False
    return True

def travel(coord,x,y,window):
    if (x,y) == coord:
        return
    enterChat(window)
    clearchat(window)
    text = "/travel "+str(x)+" "+str(y)
    typeText(text, window)
    press("enter", window)
    attenteForImg("travelPending.jpg", window, timeout = 10)
    press("enter", window)
    leaveChat(window)
    if travelImpossible(window):
        raise NameError("Can't travel")
    attenteForImg("travelFinished.JPG", window)
    print("travelled to:",x,y)

def goDir(location, direction, window):
    coord = getCoord(location, window)
    
    if direction == "top":
        exceptions = {}
        if coord in exceptions.keys():
            click(*exceptions[coord],window)
        else:
            click(1000,35,window)
            
            
            
    elif direction == "left":
        exceptions = {(-1,8):(754,500),(-5,25):(340,357),(-19,34):(754,500)}
        if coord in exceptions.keys():
            click(*exceptions[coord],window)
        else:
            click(340,500,window)
            
            
            
    elif direction == "right":
        exceptions = {(7,-27):(1576,100),(-2,8):(1200,325),(-6,25):(1574,357),(-23,-1):(1500,500)}
        if coord in exceptions.keys():
            click(*exceptions[coord],window)
        else:
            click(1576,500,window)
            
            
            
    elif direction == "bottom":
        exceptions = {}
        if coord in exceptions.keys():
            click(*exceptions[coord],window)
        else:
            click(1000,909,window)
            
            
            
    else:
        raise NameError("Can't go direction:", direction)
    res = waitForCoordChange(coord, 20, window)
    if not res:
        print("STUCK in:",getCoord(parseLocation(window), window))
    return res

def enterHavreSac(loc, window):
    if inHavreSac(loc, window):
        return
    enterChat(window)
    clearchat(window)
    leaveChat(window)
    press('h', window)
    while not inHavreSac(loc, window):
        loc = parseLocation(window)
        if locate("havreStuck.JPG",0.7,window):
            direction = ["top","bottom","left","right"][randint(0,3)]
            goDir(direction, window)
            return enterHavreSac(window)

def attenteChasse(window):
    while not hasChasse(window):
        pass

def sortirHavreSac(window):
    if not inHavreSac(window):
        return
    press('h', window)
    while inHavreSac(window):
        pass
    return

def waitForCoord(coord, timeout, window):
    start = time()
    while coord != getCoord(parseLocation(window), window):
        if time()-start > timeout:
            return False
    return True

def validateEtape(window):
    left,top = locateCenter("validate.jpg",0.7,window)
    click(left , top , window)
    clearMouse(window)

def clearMouse(window):
    loc = locateCenter("escape.jpg", 0.7, window)
    x,y = loc
    moveTo(x,y, window)
    moveTo(x + 1,y, window)

def validateIndice(window):
    x,y = getFlag(window)
    click(x+15,y+15,window)
    clearMouse(window)

def clickTranspo(window):
    click(1024,638,window)
    attenteForImg("transpo.jpg",window,0.8,10)

def bestFrigostRegion(region):
    regions = ["ile de frigost (Berceau d'Alma)","ile de frigost (Larmes d'Ouronigride)","ile de frigost (Crevasse Perge)","ile de frigost (Forêt pétrifiée)"]
    minScore = float('inf')
    bestMatch = None
    for target in regions:
        diff = wordDiff(target, region)
        if diff < minScore:
            minScore = diff
            bestMatch = target
    return bestMatch

def takeTransporteur(depRegion, window):
    clickTranspo(window)
    region = bestFrigostRegion(depRegion)
    dictt = {"ile de frigost (Berceau d'Alma)":(941,669),"ile de frigost (Larmes d'Ouronigride)":(941,695),"ile de frigost (Crevasse Perge)":(941,719),"ile de frigost (Forêt pétrifiée)":(941,745)}
    click(*dictt[region], window)
    sleep(10)

def travelImpossible(window):
    return False


def abandon(startTime, window):
    print("abandon\n\n\n\n\n")
    while time() - startTime < 600:
        sleep(IOpause)
    left,top = locateCenter("abandon.JPG",0.7,window)
    click(left , top , window)
    attenteForImg("attention.jpg", window, timeout = 10)
    left,top = locateCenter("ok.JPG",0.7,window)
    click(left , top , window)
    while hasChasse(window):
        pass

def lanceCombat(window):
    loc = locateCenter("combattre.JPG",0.7,window)
    if loc:
        click(*loc, window)
    while not inFight(window):
        sleep(IOpause)



if __name__ == "__main__":
    window = getDofusWindow("Mr-Maron")
    #clickTranspo(window)
    goDir("right", window)
