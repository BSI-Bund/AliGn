import logging
import platform
import ctypes
from typing import Protocol
import pyqtgraph as pg
import pyqtgraph.parametertree as ptree

# Needed for icons resoruces
from align.resources import resources

from PySide6.QtWidgets import QMainWindow, QStatusBar, QFrame, QSplitter

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QIcon, QAction

from align.custom_group_parameters import DataFilesGroupParameter, TraceGroupParameter


from align.filter.filter import FilterLoader
from align.trigger.trigger import TriggerLoader
from align.ui.ui_ProcessSettingsFrame import Ui_ProcessSettingsFrame


## initial ParameterTree children
main_parameter_tree = [
    # dict(name="trace_data_file_type", title="Trace Data File Type", type="list", readonly=True, limits=[*TraceDataFileType.list()]),
    dict(name="metafile", title="meta file", type="file", nameFilter="*.meta"),
    DataFilesGroupParameter(
        name="data_files", title="Data files", type="group", expanded=False
    ),
    dict(name="number_of_traces", title="Traces", type="int", readonly=True),
    dict(name="sample_freq", title="Sample Frequency", type="str", readonly=True),
    dict(name="comment", title="Comment", type="text", readonly=True),
    dict(name="ref_trace", title="Reference Trace", type="int", default=1),
    dict(name="ref_trace_type", title="Trace Type", type="list", limits=[]),
    TraceGroupParameter(
        name="trace_option_group",
        title="Traces",
        type="group",
        tip="Click to add traces",
    ),
]


class Presenter(Protocol):
    """All callbacks method are implemented in class align.presenter.Presenter"""

    def handle_action_open_npy_files(self) -> None: ...

    def handle_action_open_project(self) -> None: ...

    def handle_action_save_project(self) -> None: ...

    def handle_action_fullsize_traceplot_view(self) -> None: ...

    def handle_action_show_frequency_analyzer(self) -> None: ...

    def handle_action_show_about_dialog(self) -> None: ...

    def handle_metafile_fileparameter_changed(self, file_parameter) -> None: ...

    def handle_data_files_changed(self, parameter, changes) -> None: ...

    def handle_action_open_metafile(self) -> None: ...

    def handle_ref_trace_changed(self) -> None: ...

    def handle_trace_option_group_changed(self, param, changes) -> None: ...

    def handle_parameter_tree_item_moved(self, item, parent, index) -> None: ...

    def handle_start_stop_batch_button_clicked(self) -> None: ...

    def handle_em_traces_plotitem_range_changed(self, window, view_range) -> None: ...

    def handle_em_traces_plotitem_mouse_moved(self, point: QPointF) -> None: ...

    def handle_overview_region_changed(self) -> None: ...


