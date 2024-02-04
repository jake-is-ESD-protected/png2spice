"""
This submodule of **png2spice** deals with the extraction of horizontal
and vertical lines of a given image of an electrical schematic. Additionally,
the obtained lines also yield the positions of the components, which are saved
to a temporary folder for later classification by SPICEnet.
"""

from parameters import P2SParameters
import cv2
import numpy as np
import math
from os.path import join
import os


def imageDataFromPath(path: str) -> cv2.typing.MatLike:
    """
    BRIEF
    -----
    Load an image (schematic) screenshot in `.png` format into
    a `MatLike` representation. The coding is fixed as grayscale.

    PARAMETERS
    ----------
    `path`:
        `str`. Path to image to be analyzed.
    
    RETURNS
    -------
    `cv2.typing.MatLike`. Image as `cv2` matrix.
    """
    return cv2.imread(path, cv2.IMREAD_GRAYSCALE)


def normalizeImageData(img: cv2.typing.MatLike) -> cv2.typing.MatLike:
    """
    BRIEF
    -----
    Apply contrast thresholding and bordering to `MatLike` image data.

    PARAMETERS
    ----------
    `img`:
        `cv2.typing.MatLike`. Image data matrix to be normalized.

    RETURNS
    -------
    `cv2.typing.MatLike`. Image as `cv2` matrix.

    NOTES
    -----
    Contains **P2S parameters** `imagePadding` and `contrastThreshold`.
    See `png2spice.parameters`. 
    """
    _, img = cv2.threshold(img, 
                           P2SParameters.contrastThreshold, 
                           255, 
                           cv2.THRESH_BINARY)
    
    pad = P2SParameters.imagePadding
    img = cv2.copyMakeBorder(img, 
                            pad,
                            pad,
                            pad,
                            pad,
                            cv2.BORDER_CONSTANT,
                            value=255)
    return img


def getHoughLines(img: cv2.typing.MatLike, rmDuplicates: bool=True, show: bool=False, spath: str=P2SParameters.partSnapshotDir) -> np.ndarray:
    """
    BRIEF
    -----
    Obtain the detected Hough-lines from an image data matrix.

    PARAMETERS
    ----------
    `img`:
        `cv2.typing.MatLike`. Image data matrix to be analyzed.
    `rmDuplicates`:
        `bool`. Remove lines which are too similar to each other. For threshold
        settings, see @NOTES.
    `show`:
        `bool`. Show the detected lines over the input image. The used plotting
        backend has to be configured outside this function.
    `spath`:
        `str`. Path to save the screenshots of POIs derived from the Hough
        lines.

    RETURNS
    -------
    `np.ndarray`. Detected Hough-lines of input image. Always of shape
    `(n_lines, 4)` (x/y coordinates of the start- and end-point of a line).

    NOTES
    -----
    Contains **P2S parameters** `cannyThreshold`, `HLThreshold`,
    `HLMinLineLength`, `HLmaxLineGap`, `HoughIterations` and `imageSliceSize`.
    See `png2spice.parameters`. 
    """
    cannyThresh = P2SParameters.cannyThreshold
    HLThresh = P2SParameters.HLThreshold
    HLMinLineLen = P2SParameters.HLMinLineLength
    HLmaxLineGap = P2SParameters.HLmaxLineGap
    HLIterations = P2SParameters.HoughIterations
    imgSliceSize = P2SParameters.imageSliceSize

    linesImage = np.zeros((img.shape + (tuple([3]))), np.uint8)
    edges = cv2.Canny(img, cannyThresh, cannyThresh, None, 5)
    
    lines = [cv2.HoughLinesP(edges, 
                             rho=1, 
                             theta=np.pi/2, 
                             threshold=HLThresh + ((i+1) * HLIterations), minLineLength=HLMinLineLen, 
                             maxLineGap=HLmaxLineGap
                            ).squeeze() for i in range(HLIterations)]
    lines = np.concatenate(lines, axis=0)

    if rmDuplicates:
        lines = pruneLines(lines)

    if show:
        linesImage = np.zeros((img.shape + (tuple([3]))), np.uint8)
    
    for count, line in enumerate(lines):
        pt1 = (line[0],line[1])
        pt2 = (line[2],line[3])
        saveImageFromPos(img.copy(), pt1[0],pt1[1], imgSliceSize, str(count) + 'A', spath)
        saveImageFromPos(img.copy(), pt2[0],pt2[1], imgSliceSize, str(count) + 'B', spath)
        if show:
            cv2.line(linesImage, pt1, pt2, (0,0,255), 4)
            cv2.circle(linesImage, pt1, 2, (255,0,0), 3)
            cv2.circle(linesImage, pt2, 2, (0,255,0), 3)
    
    if show:
        _, ax = plt.subplots()
        ax.imshow(img,cmap='gray')
        ax.imshow(linesImage, alpha=0.5)
        plt.show()
    
    return lines
        



