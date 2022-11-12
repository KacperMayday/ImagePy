import logging
import math
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk

from PIL import Image

from src.utils.constants import ColourEnum, ImageModeEnum, MAX_INTENSITY_LEVEL, MIN_INTENSITY_LEVEL
from src.utils.gui.widgets import GradientBar
from src.utils.image_manager import ImageWindow
from src.utils.utils import ColourIterator

logger = logging.getLogger(__name__)


def show_histogram(source_window: ImageWindow) -> None:
    if not source_window:
        return None

    HistogramWidget(source_window.image, source_window.window_title)


@dataclass
class HistogramStatistics:
    n_count: int
    mode: tuple[int, int]
    mean: float
    st_dev: float
    min_pixel_value: int
    max_pixel_value: int


class HistogramCanvas(tk.Canvas):
    def __init__(self, root: ttk.Frame, colour: str, histogram_dict: dict[int, int], height: int,
                 width: int = MAX_INTENSITY_LEVEL, bg_colour: str = 'white', highlight_thickness: int = 1,
                 highlight_background: str = 'black'):
        super(HistogramCanvas, self).__init__(root, width=width + highlight_thickness, height=height, bg=bg_colour,
                                              highlightthickness=highlight_thickness,
                                              highlightbackground=highlight_background, cursor="tcross")
        self.colour = colour
        self.height = height
        self.width = width
        self.histogram_dict = histogram_dict
        self.max_pixel_count = max(self.histogram_dict.values())
        self.pixel_count = tk.StringVar(value=f'Count: ---')
        self.pixel_value = tk.StringVar(value=f'Value: ---')
        self.border_offset = highlight_thickness
        self.lines = []

        self.bind('<Motion>', self.set_histogram_string_vars)

        self.plot_histogram()

    def set_histogram_string_vars(self, event: tk.Event):
        mouse_x = event.x - self.border_offset
        if mouse_x < MIN_INTENSITY_LEVEL or mouse_x > MAX_INTENSITY_LEVEL:
            self.pixel_count.set(f'Count: ---')
            self.pixel_value.set(f'Value: ---')
        else:
            self.pixel_count.set(
                f'Count: {self.histogram_dict.get(mouse_x) if mouse_x in self.histogram_dict else MIN_INTENSITY_LEVEL}')
            self.pixel_value.set(f'Value: {mouse_x}')

    def plot_histogram(self):
        for intensity_level in range(self.width + 1):
            self.lines.append(self.create_line(intensity_level + self.border_offset,
                                               self.height,
                                               intensity_level + self.border_offset,
                                               self.height - ((self.histogram_dict[
                                                                   intensity_level] / self.max_pixel_count) * self.height
                                                              if intensity_level in self.histogram_dict else MIN_INTENSITY_LEVEL),
                                               fill=self.colour))


class HistogramStatisticsFrame(ttk.Frame):
    def __init__(self, root: ttk.Frame, histogram_statistics: HistogramStatistics,
                 pixel_count: tk.StringVar, pixel_value: tk.StringVar, width: int = MAX_INTENSITY_LEVEL):
        super(HistogramStatisticsFrame, self).__init__(root, width=width)
        self.histogram_statistics = histogram_statistics
        self.pixel_count = pixel_count
        self.pixel_value = pixel_value

        self.add_statistics_labels()

    def add_statistics_labels(self):
        ttk.Label(self, text=f'N: {self.histogram_statistics.n_count}').grid(row=0, column=0, sticky="w")
        ttk.Label(self, text=f'Mean: {self.histogram_statistics.mean}').grid(row=1, column=0, sticky="w")
        ttk.Label(self, text=f'StdDev: {self.histogram_statistics.st_dev}').grid(row=2, column=0, sticky="w")
        ttk.Label(self, textvariable=self.pixel_value).grid(row=3, column=0, sticky="w")

        ttk.Separator(self, orient=tk.VERTICAL).grid(row=0, column=1, rowspan=3, sticky="ns", padx=20)

        ttk.Label(self, text=f'Min: {self.histogram_statistics.min_pixel_value}').grid(row=0, column=2, sticky="w")
        ttk.Label(self, text=f'Max: {self.histogram_statistics.max_pixel_value}').grid(row=1, column=2, sticky="w")
        ttk.Label(self, text=f'Mode: {self.histogram_statistics.mode[0]} ({self.histogram_statistics.mode[1]})') \
            .grid(row=2, column=2, sticky="w")
        ttk.Label(self, textvariable=self.pixel_count).grid(row=3, column=2, sticky="w")


