import logging
import math
import tkinter as tk

from src.utils.constants import MAX_INTENSITY_LEVEL, MIN_INTENSITY_LEVEL
from src.utils.utils import ColourIterator

logger = logging.getLogger(__name__)


class SliderWidget(tk.Frame):
    def __init__(self, root: tk.Tk | tk.BaseWidget, initial_value: int | None = None,
                 min_intensity_level: float = MIN_INTENSITY_LEVEL, tick_interval: int | None = None,
                 max_intensity_level: float = MAX_INTENSITY_LEVEL, slider_length: int = 200, **options):
        super().__init__(root)
        tick_interval = max_intensity_level if not tick_interval else tick_interval
        self.slider_variable = tk.DoubleVar()
        tk.Scale(self, from_=min_intensity_level, to=max_intensity_level, orient=tk.HORIZONTAL,
                 variable=self.slider_variable,
                 tickinterval=tick_interval,
                 showvalue=False, sliderlength=10, length=slider_length, **options).grid(row=0, column=0)

        self.entry = tk.Entry(self,
                              textvariable=self.slider_variable,
                              width=int(math.log10(max_intensity_level)) + 2)
        self.entry.grid(row=0,
                        column=2,
                        sticky='NW')

        if initial_value:
            self.set(initial_value)

    def get(self) -> float:
        return self.slider_variable.get()

    def set(self, value: int):
        self.slider_variable.set(value)


class GradientBar(tk.Canvas):
    def __init__(self, root: tk.Frame, height: int, colour_iterator: ColourIterator,
                 width: int = MAX_INTENSITY_LEVEL):
        super(GradientBar, self).__init__(root, width=width, height=height)
        for i in range(width + 1):
            self.create_line(i, height, i, 0, fill=next(colour_iterator))
