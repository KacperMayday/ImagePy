import tkinter as tk

import cv2
import numpy as np
from PIL import Image

from src.lab1.histogram import HistogramCanvas, HistogramWidget
from src.utils.constants import (MAX_INTENSITY_LEVEL, MIN_INTENSITY_LEVEL,
                                 ColourEnum, ImageModeEnum)
from src.utils.gui.widgets import GradientBar, SliderWidget
from src.utils.image_manager import ImageWindow
from src.utils.utils import ColourIterator


def threshold_filter(image_window: ImageWindow) -> None:
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None

    ThresholdWidget(image_window)


class ThresholdWidget(tk.Toplevel):
    def __init__(self, source_image_window: ImageWindow):
        super(ThresholdWidget, self).__init__()
        self.title(source_image_window.window_title)
        self.geometry("350x500")
        self.pack_propagate(False)
        self.image_window = source_image_window
        self.image = source_image_window.image
        self.histogram_max_height = 200
        self.frame = tk.Frame(self)

        colour = ColourEnum.GREYSCALE
        histogram_values = HistogramWidget.calculate_histogram_values(self.image)[
            colour
        ]
        self.histogram_canvas = HistogramCanvas(
            self.frame, colour, histogram_values, self.histogram_max_height
        )
        self.histogram_canvas.pack()
        gradient_bar = GradientBar(
            root=self.frame, height=10, colour_iterator=ColourIterator(colour)
        )
        gradient_bar.pack()
        self.lower_boundary_line = self.histogram_canvas.create_line(
            self.histogram_canvas.border_offset,
            self.histogram_canvas.border_offset,
            self.histogram_canvas.border_offset,
            self.histogram_max_height + self.histogram_canvas.border_offset,
            fill="red",
        )
        slider_lower_boundary = SliderWidget(
            self.frame, initial_value=MIN_INTENSITY_LEVEL
        )
        self.lower_boundary_variable = slider_lower_boundary.slider_variable
        slider_lower_boundary.pack()

        self.higher_boundary_line = self.histogram_canvas.create_line(
            MAX_INTENSITY_LEVEL + self.histogram_canvas.border_offset,
            self.histogram_canvas.border_offset,
            MAX_INTENSITY_LEVEL + self.histogram_canvas.border_offset,
            self.histogram_max_height + self.histogram_canvas.border_offset,
            fill="red",
        )
        slider_higher_boundary = SliderWidget(
            self.frame, initial_value=MAX_INTENSITY_LEVEL
        )
        self.higher_boundary_variable = slider_higher_boundary.slider_variable
        slider_higher_boundary.pack()

        self.is_binary = tk.BooleanVar()
        tk.Checkbutton(
            self.frame, text="Use binary threshold?", variable=self.is_binary
        ).pack()
        tk.Button(
            self.frame, text="Use Otsu threshold", command=self.otsu_threshold
        ).pack()
        tk.Button(
            self.frame, text="Use adaptive threshold", command=self.adaptive_threshold
        ).pack()
        tk.Button(self.frame, text="Reset", command=self.reset_image).pack()
        tk.Button(self.frame, text="Apply", command=self.destroy).pack()
        self.frame.pack()

        self.filters = [
            [self.lower_boundary_variable, "lower"],
            [self.higher_boundary_variable, "higher"],
        ]
        self.lower_boundary_variable.trace("w", self.update_threshold)
        self.higher_boundary_variable.trace("w", self.update_threshold)
        self.is_binary.trace("w", self.update_threshold)

    def otsu_threshold(self):
        img = np.array(self.image)
        ret, thresh1 = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        self.lower_boundary_variable.set(int(ret))
        self.higher_boundary_variable.set(255)
        self.is_binary.set(True)

    def adaptive_threshold(self):
        img = np.array(self.image)
        thresh1 = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        threshold_image = Image.fromarray(thresh1.astype("uint8"), "L")
        self.image_window.update_image(threshold_image)

    def reset_image(self):
        self.image_window.update_image(self.image)
        self.lower_boundary_variable.set(MIN_INTENSITY_LEVEL)
        self.higher_boundary_variable.set(MAX_INTENSITY_LEVEL)
        self.is_binary.set(False)

    def threshold_image(self):
        filtered_image = self.image.point(
            lambda p: self.threshold(
                p,
                self.lower_boundary_variable.get(),
                self.higher_boundary_variable.get(),
                MIN_INTENSITY_LEVEL,
                MAX_INTENSITY_LEVEL if self.is_binary.get() else p,
            )
        )
        self.image_window.update_image(filtered_image)

    def update_threshold(self, var: str, _b, _c):
        if self.lower_boundary_variable.get() > self.higher_boundary_variable.get():
            active_filter = None
            for f in self.filters:
                if var == f[0]._name:
                    active_filter = f[1]
            if active_filter == "higher":
                self.lower_boundary_variable.set(self.higher_boundary_variable.get())
            elif active_filter == "lower":
                self.higher_boundary_variable.set(self.lower_boundary_variable.get())

        self.histogram_canvas.coords(
            self.lower_boundary_line,
            self.lower_boundary_variable.get() + self.histogram_canvas.border_offset,
            self.histogram_canvas.border_offset,
            self.lower_boundary_variable.get() + self.histogram_canvas.border_offset,
            self.histogram_max_height + self.histogram_canvas.border_offset,
        )
        self.histogram_canvas.coords(
            self.higher_boundary_line,
            self.higher_boundary_variable.get() + self.histogram_canvas.border_offset,
            self.histogram_canvas.border_offset,
            self.higher_boundary_variable.get() + self.histogram_canvas.border_offset,
            self.histogram_max_height + self.histogram_canvas.border_offset,
        )
        self.threshold_image()

    @staticmethod
    def threshold(
        pixel_value: int,
        min_threshold_level: int,
        max_threshold_level: int,
        min_intensity_level: int,
        max_intensity_level: int,
    ) -> int:
        if min_threshold_level <= pixel_value <= max_threshold_level:
            return max_intensity_level
        else:
            return min_intensity_level
