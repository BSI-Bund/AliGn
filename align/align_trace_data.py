import configparser
import logging
import os
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

import numpy as np
from typing_extensions import Self

from align.tracelib.traces import TraceData


class TraceDataFileType(Enum):
    """Enum class for the supported data type"""

    D15_TRACE_DATA = "D15 Trace Data Metafile"
    NPY_ARRAYS = "Numpy Arrays"

    @staticmethod
    def list() -> list:
        """Returns a list with all available enum values

        Returns
        -------
        list
           All available enum values
        """
        return list(map(lambda c: c.value, TraceDataFileType))


class TraceType(Enum):
    """Enum class for the trace data types we usually use"""

    EM = "em"
    POWER = "power"
    PLAIN = "plain"
    CIPHER = "cipher"
    AUX = "aux"


class AlignTraceData(ABC):
    """Abstract Base Class for Aligns traca data which defines all methods that
    concret classes have to implement to be used in AliGn
    """

    def __init__(self, trace_data_file_type: TraceDataFileType):
        """Init method

        Parameters
        ----------
        trace_data_file_type : TraceDataFileType
            A valid TraceDataFileType for this instance of AlignTraceData
        """
        self.path = None
        self.meta_file = None
        self.trace_data_files_dict = dict()
        self.trace_data_file_type = trace_data_file_type

    @abstractmethod
    def get_trace_data_files(self) -> dict:
        """Returns a dictionary for all available data files
        key is file type as string ('em', 'power', etc.),
        value is a path string

          Returns
          -------
          dict
              dictionary for all available data files
              key is file type as string ('em', 'power', etc.),
              value is a path string
        """

    @abstractmethod
    def get_trace_types(self) -> list[str]:
        """Returns a string list of all available data types

        Returns
        -------
        list
            list of all available data types
        """

    ##
    @abstractmethod
    def has_em(self) -> bool:
        """True if TraceData contains em trace file

        Returns
        -------
        bool
            True if TraceData contains em trace file
        """

    @abstractmethod
    def has_power(self) -> bool:
        """True if TraceData contains power trace file

        Returns
        -------
        bool
            True if TraceData contains power trace file
        """

    @abstractmethod
    def has_plain(self) -> bool:
        """True if TraceData contains plain trace file

        Returns
        -------
        bool
            True if TraceData contains plain trace file
        """

    @abstractmethod
    def has_cipher(self) -> bool:
        """True if TraceData contains cipher trace file

        Returns
        -------
        bool
            True if TraceData contains cipher trace file
        """

    ##
    @abstractmethod
    def get_comment(self) -> str | None:
        """Returns the comment string of the AlignTraceData if available

        Returns
        -------
        str, None
            comment string of the AlignTraceData if available
        """

    @abstractmethod
    def get_sample_freq(self) -> float | None:
        """Returns the sample frequency of the AlignTraceData if available

        Returns
        -------
        float, None
            sample frequency of the AlignTraceData if available
        """

    @abstractmethod
    def get_number_of_traces(self) -> int:
        """Returns the number of traces in the data file of the AlignTraceData

        Returns
        -------
        int
            number of traces in the data file of the AlignTraceData
        """

    @abstractmethod
    def set_number_of_traces(self, number_of_traces: int) -> None:
        """Set a new number of traces of the AlignTraceData.
        Used for store a subset of the original AlignTraceData traces

        Parameters
        ----------
        number_of_traces : int
            new number of traces of the AlignTraceData
        """

    @abstractmethod
    def get_trace(self, trace_type: str, trace_nr: int) -> np.ndarray:
        """Returns a single (one dimensional) trace array from
        the requested trace data type and trace number

          Parameters
          ----------
          trace_data_name : str
              type of trace data e.g. 'em', 'power', etc.
          trace_nr : int
              The number of the trace which shall be returned in array

          Returns
          -------
          np.ndarray
              An array containing the data of the requested trace type and number
        """

    @abstractmethod
    def get_traces(self, trace_type: str) -> np.ndarray | None:
        """Returns the all traces of the requested trace_type in a two dimensional array

        Parameters
        ----------
        trace_data_name : str
            type of trace data e.g. 'em', 'power', etc.

        Returns
        -------
        np.ndarray, None
            all traces of the requested trace_type in a two dimensional array
        """

    @abstractmethod
    def reduce_data_from_mask(
        self, trace_type: str, input_data: np.ndarray, trace_mask: np.ndarray
    ) -> None:
        """Reduces the (two dimensional) input_data trace array from the trace_mask.
        Keeps data at the indexes in input_data where the index in there corresponding trace_mask is "1",
        other indexes will be discarded. The reduced array will be stored as self.trace_type

          Parameters
          ----------
          trace_type : str
              Trace type as which the reduced array is to be stored in this AlignTraceData
          input_data : np.ndarray
              two dimensional input_data trace array which shall be masked
          trace_mask : np.ndarray
              one dimensional trace mask which shall have the some length as one trace in input_data
              Indexes in trace_mask which contains value '1' will be keep in input_data

          Returns
          -------
          None
            Returns nothing since the reduced array is stored inside this AlignTraceData obeject
            as type trace_type. New length of traces are the number of '1's in the trace_mask
        """

    @abstractmethod
    def register_data_file(
        self,
        trace_type: str,
        data_file_name: os.PathLike,
        length: int,
        dtype: type,
    ) -> None:
        """register/add a new trace data file to this AlignTraceData

        Parameters
        ----------
        trace_type : str
            type of trace which shall be add to this AlignTraceData
        data_file_name : os.PathLike
            file name where the new traces shall be stored into
        length : int
            The length which each trace is expected to have
        dtype : type
            stores new traces as this data type e.g. np.int16
        """

    @abstractmethod
    def add_trace(self, trace_type: str, trace_data: np.ndarray) -> None:
        """Adds a single trace to a registered trace data file
        The length of the trace_data must match the length which was defined in the
        register_data_file method.

        Parameters
        ----------
        trace_type : str
            type of trace to which the data shall be added
        trace_data : np.ndarray
            the trace to be added to the trace_type trace data file
        """

    @abstractmethod
    def finish(self) -> None:
        """finishs the editing on this AlignTraceData
        stores files to disk and cleanup
        """

    @abstractmethod
    def prepare_new_tracedata(self, new_filepath: os.PathLike) -> Self:
        """Prepare/init a new AlignTraceData object based on the actual one at the given new_file_path
        Copy meta data to the new AlignTraceData object and returns the new AlignTraceData object

        Parameters
        ----------
        new_filepath : os.PathLike
            path/filename of the new AlignTraceData

        Returns
        -------
        Self
            Returns an new AlignTraceData object based on the AlignTraceData object
            which this method was be called from
        """


