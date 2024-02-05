from PIL import Image, ImageDraw
import pytesseract
import numpy as np
from scipy.stats import gaussian_kde
from IPython.display import display
import re

def localize_part_OCR(img_path: str, threshold: int=5, get_box_heights=False, show=False) -> list:
    """
    BRIEF
    -----
    Get the text and positions of detected text on the image within a certain
    confidence interval for box areas. This hinders the inclusion of wrong detections
    which are too big or small compared to the estimated size of actual letters. 

    PARAMS
    ------
    `img_path`: str
        Path to image.
    `threshold`: int
        Defines which values `threshold` lower than the peak are classified as valid.
    `get_box_heights`: bool
        Get an array of box heights which are within the given threshold.
    `show`: bool
        Display the boxes on the image with `IPython.display`.
    
    RETURNS
    -------
    `list`:
        List of valid boxes of shape `(text, x, y, w, h)` each.
    `list`, `list`:
        List of valid boxes of shape `(text, x, y, w, h)` each and the list of
        box heights which are within the given threshold if `get_box_heights`
        is set to `True`.
    """
    image = Image.open(img_path)
    width, height = image.size
    boxes = []
    box_heights = []
    data = pytesseract.image_to_boxes(image)

    if show:
        draw = ImageDraw.Draw(image)

    for box in data.splitlines():
        b = box.split()
        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        boxes.append(b)
        box_heights.append(h - y)
        if show:
            h_flip = height - y
            y_flip = height - h
            draw.rectangle([x, y_flip, w, h_flip], outline='red', width=2)
            draw.text((x, h_flip + 5), box[0], fill='red')

    kde = gaussian_kde(box_heights)
    x_vals = np.linspace(min(box_heights), max(box_heights), 1000)
    y_vals = kde(x_vals)
    peak_index = np.argmax(y_vals)
    peak_value = x_vals[peak_index]
    selected_values = [value for value in box_heights if abs(value - peak_value) <= threshold]
    valid_boxes = []

    for b, box_height in zip(boxes, box_heights):
        if box_height not in selected_values:
            if show:
                x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
                h_flip = height - y
                y_flip = height - h
                draw.rectangle([x, y_flip, w, h_flip], outline='blue', width=2)
        else:
            valid_boxes.append(b)

    if show:
        display(image)
    if get_box_heights:
        return valid_boxes, selected_values
    return valid_boxes
    

def read_part_OCR(img_path: str):
    """
    BRIEF
    -----
    Use OCR to read the letters on the schematic.

    PARAMS
    ------
    `img_path`: `str`
        Path to image.

    RETURNS
    -------
    `str`:
        String containing the found text if present.

    NOTES
    -----
    The searched letters depend on the regex listed below.
    """
    result = pytesseract.image_to_string(Image.open(img_path))
    resultPostRegex = re.search(r"[RCDL](\d+)", result, re.IGNORECASE)
    if(resultPostRegex != None):
        resultPostRegex = resultPostRegex.group().capitalize()
    return resultPostRegex


def get_scaling_from_OCR(img_path: str, threshold: int=5, letter_to_part_ratio: float=1/3) -> float:
    """
    BRIEF
    -----
    Get the estimated size of a component in relation to the image size in percent.
    This approach uses `pytesseract` to get the bounding boxes of the OCR-scan
    performed on the image. After that, the width of these boxes is used to form
    an interpolated gaussian distribution of widths, from which the peak and 
    values within a threshold are taken and calculated into a mean peak value. 
    This is then multiplied by the assumed relation of font-size and component-size
    and divided by the image width and returned as percent.

    PARAMS
    ------
    `img_path`: str
        Path to image.
    `threshold`: int
        Defines which values `threshold` lower than the peak are taken into the 
        mean-operation.
    `letter_to_part_ratio`: float
        Assumed size of letter in relation to component size.
    
    RETURNS
    -------
    `float`:
        Ratio of component size to image size.
    """
    image = Image.open(img_path)
    width, _ = image.size
    _, selected_values = localize_part_OCR(img_path, threshold, get_box_heights=True, show=False)
    print(selected_values)
    result_mean = np.mean(selected_values)
    return (1/letter_to_part_ratio) * result_mean / width
