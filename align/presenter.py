"""
AliGn uses the Model View Presenter (MVP) architecural pattern for the user interface
In MVP, the presenter assumes the functionality of the "middle-man". 
All presentation logic is pushed to the presenter.
The presenter acts upon the model and the view. 
It retrieves data from repositories (the model), and formats it for display in the view.
See also align.gui
"""

import datetime
import logging
import os
import random
import numpy as np
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor
from pyqtgraph.parametertree.parameterTypes.file import FileParameter
from pyqtgraph import CurveArrow, PlotDataItem
from pyqtgraph.graphicsItems import GraphicsWidget
from pyqtgraph.parametertree.parameterTypes.basetypes import Parameter
import pyqtgraph
from align.custom_group_parameters import FilterGroupParameter
from align.custom_group_parameters import TriggerGroupParameter
from align.data_importer import NpyImporter
from align.helpers import Helpers
from align.tools.frequency_analyzer import FrequencyAnalyzer
from align.ui.main_window import AliGnMainWindow
from align.model import Model


class Presenter:
    """
    Presenter class acts upon the model and the view. It handles the actions the user selects in the gui
    and formats data for display in the gui.

    Parameters
        ----------
        model : Model
            The Model to use
        view : AliGnMainWindow
            The View to use is always the AliGnMainWindow
    """

    def __init__(self, model: Model, view: AliGnMainWindow):
        self._model = model
        self._view = view
        logging.getLogger(__name__)

    def show(self, *args: str) -> None:
        """Init GUI and restore app settings, then show GUI"""
        self._view.init_gui(self)
        self._view.show()
        self._restore_app_settings()
        if len(args) == 1:
            # TODO set initial (meta)file(s)
            # main_window.params.child("metafile").setValue(args[0])
            pass

    def handle_prepare_shutdown(self) -> None:
        """Do the follings steps when shutting down Align:
        - stopp running batch processing
        - save app settings to file
        """
        logging.info("Shuting down AliGn.")
        self._model.stop_batch_processing_thread()
        self._save_app_settings()

    def handle_action_fullsize_traceplot_view(self) -> None:
        """Toggle fullsize plot view
        In fullsize view the parameter tree and the processing info frame are hidden
        """
        if self._view.tree.isHidden():
            self._view.tree.show()
            self._view.processing_frame.show()
        else:
            self._view.tree.hide()
            self._view.processing_frame.hide()

    def handle_action_open_project(self) -> None:
        """Open a saved project (metafile and filter/trigger settings)
        opens a QFileDialog to select the project file
        load file content and restore state to self._view.tree_parameter
        """
        logging.info("Going to load Project settings")
        project_filename, _filter = QFileDialog.getOpenFileName(
            self._view,
            "Load Project settings from file",
            os.path.join(self._model.app_settings.last_path, "align_settings.json"),
            "JSON file (*.json)",
        )
        if project_filename == "":
            return
        try:
            state = self._model.load_project_settings(project_filename)
            self._view.tree_parameter.child("metafile").setToDefault()
            self._view.tree_parameter.restoreState(state)
        except OSError:
            logging.error("Couldn't read Project from file: %s", project_filename)

    def handle_action_save_project(self) -> None:
        """Save all settings from parameter tree in a project file
        Opens a QFileDialog to select a filename for the project file
        and stores self._view.tree_parameter state therein
        """
        logging.info("Going to save Project settings")
        default_filename = os.path.join(
            self._model.app_settings.last_path, "align_settings.json"
        )
        project_filename, _filter = QFileDialog.getSaveFileName(
            self._view,
            "Save Trace settings to file",
            default_filename,
            "JSON file (*.json)",
        )
        if project_filename == "":
            return
        state = self._view.tree_parameter.saveState()
        try:
            self._model.save_project_settings(state, project_filename)
        except OSError:
            logging.error("Couldn't save settings to file: %s", project_filename)

    def handle_action_show_about_dialog(self) -> None:
        """Open a QMessageBox with the app description"""
        msg_box = QMessageBox(self._view)
        msg_box.setWindowTitle(self._model.APP_NAME)
        msg_box.setText(self._model.APP_DESCRIPTION)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec()

    def handle_metafile_fileparameter_changed(self, fileparameter: FileParameter):
        """Handler to call if metafile parameter in parameter tree was changed
           calls _open_trace_data_and_fill_views() with new filename as parameter

        Parameters
        ----------
        fileparameter : FileParameter
            FileParameter contains new filename
        """
        filename = fileparameter.value()
        if filename is None:
            return
        self._open_trace_data_and_fill_views(filename)

    def handle_data_files_changed(self, parameter: Parameter, changes: list) -> None:
        """Handler to call if data_files (npy files dict) parameter in parameter tree was changed
           calls _open_trace_data_and_fill_views() with new npy files dict as parameter

        Parameters
        ----------
        parameter : Parameter
            the changed Parameter from the parameter tree
        changes : list
            changes in the Parameter
        """
        if self._view.tree_parameter.child("metafile").value() is not None:
            return
        logging.info("Parameter: %s", parameter)
        logging.info("Changes: %s", changes)
        npy_files = dict()
        for changed_parameter, change, data in changes:
            if change == "value":
                npy_files[changed_parameter.name().split("_")[0]] = data
        parameter.blockSignals(True)
        self._open_trace_data_and_fill_views(npy_files)
        parameter.blockSignals(False)

    def handle_action_open_metafile(self) -> None:
        """Handler to call if user click menu "Open meta file"
        open a QFileDialog to select a meta file
        and calls _open_trace_data_and_fill_views() with selected filename as parameter
        """
        filename = QFileDialog.getOpenFileName(
            self._view,
            "Open Meta file",
            self._view.tree_parameter.child("metafile").value(),
            "meta file (*.meta)",
        )[0]
        self._open_trace_data_and_fill_views(filename)

    def handle_action_open_npy_files(self) -> None:
        """Handler to call if user click menu "Open *.npy files"
        open a NpyImporter dialog to select npy files
        and calls _open_trace_data_and_fill_views() with selected npy files dict as parameter
        """
        npy_importer = NpyImporter(last_path=self._model.app_settings.last_path)
        npy_files = npy_importer.get_npy_files()
        if len(npy_files) == 0:
            return
        self._view.tree_parameter.child("data_files").blockSignals(True)
        self._open_trace_data_and_fill_views(npy_files)
        self._view.tree_parameter.child("data_files").blockSignals(False)

    def handle_action_show_frequency_analyzer(self) -> None:
        """Opens a new window with a frequency analyzer tool"""
        freqan = FrequencyAnalyzer()
        sample_freq = self._model.trace_data.get_sample_freq()
        if self._model.trace_data is not None:
            trace_data = self._get_ref_trace_data()
            freqan.plot_data(trace_data, sample_freq)

    def handle_overview_region_changed(self) -> None:
        """Handler to call if the region in the overview plot has changed
        gets the min and max x values from the overview plot
        and updates the EM trace plot region to these values
        """
        self._view.overview_linear_region_item.setZValue(10)
        min_x, max_x = self._view.overview_linear_region_item.getRegion()
        if min_x < 0:
            min_x = 0
            self._view.overview_linear_region_item.setRegion([0, max_x])
        self._view.em_traces_plot_item.setXRange(min_x, max_x, padding=0)

    def handle_em_traces_plotitem_range_changed(
        self, window: GraphicsWidget, view_range: list
    ) -> None:
        """Handler to call if the region in the EM trace plot has changed
        gets the min and max x values from the EM trace plot
        and updates the overview plot region to these values

          Parameters
          ----------
          window : GraphicsWidget
              The View or GraphicWidget where the range changed happend
          view_range : list
              the new view range
        """
        rgn = view_range[0]
        self._view.overview_linear_region_item.setRegion(rgn)

    def handle_em_traces_plotitem_mouse_moved(self, point: QPointF) -> None:
        """Handler to call if mouse was moved in EM trace plot
        prints label with x,y coordinates in plot
        and set horizontal and vertical lines at mouse position in plot

           Parameters
           ----------
           point : QPointF
               x/y coordinates from mouse pointer
        """
        if self._view.em_traces_plot_item.sceneBoundingRect().contains(point):
            mouse_point = self._view.em_traces_plot_item.vb.mapSceneToView(point)
            index = int(mouse_point.x())
            reference_trace_data = self._get_ref_trace_data()
            if reference_trace_data is None:
                return
            if 0 < index < len(reference_trace_data):
                x_value = str(round(mouse_point.x()))
                y_value = str(round(mouse_point.y()))
                self._view.mouse_position_label.setText(
                    f"<span style='font-size: 12pt'>x={x_value}, y={y_value}</span>"
                )
            self._view.vertical_line.setPos(mouse_point.x())
            self._view.horizontal_line.setPos(mouse_point.y())

    def handle_start_stop_batch_button_clicked(self):
        """Handler to call batch processing button was clicked
        Tests if filter and trigger for processing are selected
        and start batch processing thread. Shows warning dialog if no filter/trigger was set.
        Stops batch processing if it's already running.
        Updates Button text depending on batch processing status.
        """
        btn = self._view.processing_frame_ui.btn_start_stop_batch
        logging.info("clicked: %s", btn.text())
        if (
            (
                self._model.batch_filter_group is not None
                or self._model.batch_trigger_group is not None
            )
            and self._view.processing_frame_ui.btn_start_stop_batch.text()
            == "Start Batch"
        ):
            self._view.processing_frame_ui.btn_start_stop_batch.setText("STOP!")
            state = self._view.tree_parameter.saveState()
            self._model.save_project_settings_with_current_date(state)
            number_of_traces = self._view.processing_frame_ui.sb_process_traces.value()
            successfull_started_thread = self._model.start_batch_processing_thread(
                number_of_traces,
                self.handle_batch_progress_info,
                self.handle_batch_finished,
            )
            if not successfull_started_thread:
                self._view.processing_frame_ui.btn_start_stop_batch.setText("Start Batch")
        elif self._view.processing_frame_ui.btn_start_stop_batch.text() == "STOP!":
            self._model.stop_batch_processing_thread()
            self._view.processing_frame_ui.btn_start_stop_batch.setText("Start Batch")
        else:
            self._show_warning_dialog(
                "Warning",
                "Please first select a not empty filter group and/or trigger group which shall be processed.",
            )

    def handle_batch_progress_info(self, progress_dict: dict):
        """Handler for updating batch processing progress bar in gui.
        Also parses tqdm info and displays them in status bar.

          Parameters
          ----------
          progress_dict : dict
              dict containing information about batch processing progress
        """
        percentage = ((progress_dict["n"] + 1) / progress_dict["total"]) * 100
        self._view.processing_frame_ui.progressBar.setValue(int(percentage))
        remaining_seconds = int(
            (progress_dict["total"] - (progress_dict["n"] + 1))
            / (progress_dict["rate"] or 0.001)
        )
        remaining_time_str = str(datetime.timedelta(seconds=remaining_seconds))
        message = f"Processing trace: {progress_dict['n']}/{ progress_dict['total']}, remaing time: {remaining_time_str} at rate: { round(progress_dict['rate'] or 0, 2)} traces/s"
        self._view.statusbar.showMessage(message)

    def handle_batch_finished(self):
        """Handler which is called when batch processing has finished.
        Updates Button text and status bar info
        """
        self._view.processing_frame_ui.progressBar.setValue(0)
        self._view.processing_frame_ui.btn_start_stop_batch.setText("Start Batch")
        self._view.statusbar.showMessage("Batch processing finished.", 5000)
        logging.debug("Batch processing thread finished.")

    def handle_ref_trace_changed(self) -> None:
        """Handler which is called when reference trace was changed
        updates overview plot with reference trace data
        """
        if self._model.trace_data is None:
            return

        ref_trace_nr = self._view.tree_parameter.child("ref_trace").value()
        ref_trace_type = self._view.tree_parameter.child("ref_trace_type").value()

        reference_trace_data = self._model.trace_data.get_trace(
            ref_trace_type, ref_trace_nr
        )
        self._view.overview_plot_item.setYRange(
            int(np.nanmin(reference_trace_data)), int(np.nanmax(reference_trace_data))
        )
        self._view.overview_plot_item.setXRange(0, len(reference_trace_data), padding=0)

        if self._view.overview_plot_data_item is None:
            self._view.overview_plot_data_item = self._view.overview_plot_item.plot(
                reference_trace_data, pen="r"
            )
        else:
            self._view.overview_plot_data_item.setData(reference_trace_data)

        self._view.overview_linear_region_item.setBounds([0, len(reference_trace_data)])

    def handle_trace_option_group_changed(
        self, parameter: Parameter, changes: list
    ) -> None:
        """Handler which is called when any of the trace_option_group in parameter tree was changed
        Main tasks that are processed here are "childAdded", "childRemoved", "value" (value change) and "contextMenu"

          Parameters
          ----------
          parameter : Parameter
              _description_
          changes : list
              contains the changes from sigTreeStateChanged in parameter tree
        """
        if self._model.trace_data is None:
            return
        for changed_parameter, change, data in changes:
            path = self._view.tree_parameter.childPath(changed_parameter)
            if path is not None:
                child_name = ".".join(path)
            logging.info(
                "changed parameter (path): '%s', change: '%s', data: '%s'",
                child_name if path is not None else changed_parameter,
                change,
                data,
            )

            if change == "childAdded":
                # add new trace
                # len(path) == 1 and path[0] == "trace_option_group"
                if changed_parameter.name() == "trace_option_group":
                    trace_options = data[0]
                    trace_type_list = self._model.trace_data.get_trace_types()
                    number_of_trace = self._model.trace_data.get_number_of_traces()
                    if trace_type_list is not None:
                        trace_options.blockSignals(True)
                        trace_options.child("tracetype").setLimits(trace_type_list)
                        trace_options.child("tracenr").setLimits(
                            [0, number_of_trace - 1]
                        )
                        trace_options.blockSignals(False)
                    self._process_trace_options(trace_options)

                # add new filter
                elif changed_parameter.name() == "filter_group":
                    trace_options = changed_parameter.parent()
                    self._process_trace_options(trace_options)

                elif changed_parameter.name() == "trigger_group":
                    trace_options = changed_parameter.parent()
                    self._process_trace_options(trace_options)

            elif change == "childRemoved":
                # remove trace
                if changed_parameter.name() == "trace_option_group":
                    trace_options = data
                    self._remove_plot_data_item(trace_options.name())

                # remove filter
                elif changed_parameter.name() == "filter_group":
                    trace_options = changed_parameter.parent()
                    self._process_trace_options(trace_options)

                elif changed_parameter.name() == "trigger_group":
                    trace_options = changed_parameter.parent()
                    self._process_trace_options(trace_options)

                logging.info("childRemoved: %s", data.name)

            elif change == "value":
                trace_options_group = self._view.tree_parameter.child(path[0])
                trace_options = trace_options_group.child(path[1])

                if changed_parameter.name() == "tracenr":
                    trace_nr = trace_options.child("tracenr").value()
                    trace_options.child("shift").setValue(0)
                    trace_options.setOpts(title=f"Trace {trace_nr} options")
                    self._view.tree_parameter.child("ref_trace").setValue(trace_nr)
                elif changed_parameter.name() == "color":
                    plot_data_item = self._model.plot_data_items[trace_options.name()][
                        1
                    ]
                    plot_data_item.setPen(changed_parameter.value())

                self._process_trace_options(trace_options)

            elif change == "contextMenu":
                logging.info("Context Menu: %s %s", path, data)
                if data == "duplicate_trace":
                    self._duplicate_traceoptions(changed_parameter)
                elif data == "set_batch_filters":
                    self._set_batch_filters(changed_parameter)
                elif data == "set_batch_triggers":
                    self._set_batch_triggers(changed_parameter)

    def handle_parameter_tree_item_moved(
        self, item: Parameter, parent: Parameter, index: int
    ):
        """Planned handler for reordering tree parameter items
        TODO: rearrange items in the childs list (isn't fully support by pyqtgraph as for version 0.13.7)

        Parameters
        ----------
        item : Parameter
            Moved Parameter
        parent : Parameter
            Parent Parameter
        index : int
            new position
        """
        pass

    def _save_app_settings(self):
        self._model.app_settings.log_level = logging.getLevelName(
            logging.getLogger().level
        )
        self._model.app_settings.save()

    def _restore_app_settings(self):
        self._model.restore_app_settings()
        self._set_app_setting_to_view()
        self._set_log_level(self._model.app_settings.log_level)
        self._model.actual_region_around_peak = (
            self._model.app_settings.default_region_around_peak
        )

    def _set_app_setting_to_view(self):
        self._view.tree_parameter.child("metafile").setOpts(
            directory=self._model.app_settings.last_path
        )
        self._view.tree_parameter.child("metafile").setValue(
            self._model.app_settings.last_metafile
        )

    def _set_log_level(self, log_level):
        logger = logging.getLogger()
        logger.setLevel(log_level)
        for handler in logger.handlers:
            handler.setLevel(log_level)

    def _show_warning_dialog(self, title: str, message: str):
        dlg = QMessageBox(self._view)
        dlg.setWindowTitle(title)
        dlg.setText(message)
        dlg.setIcon(QMessageBox.Warning)
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.exec()

    def _remove_plot_data_item(self, trace_options_name: str) -> None:
        if trace_options_name not in self._model.plot_data_items:
            return
        plot_item, plot_data_item = self._model.plot_data_items.pop(trace_options_name)
        plot_item.removeItem(plot_data_item)

    def _open_trace_data_and_fill_views(self, files: str | dict) -> None:
        try:
            self._model.open_trace_data_from(files)
            self._fill_view_with_trace_data()
        except ValueError as error:
            logging.error("Error while loading file: %s", error)
            self._show_warning_dialog("Error!", f"Error while loading file: {error}")

    def _fill_view_with_trace_data(self):
        self._log_trace_data_info()
        self._view.statusbar.showMessage(
            f"Loaded {self._model.trace_data.get_number_of_traces()} traces",
            5000,
        )
        # reset region to default values
        self._model.actual_region_around_peak = (
            self._model.app_settings.default_region_around_peak
        )
        # clear traces
        self._view.tree_parameter.child("trace_option_group").clearChildren()

        # set Infos in ParameterTree
        self._set_comment_parameter()

        # setValue(value, blockSignal=None)
        # Disconnects the sigValueChanged listener, sets the value
        # and then reconnects sigValueChanged listener
        self._view.tree_parameter.child("metafile").setValue(
            self._model.trace_data.meta_file, self.handle_metafile_fileparameter_changed
        )

        self._view.tree_parameter.child("number_of_traces").setValue(
            self._model.trace_data.get_number_of_traces()
        )

        self._view.tree_parameter.child("data_files").set_file_names(
            self._model.trace_data.get_trace_data_files()
        )

        sample_freq = self._model.trace_data.get_sample_freq()
        self._view.tree_parameter.child("sample_freq").setValue(
            Helpers.eng_string(sample_freq, si=True) + "Hz"
        )

        self._view.tree_parameter.child("ref_trace").setLimits(
            [0, (self._model.trace_data.get_number_of_traces() - 1)]
        )

        self._view.tree_parameter.child("ref_trace_type").setLimits(
            self._model.trace_data.get_trace_types()
        )

        # set reference trace plot and force replot by emitting sigValueChanged
        default_ref_trace = self._view.tree_parameter.child("ref_trace").defaultValue()
        self._view.tree_parameter.child("ref_trace").sigValueChanged.emit(
            self, default_ref_trace
        )

        ref_trace_type = self._view.tree_parameter.child("ref_trace_type").value()
        ref_trace_nr = self._view.tree_parameter.child("ref_trace").value()
        ref_trace = self._model.trace_data.get_trace(ref_trace_type, ref_trace_nr)
        if ref_trace is not None:
            ref_trace_length = len(ref_trace)
            self._view.overview_linear_region_item.setRegion([1, int(ref_trace_length)])

        # Plot initial curves
        self._view.tree_parameter.child("trace_option_group").addNew(
            trace_nr=ref_trace_nr,
            trace_type_list=self._model.trace_data.get_trace_types(),
        )

        self._view.processing_frame_ui.sb_process_traces.setMaximum(
            self._model.trace_data.get_number_of_traces()
        )
        self._view.processing_frame_ui.sb_process_traces.setValue(
            self._model.trace_data.get_number_of_traces()
        )

    def _set_comment_parameter(self):
        comment = self._model.trace_data.get_comment()
        if not comment:
            self._view.tree_parameter.child("comment").hide()
        else:
            self._view.tree_parameter.child("comment").show()
            self._view.tree_parameter.child("comment").setValue(comment)

    def _log_trace_data_info(self):
        logging.info(
            "Loaded trace data type '%s'",
            self._model.trace_data.trace_data_file_type,
        )
        logging.info(
            "file contains %s traces", self._model.trace_data.get_number_of_traces()
        )
        logging.info(
            "file hasEM: %s, hasPower: %s",
            self._model.trace_data.has_em(),
            self._model.trace_data.has_power(),
        )

    def _set_batch_filters(self, filter_group: FilterGroupParameter) -> None:
        if (
            self._model.batch_filter_group is None
            or self._model.batch_filter_group != filter_group
        ):
            if self._model.batch_filter_group is not None:
                self._model.batch_filter_group.highlight(False)
            self._model.batch_filter_group = filter_group
            self._model.batch_filter_group.highlight(True)
            self._view.processing_frame_ui.btn_start_stop_batch.setEnabled(True)
        elif self._model.batch_filter_group == filter_group:
            self._model.batch_filter_group.highlight(False)
            self._view.processing_frame_ui.btn_start_stop_batch.setEnabled(False)
            self._model.batch_filter_group = None

    def _set_batch_triggers(self, trigger_group: TriggerGroupParameter) -> None:
        if (
            self._model.batch_trigger_group is None
            or self._model.batch_trigger_group != trigger_group
        ):
            if self._model.batch_trigger_group is not None:
                self._model.batch_trigger_group.highlight(False)
            self._model.batch_trigger_group = trigger_group
            self._model.batch_trigger_group.highlight(True)
            self._view.processing_frame_ui.btn_start_stop_batch.setEnabled(True)
        elif self._model.batch_trigger_group == trigger_group:
            self._model.batch_trigger_group.highlight(False)
            self._view.processing_frame_ui.btn_start_stop_batch.setEnabled(False)
            self._model.batch_trigger_group = None

    def _duplicate_traceoptions(self, trace_options: Parameter) -> None:
        logging.info("child: %s", trace_options.name())
        logging.info("parent: %s", trace_options.parent().name())

        new_traceoptions = trace_options.parent().addNew()
        new_traceoptions.restoreState(trace_options.saveState())
        new_traceoptions["color"] = QColor(*random.choices(range(50, 256), k=3))

    def _process_trace_options(self, trace_options: Parameter) -> None:
        filter_result = self._model.run_filters_and_triggers_on_trace_data_and_shift(
            trace_options["tracenr"],
            trace_options["tracetype"],
            trace_options.child("filter_group"),
            trace_options.child("trigger_group"),
            trace_options["shift"],
        )

        self._plot_trace(trace_options, filter_result["data"])

        self._clear_peak_region()

        if "xmarks" in filter_result and filter_result["xmarks"]:
            self._set_xmarks_and_region_in_trace_plot(
                trace_options, filter_result["xmarks"]
            )

    def _set_xmarks_and_region_in_trace_plot(
        self, trace_options: Parameter, xmarks: list
    ) -> None:
        logging.info("xmarks: %s", xmarks)

        self._add_arrows(trace_options, xmarks)

        if len(xmarks) < 1 or xmarks[0] is None:
            return

        peak_at = xmarks[0]
        self._view.processing_frame_ui.dsb_peak_at.setValue(int(peak_at))

        peak_region_start = 0
        peak_region_end = 0

        if len(xmarks) == 1:
            # add region around arrow
            self._view.peak_linear_region_item.sigRegionChanged.connect(
                lambda: self._update_peak_region(xmarks)
            )
            peak_region_start = peak_at + self._model.actual_region_around_peak[0]
            peak_region_end = peak_at + self._model.actual_region_around_peak[1]

        elif len(xmarks) == 2 and xmarks[1] is not None:
            # add region between arrows
            self._view.peak_linear_region_item.sigRegionChanged.connect(
                lambda: self._update_peak_region(xmarks)
            )
            peak_region_start = xmarks[0] + self._model.actual_region_around_peak[0]
            peak_region_end = xmarks[1] + self._model.actual_region_around_peak[1]

        self._view.peak_linear_region_item.setRegion(
            [peak_region_start, peak_region_end]
        )
        self._view.em_traces_plot_item.addItem(
            self._view.peak_linear_region_item, ignoreBounds=True
        )

    def _add_arrows(self, trace_options: Parameter, x_positions: list[int]) -> None:
        for x_position in x_positions:
            if x_position is None:
                continue
            CurveArrow(
                self._model.plot_data_items[trace_options.name()][1],
                index=x_position,
                brush=pyqtgraph.mkBrush(255, 20, 20),
            ).setStyle(angle=90)

    def _clear_peak_region(self):
        self._view.em_traces_plot_item.removeItem(self._view.peak_linear_region_item)

    def _plot_trace(self, trace_options: Parameter, trace_data) -> None:
        trace_type = trace_options["tracetype"]
        trace_color = trace_options["color"]
        logging.debug("plot_trace (%s, %s, %s)", trace_type, trace_data, trace_color)

        if trace_options.name() in self._model.plot_data_items:
            plot_item, plot_data_item = self._model.plot_data_items[
                trace_options.name()
            ]
            plot_item.removeItem(plot_data_item)

        if trace_type == "power":
            plot_item = self._view.power_traces_view_box
            plot_item.setGeometry(self._view.em_traces_plot_item.vb.sceneBoundingRect())
            plot_item.linkedViewChanged(
                self._view.em_traces_plot_item.vb,
                plot_item.XAxis,
            )
        else:
            plot_item = self._view.em_traces_plot_item

        plot_item.setYRange(int(np.nanmin(trace_data)), int(np.nanmax(trace_data)))

        plot_data_item = PlotDataItem(
            trace_data,
            pen=pyqtgraph.mkPen(
                trace_color, width=self._model.app_settings.trace_plot_width
            ),
        )
        plot_item.addItem(plot_data_item)
        self._model.plot_data_items[trace_options.name()] = (plot_item, plot_data_item)

    def _update_peak_region(self, peaks: list[int]) -> None:
        if 1 < len(peaks) < 2:
            return
        min_x, max_x = self._view.peak_linear_region_item.getRegion()
        self._model.actual_region_around_peak = [
            int(min_x - peaks[0]),
            int(max_x - (peaks[1] if len(peaks) == 2 else peaks[0])),
        ]
        self._view.processing_frame_ui.dsb_cut_area_start.blockSignals(True)
        self._view.processing_frame_ui.dsb_cut_area_end.blockSignals(True)

        self._view.processing_frame_ui.dsb_cut_area_start.setValue(int(min_x))
        self._view.processing_frame_ui.dsb_cut_area_end.setValue(int(max_x))

        self._view.processing_frame_ui.dsb_cut_area_start.blockSignals(False)
        self._view.processing_frame_ui.dsb_cut_area_end.blockSignals(False)

    def _get_ref_trace_data(self) -> np.ndarray:
        if self._model.trace_data is None:
            return
        ref_trace_nr = self._view.tree_parameter.child("ref_trace").value()
        ref_trace_type = self._view.tree_parameter.child("ref_trace_type").value()
        reference_trace_data = self._model.trace_data.get_trace(
            ref_trace_type, ref_trace_nr
        )
        return reference_trace_data
