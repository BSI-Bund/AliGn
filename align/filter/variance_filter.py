import logging
import resampy
import numpy as np

# from scipy import interpolate
from align.filter.filter import Filter
from align.tracelib.dsp import calculateVariance


class VarianceFilter(Filter):
    """An fast variance filter, which seems to be a bit too unprecise on longer traces"""

    _filter_name = "variance_filter"
    _filter_options = dict(
        name=_filter_name,
        title="Variance Filter",
        type="group",
        removable=True,
        movable=True,
        children=[
            dict(name="enabled", type="bool", value=False, default=False),
            dict(name="interval_size", type="int"),
        ],
    )

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG)

    def process_data(self, input_data: any, filter_parameter: dict) -> dict:
        try:
            enabled = filter_parameter["enabled"][0]
            interval_size = filter_parameter["interval_size"][0]
        except KeyError:
            logging.error("unexpected filter parameter: %s", filter_parameter)
            raise

        self.logger.debug("enabled: %s, interval_size: %s", enabled, interval_size)

        if enabled:
            output_data = calculateVariance(input_data, interval_size)

            ### seems to be a bit too unprecise on longer traces
            output_data = self._interpolate_stretch_np(output_data, len(input_data))

        else:
            output_data = input_data

        return dict(data=output_data)

    def _interpolate_stretch_np(self, array_to_stretch, new_len):
        xloc = np.arange(len(array_to_stretch))
        new_xloc = np.linspace(0.0, len(array_to_stretch) - 1, new_len)
        stretched_array = np.interp(new_xloc, xloc, array_to_stretch)
        return stretched_array


class VarianceFilter2(Filter):
    """An variance filter which uses resampling. It's a bit slow but sometimes delivers "better" results"""

    _filter_name = "variance_filter2"

    _filter_options = dict(
        name=_filter_name,
        title="Variance Filter (resample)",
        type="group",
        removable=True,
        movable=True,
        children=[
            dict(name="enabled", type="bool", value=False, default=False),
            dict(name="interval_size", type="int"),
        ],
    )

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG)

    def process_data(self, input_data: any, filter_parameter: dict) -> dict:
        try:
            enabled = filter_parameter["enabled"][0]
            interval_size = filter_parameter["interval_size"][0]
        except KeyError:
            logging.error("unexpected filter parameter: %s", filter_parameter)
            raise

        self.logger.debug("enabled: %s, interval_size: %s", enabled, interval_size)

        if enabled:
            output_data = calculateVariance(input_data, interval_size)

            ## good but slow
            output_data = resampy.resample(
                output_data, len(output_data), len(input_data)
            )

        else:
            output_data = input_data

        return dict(data=output_data)
