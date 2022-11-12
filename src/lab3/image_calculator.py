import logging
import tkinter as tk
from dataclasses import dataclass

from PIL import Image

from lab2.histogram_manipulation import LinearAdjustmentWidget
from utils.constants import ImageModeEnum, MAX_INTENSITY_LEVEL, MIN_INTENSITY_LEVEL
from utils.image_manager import ImageWindow
from utils.utils import duplicate_image

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImageMathOperators:
    ADDITION: str = '+'
    SUBTRACTION: str = '-'
    AND: str = '&'
    NOT: str = '~'
    OR: str = '|'
    XOR: str = '^'


def image_calculator(image_windows: list[ImageWindow], operation_type: str) -> None:
    if len(image_windows) < 1:
        return None
    match operation_type:
        case ImageMathOperators.ADDITION:
            ImageAdditionWidget(image_windows)
        case ImageMathOperators.SUBTRACTION:
            ImageSubtractionWidget(image_windows)
        case ImageMathOperators.AND:
            ImageAndWidget(image_windows)
        case ImageMathOperators.NOT:
            ImageNotWidget(image_windows)
        case ImageMathOperators.OR:
            ImageOrWidget(image_windows)
        case ImageMathOperators.XOR:
            ImageXorWidget(image_windows)
        case _:
            logger.error(ValueError(f'Incorrect image operator! {operation_type}'))


def check_window_images(image1: Image, image2: Image) -> bool:
    return image1.size == image2.size and image1.mode in [ImageModeEnum.GREYSCALE, ImageModeEnum.BINARY] \
           and image2.mode in [ImageModeEnum.GREYSCALE, ImageModeEnum.BINARY]


class ImageNotWidget(tk.Toplevel):
    def __init__(self, image_windows: list[ImageWindow]):
        super(ImageNotWidget, self).__init__()
        self.title('Image calculator')
        self.geometry('300x100')
        self.image_windows = image_windows
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        options = [window.window_title for window in self.image_windows]
        self.selected_image = tk.StringVar(value=options[0])

        tk.OptionMenu(self.frame, self.selected_image, *options).pack()

        self.close_button = tk.Button(self.frame, text='Apply', command=self.update_image)
        self.close_button.pack()

        self.frame.pack()

    def update_image(self, **_):
        selected_window = [image_window for image_window in self.image_windows
                           if image_window.window_title == self.selected_image.get()][0]
        selected_image = selected_window.image
        list_of_pixels = list(selected_image.getdata())
        match selected_image.mode:
            case ImageModeEnum.GREYSCALE | ImageModeEnum.BINARY:
                list_of_pixels = [~pixel + 2 ** 8 for pixel in list_of_pixels]
            case _:
                logger.error(ValueError('Invalid image format!'))

        inverted_image = Image.new(selected_image.mode, selected_image.size)
        inverted_image.putdata(list_of_pixels)
        duplicate_image(None, inverted_image)
        self.destroy()


class ImageAndWidget(tk.Toplevel):
    def __init__(self, image_windows: list[ImageWindow]):
        super(ImageAndWidget, self).__init__()
        self.title('Image calculator')
        self.geometry('400x150')
        self.image_windows = image_windows
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        options = [window.window_title for window in self.image_windows]
        self.selected_images = [tk.StringVar(value=options[0]), tk.StringVar(value=options[0])]

        tk.OptionMenu(self.frame, self.selected_images[0], *options).pack()
        tk.OptionMenu(self.frame, self.selected_images[1], *options).pack()

        self.warning_label = tk.StringVar(value='')
        tk.Label(self.frame, textvariable=self.warning_label).pack()

        self.close_button = tk.Button(self.frame, text='Apply', command=self.update_image)
        self.close_button.pack()

        self.frame.pack()

    def update_image(self, **_):
        selected_window_titles = [self.selected_images[i].get() for i in range(len(self.selected_images))]
        selected_windows = [image_window for image_window in self.image_windows
                            if image_window.window_title in selected_window_titles]
        if selected_window_titles[0] == selected_window_titles[1]:
            selected_windows.append(selected_windows[0])
        selected_images = [window.image for window in selected_windows]
        if not check_window_images(selected_images[0], selected_images[1]):
            self.warning_label.set('Images have to be binary or greyscale and have similar sizes!')
            return None

        list_of_pixels = [list(selected_images[0].getdata()), list(selected_images[1].getdata())]

        list_of_pixels = [pixel1 & pixel2 for pixel1, pixel2 in zip(list_of_pixels[0], list_of_pixels[1])]

        inverted_image = Image.new(selected_images[0].mode, selected_images[0].size)
        inverted_image.putdata(list_of_pixels)
        duplicate_image(None, inverted_image)
        self.destroy()


