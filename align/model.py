"""
AliGn uses the Model View Presenter (MVP) architecural pattern for the user interface
In MVP, the presenter assumes the functionality of the "middle-man". 
All presentation logic is pushed to the presenter.
The model is an interface defining the data to be displayed.
See also align.gui
"""

import datetime
import json
import os
import logging
from typing import Any, Callable
from align.align_settings import AlignSettings
from align.align_trace_data import AlignTraceDataFactory
from align.batch_processing import BatchProcessingThread
from align.filter.filter import FilterLoader
from align.trigger.trigger import TriggerLoader
from align.helpers import Helpers


class Model:
    """
    The model is an interface defining the data to be displayed.
    It contains methods to provide and store the data.
    """

    APP_NAME = "AliGn v0.4.0"
    APP_URL = "https://github.com/BSI-Bund/AliGn"
    APP_DESCRIPTION = f"<h3>{APP_NAME}</h3><br/>Visual tool to explore, align and process measurement data.<br/>Info and sources at <a href='{APP_URL}'>{APP_URL}</a>"

    def __init__(self) -> None:
        logging.getLogger(__name__)
        self.app_settings = AlignSettings()
        self.filter = FilterLoader()
        self.trigger = TriggerLoader()
        self.trace_data = None
        self.batch_filter_group = None
        self.batch_trigger_group = None
        self._batch_processing_thread = None
        self.actual_region_around_peak = None

        # dict to map key string (traceoption name) to a tuple of plot_item and plot_data_item
        self.plot_data_items = {}

    def restore_app_settings(self) -> None:
        """Loads last app settings from config file defined in AlignSettings"""
        self.app_settings.restore()

    def load_project_settings(self, project_filename: str) -> dict:
        """Opens given project filename (json file), parses it to a dict,
           modifies the metafile path inside the dict to an absolute path and returns the dict

        Parameters
        ----------
        project_filename : str
            path and file name of project file

        Returns
        -------
        dict
            project settings from given json file in a dict
        """
        if project_filename == "":
            return
        with open(project_filename, mode="r", encoding="utf-8") as file:
            state = json.loads(file.read())
        metafile_path = state["children"]["metafile"]["value"]
        if (metafile_path is not None) and (not os.path.isabs(metafile_path)):
            settings_path = os.path.dirname(project_filename)
            absolute_metafile_path = os.path.normpath(
                os.path.join(settings_path, metafile_path)
            )
            state["children"]["metafile"]["value"] = absolute_metafile_path
        return state

    def save_project_settings(
        self, state: dict, settings_filename: str, use_relative_path: bool = False
    ) -> None:
        """Writes the given state dict to the given project filename (json file).
           if use_relative_path is True the metafile path inside the dict will be
           changed from absolute path to relative path
           before dict is parsed to json and saved to settings file

        Parameters
        ----------
        state : dict
            contains the state of the ParameterTree which contains all filter/trigger settings
        settings_filename : str
            path and filename to store the settings into
        use_relative_path : bool, optional
            if True the metafile path inside the dict will be changed from absolute path
            to relative path, by default False

        Returns
        -------
        None
           This method does not return anything.
        """
        state_metafile_value = state["children"]["metafile"]["value"]

        if use_relative_path and (state_metafile_value is not None):
            metafile_path = os.path.dirname(state_metafile_value)
            metafile_name = os.path.basename(state_metafile_value)
            settings_path = os.path.dirname(settings_filename)
            relative_path = os.path.relpath(metafile_path, settings_path)
            state["children"]["metafile"]["value"] = os.path.join(
                relative_path, metafile_name
            )

        with open(settings_filename, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(state))

    def save_project_settings_with_current_date(self, state: dict) -> None:
        """Writes the given state dict to current path to a file with current date.
           Format filename is Y-m-d-H.M_align_settings.json.
           Uses save_project_settings with use_relative_path is set to True

        Parameters
        ----------
        state : dict
            contains the state of the ParameterTree which contains all filter/trigger settings

        Returns
        -------
        None
           This method does not return anything.
        """
        date_string = datetime.datetime.today().strftime("%Y-%m-%d-%H.%M")
        settings_filename = os.path.join(
            self.app_settings.last_path, date_string + "_align_settings.json"
        )
        self.save_project_settings(state, settings_filename, True)

    def open_trace_data_from(self, files: str | dict) -> None:
        """Opens data from D15 meta file or from dict containing npy data files

        Parameters
        ----------
        files : str, dict
           If files is 'str' it should contain a single D15 meta file,
           if it's 'dict' the dict should contain the npy-files.

        Returns
        -------
        None
           This method does not return anything.
        """
        self.batch_filter_group = None
        self.batch_trigger_group = None
        if files is None:
            return
        self.trace_data = AlignTraceDataFactory.open_trace_data(files)
        self.app_settings.last_path = self.trace_data.path
        self.app_settings.last_metafile = self.trace_data.meta_file

    def start_batch_processing_thread(
        self, number_of_traces: int, on_progress: Callable, on_finished: Callable
    ) -> bool:
        """Starts batch prossing in a separat thread
           All current selected filters and triggers will be performed on the current open
           trace data. A new sub folder with the prcessed data will be created in the
           origin data folder

        Parameters
        ----------
        number_of_traces : int
            number_of_traces to process in batch processing thread
        on_progress : Callable
            method which shall receive progress signals from batch processing thread
        on_finished : Callable
            method to call when batch processing thread is finished

        Returns
        -------
        bool
           Returns True if batch process successfull started, else if batch process could be started return False.
        """

        filter_dict = None
        trigger_dict = None
        trace_type = ""
        if self.batch_filter_group is not None:
            filter_dict = self.batch_filter_group.getValues()
            trace_type = self.batch_filter_group.parent().child("tracetype").value()
        if self.batch_trigger_group is not None:
            trigger_dict = self.batch_trigger_group.getValues()
            trace_type = self.batch_trigger_group.parent().child("tracetype").value()

        if (filter_dict is None or len(filter_dict) == 0) and (
            trigger_dict is None or len(trigger_dict) == 0
        ):
            return False

        self._batch_processing_thread = BatchProcessingThread(
            None,
            self.trace_data,
            filter_dict,
            trigger_dict,
            self.actual_region_around_peak,
            trace_type,
            number_of_traces,
        )
        self._batch_processing_thread.progress_signal.connect(on_progress)
        self._batch_processing_thread.finished.connect(on_finished)
        self._batch_processing_thread.start()
        return self._batch_processing_thread.isRunning

    def stop_batch_processing_thread(self, grace_period_ms: int = 2000) -> None:
        """Stops running batch processing thread. If thread didn't stop after a
           grace period, the process will be terminated

        Parameters
        ----------
        grace_period_ms : int, optional
            Leave process this time to cleanly shut down, before it will be terminated,
            by default 2000

        Returns
        -------
        None
           This method does not return anything.
        """
        if (
            self._batch_processing_thread is None
            or not self._batch_processing_thread.isRunning()
        ):
            return
        logging.info("Sending stop signal to running batch processing thread")
        # send stop signal to running thread (it tries a clean shutdown)
        self._batch_processing_thread.stop()
        # wait {grace_period_ms} to finish
        if not self._batch_processing_thread.wait(grace_period_ms):
            logging.info(
                "batch processing thread didn't react to stop signal within %s milli seconds.\
                  Going to terminate this thread!",
                grace_period_ms,
            )
            self._batch_processing_thread.terminate()
        else:
            logging.info("Batch processing thread was stopped cleanly.")
        self._batch_processing_thread = None

    def run_filters_and_triggers_on_trace_data_and_shift(
        self,
        tracenr: int,
        tracetype: str,
        filter_group: dict,
        trigger_group: dict,
        shift: int = 0,
    ) -> dict[str, Any]:
        """Process the given filter and trigger on a given single trace of the current
           open trace data file and return a dict with keywords "data" containing
           modified trace and "xmarks" containing found trigger point(s) within this modified trace

        Parameters
        ----------
        tracenr : int
           Trace number in trace data file to apply the filter(s) and trigger(s) on
        tracetype : str
            Type of trace eg. "em", "power", etc.
        filter_group : dict
            filter group from parameter tree which contains all
            selected filters and their parameters
        trigger_group : dict
           trigger group from parameter tree which contains all
           selected triggers and their parameters
        shift : int, optional
            optional shift trace by this values before process filter and triggers, by default 0

        Returns
        -------
        dict[str, Any]
            a dict with keywords "data" containing modified trace and "xmarks"
            containing found trigger point(s) within this modified trace
        """
        trace_data = self.trace_data.get_trace(tracetype, tracenr)
        # always do shifting (even for zero)
        trace_data = Helpers.shift4(trace_data, shift)

        # process filters
        filter_trigger_result = {"data": trace_data, "xmarks": None}
        logging.debug("CHILDREN: %s", filter_group.children())
        for child in filter_group.children():
            logging.debug("CHILD: NAME: %s, VALUES: %s", child.name(), dict(child))
            filter_instance = self.filter.get_filter_by_name(child.name())
            filter_trigger_result["data"] = filter_instance.process_data(
                filter_trigger_result["data"], child.getValues()
            )["data"]

        # process triggers
        current_offset = 0
        for child in trigger_group.children():
            logging.debug("CHILD: NAME: %s, VALUES: %s", child.name(), dict(child))
            trigger_instance = self.trigger.get_trigger_by_name(child.name())
            # each trigger should start on the trace w.r.t. to the previous identified trigger point
            # if no trigger is identified, we abort
            filter_trigger_result["xmarks"] = trigger_instance.process_data(
                filter_trigger_result["data"], current_offset, child.getValues()
            )["xmarks"]

            if (filter_trigger_result["xmarks"] is None) or not filter_trigger_result[
                "xmarks"
            ]:
                break

            # calculate new offset, so that we get a cascading trigger for the
            # next tigger in the list
            # convention: zero-th element of xmarks contains trigger value
            current_offset = filter_trigger_result["xmarks"][0]
            logging.debug(
                f"filter_trigger_result xmarks: {filter_trigger_result['xmarks']}"
            )

        return filter_trigger_result
