import logging
import tkinter as tk
from tkinter import filedialog as fd

import cv2
import numpy as np

from utils.constants import ImageModeEnum
from utils.image_manager import ImageWindow

logger = logging.getLogger(__name__)


def calculate_measures(image_window: ImageWindow):
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None
    MeasuresWidget(image_window)


class Measures:
    def __init__(self, cnt: np.array):
        x, y, w, h = cv2.boundingRect(cnt)
        rect_area = w * h
        convex_hull = cv2.convexHull(cnt)
        convex_hull_area = cv2.contourArea(convex_hull)

        self.moments: dict[str, float] = cv2.moments(cnt)
        self.area: float = cv2.contourArea(cnt)
        self.perimeter: float = cv2.arcLength(cnt, True)
        self.aspect_ratio: float = w / h
        self.extent: float = self.area / rect_area
        self.solidity: float = self.area / convex_hull_area
        self.equivalent_diameter: float = np.sqrt(4 * self.area / np.pi)

        logger.debug('Created Measure object with following data:')
        logger.debug(f'{self.moments=}')
        logger.debug(f'{self.area=}')
        logger.debug(f'{self.perimeter=}')
        logger.debug(f'{self.aspect_ratio=}')
        logger.debug(f'{self.extent=}')
        logger.debug(f'{self.solidity=}')
        logger.debug(f'{self.equivalent_diameter=}')


class MeasuresFrame(tk.Frame):
    def __init__(self, root: tk.Frame):
        super(MeasuresFrame, self).__init__(root)
        tk.Label(self, text='Measures').pack()


# class MeasuresWidget(tk.Toplevel):
class MeasuresWidget:
    def __init__(self, source_window: ImageWindow):
        super(MeasuresWidget, self).__init__()
        # self.title(source_window.window_title)
        # self.image_window = source_window
        self.image = source_window.image
        # self.geometry('300x250')
        # self.pack_propagate(False)
        # self.frame = tk.Frame(self)

        # MeasuresFrame(self.frame).pack()
        self.measures = self.get_measures()

        # tk.Button(self.frame, text='Export to csv', command=self.save_measures).pack()
        # tk.Button(self.frame, text='Close', command=self.destroy).pack()
        #
        # self.frame.pack()
        self.save_measures()

    @staticmethod
    def get_save_path() -> str:
        default_ask_save_params = {'filetypes': (('CSV file', '*.csv'),), 'defaultextension': 'csv'}
        save_path = fd.asksaveasfilename(**default_ask_save_params)

        return save_path

    def save_measures(self):
        save_path = self.get_save_path()
        if save_path:
            measure_vals = []
            for measure in self.measures:
                measure_dict = measure.__dict__
                measure_dict.update(measure_dict.pop('moments'))
                measure_vals.append(list(measure_dict.values()))

            measure_vals = np.array(measure_vals)
            measure_cols = list(self.measures[0].__dict__.keys())

            # noinspection PyTypeChecker
            np.savetxt(save_path, measure_vals, fmt='%1.4f', delimiter=',', header=','.join(measure_cols), comments='')

    def get_measures(self) -> list[Measures]:
        image_array = np.array(self.image)
        contours, _hierarchy = cv2.findContours(image_array, 1, 2)
        measures = [Measures(cnt) for cnt in contours]
        return measures
