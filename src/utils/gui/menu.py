import logging
import tkinter as tk

from debug.debug import create_debug_menu
from lab1.histogram import show_histogram
from lab2.histogram_manipulation import histogram_equalization
from lab2.negation import invert_image
from lab2.threshold import threshold_filter
from utils.image_manager import ImageManager
from utils.utils import duplicate_image, open_file, save_file_as

logger = logging.getLogger(__name__)


def not_implemented():
    logger.error(NotImplementedError('To be implemented...'))


def create_menu(root: tk.Toplevel | tk.Tk) -> tk.Menu:
    menubar = tk.Menu(root)
    custom_font = ('', 13)

    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open", command=open_file, font=custom_font)
    file_menu.add_command(label="Save",
                          command=lambda: save_file_as(ImageManager.get_focus_window(), extract_path=True),
                          font=custom_font)
    file_menu.add_command(label="Save as...", command=lambda: save_file_as(ImageManager.get_focus_window()),
                          font=custom_font)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit, font=custom_font)
    menubar.add_cascade(label="File", menu=file_menu)

    edit_menu = tk.Menu(menubar, tearoff=0)
    edit_menu.add_command(label="Duplicate", command=lambda: duplicate_image(ImageManager.get_focus_window()),
                          font=custom_font)
    edit_menu.add_separator()
    edit_menu.add_command(label="Threshold", command=lambda: threshold_filter(ImageManager.get_focus_window()),
                          font=custom_font)
    edit_menu.add_command(label="Invert", command=lambda: invert_image(ImageManager.get_focus_window()),
                          font=custom_font)
    menubar.add_cascade(label="Image", menu=edit_menu)

    process_menu = tk.Menu(menubar, tearoff=0)
    process_menu.add_command(label="Histogram equalization",
                             command=lambda: histogram_equalization(ImageManager.get_focus_window()),
                             font=custom_font)
    process_menu.add_command(label="Image Calculator", command=not_implemented, font=custom_font)
    menubar.add_cascade(label="Process", menu=process_menu)

    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="Histogram", command=lambda: show_histogram(ImageManager.get_focus_window()),
                          font=custom_font)
    menubar.add_cascade(label="Analyze", menu=help_menu)

    menubar.add_cascade(label="Debug", menu=create_debug_menu(menubar))

    return menubar
