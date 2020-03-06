#Engineers: Sean Duback, Robert Geoffrion
#School: Weber State University 
#Project: Motion Tracking
#Year: 2019 Acidemic Year
import numpy as np 
import cv2

white = [255,255,255]
black = [0,0,0]

im_gray = cv2.imread('ScriptLsmall.jpg', cv2.IMREAD_GRAYSCALE)
(thresh, im_bw) = cv2.threshold(im_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
cv2.imwrite('bw_image.jpg', im_bw)

letter2 = cv2.imread('bw_image.png', 1) 
for x in range(0, 799):
    for y in range(599, 0, -1):
        if (np.array_equal(letter2[y, x],white) == False) and (np.array_equal(letter2[y, x],black) == False):
            print ("Color = %s, x = %s, y = %s"%(letter2[y,x], x, y))

######################################################### Archive ###############################################################
## Below is a way to acomplish the same thing happening above
# white = [255,255,255]
# black = [0,0,0]
# nearBlack = [20,20,20]

# letter = cv2.imread('ScriptLsmall.jpg', 3) 
# def changeToBW (img):
#     """Change image to Black and White"""
#     # find the height, width, of the image
#     ys = img.shape[0]
#     xs = img.shape[1]
#     #iterate over entire image starting at top left 
#     for x in range(0, 799):
#         for y in range(599, 0, -1):
#             if ((np.array_equal(img[y, x],[1, 1, 1]) == True) or (np.array_equal(img[y, x],[2, 2, 2]) == True) or (np.array_equal(img[y, x],[3, 3, 3]) == True) or (np.array_equal(img[y, x],[4, 4, 4]) == True) or (np.array_equal(img[y, x],[5, 5, 5]) == True)):
#             #if np.allclose((img[y,x]), black, 50, 10): #if a pixel is not black/near black make it true white
#                 img[y,x] = black
#             else: #if a pixel is black/near black make it true black
#                 img[y,x] = white
#     filename = "BW_ScriptLsmall.jpg"
#     cv2.imwrite(filename, img)


# white = [255,255,255]
# black = [0,0,0]
# nearBlack = [5,5,5]
# letter = cv2.imread('ScriptLsmall.jpg', 1) 

# def changeToBW (img):
#     """Change image to Black and White"""
#     # find the height, width, of the image
#     ys = img.shape[0]
#     xs = img.shape[1]
#     #iterate over entire image starting at top left 
#     for x in range(0, xs):
#         for y in range(0, ys):
#             if np.allclose((img[y,x]), nearBlack, 5, 5): #if a pixel is not black/near black make it true white
#                 img[y,x] = black
#             else: #if a pixel is black/near black make it true black
#                 img[y,x] = white
#     cv2.imwrite('image.jpg', img)
#     letter2 = cv2.imread('image.jpg', 1) 
#     for x in range(0, 799):
#         for y in range(599, 0, -1):
#             if (np.array_equal(letter2[y, x],white) == False) and (np.array_equal(letter2[y, x],black) == False):
#                 print ("Color = %s, x = %s, y = %s"%(letter2[y,x], x, y))


# changeToBW(letter)