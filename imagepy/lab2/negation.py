import logging

from PIL import Image

from imagepy.utils.constants import MAX_INTENSITY_LEVEL, ImageModeEnum
from imagepy.utils.image_manager import ImageWindow

logger = logging.getLogger(__name__)


def invert_image(image_window: ImageWindow | None) -> None:
    if not image_window:
        return None

    source_image = image_window.image

    list_of_pixels = list(image_window.image.getdata())
    match source_image.mode:
        case ImageModeEnum.GREYSCALE:
            list_of_pixels = [MAX_INTENSITY_LEVEL - i for i in list_of_pixels]
        case ImageModeEnum.COLOR:
            list_of_pixels = [
                tuple([MAX_INTENSITY_LEVEL - j for j in i]) for i in list_of_pixels
            ]
        case _:
            logger.error(ValueError("Invalid image format!"))

    inverted_image = Image.new(source_image.mode, source_image.size)
    inverted_image.putdata(list_of_pixels)
    image_window.update_image(inverted_image)