class AlignTraceDataFactory:
    """Factory class that provides an unified opening and creating methods for all
    supported types of AlignTraceData objects
    """

    @staticmethod
    def open_trace_data(trace_data_file: str | dict) -> AlignTraceData:
        """Opens AlignTraceData file(s). If trace_data_file contains a string with a
        path to a D15TraceData .meta file a D15TraceData AlignTraceData instance is returned.
        If trace_data_file is a dict a NumpyArrays AlignTraceData instance is returned


        Parameters
        ----------
        trace_data_file : str, dict
           filename of a D15TraceData .meta file or a dict containing
           the filenames to the different trace_types

        Returns
        -------
        AlignTraceData
            Either an instance of D15TraceData or an instance of NumpyArrays

        Raises
        ------
        ValueError
            if an unsupported file format was provided
        """
        if isinstance(trace_data_file, str) or isinstance(trace_data_file, Path):
            if os.path.splitext(trace_data_file)[1] == ".meta":
                return D15TraceData(str(trace_data_file))
        elif isinstance(trace_data_file, dict):
            return NumpyArrays(trace_data_file)
        else:
            raise ValueError("unsupported file format!")

    @staticmethod
    def get_new_trace_data(trace_data_file_type: TraceDataFileType) -> AlignTraceData:
        """Returns a new AlignTraceData object. Based on the requested trace_data_file_type
        either an instance of D15TraceData or an instance of NumpyArrays.

        Parameters
        ----------
        trace_data_file_type : TraceDataFileType
            AlignTraceData trace data instance to create

        Returns
        -------
        AlignTraceData
            Based on the requested trace_data_file_type either an
            instance of D15TraceData or an instance of NumpyArrays

        Raises
        ------
        ValueError
            if an unsupported TraceDataFileType was requested
        """
        if trace_data_file_type == TraceDataFileType.D15_TRACE_DATA:
            return D15TraceData()
        elif trace_data_file_type == TraceDataFileType.NPY_ARRAYS:
            return NumpyArrays()
        else:
            raise ValueError(f"Unsupported file format: {trace_data_file_type}")


