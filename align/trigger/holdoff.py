import logging
from numpy import ndarray
from align.trigger.trigger import Trigger


class HoldoffTrigger(Trigger):
    """Trigger class for hold off trigger
    adds a given offset(hold-on) time"""

    _trigger_name = "hold_off"
    _trigger_options = dict(
        name=_trigger_name,
        title="Hold Off",
        type="group",
        removable=True,
        movable=True,
        children=[
            dict(name="holdoff", type="int"),
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
            dictionary which stores the found trigger point
        """
        try:
            holdoff = trigger_parameter["holdoff"][0]
        except KeyError:
            logging.error("unexpected trigger parameter: %s", trigger_parameter)
            raise

        self.logger.debug("offset: %s, holdoff: %s", offset, holdoff)

        x_matches = []
        if offset + holdoff < len(input_data):
            x_matches.append(offset + holdoff)

        return dict(xmarks=x_matches)