class HistogramWidget(tk.Toplevel):
    def __init__(self, source_image: Image, title: str):
        super(HistogramWidget, self).__init__()
        self.title(title)
        self.geometry('400x400')
        self.pack_propagate(False)
        self.image = source_image
        self.histogram_max_height = 200
        tk.Label(self, text='Hover cursor over histogram to see value and count for specific pixel').pack()
        self.histogram_values = self.calculate_histogram_values(self.image)
        self.plot_histogram(self.histogram_values)

    @staticmethod
    def count_values(image: Image, colour_dimension: int | None = None) -> dict[int, int]:
        width, height = image.size
        if colour_dimension is None:
            values = [image.getpixel((i, j)) for i in range(width) for j in range(height)]
        else:
            values = [image.getpixel((i, j))[colour_dimension] for i in range(width) for j in range(height)]

        intensity_count = {v: values.count(v) for v in set(values)}
        return intensity_count

    @staticmethod
    def calculate_histogram_values(image: Image) -> dict[str, dict[int, int]]:
        histogram_values = dict()
        match image.mode:
            case ImageModeEnum.GREYSCALE | ImageModeEnum.BINARY:
                histogram_values[ColourEnum.GREYSCALE] = HistogramWidget.count_values(image)
            case ImageModeEnum.COLOUR:
                for i, colour in enumerate([ColourEnum.RED, ColourEnum.GREEN, ColourEnum.BLUE]):
                    histogram_values[colour] = HistogramWidget.count_values(image, i)
            case _:
                logger.error(ValueError('Invalid image format!'))

        return histogram_values

    def plot_histogram(self, histogram_values: dict[str, dict[int, int]]):
        def show_frame(frames: dict[str, ttk.Frame], selected: str) -> None:
            for f in frames.values():
                f.pack_forget()
            frames[selected.lower()].pack()

        options = list(map(lambda s: s.capitalize(), histogram_values.keys()))

        clicked = tk.StringVar(value=options[0])
        if len(options) > 1:
            drop = tk.OptionMenu(self, clicked, *options, command=lambda _: show_frame(histogram_frames, clicked.get()))
            drop.pack()

        histogram_main_frame = ttk.Frame(self)
        histogram_main_frame.pack(expand=False, fill="none")
        histogram_main_frame.update()

        histogram_frames = dict()
        for colour in histogram_values:
            values = histogram_values[colour]
            histogram_frame = ttk.Frame(histogram_main_frame)
            histogram_frames[colour] = histogram_frame
            histogram_canvas = HistogramCanvas(histogram_frame, colour, values, self.histogram_max_height)
            histogram_canvas.pack()
            gradient_bar = GradientBar(root=histogram_frame, height=10, colour_iterator=ColourIterator(colour))
            gradient_bar.pack()

            scale_frame = ttk.Frame(histogram_frame, width=MAX_INTENSITY_LEVEL, height=self.histogram_max_height)
            ttk.Label(scale_frame, text=MIN_INTENSITY_LEVEL).grid(row=0, column=0, sticky='w')
            ttk.Label(scale_frame, text=MAX_INTENSITY_LEVEL).grid(row=0, column=1, sticky='e')
            scale_frame.columnconfigure('all', minsize=(MAX_INTENSITY_LEVEL + 1) // 2)
            scale_frame.pack()

            histogram_statistics = self.calculate_statistics(values)
            histogram_statistics_frame = HistogramStatisticsFrame(histogram_frame, histogram_statistics,
                                                                  pixel_count=histogram_canvas.pixel_count,
                                                                  pixel_value=histogram_canvas.pixel_value)
            histogram_statistics_frame.pack(pady=10)

        show_frame(histogram_frames, options[0])

    @staticmethod
    def calculate_statistics(histogram_values: dict[int, int]) -> HistogramStatistics:
        decimal_places = 3
        n_count = 0
        min_key_value = math.inf
        max_key_value = -math.inf
        sum_product = 0
        k_square_v_product = 0
        mode = [None, -math.inf]
        for k, v in histogram_values.items():
            n_count += v
            min_key_value = k if k < min_key_value and v else min_key_value
            max_key_value = k if k > max_key_value and v else max_key_value
            sum_product += k * v
            k_square_v_product += pow(k, 2) * v
            mode = [k, v] if mode[1] < v else mode

        mean = round(sum_product / n_count, decimal_places)
        st_dev = round(pow((k_square_v_product - 2 * mean * sum_product) / n_count + pow(mean, 2), 0.5), decimal_places)

        logger.debug(f'mode {mode[0]}, {mode[1]}')
        logger.debug(f'mean {round(mean, 3)}')
        logger.debug(f'standard_deviation {round(st_dev, 3)}')
        logger.debug(f'N {n_count}')
        logger.debug(f'min {min_key_value}')
        logger.debug(f'max {max_key_value}')
        return HistogramStatistics(n_count=n_count, mode=mode, mean=mean, st_dev=st_dev, min_pixel_value=min_key_value,
                                   max_pixel_value=max_key_value)
