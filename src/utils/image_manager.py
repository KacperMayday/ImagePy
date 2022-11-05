import copy
import logging
import os
import time
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from src.utils.constants import ZoomEnum

logger = logging.getLogger(__name__)


class ImageWindow(tk.Toplevel):
    def __init__(self, image: Image, source_path: str | None = None):
        super().__init__()
        self.source_path: str = source_path
        self.image: Image = image
        self.displayed_image = copy.deepcopy(image)
        self.zoom_options = [ZoomEnum.ZOOM_10, ZoomEnum.ZOOM_20, ZoomEnum.ZOOM_25, ZoomEnum.ZOOM_50, ZoomEnum.ZOOM_100,
                             ZoomEnum.ZOOM_150, ZoomEnum.ZOOM_200, ZoomEnum.ZOOM_FULL]
        self.current_resize = self.zoom_options.index(ZoomEnum.ZOOM_100)
        self.mode: str = self.is_gray(self.image)
        self.window_id: str = self.calculate_window_id()
        self.default_file_name: str = 'Duplicated'
        self._img = None  # this is needed only to keep canvas image away from garbage collector
        self.frame = ttk.Frame(self)
        self.img_canvas = tk.Canvas(self.frame, scrollregion=(0, 0, self.image.width, self.image.height))
        self.hbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.hbar.config(command=self.img_canvas.xview)
        self.vbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vbar.config(command=self.img_canvas.yview)
        self.img_canvas.pack()
        self.update_image(self.image)

        self.frame.pack()
        self.window_title = self.source_path
        self.focus_set()
        self.bind("<FocusIn>", lambda _: ImageManager.set_focus(self))
        self.bind('<Destroy>', lambda _: ImageManager.set_focus(None))
        self.bind('<Control-MouseWheel>', self.resize)
        self.bind('<MouseWheel>', lambda e: self.img_canvas.yview_scroll(-1 * (e.delta // 120), "units"))

    @staticmethod
    def is_gray(img: Image) -> str:
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
        resize_option = self.zoom_options[self.current_resize]
        return f'{self.window_id} ' \
               f'{os.path.split(self.source_path)[-1] if self.source_path else self.default_file_name} ' \
               f'{resize_option if isinstance(resize_option, str) else int(resize_option * 100)}%'

    @window_title.setter
    def window_title(self, source_path: str | None = None):
        self.source_path = source_path
        self.title(self.window_title)

    def update_image(self, image: Image):
        self.image = image
        resize_scale = self.zoom_options[self.current_resize]
        self.resize_image(resize_scale)

    def refresh_display_image(self):
        self._img = ImageTk.PhotoImage(self.displayed_image)
        self.img_canvas.config(height=self._img.height(), width=self._img.width())
        self.img_canvas.create_image(0, 0, image=self._img, anchor=tk.NW)
        self.img_canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.window_title = self.source_path
        self.img_canvas.config(scrollregion=(0, 0, self.displayed_image.width, self.displayed_image.height))

    def resize(self, resize_event: tk.Event):
        self.current_resize -= resize_event.delta // 120
        if self.current_resize < 0:
            self.current_resize = 0
        elif self.current_resize >= len(self.zoom_options):
            self.current_resize = len(self.zoom_options) - 1

        resize_scale = self.zoom_options[self.current_resize]
        self.resize_image(resize_scale)

    def resize_image(self, resize_scale: float | str):
        if resize_scale == ZoomEnum.ZOOM_FULL:
            resize_scale = self.winfo_screenwidth() / self.image.width

        self.displayed_image = self.image.resize(
            (round(self.image.width * resize_scale), round(self.image.height * resize_scale)), Image.ANTIALIAS)
        self.refresh_display_image()


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
