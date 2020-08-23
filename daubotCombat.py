from daubotControl import lanceCombat,leaveChat,clearMouse,clearInterface
from daubotImg import chasseLegendaire,inFight,victoire,myTurn,waitForEndScreen,placementPhase,initializeCharIndex,readText,isolateInImg,getEntityDelta,defaite,chassePortail
from daubotIO import getDofusWindow,press,screenshot,locateCenter,click
from time import sleep
from random import randint
import cv2
import numpy as np

tileConstant = 87
region = (340,31,1600,890)

def Combat(window):
    history = set()
    while True:
        img = screenshot(None, window)
        charIndex = -1
        print("combat.")
        if chasseLegendaire(window):
            print("chasse legendaire terminee")
            return False
        if chassePortail(window):
            print("chasse portail terminee")
            return False
        lanceCombat(window)
        iniCreature(window)
        while inFight(window):
            sleep(1)
            print("trying to play")
            if placementPhase(window):
                print("placements")
                playPlacements(window)
            if charIndex == -1:
                charIndex = initializeCharIndex(window)
                print("my turn index:",charIndex)
            elif myTurn(charIndex, window):
                print("my turn")
                turn = playTurn(window, history)
                if not(turn is None):
                    history.add(turn)
                while myTurn(charIndex, window):
                    sleep(1)
                    img = screenshot(None, window)
                    if getPA(img) == 11 and getPM(img) == 6:
                        break
                    if np.all(screenshot((850,1015,851,1016),window) == [[[0, 200, 252]]]):
                        charIndex = initializeCharIndex(window)
                        break
            if np.all(screenshot((850,1015,851,1016),window) == [[[0, 200, 252]]]):
                charIndex = initializeCharIndex(window)
        print("fight ended?")
        waitForEndScreen(window)
        if victoire(window):
            print("victoire")
            clearInterface(window)
            sleep(5)
            return True
        if defaite(window):
            print("defaite")
            clearInterface(window)
            sleep(5)
            return False
        clearInterface(window)
        return False

def passTurn(window):
    press('f1',window)



def addrandommargin(inputImg):
    img = inputImg.copy()
    marginsInterval = (5,7)
    margins = [randint(*marginsInterval) for i in range(4)]
    img = cv2.copyMakeBorder(img, *margins, cv2.BORDER_CONSTANT)
    return img

