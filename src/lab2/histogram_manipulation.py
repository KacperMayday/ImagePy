import logging
import tkinter as tk

from PIL import Image

from src.lab1.histogram import HistogramCanvas, HistogramWidget
from src.utils.constants import ColourEnum, ImageModeEnum, MAX_INTENSITY_LEVEL, MIN_INTENSITY_LEVEL
from src.utils.gui.widgets import GradientBar, SliderWidget
from src.utils.image_manager import ImageWindow
from src.utils.utils import ColourIterator

logger = logging.getLogger(__name__)


def linear_adjustment(image_window: ImageWindow) -> None:
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None

    LinearAdjustmentWidget(image_window)


class LinearAdjustmentWidget(tk.Toplevel):
    def __init__(self, source_image_window: ImageWindow):
        super(LinearAdjustmentWidget, self).__init__()
        self.title(source_image_window.window_title)
        self.geometry('350x400')
        self.pack_propagate(False)
        self.image_window = source_image_window
        self.image = source_image_window.image
        self.histogram_max_height = 200
        self.frame = tk.Frame(self)

        colour = ColourEnum.GREYSCALE
        histogram_values = HistogramWidget.calculate_histogram_values(self.image)[colour]
        self.histogram_canvas = HistogramCanvas(self.frame, colour, histogram_values, self.histogram_max_height)
        self.histogram_canvas.pack()
        gradient_bar = GradientBar(root=self.frame, height=10, colour_iterator=ColourIterator(colour))
        gradient_bar.pack()

        self.percent_frame = tk.Frame(self.frame)
        tk.Label(self.percent_frame, text="Procent przesycenia %: ").pack()
        slider_percent = SliderWidget(self.percent_frame, initial_value=MIN_INTENSITY_LEVEL, slider_length=100,
                                      max_intensity_level=100)
        self.percent = slider_percent.slider_variable
        self.percent.trace('w', self.linear_adjustment)
        slider_percent.pack()
        self.percent_frame.pack()

        self.reset_button = tk.Button(self.frame, text='Reset', command=self.reset_image)
        self.reset_button.pack()
        self.close_button = tk.Button(self.frame, text='Apply', command=self.destroy)
        self.close_button.pack()
        self.frame.pack()

    def reset_image(self):
        self.image_window.update_image(self.image)
        self.percent.set(0)
        for child in self.histogram_canvas.lines:
            self.histogram_canvas.delete(child)

        self.histogram_canvas.lines = []
        colour = ColourEnum.GREYSCALE
        histogram_values = HistogramWidget.calculate_histogram_values(self.image)[colour]
        self.histogram_canvas.histogram_dict = histogram_values
        self.histogram_canvas.plot_histogram()

    @staticmethod
    def calculate_linear_adjustment(pixel_value: int, min_value: int, max_value: int) -> int:
        if pixel_value < min_value:
            return MIN_INTENSITY_LEVEL
        elif pixel_value > max_value:
            return MAX_INTENSITY_LEVEL
        else:
            if max_value == min_value:
                return pixel_value
            return (pixel_value - min_value) * MAX_INTENSITY_LEVEL // (max_value - min_value)

    def linear_adjustment(self, _a, _b, _c):
        image = self.image
        list_of_pixels = list(image.getdata())
        stretch_threshold_coefficient = max(int(self.percent.get()) / 100, 0) if isinstance(self.percent.get(),
                                                                                            int) else 0
        threshold = round(stretch_threshold_coefficient * len(list_of_pixels))
        match image.mode:
            case ImageModeEnum.GREYSCALE:
                sorted_list = sorted(list_of_pixels)
                max_value = max(sorted_list[:-threshold if threshold != 0 else -1])
                min_value = min(sorted_list[threshold:])
                list_of_pixels = [self.calculate_linear_adjustment(i, min_value, max_value) for i in
                                  list_of_pixels]
            case _:
                logger.error(ValueError('Niepoprawny format obrazu!'))

        inverted_image = Image.new(image.mode, image.size)
        inverted_image.putdata(list_of_pixels)
        self.image_window.update_image(inverted_image)

        for child in self.histogram_canvas.lines:
            self.histogram_canvas.delete(child)

        self.histogram_canvas.lines = []
        colour = ColourEnum.GREYSCALE
        histogram_values = HistogramWidget.calculate_histogram_values(inverted_image)[colour]
        self.histogram_canvas.histogram_dict = histogram_values
        self.histogram_canvas.plot_histogram()


