from daubotControl import travel,zaapTo,clickOnZaap,enterCouloirMalle,enterSalleMalle,takeChasse,goDir,enterHavreSac,waitForCoord,attenteChasse,validateEtape,validateIndice,takeTransporteur,abandon,regenEnergy,clearInterface
from daubotImg import getCoord,hasChasse,getDepCoord,getIndice,getEtape,getNumeroIndice,etapeFinie,getDir,isPho,phorreurOnMap,directionOpposee,getDepRegion,isDownOfOtomai,isRegionOnlyAccessibleThroughTranspo,parseLocation,inFight,chassePortail,chasseLegendaire
from daufousMap import getIndiceDist,getIndiceCoord,getIndiceAnswers,zaapName, closestZaapCoord
from daubotIO import waitFor,getDofusWindow
from daubotCombat import Combat
from time import time, strftime


def goThroughZaap(loc,x,y,window):
    coord = getCoord(loc,window)
    distToObj = abs(x-coord[0]) + abs(y-coord[1])
    if coord == (x,y):
        return
    zaapcoord = closestZaapCoord(x,y)
    distfromzaap = abs(x-zaapcoord[0]) + abs(y-zaapcoord[1])
    if coord == zaapcoord or distToObj < distfromzaap:
        travel(coord, x,y,window)
        return
    enterHavreSac(loc, window)
    clickOnZaap(window)
    zaapTo(coord, zaapName(*zaapcoord), window)
    waitForCoord(zaapcoord, 10,window)
    if zaapcoord != (x,y):
        print("not quite there")
        travel(zaapcoord,x,y,window)
        return

def TakeChasse(window):
    try:
        if hasChasse(window):
            print("chasse en cours")
            if chassePortail(window):
                print("chasse portail")
            if chasseLegendaire(window):
                print("chasse legendaire")
            return time()
        print("Je vais a la malle")
        loc = parseLocation(window)
        goThroughZaap(loc, -25,-36,window)
        print("J\'entres")
        enterCouloirMalle(window)
        enterSalleMalle(window)
        print("Je prends une chasse")
        takeChasse(window)
        takeChasse(window)
        takeChasse(window)
        attenteChasse(window)
        start = time()
        print("Je resors")
        travel(getCoord("La Malle aux tresors \n-25,-36", window),-24,-36,window)
        return start
    except NameError:
        travel(getCoord(loc, window),-24,-36,window)
        return TakeChasse(window)

