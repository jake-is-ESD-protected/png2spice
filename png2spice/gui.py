"""
This is a demo app using tkinter and PIL to detect the pasting of
an image into an app-window. It SHOULD support all platforms,
however installation is not out of the box with Linux distros.
ImageGrab relies on xclip, which has to be installed via
sudo apt-get install xclip for all ubuntu/debian related distros.
Tkinter SHOULD be a default install with any Python installation.
"""

import tkinter as tk
from PIL import ImageGrab
import io

class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screenshot Viewer Template")
        self.root.geometry("300x200")
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)
        self.root.bind("<Control-v>", self.on_ctrl_v)

    def on_ctrl_v(self, event):
        screenshot = ImageGrab.grabclipboard()
        if screenshot:
            image_bytes = io.BytesIO()
            screenshot.save(image_bytes, format='PNG')
            image = tk.PhotoImage(data=image_bytes.getvalue())
            self.image_label.config(image=image)
            self.image_label.image = image

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()
