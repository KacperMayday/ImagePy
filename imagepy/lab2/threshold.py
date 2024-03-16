import tkinter as tk
from typing import Any

import cv2
import numpy as np
from PIL import Image

from imagepy.lab1.histogram import HistogramCanvas, HistogramWidget
from imagepy.utils.constants import (
    MAX_INTENSITY_LEVEL,
    MIN_INTENSITY_LEVEL,
    ColorEnum,
    ImageModeEnum,
)
from imagepy.utils.gui.widgets import GradientBar, SliderWidget
from imagepy.utils.image_manager import ImageWindow
from imagepy.utils.utils import ColorIterator


def threshold_filter(image_window: ImageWindow | None) -> None:
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
        self.widget_frame: tk.Frame = tk.Frame(self)

        color = ColorEnum.GREYSCALE
        histogram_values = HistogramWidget.calculate_histogram_values(self.image)[color]
        self.histogram_canvas = HistogramCanvas(
            self.widget_frame, color, histogram_values, self.histogram_max_height
        )
        self.histogram_canvas.pack()
        gradient_bar = GradientBar(
            root=self.widget_frame, height=10, color_iterator=ColorIterator(color)
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
            self.widget_frame,
            initial_value=MIN_INTENSITY_LEVEL,
            slider_var_flag=True,
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
            self.widget_frame,
            initial_value=MAX_INTENSITY_LEVEL,
            slider_var_flag=True,
        )
        self.higher_boundary_variable = slider_higher_boundary.slider_variable
        slider_higher_boundary.pack()

        self.is_binary = tk.BooleanVar()
        tk.Checkbutton(
            self.widget_frame, text="Use binary threshold?", variable=self.is_binary
        ).pack()
        tk.Button(
            self.widget_frame, text="Use Otsu threshold", command=self.otsu_threshold
        ).pack()
        tk.Button(
            self.widget_frame,
            text="Use adaptive threshold",
            command=self.adaptive_threshold,
        ).pack()
        tk.Button(self.widget_frame, text="Reset", command=self.reset_image).pack()
        tk.Button(self.widget_frame, text="Apply", command=self.destroy).pack()
        self.widget_frame.pack()

        self.filters = (
            (self.lower_boundary_variable, "lower"),
            (self.higher_boundary_variable, "higher"),
        )
        self.lower_boundary_variable.trace("w", self.update_threshold)
        self.higher_boundary_variable.trace("w", self.update_threshold)
        self.is_binary.trace("w", self.update_threshold)

    def otsu_threshold(self) -> None:
        img = np.array(self.image)
        ret, thresh1 = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        self.lower_boundary_variable.set(int(ret))
        self.higher_boundary_variable.set(255)
        self.is_binary.set(True)

    def adaptive_threshold(self) -> None:
        img = np.array(self.image)
        thresh1 = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        threshold_image = Image.fromarray(thresh1.astype("uint8"), "L")
        self.image_window.update_image(threshold_image)

    def reset_image(self) -> None:
        self.image_window.update_image(self.image)
        self.lower_boundary_variable.set(MIN_INTENSITY_LEVEL)
        self.higher_boundary_variable.set(MAX_INTENSITY_LEVEL)
        self.is_binary.set(False)

    def threshold_image(self) -> None:
        filtered_image = self.image.point(
            lambda p: self.threshold(
                p,
                int(self.lower_boundary_variable.get()),
                int(self.higher_boundary_variable.get()),
                MIN_INTENSITY_LEVEL,
                MAX_INTENSITY_LEVEL if self.is_binary.get() else p,
            )
        )
        self.image_window.update_image(filtered_image)

    def update_threshold(self, var: str, _b: Any = None, _c: Any = None) -> None:
        if self.lower_boundary_variable.get() > self.higher_boundary_variable.get():
            active_filter = None
            for f in self.filters:
                if var == f[0]._name:  # type: ignore  # noqa
                    active_filter = f[1]
            if active_filter == "higher":
                self.lower_boundary_variable.set(
                    int(self.higher_boundary_variable.get())
                )
            elif active_filter == "lower":
                self.higher_boundary_variable.set(
                    int(self.lower_boundary_variable.get())
                )

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
