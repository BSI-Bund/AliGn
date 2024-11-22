import logging
import numpy as np
from align.trigger.trigger import Trigger
from align.tracelib.dsp import matchByCorrelation


# TODO !NOT yet ready to use!
class MaxCorrelationTrigger(Trigger):
    _trigger_name = "max_correlation_trigger"
    _trigger_options = dict(
        name=_trigger_name,
        title="Max. Correlation Trigger",
        type="group",
        removable=True,
        movable=True,
        children=[
            dict(name="interval_length", type="int"),
            dict(name="stepsize", type="int", default=1),
        ],
    )

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG)

    def process_data(self, input_data: any, trigger_parameter: dict) -> dict:
        try:
            enabled = trigger_parameter["enabled"][0]
            # pattern = filter_parameter['pattern'][0]
            interval_length = trigger_parameter["interval_length"][0]
            stepsize = trigger_parameter["stepsize"][0]
        except KeyError:
            logging.error("unexpected filter parameter: %s", trigger_parameter)
            raise

        # self.logger.debug("enabled: %s, offset: %s, threshold: %s", enabled, offset, threshold)

        # FIXME Do it properly!
        # Demo Pattern
        # traces = np.load("/home/user/code/AliGn/demo/traces.npy")
        # pattern = traces[0, 90:110]

        x_matches = []
        # if enabled:
        #     x, corr = matchByCorrelation(input_data, pattern, offset_start, offset_stop)
        #     if x != 0:
        #         x_matches.append(x)

        return dict(xmarks=x_matches)
