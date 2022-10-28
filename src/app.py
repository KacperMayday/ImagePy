import logging
import tkinter as tk

from utils.gui.menu import create_menu

logger = logging.getLogger(__name__)


class App:
    @staticmethod
    def run():
        logger.debug('Creating window...')

        root = tk.Tk()
        menubar = create_menu(root)
        root.config(menu=menubar)
        root.title('ImagePy')
        root.geometry('400x0')

        logger.info('Starting...')
        root.mainloop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    pil_logger = logging.getLogger('PIL')
    pil_logger.setLevel(logging.INFO)
    app = App()
    app.run()
