import tkinter as tk
from dataclasses import asdict
from typing import Callable

import numpy as np
from PIL import Image

from utils.constants import ImageModeEnum, LogicFilterEnum
from utils.gui.widgets import BorderFillWidget
from utils.image_manager import ImageWindow


def logic_filter(image_window: ImageWindow):
    """
    Entry function checking prerequisites for logic filter functionality.
    :param image_window: selected image window
    """
    if not image_window or image_window.mode != ImageModeEnum.BINARY:
        return None
    LogicFiltersWidget(image_window)


class LogicFiltersWidget(tk.Toplevel):
    # define filter formulas for each type
    predicates_per_filter_type = {
        LogicFilterEnum.HORIZONTAL: lambda a, b, c, d, x: a if a == d else x,
        LogicFilterEnum.VERTICAL: lambda a, b, c, d, x: b if b == c else x,
        LogicFilterEnum.ISOLATED_POINTS: lambda a, b, c, d, x: (
            a if a == b == c == d else x
        ),
    }

    def __init__(self, source_window: ImageWindow):
        super(LogicFiltersWidget, self).__init__()
        self.title(source_window.window_title)
        self.image_window = source_window
        self.image = source_window.image
        self.geometry("300x250")
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        # UI for choosing logic filter
        tk.Label(self.frame, text="Choose filter type:").pack()
        options = list(asdict(LogicFilterEnum()).values())
        self.chosen_filter = tk.StringVar(value=options[0])
        tk.OptionMenu(self.frame, self.chosen_filter, *options).pack()

        # border boundaries fill functionality
        self.border_widget = BorderFillWidget(self.frame)
        self.border_widget.pack()

        tk.Button(self.frame, text="Reset", command=self.reset_image).pack()
        tk.Button(self.frame, text="Apply", command=self.update_image).pack()

        self.frame.pack()

    def reset_image(self):
        """
        Resets image to previous state.
        """
        self.image_window.update_image(self.image)

    def update_image(self):
        image_array = np.array(self.image)

        modified_image_array = self.border_widget.apply_border_fill(
            image_array=image_array.astype(int),
            pad_size=1,
            filter_operation=self.run_filter,
            func=self.predicates_per_filter_type.get(self.chosen_filter.get()),
        )
        modified_image = Image.fromarray(modified_image_array.astype(bool))
        self.image_window.update_image(modified_image)

    @staticmethod
    def run_filter(
        image_array: np.array, func: Callable[[int, int, int, int, int], int]
    ) -> np.array:
        """
        Filter method operating on neighbouring pixels.

        :param image_array: image array to filter
        :param func: function to apply. One from LogicFiltersWidget.predicates_per_filter_type
        :return: filtered image array
        """
        target_array = np.copy(
            image_array
        )  # array copy is needed to prevent cascade pixel changing
        for (row, col), val in np.ndenumerate(image_array):
            try:
                target_array[row][col] = func(
                    image_array[row - 1][col],
                    image_array[row][col - 1],
                    image_array[row][col + 1],
                    image_array[row + 1][col],
                    image_array[row][col],
                )
            except IndexError:  # if index is out of bounds element will not be changed
                pass

        return target_array
