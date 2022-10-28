from utils.constants import ImageModeEnum
from utils.image_manager import ImageWindow


def threshold(pixel_value: int, min_threshold_level: int, max_threshold_level: int, min_intensity_level: int,
              max_intensity_level: int) -> int:
    if min_threshold_level <= pixel_value <= max_threshold_level:
        return max_intensity_level
    else:
        return min_intensity_level


def threshold_filter(image_window: ImageWindow) -> None:
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None

    # TODO dodać min_value i max_value do GUI
    min_threshold_level = 0
    max_threshold_level = 150
    min_intensity_level = 0
    max_intensity_level = 255

    source_image = image_window.image
    filtered_image = source_image.point(lambda p: threshold(p, min_threshold_level, max_threshold_level,
                                                            min_intensity_level, max_intensity_level))
    image_window.update_image(filtered_image)
