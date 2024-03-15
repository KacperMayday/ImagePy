import tkinter as tk

import numpy as np

from utils.constants import MAX_INTENSITY_LEVEL, ImageModeEnum
from utils.image_manager import ImageWindow


def plot_profile(image_window: ImageWindow):
    """
    Entry function checking prerequisites for plot profile functionality.
    :param image_window: selected image window
    """
    # image_window must have at least 2 points drawn, it is impossible to plot profile line with fewer points
    if image_window is None or len(image_window.drawn_coords) < 2:
        return None
    PlotProfileWidget(image_window)


def show_plot_info():
    """
    Creates tutorial box for plot profile line functionality
    """
    msg = """
            Instructions for plotting profiles:
1. Draw line by selecting either Free drawing or Line drawing.
    1a. Free drawing.
        Press and hold LMB to draw line on image.
        To erase current line release and press LMB.
    1b. Line drawing.
        Click on image to start drawing,
        then click to choose line's end.
        Click to draw another line.
        To erase current lines press RMB.
2. Select Plot option to generate profile plot.
3. To stop drawing and clear image canvas select Clear option.
            """
    tk.messagebox.showinfo(title="Plot functionality info", message=msg)


class PlotProfileWidget(tk.Toplevel):
    def __init__(self, source_window: ImageWindow):
        super(PlotProfileWidget, self).__init__()
        self.title(source_window.window_title)
        self.image_window = source_window
        self.geometry("550x400")
        self.pack_propagate(False)
        self.frame = tk.Frame(self)

        # define constants
        self.plot_height = 255
        self.plot_width = 400
        self.line_width = 1
        self.checkerboard_size = 50
        self.checkerboard_lines_interval = 5
        self.checkerboard_lines_size = (
            self.checkerboard_size // self.checkerboard_lines_interval
        )
        self.checkerboard_lines_length = 10
        self.legend_canvas_size = 40
        self.n_points = len(self.image_window.drawn_coords) - 1
        self.min_height = self.line_width * 2
        self.max_height = self.plot_height - self.line_width * 2

        self.drawn_coords = self.image_window.drawn_coords
        self.image_array = np.array(self.image_window.image)

        plot_frame = self.create_plot_frame()
        plot_frame.pack(pady=(10, 0))
        self.frame.pack()

        self.pixel_value_var = tk.StringVar()
        self.pixel_distance_var = tk.StringVar()
        # sets initial vars values
        self.unset_string_vars()

        tk.Label(self.frame, textvariable=self.pixel_distance_var).pack()
        tk.Label(self.frame, textvariable=self.pixel_value_var).pack()

    def create_plot_frame(self) -> tk.Frame:
        """
        Creates frame containing plot and legend
        """
        frame = tk.Frame(self.frame)
        horizontal_canvas = tk.Canvas(
            frame, width=self.plot_width, height=self.legend_canvas_size
        )
        vertical_canvas = tk.Canvas(
            frame, width=self.legend_canvas_size, height=self.plot_height
        )
        plot_canvas = tk.Canvas(
            frame,
            width=self.plot_width,
            height=self.plot_height,
            bg="white",
            cursor="tcross",
        )
        self.draw_checkerboard(plot_canvas, horizontal_canvas, vertical_canvas)
        match self.image_window.mode:
            case ImageModeEnum.BINARY:
                self.image_array = self.image_array.astype(int) * MAX_INTENSITY_LEVEL
                self.plot_mono_profile(plot_canvas)
            case ImageModeEnum.GREYSCALE:
                self.plot_mono_profile(plot_canvas)
            case ImageModeEnum.COLOUR:
                self.plot_colour_profile(plot_canvas)
            case _:
                raise AttributeError("Not allowed image mode to profile!")

        plot_canvas.bind("<Motion>", self.set_string_vars)
        plot_canvas.bind("<Leave>", self.unset_string_vars)

        horizontal_canvas.grid(column=1, row=1)
        vertical_canvas.grid(column=0, row=0)
        plot_canvas.grid(column=1, row=0)

        return frame

    def draw_checkerboard(
        self,
        canvas: tk.Canvas,
        horizontal_canvas: tk.Canvas,
        vertical_canvas: tk.Canvas,
    ) -> None:
        def scale_width(size: int) -> int:
            return size * self.plot_width // self.n_points

        def scale_height(size: int) -> int:
            return size * self.plot_height // MAX_INTENSITY_LEVEL

        checkerboard_width_scaled = scale_width(self.checkerboard_size)
        checkerboard_height_scaled = scale_height(self.checkerboard_size)
        lines_width_interval = (
            checkerboard_width_scaled // self.checkerboard_lines_interval
        )
        lines_height_interval = (
            checkerboard_height_scaled // self.checkerboard_lines_interval
        )
        offset = 5
        legend_padding = 10

        for ii, i in enumerate(range(0, self.plot_width, checkerboard_width_scaled)):
            canvas.create_line(i, 0, i, self.plot_height, fill="gray")
            for j in range(
                i + lines_width_interval,
                i + checkerboard_width_scaled - lines_width_interval,
                lines_width_interval,
            ):
                canvas.create_line(
                    j,
                    self.plot_height,
                    j,
                    self.plot_height - self.checkerboard_lines_length,
                    fill="gray",
                )
            horizontal_canvas.create_text(
                i + offset, legend_padding, text=ii * self.checkerboard_size
            )

        horizontal_canvas.create_text(
            self.plot_width // 2, legend_padding * 3, text="pixel distance"
        )

        for ii, i in enumerate(
            range(
                self.plot_height - checkerboard_height_scaled,
                0,
                -checkerboard_height_scaled,
            )
        ):
            canvas.create_line(0, i, self.plot_width, i, fill="gray")
            for j in range(
                i + checkerboard_height_scaled - lines_height_interval,
                i,
                -lines_height_interval,
            ):
                canvas.create_line(0, j, self.checkerboard_lines_length, j, fill="gray")
            vertical_canvas.create_text(
                self.legend_canvas_size - legend_padding,
                i + offset,
                text=(ii + 1) * self.checkerboard_size,
            )

        # PyCharm inspection does not recognize angle argument
        # noinspection PyArgumentList
        vertical_canvas.create_text(
            self.legend_canvas_size - legend_padding * 3,
            self.plot_height // 2,
            text="pixel value",
            angle=90,
        )

    def plot_mono_profile(self, canvas: tk.Canvas) -> None:
        """
        Plots profile line for mono pixel values.
        :param canvas: plot canvas
        """
        for i in range(len(self.drawn_coords[:-1])):
            current_value = (
                self.min_height
                + self.max_height
                - self.image_array[self.drawn_coords[i + 1]]
                * self.max_height
                / MAX_INTENSITY_LEVEL
            )
            previous_value = (
                self.min_height
                + self.max_height
                - self.image_array[self.drawn_coords[i]]
                * self.max_height
                / MAX_INTENSITY_LEVEL
            )

            coord_x = self.plot_width * i / self.n_points
            canvas.create_line(
                coord_x,
                previous_value,
                self.plot_width * (i + 1) / self.n_points,
                current_value,
                width=self.line_width,
            )

    def plot_colour_profile(self, canvas: tk.Canvas) -> None:
        """
        Plots profile line for each RGB channel.
        :param canvas: plot canvas
        """
        for j, c in enumerate(["red", "green", "blue"]):
            for i in range(len(self.drawn_coords[:-1])):
                current_value = (
                    self.min_height
                    + self.max_height
                    - self.image_array[self.drawn_coords[i + 1]][j]
                    * self.max_height
                    / MAX_INTENSITY_LEVEL
                )
                previous_value = (
                    self.min_height
                    + self.max_height
                    - self.image_array[self.drawn_coords[i]][j]
                    * self.max_height
                    / MAX_INTENSITY_LEVEL
                )

                coord_x = self.plot_width * i / self.n_points
                canvas.create_line(
                    coord_x,
                    previous_value,
                    self.plot_width * (i + 1) / self.n_points,
                    current_value,
                    width=self.line_width,
                    fill=c,
                )

    def set_string_vars(self, event: tk.Event):
        """
        Sets string labels based on mouse position.

        :param event: tkinter event provided by bind method. Contains mouse x coordinate as event.x
        """
        pixel_distance = event.x * self.n_points // self.plot_width
        self.pixel_distance_var.set(f"Pixel distance: {pixel_distance}")
        self.pixel_value_var.set(f"Pixel value: {self.get_pixel_value(pixel_distance)}")

    def get_pixel_value(self, pixel_distance: int) -> str | int:
        """
        For given pixel distance returns pixel value for mono images
        or formatted string with RGB values for colour images
        :param pixel_distance: pixel distance from line starting point, basically an index of self.drawn_coords
        :return: formatted string with RGB values or pixel value integer
        """
        try:
            pixel_value = self.image_array[self.drawn_coords[pixel_distance]]
        except IndexError:
            pixel_value = "---"  # tkinter detects mouse on boundaries, so it may lead to IndexError, which is ok

        # pixel_value is ndarray if image is RGB
        if type(pixel_value) == np.ndarray:
            pixel_value = (
                f"red {pixel_value[0]}, green {pixel_value[1]}, blue: {pixel_value[2]}"
            )

        return pixel_value

    def unset_string_vars(self, _event: tk.Event | None = None):
        """
        Unsets vars to default state.
        :param _event: Not used.
        """
        self.pixel_distance_var.set(f"Pixel distance: ---")
        self.pixel_value_var.set(f"Pixel value: ---")
