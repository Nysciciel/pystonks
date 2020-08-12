import numpy as np
import cv2, pytesseract
from daubotIO import screenshot, locate, moveTo,getDofusWindow,hotkey
import difflib
from time import sleep

phos = ["Phorreur sournois", "Phorreur baveux", "Phorreur chafouin", "Phorreur fourbe", "Phorreur mefiant", "Phorreur ruse"]

def parseLocation(window, tolerance = 200):
    screen = screenshot((6,33,320,100), window)
    if screen is None:
        return None
    cv2.imwrite('debug\\parseLocationDebug1.jpg', screen)
    isolated = doubleIsolateInImg(screen,8,tolerance)
    cv2.imwrite('debug\\parseLocationDebug2.jpg', isolated)
    cropped = cropOut(isolated)
    cv2.imwrite('debug\\parseLocationDebug3.jpg', cropped)
    text = readText(cropped)
    try:
        getCoord(text, window)
        return text
    except ValueError:
        return parseLocation(window, tolerance - 5)

def isolateInImg(inputImg, color, epsilon = 50):
    color = np.array(color)
    low = color - epsilon
    low[np.where(low<0)]=0
    high = color + epsilon
    high[np.where(high>255)]=255
    return np.tile(cv2.inRange(inputImg, low, high)[:,:,None],3)

def cropOut(inputImg, margin = 10):
    return inputImg

def cropOutOld(inputImg, margin = 10):
    img = cv2.copyMakeBorder(inputImg, margin, margin, margin, margin, cv2.BORDER_CONSTANT, value = [255,255,255])
    argmin = None
    argmax = None
    for x in range(img.shape[0]):
        for y in range(img.shape[1]):
            pixel = img[x,y]
            if np.sum(np.abs((pixel-[0,0,0]))) == 0:
                if argmin == argmax == None:
                    argmin = [float('inf'), float('inf')]
                    argmax = [-float('inf'), -float('inf')]
                if x > argmax[0]:
                    argmax[0] = x
                if y > argmax[1]:
                    argmax[1] = y
                if x < argmin[0]:
                    argmin[0] = x
                if y < argmin[1]:
                    argmin[1] = y
    if argmin == argmax == None:
        return None
    (x,y,_) = img.shape
    (xmin, ymin) = argmin
    (xmax, ymax) = argmax
    xmin = max(xmin - margin, 0)
    ymin = max(ymin - margin, 0)
    ymax = min(y, ymax + margin)
    xmax = min(x, xmax + margin)
    return img[xmin:xmax, ymin:ymax]

def readText(img,lang='eng', config = None):
    text = pytesseract.image_to_string(img, lang=lang, config = config)
    return text

def getCoord(location, window):
    coord = location[location.find('\n')+1:]
    if coord.find(',') != coord.rfind(','):
        coord = coord[:coord.rfind(',')]
    coord = coord.split(',')
    x,y = (int(coord[0]),int(coord[1]))
    return x,y
        

def getRegion(location, window):
    if not location:
        return None
    region = location[:location.find('\n')]
    return region

def inHavreSac(location, window):
    return wordDiff(getRegion(location, window), "Havre-Sac Kerubim") <3

def hasChasse(window):
    return not(not(locate("chasse.jpg", 0.7,window))) or not(not(locate("chasseLeg.jpg", 0.7,window)))

def parsingChasseCoord(window):
    if chasseLegendaire(window):
        x,y = locate("chasseLeg.jpg", 0.7, window)
        return (x+40, y)
    return locate("chasse.jpg", 0.7, window)


def getEtape(window):
    (x,y) = parsingChasseCoord(window)
    screen = screenshot((x-52,y+34,x+60,y+61), window)
    cv2.imwrite('debug\\parseEtapeDebug1.jpg', screen)
    isolated = isolateInImg(screen, [80,60,40],80)
    cv2.imwrite('debug\\parseEtapeDebug2.jpg', isolated)
    cropped = cropOut(isolated)
    cv2.imwrite('debug\\parseEtapeDebug3.jpg', cropped)
    text = readText(cropped).replace(' ','')
    sep = text.find('/')
    res = int(text[sep-1]), int(text[sep+1])
    return res




def getDepCoord(window):
    (x,y) = parsingChasseCoord(window)
    screen = screenshot((x-26,y+80,x+126,y+103), window)
    cv2.imwrite('debug\\parseDepCoordDebug1.jpg', screen)
    for tolerance in range(80,120):
        try:
            isolated = isolateInImg(screen, [80,60,40],tolerance)
            cv2.imwrite('debug\\parseDepCoordDebug2.jpg', isolated)
            text = readText(isolated).replace('—','-').replace('.',',')
            sep1 = text.find(',')
            sep0 = text.find('[')
            sep2 = text.find(']')
            x = int(text[sep0+1:sep1])
            y = int(text[sep1+1:sep2])
            return (x,y)
        except ValueError:
            pass
    raise NameError("coordonnees de depart illisibles")


