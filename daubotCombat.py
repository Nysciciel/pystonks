from daubotControl import travel,zaapTo,clickOnZaap,enterCouloirMalle,enterSalleMalle,takeChasse,goDir,enterHavreSac,waitForCoord,attenteChasse,validateEtape,validateIndice,takeTransporteur,abandon,lanceCombat,leaveChat
from daubotImg import getCoord,hasChasse,getDepCoord,getIndice,getEtape,getNumeroIndice,etapeFinie,getDir,isPho,phorreurOnMap,directionOpposée,getDepRegion,isDownOfOtomai,isRegionOnlyAccessibleThroughTranspo,chasseLegendaire,parseLocation,inFight,victoire,myTurn,waitForEndScreen,placementPhase,getTurnIndex,initializeCharIndex
from daufousMap import getIndiceDist,getIndiceCoord,getIndiceAnswers,zaapName, closestZaapCoord
from daubotIO import waitFor,getDofusWindow,press
from time import time, strftime
import cv2
import numpy as np

def Combat(strat, window):
    charIndex = -1
    print("combat.")
    if chasseLegendaire(window):
        print("chasse légendaire terminée")
        return False
    lanceCombat(window)
    while inFight(window):
        if placementPhase(window):
            print("placements")
            playPlacements(strat, window)
            while placementPhase(window):
                if not inFight(window):
                    break
            print("placements done")
        if charIndex == -1:
            charIndex = initializeCharIndex(window)
        if myTurn(charIndex, window):
            print("my turn")
            playTurn(strat, window)
            while myTurn(charIndex, window):
                if not inFight(window):
                    break
        else:
            print("not my turn")
            while not myTurn(charIndex, window):
                if not inFight(window):
                    break
    waitForEndScreen(window)
    if victoire(window):
        print("victoire")
    else:
        print("défaite")
    leaveChat(window)
    return True

def playTurn(strat, window):
    fightMap = parseMap(window)
    strat.turn(fightMap, window)
    passTurn(window)

def passTurn(window):
    press('f1',window)
    
def parseMap(window):
    return#TODO

def playPlacements(window):
    fightMap = parseMap(window)
    strat.placements(fightMap, window)
    passTurn(window)




class standardStrat:
    
    def __init__(self):
        pass
    
    def placements(self, fightMap, window):
        pass
    
    def turn(self, fightMap, window):
        pass



if __name__ == "__main__":
    strat = standardStrat()
    window = getDofusWindow("Mr-Maron")
    Combat(strat, window)
    
    