class D15TraceData(AlignTraceData):
    def __init__(self, filename: str = None):
        super().__init__(TraceDataFileType.D15_TRACE_DATA)
        self.trace_data = TraceData(filename)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        if filename is not None:
            self.path = os.path.dirname(filename)
            self.meta_file = os.path.realpath(filename)

    def get_trace_data_files(self) -> dict:
        self.trace_data_files_dict = dict()
        if self.trace_data.hasEM and self.trace_data.em.isFile:
            self.trace_data_files_dict["em"] = self.trace_data.em.fileName
        if self.trace_data.hasPower and self.trace_data.power.isFile:
            self.trace_data_files_dict["power"] = self.trace_data.power.fileName
        if self.trace_data.hasPlain and self.trace_data.plain.isFile:
            self.trace_data_files_dict["plain"] = self.trace_data.plain.fileName
        if self.trace_data.hasCipher and self.trace_data.cipher.isFile:
            self.trace_data_files_dict["cipher"] = self.trace_data.cipher.fileName
        if self.trace_data.hasAux:
            for key in self.trace_data.aux:
                self.trace_data_files_dict["aux_" + key] = self.trace_data.aux[
                    key
                ].fileName
        return self.trace_data_files_dict

    def get_trace_types(self) -> list:
        return list(self.trace_data_files_dict.keys())

    def get_number_of_traces(self) -> int:
        if self.trace_data is None:
            return None

        return self.trace_data.getNrTraces()

    def set_number_of_traces(self, number_of_traces: int) -> None:
        self.trace_data.setNrTraces(number_of_traces)

    def has_em(self) -> bool:
        if self.trace_data is None:
            return False

        return self.trace_data.hasEM

    def has_power(self) -> bool:
        if self.trace_data is None:
            return False

        return self.trace_data.hasPower

    def has_plain(self) -> bool:
        if self.trace_data is None:
            return False

        return self.trace_data.hasPlain

    def has_cipher(self) -> bool:
        if self.trace_data is None:
            return False

        return self.trace_data.hasCipher

    def get_comment(self) -> str | None:
        if self.trace_data is None:
            return None

        return self.trace_data.config.get("COMMON", "comment")

    def get_sample_freq(self) -> float | None:
        if self.trace_data is None:
            return None

        sample_freq = None
        try:
            if self.trace_data.hasEM:
                sample_freq = 1 / float(
                    self.trace_data.config.get("EM_SCOPE", "HORIZ_INTERVAL")
                )
            elif self.trace_data.hasPower:
                sample_freq = 1 / float(
                    self.trace_data.config.get("POWER_SCOPE", "HORIZ_INTERVAL")
                )
            return round(sample_freq, 3)
        except configparser.NoSectionError:
            return -1.0

    def get_trace(self, trace_type: str, trace_nr: int) -> np.ndarray | None:
        if self.trace_data is None or trace_type == "":
            return None
        if trace_nr >= self.get_number_of_traces():
            return None
        return self.get_traces(trace_type)[trace_nr, :]

    def get_traces(self, trace_type: str) -> np.ndarray | None:
        if self.trace_data is None:
            return None
        if trace_type == "":
            return None

        if trace_type == "em":
            traces = self.trace_data.em.data
        elif trace_type == "power":
            traces = self.trace_data.power.data
        elif trace_type == "plain":
            traces = self.trace_data.plain.data
        elif trace_type == "cipher":
            traces = self.trace_data.cipher.data
        # elif trace_data_name == "aux":
        #     traces = self.trace_data.aux[trace_data_name].data
        else:
            traces = None

        return traces

    def reduce_data_from_mask(
        self, trace_type: str, input_data: np.ndarray, trace_mask: np.ndarray
    ) -> None:
        if self.trace_data is None:
            return None
        self.logger.debug(
            "input_data type: %s, trace_mask type: %s",
            type(input_data),
            type(trace_mask),
        )

        if trace_type == "em":
            trace_data_object = self.trace_data.em
        elif trace_type == "power":
            trace_data_object = self.trace_data.power
        elif trace_type == "plain":
            trace_data_object = self.trace_data.plain
        elif trace_type == "cipher":
            trace_data_object = self.trace_data.cipher
        else:
            trace_data_object = self.trace_data.aux[trace_type]

        for iTrace in range(trace_mask.shape[0]):
            if trace_mask[iTrace]:
                trace_data_object._addTraceRaw(input_data[iTrace].tobytes())

    def register_data_file(
        self,
        trace_type: str,
        data_file_name: os.PathLike,
        length: int,
        dtype: type,
    ) -> None:
        if self.trace_data is None:
            return None

        if trace_type == "em":
            self.trace_data.registerEMFile(data_file_name, length, dtype)
        elif trace_type == "power":
            self.trace_data.registerPowerFile(data_file_name, length, dtype)
        elif trace_type == "plain":
            self.trace_data.registerPlainFile(data_file_name, length, dtype)
        elif trace_type == "cipher":
            self.trace_data.registerCipherFile(data_file_name, length, dtype)
        else:
            self.trace_data.registerAuxFile(data_file_name, trace_type, length, dtype)

    def add_trace(self, trace_type: str, trace_data: np.ndarray) -> None:
        if self.trace_data is None:
            return None

        if trace_type == "em":
            self.trace_data.em.addTrace(trace_data)
        elif trace_type == "power":
            self.trace_data.power.addTrace(trace_data)
        elif trace_type == "plain":
            self.trace_data.plain.addTrace(trace_data)
        elif trace_type == "cipher":
            self.trace_data.cipher.addTrace(trace_data)
        else:
            self.trace_data.aux[trace_type].addTrace(trace_data)

    def finish(self) -> None:
        self.trace_data.finishRecord()

    def prepare_new_tracedata(self, new_filepath: os.PathLike) -> AlignTraceData:
        new_tracedata = AlignTraceDataFactory.get_new_trace_data(
            self.trace_data_file_type
        )
        new_meta_filename = os.path.join(new_filepath, "traces_aligned.meta")
        new_tracedata.trace_data.newFrom(new_meta_filename, self.meta_file)
        return new_tracedata


