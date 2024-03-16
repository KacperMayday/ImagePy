from dataclasses import dataclass
from enum import Enum, StrEnum, unique
from typing import Final, TypedDict

MAX_INTENSITY_LEVEL: Final = 255
MIN_INTENSITY_LEVEL: Final = 0
FILE_TYPES: Final = (("Obraz", "*.bmp *tif *png *jpg"),)
DEBUG: Final = False

FileDialogArgs: Final = TypedDict(
    "FileDialogArgs", {"filetypes": tuple[tuple[str, str]], "defaultextension": str}
)


@unique
class ImageModeEnum(StrEnum):
    COLOR: str = "RGB"
    GREYSCALE: str = "L"
    BINARY: str = "1"


@unique
class ColorEnum(StrEnum):
    GREYSCALE: str = "black"
    RED: str = "red"
    BLUE: str = "blue"
    GREEN: str = "green"


@unique
class ZoomEnum(Enum):
    ZOOM_10: float = 0.1
    ZOOM_20: float = 0.2
    ZOOM_25: float = 0.25
    ZOOM_50: float = 0.5
    ZOOM_100: float = 1
    ZOOM_150: float = 1.5
    ZOOM_200: float = 2
    ZOOM_FULL: str = "FULL"


@unique
class BinaryOperationEnum(StrEnum):
    OPEN: str = "Open"
    CLOSE: str = "Close"
    ERODE: str = "Erode"
    DILATE: str = "Dilate"


@unique
class LogicFilterEnum(StrEnum):
    HORIZONTAL: str = "Horizontal lines and isolated points"
    VERTICAL: str = "Vertical lines and isolated points"
    ISOLATED_POINTS: str = "Only isolated points"