class ImageOrWidget(tk.Toplevel):
    def __init__(self, image_windows: list[ImageWindow]):
        super(ImageOrWidget, self).__init__()
        self.title('Image calculator')
        self.geometry('400x150')
        self.image_windows = image_windows
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        options = [window.window_title for window in self.image_windows]
        self.selected_images = [tk.StringVar(value=options[0]), tk.StringVar(value=options[0])]

        tk.OptionMenu(self.frame, self.selected_images[0], *options).pack()
        tk.OptionMenu(self.frame, self.selected_images[1], *options).pack()

        self.warning_label = tk.StringVar(value='')
        tk.Label(self.frame, textvariable=self.warning_label).pack()

        self.close_button = tk.Button(self.frame, text='Apply', command=self.update_image)
        self.close_button.pack()

        self.frame.pack()

    def update_image(self, **_):
        selected_window_titles = [self.selected_images[i].get() for i in range(len(self.selected_images))]
        selected_windows = [image_window for image_window in self.image_windows
                            if image_window.window_title in selected_window_titles]
        if selected_window_titles[0] == selected_window_titles[1]:
            selected_windows.append(selected_windows[0])
        selected_images = [window.image for window in selected_windows]
        if not check_window_images(selected_images[0], selected_images[1]):
            self.warning_label.set('Images have to be binary or greyscale and have similar sizes!')
            return None

        list_of_pixels = [list(selected_images[0].getdata()), list(selected_images[1].getdata())]

        list_of_pixels = [pixel1 | pixel2 for pixel1, pixel2 in zip(list_of_pixels[0], list_of_pixels[1])]

        inverted_image = Image.new(selected_images[0].mode, selected_images[0].size)
        inverted_image.putdata(list_of_pixels)
        duplicate_image(None, inverted_image)
        self.destroy()


class ImageXorWidget(tk.Toplevel):
    def __init__(self, image_windows: list[ImageWindow]):
        super(ImageXorWidget, self).__init__()
        self.title('Image calculator')
        self.geometry('400x150')
        self.image_windows = image_windows
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        options = [window.window_title for window in self.image_windows]
        self.selected_images = [tk.StringVar(value=options[0]), tk.StringVar(value=options[0])]

        tk.OptionMenu(self.frame, self.selected_images[0], *options).pack()
        tk.OptionMenu(self.frame, self.selected_images[1], *options).pack()

        self.warning_label = tk.StringVar(value='')
        tk.Label(self.frame, textvariable=self.warning_label).pack()

        self.close_button = tk.Button(self.frame, text='Apply', command=self.update_image)
        self.close_button.pack()

        self.frame.pack()

    def update_image(self, **_):
        selected_window_titles = [self.selected_images[i].get() for i in range(len(self.selected_images))]
        selected_windows = [image_window for image_window in self.image_windows
                            if image_window.window_title in selected_window_titles]
        if selected_window_titles[0] == selected_window_titles[1]:
            selected_windows.append(selected_windows[0])
        selected_images = [window.image for window in selected_windows]
        if not check_window_images(selected_images[0], selected_images[1]):
            self.warning_label.set('Images have to be binary or greyscale and have similar sizes!')
            return None

        list_of_pixels = [list(selected_images[0].getdata()), list(selected_images[1].getdata())]

        list_of_pixels = [pixel1 ^ pixel2 for pixel1, pixel2 in zip(list_of_pixels[0], list_of_pixels[1])]

        inverted_image = Image.new(selected_images[0].mode, selected_images[0].size)
        inverted_image.putdata(list_of_pixels)
        duplicate_image(None, inverted_image)
        self.destroy()


