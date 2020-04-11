"""
Provides base application data
"""
import logging
from typing import List

import numpy as np

from PyQt5.QtCore import QObject

import als
from als.code_utilities import SignalingQueue, log
from als.model.base import Session

_LOGGER = logging.getLogger(__name__)

VERSION = als.__version__

WORKER_STATUS_IDLE = "-"

IMAGE_SAVE_TYPE_TIFF = "tiff"
IMAGE_SAVE_TYPE_PNG = "png"
IMAGE_SAVE_TYPE_JPEG = "jpg"

STACKED_IMAGE_FILE_NAME_BASE = "stack_image"
WEB_SERVED_IMAGE_FILE_NAME_BASE = "web_image"


# pylint: disable=R0903
class LocalizedStrings(QObject):
    """
    Holds global localized strings.

    All strings are initialized with dummy text and MUST be defined in setup()
    """

    STACKING_MODE_SUM = "TEMP"
    STACKING_MODE_MEAN = "TEMP"
    STRETCH_MODE_LOCAL = "TEMP"
    STRETCH_MODE_GLOBAL = "TEMP"
    WORKER_STATUS_BUSY = "TEMP"

    SCANNER = "TEMP"
    OF = "TEMP"

    RUNNING_M = "TEMP"
    RUNNING_F = "TEMP"
    STOPPED_M = "TEMP"
    STOPPED_F = "TEMP"
    PAUSED = "TEMP"

    WEB_SERVER = "TEMP"
    ADDRESS = "TEMP"

    def setup(self):
        """
        Sets real values for localized strings
        """
        LocalizedStrings.STACKING_MODE_SUM = self.tr("sum")
        LocalizedStrings.STACKING_MODE_MEAN = self.tr("mean")
        LocalizedStrings.STRETCH_MODE_LOCAL = self.tr("local")
        LocalizedStrings.STRETCH_MODE_GLOBAL = self.tr("global")
        LocalizedStrings.WORKER_STATUS_BUSY = self.tr("busy")
        LocalizedStrings.SCANNER = self.tr("scanner")
        LocalizedStrings.OF = self.tr("of")
        LocalizedStrings.RUNNING_M = self.tr("running", "gender m")
        LocalizedStrings.RUNNING_F = self.tr("running", "gender f")
        LocalizedStrings.STOPPED_M = self.tr("stopped", "gender m")
        LocalizedStrings.STOPPED_F = self.tr("stopped", "gender f")
        LocalizedStrings.PAUSED = self.tr("paused")
        LocalizedStrings.WEB_SERVER = self.tr("web server")
        LocalizedStrings.ADDRESS = self.tr("address")


# pylint: disable=R0902, R0903
class DynamicData:
    """
    Holds and maintain application dynamic data and notify observers on significant changes
    """
    def __init__(self):
        self.session = Session()
        self.web_server_is_running = False
        self.web_server_ip = ""
        self.stack_size = 0
        self.post_processor_result = None
        self.histogram_container: HistogramContainer = None
        self.pre_process_queue = SignalingQueue()
        self.stacker_queue = SignalingQueue()
        self.process_queue = SignalingQueue()
        self.save_queue = SignalingQueue()
        self.pre_processor_status = ""
        self.stacker_status = ""
        self.post_processor_status = ""
        self.saver_status = ""


class HistogramContainer:
    """
    Holds histogram data for an image (color or b&w)

    also holds the global maximum among all held histograms and a way to get the number of bins
    """
    @log
    def __init__(self):
        self._histograms: List[np.ndarray] = list()
        self._global_maximum: int = 0

    @log
    def add_histogram(self, histogram: np.ndarray):
        """
        Add an histogram

        :param histogram: the histogram to add
        :type histogram: numpy.ndarray
        :return:
        """
        self._histograms.append(histogram)

    @log
    def get_histograms(self) -> List[np.ndarray]:
        """
        Gets the histograms

        :return: the histograms
        :rtype: List[numpy.ndarray]
        """
        return self._histograms

    @property
    @log
    def global_maximum(self) -> int:
        """
        Gets the global maximum among all histograms

        :return: the global maximum among all histograms
        :rtype: int
        """
        return self._global_maximum

    @global_maximum.setter
    @log
    def global_maximum(self, value: int):
        """
        Sets the global maximum among all histograms

        :param value: the global maximum among all histograms
        :type value: int
        """
        self._global_maximum = value

    @property
    @log
    def bin_count(self):
        """
        Get the bin count, that is the length of any stored histogram. We check the first one if exists

        :return: the number of bins used to compute the stored histograms.
        :rtype: int
        """
        return len(self._histograms[0]) if self._histograms else 0


DYNAMIC_DATA = DynamicData()
