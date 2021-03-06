"""
Provides all dialogs used in ALS GUI
"""
import logging
from pathlib import Path

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox, QApplication

import als.model.data
from als import config
from als.code_utilities import log
from als.logic import Controller
from als.model.data import VERSION, DYNAMIC_DATA, WORKER_STATUS_BUSY
from generated.about_ui import Ui_AboutDialog
from generated.prefs_ui import Ui_PrefsDialog
from generated.save_wait_ui import Ui_SaveWaitDialog

_LOGGER = logging.getLogger(__name__)
_WARNING_STYLE_SHEET = "border: 1px solid orange"
_NORMAL_STYLE_SHEET = "border: 1px"


class PreferencesDialog(QDialog):
    """
    Our main preferences dialog box
    """

    @log
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui = Ui_PrefsDialog()
        self._ui.setupUi(self)

        self._ui.ln_scan_folder_path.setText(config.get_scan_folder_path())
        self._ui.ln_work_folder_path.setText(config.get_work_folder_path())
        self._ui.ln_web_server_port.setText(str(config.get_www_server_port_number()))
        self._ui.spn_webpage_refresh_period.setValue(config.get_www_server_refresh_period())
        self._ui.chk_debug_logs.setChecked(config.is_debug_log_on())
        self._ui.spn_minimum_match_count.setValue(config.get_minimum_match_count())
        self._ui.chk_use_dark.setChecked(config.get_use_master_dark())
        self._ui.ln_master_dark_path.setText(config.get_master_dark_file_path())

        config_to_image_save_type_mapping = {

            als.model.data.IMAGE_SAVE_TYPE_JPEG: self._ui.radioSaveJpeg,
            als.model.data.IMAGE_SAVE_TYPE_PNG:  self._ui.radioSavePng,
            als.model.data.IMAGE_SAVE_TYPE_TIFF: self._ui.radioSaveTiff
        }

        config_to_image_save_type_mapping[config.get_image_save_format()].setChecked(True)

        self._validate_all_paths()

    @log
    def _validate_all_paths(self):
        """
        Draw a red border around text fields containing a path to a missing folder
        """

        for ui_field in [self._ui.ln_work_folder_path, self._ui.ln_scan_folder_path]:

            if not Path(ui_field.text()).is_dir():
                ui_field.setStyleSheet(_WARNING_STYLE_SHEET)
            else:
                ui_field.setStyleSheet(_NORMAL_STYLE_SHEET)

        master_dark_path = self._ui.ln_master_dark_path.text()
        if (Path(master_dark_path).is_file() or
                (not master_dark_path and not self._ui.chk_use_dark.isChecked())):
            self._ui.ln_master_dark_path.setStyleSheet(_NORMAL_STYLE_SHEET)
        else:
            self._ui.ln_master_dark_path.setStyleSheet(_WARNING_STYLE_SHEET)

    @log
    def on_chk_use_dark_toggled(self, _):
        """
        Triggers config values validation when chk_use_dark is toggled

        :param _: well, you know, we really don't care. This the method we call that will check this
        """
        self._validate_all_paths()

    @log
    @pyqtSlot()
    def on_btn_dark_clear_clicked(self):
        """
        Clears dark path input field and validate settings
        """
        self._ui.ln_master_dark_path.clear()
        self._validate_all_paths()

    @log
    @pyqtSlot()
    def accept(self):
        """checks and stores user settings"""
        config.set_scan_folder_path(self._ui.ln_scan_folder_path.text())
        config.set_work_folder_path(self._ui.ln_work_folder_path.text())
        web_server_port_number_str = self._ui.ln_web_server_port.text()
        config.set_minimum_match_count(self._ui.spn_minimum_match_count.value())
        config.set_use_master_dark(self._ui.chk_use_dark.isChecked())
        config.set_master_dark_file_path(self._ui.ln_master_dark_path.text())

        if web_server_port_number_str.isdigit() and 1024 <= int(web_server_port_number_str) <= 65535:
            config.set_www_server_port_number(web_server_port_number_str)
        else:
            message = "Web server port number must be a number between 1024 and 65535"
            error_box("Wrong value", message)
            _LOGGER.error(f"Port number validation failed : {message}")
            self._ui.ln_web_server_port.setFocus()
            self._ui.ln_web_server_port.selectAll()
            return

        config.set_www_server_refresh_period(self._ui.spn_webpage_refresh_period.value())

        config.set_debug_log(self._ui.chk_debug_logs.isChecked())

        image_save_type_to_config_mapping = {

            self._ui.radioSaveJpeg: als.model.data.IMAGE_SAVE_TYPE_JPEG,
            self._ui.radioSavePng: als.model.data.IMAGE_SAVE_TYPE_PNG,
            self._ui.radioSaveTiff: als.model.data.IMAGE_SAVE_TYPE_TIFF
        }

        for radio_button, image_save_type in image_save_type_to_config_mapping.items():
            if radio_button.isChecked():
                config.set_image_save_format(image_save_type)
                break

        PreferencesDialog._save_config()

        super().accept()

    @pyqtSlot(name="on_btn_browse_scan_clicked")
    @log
    def browse_scan(self):
        """Opens a folder dialog to choose scan folder"""
        scan_folder_path = QFileDialog.getExistingDirectory(self,
                                                            _("Select scan folder"),
                                                            self._ui.ln_scan_folder_path.text())
        if scan_folder_path:
            self._ui.ln_scan_folder_path.setText(scan_folder_path)

        self._validate_all_paths()

    @pyqtSlot(name="on_btn_browse_work_clicked")
    @log
    def browse_work(self):
        """Opens a folder dialog to choose work folder"""
        work_folder_path = QFileDialog.getExistingDirectory(self,
                                                            _("Select work folder"),
                                                            self._ui.ln_work_folder_path.text())
        if work_folder_path:
            self._ui.ln_work_folder_path.setText(work_folder_path)

        self._validate_all_paths()

    @pyqtSlot(name="on_btn_dark_scan_clicked")
    @log
    def browse_dark(self):
        """Opens a folder dialog to choose dark file"""
        dark_file_path = QFileDialog.getOpenFileName(self,
                                                     _("Select dark file"),
                                                     self._ui.ln_master_dark_path.text())
        if dark_file_path[0]:
            self._ui.ln_master_dark_path.setText(dark_file_path[0])

        self._validate_all_paths()

    @staticmethod
    @log
    def _save_config():

        try:
            config.save()
        except config.CouldNotSaveConfig as save_error:
            error_box(save_error.message, f"Your settings could not be saved\n\nDetails : {save_error.details}")


