import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from align.model import Model
from align.presenter import Presenter
from align.ui.main_window import AliGnMainWindow


def start_gui():
    """Set up and build the main window GUI"""
    args = sys.argv
    print(args)

    # Set logging handler for file and console logging
    # Default logging level
    log_level = "INFO"
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(module)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("AliGn.log"), logging.StreamHandler()],
    )

    app = QApplication(args)

    app.setStyle("fusion")
    app.setPalette(_get_dark_mode_palette(app))

    # Build up the Model View Presenter (MVP) architecural pattern from our classes
    model = Model()
    view = AliGnMainWindow()
    presenter = Presenter(model, view)

    # Method to call before app closes
    app.aboutToQuit.connect(presenter.handle_prepare_shutdown)

    presenter.show(args)
    sys.exit(app.exec())


## Set dark colors palette for a dark mode GUI
def _get_dark_mode_palette(app=None):

    dark_palette = app.palette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Base, QColor(42, 42, 42))
    dark_palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Dark, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)
    dark_palette.setColor(
        QPalette.Disabled,
        QPalette.HighlightedText,
        QColor(127, 127, 127),
    )

    return dark_palette


if __name__ == "__main__":
    start_gui()
