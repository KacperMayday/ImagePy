import logging
import os
from tkinter import filedialog as fd

from PIL import Image, UnidentifiedImageError

from utils.constants import ColourEnum, FILE_TYPES, MAX_INTENSITY_LEVEL
from utils.image_manager import ImageWindow

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
    logger.info(f'Image opened from {filename}')


def save_image(image: Image, save_path: str) -> bool:
    try:
        image.save(save_path)
        logger.info(f'Image saved at {save_path}')
        return True
    except ValueError as e:
        logger.error(e)
        return False


def save_file_as(source_window: ImageWindow, extract_path: bool = False) -> None:
    default_ask_save_params = {'filetypes': FILE_TYPES, 'defaultextension': 'png'}
    if not source_window:
        logger.debug('Image to save is not selected')
        return None

    image_to_save = source_window.image
    save_path = source_window.source_path
    if not save_path:
        save_path = fd.asksaveasfilename(**default_ask_save_params)
    elif not extract_path:
        save_path = fd.asksaveasfilename(**default_ask_save_params, initialdir=os.path.split(save_path)[0])

    if save_path and save_image(image_to_save, save_path):
        source_window.window_title = save_path


def duplicate_image(source_window: ImageWindow | None) -> None:
    if source_window:
        ImageWindow(source_window.image)
    else:
        logger.debug('Image to duplicate is not selected')
        return None


class ColourIterator:
    def __init__(self, starting_colour_name: str = 'black', colour_diff: int = 1, max_value: int = MAX_INTENSITY_LEVEL):
        self.max_value = max_value
        match starting_colour_name:
            case ColourEnum.GREYSCALE:
                self.starting_colour = [-colour_diff, -colour_diff, -colour_diff]
                self.iter_func = lambda colours: [c + colour_diff for c in colours]
            case ColourEnum.RED:
                self.starting_colour = [-colour_diff, 0, 0]
                self.iter_func = lambda colours: [colours[0] + colour_diff, colours[1], colours[2]]
            case ColourEnum.GREEN:
                self.starting_colour = [0, -colour_diff, 0]
                self.iter_func = lambda colours: [colours[0], colours[1] + colour_diff, colours[2]]
            case ColourEnum.BLUE:
                self.starting_colour = [0, 0, -colour_diff]
                self.iter_func = lambda colours: [colours[0], colours[1], colours[2] + colour_diff]

    @staticmethod
    def get_hex(colour: list[int, int, int]) -> str:
        return f'#{"".join(["%0.2X" % c for c in colour])}'

    def __iter__(self):
        return self

    def __next__(self):
        self.starting_colour = self.iter_func(self.starting_colour)
        if all([c <= self.max_value for c in self.starting_colour]):
            return self.get_hex(self.starting_colour)
        raise StopIteration
