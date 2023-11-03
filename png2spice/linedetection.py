# from here: https://www.geeksforgeeks.org/line-detection-python-opencv-houghline-method/
# Python program to illustrate HoughLine
# method for line detection
import cv2
import numpy as np

def locateLines(img_path: str, save_path: None=None):
    img = cv2.imread(img_path)
    edges = cv2.Canny(img, 50, 150, apertureSize=3)

    # This returns an array of r and theta values
    lines = cv2.HoughLines(edges, 1, np.pi/180, 200)

    # The below for loop runs till r and theta values
    # are in the range of the 2d array
    for r_theta in lines:
        arr = np.array(r_theta[0], dtype=np.float64)
        r, theta = arr
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*r
        y0 = b*r
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    if save_path != None:
        cv2.imwrite(save_path, img)

    return img