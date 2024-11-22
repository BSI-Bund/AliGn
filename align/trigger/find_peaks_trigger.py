from numpy import ndarray
from align.trigger.trigger import Trigger
from align.tracelib.dsp import findFirstPeak, findLastPeak
import logging


# Filter that generate xmarks shall not return 'xmarks = None' if not peaks were found but return a empty list 'xmarks = []'
# otherwise batch processing may produce wrong results


class FirstPeakFilter(Trigger):
    """Trigger class to get a trigger point on the first peak with given (positive or negative) threshold"""

    _trigger_name = "first_peak_trigger"

    ## This trigger uses the following parameters
    #  - threshold: threshold (y-value) to be found
    _trigger_options = dict(
        name=_trigger_name,
        title="First Peak Trigger",
        type="group",
        removable=True,
        movable=True,
        children=[
            dict(name="threshold", type="float", default=1.0),
        ],
    )

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG)

    def process_data(
        self, input_data: ndarray, offset: int, trigger_parameter: dict
    ) -> dict:
        """Implements process_data method from parent class Trigger

        Parameters
        ----------
        input_data : ndarray
            trace in which the trigger should be found
        offset : int
            offset to start the search from for trigger in input_data_
        trigger_parameter : dict
            dictionary which contains the trigger(-specific) parameters

        Returns
        -------
        _dict
            dictionary with the keyword "xmarks", which contains a list with the found x-coordinate of the first peak.
        """
        peak = []
        try:
            threshold = trigger_parameter["threshold"][0]
        except KeyError:
            self.logger.error("unexpected trigger parameter: %s", trigger_parameter)
            raise

        self.logger.debug("threshold: %s", threshold)

        find_max = threshold >= 0
        min_dist = 10

        found_peak = findFirstPeak(input_data[offset:], min_dist, threshold, find_max)
        if found_peak is not None:
            peak.append(found_peak[0] + offset)
            self.logger.debug(
                "found peak at: %s, value: %s", found_peak[0], found_peak[1]
            )
        else:
            self.logger.debug("didn't find a peak")

        return dict(xmarks=peak)


class LastPeakFilter(Trigger):
    """Trigger class to get a trigger point on the last peak with given (positive or negative)
    threshold by searching through the trace backwards"""

    _trigger_name = "last_peak_filter"

    ## This trigger uses the following parameters
    #  - threshold: threshold (y-value) to be found
    _trigger_options = dict(
        name=_trigger_name,
        title="Last Peak filter",
        type="group",
        removable=True,
        movable=True,
        children=[
            dict(name="threshold", type="float", default=1.0),
        ],
    )

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG)

    def process_data(
        self, input_data: ndarray, offset: int, trigger_parameter: dict
    ) -> dict:
        """Implements process_data method from parent class Trigger

        Parameters
        ----------
        input_data : ndarray
            input_data trace in which the trigger should be found
        offset : int
            offset to start the search from for trigger in input_data
        trigger_parameter : dict
            dictionary which contains the trigger(-specific) parameters

        Returns
        -------
        dict
            dictionary with the keyword "xmarks", which contains a list with the found x-coordinate of the last peak.
        """

        peak = []
        try:
            threshold = trigger_parameter["threshold"][0]
        except KeyError:
            self.logger.error("unexpected trigger parameter: %s", trigger_parameter)
            raise

        self.logger.debug("threshold: %s", threshold)

        find_max = threshold >= 0
        min_dist = 10

        found_peak = findLastPeak(input_data[offset:], min_dist, threshold, find_max)
        if found_peak is not None:
            peak.append(found_peak[0])
            self.logger.debug(
                "found peak at: %s, value: %s", found_peak[0], found_peak[1]
            )
        else:
            self.logger.debug("didn't find a peak")

        return dict(xmarks=peak)


class ThresholdTrigger(Trigger):
    """Trigger class searchs for a range in which the y-values keeps over the threshold (+-hysteresis)
    value over the given minimum range size. Can be inversed to search for a range in which the
    y-values keeps below threshold (+-hysteresis). Returns two xmark points.
    The first is the starting point of the found range. The second is the end of the found range.
    """

    _trigger_name = "threshold_trigger"

    ## This trigger uses the following parameters
    #  - threshold: threshold (y-value) to be keeped over the min_range
    #  - hysteresis: value to add to threshold on start point and substract from threshold at end point
    #  - min_range: minimum range that the treshold value should be keeped over / under (if inversed)
    #  - inverse: if selected it will be searched for min_range for which the y-values keeped below threshold
    _trigger_options = dict(
        name=_trigger_name,
        title="Threshold Trigger",
        type="group",
        removable=True,
        movable=True,
        children=[
            dict(name="threshold", type="float", default=1.0),
            dict(name="hysteresis", type="float", default=0.0),
            dict(name="min_range", type="int", default=500),
            dict(name="inverse", type="bool", value=False, default=False),
        ],
    )

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG)

    def process_data(
        self, input_data: ndarray, offset: int, trigger_parameter: dict
    ) -> dict:
        """Implements process_data method from parent class Trigger

        Parameters
        ----------
        input_data : ndarray
            trace in which the trigger should be found
        offset : int
            offset to start the search from for trigger in input_data
        trigger_parameter : dict
            dictionary which contains the trigger(-specific) parameters

        Returns
        -------
        dict
            dictionary with the keyword "xmarks", which contains a list with two x-values which marks the found range.
        """

        peaks = [None, None]
        try:
            threshold = trigger_parameter["threshold"][0]
            hysteresis = trigger_parameter["hysteresis"][0]
            min_range = trigger_parameter["min_range"][0]
            inverse = trigger_parameter["inverse"][0]
        except KeyError:
            self.logger.error("unexpected filter parameter: %s", trigger_parameter)
            raise

        self.logger.debug(
            "threshold: %s, hysteresis: %s, min_range: %s, inverse: %s",
            threshold,
            hysteresis,
            min_range,
            inverse,
        )

        i = offset
        while i < len(input_data):
            if not inverse:
                if peaks[0] is None and input_data[i] >= (threshold + hysteresis):
                    peaks[0] = i
                elif peaks[0] is not None and input_data[i] <= (threshold - hysteresis):
                    peaks[1] = i
                    if peaks[1] - peaks[0] >= min_range:
                        break
                    else:
                        peaks = [None, None]
            else:
                if peaks[0] is None and input_data[i] <= (threshold - hysteresis):
                    peaks[0] = i
                elif peaks[0] is not None and input_data[i] >= (threshold + hysteresis):
                    peaks[1] = i
                    if peaks[1] - peaks[0] >= min_range:
                        break
                    else:
                        peaks = [None, None]

            i += 1

        # Ensure that always two peaks are returned
        if peaks[0] is None or peaks[1] is None:
            peaks = [None, None]

        self.logger.debug("%s returns: %s", self._trigger_name, dict(xmarks=peaks))

        return dict(xmarks=peaks)
