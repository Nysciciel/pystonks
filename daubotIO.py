import win32gui, win32com.client
import pyautogui
import numpy as np
from time import sleep
pyautogui.PAUSE = 0.1
IOpause = 0.01



def waitFor(window):
    while not win32gui.GetForegroundWindow() == window:
        sleep(IOpause)
        if not((win32gui.GetWindowText(window), window) in enumerateWindows()):
            raise NameError("Window to command doesn't exist.")

def locate(img, confidence, window):
    waitFor(window)
    res = pyautogui.locateOnScreen(img, confidence = confidence)
    if res:
        (x,y,_,_) = res
        return x,y
    return None

def locateCenter(img, confidence, window):
    waitFor(window)
    return pyautogui.locateCenterOnScreen(img, confidence = confidence)

def locateAll(img, confidence, window):
    waitFor(window)
    res = []
    positions = pyautogui.locateAllOnScreen(img, confidence = confidence)
    for pos in positions:
        (x,y,w,h) = pos
        res.append((x + w//2, y + h//2))
    return res

def enumerateWindows():
    res = []
    def winEnumHandler( hwnd, ctx ):
        if win32gui.IsWindowVisible( hwnd ):
            if win32gui.GetWindowText( hwnd ):
                res.append( (win32gui.GetWindowText( hwnd ), hwnd))
    win32gui.EnumWindows( winEnumHandler, None )
    return res

def getDofusWindow(characterName):
    for win in enumerateWindows():
        name = win[0]
        if name.startswith(characterName + " - Dofus "):
            return win[1]
    return None

def press(key, window):
    waitFor(window)
    pyautogui.press(key)

def typeText(text, window):
    waitFor(window)
    for char in text:
        press(char, window)

def click(x, y, window):
    waitFor(window)
    pyautogui.click(x,y)

def doubleClick(x, y, window):
    waitFor(window)
    pyautogui.click(x,y,clicks = 2)

def hotkey(k0, k1, window):
    waitFor(window)
    pyautogui.hotkey(k0, k1)

def screenshot(region = None, window = None):
    waitFor(window)
    if region:
        (xmin, ymin, xmax, ymax) = region
        screen = pyautogui.screenshot(region=(xmin, ymin, xmax-xmin, ymax-ymin))
    else:
        screen = pyautogui.screenshot()
    return np.array(screen)[:, :, ::-1].astype(np.uint8)

def moveTo(x,y,window):
    waitFor(window)
    pyautogui.moveTo(x,y)
    sleep(IOpause)

def setWindow(window):
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(window)

if __name__ == "__main__":
    window = getDofusWindow("Mr-Maron")
    #clickTranspo(window)
