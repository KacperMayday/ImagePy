import logging
import os
from tkinter import filedialog as fd
from typing import Self

from PIL import Image, UnidentifiedImageError
from PIL.Image import Image as PILImage

from imagepy.utils.constants import (
    FILE_TYPES,
    MAX_INTENSITY_LEVEL,
    ColorEnum,
    FileDialogArgs,
)
from imagepy.utils.image_manager import ImageWindow

logger = logging.getLogger(__name__)


def open_file() -> None:
    filename = fd.askopenfilename(filetypes=FILE_TYPES)

    if not filename:
        return None

    try:
        image = Image.open(filename)
    except (UnidentifiedImageError, FileNotFoundError) as e:
        logger.error(e)
        return None

    # Put it in the display window
    ImageWindow(source_path=filename, image=image)
    logger.info(f"Image opened from {filename}")


def save_image(image: PILImage, save_path: str) -> bool:
    try:
        image.save(save_path)
        logger.info(f"Image saved at {save_path}")
        return True
    except ValueError as e:
        logger.error(e)
        return False


def save_file_as(source_window: ImageWindow | None, extract_path: bool = False) -> None:
    default_ask_save_params: FileDialogArgs = {
        "filetypes": FILE_TYPES,
        "defaultextension": "png",
    }
    if not source_window:
        logger.debug("Image to save is not selected")
        return None

    image_to_save = source_window.image
    save_path = source_window.source_path
    if not save_path:
        save_path = fd.asksaveasfilename(**default_ask_save_params)
    elif not extract_path:
        save_path = fd.asksaveasfilename(
            **default_ask_save_params,
            initialdir=os.path.split(save_path)[0],
            initialfile=os.path.split(save_path)[1],
        )

    if save_path and save_image(image_to_save, save_path):
        source_window.window_title = save_path


def duplicate_image(
    source_window: ImageWindow | None, source_image: PILImage | None = None
) -> None:
    if source_image:
        ImageWindow(source_image)
    elif source_window:
        ImageWindow(source_window.image)
    else:
        logger.debug("Image to duplicate is not selected")
        return None


class ColorIterator:
    def __init__(
        self,
        starting_color_name: ColorEnum = ColorEnum.GREYSCALE,
        color_diff: int = 1,
        max_value: int = MAX_INTENSITY_LEVEL,
    ):
        self.max_value = max_value
        match starting_color_name:
            case ColorEnum.GREYSCALE:
                self.starting_color = [-color_diff, -color_diff, -color_diff]
                self.iter_func = lambda colors: [c + color_diff for c in colors]
            case ColorEnum.RED:
                self.starting_color = [-color_diff, 0, 0]
                self.iter_func = lambda colors: [
                    colors[0] + color_diff,
                    colors[1],
                    colors[2],
                ]
            case ColorEnum.GREEN:
                self.starting_color = [0, -color_diff, 0]
                self.iter_func = lambda colors: [
                    colors[0],
                    colors[1] + color_diff,
                    colors[2],
                ]
            case ColorEnum.BLUE:
                self.starting_color = [0, 0, -color_diff]
                self.iter_func = lambda colors: [
                    colors[0],
                    colors[1],
                    colors[2] + color_diff,
                ]

    @staticmethod
    def get_hex(color: list[int]) -> str:
        return f'#{"".join(["%0.2X" % c for c in color])}'

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> str:
        self.starting_color = self.iter_func(self.starting_color)
        if all([c <= self.max_value for c in self.starting_color]):
            return self.get_hex(self.starting_color)
        raise StopIteration
