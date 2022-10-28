import tkinter as tk

from PIL import Image

from lab1.histogram import show_histogram
from utils.image_manager import ImageWindow


def main():
    filename = '../resources/1lsb.png'
    image = Image.open(filename)
    # Put it in the display window
    image_window = ImageWindow(source_path=filename, image=image)
    root = tk.Tk()
    root.title('ROOT')
    show_histogram(image_window)

    root.mainloop()


if __name__ == '__main__':
    main()
