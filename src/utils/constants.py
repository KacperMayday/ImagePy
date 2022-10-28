from dataclasses import dataclass

MAX_INTENSITY_LEVEL = 255
MIN_INTENSITY_LEVEL = 0
FILE_TYPES = (('Obraz', '*.bmp *tif *png *jpg'),)


@dataclass(frozen=True)
class ImageModeEnum:
    COLOUR: str = 'RGB'
    GREYSCALE: str = 'L'


@dataclass(frozen=True)
class ColourEnum:
    GREYSCALE: str = 'black'
    RED: str = 'red'
    BLUE: str = 'blue'
    GREEN: str = 'green'
