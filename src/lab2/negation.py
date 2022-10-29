import logging

from PIL import Image

from src.utils.constants import ImageModeEnum, MAX_INTENSITY_LEVEL
from src.utils.image_manager import ImageWindow

logger = logging.getLogger(__name__)


def invert_image(image_window: ImageWindow) -> None:
    if not image_window:
        return None

    source_image = image_window.image

    list_of_pixels = list(image_window.image.getdata())
    match source_image.mode:
        case ImageModeEnum.GREYSCALE:
            list_of_pixels = [MAX_INTENSITY_LEVEL - i for i in list_of_pixels]
        case ImageModeEnum.COLOUR:
            list_of_pixels = [tuple([MAX_INTENSITY_LEVEL - j for j in i]) for i in list_of_pixels]
        case _:
            logger.error(ValueError('Niepoprawny format obrazu!'))

    inverted_image = Image.new(source_image.mode, source_image.size)
    inverted_image.putdata(list_of_pixels)
    image_window.update_image(inverted_image)
