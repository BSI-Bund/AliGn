import logging

from numpy import ndarray
from align.trigger.trigger import Trigger
from align.tracelib.dsp import matchRisingEdge, matchFallingEdge


class RisingEdgeTrigger(Trigger):
    """Trigger class to get a trigger point on a rising edge with given threshold"""

    _trigger_name = "rising_edge_trigger"

    ## This trigger uses the following parameters
    #  - threshold: rising threshold (y-value) to be found
    _trigger_options = dict(
        name=_trigger_name,
        title="Rising Edge Trigger",
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
            trace data in which the trigger should be found
        offset : int
            offset to start the search from for trigger in input_data
        trigger_parameter : dict
            dictionary which contains the trigger(-specific) parameters

        Returns
        -------
        dict
            dictionary with the keyword "xmarks", which contains a list with the found x-coordinate of the rising edge.
        """
        try:
            threshold = trigger_parameter["threshold"][0]
        except KeyError:
            logging.error("unexpected trigger parameter: %s", trigger_parameter)
            raise

        self.logger.debug("offset: %s, threshold: %s", offset, threshold)

        x_matches = []
        x = matchRisingEdge(input_data, offset, threshold)
        if x != 0:
            x_matches.append(x)

        return dict(xmarks=x_matches)


class FallingEdgeTrigger(Trigger):
    """Trigger class to get a trigger point on a falling edge with given threshold"""

    _trigger_name = "falling_edge_trigger"

    ## This trigger uses the following parameters
    #  - threshold: falling threshold (y-value) to be found
    _trigger_options = dict(
        name=_trigger_name,
        title="Falling Edge Trigger",
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
        self, input_data: any, offset: int, trigger_parameter: dict
    ) -> dict:
        """Implements process_data method from parent class Trigger

        Parameters
        ----------
        input_data : ndarray
            trace data in which the trigger should be found
        offset : int
            offset to start the search from for trigger in input_data
        trigger_parameter : dict
            dictionary which contains the trigger(-specific) parameters

        Returns
        -------
        dict
            dictionary with the keyword "xmarks", which contains a list with the found x-coordinate of the falling edge.
        """
        try:
            threshold = trigger_parameter["threshold"][0]
        except KeyError:
            logging.error("unexpected filter parameter: %s", trigger_parameter)
            raise

        self.logger.debug("offset: %s, threshold: %s", offset, threshold)

        x_matches = []
        x = matchFallingEdge(input_data, offset, threshold)
        if x != 0:
            x_matches.append(x)

        return dict(xmarks=x_matches)
