from numpy import ndarray
from align.filter.filter import Filter
from align.tracelib.dsp import smooth
import logging


class HanningFilter(Filter):
    """Hanning Filter"""

    _filter_name = "hanning_filter"
    _filter_options = dict(
        name=_filter_name,
        title="Hanning filter",
        type="group",
        removable=True,
        movable=True,
        children=[
            dict(name="enabled", type="bool", value=True),
            dict(name="window_len", title="window length", type="int"),
        ],
    )

    def __init__(self):
        logging.getLogger(__name__)

    def process_data(self, input_data: ndarray, filter_parameter: dict) -> dict:
        try:
            enabled = filter_parameter["enabled"][0]
            window_len = filter_parameter["window_len"][0]
        except KeyError:
            logging.error("unexpected filter parameter: %s", filter_parameter)
            raise

        logging.debug("enabled: %s, window_len: %s", enabled, window_len)

        if window_len > 0 and enabled:
            output_data = smooth(input_data, window_len, "hanning")[::]
        else:
            output_data = input_data

        return dict(data=output_data)
