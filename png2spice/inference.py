"""
This submodule of **png2spice** deals with inferencing SPICEnet and
integrating its results into the entire process. Application access
to SPICEnet is managed via a virtual representation as its own 
class. This class is not part of the standalone SPICEnet project/repo
and only exists within the context of **png2spice**.
"""

from keras.applications.vgg16 import preprocess_input
from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
from parameters import P2SParameters
from os.path import join
import os
import re
from PIL import Image
import json
from ocrtools import read_part_OCR


class CSPICEnet:
    def __init__(self, path: str) -> None:
        """
        BRIEF
        -----
        Abstraction object for the SPICEnet neural network.

        PARAMETERS
        ----------
        `path`:
            `str`. Path to the saved SPICEnet model in `.h5` format.

        """
        self.model = load_model(join(path, "SPICEnet.h5"))
        self.imgResize = int(P2SParameters.imageSliceSize * P2SParameters.scalingFactor * 1.37)
        self.dataGenerator = ImageDataGenerator(
            rescale=1./255
        )
        with open(join(path, "CLASSLIST.json")) as f:
            self.classlist = json.load(f)["class_list"]
    

    def __predictRaw(self, path: str) -> np.ndarray:
        """
        BRIEF
        -----
        Get the raw output of the SPICEnet inference.
        
        PARAMETERS
        ----------
        `path`:
            `str`. Path to the folder containing the data.
            Since `keras` is used, the folder above the folder(s)
            containing the data is expected.

        RETURNS
        -------
        `np.ndarray`. Always of shape `(nPOIs, nClasses)`.
        """
        pred = self.model.predict(
            ImageDataGenerator(
                preprocessing_function=preprocess_input,
                ).flow_from_directory(
                    path,
                    target_size=(self.imgResize, self.imgResize),
                    shuffle=False)
        )
        return pred
    

    def predict(self, path: str, ocr: bool=True, show: bool=False):
        """
        BRIEF
        -----
        Get the predictions from the inference of SPICEnet.
        
        PARAMETERS
        ----------
        `path`:
            `str`. Path to the folder containing the data.
            Since `keras` is used, the folder above the folder(s)
            containing the data is expected.
        `ocr`:
            `bool`. Perform OCR on the POI snapshots in addition
            to the classification.
        `show`:
            `bool`. Show a plot listing all detected POIs and their
            classifications. The used plotting backend has to be configured 
            outside this function.
        
        RETURNS
        -------
        `dict`(1), [`dict`](2). Dict of dicts (1). Upper dict contains the labels of the POIs and
        their sub-dicts. These consist of the component class names and their
        probability per class. If `ocr` is set to `True`, a dict (2) of the OCR results
        is returned as well. Both dicts have the same keys.
        """
        preds = self.__predictRaw(path)
        imageDisplayGenerator = self.dataGenerator.flow_from_directory(
            path,
            target_size=(self.imgResize, self.imgResize),
            shuffle=False,
            batch_size=100)
        fileLabels =  [os.path.basename(s).replace('.png', '') for s in imageDisplayGenerator.filenames]

        if ocr:
            OCRNameResults = dict()
            for file, label in zip(imageDisplayGenerator.filenames, fileLabels):
                partOcr = read_part_OCR(join(path, file))
                if partOcr != None:
                    OCRNameResults[f"{label}"] = partOcr

        batch_images = imageDisplayGenerator.next()[0]

        predDict = dict()
        for pred, label in zip(preds, fileLabels):
            classDict = dict()
            for classVal, className in zip(pred, self.classlist):
                classDict[className] = classVal
            predDict[label] = classDict

        if show:
            rowColSplit = int(np.sqrt(int(imageDisplayGenerator.n)))
            fig, axs = plt.subplots(nrows=rowColSplit, ncols=rowColSplit, figsize=(40, 20))
            ind = 0
            for ax1 in axs:
                for ax2 in ax1:
                    ax2.imshow(batch_images[ind])
                    partsFormat = " ".join([part[:3] + "%.2f\n" % preds[ind][i] for i, part in enumerate(self.classlist)])
                    ax2.text(1.05, 0.5, partsFormat, verticalalignment='center', horizontalalignment='left', transform=ax2.transAxes)
                    ax2.set_title(str(fileLabels[ind]))
                    ax2.set_xticks([])
                    ax2.set_yticks([])
                    ind += 1

            fig.suptitle('Component Classifaction')
            plt.tight_layout()
            plt.show()
        if ocr:
            return predDict, OCRNameResults
        else:
            return predDict
    

if __name__ == "__main__":
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from pprint import pprint

    SPICEnet = CSPICEnet("../SPICEnet")
    p = SPICEnet.predict(join(P2SParameters.partSnapshotDir, ".."), show=True)
    pprint(p)