class ImageSubtractionWidget(tk.Toplevel):
    def __init__(self, image_windows: list[ImageWindow]):
        super(ImageSubtractionWidget, self).__init__()
        self.title('Image calculator')
        self.geometry('400x150')
        self.image_windows = image_windows
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        options = [window.window_title for window in self.image_windows]
        self.selected_images = [tk.StringVar(value=options[0]), tk.StringVar(value=options[0])]

        tk.OptionMenu(self.frame, self.selected_images[0], *options).pack()
        tk.OptionMenu(self.frame, self.selected_images[1], *options).pack()

        self.warning_label = tk.StringVar(value='')
        tk.Label(self.frame, textvariable=self.warning_label).pack()

        self.close_button = tk.Button(self.frame, text='Apply', command=self.update_image)
        self.close_button.pack()

        self.frame.pack()

    def update_image(self, **_):
        selected_window_titles = [self.selected_images[i].get() for i in range(len(self.selected_images))]
        selected_windows = [image_window for image_window in self.image_windows
                            if image_window.window_title in selected_window_titles]
        if selected_window_titles[0] == selected_window_titles[1]:
            selected_windows.append(selected_windows[0])
        selected_images = [window.image for window in selected_windows]
        if not check_window_images(selected_images[0], selected_images[1]):
            self.warning_label.set('Images have to be binary or greyscale and have similar sizes!')
            return None

        list_of_pixels = [list(selected_images[0].getdata()), list(selected_images[1].getdata())]

        list_of_pixels = [abs(pixel1 - pixel2) for pixel1, pixel2 in zip(list_of_pixels[0], list_of_pixels[1])]

        inverted_image = Image.new(selected_images[0].mode, selected_images[0].size)
        inverted_image.putdata(list_of_pixels)
        duplicate_image(None, inverted_image)
        self.destroy()


class ImageAdditionWidget(tk.Toplevel):
    def __init__(self, image_windows: list[ImageWindow]):
        super(ImageAdditionWidget, self).__init__()
        self.title('Image calculator')
        self.geometry('400x150')
        self.image_windows = image_windows
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        options = [window.window_title for window in self.image_windows]
        self.selected_images = [tk.StringVar(value=options[0]), tk.StringVar(value=options[0])]

        tk.OptionMenu(self.frame, self.selected_images[0], *options).pack()
        tk.OptionMenu(self.frame, self.selected_images[1], *options).pack()

        self.normalize_flag = tk.BooleanVar()
        tk.Checkbutton(self.frame, text='Normalize', variable=self.normalize_flag).pack()

        self.warning_label = tk.StringVar(value='')
        tk.Label(self.frame, textvariable=self.warning_label).pack()

        self.close_button = tk.Button(self.frame, text='Apply', command=self.update_image)
        self.close_button.pack()

        self.frame.pack()

    @staticmethod
    def normalize(list_of_pixels: list[int]) -> list[int]:
        min_in = min(list_of_pixels)
        max_in = max(list_of_pixels)
        if max_in > MAX_INTENSITY_LEVEL:
            max_out = MAX_INTENSITY_LEVEL
            min_out = max(max_out - max_in + min_in, MIN_INTENSITY_LEVEL)
        elif min_in < MIN_INTENSITY_LEVEL:
            min_out = MIN_INTENSITY_LEVEL
            max_out = min(min_out - min_in + max_in, MAX_INTENSITY_LEVEL)
        else:
            return list_of_pixels

        return [LinearAdjustmentWidget.calculate_linear_adjustment(pixel, min_in, max_in, min_out, max_out)
                for pixel in list_of_pixels]

    def update_image(self, **_):
        selected_window_titles = [self.selected_images[i].get() for i in range(len(self.selected_images))]
        selected_windows = [image_window for image_window in self.image_windows
                            if image_window.window_title in selected_window_titles]
        if selected_window_titles[0] == selected_window_titles[1]:
            selected_windows.append(selected_windows[0])
        selected_images = [window.image for window in selected_windows]
        if not check_window_images(selected_images[0], selected_images[1]):
            self.warning_label.set('Images have to be binary or greyscale and have similar sizes!')
            return None

        list_of_pixels = [list(selected_images[0].getdata()), list(selected_images[1].getdata())]

        list_of_pixels = [pixel1 + pixel2 for pixel1, pixel2 in zip(list_of_pixels[0], list_of_pixels[1])]
        if self.normalize_flag.get():
            list_of_pixels = self.normalize(list_of_pixels)

        inverted_image = Image.new(selected_images[0].mode, selected_images[0].size)
        inverted_image.putdata(list_of_pixels)
        duplicate_image(None, inverted_image)
        self.destroy()
