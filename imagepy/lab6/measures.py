import logging
import math
from tkinter import filedialog as fd

import cv2
import numpy as np

from imagepy.utils.constants import FileDialogArgs, ImageModeEnum
from imagepy.utils.image_manager import ImageWindow

logger = logging.getLogger(__name__)


def calculate_measures(image_window: ImageWindow | None) -> None:
    if not image_window or image_window.mode != ImageModeEnum.GREYSCALE:
        return None
    MeasuresWidget(image_window)


class Measures:
    def __init__(self, cnt: np.ndarray):
        convex_hull = cv2.convexHull(cnt)
        convex_hull_area = cv2.contourArea(convex_hull, False)
        self.area: float = cv2.contourArea(cnt, False)
        self.perimeter: float = cv2.arcLength(cnt, True)
        self.w1: float = 2 * pow(self.area / math.pi, 0.5)
        self.w2: float = self.perimeter / math.pi
        self.w3: float = (self.perimeter / (2 * pow(self.area * math.pi, 0.5))) - 1
        self.w9: float = 2 * pow(math.pi * self.area, 0.5) / self.perimeter
        self.w10: float = self.area / convex_hull_area
        moments = cv2.moments(cnt)
        self.m1: float = moments["nu20"] + moments["nu02"]
        self.m2: float = pow(moments["nu20"] - moments["nu02"], 2) + 4 * pow(
            moments["nu11"], 2
        )
        self.m3: float = pow(moments["nu30"] - 3 * moments["nu12"], 2) + pow(
            3 * moments["nu21"] - moments["nu03"], 2
        )
        self.moments = moments

        logger.debug("Created Measure object with following data:")
        logger.debug(f"{self.area=}")
        logger.debug(f"{self.perimeter=}")
        logger.debug(f"{self.w1=}")
        logger.debug(f"{self.w2=}")
        logger.debug(f"{self.w3=}")
        logger.debug(f"{self.w9=}")
        logger.debug(f"{self.w10=}")
        logger.debug(f"{self.m1=}")
        logger.debug(f"{self.m2=}")
        logger.debug(f"{self.m3=}")
        logger.debug(f"{self.moments=}")


class MeasuresWidget:
    def __init__(self, source_window: ImageWindow):
        super(MeasuresWidget, self).__init__()
        self.image = source_window.image
        self.measures = self.get_measures()
        self.save_measures()

    @staticmethod
    def get_save_path() -> str | None:
        default_ask_save_params: FileDialogArgs = {
            "filetypes": (("CSV file", "*.csv"),),
            "defaultextension": "csv",
        }
        save_path = fd.asksaveasfilename(**default_ask_save_params)

        return save_path

    def save_measures(self) -> None:
        save_path = self.get_save_path()
        if save_path:
            measure_vals = []
            for measure in self.measures:
                measure_dict = measure.__dict__
                measure_dict.update(measure_dict.pop("moments"))
                measure_vals.append(list(measure_dict.values()))

            measure_arr = np.array(measure_vals)
            measure_cols = list(self.measures[0].__dict__.keys())
            sep = ";"

            # noinspection PyTypeChecker
            np.savetxt(
                save_path,
                measure_arr,
                fmt=" %1.4f",
                delimiter=sep,
                header=sep.join(measure_cols),
                comments="",
            )

            with open(save_path, "r+") as f:
                content = f.read()
                f.seek(0, 0)
                f.write(f'"sep={sep}"\n' + content)

    def get_measures(self) -> list[Measures]:
        image_array: np.ndarray = np.array(self.image)
        contours, _hierarchy = cv2.findContours(
            image_array, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        measures = [Measures(cnt) for cnt in contours]
        return measures
