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


@dataclass(frozen=True)
class ZoomEnum:
    ZOOM_10: float = 0.1
    ZOOM_20: float = 0.2
    ZOOM_25: float = 0.25
    ZOOM_50: float = 0.5
    ZOOM_100: float = 1
    ZOOM_150: float = 1.5
    ZOOM_200: float = 2
    ZOOM_FULL: str = 'FULL'