def saveImageFromPos(img: cv2.typing.MatLike, x: int, y: int, winSize: int, name: str, spath: str):
    """
    BRIEF
    -----
    Save a graphical square box around a specified point on an image as seperate image.

    PARAMETERS
    ----------
    `img`:
        `cv2.typing.MatLike`. Image data matrix to be analyzed.
    `x`:
        `int`. Center point x-coordinate of box.
    `y`:
        `int`. Center point y-coordinate of box.
    `winSize`:
        `int`. Size of square box in pixels.
    `name`:
        `str`. Name and therefore destination path for image.
    `spath`:
        `str`. Path to save location.
    """
    if not os.path.exists(spath):
        try:
            os.makedirs(spath)
        except OSError as e:
            print(f"Error creating subdirectory {spath}: {e}")

    yMax, xMax = img.shape
    if(x+int(winSize/2) > xMax or y+int(winSize/2) > yMax or x-int(winSize/2) < 0 or y-int(winSize/2) < 0):
        return
    img = img[y-int(winSize/2):y+int(winSize/2), x-int(winSize/2):x+int(winSize/2)]
    fname = join(spath, str(name) + ".png")
    cv2.imwrite(fname, img)


def hasSimilairLineInList(lineList: list, line: np.ndarray):
    """
    BRIEF
    -----
    Check whether a given line is similar to another line in the list
    of lines.

    PARAMETERS
    ----------
    `lineList`:
        `list`. List of lines to scan through.
    `line`:
        `np.ndarray`. Line as represented in start- and end-point coordinates.
        `(x1, y1, x2, y2)`.

    RETURNS
    -------
    `bool`. Truth of similarity.

    NOTES
    -----
    Contains **P2S parameters** `pointDistance`.
    See `png2spice.parameters`. 
    """
    dist = P2SParameters.pointDistance
    for l in lineList:
        pt1 = (l[0],l[1])
        pt2 = (l[2],l[3])
        pt3 = (line[0],line[1])
        pt4 = (line[2],line[3])
        if((math.dist(pt1, pt3) < dist and math.dist(pt2, pt4) < dist) or ((math.dist(pt1, pt4) < dist and math.dist(pt2, pt3) < dist))):
            return True
    return False


def pruneLines(lines: np.ndarray) -> np.ndarray:
    """
    BRIEF
    -----
    Remove duplicate lines in the list of lines.

    PARAMETERS
    ----------
    `lines`:
        `np.ndarray`. List of lines containing duplicates.
    
    RETURNS
    -------
    `np.ndarray`. Modified input array without duplicates.
    """
    prunedLinesList = []
    prunedLinesList.append(lines[1].tolist())
    for line in lines:
        if(not hasSimilairLineInList(prunedLinesList,line)):
            prunedLinesList.append(line.tolist())
    return np.asarray(prunedLinesList)


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt

    img = imageDataFromPath(join("testSchematicsPNG", "schematic1.JPG"))
    img = normalizeImageData(img)
    HLs = getHoughLines(img, show=True)
    print(f"Detected {np.shape(HLs)[0]} Hough lines")

