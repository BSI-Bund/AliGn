import logging
from os.path import abspath

from PySide6.QtWidgets import QDialog, QFileDialog

from align.ui.DialogOpenNpy import Ui_OpenNpyDialogFrame


class NpyImporter:
    """reates a QDialog for selecting npy-Files
    Selected files dict is avalaible after dialog is closed
    via method get_npy_files()
    """

    def __init__(self, last_path=""):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.npy_files = dict()
        self.last_path = last_path

        # create a "hosting" Dialog
        self.npy_dialog = QDialog()
        # create Instance of ui class
        self.open_npy_dialog_frame = Ui_OpenNpyDialogFrame()
        # call setupUi and provide hosting frame
        self.open_npy_dialog_frame.setupUi(self.npy_dialog)
        self.open_npy_dialog_frame.bt_select_em_2.clicked.connect(
            lambda: self._handle_select_file_button_clicked("em")
        )
        self.open_npy_dialog_frame.bt_select_power_2.clicked.connect(
            lambda: self._handle_select_file_button_clicked("power")
        )
        self.open_npy_dialog_frame.bt_select_plain.clicked.connect(
            lambda: self._handle_select_file_button_clicked("plain")
        )
        self.open_npy_dialog_frame.bt_select_cipher.clicked.connect(
            lambda: self._handle_select_file_button_clicked("cipher")
        )
        self.open_npy_dialog_frame.bt_select_aux.clicked.connect(
            lambda: self._handle_select_file_button_clicked("aux")
        )
        self.open_npy_dialog_frame.btn_load_files.clicked.connect(
            self._handle_load_button_clicked
        )
        self.open_npy_dialog_frame.btn_cancel.clicked.connect(
            self._handle_cancel_button_clicked
        )

    def _handle_select_file_button_clicked(self, type_name: str):
        logging.info("Button %s clicked.", type_name)
        filename = self._selectFile(type_name)
        if type_name == "em":
            self.open_npy_dialog_frame.lineEdit.setText(filename)
        elif type_name == "power":
            self.open_npy_dialog_frame.lineEdit_4.setText(filename)
        elif type_name == "plain":
            self.open_npy_dialog_frame.lineEdit_3.setText(filename)
        elif type_name == "cipher":
            self.open_npy_dialog_frame.lineEdit_6.setText(filename)
        elif type_name == "aux":
            self.open_npy_dialog_frame.lineEdit_8.setText(filename)

    def _handle_load_button_clicked(self):
        if self.open_npy_dialog_frame.lineEdit.text() != "":
            self.npy_files["em"] = self.open_npy_dialog_frame.lineEdit.text()
        if self.open_npy_dialog_frame.lineEdit_4.text() != "":
            self.npy_files["power"] = self.open_npy_dialog_frame.lineEdit_4.text()
        if self.open_npy_dialog_frame.lineEdit_3.text() != "":
            self.npy_files["plain"] = self.open_npy_dialog_frame.lineEdit_3.text()
        if self.open_npy_dialog_frame.lineEdit_6.text() != "":
            self.npy_files["cipher"] = self.open_npy_dialog_frame.lineEdit_6.text()
        if self.open_npy_dialog_frame.lineEdit_8.text() != "":
            self.npy_files["aux"] = self.open_npy_dialog_frame.lineEdit_8.text()
        logging.info("Selected files: %s", self.npy_files)
        self.npy_dialog.done(QDialog.DialogCode.Accepted)

    def _handle_cancel_button_clicked(self):
        logging.info("CANCEL Button clicked.")
        self.npy_dialog.done(QDialog.DialogCode.Rejected)

    def get_npy_files(self) -> dict:
        self.npy_dialog.exec()
        return self.npy_files

    def _selectFile(self, type_name: str, path: str = "") -> str:
        if path != "":
            self.last_path = path

        filename = QFileDialog.getOpenFileName(
            None, f"Select {type_name} file", self.last_path, "numpy array (*.npy)"
        )

        if filename[0] != "":
            self.last_path = abspath(filename[0])

        return filename[0]
