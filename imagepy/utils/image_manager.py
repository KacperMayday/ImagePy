import copy
import logging
import os
import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import Literal

import numpy as np
from PIL import ImageTk
from PIL.Image import Image as PILImage
from PIL.Image import Resampling

from imagepy.utils.constants import ZoomEnum

logger = logging.getLogger(__name__)

Point = tuple[int, int]


def bresenham(start: Point, end: Point) -> list[Point]:
    """
    Calculate list of points for given starting and ending points

    :param start: line starting point
    :param end: line ending point
    :return: list of points on given line
    """
    x, y = start
    x1, y1 = end
    points_in_line = []
    dx = abs(x1 - x)
    dy = abs(y1 - y)
    sx = -1 if x > x1 else 1
    sy = -1 if y > y1 else 1

    if dx > dy:  # determine direction
        err = dx / 2
        while x != x1:
            points_in_line.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2
        while y != y1:
            points_in_line.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    points_in_line.append((x, y))
    return points_in_line


class ImageWindow(tk.Toplevel):
    """
    Main class representing window with an image. It is selectable, zoomable and has drawing functionality.
    """

    def __init__(self, image: PILImage, source_path: str | None = None):
        super().__init__()
        # image OS absolute path
        self.source_path: str | None = source_path
        self.image: PILImage = image
        # make a copy of original image to prevent changing it
        self.displayed_image = copy.deepcopy(image)
        # define zoom order and possible options
        self.zoom_options = [
            ZoomEnum.ZOOM_10,
            ZoomEnum.ZOOM_20,
            ZoomEnum.ZOOM_25,
            ZoomEnum.ZOOM_50,
            ZoomEnum.ZOOM_100,
            ZoomEnum.ZOOM_150,
            ZoomEnum.ZOOM_200,
            ZoomEnum.ZOOM_FULL,
        ]
        # set default zoom
        self.current_resize = self.zoom_options.index(ZoomEnum.ZOOM_100)
        # unique window id number
        self.window_id: str = self.calculate_window_id()
        self.default_file_name: str = "Duplicated"
        self._img = ImageTk.PhotoImage(self.displayed_image)
        self.widget_frame: ttk.Frame = ttk.Frame(self)
        self.img_canvas = tk.Canvas(
            self.widget_frame, scrollregion=(0, 0, self.image.width, self.image.height)
        )
        self.hbar = tk.Scrollbar(self.widget_frame, orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.hbar.config(command=self.img_canvas.xview)
        self.vbar = tk.Scrollbar(self.widget_frame, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vbar.config(command=self.img_canvas.yview)
        self.img_canvas.pack()
        self.update_image(self.image)

        self.widget_frame.pack()
        self.window_title = self.source_path  # type: ignore
        # set focus for new window
        self.focus_set()
        # register this window in ImageManager
        ImageManager.add_window(self)
        # bind controls
        self.bind("<FocusIn>", lambda _: ImageManager.set_focus(self))
        self.bind("<Destroy>", lambda _: ImageManager.delete_window(self))
        self.bind("<Control-MouseWheel>", self.resize)
        self.bind(
            "<MouseWheel>",
            lambda e: self.img_canvas.yview_scroll(-1 * (e.delta // 120), "units"),
        )

        # project
        self.previous_coords: tuple[int, int] | None = None
        self.lines: list[int] = []
        self.drawn_coords: list[tuple[int, int]] = []
        # define line parameters for tk.Canvas.create_line() method
        self._line_width = 2
        self._line_fill_color = "#f5e505"

    def clear_drawing(self) -> None:
        """
        Resets drawing state.
        """
        self.img_canvas.configure(cursor="arrow")
        self.clear_canvas()
        self.img_canvas.unbind("<B1-Motion>")
        self.img_canvas.unbind("<Button-1>")
        self.img_canvas.unbind("<ButtonRelease-1>")

    def clear_canvas(self, _event: tk.Event | None = None) -> None:
        """
        Clears and prepares canvas for new drawing.

        :param _event: Provided by tkinter bind method. Not used.
        """
        self.previous_coords = None
        for line in self.lines:
            self.img_canvas.delete(line)
        self.lines = []
        self.drawn_coords = []

    def mouse_draw(self, event: tk.Event) -> None:
        """
        Draws lines on image canvas and saves selected coordinates

        :param event: tkinter event from bind method
        """
        current_coords = (event.x, event.y)
        logger.debug(
            [
                *current_coords,
                np.array(self.image)[current_coords[::-1]],
                datetime.now(),
            ]
        )
        if self.previous_coords is not None:
            self.lines.append(
                self.img_canvas.create_line(
                    self.previous_coords,
                    current_coords,
                    width=self._line_width,
                    fill=self._line_fill_color,
                )
            )
            coords_bresenham = bresenham(self.previous_coords, current_coords)

            # last item in draw_coords is previous_coords from previous iteration,
            # so it have to be removed to avoid duplicates
            if len(self.drawn_coords) > 0:
                self.drawn_coords.pop()

            # points are given by (x, y) but it should be reverted (y, x) for future numpy array indexing
            coords_bresenham = [c[::-1] for c in coords_bresenham]
            self.drawn_coords.extend(coords_bresenham)
        else:
            self.clear_canvas()

        self.previous_coords = current_coords

    def point_move(self) -> None:
        """
        Sets canvas drawing mode to point/line mode
        """
        self.clear_drawing()
        self.img_canvas.configure(cursor="pencil")
        self.img_canvas.bind("<Button-1>", self.mouse_draw)
        self.img_canvas.bind("<Button-3>", self.clear_canvas)

    def constant_move(self) -> None:
        """
        Sets canvas drawing mode to free drawing
        """
        self.clear_drawing()
        self.img_canvas.configure(cursor="pencil")
        self.img_canvas.bind("<B1-Motion>", self.mouse_draw)
        self.img_canvas.bind("<Button-1>", self.mouse_draw)

        def clear_previous_coords_when_released(_event: tk.Event | None = None) -> None:
            """
            :param _event: Provided by tkinter bind method. Not used.
            """
            self.previous_coords = None

        # clear previous coordinates when LMB is released
        self.img_canvas.bind("<ButtonRelease-1>", clear_previous_coords_when_released)

    @property
    def mode(self) -> str:
        return self.image.mode

    @staticmethod
    def calculate_window_id() -> str:
        id_max_digits_length = 9
        digits_separator = "-"
        digits_group_length = 3
        id_number = str(int(time.time()) % 10**id_max_digits_length)

        id_list = [
            id_number[max(i - digits_group_length, 0) : i]
            for i in range(len(id_number), 0, -digits_group_length)
        ][::-1]
        window_id = digits_separator.join(id_list)
        return window_id

    @property
    def window_title(self) -> str:
        resize_option = self.zoom_options[self.current_resize].value
        if isinstance(resize_option, str):
            image_size = resize_option
        else:
            image_size = f"{int(resize_option * 100)}%"
        return (
            f"{self.window_id} "
            f"{os.path.split(self.source_path)[-1] if self.source_path else self.default_file_name} "
            f"{self.image.mode} "
            f"{image_size}"
        )

    @window_title.setter
    def window_title(self, source_path: str | None) -> None:
        self.source_path = source_path
        self.title(self.window_title)

    def update_image(self, image: PILImage) -> None:
        self.image = image
        resize_scale = self.zoom_options[self.current_resize]
        self.resize_image(resize_scale.value)

    def refresh_display_image(self) -> None:
        self._img.paste(self.displayed_image)
        self.img_canvas.config(height=self._img.height(), width=self._img.width())
        self.img_canvas.create_image(0, 0, image=self._img, anchor=tk.NW)
        self.img_canvas.config(
            xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set
        )
        self.window_title = self.source_path  # type: ignore
        self.img_canvas.config(
            scrollregion=(0, 0, self.displayed_image.width, self.displayed_image.height)
        )

    def resize(self, resize_event: tk.Event) -> None:
        self.current_resize -= resize_event.delta // 120
        if self.current_resize < 0:
            self.current_resize = 0
        elif self.current_resize >= len(self.zoom_options):
            self.current_resize = len(self.zoom_options) - 1

        resize_scale = self.zoom_options[self.current_resize]
        self.resize_image(resize_scale.value)

    def resize_image(self, resize_scale: float | Literal[ZoomEnum.ZOOM_FULL]) -> None:
        if (
            resize_scale == ZoomEnum.ZOOM_FULL
            or resize_scale == ZoomEnum.ZOOM_FULL.value
        ):
            resize_scale = self.winfo_screenwidth() / self.image.width

        self.displayed_image = self.image.resize(
            (
                round(self.image.width * resize_scale),
                round(self.image.height * resize_scale),
            ),
            Resampling.LANCZOS,
        )
        self.refresh_display_image()


class ImageManager:
    image_windows: list[ImageWindow] = []
    focused_window = None

    @staticmethod
    def set_focus(window: ImageWindow | None) -> None:
        if ImageManager.focused_window is not window:
            ImageManager.focused_window = window
            ImageManager.get_focus_window()

    @staticmethod
    def add_window(window: ImageWindow) -> None:
        if window.window_id not in [w.window_id for w in ImageManager.image_windows]:
            ImageManager.image_windows.append(window)

    @staticmethod
    def delete_window(deleted_window: ImageWindow) -> None:
        ImageManager.image_windows = [
            w
            for w in ImageManager.image_windows
            if w.window_id != deleted_window.window_id
        ]

    @staticmethod
    def get_focus_window() -> ImageWindow | None:
        focused_window = ImageManager.focused_window
        if focused_window:
            msg = f"Window name: {focused_window.window_title} Image mode: {focused_window.mode}"
        else:
            msg = None

        logger.debug(f"Selected window: {msg}")
        return focused_window
