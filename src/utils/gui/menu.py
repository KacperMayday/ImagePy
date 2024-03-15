import logging
import tkinter as tk

from lab3.image_calculator import ImageMathOperators, image_calculator
from lab3.image_math import image_math
from lab3.utils import convert_to_binary
from lab4.edge_detection import edge_detection
from lab4.filter_operations import filter_calculation
from lab4.median_blur_filter import median_blur
from lab6.binary_operations import binary_calculation
from lab6.measures import calculate_measures
from lab_project.logic_filter import logic_filter
from src.debug.debug import create_debug_menu
from src.lab1.histogram import show_histogram
from src.lab2.histogram_manipulation import (
    gamma_correction,
    histogram_equalization,
    linear_adjustment,
)
from src.lab2.negation import invert_image
from src.lab2.threshold import threshold_filter
from src.lab_project.plot_profile import plot_profile, show_plot_info
from src.utils.image_manager import ImageManager
from src.utils.utils import duplicate_image, open_file, save_file_as
from utils.constants import DEBUG

logger = logging.getLogger(__name__)


def not_implemented():
    logger.error(NotImplementedError("To be implemented..."))


def create_menu(root: tk.Toplevel | tk.Tk) -> tk.Menu:
    menubar = tk.Menu(root)
    custom_font = ("", 13)

    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open", command=open_file, font=custom_font)
    file_menu.add_command(
        label="Save",
        command=lambda: save_file_as(
            ImageManager.get_focus_window(), extract_path=True
        ),
        font=custom_font,
    )
    file_menu.add_command(
        label="Save as...",
        command=lambda: save_file_as(ImageManager.get_focus_window()),
        font=custom_font,
    )

    file_menu.add_separator()

    file_menu.add_command(label="Exit", command=root.quit, font=custom_font)
    menubar.add_cascade(label="File", menu=file_menu)

    edit_menu = tk.Menu(menubar, tearoff=0)
    edit_menu.add_command(
        label="Duplicate",
        command=lambda: duplicate_image(ImageManager.get_focus_window()),
        font=custom_font,
    )

    edit_menu.add_separator()

    edit_menu.add_command(
        label="Threshold",
        command=lambda: threshold_filter(ImageManager.get_focus_window()),
        font=custom_font,
    )
    edit_menu.add_command(
        label="Invert",
        command=lambda: invert_image(ImageManager.get_focus_window()),
        font=custom_font,
    )
    edit_menu.add_command(
        label="To binary",
        command=lambda: convert_to_binary(ImageManager.get_focus_window()),
        font=custom_font,
    )
    menubar.add_cascade(label="Image", menu=edit_menu)

    process_menu = tk.Menu(menubar, tearoff=0)
    process_menu.add_command(
        label="Histogram equalization",
        command=lambda: histogram_equalization(ImageManager.get_focus_window()),
        font=custom_font,
    )
    process_menu.add_command(
        label="Linear stretching",
        command=lambda: linear_adjustment(ImageManager.get_focus_window()),
        font=custom_font,
    )
    process_menu.add_command(
        label="Gamma correction",
        command=lambda: gamma_correction(ImageManager.get_focus_window()),
        font=custom_font,
    )

    process_menu.add_separator()

    image_calculator_menu = tk.Menu(menubar, tearoff=0)
    process_menu.add_cascade(
        label="Image Calculator", menu=image_calculator_menu, font=custom_font
    )
    image_calculator_menu.add_command(
        label="Add",
        command=lambda: image_calculator(
            ImageManager.image_windows, ImageMathOperators.ADDITION
        ),
        font=custom_font,
    )
    image_calculator_menu.add_command(
        label="Subtract",
        command=lambda: image_calculator(
            ImageManager.image_windows, ImageMathOperators.SUBTRACTION
        ),
        font=custom_font,
    )

    image_calculator_menu.add_separator()

    image_calculator_menu.add_command(
        label="Not",
        command=lambda: image_calculator(
            ImageManager.image_windows, ImageMathOperators.NOT
        ),
        font=custom_font,
    )
    image_calculator_menu.add_command(
        label="And",
        command=lambda: image_calculator(
            ImageManager.image_windows, ImageMathOperators.AND
        ),
        font=custom_font,
    )
    image_calculator_menu.add_command(
        label="Or",
        command=lambda: image_calculator(
            ImageManager.image_windows, ImageMathOperators.OR
        ),
        font=custom_font,
    )
    image_calculator_menu.add_command(
        label="Xor",
        command=lambda: image_calculator(
            ImageManager.image_windows, ImageMathOperators.XOR
        ),
        font=custom_font,
    )

    process_menu.add_command(
        label="Math",
        command=lambda: image_math(ImageManager.get_focus_window()),
        font=custom_font,
    )

    process_menu.add_separator()

    process_menu.add_command(
        label="Binary operations",
        command=lambda: binary_calculation(ImageManager.get_focus_window()),
        font=custom_font,
    )

    menubar.add_cascade(label="Process", menu=process_menu)

    filter_menu = tk.Menu(menubar, tearoff=0)
    filter_menu.add_command(
        label="Blur image",
        command=lambda: filter_calculation(
            ImageManager.get_focus_window(), blur_flag=True
        ),
        font=custom_font,
    )
    filter_menu.add_command(
        label="Sharpen image",
        command=lambda: filter_calculation(
            ImageManager.get_focus_window(), blur_flag=False
        ),
        font=custom_font,
    )
    filter_menu.add_command(
        label="Edge detection",
        command=lambda: edge_detection(ImageManager.get_focus_window()),
        font=custom_font,
    )
    filter_menu.add_command(
        label="Median blur",
        command=lambda: median_blur(ImageManager.get_focus_window()),
        font=custom_font,
    )
    filter_menu.add_separator()
    filter_menu.add_command(
        label="Advanced edge detection",
        command=lambda: edge_detection(
            ImageManager.get_focus_window(), advanced_filter=True
        ),
        font=custom_font,
    )
    filter_menu.add_command(
        label="Canny operator",
        command=lambda: edge_detection(
            ImageManager.get_focus_window(), canny_detection=True
        ),
        font=custom_font,
    )
    menubar.add_cascade(label="Filters", menu=filter_menu)

    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(
        label="Histogram",
        command=lambda: show_histogram(ImageManager.get_focus_window()),
        font=custom_font,
    )
    help_menu.add_command(
        label="Export measures",
        command=lambda: calculate_measures(ImageManager.get_focus_window()),
        font=custom_font,
    )
    menubar.add_cascade(label="Analyze", menu=help_menu)

    project_menu = tk.Menu(menubar, tearoff=0)
    plot_profile_menu = tk.Menu(menubar, tearoff=0)
    plot_profile_menu.add_command(
        label="Free drawing",
        command=lambda: ImageManager.get_focus_window().constant_move(),
        font=custom_font,
    )
    plot_profile_menu.add_command(
        label="Line drawing",
        command=lambda: ImageManager.get_focus_window().point_move(),
        font=custom_font,
    )
    plot_profile_menu.add_command(
        label="Clear",
        command=lambda: ImageManager.get_focus_window().clear_drawing(),
        font=custom_font,
    )
    plot_profile_menu.add_separator()
    plot_profile_menu.add_command(
        label="Plot",
        command=lambda: plot_profile(ImageManager.get_focus_window()),
        font=custom_font,
    )
    plot_profile_menu.add_separator()
    plot_profile_menu.add_command(
        label="Info", command=show_plot_info, font=custom_font
    )
    project_menu.add_cascade(
        label="Plot profile", menu=plot_profile_menu, font=custom_font
    )
    project_menu.add_command(
        label="Logic filters",
        command=lambda: logic_filter(ImageManager.get_focus_window()),
        font=custom_font,
    )
    menubar.add_cascade(label="Project", menu=project_menu)

    if DEBUG:
        menubar.add_cascade(label="Debug", menu=create_debug_menu(menubar))

    return menubar
