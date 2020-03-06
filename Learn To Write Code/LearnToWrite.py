#Engineers: Sean Duback, Robert Geoffrion
#School: Weber State University 
#Project: Motion Tracking
#Year: 2019 Acidemic Year

import numpy as np
import cv2
import math
import paho.mqtt.client as mqtt

############################################################ Global Variables ###############################################
white = [255,255,255]
black = [0,0,0]
nearBlack = [5,5,5]
dWinList = []
letter = cv2.imread('bw_image.png', 1)
pixDistance = 0
pixDistFirst = []
pixDirFirst = {}
pixDistSecond = []
pixDirSecond = {}
pixDistStart = 100
minPixDist = {}
# grab the reference to the webcam
camera = cv2.VideoCapture(0)
# define the lower and upper boundaries of the "orange"
colorLower = (0, 120, 70)
colorUpper = (50, 255, 180)
winNum = 0

startFlag = False
oldStartFlag = False 
endFlag = False 
score = 0

############################################################# Class Definitions #################################################

class Dwin(object):
    def __init__(self, idnum=0, ymin=0, ymax=0, xmin=0, xmax=0):
        self.idnum = idnum
        self.ymin = ymin
        self.ymax = ymax
        self.xmin = xmin
        self.xmax = xmax


############################################################# Functions ###########################################

def colorDwin (img, class_type="Dwin"):
    #func used for debugging colors in the dWins black and makes the letter white
    for Dwin in dWinList:
        print ("Window#= %s, xmin=%s, xmax= %s, ymin= %s ymax= %s"% (Dwin.idnum, Dwin.xmin, Dwin.xmax, Dwin.ymin, Dwin.ymax))
        for x in range(Dwin.xmin, Dwin.xmax):
            for y in range(Dwin.ymin, Dwin.ymax, -1):
                if np.array_equal(img[y, x], black):
                    print ("x=%s y=%s"%(x, y))
                    img[y, x] = white
                else:
                     img[y, x] = 0

def init ():
    #make Distance windows starting at the lower left corner and moving towards the upper right 
    dWinList.append(Dwin(0, 421, 404, 366, 374))
    dWinList.append(Dwin(1, 404, 402, 372, 376))
    dWinList.append(Dwin(2, 402, 396, 374, 378))
    dWinList.append(Dwin(3, 396, 394, 376, 383))
    dWinList.append(Dwin(4, 394, 390, 379, 384))
    dWinList.append(Dwin(5, 390, 386, 380, 385))
    dWinList.append(Dwin(6, 386, 365, 382, 400))
    dWinList.append(Dwin(7, 365, 345, 390, 410))
    dWinList.append(Dwin(8, 345, 325, 395, 415))
    dWinList.append(Dwin(9, 325, 305, 400, 420))
    dWinList.append(Dwin(10, 305, 285, 405, 425))
    dWinList.append(Dwin(11, 285, 265, 410, 430))
    dWinList.append(Dwin(12, 265, 245, 420, 440))
    dWinList.append(Dwin(13, 245, 225, 420, 440))
    dWinList.append(Dwin(14, 225, 205, 420, 440))
    dWinList.append(Dwin(15, 205, 185, 420, 440))
    #Dwin 16 begins left movement
    dWinList.append(Dwin(16, 205, 185, 400, 420))
    #Dwin 17 begins down movement
    dWinList.append(Dwin(17, 225, 205, 390, 410))
    dWinList.append(Dwin(18, 245, 225, 385, 405))
    dWinList.append(Dwin(19, 265, 245, 380, 400))
    dWinList.append(Dwin(20, 285, 265, 380, 400))
    dWinList.append(Dwin(21, 305, 285, 375, 395))
    dWinList.append(Dwin(22, 325, 305, 375, 390))
    dWinList.append(Dwin(23, 345, 325, 375, 385))
    dWinList.append(Dwin(24, 365, 345, 375, 385))
    dWinList.append(Dwin(25, 385, 365, 370, 380))
    dWinList.append(Dwin(26, 405, 385, 370, 380))
    dWinList.append(Dwin(27, 425, 405, 370, 380))
    dWinList.append(Dwin(28, 445, 425, 370, 380))
    dWinList.append(Dwin(29, 465, 445, 370, 380))
    dWinList.append(Dwin(30, 490, 465, 370, 380))
    #Dwin 28 begins right movement
    dWinList.append(Dwin(31, 495, 475, 380, 400))
    dWinList.append(Dwin(32, 495, 475, 400, 420))
    #Dwin 30 begins up movement
    dWinList.append(Dwin(33, 475, 455, 410, 430))
    dWinList.append(Dwin(34, 455, 435, 420, 440))
    dWinList.append(Dwin(35, 435, 405, 430, 450))
    dWinList.append(Dwin(36, 0, 0, 0, 0)) #dummy window for dWin +1 loop when dWin loop is on dwin=35