def histogram_equalization(image_window: ImageWindow):
    if not image_window:
        return None

    image = image_window.image
    list_of_pixels = list(image.getdata())
    histogram = HistogramWidget.count_values(image)
    max_intensity_level = MAX_INTENSITY_LEVEL + 1
    histogram_list = [0] * max_intensity_level
    for i in histogram:
        histogram_list[i] = histogram[i]

    histogram_cumulative_distributor = [sum(histogram_list[:i + 1]) for i in range(len(histogram_list))]
    dim = len(list_of_pixels)
    hcd_min = min(i for i in histogram_cumulative_distributor if i > 0)
    list_of_pixels = [(histogram_cumulative_distributor[p] - hcd_min) * (max_intensity_level - 1) // (dim - hcd_min)
                      for p in list_of_pixels]

    inverted_image = Image.new(image.mode, image.size)
    inverted_image.putdata(list_of_pixels)
    image_window.update_image(inverted_image)


def gamma_correction(image_window: ImageWindow):
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None

    GammaCorrectionWidget(image_window)


class GammaCorrectionWidget(tk.Toplevel):
    def __init__(self, source_image_window: ImageWindow):
        super(GammaCorrectionWidget, self).__init__()
        self.title(source_image_window.window_title)
        self.geometry('350x400')
        self.pack_propagate(False)
        self.image_window = source_image_window
        self.image = source_image_window.image
        self.histogram_max_height = 200
        self.frame = tk.Frame(self)

        colour = ColourEnum.GREYSCALE
        histogram_values = HistogramWidget.calculate_histogram_values(self.image)[colour]
        self.histogram_canvas = HistogramCanvas(self.frame, colour, histogram_values, self.histogram_max_height)
        self.histogram_canvas.pack()
        gradient_bar = GradientBar(root=self.frame, height=10, colour_iterator=ColourIterator(colour))
        gradient_bar.pack()

        self.percent_frame = tk.Frame(self.frame)
        tk.Label(self.percent_frame, text="Procent przesycenia %: ").pack()
        slider_percent = SliderWidget(self.percent_frame, initial_value=1, slider_length=100,
                                      max_intensity_level=1.5, resolution=0.05, min_intensity_level=0.5,
                                      tick_interval=1)
        slider_percent.entry = tk.Entry(slider_percent,
                                        textvariable=slider_percent.slider_variable,
                                        width=4)
        slider_percent.entry.grid(row=0,
                                  column=2,
                                  sticky='NW')
        self.percent = slider_percent.slider_variable
        self.percent.trace('w', self.gamma_correction_calc)
        slider_percent.pack()
        self.percent_frame.pack()

        self.reset_button = tk.Button(self.frame, text='Reset', command=self.reset_image)
        self.reset_button.pack()
        self.close_button = tk.Button(self.frame, text='Apply', command=self.destroy)
        self.close_button.pack()
        self.frame.pack()

    def reset_image(self):
        self.image_window.update_image(self.image)
        self.percent.set(1)
        for child in self.histogram_canvas.lines:
            self.histogram_canvas.delete(child)

        self.histogram_canvas.lines = []
        colour = ColourEnum.GREYSCALE
        histogram_values = HistogramWidget.calculate_histogram_values(self.image)[colour]
        self.histogram_canvas.histogram_dict = histogram_values
        self.histogram_canvas.plot_histogram()

    @staticmethod
    def calculate_gamma_adjustment(pixel_value: int, gamma_coefficient: float,
                                   max_intensity_value: int = MAX_INTENSITY_LEVEL) -> int:
        return round(((pixel_value / max_intensity_value) ** (1 / gamma_coefficient)) * MAX_INTENSITY_LEVEL)

    def gamma_correction_calc(self, _a, _b, _c):
        image = self.image

        gamma_coefficient = self.percent.get()
        list_of_pixels = list(image.getdata())
        match image.mode:
            case ImageModeEnum.GREYSCALE:
                list_of_pixels = [self.calculate_gamma_adjustment(i, gamma_coefficient) for i in list_of_pixels]
            case _:
                logger.error(ValueError('Niepoprawny format obrazu!'))

        inverted_image = Image.new(image.mode, image.size)
        inverted_image.putdata(list_of_pixels)
        self.image_window.update_image(inverted_image)

        for child in self.histogram_canvas.lines:
            self.histogram_canvas.delete(child)

        self.histogram_canvas.lines = []
        colour = ColourEnum.GREYSCALE
        histogram_values = HistogramWidget.calculate_histogram_values(inverted_image)[colour]
        self.histogram_canvas.histogram_dict = histogram_values
        self.histogram_canvas.plot_histogram()