def FaireChasse(window):
    world = 0
    try:
        coord = getDepCoord(window)
    except NameError:
        return False
    (etape,nEtape) = getEtape(window)
    nIndice = getNumeroIndice(window)
    print("Depart en:",coord,"etape:",etape,"/",nEtape," indice trouves:",nIndice)
    visited = [coord]
    location = parseLocation(window)
    if (etape == nEtape or nIndice == 0) and getCoord(location, window) == coord:
        print("already there")
    else:
        if coord[0] < -40:
            if coord[1] > -20:
                print("ile d'otomai")
                depRegion = getDepRegion(window)
                if isDownOfOtomai(depRegion):
                    print("en bas de l'arbre")
                    if (etape == 1 and nIndice == 0) or etape == nEtape:
                        enterHavreSac(location, window)
                        clickOnZaap(window)
                        zaapTo(getCoord(location, window), "cotier",window)
                        waitForCoord((-46,18), 10,window)
                        travel(getCoord(parseLocation(window), window), *coord, window)
                else:
                    print("en haut de l'arbre")
                    world = 2
                    if (etape == 1 and nIndice == 0) or etape == nEtape:
                        enterHavreSac(location, window)
                        clickOnZaap(window)
                        zaapTo(getCoord(location, window), "canopee",window)
                        waitForCoord((-54,16), 10,window)
                        travel(getCoord(parseLocation(window), window), *coord, window)
            else:
                print("frigost")
                if (etape == 1 and nIndice == 0) or etape == nEtape:
                    enterHavreSac(location, window)
                    clickOnZaap(window)
                    zaapTo(getCoord(location, window), "bourgade",window)
                    waitForCoord((-78,-41), 10,window)
                    depRegion = getDepRegion(window)
                    if isRegionOnlyAccessibleThroughTranspo(depRegion):
                        travel((-78,-41),-68,-34,window)
                        takeTransporteur(depRegion, window)
                    travel(getCoord(parseLocation(window), window), *coord, window)
        else:
            if (etape == 1 and nIndice == 0) or etape == nEtape:
                goThroughZaap(location, *coord, window)
    while etape != nEtape:
        while True:
            if etapeFinie(window):
                print("etape:", etape, "validee\n")
                break
            location = parseLocation(window)
            coord = getCoord(location, window)
            print("\nat:",coord)
            direction = getDir(window)
            print("towards:", direction)
            answers = getIndiceAnswers(*coord,direction, world = world)
            indice = getIndice(window, answers = answers)
            print("Found:", indice)
            if isPho(indice):
                if not searchPho(location, indice, direction, visited, window):
                    print("pho not found")
                    return False
                location = parseLocation(window)
            else:
                dist = getIndiceDist(indice, *coord, direction,world = world)
                indiceCoord = getIndiceCoord(indice, *coord, direction, world = world)
                print("Distance:",dist)
                if not dist:
                    print("error")
                    return False
                for i in range(dist):
                    if not goDir(location, direction, window):
                        if inFight(window):
                            if not Combat(window):
                                print("died in accidental combat")
                                return False
                        clearInterface(window)
                        print("Resort to direct travel:",indiceCoord)
                        location = parseLocation(window)
                        travel(getCoord(location, window), *indiceCoord,window)
                        location = parseLocation(window)
                        break
                    location = parseLocation(window)
            print("indice numero",nIndice+1," valide")
            print("at:",getCoord(location, window), "visited:",visited)
            if getCoord(location, window) in visited:
                print("already visited")
                return False
            visited.append(getCoord(location, window))
            validateIndice(window)
            nIndice = getNumeroIndice(window)
            if nIndice:
                print(nIndice," indices valides")
            if not indice:
                return False
        validateEtape(window)
        (etapeNext, nEtape) = getEtape(window)
        nIndice = 0
        coord = getDepCoord(window)
        visited = [coord]
        if etapeNext == etape:
            print("Dofus map fail")
            return False
        etape = etapeNext
    return True

def searchPho(location, phorreur, direction, visited, window):
    goDir(location, direction, window)
    if inFight(window):
        if not Combat(window):
            print("died in accidental combat")
            return False
    loc = parseLocation(window)
    if phorreurOnMap(phorreur,window):
        return True
    j = 9
    for k in range(3):
        for i in range(1, max(1,j)+1):
            if not goDir(loc, direction, window):
                if inFight(window):
                    if not Combat(window):
                        print("died in accidental combat")
                        return False
                i -= 1
                loc = parseLocation(window)
                break
            loc = parseLocation(window)
            if not (getCoord(loc, window) in visited):
                if phorreurOnMap(phorreur,window):
                    return True
        for j in range(1, max(1,i)+1):
            if not goDir(loc, directionOpposee(direction), window):
                if inFight(window):
                    if not Combat(window):
                        print("died in accidental combat")
                        return False
                j -= 1
                loc = parseLocation(window)
                break
            loc = parseLocation(window)
            if not (getCoord(loc, window) in visited):
                if phorreurOnMap(phorreur,window):
                    return True
    return False


def faireChasses(window):
    waitFor(window)
    while True:
        regenEnergy(window)
        startTime = TakeChasse(window)
        print("chasse started at:", strftime("%H:%M"))
        if not FaireChasse(window):
            abandon(startTime, window)
            continue
        if not Combat( window):
            abandon(startTime, window)
            continue
            




if __name__ == "__main__":
    window = getDofusWindow("Xbani")
    faireChasses(window)