def totalDistance(x0, y0, x1, y1):
    return math.sqrt((x0 - x1)**2 + (y0 - y1)**2)

def start (img, inputX, inputY):
    
    for x in range(dWinList[0].xmin, dWinList[0].xmax):
        for y in range(dWinList[0].ymin, dWinList[0].ymax, -1):
            if np.array_equal(img[y, x], black):
                pixDistStart = int(totalDistance(x, y, inputX, inputY))
                if pixDistStart <= 5:
                    return True
    return False

def getdirection(inputX, inputY, x, y):
    yDistance = y - inputY
    xDistance = x - inputX
    if abs(yDistance) >= abs(xDistance):
        if y >inputY: return 3
        else: return 1
    else:
        if x > inputX: return 4
        else: return 2
    
    
def getMinDistance (img, dWinNum, inputX, inputY, score):
    FirstKey = 0 #used as flags for distance to not update min distince if no new values
    SecondKey = 0 #used as flags for distance to not update min distince if no new values
    direction = 0
    #print("DwinNum = %s"%(dWinNum))  #used for debugging
    if dWinNum == 36: #if the game is over return end game true, no currect dWin 36 in logic, game will never end
        return 36, 0, True
    else:
        for x in range(dWinList[dWinNum].xmin, dWinList[dWinNum].xmax):
            for y in range(dWinList[dWinNum].ymin, dWinList[dWinNum].ymax, -1):
                if np.array_equal(img[y, x], black):
                    yDistance = y - inputY
                    xDistance = x - inputX
                     #numpy.allclose(a, b, rtol=0, atol=3, equal_nan=False)
                    if yDistance <= 2 and xDistance <= 2: # a two pixel tolerance is added to the first window as a handicap for the user
                        score = score +1
                        pixDistFirst.clear()
                        pixDistSecond.clear()
                        pixDirFirst.clear()
                        pixDirSecond.clear()
                        return dWinNum, 0, False, score, direction
                    else:    
                        FirstKey += 1 #Counts up as the loop goes on so every value has a unquie key in the dict
                        totalDisOne = int(totalDistance(x, y, inputX, inputY)) #the distance of the user input from the black pixel is calculated
                        pixDistFirst.insert(FirstKey, totalDisOne) #the distance is stored in a dict with the "FirstKey" acting as the key
                        pixDirFirst[totalDisOne] =  getdirection(inputX, inputY, x, y) #A direction is stored with using the distance as its location in a list


        for x in range(dWinList[dWinNum+1].xmin, dWinList[dWinNum+1].xmax):
            for y in range(dWinList[dWinNum+1].ymin, dWinList[dWinNum+1].ymax, -1):
                if  np.array_equal(img[y, x],black):
                    if np.array_equal(img[y,x], [inputY, inputX]): #if the input is on a letter pixel add one to score and return
                        score = score +1
                        pixDistFirst.clear()
                        pixDistSecond.clear()
                        pixDirFirst.clear()
                        pixDirSecond.clear()
                        return dWinNum+1, 0, False, score, direction
                    else:
                        SecondKey += 1 #Counts up as the loop goes on so every value has a unquie key in the dict
                        totalDisTwo = int(totalDistance(x, y, inputX, inputY))
                        pixDistSecond.insert(SecondKey, totalDisTwo)
                        pixDirSecond[totalDisTwo] =  getdirection(inputX, inputY, x, y)
        
        if FirstKey != 0: 
            minPixDist.update({dWinNum: min(pixDistFirst)}) #the minimum distance from the first Dwin is taken
        else: minPixDist[dWinNum] = 1000 #used to asign a value to minPixDist if none was found 
        if SecondKey != 0: 
            minPixDist.update({dWinNum+1: min(pixDistSecond)})  #the minimum distance from the second Dwin is taken
        else: minPixDist[dWinNum+1] = 1000  #used to asign a value to minPixDist if none was found 
        if (minPixDist[dWinNum+1] + 1) < minPixDist[dWinNum]: #compares the two min distances
            direction = pixDirSecond[minPixDist[dWinNum+1]] #grabs the direction associated with the minimum distance
            #print ("Window#= %s, Distance = %s, direction = %s"% (dWinNum+1, minPixDist[dWinNum+1], direction))  #used for debugging
            pixDistFirst.clear()
            pixDistSecond.clear()
            pixDirFirst.clear()
            pixDirSecond.clear()
            return dWinNum+1, minPixDist[dWinNum+1], False, score, direction 
            #returns the new dWinNum, min distance, flag signaling the game is to continue, the current score, and direction
        #end the gmae here elif dwin 36 ... need to make it go to dwin 36 no current logic for a 36th decision window 
