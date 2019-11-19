"""
Main module, basically in charge of application init / start
"""
import locale
import logging
import os
import platform
import sys

from pathlib import Path

import psutil
from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication

from als import config
from als.logic import Controller
from als.code_utilities import Timer
from als.model.data import VERSION
from als.ui.windows import MainWindow

_LOGGER = logging.getLogger(__name__)


def log_sys_info():
    """
    Log detailed info about current running system
    """

    _LOGGER.debug("***************************************************************************")
    _LOGGER.debug('System info dump - START')
    _LOGGER.debug(f"Platform name         : {sys.platform}")
    _LOGGER.debug(f"Platform architecture : {platform.architecture()}")
    _LOGGER.debug(f"Machine name          : {platform.machine()}")
    _LOGGER.debug(f"CPU type              : {platform.processor()}")
    _LOGGER.debug(f"CPU count             : {os.cpu_count()}")
    _LOGGER.debug(f"OS name               : {platform.system()}")
    _LOGGER.debug(f"OS release            : {platform.release()}")
    _LOGGER.debug(f"Available memory      : {psutil.virtual_memory().available}")
    _LOGGER.debug(f"Python version        : {sys.version}")
    _LOGGER.debug('System info dump - END')
    _LOGGER.debug("***************************************************************************")


def main():
    """
    Application launcher
    """

    with Timer() as startup:
        app = QApplication(sys.argv)
        config.setup()

        log_sys_info()

        # look for existing "Stacker" processes and kill them
        #
        # Those Stacker processes are leftovers from a previous ALS crash occurring while stacking
        # using multiprocessing
        for process in psutil.process_iter():
            if process.name() == "Stacker" and process.status() != psutil.STATUS_ZOMBIE:
                process.kill()

        with open(Path(__file__).parent / "main.css", "r") as style_file:

            sheet = style_file.read()
            app.setStyleSheet(sheet)

        # get system locale and install translators
        system_locale = locale.getlocale()[0]
        _LOGGER.debug(f"Detected system locale = {system_locale}")
        locale_prefix = system_locale[:system_locale.find("_")]
        _LOGGER.debug(f"System locale prefix = {locale_prefix}")
        i18n_folder_path = Path(__file__).parent.parent.parent / 'i18n'
        _LOGGER.debug(f"i18n folder path = {i18n_folder_path}")

        translators = list()
        for component in ["als", "qtbase"]:
            i18n_file_name = f'{component}_{locale_prefix}'
            translator = QTranslator()
            if translator.load(i18n_file_name, str(i18n_folder_path)):
                _LOGGER.debug(f"Translation successfully loaded for {i18n_file_name}")
                translator.setObjectName(i18n_file_name)
                translators.append(translator)

        for translator in translators:
            if app.installTranslator(translator):
                _LOGGER.debug(f"Translator successfully installed for {translator.objectName()}")

        _LOGGER.debug("Building and showing main window")
        controller = Controller()
        window = MainWindow(controller)

        window.reset_image_view()

    _LOGGER.info(QApplication.translate(
        "main",
        "Astro Live Stacker version {} started in {} ms.").format(VERSION, startup.elapsed_in_milli_as_str))

    app_return_code = app.exec()
    controller.shutdown()

    _LOGGER.info(QApplication.translate(
        "main",
        "Astro Live Stacker terminated with return code = {}").format(app_return_code))

    sys.exit(app_return_code)


if __name__ == "__main__":
    main()
