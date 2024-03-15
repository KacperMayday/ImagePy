import logging
import tkinter as tk
from dataclasses import dataclass, fields

from PIL import Image

from lab2.histogram_manipulation import LinearAdjustmentWidget
from utils.constants import MAX_INTENSITY_LEVEL, MIN_INTENSITY_LEVEL, ImageModeEnum
from utils.image_manager import ImageWindow

logger = logging.getLogger(__name__)


def image_math(image_window: ImageWindow) -> None:
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None
    ImageMathWidget(image_window)


@dataclass(frozen=True)
class MathOperators:
    ADDITION: str = "+"
    MULTIPLICATION: str = "*"
    DIVISION: str = "/"


class ImageMathWidget(tk.Toplevel):
    def __init__(self, source_image: ImageWindow):
        super(ImageMathWidget, self).__init__()
        self.title(source_image.window_title)
        self.image_window = source_image
        self.image = source_image.image
        self.geometry("300x150")
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        self.input_number = tk.IntVar()
        tk.Entry(self.frame, textvariable=self.input_number, width=5).pack()

        options = [
            getattr(MathOperators, field.name) for field in fields(MathOperators)
        ]
        self.selected_math_operation = tk.StringVar(value=MathOperators.ADDITION)
        tk.OptionMenu(self.frame, self.selected_math_operation, *options).pack()

        self.normalize_flag = tk.BooleanVar()
        tk.Checkbutton(
            self.frame, text="Normalize", variable=self.normalize_flag
        ).pack()

        self.threshold_button = tk.Button(
            self.frame, text="Reset", command=self.reset_image
        )
        self.threshold_button.pack()
        self.close_button = tk.Button(self.frame, text="Apply", command=self.destroy)
        self.close_button.pack()

        self.selected_math_operation.trace("w", self.update_image)
        self.input_number.trace("w", self.update_image)
        self.normalize_flag.trace("w", self.update_image)

        self.frame.pack()

    def reset_image(self):
        self.image_window.update_image(self.image)
        self.input_number.set(0)
        self.selected_math_operation.set(MathOperators.ADDITION)
        self.normalize_flag.set(False)

    @staticmethod
    def calculate_math(
        list_of_pixels: list[int], math_operator: str, input_value: int
    ) -> list[int] | None:
        match math_operator:
            case MathOperators.ADDITION:
                return [pixel + input_value for pixel in list_of_pixels]
            case MathOperators.MULTIPLICATION:
                return [pixel * input_value for pixel in list_of_pixels]
            case MathOperators.DIVISION:
                input_value = 1 if input_value == 0 else input_value
                return [pixel // input_value for pixel in list_of_pixels]
            case _:
                raise ValueError(f'Unsupported math operator! "{math_operator}"')

    @staticmethod
    def normalize(list_of_pixels: list[int]) -> list[int]:
        min_in = min(list_of_pixels)
        max_in = max(list_of_pixels)
        if max_in > MAX_INTENSITY_LEVEL:
            max_out = MAX_INTENSITY_LEVEL
            min_out = max(max_out - max_in + min_in, MIN_INTENSITY_LEVEL)
        elif min_in < MIN_INTENSITY_LEVEL:
            min_out = MIN_INTENSITY_LEVEL
            max_out = min(min_out - min_in + max_in, MAX_INTENSITY_LEVEL)
        else:
            return list_of_pixels

        return [
            LinearAdjustmentWidget.calculate_linear_adjustment(pixel, min_out, max_out)
            for pixel in list_of_pixels
        ]

    def update_image(self, *_):
        list_of_pixels = list(self.image.getdata())
        match self.image.mode:
            case ImageModeEnum.GREYSCALE:
                try:
                    input_value = self.input_number.get()
                except tk.TclError:
                    input_value = 0
                list_of_pixels = self.calculate_math(
                    list_of_pixels, self.selected_math_operation.get(), input_value
                )
                list_of_pixels = (
                    self.normalize(list_of_pixels)
                    if self.normalize_flag.get()
                    else list_of_pixels
                )
            case _:
                logger.error(ValueError("Invalid image format!"))

        inverted_image = Image.new(self.image.mode, self.image.size)
        inverted_image.putdata(list_of_pixels)
        self.image_window.update_image(inverted_image)