# =============================================================================
#         else:
#             return dWinNum, 0, True, score, direction 
# =============================================================================
        else:  
            direction = pixDirFirst[minPixDist[dWinNum]]
            #print ("Window#= %s, Distance = %s, direction = %s"% (dWinNum, minPixDist[dWinNum], direction)) #used for debugging
            pixDistFirst.clear()
            pixDistSecond.clear()
            pixDirFirst.clear()
            pixDirSecond.clear()
            return dWinNum, minPixDist[dWinNum], False, score, direction
        

############################################################# Main ########################################################
init()
#colorDwin(letter, dWinList) #used to color in the dWin black for debugging
broker = "192.168.43.175"
client = mqtt.Client("computer2")
client.connect(broker)
while True:
    cv2.imshow("Learn to Write!", letter)
    key = cv2.waitKey(1) & 0xFF
 
    # grab the current frame
    (grabbed, frame) = camera.read()
    frame = cv2.flip(frame, 1)

    # resize the frame, blur it, and convert it to the HSV color space
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color then perform a series of dilations and erosions to remove any small blobs left in the mask
    mask = cv2.inRange(hsv, colorLower, colorUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    #center = None #why is center none?

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        centerX = (int(M["m10"] / M["m00"])+50)
        centerY = (int(M["m01"] / M["m00"])+50)
        #print("X is %s, Y is %s"%(int(centerX),int(centerY))) #used for debugging
        #if centerX < 800 and centerY < 600: 
        if startFlag == False: #Wait until input is near Dwin 0 to start game
            cv2.circle(letter, (centerX, centerY), 1, (0, 0, 255), -1)
            startFlag = start(letter, centerX,centerY)
        else: 
            if oldStartFlag == False: #Clean the img on game start 
                oldStartFlag = True 
                letter = cv2.imread('bw_image.png', 1)
                winNum, pixDistance, endFlag, score, direction = getMinDistance(letter, winNum, centerX, centerY, score)
                cv2.circle(letter, (centerX, centerY), 1, (0, 0, 255), -1)
            else: #Play the game
                winNum, pixDistance, endFlag, score, direction = getMinDistance(letter, winNum, centerX, centerY, score)
                cv2.circle(letter, (centerX, centerY), 1, (0, 0, 255), -1)
                print ("Distance = %s, direction = %s, Win# %s"% (pixDistance, direction, winNum))
                msg = ("{0},{1}".format(direction, pixDistance))
                #send distance to arduino here!
                client.publish("motors",msg)

    

    cv2.imshow("Learn to Write!", letter)
    key = cv2.waitKey(1) & 0xFF

    # if the q key is pressed, stop the loop
    if key == ord("q") or endFlag == True:
        msg = ("{0},{1}".format(0, 0 ))
        client.publish("motors",msg)
        print("Your Score is %s letter pixels hit out of 611 letter pixels"%(score))
        break

camera.release()
cv2.destroyAllWindows()


###################################################################### ARCHIVE ###################################################################
#Below is a failed attempt at automating the creation of Decision Windows

# def isPixUp(img, y, x, wId):
#     y = y-3
#     for xw in range(x, x+2):
#         for yw in range(y-2, y):
#             if xw >= 1920: break
#             elif img[yw, xw] == 0:
#                 wId += 1   
#                 dWinList.append(Dwin(wId, y, y-3, x, x+3, 'u'))
#                 return y, x, wId 
#     return y, x, wId 

# def isPixUpperRight(img, y, x, wId):
#     y = y-3
#     x = x+3
#     for xw in range(x, x+2):
#         for yw in range(y-2, y):
#             if xw >= 1920: break
#             elif img[yw, xw] == 0:    
#                 wId += 1   
#                 dWinList.append(Dwin(wId, y, y-3, x, x+3, 'ur'))
#                 return y, x, wId 
#     return 0

# def isPixRight(img, y, x, wId):
#     x = x+5
#     for xw in range(x, x+4):
#         for yw in range(y-4, y+1):
#             if img[yw, xw] == 0: 
#                 wId += 1   
#                 dWinList.append(Dwin(wId, y, y-5, x, x+5, 'r'))
#                 return y, x, wId 
#     return 0

# def isPixLeft(img, y, x, wId):
#     x = x - 10
#     for xw in range(x, x+4):
#         for yw in range(y-4, y):
#             if img[yw, xw] == 0:
#                 wId += 1
#                 dWinList.append(Dwin(wId, y, y-5, x, x+5, 'l'))
#                 return y, x, wId 
#     return 0

# def isPixUpperLeft(img, y, x, wId):
#     y = y-5
#     x = x-5
#     for xw in range(x, x+4):
#         for yw in range(y-4, y):
#             if xw >= 1920: break
#             elif img[yw, xw] == 0:
#                 wId += 1
#                 dWinList.append(Dwin(wId, y, y-5, x, x+5, 'ul'))
#                 return y, x, wId 
#     return 0

# def isPixDown(img, y, x, wId):
#     y = y+5
#     for xw in range(x, x+4):
#         for yw in range(y-4, y):
#             if xw >= 1920: break
#             elif img[yw, xw] == 0:
#                 wId += 1
#                 dWinList.append(Dwin(wId, y, y-5, x, x+5, 'd'))
#                 return y, x, wId 
#     return 

# def isPixDownLeft(img, y, x, wId):
#     y = y+5
#     x = x-5
#     for xw in range(x, x+9):
#         for yw in range(y-9, y):
#             if xw >= 1920: break
#             elif img[yw, xw] == 0:
#                 wId += 1
#                 dWinList.append(Dwin(wId, y, y-5, x, x+5, 'dl'))
#                 return y, x, wId 
#     return 0

# def isPixDownRight(img, y, x, wId):
#     y = y+5
#     x = x+5
#     for xw in range(x, x+9):
#         for yw in range(y-9, y):
#             if xw >= 1920: break
#             elif img[yw, xw] == 0:    
#                 wId += 1   
#                 dWinList.append(Dwin(wId, y, y-5, x, x+5, 'dr'))
#                 return y, x, wId
#     return 0

# def createFirstDWindow(img, y, x, wId):
#     dWinList.append(Dwin(wId, y, y-5, x, x+5, 'fr')) #create first window at the most lower left pixel
#     return y, x, wId

# def initLetter(img, class_type = "Dwin"):
#     """Convert img to BW and Create Decision windows"""
#     #change the image to black and white
#     changeToBW(img)
#     # find the height, width, of the image
#     ys = img.shape[0]
#     xs = img.shape[1]
#     oneTimeFlag = 1
#     wId = 1
#     #iterate over image starting at bottom left to find most lower left pixel
#     x = 0
#     y = ys-1
#     while x < xs-1:
#         y = ys-1
#         while  y > 0:
#             if img[y, x] == 0:
#                 if oneTimeFlag:
#                     oneTimeFlag = 0
#                     y, x, wId = createFirstDWindow(img, y, x, wId)
#                     y, x, wId = isPixUp(img, y, x, wId)
#                     y, x, wId = isPixUpperRight(img, y, x, wId)
#                     y, x, wId = isPixUp(img, y, x, wId)
#                     y, x, wId = isPixUpperRight(img, y, x, wId)

                   
#                     return 
#             else:
#                 y -= 1
#         x += 1   
