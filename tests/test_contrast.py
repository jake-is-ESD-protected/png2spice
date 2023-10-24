from schematicLT import preprocess
from PIL import Image
import os

RAW_IMG_PATH = "./tests/images/schematic.png"
BW_IMG_PATH = "./tests/images/schematic_bw.png"


def test_contrast():
    img = preprocess.contrast(RAW_IMG_PATH)
    assert isinstance(img, Image.Image)


def test_contrast_file_save():
    img = preprocess.contrast(RAW_IMG_PATH, save_path=BW_IMG_PATH)
    assert os.path.exists(BW_IMG_PATH)