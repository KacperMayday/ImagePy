import logging
import tkinter as tk
from dataclasses import asdict, dataclass

import cv2
import numpy as np
from PIL import Image

from lab4.filters import edge_detection_filters, prewitt_filters
from utils.constants import ImageModeEnum
from utils.gui.widgets import BorderFillWidget, SliderWidget
from utils.image_manager import ImageWindow

logger = logging.getLogger(__name__)


def edge_detection(image_window: ImageWindow, advanced_filter: bool = False, canny_detection: bool = False):
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None

    if advanced_filter:
        AdvancedEdgeDetectionWidget(image_window)
    elif canny_detection:
        CannyEdgeDetectionWidget(image_window)
    else:
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


@dataclass(frozen=True)
class AdvancedFilters:
    PREWITT: str = 'Prewitt'
    SOBEL: str = 'Sobel'


class AdvancedEdgeDetectionWidget(tk.Toplevel):
    def __init__(self, source_window: ImageWindow):
        super(AdvancedEdgeDetectionWidget, self).__init__()
        self.title(source_window.window_title)
        self.image_window = source_window
        self.image = source_window.image
        self.geometry('300x250')
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        options = list(asdict(AdvancedFilters()).values())
        self.chosen_filter = tk.StringVar(value=options[0])
        tk.OptionMenu(self.frame, self.chosen_filter, *options).pack()

        self.exact_results = tk.BooleanVar(value=True)
        tk.Checkbutton(self.frame, text='Use exact results?', variable=self.exact_results).pack()

        self.border_widget = BorderFillWidget(self.frame)
        self.border_widget.pack()

        tk.Button(self.frame, text='Reset', command=self.reset_image).pack()
        tk.Button(self.frame, text='Apply', command=self.update_image).pack()

        self.frame.pack()

    def reset_image(self):
        self.image_window.update_image(self.image)

    def update_image(self):
        image_array = np.array(self.image)

        match self.chosen_filter.get():
            case AdvancedFilters.SOBEL:
                grad_x = self.border_widget.apply_border_fill(image_array, 1, cv2.Sobel, ddepth=-1, dx=1, dy=0) \
                    .astype(float)
                grad_y = self.border_widget.apply_border_fill(image_array, 1, cv2.Sobel, ddepth=-1, dx=0, dy=1) \
                    .astype(float)
                if self.exact_results.get():
                    filtered_image_array = np.sqrt(grad_x ** 2 + grad_y ** 2)
                else:
                    filtered_image_array = np.abs(grad_x) + np.abs(grad_y)

            case AdvancedFilters.PREWITT:
                grad_x = self.border_widget.apply_border_fill(image_array, 1, cv2.filter2D, ddepth=-1,
                                                              kernel=np.array(prewitt_filters['x'])).astype(float)
                grad_y = self.border_widget.apply_border_fill(image_array, 1, cv2.filter2D, ddepth=-1,
                                                              kernel=np.array(prewitt_filters['y'])).astype(float)
                if self.exact_results.get():
                    filtered_image_array = np.sqrt(grad_x ** 2 + grad_y ** 2)
                else:
                    filtered_image_array = np.abs(grad_x) + np.abs(grad_y)

            case _:
                raise ValueError()

        filtered_image = Image.fromarray(filtered_image_array.astype('uint8'), 'L')
        self.image_window.update_image(filtered_image)


class CannyEdgeDetectionWidget(tk.Toplevel):
    def __init__(self, source_window: ImageWindow):
        super(CannyEdgeDetectionWidget, self).__init__()
        self.title(source_window.window_title)
        self.image_window = source_window
        self.image = source_window.image
        self.geometry('300x250')
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        tk.Label(text='Minimal threshold:')
        self.slider = SliderWidget(self, 0, 0, None, 255)
        self.slider.pack()

        self.border_widget = BorderFillWidget(self.frame)
        self.border_widget.pack()

        tk.Button(self.frame, text='Reset', command=self.reset_image).pack()
        tk.Button(self.frame, text='Apply', command=self.update_image).pack()

        self.frame.pack()

    def reset_image(self):
        self.image_window.update_image(self.image)

    def update_image(self):
        image_array = np.array(self.image)
        threshold_value = self.slider.get()
        filtered_image_array = self.border_widget.apply_border_fill(image_array, 1, cv2.Canny,
                                                                    threshold1=threshold_value,
                                                                    threshold2=threshold_value * 3,
                                                                    apertureSize=3)

        filtered_image = Image.fromarray(filtered_image_array.astype('uint8'), 'L')
        self.image_window.update_image(filtered_image)
