import logging
from tkinter import Menu

from utils.image_manager import ImageManager

logger = logging.getLogger(__name__)


def create_debug_menu(menubar: Menu) -> Menu:
    debug_menu = Menu(menubar, tearoff=0)
    debug_menu.add_command(label="Selected image", command=ImageManager.get_focus_window)
    return debug_menu
