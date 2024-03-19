import logging
import tkinter as tk

from imagepy import ROOT_DIR
from imagepy.utils.gui.menu import create_menu

logger = logging.getLogger(__name__)


class App:
    @staticmethod
    def run() -> None:
        logger.debug("Creating window...")

        root = tk.Tk()
        menubar = create_menu(root)
        root.config(menu=menubar)
        root.title("ImagePy")
        root.geometry("400x0")

        logger.info("Starting...")
        root.mainloop()


def setup_logging(log_level: int = logging.INFO) -> None:
    module_root_logger = logging.getLogger(ROOT_DIR.stem)
    module_root_logger.setLevel(log_level)


def shell() -> None:
    setup_logging()
    app = App()
    app.run()


if __name__ == "__main__":
    shell()
