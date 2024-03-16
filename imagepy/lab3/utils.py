from imagepy.utils.constants import ImageModeEnum
from imagepy.utils.image_manager import ImageWindow


def convert_to_binary(source_window: ImageWindow | None) -> None:
    if not source_window or source_window.mode != ImageModeEnum.GREYSCALE:
        return None

    source_window.update_image(source_window.image.convert("1"))
