import cv2, cvzone
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

with open("camera.txt") as f:
    camera = f.read()

if camera.isdigit():
    camera = int(camera)
else:
    camera = 0


##########################
wCam, hCam = 640, 480
frameR = 100 # Frame Reduction
smoothening = 7
wScr, hScr = autopy.screen.size()
#wCam, hCam = wScr, hScr
#########################

plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(camera)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
toggle = 0
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = hCam - frameR * 2
volPer = 0

imgVolume = cv2.imread("volume.png", cv2.IMREAD_UNCHANGED)
imgVolume = cv2.resize(imgVolume, (0, 0), None, 0.1, 0.1)
imgIrsiyat = cv2.imread("IRSIYAT.png", cv2.IMREAD_UNCHANGED)
imgIrsiyat = cv2.resize(imgIrsiyat, (0, 0), None, 0.32, 0.32)
while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img)
    # 2. Get the tip of the index and middle fingers
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR * 2),(255, 0, 255), 2)

    if len(lmList) != 0:
        x0, y0 = lmList[4][1:]
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    
        # 3. Check which fingers are up
        fingers = detector.fingersUp()

        # 4. Only Index Finger : Moving Mode
        if fingers == [0, 1, 0, 0, 0] or fingers == [0, 1, 1, 0, 0]:
            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR * 2), (0, hScr))
            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # 7. Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY
        

        if fingers[1] == 1 and fingers[2] == 0:
            toggle = 0
            autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)


        # 8. Both Index and middle fingers are up : Clicking Mode
        if fingers == [0, 1, 1, 0, 0]:
            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)

            # 10. Click mouse if distance short
            if length > 50:

                toggle = 0
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)

                cv2.circle(img, (lineInfo[4], lineInfo[5]),
                15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()
            elif length < 40 and not toggle:
                toggle = 1
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)
                cv2.circle(img, (lineInfo[4], lineInfo[5]),
                15, (0, 255, 0), cv2.FILLED)
         

        if fingers == [1, 1, 0, 0, 0]:

            cv2.circle(img, (x0, y0), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x0, y0), (x1, y1), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

            length = math.hypot(x1 - x0, y1 - y0)

            vol = np.interp(length, [50, 200], [minVol, maxVol])
            volBar = np.interp(length, [50, 200], [hCam - frameR * 2, frameR])
            volPer = np.interp(length, [50, 200], [0, 100])
            volume.SetMasterVolumeLevel(vol, None)

            if length < 50:
                cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    cv2.rectangle(img, (35, frameR), (65, hCam - frameR * 2), (255, 0, 0), 2)
    cv2.rectangle(img, (35, int(volBar)), (65, hCam - frameR * 2), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (30, hCam - frameR * 2 + 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 2)

    # 12. Display
    img = cvzone.overlayPNG(img, imgVolume, [25, 30])
    img = cvzone.overlayPNG(img, imgIrsiyat, [0, hCam - 100])
    cv2.imshow("IRSIYAT VM", img)
    #cv2.imshow("Image1", imgVolume)
    if cv2.waitKey(1) & 0xff == ord('q') or (cv2.getWindowProperty('IRSIYAT VM',cv2.WND_PROP_VISIBLE)) == 0:
        break

cap.release()
cv2.destroyAllWindows()        