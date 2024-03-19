import logging
import tkinter as tk

import cv2
import numpy
from PIL import Image

from imagepy.lab4.filters import median_blur_filters
from imagepy.utils.constants import ImageModeEnum
from imagepy.utils.gui.widgets import BorderFillWidget
from imagepy.utils.image_manager import ImageWindow

logger = logging.getLogger(__name__)


def median_blur(image_window: ImageWindow | None) -> None:
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None
    MedianBlurWidget(image_window)


class MedianBlurWidget(tk.Toplevel):
    def __init__(self, source_window: ImageWindow):
        super(MedianBlurWidget, self).__init__()
        self.title(source_window.window_title)
        self.image_window = source_window
        self.image = source_window.image
        self.geometry("300x250")
        self.pack_propagate(False)
        self.widget_frame: tk.Frame = tk.Frame(self)

        self.chosen_filter = tk.StringVar(value=list(median_blur_filters.keys())[0])
        options = list(median_blur_filters.keys())
        tk.Label(self.widget_frame, text="Choose kernel size:").pack()
        tk.OptionMenu(self.widget_frame, self.chosen_filter, *options).pack()

        self.border_widget = BorderFillWidget(self.widget_frame)
        self.border_widget.pack()
        tk.Button(self.widget_frame, text="Reset", command=self.reset_image).pack()
        tk.Button(self.widget_frame, text="Apply", command=self.update_image).pack()

        self.widget_frame.pack()

    def reset_image(self) -> None:
        self.image_window.update_image(self.image)

    def update_image(self) -> None:
        filter_size = median_blur_filters.get(
            self.chosen_filter.get(), list(median_blur_filters.values())[0]
        )
        image_array = numpy.array(self.image)

        pad_size = (filter_size - 1) // 2
        blurred_image_array = self.border_widget.apply_border_fill(
            image_array, pad_size, cv2.medianBlur, ksize=filter_size
        )
        blurred_image = Image.fromarray(blurred_image_array.astype("uint8"), "L")

        self.image_window.update_image(blurred_image)
