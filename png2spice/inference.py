"""
This submodule of **png2spice** deals with inferencing SPICEnet and
integrating its results into the entire process.
"""

from keras.applications.vgg16 import preprocess_input
from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
from parameters import P2SParameters
from os.path import join
import os
from pytesseract import pytesseract
import re
from PIL import Image
import json

class CSPICEnet:
    def __init__(self, path: str) -> None:
        self.model = load_model(join(path, "SPICEnet.h5"))
        self.imgResize = 224
        self.dataGenerator = ImageDataGenerator(
            rescale=1./255
        )
        with open(join(path, "CLASSLIST.json")) as f:
            self.classlist = json.load(f)["class_list"]
    
    def __predictRaw(self, path: str) -> np.ndarray:
        pred = self.model.predict(
            ImageDataGenerator(
                preprocessing_function=preprocess_input,
                ).flow_from_directory(
                    path,
                    target_size=(self.imgResize, self.imgResize),
                    shuffle=False)
        )
        return pred
    
    def predict(self, path: str, show: bool=False):
        preds = self.__predictRaw(path)
        imageDisplayGenerator = self.dataGenerator.flow_from_directory(
            path,
            target_size=(self.imgResize, self.imgResize),
            shuffle=False,
            batch_size=100)
        fileLabels =  [os.path.basename(s).replace('.png', '') for s in imageDisplayGenerator.filenames]

        batch_images = imageDisplayGenerator.next()[0]

        fig, axs = plt.subplots(nrows=int(imageDisplayGenerator.n/4), ncols=4, figsize=(20, 15)) # define your figure and axes
        ind = 0
        for ax1 in axs:
            for ax2 in ax1:
                ax2.imshow(batch_images[ind])
                ax2.title.set_text(str(fileLabels[ind]) + " " + getType(preds[ind]) + "   R: %.2f C: %.2f I: %.2f D: %.2f \n Co: %.2f J: %.2f Cr: %.2f GND: %.2f" % (preds[ind][0],preds[ind][1],preds[ind][2],preds[ind][3],preds[ind][4],preds[ind][5],preds[ind][6],preds[ind][7]))
                ind += 1

        fig.suptitle('Component Classifaction')
        plt.tight_layout()
        plt.show()



    

if __name__ == "__main__":
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt

    SPICEnet = CSPICEnet("../SPICEnet")
    print(SPICEnet.classlist)
    # print(SPICEnet.predictRaw(join(P2SParameters.partSnapshotDir, "..")))