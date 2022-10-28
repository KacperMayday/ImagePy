import logging
import os
import time
from tkinter import Label, Toplevel

from PIL import Image, ImageTk

logger = logging.getLogger(__name__)


class ImageWindow(Toplevel):
    def __init__(self, image: Image, source_path: str | None = None):
        super().__init__()
        self.source_path: str = source_path
        self.image: Image = image
        self.mode: str = self.is_gray(self.image)
        self.window_id: str = self.calculate_window_id()
        self.default_file_name: str = 'Duplicated'
        self.img_label = Label(master=self)
        self.img_label.pack()
        self.update_image(self.image)

        self.window_title = self.source_path
        self.focus_set()
        self.bind("<FocusIn>", lambda _: ImageManager.set_focus(self))
        self.bind('<Destroy>', lambda _: ImageManager.set_focus(None))

    @staticmethod
    def is_gray(img: Image) -> str:
        # if len(img.shape) < 3 or img.shape[2] == 1:
        #     return True
        #
        # b, g, r = img[:, :, 0], img[:, :, 1], img[:, :, 2]
        # if (b == g).all() and (b == r).all():
        #     return True
        #
        # return False
        return img.mode

    @staticmethod
    def calculate_window_id() -> str:
        id_max_digits_length = 9
        digits_separator = '-'
        digits_group_length = 3
        id_number = str(int(time.time()) % 10 ** id_max_digits_length)

        id_list = [id_number[max(i - digits_group_length, 0): i]
                   for i in range(len(id_number), 0, -digits_group_length)][::-1]
        window_id = digits_separator.join(id_list)
        return window_id

    @property
    def window_title(self) -> str:
        return f'{self.window_id} {os.path.split(self.source_path)[-1] if self.source_path else self.default_file_name}'

    @window_title.setter
    def window_title(self, source_path: str | None = None):
        self.source_path = source_path
        self.title(self.window_title)

    def update_image(self, image: Image):
        self.image = image
        img = ImageTk.PhotoImage(self.image)
        self.img_label.configure(image=img)
        self.img_label.image = img


class ImageManager:
    focused_window = None

    @staticmethod
    def set_focus(window: ImageWindow | None) -> None:
        if ImageManager.focused_window is not window:
            ImageManager.focused_window = window
            ImageManager.get_focus_window()

    @staticmethod
    def get_focus_window() -> ImageWindow | None:
        focused_window = ImageManager.focused_window
        if focused_window:
            msg = f'Window name: {focused_window.window_title} Image mode: {focused_window.mode}'
        else:
            msg = None

        logger.debug(f'Selected window: {msg}')
        return focused_window
