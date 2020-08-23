import win32gui, win32com.client
import pyautogui
import numpy as np
import cv2
from time import sleep
pyautogui.PAUSE = 0.01
IOpause = 0.01



def waitFor(window):
    while not win32gui.GetForegroundWindow() == window:
        if not((win32gui.GetWindowText(window), window) in enumerateWindows()):
            raise NameError("Window to command doesn't exist.")

def locate(img, confidence, window):
    waitFor(window)
    
    res = cv2.matchTemplate(screenshot(window = window), cv2.imread(img), cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    x,y = min_loc
    if min_val < 1 - confidence:
        return x,y
    return None

def locateCenter(img, confidence, window):
    waitFor(window)
    
    res = cv2.matchTemplate(screenshot(window = window), cv2.imread(img), cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    x,y = min_loc
    h,w,_ = cv2.imread(img).shape
    if min_val < 1 - confidence:
        return x + w//2,y + h//2
    return None

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
    sleep(IOpause)
    waitFor(window)
    pyautogui.press(key)

def typeText(text, window):
    sleep(IOpause)
    sleep(0.5)
    waitFor(window)
    pyautogui.typewrite(text)
    sleep(0.5)

def click(x, y, window):
    # lParam = win32api.MAKELONG(x, y)
    # win32api.PostMessage(hWnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    # win32api.PostMessage(hWnd, win32con.WM_LBUTTONUP, None, lParam)
    
    sleep(IOpause)
    waitFor(window)
    pyautogui.moveTo(x,y)
    pyautogui.moveTo(x+1,y)
    pyautogui.click(x,y)

def doubleClick(x, y, window):
    sleep(IOpause)
    waitFor(window)
    pyautogui.click(x,y,clicks = 2)

def hotkey(k0, k1, window):
    sleep(IOpause)
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
    sleep(IOpause)
    waitFor(window)
    pyautogui.moveTo(x,y)
    sleep(IOpause)

def setWindow(window):
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(window)

if __name__ == "__main__":
    window = getDofusWindow("Mr-Maron")
