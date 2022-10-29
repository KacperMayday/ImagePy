import logging
import math
import tkinter as tk

from utils.constants import MAX_INTENSITY_LEVEL, MIN_INTENSITY_LEVEL
from utils.utils import ColourIterator

logger = logging.getLogger(__name__)


class SliderWidget(tk.Frame):
    def __init__(self, root: tk.Tk | tk.BaseWidget, initial_value: int | None = None,
                 min_intensity_level: int = MIN_INTENSITY_LEVEL,
                 max_intensity_level: int = MAX_INTENSITY_LEVEL, slider_length: int = 200, **options):
        super().__init__(root, **options)
        self.slider_variable = tk.IntVar()
        tk.Scale(self, from_=min_intensity_level, to=max_intensity_level, orient=tk.HORIZONTAL,
                 variable=self.slider_variable,
                 tickinterval=max_intensity_level,
                 showvalue=False, sliderlength=10, length=slider_length).grid(row=0, column=0)

        tk.Entry(self,
                 textvariable=self.slider_variable,
                 width=int(math.log10(max_intensity_level)) + 2).grid(row=0,
                                                                      column=2,
                                                                      sticky='NW')

        if initial_value:
            self.set(initial_value)

    def get(self) -> int:
        return self.slider_variable.get()

    def set(self, value: int):
        self.slider_variable.set(value)


class GradientBar(tk.Canvas):
    def __init__(self, root: tk.Frame, height: int, colour_iterator: ColourIterator,
                 width: int = MAX_INTENSITY_LEVEL):
        super(GradientBar, self).__init__(root, width=width, height=height)
        for i in range(width + 1):
            self.create_line(i, height, i, 0, fill=next(colour_iterator))
