import logging
import tkinter as tk

import cv2
import numpy
from PIL import Image

from lab4.filters import blur_filters, sharpen_filters
from utils.constants import ImageModeEnum
from utils.gui.widgets import BorderFillWidget
from utils.image_manager import ImageWindow

logger = logging.getLogger(__name__)


def filter_calculation(image_window: ImageWindow, blur_flag: bool):
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None
    if blur_flag:
        BlurWidget(image_window)
    else:
        SharpenWidget(image_window)


class BlurWidget(tk.Toplevel):
    def __init__(self, source_window: ImageWindow):
        super(BlurWidget, self).__init__()
        self.title(source_window.window_title)
        self.image_window = source_window
        self.image = source_window.image
        self.geometry('300x250')
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        self.chosen_filter = tk.StringVar(value='0')
        options = list(range(len(blur_filters)))
        tk.Label(self.frame, text='Choose kernel:').pack()
        tk.OptionMenu(self.frame, self.chosen_filter, *options).pack()

        self.border_widget = BorderFillWidget(self.frame)
        self.border_widget.pack()

        tk.Button(self.frame, text='Reset', command=self.reset_image).pack()
        tk.Button(self.frame, text='Apply', command=self.update_image).pack()

        self.frame.pack()

    def reset_image(self):
        self.image_window.update_image(self.image)

    def update_image(self):
        image_array = numpy.array(self.image)
        kernel = numpy.array(blur_filters[int(self.chosen_filter.get())])
        kernel_sum = kernel.sum()
        kernel = kernel / kernel_sum if kernel_sum else kernel

        modified_image_array = self.border_widget.apply_border_fill(image_array, kernel, cv2.filter2D)
        modified_image = Image.fromarray(modified_image_array.astype('uint8'), 'L')

        self.image_window.update_image(modified_image)


class SharpenWidget(tk.Toplevel):
    def __init__(self, source_window: ImageWindow):
        super(SharpenWidget, self).__init__()
        self.title(source_window.window_title)
        self.image_window = source_window
        self.image = source_window.image
        self.geometry('300x250')
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        self.chosen_filter = tk.StringVar(value='0')
        options = list(range(len(sharpen_filters)))
        tk.Label(self.frame, text='Choose kernel:').pack()
        tk.OptionMenu(self.frame, self.chosen_filter, *options).pack()

        self.border_widget = BorderFillWidget(self.frame)
        self.border_widget.pack()

        tk.Button(self.frame, text='Reset', command=self.reset_image).pack()
        tk.Button(self.frame, text='Apply', command=self.update_image).pack()

        self.frame.pack()

    def reset_image(self):
        self.image_window.update_image(self.image)

    def update_image(self):
        image_array = numpy.array(self.image)
        kernel = numpy.array(sharpen_filters[int(self.chosen_filter.get())])

        modified_image_array = self.border_widget.apply_border_fill_2d(image_array, kernel, cv2.filter2D)
        modified_image = Image.fromarray(modified_image_array.astype('uint8'), 'L')

        self.image_window.update_image(modified_image)
