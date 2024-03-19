import logging
import tkinter as tk
from typing import Literal

import cv2
import numpy as np
from PIL import Image

from imagepy.lab4.filters import FILTER_3_3, blur_filters, sharpen_filters
from imagepy.utils.constants import ImageModeEnum
from imagepy.utils.gui.widgets import BorderFillWidget
from imagepy.utils.image_manager import ImageWindow

logger = logging.getLogger(__name__)


def filter_calculation(image_window: ImageWindow | None, blur_flag: bool) -> None:
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
        self.widget_frame: tk.Frame = tk.Frame(self)

        self.filter_widget = FilterWidget(self.widget_frame, blur_filters, blur=True)
        options = self.filter_widget.get_options()
        self.chosen_filter = tk.StringVar(value=options[0])
        tk.Label(self.widget_frame, text="Choose kernel:").pack()
        tk.OptionMenu(self.widget_frame, self.chosen_filter, *options).pack()

        self.filter_widget.pack()

        self.border_widget = BorderFillWidget(self.widget_frame)
        self.border_widget.pack()

        tk.Button(self.widget_frame, text="Reset", command=self.reset_image).pack()
        tk.Button(self.widget_frame, text="Apply", command=self.update_image).pack()

        self.widget_frame.pack()

    def reset_image(self) -> None:
        self.image_window.update_image(self.image)

    def update_image(self) -> None:
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
        self.widget_frame: tk.Frame = tk.Frame(self)

        self.filter_widget = FilterWidget(self.widget_frame, sharpen_filters)
        options = self.filter_widget.get_options()
        self.chosen_filter = tk.StringVar(value=options[0])
        tk.Label(self.widget_frame, text="Choose kernel:").pack()
        tk.OptionMenu(self.widget_frame, self.chosen_filter, *options).pack()

        self.filter_widget.pack()

        self.border_widget = BorderFillWidget(self.widget_frame)
        self.border_widget.pack()

        tk.Button(self.widget_frame, text="Reset", command=self.reset_image).pack()
        tk.Button(self.widget_frame, text="Apply", command=self.update_image).pack()

        self.widget_frame.pack()

    def reset_image(self) -> None:
        self.image_window.update_image(self.image)

    def update_image(self) -> None:
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
        self,
        root: tk.Tk | tk.BaseWidget,
        filters: FILTER_3_3,
        blur: bool = False,
    ):
        super(FilterWidget, self).__init__(root)

        self.options = {
            f"filter nr {i}": np.array(filter_arr)
            for i, filter_arr in enumerate(filters)
        }
        self.is_blur = blur
        self.k_entry = tk.IntVar()

        for i, filter_tuple in enumerate(self.options.items()):
            self.create_filter_cell(filter_tuple, k_enabled=(i == 1)).grid(
                row=0, column=i
            )

    def get_options(self) -> list[str]:
        return list(self.options.keys())

    def get_filter(self, filter_name: str) -> np.ndarray:
        kernel = self.options[filter_name]
        if self.is_blur:
            if filter_name == "filter nr 1":
                kernel[1][1] = self.k_entry.get()
            kernel_sum = kernel.sum()
            kernel = kernel / kernel_sum if kernel_sum else kernel
        return kernel

    def create_filter_cell(
        self, filter_info: tuple[str, np.ndarray], k_enabled: bool = False
    ) -> tk.Frame:
        filter_name, filter_arr = filter_info
        frame = tk.Frame(self, highlightbackground="black", highlightthickness=1, bd=0)
        tk.Label(frame, text=filter_name).grid(row=0, column=1)
        for i, row in enumerate(filter_arr):
            for j, column in enumerate(row):
                state: Literal["normal", "disabled"]
                if self.is_blur and i == 1 and j == 1 and k_enabled:
                    state = "normal"
                else:
                    state = "disabled"

                if self.is_blur and i == 1 and j == 1 and k_enabled:
                    self.k_entry.set(value=8)
                    e = tk.Entry(
                        frame, width=3, justify="center", textvariable=self.k_entry
                    )
                else:
                    e = tk.Entry(frame, width=3, justify="center")
                    e.insert(tk.END, column)
                e.config(state=state)
                e.grid(row=i + 1, column=j, padx=5, pady=5)

        return frame
