import logging
import math
import tkinter as tk
from dataclasses import dataclass

import cv2
import numpy as np

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


@dataclass
class BorderFillEntry:
    border_type: int | None
    disable_user_entry: bool = True


border_fill_types = {
    'User constant applied before': BorderFillEntry(cv2.BORDER_CONSTANT, False),
    'User constant applied after': BorderFillEntry(None, False),
    'Border reflect': BorderFillEntry(cv2.BORDER_REFLECT),
    'Border wrap': BorderFillEntry(cv2.BORDER_WRAP)
}


class BorderFillWidget(tk.Frame):
    def __init__(self, root: tk.Tk | tk.BaseWidget):
        super(BorderFillWidget, self).__init__(root)

        options = list(border_fill_types.keys())
        self.chosen_border = tk.StringVar(value=options[0])
        tk.Label(self, text='Choose border fill type:').pack()
        tk.OptionMenu(self, self.chosen_border, *options, command=self.disable_entry).pack()

        tk.Label(self, text='User constant:').pack()
        self.user_constant_entry = tk.Entry(self, width=5)
        self.user_constant_entry.pack()

    def disable_entry(self, *_):
        border_fill_entry = border_fill_types.get(self.chosen_border.get())
        if border_fill_entry and border_fill_entry.disable_user_entry:
            self.user_constant_entry.config(state='disabled')
        else:
            self.user_constant_entry.config(state='normal')

    def get(self) -> tuple[int | None] | tuple[int | None, int]:
        border_fill_entry = border_fill_types.get(self.chosen_border.get())
        if not border_fill_entry:
            raise ValueError()

        if border_fill_entry.disable_user_entry:
            return border_fill_entry.border_type,
        else:
            user_constant = int(self.user_constant_entry.get())
            return border_fill_entry.border_type, user_constant

    def apply_border_fill_2d(self, image_array: np.array, kernel: np.array, filter_operation) -> np.array:
        border_fill_type_tuple = self.get()
        pad_size = (kernel.shape[0] - 1) // 2

        if len(border_fill_type_tuple) == 1:
            border_type = border_fill_type_tuple[0]
            padded_image_array = cv2.copyMakeBorder(image_array, pad_size, pad_size, pad_size, pad_size, border_type)
            modified_image_array = filter_operation(padded_image_array, -1, kernel)
            modified_image_array = modified_image_array[pad_size:-pad_size, pad_size:-pad_size]
        else:
            border_type, border_constant = border_fill_type_tuple
            if border_type is not None:
                image_array = cv2.copyMakeBorder(image_array, pad_size, pad_size, pad_size, pad_size,
                                                 border_type, value=border_constant)
                modified_image_array = filter_operation(image_array, -1, kernel)
                modified_image_array = modified_image_array[pad_size:-pad_size, pad_size:-pad_size]
            else:
                modified_image_array = filter_operation(image_array, -1, kernel)
                modified_image_array = np.pad(modified_image_array, pad_size, constant_values=border_constant)

        return modified_image_array

    def apply_border_fill(self, image_array: np.array, kernel_size: int, filter_operation) -> np.array:
        border_fill_type_tuple = self.get()
        pad_size = (kernel_size - 1) // 2

        if len(border_fill_type_tuple) == 1:
            border_type = border_fill_type_tuple[0]
            padded_image_array = cv2.copyMakeBorder(image_array, pad_size, pad_size, pad_size, pad_size, border_type)
            modified_image_array = filter_operation(padded_image_array, kernel_size)
            modified_image_array = modified_image_array[pad_size:-pad_size, pad_size:-pad_size]
        else:
            border_type, border_constant = border_fill_type_tuple
            if border_type is not None:
                image_array = cv2.copyMakeBorder(image_array, pad_size, pad_size, pad_size, pad_size,
                                                 border_type, value=border_constant)
                modified_image_array = filter_operation(image_array, kernel_size)
                modified_image_array = modified_image_array[pad_size:-pad_size, pad_size:-pad_size]
            else:
                modified_image_array = filter_operation(image_array, kernel_size)
                modified_image_array = np.pad(modified_image_array, pad_size, constant_values=border_constant)

        return modified_image_array
