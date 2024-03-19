import tkinter as tk
from dataclasses import asdict

import cv2
import numpy as np
from PIL import Image

from imagepy.utils.constants import BinaryOperationEnum, ImageModeEnum
from imagepy.utils.gui.widgets import BorderFillWidget
from imagepy.utils.image_manager import ImageWindow


def binary_calculation(image_window: ImageWindow | None) -> None:
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None
    BinaryOperationsWidget(image_window)


class BinaryOperationsWidget(tk.Toplevel):
    def __init__(self, source_window: ImageWindow):
        super(BinaryOperationsWidget, self).__init__()
        self.title(source_window.window_title)
        self.image_window = source_window
        self.image = source_window.image
        self.geometry("300x250")
        self.pack_propagate(False)
        self.widget_frame: tk.Frame = tk.Frame(self)

        options = [p.value for p in BinaryOperationEnum]
        self.chosen_filter = tk.StringVar(value=options[0])
        tk.OptionMenu(self.widget_frame, self.chosen_filter, *options).pack()

        self.border_widget = BorderFillWidget(self.widget_frame)
        self.border_widget.pack()

        tk.Button(self.widget_frame, text="Reset", command=self.reset_image).pack()
        tk.Button(self.widget_frame, text="Apply", command=self.update_image).pack()

        self.widget_frame.pack()

    def reset_image(self) -> None:
        self.image_window.update_image(self.image)

    def update_image(self) -> None:
        image_array = np.array(self.image)
        kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)

        match self.chosen_filter.get():
            case BinaryOperationEnum.ERODE:
                filtered_image_array = cv2.erode(image_array, kernel)
            case BinaryOperationEnum.DILATE:
                filtered_image_array = cv2.dilate(image_array, kernel)
            case BinaryOperationEnum.OPEN:
                filtered_image_array = cv2.morphologyEx(
                    image_array, cv2.MORPH_OPEN, kernel
                )
            case BinaryOperationEnum.CLOSE:
                filtered_image_array = cv2.morphologyEx(
                    image_array, cv2.MORPH_CLOSE, kernel
                )
            case _:
                raise ValueError()

        filtered_image = Image.fromarray(filtered_image_array.astype("uint8"), "L")
        self.image_window.update_image(filtered_image)
