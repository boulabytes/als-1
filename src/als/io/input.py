"""
Provides everything need to handle ALS main inputs : images.

We need to read file and in the future, get images from INDI
"""
import logging
from abc import abstractmethod

from PyQt5.QtCore import QObject

_LOGGER = logging.getLogger(__name__)


class InputListener(QObject):
    """
    In charge of input management, **abstract class**
    """

    @staticmethod
    def create_listener(listener_type):
        """
        Creates specialized input listeners.

        :param listener_type: what type of listener to create
        :type listener_type: str : allowed values :

          - 'FS' to create a filesystem listener

        :return: an input listener
        :rtype: FileSystemListener
        """
        pass

    @abstractmethod
    def start(self):
        """
        Start listening for new images.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stop listening for new images.
        """
        pass


class FileSystemListener(InputListener):
    """
    Watches file changes (creation, move) in a specific filesystem folder
    """
    pass


def read_image(path):
    """
    Reads an image from disk

    :param path: path to the file to load image from
    :type path:  pathlib.Path

    :return: the image read from disk
    :rtype: Image
    """
    pass
