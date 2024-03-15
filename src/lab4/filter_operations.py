import logging
import tkinter as tk

import cv2
import numpy as np
from PIL import Image

from lab4.filters import blur_filters, sharpen_filters
from utils.constants import ImageModeEnum
from utils.gui.widgets import BorderFillWidget
from utils.image_manager import ImageWindow

logger = logging.getLogger(__name__)


def filter_calculation(image_window: ImageWindow, blur_flag: bool):
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None
    if blur_flag:
        BlurWidget(image_window)
    else:
        SharpenWidget(image_window)


class BlurWidget(tk.Toplevel):
    def __init__(self, source_window: ImageWindow):
        super(BlurWidget, self).__init__()
        self.title(source_window.window_title)
        self.image_window = source_window
        self.image = source_window.image
        self.geometry("400x350")
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        self.filter_widget = FilterWidget(self.frame, blur_filters, blur=True)
        options = self.filter_widget.get_options()
        self.chosen_filter = tk.StringVar(value=options[0])
        tk.Label(self.frame, text="Choose kernel:").pack()
        tk.OptionMenu(self.frame, self.chosen_filter, *options).pack()

        self.filter_widget.pack()

        self.border_widget = BorderFillWidget(self.frame)
        self.border_widget.pack()

        tk.Button(self.frame, text="Reset", command=self.reset_image).pack()
        tk.Button(self.frame, text="Apply", command=self.update_image).pack()

        self.frame.pack()

    def reset_image(self):
        self.image_window.update_image(self.image)

    def update_image(self):
        image_array = np.array(self.image)
        kernel = self.filter_widget.get_filter(self.chosen_filter.get())

        pad_size = (kernel.shape[0] - 1) // 2
        modified_image_array = self.border_widget.apply_border_fill(
            image_array, pad_size, cv2.filter2D, ddepth=-1, kernel=kernel
        )
        modified_image = Image.fromarray(modified_image_array.astype("uint8"), "L")

        self.image_window.update_image(modified_image)


class SharpenWidget(tk.Toplevel):
    def __init__(self, source_window: ImageWindow):
        super(SharpenWidget, self).__init__()
        self.title(source_window.window_title)
        self.image_window = source_window
        self.image = source_window.image
        self.geometry("400x350")
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        self.filter_widget = FilterWidget(self.frame, sharpen_filters)
        options = self.filter_widget.get_options()
        self.chosen_filter = tk.StringVar(value=options[0])
        tk.Label(self.frame, text="Choose kernel:").pack()
        tk.OptionMenu(self.frame, self.chosen_filter, *options).pack()

        self.filter_widget.pack()

        self.border_widget = BorderFillWidget(self.frame)
        self.border_widget.pack()

        tk.Button(self.frame, text="Reset", command=self.reset_image).pack()
        tk.Button(self.frame, text="Apply", command=self.update_image).pack()

        self.frame.pack()

    def reset_image(self):
        self.image_window.update_image(self.image)

    def update_image(self):
        image_array = np.array(self.image)
        kernel = self.filter_widget.get_filter(self.chosen_filter.get())

        pad_size = (kernel.shape[0] - 1) // 2
        modified_image_array = self.border_widget.apply_border_fill(
            image_array, pad_size, cv2.filter2D, ddepth=-1, kernel=kernel
        )
        modified_image = Image.fromarray(modified_image_array.astype("uint8"), "L")

        self.image_window.update_image(modified_image)


class FilterWidget(tk.Frame):
    def __init__(
        self, root: tk.Tk | tk.BaseWidget, filters: list[list[int]], blur: bool = False
    ):
        super(FilterWidget, self).__init__(root)

        self.options = {
            f"filter nr {i}": np.array(filter_arr)
            for i, filter_arr in enumerate(filters)
        }
        self.is_blur = blur
        self.k_entry = None

        for i, filter_tuple in enumerate(self.options.items()):
            self.create_filter_cell(filter_tuple, k_enabled=(i == 1)).grid(
                row=0, column=i
            )

    def get_options(self) -> list[str]:
        return list(self.options.keys())

    def get_filter(self, filter_name: str) -> np.array:
        kernel = self.options[filter_name]
        if self.is_blur:
            if filter_name == "filter nr 1":
                kernel[1][1] = self.k_entry.get()
            kernel_sum = kernel.sum()
            kernel = kernel / kernel_sum if kernel_sum else kernel
        return kernel

    def create_filter_cell(
        self, filter_info: tuple[str, np.array], k_enabled: bool = False
    ) -> tk.BaseWidget:
        filter_name, filter_arr = filter_info
        frame = tk.Frame(self, highlightbackground="black", highlightthickness=1, bd=0)
        tk.Label(frame, text=filter_name).grid(row=0, column=1)
        for i, row in enumerate(filter_arr):
            for j, column in enumerate(row):
                state = (
                    "normal"
                    if self.is_blur and i == 1 and j == 1 and k_enabled
                    else "disabled"
                )
                if self.is_blur and i == 1 and j == 1 and k_enabled:
                    self.k_entry = tk.IntVar(value=8)
                    e = tk.Entry(
                        frame, width=3, justify="center", textvariable=self.k_entry
                    )
                else:
                    e = tk.Entry(frame, width=3, justify="center")
                    e.insert(tk.END, column)
                e.config(state=state)
                e.grid(row=i + 1, column=j, padx=5, pady=5)

        return frame
