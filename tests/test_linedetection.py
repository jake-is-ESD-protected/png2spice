from schematicLT import linedetection
import os

BW_IMG_PATH = "./tests/images/schematic_bw.png"
LD_IMAGE_PATH = "./tests/images/schematic_linedetection.png"


def test_linedetection():
    img = linedetection.locateLines(BW_IMG_PATH)


def test_linedetection_save():
    img = linedetection.locateLines(BW_IMG_PATH, save_path=LD_IMAGE_PATH)
    assert os.path.exists(LD_IMAGE_PATH)