class AliGnMainWindow(QMainWindow):
    """Build the main AliGn windows"""

    def __init__(self):
        super(AliGnMainWindow, self).__init__()

        self._filters = FilterLoader()
        self._triggers = TriggerLoader()

        # initialize some globals
        self.plot_widget = None
        self.mouse_position_label = None
        self.tree_parameter = None
        self.tree = None
        self.processing_frame = None
        self.processing_frame_ui = None
        self.em_traces_plot_item = None
        self.power_traces_view_box = None
        self.overview_plot_item = None
        self.overview_plot_data_item = None
        self.overview_linear_region_item = None
        self.vertical_line = None
        self.horizontal_line = None
        self.statusbar = None

        self.peak_linear_region_item = pg.LinearRegionItem(
            brush=pg.mkBrush(255, 20, 20, 80)
        )
        self.peak_linear_region_item.setZValue(20)

    def init_gui(self, presenter: Presenter):
        self.setWindowTitle("AliGn")
        # self.setStyle(QStyleFactory.create("Fusion"))

        self.setGeometry(100, 100, 1600, 800)

        # set window icon
        self.setWindowIcon(QIcon(":/icons/align_icon.png"))

        # tell windows to use window icon for taskbar instead of python icon
        if platform.system() == "Windows":
            myappid = "de.bund.bsi.align"  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # create Plot Widget
        self.plot_widget = pg.GraphicsLayoutWidget(show=True)
        self.mouse_position_label = pg.LabelItem(justify="right")
        self.plot_widget.addItem(self.mouse_position_label)

        # create ParameterTree Widget
        self.tree_parameter = ptree.Parameter.create(
            name="Parameters", type="group", children=main_parameter_tree
        )
        self.tree = ptree.ParameterTree(showHeader=False)
        self.tree.setParameters(self.tree_parameter)

        self.tree_parameter.child("metafile").sigValueChanged.connect(
            presenter.handle_metafile_fileparameter_changed
        )
        self.tree_parameter.child("data_files").sigTreeStateChanged.connect(
            presenter.handle_data_files_changed
        )
        self.tree_parameter.child("ref_trace").sigValueChanged.connect(
            presenter.handle_ref_trace_changed
        )
        self.tree_parameter.child("ref_trace_type").sigValueChanged.connect(
            presenter.handle_ref_trace_changed
        )
        self.tree_parameter.child("trace_option_group").sigTreeStateChanged.connect(
            presenter.handle_trace_option_group_changed
        )

        self.tree.sigItemMoved.connect(presenter.handle_parameter_tree_item_moved)

        # Create Frame for Batch Processing
        ###################################
        # Use Qt Designer generated UI PYthon file

        # First create a "hosting" Frame
        self.processing_frame = QFrame()
        # Second create Instance of ui class
        self.processing_frame_ui = Ui_ProcessSettingsFrame()
        # Finally call setupUi and provide hosting frame
        self.processing_frame_ui.setupUi(self.processing_frame)
        self.processing_frame_ui.btn_start_stop_batch.clicked.connect(
            presenter.handle_start_stop_batch_button_clicked
        )
        self.processing_frame_ui.dsb_cut_area_start.valueChanged.connect(
            lambda: self.peak_linear_region_item.setRegion(
                [
                    self.processing_frame_ui.dsb_cut_area_start.value(),
                    self.processing_frame_ui.dsb_cut_area_end.value(),
                ]
            )
        )
        self.processing_frame_ui.dsb_cut_area_end.valueChanged.connect(
            lambda: self.peak_linear_region_item.setRegion(
                [
                    self.processing_frame_ui.dsb_cut_area_start.value(),
                    self.processing_frame_ui.dsb_cut_area_end.value(),
                ]
            )
        )

        # Create Splitter
        splitter1 = QSplitter(Qt.Orientation.Horizontal)

        # add Widgets to Splitter
        splitter1.addWidget(self.tree)  # ParameterTree widget
        splitter1.addWidget(self.plot_widget)  # Ploting widget
        splitter1.setSizes([50, 200])

        splitter2 = QSplitter(Qt.Orientation.Vertical)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(self.processing_frame)  # Processing Widget)
        # splitter2.setSizes([1000,200])

        # add Splitter to layout (CentralWidget)
        self.setCentralWidget(splitter2)

        # create upper Plot for EM traces
        self.em_traces_plot_item = self.plot_widget.addPlot(
            row=1, col=0, title="Traces", name="em_traces_viewBox"
        )
        # customize the averaged curve that can be activated from the context menu:
        self.em_traces_plot_item.setMouseEnabled(y=False)  # Only allow zoom in x-axis
        self.em_traces_plot_item.setAutoVisible(y=True)
        self.em_traces_plot_item.showAxis("right")
        self.em_traces_plot_item.setLabels(left="EM")

        # create second ViewBox for Power traces
        self.power_traces_view_box = pg.ViewBox()
        self.em_traces_plot_item.scene().addItem(self.power_traces_view_box)
        self.power_traces_view_box.setXLink(self.em_traces_plot_item)
        self.em_traces_plot_item.getAxis("right").linkToView(self.power_traces_view_box)
        self.em_traces_plot_item.getAxis("right").setLabel("Power")

        self.em_traces_plot_item.sigRangeChanged.connect(
            presenter.handle_em_traces_plotitem_range_changed
        )
        self.em_traces_plot_item.scene().sigMouseMoved.connect(
            presenter.handle_em_traces_plotitem_mouse_moved
        )

        # create lower Plot
        self.overview_plot_item = self.plot_widget.addPlot(
            row=2, col=0, title="Overview"
        )
        self.overview_plot_item.setMouseEnabled(x=False, y=False)  # no zoom
        self.overview_plot_item.showAxis("right")
        self.overview_plot_item.getAxis("right").setLabel("Power")
        self.overview_plot_item.setLabels(left="EM")

        # set ratio in the plot widget
        grid_layout = self.plot_widget.ci.layout
        grid_layout.setRowStretchFactor(1, 2)  # row 1, stretch factor 2
        grid_layout.setRowStretchFactor(2, 1)  # row 2, stretch factor 1

        self.overview_linear_region_item = pg.LinearRegionItem()
        self.overview_linear_region_item.setZValue(10)
        self.overview_linear_region_item.sigRegionChanged.connect(
            presenter.handle_overview_region_changed
        )
        self.overview_linear_region_item.setRegion([1, 10000])
        # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this
        # item when doing auto-range calculations.
        self.overview_plot_item.addItem(
            self.overview_linear_region_item, ignoreBounds=True
        )

        # cross hair
        self.vertical_line = pg.InfiniteLine(angle=90, movable=False)
        self.horizontal_line = pg.InfiniteLine(angle=0, movable=False)
        self.vertical_line.setZValue(30)
        self.horizontal_line.setZValue(30)
        self.em_traces_plot_item.addItem(self.vertical_line, ignoreBounds=True)
        self.em_traces_plot_item.addItem(self.horizontal_line, ignoreBounds=True)

        self._createMenuBar(presenter)
        self._createStatusBar()

    def _createMenuBar(self, presenter: Presenter) -> None:
        # get the menubar
        menubar = self.menuBar()

        # define File/Trace open action
        open_metafile_action = QAction("&Open meta file", self)
        open_metafile_action.setShortcut("Ctrl+O")
        open_metafile_action.triggered.connect(presenter.handle_action_open_metafile)

        # define Npy open action
        open_numpy_arrays_action = QAction("&Open *.npy files", self)
        open_numpy_arrays_action.triggered.connect(
            presenter.handle_action_open_npy_files
        )

        # define File/Load Settings action
        open_project_action = QAction("&Open Project", self)
        open_project_action.triggered.connect(presenter.handle_action_open_project)

        # define File/Save Settings action
        save_project_action = QAction("&Save Project", self)
        save_project_action.setShortcut("Ctrl+S")
        save_project_action.triggered.connect(presenter.handle_action_save_project)

        # define File/Quit action
        quit_action = QAction(QIcon(":/icons/ausgang.png"), "Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)

        file_menu = menubar.addMenu("File")
        file_menu.addAction(open_metafile_action)
        file_menu.addAction(open_numpy_arrays_action)
        file_menu.addSeparator()
        file_menu.addAction(open_project_action)
        file_menu.addAction(save_project_action)
        file_menu.addSeparator()
        file_menu.addAction(quit_action)

        # define View action/menu
        fullsize_trace_plot_action = QAction("Trace view fullsize", self)
        fullsize_trace_plot_action.setCheckable(True)
        fullsize_trace_plot_action.setChecked(False)
        fullsize_trace_plot_action.setShortcut("Tab")
        fullsize_trace_plot_action.triggered.connect(
            presenter.handle_action_fullsize_traceplot_view
        )

        view_menu = menubar.addMenu("View")
        view_menu.addAction(fullsize_trace_plot_action)

        # define Tools action/menu
        show_frequency_analyzer_action = QAction(
            QIcon(":/icons/signal-alt-2.png"), "Frequency Analyzer", self
        )
        show_frequency_analyzer_action.setShortcut("Ctrl+Alt+F")
        show_frequency_analyzer_action.triggered.connect(
            presenter.handle_action_show_frequency_analyzer
        )

        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction(show_frequency_analyzer_action)

        # define About action/menu

        show_about_action = QAction(QIcon(":/icons/die-info.png"), "About", self)
        show_about_action.triggered.connect(presenter.handle_action_show_about_dialog)

        info_menu = menubar.addMenu("Info")
        info_menu.addAction(show_about_action)

    def _createStatusBar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("AliGn is ready to go", 5000)
        # self.wcLabel = QLabel(f"{self.getWordCount()} Words")
        # self.statusbar.addPermanentWidget(self.wcLabel)