class AboutDialog(QDialog):
    """
    Our about dialog box
    """

    @log
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui = Ui_AboutDialog()
        self._ui.setupUi(self)
        self._ui.lblVersionValue.setText(VERSION)


class SaveWaitDialog(QDialog):
    """
    Dialog shown while waiting for all pending image saves to complete
    """
    @log
    def __init__(self, controller: Controller, parent=None):
        super().__init__(parent)
        self._ui = Ui_SaveWaitDialog()
        self._ui.setupUi(self)

        self._controller = controller

        self.update_display(_)
        self._controller.add_model_observer(self)

    @log
    def update_display(self, _):
        """
        Update display
        """

        remaining_image_count = self.count_remaining_images()
        self._ui.lbl_remaining_saves.setText(str(remaining_image_count))

        if remaining_image_count == 0:
            self._controller.remove_model_observer(self)
            self.close()

    @log
    def count_remaining_images(self):
        """
        Count images that still need to be saved.

        We count 1 image to save for each image in the queues and each worker still Busy and also
        take 'save every image' setting and web server status into account

        :return: the number of images remaining to be saved
        :rtype: int
        """

        remaining_image_save_count = 0

        for status in [

                DYNAMIC_DATA.pre_processor_status,
                DYNAMIC_DATA.stacker_status,
                DYNAMIC_DATA.post_processor_status,
        ]:
            if status == WORKER_STATUS_BUSY:
                remaining_image_save_count += 1

        for queue_size in [

                DYNAMIC_DATA.pre_process_queue.qsize(),
                DYNAMIC_DATA.stacker_queue.qsize(),
                DYNAMIC_DATA.process_queue.qsize(),
        ]:
            remaining_image_save_count += queue_size

        additional_saves_per_image = [
            self._controller.get_save_every_image(), DYNAMIC_DATA.web_server_is_running].count(True)

        remaining_image_save_count *= 1 + additional_saves_per_image

        remaining_image_save_count += 1 if DYNAMIC_DATA.saver_status == WORKER_STATUS_BUSY else 0
        remaining_image_save_count += DYNAMIC_DATA.save_queue.qsize()

        return remaining_image_save_count

    @log
    @pyqtSlot()
    def on_btn_quit_clicked(self):
        """
        Qt slot called when user clicks 'Discard unsaved images and quit'
        """
        self.close()


@log
def question(title, message, default_yes: bool = True):
    """
    Asks a question to user in a Qt MessageBox and return True/False as Yes/No

    :param title: Title of the box
    :param message: Message displayed in the box

    :param default_yes: set 'yes' button as the default button
    :type default_yes: bool

    :return: True if user replies "Yes", False otherwise
    """

    default_button = QMessageBox.Yes if default_yes else QMessageBox.No

    return QMessageBox.Yes == QMessageBox.question(
        QApplication.activeWindow(),
        title,
        message,
        QMessageBox.Yes | QMessageBox.No,
        default_button)


@log
def warning_box(title, message):
    """
    Displays a waring Qt MessageBox

    :param title: Title of the box
    :param message: Message displayed in the box
    :return: None
    """
    message_box('Warning : ' + title, message, QMessageBox.Warning)


@log
def error_box(title, message):
    """
    Displays an error Qt MessageBox

    :param title: Title of the box
    :param message: Message displayed in the box
    :return: None
    """
    message_box('Error : ' + title, message, QMessageBox.Critical)


@log
def message_box(title, message, icon=QMessageBox.Information):
    """
    Displays a Qt MessageBox with custom icon : Info by default

    :param title: Title of the box
    :param message: Message displayed in the box
    :param icon: The icon to show
    :return: None
    """
    box = QMessageBox()
    box.setIcon(icon)
    box.setWindowTitle(title)
    box.setText(message)
    box.exec()
