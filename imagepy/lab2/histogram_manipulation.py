import logging
import tkinter as tk
from typing import Any

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

logger = logging.getLogger(__name__)


def linear_adjustment(image_window: ImageWindow | None) -> None:
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None

    LinearAdjustmentWidget(image_window)


class LinearAdjustmentWidget(tk.Toplevel):
    def __init__(self, source_image_window: ImageWindow):
        super(LinearAdjustmentWidget, self).__init__()
        self.title(source_image_window.window_title)
        self.geometry("350x400")
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
        )
        self.lower_boundary_variable: tk.DoubleVar = slider_lower_boundary.slider_variable  # type: ignore
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
        )
        self.higher_boundary_variable: tk.DoubleVar = slider_higher_boundary.slider_variable  # type: ignore
        slider_higher_boundary.pack()
        self.filters = (
            (self.lower_boundary_variable, "lower"),
            (self.higher_boundary_variable, "higher"),
        )
        self.lower_boundary_variable.trace("w", self.update_threshold)
        self.higher_boundary_variable.trace("w", self.update_threshold)

        self.reset_button = tk.Button(
            self.widget_frame, text="Reset", command=self.reset_image
        )
        self.reset_button.pack()
        self.close_button = tk.Button(
            self.widget_frame, text="Apply", command=self.linear_adjustment
        )
        self.close_button.pack()
        self.widget_frame.pack()

    def update_threshold(
        self, var: str | None = None, _b: Any = None, _c: Any = None
    ) -> None:
        if self.lower_boundary_variable.get() > self.higher_boundary_variable.get():
            active_filter = None
            for f in self.filters:
                if var == f[0]._name:  # type: ignore  # noqa
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

    def reset_image(self) -> None:
        self.image_window.update_image(self.image)
        for child in self.histogram_canvas.lines:
            self.histogram_canvas.delete(child)

        self.histogram_canvas.lines = []
        color = ColorEnum.GREYSCALE
        histogram_values = HistogramWidget.calculate_histogram_values(self.image)[color]
        self.histogram_canvas.histogram_dict = histogram_values
        self.histogram_canvas.plot_histogram()

    @staticmethod
    def calculate_linear_adjustment(
        pixel_value: int, min_out: int, max_out: int
    ) -> int:
        if pixel_value < min_out:
            return MIN_INTENSITY_LEVEL
        elif pixel_value > max_out:
            return MAX_INTENSITY_LEVEL
        else:
            if max_out == min_out:
                return pixel_value

            return round(
                (pixel_value - min_out) * (MAX_INTENSITY_LEVEL / (max_out - min_out))
            )

    def linear_adjustment(self, _a: Any = None, _b: Any = None, _c: Any = None) -> None:
        image = self.image
        list_of_pixels = list(image.getdata())

        min_in = min(list_of_pixels)
        max_in = max(list_of_pixels)
        min_out = max(self.lower_boundary_variable.get(), min_in)
        max_out = min(self.higher_boundary_variable.get(), max_in)
        match image.mode:
            case ImageModeEnum.GREYSCALE:
                list_of_pixels = [
                    self.calculate_linear_adjustment(i, min_out, max_out)
                    for i in list_of_pixels
                ]
            case _:
                logger.error(ValueError("Invalid image format!"))

        inverted_image = Image.new(image.mode, image.size)
        inverted_image.putdata(list_of_pixels)
        self.image_window.update_image(inverted_image)

        for child in self.histogram_canvas.lines:
            self.histogram_canvas.delete(child)

        self.histogram_canvas.lines = []
        color = ColorEnum.GREYSCALE
        histogram_values = HistogramWidget.calculate_histogram_values(inverted_image)[
            color
        ]
        self.histogram_canvas.histogram_dict = histogram_values
        self.histogram_canvas.plot_histogram()


def histogram_equalization(image_window: ImageWindow | None) -> None:
    if not image_window:
        return None

    image = image_window.image
    list_of_pixels = list(image.getdata())
    match image.mode:
        case ImageModeEnum.GREYSCALE:
            histogram = HistogramWidget.count_values(image)
            max_intensity_level = MAX_INTENSITY_LEVEL + 1
            histogram_list = [0] * max_intensity_level
            for i in histogram:
                histogram_list[i] = histogram[i]

            histogram_cumulative_distributor = [
                sum(histogram_list[: i + 1]) for i in range(len(histogram_list))
            ]
            dim = len(list_of_pixels)
            hcd_min = min(i for i in histogram_cumulative_distributor if i > 0)
            list_of_pixels = [
                (histogram_cumulative_distributor[p] - hcd_min)
                * (max_intensity_level - 1)
                // (dim - hcd_min)
                for p in list_of_pixels
            ]
        case _:
            logger.error(ValueError("Invalid image format!"))

    inverted_image = Image.new(image.mode, image.size)
    inverted_image.putdata(list_of_pixels)
    image_window.update_image(inverted_image)


