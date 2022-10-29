import logging
import tkinter as tk

from PIL import Image

from lab1.histogram import HistogramCanvas, HistogramWidget
from utils.constants import ColourEnum, ImageModeEnum, MAX_INTENSITY_LEVEL, MIN_INTENSITY_LEVEL
from utils.gui.widgets import GradientBar, SliderWidget
from utils.image_manager import ImageWindow
from utils.utils import ColourIterator

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

        self.percent = tk.IntVar(value=0)
        self.percent_frame = tk.Frame(self.frame)
        tk.Label(self.percent_frame, text="Procent przesycenia %: ").grid(row=0, column=0)
        tk.Entry(self.percent_frame, textvariable=self.percent, width=4).grid(row=0, column=1)
        self.percent_frame.pack()

        self.reset_button = tk.Button(self.frame, text='Reset', command=self.reset_image)
        self.reset_button.pack()
        self.apply_button = tk.Button(self.frame, text='Apply', command=self.linear_adjustment)
        self.apply_button.pack()
        self.frame.pack()

    def reset_image(self):
        self.image_window.update_image(self.image)
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

    def linear_adjustment(self):
        image = self.image
        list_of_pixels = list(image.getdata())
        stretch_threshold_coefficient = max(self.percent.get() / 100, 0) if isinstance(self.percent.get(), int) else 0
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
        self.lower_boundary_line = self.histogram_canvas.create_line(self.histogram_canvas.border_offset,
                                                                     self.histogram_canvas.border_offset,
                                                                     self.histogram_canvas.border_offset,
                                                                     self.histogram_max_height + self.histogram_canvas.border_offset,
                                                                     fill='red')
        slider_lower_boundary = SliderWidget(self.frame, initial_value=MIN_INTENSITY_LEVEL)
        self.lower_boundary_variable = slider_lower_boundary.slider_variable
        slider_lower_boundary.pack()

        self.higher_boundary_line = self.histogram_canvas.create_line(
            MAX_INTENSITY_LEVEL + self.histogram_canvas.border_offset,
            self.histogram_canvas.border_offset,
            MAX_INTENSITY_LEVEL + self.histogram_canvas.border_offset,
            self.histogram_max_height + self.histogram_canvas.border_offset,
            fill='red')
        slider_higher_boundary = SliderWidget(self.frame, initial_value=MAX_INTENSITY_LEVEL)
        self.higher_boundary_variable = slider_higher_boundary.slider_variable
        slider_higher_boundary.pack()

        self.close_button = tk.Button(self.frame, text='Apply', command=self.linear_adjustment)
        self.close_button.pack()
        self.frame.pack()

        self.filters = [[self.lower_boundary_variable, 'lower'],
                        [self.higher_boundary_variable, 'higher']]
        self.lower_boundary_variable.trace('w', self.update_threshold)
        self.higher_boundary_variable.trace('w', self.update_threshold)

    def update_threshold(self, var: str, _b, _c):
        if self.lower_boundary_variable.get() > self.higher_boundary_variable.get():
            active_filter = None
            for f in self.filters:
                if var == f[0]._name:
                    active_filter = f[1]
            if active_filter == 'higher':
                self.lower_boundary_variable.set(self.higher_boundary_variable.get())
            elif active_filter == 'lower':
                self.higher_boundary_variable.set(self.lower_boundary_variable.get())

        self.histogram_canvas.coords(self.lower_boundary_line,
                                     self.lower_boundary_variable.get() + self.histogram_canvas.border_offset,
                                     self.histogram_canvas.border_offset,
                                     self.lower_boundary_variable.get() + self.histogram_canvas.border_offset,
                                     self.histogram_max_height + self.histogram_canvas.border_offset)
        self.histogram_canvas.coords(self.higher_boundary_line,
                                     self.higher_boundary_variable.get() + self.histogram_canvas.border_offset,
                                     self.histogram_canvas.border_offset,
                                     self.higher_boundary_variable.get() + self.histogram_canvas.border_offset,
                                     self.histogram_max_height + self.histogram_canvas.border_offset)

    @staticmethod
    def calculate_linear_adjustment(pixel_value: int, min_value: int, max_value: int) -> int:
        if pixel_value < min_value:
            return min_value
        elif pixel_value > max_value:
            return max_value
        else:
            if max_value == min_value:
                return pixel_value
            return (pixel_value - min_value) * MAX_INTENSITY_LEVEL // (max_value - min_value)

    def linear_adjustment(self):
        image = self.image
        list_of_pixels = list(image.getdata())
        stretch_threshold_coefficient = 0.00
        threshold = round(stretch_threshold_coefficient * len(list_of_pixels))
        match image.mode:
            case ImageModeEnum.GREYSCALE:
                sorted_list = sorted(list_of_pixels)
                max_value = max(sorted_list[:-threshold if threshold != 0 else -1])
                min_value = min(sorted_list[threshold:])
                list_of_pixels = [self.calculate_linear_adjustment(i, min_value, max_value) for i in list_of_pixels]
            case _:
                logger.error(ValueError('Niepoprawny format obrazu!'))

        inverted_image = Image.new(image.mode, image.size)
        inverted_image.putdata(list_of_pixels)
        self.image_window.update_image(inverted_image)
        self.destroy()

    @staticmethod
    def calculate_gamma_adjustment(pixel_value: int, gamma_coefficient: float,
                                   max_intensity_value: int = MAX_INTENSITY_LEVEL) -> int:
        return round(((pixel_value / max_intensity_value) ** (1 / gamma_coefficient)) * MAX_INTENSITY_LEVEL)

    def gamma_correction_calc(self, image: Image) -> list[int] | list[tuple[int, int, int]]:
        # TODO dodać gamma do GUI
        gamma_coefficient = 0.5
        list_of_pixels = list(image.getdata())
        match image.mode:
            case ImageModeEnum.GREYSCALE:
                list_of_pixels = [self.calculate_gamma_adjustment(i, gamma_coefficient) for i in list_of_pixels]
            # case ImageModeEnum.GREYSCALE:
            #     list_of_pixels = [tuple([calculate_gamma_adjustment(j, gamma_coefficient) for j in pixel]) for pixel in
            #                       list_of_pixels]
            case _:
                logger.error(ValueError('Niepoprawny format obrazu!'))

        return list_of_pixels
