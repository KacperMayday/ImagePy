import logging
import tkinter as tk

import cv2
import numpy as np
from PIL import Image

from lab4.filters import edge_detection_filters
from utils.constants import ImageModeEnum
from utils.image_manager import ImageWindow

logger = logging.getLogger(__name__)


def edge_detection(image_window: ImageWindow):
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None
    EdgeDetectionWidget(image_window)


class EdgeDetectionWidget(tk.Toplevel):
    def __init__(self, source_window: ImageWindow):
        super(EdgeDetectionWidget, self).__init__()
        self.title(source_window.window_title)
        self.image_window = source_window
        self.image = source_window.image
        self.geometry('300x150')
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        options = list(edge_detection_filters.keys())
        self.chosen_filter = tk.StringVar(value=options[0])
        tk.OptionMenu(self.frame, self.chosen_filter, *options).pack()

        tk.Button(self.frame, text='Reset', command=self.reset_image).pack()
        tk.Button(self.frame, text='Apply', command=self.update_image).pack()

        self.frame.pack()

    def reset_image(self):
        self.image_window.update_image(self.image)

    def update_image(self):
        filter_kernel = edge_detection_filters.get(self.chosen_filter.get(), list(edge_detection_filters.values())[0])

        image_array = np.array(self.image)
        filtered_image_array = cv2.filter2D(image_array, -1, np.array(filter_kernel))
        filtered_image = Image.fromarray(filtered_image_array.astype('uint8'), 'L')

        self.image_window.update_image(filtered_image)
