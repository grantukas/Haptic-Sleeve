#Engineers: Sean Duback, Robert Geoffrion
#School: Weber State University 
#Project: Motion Tracking
#Year: 2019 Acidemic Year
import numpy as np 
import cv2
import xlwt

White = [255,255,255]
Black = [0,0,0]
nearBlack = [5,5,5]
pixColor = []



pixLoc = []
letter = cv2.imread('bw_image.png', 1) 

class PixelLocation(object):
    def __init__(self, pixNum=0, yLoc=0, xLoc=0, pixR=0, pixG=0, pixB =0):
        self.pixNum =pixNum
        self.yLoc= yLoc
        self.xLoc= xLoc
        self.pixR= pixR
        self.pixG= pixG
        self.pixB= pixB

 
def changeToBW (img):
    """Change image to Black and White"""
    # find the height, width, of the image
    ys = img.shape[0]
    xs = img.shape[1]
    #iterate over entire image starting at top left 
    for x in range(0, xs):
        for y in range(0, ys):
            pixC = img[y, x]
            if pixC > 5: #if a pixel is not black/near black make it true white
                img[y,x] = 255
            else: #if a pixel is black/near black make it true black
                img[y,x] = 0

def initLetter(img, class_type = "PixelLocation"):
 #change the image to black and white
    # find the height, width, of the image
    ys = img.shape[0]
    xs = img.shape[1]
    #iterate over image starting at bottom left to find most lower left pixel
    x = 0
    y = ys-1
    num = 0
    while x < xs-1:
        y = ys-1
        while  y > 0:
            #if  np.array_equal(img[y, x],Black):
            if np.array_equal(img[y, x],White) == False:
              #  num += 1
                pixLoc.append(PixelLocation(num, y, x))
            #    pixColor[num] = img[y,x]
                y -= 1
            else:
                y -= 1
        x += 1  



def excelOutput(filename, sheet, class_type = "PixelLocation"):
    i = 1
    book = xlwt.Workbook()
    sh = book.add_sheet(sheet)
    col1_name = 'Pixel Number'
    col2_name = 'Pixel Y value'
    col3_name = 'Pixel X value'
    col4_name = 'Pixel Color'

    sh.write(0, 0, col1_name)
    sh.write(0, 1, col2_name)
    sh.write(0, 2, col3_name)
    sh.write(0, 3, col4_name)

    for pixelLocation in pixLoc:
        i += 1
     #   sh.write(i+1, 3, pixColor[i])
        sh.write(i+1, 2, pixelLocation.xLoc)
        sh.write(i+1, 1, pixelLocation.yLoc)
        sh.write(i+1, 0, pixelLocation.pixNum)

    
    book.save(filename)


initLetter(letter, pixLoc)
excelOutput("letterPixelLocation.xls", '1', pixLoc)