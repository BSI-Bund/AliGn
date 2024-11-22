import datetime
import logging
from collections import OrderedDict
from os import devnull, path
from typing import Optional

import numpy as np
from PySide6.QtCore import QThread, QObject, Signal as pyqtSignal
from tqdm import tqdm

from align.align_trace_data import AlignTraceData, TraceDataFileType
from align.filter.filter import FilterLoader
from align.trigger.trigger import TriggerLoader


class BatchProcessingThread(QThread):
    """Class that processes all selected filter and trigger on the original TraceData
    in a Thread so that the GUI is still available and shows status information on
    the processing. After all filter/triggers are processed new TraceData file(s)
    will be stored in an sub folder of the original TraceData
    """

    # define a signal for progress updates
    progress_signal = pyqtSignal(dict)

    def __init__(
        self,
        parent: Optional[QObject],
        align_trace_data: AlignTraceData,
        filter_dict: OrderedDict,
        trigger_dict: OrderedDict,
        region_around_peak: list,
        trace_type: str,
        trace_count: int = None,
    ):
        """Init a new BatchProcessingThread

        Parameters
        ----------
        parent : Optional[QObject]
            optional parent PySide6.QtCore.QObject for this new QThread
        align_trace_data : AlignTraceData
            AlignTraceData instance to work with
        filter_dict : OrderedDict
            The return from getValues() from filter GroupParameterItem in the parameter tree
            that contains all filter items
        trigger_dict : OrderedDict
            The return from getValues() from trigger GroupParameterItem in the parameter tree
            that contains all trigger items
        region_around_peak : list
            List with two values which defines the region around a peak (before and after)
            which shall be cutted out. e.g. [-500,500] will define the region 500 points
            before the peak and 500 point after the peak which will be cutted out and stored
        trace_type : str
            Trace type to work on e.g. 'em', 'power', etc.
        trace_count : int, optional
            If not defined all traces will be processed. Otherwise the first 'trace_count'
            traces will be processed
        """
        super(BatchProcessingThread, self).__init__(parent)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Import filter
        self._filters = FilterLoader()
        self._triggers = TriggerLoader()

        self.tracetype = trace_type

        self._is_running = True

        self.trace_data = align_trace_data
        self.filter_dict = filter_dict
        self.trigger_dict = trigger_dict
        self.region_around_peak = region_around_peak
        if trace_count is None:
            self.trace_count = align_trace_data.get_number_of_traces()
        else:
            self.trace_count = trace_count

        self.peak_array = np.zeros((self.trace_count, 2), dtype=int)
        self.valid_traces_array = np.zeros(self.trace_count, dtype=bool)

        now_date_string = datetime.datetime.today().strftime("%Y-%m-%d-%H.%M")
        self.new_filepath = path.join(align_trace_data.path, now_date_string, "")
        self.new_trace_data = self.trace_data.prepare_new_tracedata(self.new_filepath)

    def run(self):
        t = tqdm(range(self.trace_count), file=open(devnull, "w"))

        if not self._is_running:
            self._is_running = True

        # filter loop for finding cutout region
        for tracenr in t:
            if self._is_running:
                self.run_filters_and_triggers(tracenr)
                self.progress_signal.emit(t.format_dict)

        self.logger.info("Valid traces: {}".format(np.sum(self.valid_traces_array)))

        # Finished filter processing
        # going to cut traces based on filter results (cutout region)

        if self._is_running:
            # calculate the new maximum trace length. Some filter will return two peaks which distance varies between different traces.
            # But traces must all have the same trace length. Therefore we search for the max distance and use this for all traces
            new_trace_length = int(
                np.diff(self.peak_array)[0].max() + np.diff(self.region_around_peak)[0]
            )
            self.logger.debug("new_trace_length: {}".format(new_trace_length))
            number_of_valid_traces = int(np.sum(self.valid_traces_array))
            self.new_trace_data.set_number_of_traces(number_of_valid_traces)

            # register new power/em files
            if self.trace_data.has_power():
                power_dtype = self.trace_data.get_traces("power").dtype
                filename = "power_aligned." + (
                    "dat"
                    if self.trace_data.trace_data_file_type
                    == TraceDataFileType.D15_TRACE_DATA
                    else "npy"
                )
                self.new_trace_data.register_data_file(
                    "power",
                    self.new_filepath + filename,
                    length=new_trace_length,
                    dtype=power_dtype,
                )
            if self.trace_data.has_em():
                em_dtype = self.trace_data.get_traces("em").dtype
                filename = "em_aligned." + (
                    "dat"
                    if self.trace_data.trace_data_file_type
                    == TraceDataFileType.D15_TRACE_DATA
                    else "npy"
                )
                self.new_trace_data.register_data_file(
                    "em",
                    self.new_filepath + filename,
                    length=new_trace_length,
                    dtype=em_dtype,
                )

            # reset tqdm for cutting loop
            t = tqdm(range(self.trace_count), file=open(devnull, "w"))

            # cut loop
            new_trace_count = 0
            for tracenr in t:
                if self._is_running is True:
                    new_trace_count += self.cut_and_modify_traces(
                        tracenr, new_trace_length
                    )
                    self.progress_signal.emit(t.format_dict)

            if new_trace_count != number_of_valid_traces:
                self.logger.warning("Trace count missmatch!")

            self._finalize_new_traces()

    def stop(self):
        self._is_running = False

    def run_filters_and_triggers(self, tracenr: int):
        """Run filter to search for peaks and fill the self.valid_traces_array which will be used for cutting.
        Modifying filter will not processed in this run but will be run after the cutting was performed.
        """
        self.logger.debug(
            f"Run filters and triggers on trace nr.: {tracenr}, trace type: {str(self.tracetype)}"
        )
        modify_data = None
        xmarks = None
        temp_trace_data = self.trace_data.get_trace(self.tracetype, tracenr)

        # first run all filters
        if self.filter_dict:
            modify_data, temp_trace_data = self._run_filters(temp_trace_data)

        # next run all triggers
        current_offset = 0
        if self.trigger_dict:
            xmarks = self._run_triggers(temp_trace_data, current_offset)

        if xmarks is not None:
            if len(xmarks) == 1 and xmarks[0] is not None:
                peak_at = xmarks[0]
                # check whether the region exceeds the length of the trace
                if ((peak_at + self.region_around_peak[1]) > temp_trace_data.size) or (
                    (peak_at + self.region_around_peak[0]) < 0
                ):
                    self.valid_traces_array[tracenr] = False
                else:
                    self.valid_traces_array[tracenr] = True
                    self.peak_array[tracenr] = peak_at
            elif len(xmarks) == 2 and xmarks[0] is not None and xmarks[1] is not None:
                # check whether the region exceeds the length of the trace
                if (
                    (xmarks[1] + self.region_around_peak[1]) > temp_trace_data.size
                ) or ((xmarks[0] + self.region_around_peak[0]) < 0):
                    self.valid_traces_array[tracenr] = False
                else:
                    self.valid_traces_array[tracenr] = True
                    self.peak_array[tracenr] = xmarks
            else:
                # no peaks were found
                self.valid_traces_array[tracenr] = False

        elif modify_data:
            # There are no xmarks, so set marks to whole trace length.
            self.valid_traces_array[tracenr] = True
            self.peak_array[tracenr] = 0
            self.region_around_peak[0] = 0
            self.region_around_peak[1] = len(temp_trace_data)

        else:
            # neither xmark nor modifying filter
            self.valid_traces_array[tracenr] = False

    def _run_triggers(self, temp_trace_data, current_offset):
        xmarks = None
        for trigger_name, trigger_parameter in self.trigger_dict.items():
            # get data trigger
            trigger = self._triggers.get_trigger_by_name(trigger_name)

            try:
                trigger_result = trigger.process_data(
                    temp_trace_data, current_offset, dict(trigger_parameter[1])
                )
                # be sure the trigger_result contains 'xmarks' key
                xmarks = trigger_result["xmarks"]
            except KeyError as err:
                self.logger.error("Skipping trigger result: %s", err)
                break  # If one of the Triggers fail, skip the remaining Triggers.

            # Calculate new offset, so that we get a cascading Trigger for the
            # next Trigger in the list
            if trigger_result["xmarks"] == []:
                break  # If one of the Triggers return empty xmarks, skip the remaining Triggers.

            # Convention: Index 0 of xmarks contains the Trigger value.
            current_offset = trigger_result["xmarks"][0]
        return xmarks

    def _run_filters(self, temp_trace_data):
        modify_data = None
        for filter_name, filter_parameter in self.filter_dict.items():
            # get data filter
            data_filter = self._filters.get_filter_by_name(filter_name)

            # Check for "modify_data" key in filter parameter.
            # If modifying filter sets 'modify_data' to true, the preprocessing for xmarks search will be skipped.
            filter_settings = filter_parameter[1]

            if "modify_data" in filter_settings:
                self.logger.debug("filter '%s' has set modify_data flag.", filter_name)
                modify_data = bool(filter_parameter[1]["modify_data"][0])
                if modify_data:
                    # skip filter
                    filter_result = dict(data=temp_trace_data, xmarks=None)

                else:
                    filter_result = data_filter.process_data(
                        temp_trace_data, dict(filter_parameter[1])
                    )

            else:
                # process data filter
                filter_result = data_filter.process_data(
                    temp_trace_data, dict(filter_parameter[1])
                )

            # be sure the filter_result contains 'data' key
            try:
                temp_trace_data = filter_result["data"]
            except KeyError as err:
                self.logger.error(
                    "Skipping filter result! Filter result must contain dict with keyword 'data'. See Filter documentation. %s",
                    err,
                )
                continue
        return modify_data, temp_trace_data

    def cut_and_modify_traces(self, tracenr: int, trace_length: int) -> int:
        """cut out region around peak at a single trace and run modifying filters on cutted trace

        Parameters
        ----------
        tracenr : int
            trace number to process
        trace_length : int
            The new length which the cutted trace shall have.

        Returns
        -------
        int
            Returns 1 for a processed trace. If trace wasn't processed 1 is returned
        """
        if not self.valid_traces_array[tracenr]:
            return 0
        start = int(self.peak_array[tracenr, 0] + self.region_around_peak[0])
        end = int(start + trace_length)

        # Only cut/modify em and power traces
        trace_types = []
        if self.trace_data.has_power():
            trace_types.append("power")
        if self.trace_data.has_em():
            trace_types.append("em")

        for trace_type in trace_types:
            cutted_trace = self.trace_data.get_trace(trace_type, tracenr)[start:end]
            if len(cutted_trace) < trace_length:
                # get a copy, before we can resize (sometimes "end" is beyond the end of the trace)
                cutted_trace = self.trace_data.get_trace(trace_type, tracenr)[
                    start:end
                ].copy()
                np.ndarray.resize(cutted_trace, trace_length)
            dtype = self.trace_data.get_traces(trace_type).dtype
            filtered_data = np.array(
                self._run_modifying_filter(cutted_trace), dtype=dtype
            )
            self.new_trace_data.add_trace(trace_type, filtered_data)

        return 1

    def _run_modifying_filter(self, trace_data: np.ndarray) -> np.ndarray:
        """Run all filters which have the key "modify_data" enabled and process them on the trace_data.
        In this case the filter isn't only processed to prepare trigger detection
        but actual modify the given data permant for storing.

        Parameters
        ----------
        trace_data : np.ndarray
            single trace to process. Should be a one dimensional array

        Returns
        -------
        np.ndarray
            processed trace data based on a "modifying" filter
        """
        # If no filters were selected, just return unmodified trace_data
        if self.filter_dict is None:
            return trace_data

        for filter_name, filter_parameter in self.filter_dict.items():
            # get data filter
            filter_to_use = self._filters.get_filter_by_name(filter_name)

            # check for "modify_data" key in filter parameter
            # If Modifying filter parameter 'modify_data' is true, it will be run now.
            filter_settings = filter_parameter[1]
            if "modify_data" in filter_settings:
                modify_data = bool(filter_parameter[1]["modify_data"][0])
                if modify_data:
                    # run filter
                    filter_result = filter_to_use.process_data(
                        trace_data, dict(filter_parameter[1])
                    )
                    trace_data = filter_result["data"]

        return trace_data

    def _finalize_new_traces(self):
        """Finalize AlignTraceData by register and store reduced
        plain and cipher traces and based on the valid_trace_array.
        """

        # Only process plain and cipher traces
        trace_types = []
        if self.trace_data.has_plain():
            trace_types.append("plain")
        if self.trace_data.has_cipher():
            trace_types.append("cipher")

        for trace_type in trace_types:
            trace_length = len(self.trace_data.get_trace(trace_type, 0))
            dtype = self.trace_data.get_traces(trace_type).dtype
            filename = (
                trace_type
                + "_aligned."
                + (
                    "dat"
                    if self.trace_data.trace_data_file_type
                    == TraceDataFileType.D15_TRACE_DATA
                    else "npy"
                )
            )
            self.new_trace_data.register_data_file(
                trace_type,
                self.new_filepath + filename,
                length=trace_length,
                dtype=dtype,
            )
            self.new_trace_data.reduce_data_from_mask(
                trace_type,
                self.trace_data.get_traces(trace_type),
                self.valid_traces_array,
            )

        self.new_trace_data.finish()