class NumpyArrays(AlignTraceData):
    def __init__(self, npy_files: dict = None):
        super().__init__(TraceDataFileType.NPY_ARRAYS)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self._npy_mm = dict()
        self._records_written = 0
        last_file_name = None
        self.path = None
        self.number_of_traces = 0

        if npy_files is not None:
            self.trace_data_files_dict = npy_files
            i = 0
            n_of_t = []
            for trace_data_name, filename in npy_files.items():
                if not os.path.exists(filename):
                    continue
                self._npy_mm[trace_data_name] = np.atleast_2d(
                    np.lib.format.open_memmap(filename)
                )
                shape = self._npy_mm[trace_data_name].shape

                if len(shape) != 2:
                    self.logger.warning("NPY array has wrong shape!")
                    raise ValueError("NPY array has wrong shape!")

                n_of_t.insert(i, shape[0])
                self.logger.info(
                    "NPY %s array contains %s trace(s).", trace_data_name, n_of_t[i]
                )

                # Check if all npy array have the same number of traces
                if i > 0 and n_of_t[i] != n_of_t[i - 1]:
                    self.logger.warning("Number of traces of NPY arrays don't match!")
                    raise ValueError

                last_file_name = os.path.realpath(filename)
                i = i + 1

            if len(n_of_t) != 0:
                self.number_of_traces = n_of_t[0]
            if last_file_name is not None:
                self.path = os.path.dirname(last_file_name)

    def get_trace_data_files(self) -> dict:
        return self.trace_data_files_dict

    def get_trace_types(self) -> list:
        return list(self.trace_data_files_dict.keys())

    def has_em(self) -> bool:
        if self.trace_data_files_dict is not None:
            return "em" in self._npy_mm

    def has_power(self) -> bool:
        if self.trace_data_files_dict is not None:
            return "power" in self._npy_mm

    def has_plain(self) -> bool:
        if self.trace_data_files_dict is not None:
            return "plain" in self._npy_mm

    def has_cipher(self) -> bool:
        if self.trace_data_files_dict is not None:
            return "cipher" in self._npy_mm

    def get_comment(self) -> str:
        return ""

    def get_sample_freq(self) -> float:
        return -1.0

    def get_number_of_traces(self) -> int:
        return self.number_of_traces

    def set_number_of_traces(self, number_of_traces: int) -> None:
        self.number_of_traces = number_of_traces

    def get_trace(self, trace_type: str, trace_nr: int) -> np.ndarray:
        if trace_type == "":
            return None
        self.logger.debug(
            f"get trace({trace_type}, {trace_nr}) on {type(self._npy_mm[trace_type])} with shape {self._npy_mm[trace_type].shape}"
        )
        return self._npy_mm[trace_type][trace_nr, :]

    def get_traces(self, trace_type: str) -> np.ndarray:
        return self._npy_mm[trace_type]

    def reduce_data_from_mask(
        self,
        trace_type: str,
        input_data: np.ndarray,
        trace_mask: np.ndarray[np.bool_],
    ) -> None:
        if self._npy_mm is None:
            return
        # remove positions in input_data which are "False" in trace_mask
        # first get the ensure trace_mask has the same length as the number of traces in input_data
        number_to_pad = input_data.shape[0] - trace_mask.shape[0]
        new_trace_mask = np.pad(
            trace_mask, (0, number_to_pad), "constant", constant_values=(False)
        )
        self._npy_mm[trace_type] = input_data[new_trace_mask, ...]

    def register_data_file(
        self,
        trace_type: str,
        data_file_name: os.PathLike,
        length: int,
        dtype: type,
    ) -> None:
        self.trace_data_files_dict[trace_type] = data_file_name
        self._npy_mm[trace_type] = np.ndarray(
            dtype=dtype, shape=(self.number_of_traces, length)
        )
        # self.npy_mm[trace_data_name] = np.memmap(data_file_name, dtype=dtype, mode='w+', shape=(self.number_of_traces, length))

    def add_trace(self, trace_type: str, trace_data: np.ndarray) -> None:
        if self._records_written >= self.number_of_traces:
            self.logger.warning(
                "Already wrote %s records to array with size %s. Can't write more traces into array! Ignoring trace.",
                self._records_written,
                self.number_of_traces,
            )
            return
        self._npy_mm[trace_type][self._records_written] = trace_data
        self._records_written += 1

    def finish(self) -> None:
        if self.has_em():
            with open(self.trace_data_files_dict["em"], "wb") as file:
                np.save(file, self._npy_mm["em"])
        if self.has_power():
            with open(self.trace_data_files_dict["power"], "wb") as file:
                np.save(file, self._npy_mm["power"])
        if self.has_cipher():
            with open(self.trace_data_files_dict["cipher"], "wb") as file:
                np.save(file, self._npy_mm["cipher"])
        if self.has_plain():
            with open(self.trace_data_files_dict["plain"], "wb") as file:
                np.save(file, self._npy_mm["plain"])

    def prepare_new_tracedata(self, new_filepath: os.PathLike) -> AlignTraceData:
        new_tracedata = AlignTraceDataFactory.get_new_trace_data(
            self.trace_data_file_type
        )
        self._create_dir(os.path.abspath(new_filepath))
        new_tracedata.set_number_of_traces(self.get_number_of_traces())
        return new_tracedata

    def _create_dir(self, directory):
        if directory[-1] == "/":
            directory = directory[:-1]
        if not os.path.exists(directory):
            os.makedirs(directory)
            return directory
