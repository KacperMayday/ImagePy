import logging

from PIL import Image

from lab1.histogram import HistogramWidget
from utils.constants import ImageModeEnum, MAX_INTENSITY_LEVEL
from utils.image_manager import ImageWindow

logger = logging.getLogger(__name__)


# TODO usunąć
def gui_mock(source_window: ImageWindow) -> None:
    mocked_func = linear_adjustment
    if not source_window:
        return None

    image = source_window.image

    list_of_pixels = mocked_func(image)

    inverted_image = Image.new(image.mode, image.size)
    inverted_image.putdata(list_of_pixels)
    source_window.update_image(inverted_image)


def calculate_linear_adjustment(pixel_value: int, min_value: int, max_value: int) -> int:
    if pixel_value < min_value:
        return min_value
    elif pixel_value > max_value:
        return max_value
    else:
        if max_value == min_value:
            return pixel_value
        return (pixel_value - min_value) * MAX_INTENSITY_LEVEL // (max_value - min_value)


def linear_adjustment(image: Image) -> list[int] | list[tuple[int, int, int]]:
    list_of_pixels = list(image.getdata())
    stretch_threshold_coefficient = 0.00
    threshold = round(stretch_threshold_coefficient * len(list_of_pixels))
    match image.mode:
        case ImageModeEnum.GREYSCALE:
            # TODO dodać min_value i max_value i threshold do GUI
            sorted_list = sorted(list_of_pixels)
            max_value = max(sorted_list[:-threshold if threshold != 0 else -1])
            min_value = min(sorted_list[threshold:])
            # max_value = max(list_of_pixels)
            # min_value = min(list_of_pixels)
            list_of_pixels = [calculate_linear_adjustment(i, min_value, max_value) for i in list_of_pixels]
        # case ImageModeEnum.GREYSCALE:
        #     max_value = [max([i[j] for i in list_of_pixels]) for j in range(3)]
        #     min_value = [min([i[j] for i in list_of_pixels]) for j in range(3)]
        #     list_of_pixels = [tuple([calculate_linear_adjustment(j, min_v, max_v)
        #                              for j, max_v, min_v in zip(i, max_value, min_value)])
        #                       for i in list_of_pixels]
        case _:
            logger.error(ValueError('Niepoprawny format obrazu!'))

    return list_of_pixels


def histogram_equalization(image: Image) -> list[int] | list[tuple[int, int, int]]:
    list_of_pixels = list(image.getdata())
    histogram = HistogramWidget.count_values(image)
    max_intensity_level = MAX_INTENSITY_LEVEL + 1
    histogram_list = [0] * max_intensity_level
    for i in histogram:
        histogram_list[i] = histogram[i]

    histogram_cumulative_distributor = [sum(histogram_list[:i + 1]) for i in range(len(histogram_list))]
    dim = len(list_of_pixels)
    hcd_min = min(i for i in histogram_cumulative_distributor if i > 0)
    list_of_pixels = [(histogram_cumulative_distributor[p] - hcd_min) * (max_intensity_level - 1) // (dim - hcd_min)
                      for p in list_of_pixels]

    return list_of_pixels


def calculate_gamma_adjustment(pixel_value: int, gamma_coefficient: float,
                               max_intensity_value: int = MAX_INTENSITY_LEVEL) -> int:
    return round(((pixel_value / max_intensity_value) ** (1 / gamma_coefficient)) * MAX_INTENSITY_LEVEL)


def gamma_correction(image: Image) -> list[int] | list[tuple[int, int, int]]:
    # TODO dodać gamma do GUI
    gamma_coefficient = 0.5
    list_of_pixels = list(image.getdata())
    match image.mode:
        case ImageModeEnum.GREYSCALE:
            list_of_pixels = [calculate_gamma_adjustment(i, gamma_coefficient) for i in list_of_pixels]
        # case ImageModeEnum.GREYSCALE:
        #     list_of_pixels = [tuple([calculate_gamma_adjustment(j, gamma_coefficient) for j in pixel]) for pixel in
        #                       list_of_pixels]
        case _:
            logger.error(ValueError('Niepoprawny format obrazu!'))

    return list_of_pixels
