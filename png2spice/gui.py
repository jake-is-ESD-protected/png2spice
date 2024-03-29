"""
This is a demo app using tkinter and PIL to detect the pasting of
an image into an app-window. It SHOULD support all platforms,
however installation is not out of the box with Linux distros.
ImageGrab relies on xclip, which has to be installed via
sudo apt-get install xclip for all ubuntu/debian related distros.
Tkinter SHOULD be a default install with any Python installation.
"""

import tkinter as tk
from tkinter import filedialog, ttk
from PIL import ImageGrab, ImageTk, Image
import io
import lines
import cv2
import inference
from os.path import join, exists
import os
from graphing import CGraph
from parsing import CParser
from ocrtools import get_scaling_from_OCR
from parameters import P2SParameters
import numpy as np

class ScreenshotApp:
    def __init__(self, root):
        """
        Open a `tkinter` app for pasting and analyzing a supplied image.
        UI elements are commented in place.
        """
        self.root = root
        self.root.title("PNG2Spice")
        self.root.geometry("800x600")

        # Left panel
        ## base frame
        self.left_frame = tk.Frame(root, bd=2, relief="solid")
        self.left_frame.place(relx=0, rely=0, relwidth=0.8, relheight=1)
        
        ## image frame
        self.image_label = tk.Label(self.left_frame)
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")

        # Right panel
        ## base frame
        self.right_frame = tk.Frame(root, bd=2, relief="solid")
        self.right_frame.place(relx=0.8, rely=0, relwidth=0.2, relheight=1)
        
        ## Analyze button
        self.analyze_button = tk.Button(self.right_frame, text="Analyze", command=self.analyze)
        self.analyze_button.pack(pady=10)
        
        ## Path select button
        self.folder_path_button = tk.Button(self.right_frame, text="Select Folder", command=self.open_folder_dialog)
        self.folder_path_button.pack(pady=10)

        ## key-stroke callback registration
        self.root.bind("<Control-v>", self.on_ctrl_v)

        ## run-time variables
        self.folder_path = os.getcwd()
        self.input_path = join(self.folder_path, "input.png")

        self.poi_image_path = join(os.getcwd(), "temp", "randomSubFolder")
        if not os.path.exists(self.poi_image_path):
            try:
                os.makedirs(self.poi_image_path)
            except OSError as e:
                print(f"Error creating subdirectory {self.poi_image_path}: {e}")


    def on_ctrl_v(self, event):
        """
        Upon pasting an image from the clipboard into the left panel
        of the app, the image is saved to a temporary folder and diplayed
        in scaled fashion inside of the app window.
        """
        screenshot = ImageGrab.grabclipboard()
        if screenshot:
            max_width, max_height = self.left_frame.winfo_width() - 40, self.left_frame.winfo_height() - 40
            original_width, original_height = screenshot.size
            ratio = min(max_width/original_width, max_height/original_height)
            new_width, new_height = int(original_width*ratio), int(original_height*ratio)
            displayScreenshot = screenshot.resize((new_width, new_height))

            image_bytes = io.BytesIO()
            displayScreenshot.save(image_bytes, format='PNG')
            screenshot.save(self.input_path, format="PNG")
            image = ImageTk.PhotoImage(data=image_bytes.getvalue())
            self.image_label.config(image=image)
            self.image_label.image = image

            self.image_label.place(relx=0.5, rely=0.5, anchor="center")


    def open_folder_dialog(self):
        """
        The `Select Folder` button will trigger this callback, which will open
        a file dialog. Upon choosing a folder, it will be stored and used for both
        the working resources for the classification process as well as the
        output file. 
        """
        selected_path = filedialog.askdirectory()
        if selected_path:
            self.folder_path = selected_path
            self.poi_image_path = join(self.folder_path, "POIs", "snapshots")
        print("Selected folder:", self.folder_path)


    def analyze(self):
        """
        The `Analyze` button will trigger this callback. At first, the temporary
        image stored in `on_ctrl_v()` will be consumed. Then, the process will walk 
        through 6 stages described below in the `dict` `stages`. Each stage updates
        a progress bar. The stages are described in detail in the paper for this
        project.
        """
        if not exists(self.input_path):
            Warning("No image in buffer!")
            return
        
        stages = dict({
            "Normalizing image": self.stage1,
            "Extracting lines": self.stage2,
            "Launching SPICEnet": self.stage3,
            "Classify POIs": self.stage4,
            "Building graph": self.stage5,
            "Parsing and exporting": self.stage6})
        
        i = 0
        step = 100 // len(stages.keys())
        progress_dialog = ProgressDialog(self.root)

        for stage, label in zip(list(stages.values()), list(stages.keys())):
            progress_dialog.update_progress(i, f"{label}... {i}%")
            stage()
            i += step
        
        progress_dialog.destroy()

    def stage1(self):
        """
        Data import and normalization stage.
        """
        print(self.input_path)
        scalingFactor = get_scaling_from_OCR(self.input_path, threshold=15, letter_to_part_ratio=1/3)

        P2SParameters.setScalingFactor(scalingFactor * -0.5215 + 0.088)
        
        img = lines.imageDataFromPath(self.input_path)
        self.img = lines.normalizeImageData(img)
        os.remove(self.input_path)


    def stage2(self):
        """
        Line extraction and POI localization stage. 
        """
        if not os.path.exists(self.poi_image_path):
            try:
                os.makedirs(self.poi_image_path)
            except OSError as e:
                print(f"Error creating subdirectory {self.poi_image_path}: {e}")
        self.HLs = lines.getHoughLines(self.img, spath=self.poi_image_path)


    def stage3(self):
        """
        SPICEnet instanciation stage.
        """
        self.SPICEnet = inference.CSPICEnet(join(os.getcwd(), "SPICEnet"))


    def stage4(self):
        """
        SPICEnet inference stage.
        """
        self.preds, self.ocrs = self.SPICEnet.predict(self.folder_path)
    

    def stage5(self):
        """
        Graph building stage.
        """
        self.graph = CGraph(self.HLs, self.preds, self.ocrs)
        self.graph.rmDuplicates()
        self.graph.link()
        self.graph.analyzeRotations()
        self.graph.snapToGrid()
        self.graph.alignToGrid()
    

    def stage6(self):
        """
        Parsing and export stage.
        """
        parser = CParser(self.graph)
        output_path = join(self.folder_path, "output.asc")
        dir = os.listdir(os.getcwd())
        if(output_path in dir):
            os.remove(os.path.join(os.getcwd(), output_path))

        parser.Graph2Asc(output_path)



class ProgressDialog(tk.Toplevel):
    def __init__(self, parent):
        """
        Progress bar pop-up for the `analyze()` function. Displays the progress as
        percent and descriptions of the stages.
        """
        super().__init__(parent)

        self.title("Progress")
        self.geometry("300x100")

        self.progress = ttk.Progressbar(self, length=200, mode="determinate")
        self.progress.pack(pady=20)

        self.progress_text = tk.Label(self, text="")
        self.progress_text.pack()

        self.grab_set()

    def update_progress(self, value, text):
        self.progress["value"] = value
        self.progress_text["text"] = text
        self.update()


root = tk.Tk()
app = ScreenshotApp(root)
root.mainloop()
