from align.filter.filter import Filter
from numpy import convolve, ones
import logging


class MovingAverageFilter(Filter):
    """Moving average filter"""

    _filter_name = "moving_average_filter"
    _filter_options = dict(
        name=_filter_name,
        title="Moving Average filter",
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

    def process_data(self, input_data: any, filter_parameter: dict) -> dict:
        try:
            enabled = filter_parameter["enabled"][0]
            window_len = filter_parameter["window_len"][0]
        except KeyError:
            logging.error("unexpected filter parameter: %s", filter_parameter)
            raise

        logging.debug("enabled: %s, window_len: %s", enabled, window_len)

        if window_len > 0 and enabled:
            output_data = self._moving_average(input_data, window_len)
        else:
            output_data = input_data

        return dict(data=output_data)

    def _moving_average(self, data, factor_compression):
        return convolve(data, ones(factor_compression) / factor_compression, "valid")