def gamma_correction(image_window: ImageWindow | None) -> None:
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None

    GammaCorrectionWidget(image_window)


class GammaCorrectionWidget(tk.Toplevel):
    def __init__(self, source_image_window: ImageWindow):
        super(GammaCorrectionWidget, self).__init__()
        self.title(source_image_window.window_title)
        self.geometry("350x400")
        self.pack_propagate(False)
        self.image_window = source_image_window
        self.image = source_image_window.image
        self.histogram_max_height = 200
        self.widget_frame: tk.Frame = tk.Frame(self)

        color: ColorEnum = ColorEnum.GREYSCALE
        histogram_values = HistogramWidget.calculate_histogram_values(self.image)[color]
        self.histogram_canvas = HistogramCanvas(
            self.widget_frame, color, histogram_values, self.histogram_max_height
        )
        self.histogram_canvas.pack()
        gradient_bar = GradientBar(
            root=self.widget_frame, height=10, color_iterator=ColorIterator(color)
        )
        gradient_bar.pack()

        self.percent_frame = tk.Frame(self.widget_frame)
        tk.Label(self.percent_frame, text="Gamma coefficient: ").pack()
        slider_percent = SliderWidget(
            self.percent_frame,
            initial_value=1,
            slider_length=100,
            max_intensity_level=3,
            resolution=0.05,
            min_intensity_level=0.5,
            tick_interval=1,
        )
        slider_percent.entry = tk.Entry(
            slider_percent, textvariable=slider_percent.slider_variable, width=4
        )
        slider_percent.entry.grid(row=0, column=2, sticky="NW")
        self.percent = slider_percent.slider_variable
        slider_percent.pack()
        self.percent_frame.pack()

        self.reset_button = tk.Button(
            self.widget_frame, text="Reset", command=self.reset_image
        )
        self.reset_button.pack()
        self.close_button = tk.Button(
            self.widget_frame, text="Apply", command=self.gamma_correction_calc
        )
        self.close_button.pack()
        self.widget_frame.pack()

    def reset_image(self) -> None:
        self.image_window.update_image(self.image)
        self.percent.set(1)
        for child in self.histogram_canvas.lines:
            self.histogram_canvas.delete(child)

        self.histogram_canvas.lines = []
        color = ColorEnum.GREYSCALE
        histogram_values = HistogramWidget.calculate_histogram_values(self.image)[color]
        self.histogram_canvas.histogram_dict = histogram_values
        self.histogram_canvas.plot_histogram()

    @staticmethod
    def calculate_gamma_adjustment(
        pixel_value: int,
        gamma_coefficient: float,
        max_intensity_value: int = MAX_INTENSITY_LEVEL,
    ) -> int:
        return round(
            ((pixel_value / max_intensity_value) ** (1 / gamma_coefficient))
            * MAX_INTENSITY_LEVEL
        )

    def gamma_correction_calc(
        self, _a: Any = None, _b: Any = None, _c: Any = None
    ) -> None:
        image = self.image

        gamma_coefficient = self.percent.get()
        list_of_pixels = list(image.getdata())
        match image.mode:
            case ImageModeEnum.GREYSCALE:
                list_of_pixels = [
                    self.calculate_gamma_adjustment(i, gamma_coefficient)
                    for i in list_of_pixels
                ]
            case _:
                logger.error(ValueError("Invalid image format!"))

        inverted_image = Image.new(image.mode, image.size)
        inverted_image.putdata(list_of_pixels)
        self.image_window.update_image(inverted_image)

        for child in self.histogram_canvas.lines:
            self.histogram_canvas.delete(child)

        self.histogram_canvas.lines = []
        color = ColorEnum.GREYSCALE
        histogram_values = HistogramWidget.calculate_histogram_values(inverted_image)[
            color
        ]
        self.histogram_canvas.histogram_dict = histogram_values
        self.histogram_canvas.plot_histogram()