def getFlag(window):
    return locate("flag.jpg", 0.9, window)

def findIndiceSquare(window):
    res = cv2.matchTemplate(screenshot(window = window), cv2.imread("indiceSquare.jpg"), cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    x,y = min_loc
    return x,y

def getIndice(window, answers = [], color = [72,56,30], tolerance = 100):
    if etapeFinie(window):
        return "etape finie"
    x,y = parsingChasseCoord(window)
    x0,y0 = getFlag(window)
    screen = screenshot((x-30,y0-6,x0,y0+20), window)
    cv2.imwrite('debug\\parseIndiceDebug1.jpg', screen)
    isolated = isolateInImg(screen, color,tolerance)
    cv2.imwrite('debug\\parseIndiceDebug2.jpg', isolated)
    indice = readText(isolated)
    if not(indice in answers) and not(isPho(indice)):
        minDiff = float('inf')
        bestMatch = None
        for word in answers + phos:
            diff = wordDiff(indice, word)
            if diff < minDiff:
                minDiff = diff
                bestMatch = word
        return bestMatch
    return indice

def wordDiff(str1, str2):
    return len([li for li in difflib.ndiff(str1, str2) if li[0] != ' '])

def getDir(window):
    if etapeFinie(window):
        return None
    x,y = parsingChasseCoord(window)
    x0,y0 = getFlag(window)
    screen = screenshot((x-52,y0-3,x-30,y0+20), window)
    cv2.imwrite('debug\\parseDirDebug1.jpg', screen)
    if screen is None:
        return None
    isolated = isolateInImg(screen, [70,60,40],60)
    cv2.imwrite('debug\\parseDirDebug2.jpg', isolated)
    cropped = cropOut(isolated,0)
    cv2.imwrite('debug\\parseDirDebug3.jpg', cropped)
    return bestMatchDir(cropped)


def score(img, dirr):
    res = cv2.matchTemplate(isolateInImg(cv2.imread("dir"+dirr+".JPG"), [70,60,40],60), img, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    return min_val

def bestMatchDir(img):
    minScore = float('inf')
    bestdir = None
    for dirr in ["top","left","bottom","right"]:
        s = score(img, dirr)
        if s < minScore:
            minScore=s
            bestdir = dirr
    return bestdir


def etapeFinie(window):
    return not(getFlag(window))


def getNumeroIndice(window):
    if etapeFinie(window):
        return None
    x,y = getFlag(window)
    _,y0 = parsingChasseCoord(window)
    return int(round((y-(y0+107))/28))


def isPho(indice):
    return indice in phos

def directionOpposee(dirr):
    return {"top":"bottom","bottom":"top","left":"right","right":"left"}[dirr]

def canAdd(x,y,coordList):
    for i in coordList:
        if abs(x - i[0]) + abs(y - i[1]) <30:
            return None
    return True

def whereCouldBePho(img, window):
    #phoColor = [78 , 100, 80]
    liste = []
    for dirr in ["left","bottom","right","top"]:
        comp = cv2.imread("Pho"+dirr+".png")
        #comp = isolateInImg(comp, phoColor, 20)
        cv2.imwrite("debug\\phoDebug0.jpg", comp)
        res = cv2.matchTemplate(comp, img, cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if min_val < 0.96:
            min_loc = list(min_loc)
            min_loc[0] += 30
            min_loc[1] += 30
            liste.append(tuple(min_loc))
    return liste

def phorreurOnMap(phorreur, window):
    #phoColor = [78 , 100, 80]
    region = (325,25,1600,920)
    # screen = screenshot(region = region, window = window)
    # cv2.imwrite("debug\\phoDebug1.jpg", screen)
    # screen = isolateInImg(screen, phoColor, 27)
    # cv2.imwrite("debug\\phoDebug2.jpg", screen)
    mask = getEntityDelta(window)
    screen = screenshot(region, window)
    img = cv2.bitwise_and(screen,screen,mask = mask)
    cv2.imwrite("debug\\phoDebug1.jpg", img)
    coordList = whereCouldBePho(img,window)
    for i in range(len(coordList)):
        x,y = coordList[i]
        x += region[0]
        y += region[1]
        moveTo(x, y, window)
        screen = screenshot((x-300, y-100, x+300, y+100), window)
        cv2.imwrite("debug\\phoDebug3"+str(i)+".jpg", screen)
        orange = [0, 175, 255]
        for tolerance in [20]:#range(20,51,6):
            isolated = isolateInImg(screen, orange, tolerance)
            cv2.imwrite("debug\\phoDebug4"+str(i)+".jpg", isolated)
            text = readText(isolated)
            if wordDiff(text, phorreur) < 10:
                return True
    return False

def stats(path):
    img = cv2.imread(path)
    moy = np.mean(img, axis=(0, 1))
    dev = np.max(np.abs(img-moy))
    return moy[::-1], dev

def getDepRegion(window):
    (x,y) = parsingChasseCoord(window)
    moveTo(x, y+83, window)
    moveTo(x, y+82, window)
    screen = screenshot((x-100,y,x+200,y+150),window)
    cv2.imwrite("debug\\depRegionDebug0.jpg", screen)
    isolated = doubleIsolateInImg(screen)
    cv2.imwrite("debug\\depRegionDebug1.jpg", isolated)
    text = readText(isolated)
    return text

def doubleIsolateInImg(inputImg, greyTolerance = 15, whiteTolerance = 70):
    color = [whiteTolerance + (255-whiteTolerance)//2]*3
    epsilon = (255-whiteTolerance)//2
    return isolateInImg(inputImg, color, epsilon)

def isDownOfOtomai(region):
    downRegions = ["ile d'Otomaï (Jungle obscure)","ile d'Otomaï (Plaines herbeuses)","ile d'Otomaï (Plage de corail)","ile d'Otomaï (Village côtier)","ile d'Otomaï (Feuillage de l'arbre Hakam)"]
    downDiff = min([wordDiff(region, downRegion) for downRegion in downRegions])
    upRegions = ["ile d'Otomaï (Tronc de l'arbre Hakam)","ile d'Otomaï (Village de la canopee)"]
    upDiff = min([wordDiff(region, upRegion) for upRegion in upRegions])
    return downDiff < upDiff

def isRegionOnlyAccessibleThroughTranspo(region):
    bourgadeRegions = ["ile de frigost (La Bourgade)","ile de frigost (Port de givre)","ile de frigost (Mer Kantil)","ile de frigost (Champs de glace)","ile de frigost (Forêt des pins perdus)","ile de frigost (Lac gele)"]
    bourgadeDiff = min([wordDiff(region, bourgadeRegion) for bourgadeRegion in bourgadeRegions])
    resteRegions = ["ile de frigost (Berceau d'Alma)","ile de frigost (Larmes d'Ouronigride)","ile de frigost (Crevasse Perge)","ile de frigost (Forêt petrifiee)"]
    resteDiff = min([wordDiff(region, resteRegion) for resteRegion in resteRegions])
    return resteDiff < bourgadeDiff
    
def chasseLegendaire(window):
    return not(not(locate("chasseLeg.jpg", 0.7,window)))

def inFight(window):
    return not(not(locate("fight.jpg",0.7,window)))

def myTurn(charIndex, window):
    return getTurnIndex(window) == charIndex

def getTurnIndex(window):
    xArrow,_ = bestMatch("turnArrow.jpg",window)
    xRef,_ = bestMatch("fight.jpg",window)
    index = round((xRef - xArrow - 75)/60)
    return index

def bestMatch(path, window):
    screen = screenshot(window = window)
    ref = cv2.imread(path)
    res = cv2.matchTemplate(ref, screen, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    min_loc = list(min_loc)
    # min_loc[0] += ref.shape[0]
    # min_loc[1] += ref.shape[1]
    return tuple(min_loc)

def victoire(window):
    return not(not(locate("victoire.jpg",0.8,window)))

def defaite(window):
    return not(not(locate("defaite.jpg",0.8,window)))

def toggleTransparency(window):
    hotkey('shift','2', window)
    sleep(0.1)

def getEntityDelta(window, region = (325,25,1600,920)):
    screen0 = screenshot(region, window)
    toggleTransparency(window)
    cv2.imwrite("debug\\phoDelta0.jpg",screen0)
    screen1 = screenshot(region, window)
    cv2.imwrite("debug\\phoDelta1.jpg",screen1)
    res = np.abs(screen0 - screen1)
    cv2.imwrite("debug\\phoDelta2.jpg",res)
    toggleTransparency(window)
    whiteTolerance = 10
    color, epsilon = [whiteTolerance + (255-whiteTolerance)//2]*3, (255-whiteTolerance)//2
    r = isolateInImg(res, color, epsilon)[:,:,0]
    cv2.imwrite("debug\\phoDelta3.jpg",r)
    return r

def waitForEndScreen(window):
    while not victoire(window) and not defaite(window):
        sleep(1)

def placementPhase(window):
    return not(locate("turnArrow.jpg",0.8,window))

def initializeCharIndex(window):
    while np.all(screenshot((850,1015,851,1016),window) != [[[0, 200, 252]]]):
        sleep(1)
    return getTurnIndex(window)

if __name__ == "__main__":
    window = getDofusWindow("Mr-Maron")
    print(parseLocation(window))
    #print(phorreurOnMap("phorreur sournois", window))
    