def convertibleToInt(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def suppressMargin(im):
    Xmin = float('inf')
    Xmax = -float('inf')
    Ymin = float('inf')
    Ymax = -float('inf')

    for x in range(im.shape[0]):
        for y in range(im.shape[1]):
            pxl = im[x,y]
            if np.all(pxl == 255):
                if x < Xmin:
                    Xmin = x
                if x > Xmax:
                    Xmax = x
                if y < Ymin:
                    Ymin = y
                if y > Ymax:
                    Ymax = y
    res = im[Xmin:Xmax+1, Ymin:Ymax+1]
    return res

def numberScore(img, dirr):
    res = cv2.matchTemplate(cv2.imread("number"+dirr+".JPG"), img, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    return min_val

def bestMatchInNumbers(img):
    minScore = float('inf')
    bestdir = None
    for dirr in ["0","1","2","3","4","5","6","7","8","9","10","11","12","13"]:
        s = numberScore(img, dirr)
        if s < minScore:
            minScore=s
            bestdir = dirr
    return int(bestdir)

def findOrigin(img):
    ref = cv2.imread("origin.png")
    res = cv2.matchTemplate(ref, img, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    min_loc = list(min_loc)
    min_loc[0] += ref.shape[1]
    min_loc[1] += ref.shape[0]
    return tuple(min_loc)

def findRealOrigin(screen):
    loc = findOrigin(screen)
    Xorigin, Yorigin = loc


    u = (Yorigin*2 + Xorigin)/tileConstant
    v = (Yorigin*2 + -Xorigin)/tileConstant

    u += 1/2
    v += 1/2

    x = int(round((u-v)*tileConstant/2))
    y = int(round((u+v)*tileConstant/4))

    return (x,y)

def findAllies(window, filtering = True):
    if filtering:
        mask = getEntityDelta(window, region)
        screen = screenshot(region, window)
        img = cv2.bitwise_and(screen,screen,mask = mask)
        cv2.imwrite("debug\\findAllies.jpg",img)
    else:
        img = screenshot(region, window)
    red = np.where(img[:,:,2] > 170, True, False)
    green = np.where(img[:,:,1] < 60, True, False)
    blue = np.where(img[:,:,0] < 60, True, False)
    res = np.where(red*blue*green)
    res = (res[0], res[1])
    return res

def findEnemies(window, filtering = True):
    if filtering:
        mask = getEntityDelta(window, region)
        screen = screenshot(region, window)
        img = cv2.bitwise_and(screen,screen,mask = mask)
        cv2.imwrite("debug\\findEnemies.jpg",img)
    else:
        img = screenshot(region, window)
    red = np.where(img[:,:,0] > 170, True, False)
    green = np.where(img[:,:,1] < 60, True, False)
    blue = np.where(img[:,:,2] < 60, True, False)
    res = np.where(red*blue*green)
    res = (res[0], res[1])
    return res


def findRealAllies(window,filtering = True):
    clearMouse(window)

    screen = screenshot(region, window)
    origin = findOrigin(screen)
    Xorigin, Yorigin = origin
    potentialAllies = findAllies(window,filtering)


    u0 = (Yorigin*2 + Xorigin)/tileConstant
    v0 = (Yorigin*2 + -Xorigin)/tileConstant


    screen = drawCross(screen, *findRealOrigin(screen), [0,255,0])

    Allies = []
    for i in range(len(potentialAllies[0])):
        y = potentialAllies[0][i]
        x = potentialAllies[1][i]

        screen[y,x] = [0,255,255]

        tempU = (x + y*2)/tileConstant - u0
        tempV = (-x + y*2)/tileConstant - v0
        if int(tempU) == tempU or int(tempV) == tempV:
            continue

        u = round(tempU -1/2) + u0 + 1/2
        v = round(tempV -1/2) + v0 + 1/2


        x = int(round((u-v)*tileConstant/2))
        y = int(round((u+v)*tileConstant/4))



        Allies.append((x,y))
    realAllies = set(Allies)

    for elem in realAllies:
        x,y = elem
        screen = drawCross(screen, x, y, [255,255,0])
    cv2.imwrite("debug\\allies.png", screen)
    return list(realAllies)

def findRealEnemies(window,filtering = True):
    clearMouse(window)

    screen = screenshot(region, window)
    origin = findOrigin(screen)
    Xorigin, Yorigin = origin
    potentialAllies = findEnemies(window,filtering)


    u0 = (Yorigin*2 + Xorigin)/tileConstant
    v0 = (Yorigin*2 + -Xorigin)/tileConstant


    screen = drawCross(screen, *findRealOrigin(screen), [0,255,0])

    Allies = []
    for i in range(len(potentialAllies[0])):
        y = potentialAllies[0][i]
        x = potentialAllies[1][i]

        screen[y,x] = [0,255,255]

        tempU = (x + y*2)/tileConstant - u0
        tempV = (-x + y*2)/tileConstant - v0
        if int(tempU) == tempU or int(tempV) == tempV:
            continue

        u = round(tempU -1/2) + u0 + 1/2
        v = round(tempV -1/2) + v0 + 1/2


        x = int(round((u-v)*tileConstant/2))
        y = int(round((u+v)*tileConstant/4))



        Allies.append((x,y))
    realAllies = set(Allies)

    for elem in realAllies:
        x,y = elem
        screen = drawCross(screen, x, y, [255,255,0])
    cv2.imwrite("debug\\enemies.png", screen)
    return list(realAllies)



def drawCross(img, x,y,color):
    for i in range(0,5):
        try:
            img[y+i,x+i] = color
            img[y+i,x-i] = color
            img[y-i,x+i] = color
            img[y-i,x-i] = color
        except IndexError:
            pass
    return img

def ToDofCoord(x,y,xOrigin, yOrigin):
    u = (y*2 + x)/tileConstant
    v = (y*2 + -x)/tileConstant

    u0 = (yOrigin*2 + xOrigin)/tileConstant
    v0 = (yOrigin*2 + -xOrigin)/tileConstant

    return (int(round(u-u0)),int(round(v-v0)))

def ToRealCoord(u,v,xOrigin, yOrigin):
    u0 = (yOrigin*2 + xOrigin)/tileConstant
    v0 = (yOrigin*2 + -xOrigin)/tileConstant
    u += u0
    v += v0
    x = int(round((u-v)*tileConstant/2))
    y = int(round((u+v)*tileConstant/4))
    return (x,y)

def findState(b,g,r):
    statesConversion = {((142,134),94):"walkable", ((150,142),103):"walkable", ((0,0),0):"void", ((90,125),62):"accessible", ((85,121),56):"accessible", ((221,34),0):"accessible"}

    if not(((r,g),b) in statesConversion.keys()):
        return "stop"
    return statesConversion[((r,g),b)]

def CaseState(u,v,x0,y0,screen):
    try:
        x,y = ToRealCoord(u, v, x0, y0)
        if x <0:
            return None
        if y<0:
            return None
        res = findState(*screen[y-3,x])
        return res
    except:
        return None

def getPA(img):

    paScreen = img[994:1030,740:775]
    cv2.imwrite('debug\\parsePA1.jpg', paScreen)
    screen = addrandommargin(suppressMargin(isolateInImg(paScreen, [255,255,255], epsilon = 140)))
    pa = bestMatchInNumbers(screen)
    return pa

def getPM(img):

    pmScreen = img[997:1022,790:820]
    cv2.imwrite('debug\\parsePM1.jpg', pmScreen)
    screen = addrandommargin(suppressMargin(isolateInImg(pmScreen, [255,255,255], epsilon = 140)))
    pm = bestMatchInNumbers(screen)
    return pm

def uLign(u, origin, img, v0):
    vMin = v0
    vMax = v0
    while CaseState(u,vMin - 1, *origin, img) != None:
        vMin -= 1
    while CaseState(u,vMax + 1, *origin, img) != None:
        vMax += 1
    return np.array([CaseState(u,v, *origin, img) for v in range(vMin, vMax + 1)])

def vLign(v, origin, img, u0):
    uMin = u0
    uMax = u0
    while CaseState(uMin - 1,v, *origin, img) != None:
        uMin -= 1
    while CaseState(uMax + 1,v, *origin, img) != None:
        uMax += 1
    return np.array([CaseState(u,v, *origin, img) for u in range(uMin, uMax + 1)])

def isLignEmpty(lign):
    void = lign == "void"
    stop = lign == "stop"
    none = lign == None
    return np.all(void + stop + none)

def findRealBoundaries(origin, img):
    boundaries = findBoundaries(origin, img)
    exBoundaries = None
    while boundaries != exBoundaries:
        exBoundaries = boundaries
        boundaries = list(boundaries)
        for u in range(exBoundaries[0], exBoundaries[1] + 1,6):
            for v in range(exBoundaries[2], exBoundaries[3] + 1,6):
                um, uM, vm, vM = findBoundaries(origin, img, u, v)
                boundaries[0] = min(boundaries[0], um)
                boundaries[1] = max(boundaries[1], uM)
                boundaries[2] = min(boundaries[2], vm)
                boundaries[3] = max(boundaries[3], vM)
        boundaries = tuple(boundaries)
    return boundaries



def findBoundaries(origin, img, u0=0, v0=0):
    uMin = u0
    while not(isLignEmpty(uLign(uMin, origin, img, v0))):
        uMin -= 1
    uMax = u0
    while not(isLignEmpty(uLign(uMax, origin, img, v0))):
        uMax += 1

    vMin = v0
    while not(isLignEmpty(vLign(vMin, origin, img, u0))):
        vMin -= 1
    vMax = v0
    while not(isLignEmpty(vLign(vMax, origin, img, u0))):
        vMax += 1

    return uMin+1, uMax-1, vMin+1, vMax-1

def findAccessible(img, boundaries, origin):
    um,uM,vm,vM = boundaries
    accessible = []
    for u in range(um,uM+1):
        for v in range(vm,vM+1):
            if CaseState(u, v, *origin, img) == "accessible":
                accessible.append((u,v))
    return accessible

def closestCase(caseList, target, character, origin, img, radius = 0,lineOfSight = True):
    minDist = float('inf')
    distToCharMin = float('inf')
    case = None
    lineFound = False
    caseList.append(character)
    for i in caseList:
        distance = dist(i, target,origin,img)
        distToChar = dist(i, character,origin,img)
        line = hasLineOfSight(i, target, origin, img)
        if ((distance <= minDist and distance >= radius) and ((line or not(lineFound)) or not(lineOfSight))) :
            if (distance == minDist and distToChar > distToCharMin):
                continue
            minDist = distance
            distToCharMin = distToChar
            case = i
            if line:
                lineFound = True
            else:
                lineFound = False
    return case

def casesBetween(case, target):
    liste = []
    x0,y0 = case
    x1,y1 = target
    Lx = np.linspace(x0,x1,100)
    Ly = np.linspace(y0,y1,100)
    for index in range(100):
        x = round(Lx[index])
        y = round(Ly[index])
        liste.append((x,y))
    return list(set(liste))

def hasLineOfSight(i, target, origin, img):
    if i == target:
        return True
    for case in casesBetween(i, target):
        if case == i or case == target:
            continue
        if CaseState(*case, *origin, img) == "stop":
            return False
    return True

def playPlacements(window):
    screen = screenshot(region, window)
    cv2.imwrite("debug\\placements.png", screen)
    origin = findRealOrigin(screen)
    boundaries = findRealBoundaries(origin, screen)
    accessible = findAccessible(screen, boundaries, origin)
    enemies = findRealEnemies(window)
    allies = findRealAllies(window)
    if (len(allies) == 0) or (len(enemies) == 0):
        return
    target = ToDofCoord(*enemies[0], *origin)
    print("enemy at:", target)
    character = [ToDofCoord(*i, *origin) for i in allies][0]
    print("i am at:", character)
    closest = closestCase(accessible, target, character,origin, screen)
    print("going to:", closest)
    x,y = ToRealCoord(*closest, *origin)
    if closest != character:
        click(x + region[0], y + region[1],window)
        sleep(0.5)
    press('f1', window)
    print("\n")
    sleep(1)

def playTurn(window, history):
    clearInterface(window)
    screen = screenshot(region, window)
    cv2.imwrite("debug\\turn.png", screen)
    screenFull = screenshot(None, window)
    allies = findRealAllies(window)
    enemies = findRealEnemies(window)
    if (len(allies) == 0) or (len(enemies) == 0):
        print("no one found")
        return
    origin = findRealOrigin(screen)
    boundaries = findRealBoundaries(origin, screen)
    character = whichAllyIsMe([ToDofCoord(*i, *origin) for i in allies],origin,screen)
    while not character:
        character = whichAllyIsMe([ToDofCoord(*i, *origin) for i in allies],origin,screenshot(region, window))
    print("i am at:", character)
    accessible = findAccessible(screen, boundaries, origin)
    if accessible == [] and getPM(screenFull) > 0:
        print("should be able to see accessibles, can't")
        return
    target = ToDofCoord(*enemies[0], *origin)
    print("enemy at:", target)
    
    
    
    closest = closestCase(accessible, target,character,origin, screen,2)
    print("going to:", closest)
    
    if ((character,target),target) in history:
        print("cycle, passing turn\n")
        press('f1',window)
        sleep(1)
        return
    
    x,y = ToRealCoord(*closest, *origin)
    if closest != character:
        click(x + region[0], y + region[1],window)
        sleep(0.5)
    
    x,y = ToRealCoord(*target, *origin)
    
    if inFight(window):
        spell(2,window)
        spell(2,window)
        spell(2,window)
        click(x + region[0], y + region[1],window)
        click(x + region[0], y + region[1],window)
        click(x + region[0], y + region[1],window)
        sleep(3)
        
        
    if inFight(window):
        spell(2,window)
        spell(2,window)
        spell(2,window)
        click(x + region[0], y + region[1],window)
        click(x + region[0], y + region[1],window)
        click(x + region[0], y + region[1],window)
        sleep(3)
    press('f1',window)
    print("\n")
    sleep(1)
    return ((character,target),target)
    
    
def spell(n, window):
    click(856 + (n-1)*44,943,window)
    sleep(0.5)
    

def dist(c1,c2,origin,screen):
    distance = 0
    reached = set([c1])
    while not(c2 in reached):
        toAdd = []
        distance += 1
        for c in reached:
            nextC = (c[0]+1, c[1])
            if nextC == c2:
                return distance
            if not(nextC in reached):
                state = CaseState(*nextC, *origin, screen)
                if state in ["walkable","accessible"]:
                    toAdd.append(nextC)
                
            nextC = (c[0]-1, c[1])
            if nextC == c2:
                return distance
            if not(nextC in reached):
                state = CaseState(*nextC, *origin, screen)
                if state in ["walkable","accessible"]:
                    toAdd.append(nextC)
            
            nextC = (c[0], c[1]+1)
            if nextC == c2:
                return distance
            if not(nextC in reached):
                state = CaseState(*nextC, *origin, screen)
                if state in ["walkable","accessible"]:
                    toAdd.append(nextC)
                
            nextC = (c[0], c[1]-1)
            if nextC == c2:
                return distance
            if not(nextC in reached):
                state = CaseState(*nextC, *origin, screen)
                if state in ["walkable","accessible"]:
                    toAdd.append(nextC)
        if len(toAdd) == 0:
            return float('inf')
        for c in toAdd:
            reached.add(c)
    return distance

def iniCreature(window):
    loc = locateCenter("creature.jpg",0.9,window)
    if loc:
        click(*loc, window)
    

def whichAllyIsMe(allies,origin,screen):
    cv2.imwrite("begug\\findingMe.png",screen)
    if len(allies) ==1:
        return allies[0]
    for case in allies:
        if isMe(case,origin,screen):
            return case
    return

def isMe(case,origin,screen):
    reached = set([case])
    while True:
        toAdd = []
        for c in reached:
            nextC = (c[0]+1, c[1])
            if not(nextC in reached):
                state = CaseState(*nextC, *origin, screen)
                if state in ["walkable","accessible"]:
                    toAdd.append(nextC)
                
            nextC = (c[0]-1, c[1])
            if not(nextC in reached):
                state = CaseState(*nextC, *origin, screen)
                if state in ["walkable","accessible"]:
                    toAdd.append(nextC)
            
            nextC = (c[0], c[1]+1)
            if not(nextC in reached):
                state = CaseState(*nextC, *origin, screen)
                if state in ["walkable","accessible"]:
                    toAdd.append(nextC)
                
            nextC = (c[0], c[1]-1)
            if not(nextC in reached):
                state = CaseState(*nextC, *origin, screen)
                if state in ["walkable","accessible"]:
                    toAdd.append(nextC)
        foundAccessible = False
        foundWalkable = False
        for c in toAdd:
            if CaseState(*c, *origin, screen) == "walkable":
                foundWalkable = True
            if CaseState(*c, *origin, screen) == "accessible":
                foundAccessible = True
            reached.add(c)
        if foundAccessible and not(foundWalkable):
            continue
        if foundWalkable and not(foundAccessible):
            return True
        if foundWalkable and foundAccessible:
            return False
        if not(foundWalkable) and not(foundAccessible):
            return False

def filterWhiteOut(img):
    color, epsilon = [255]*3, 150
    mask = 255 - isolateInImg(img, color, epsilon)[:,:,0]
    return cv2.bitwise_and(img,img,mask = mask)

if __name__ == "__main__":
    window = getDofusWindow("Mr-Maron")
    iniCreature(window)
    #Combat(window)