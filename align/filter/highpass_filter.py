import logging
from scipy.signal import filtfilt, iirfilter, freqz
from align.filter.filter import Filter
import numpy as np


class HighpassFilter(Filter):
    """An IIR hihpass filter"""

    _filter_name = "highpass_filter"
    _filter_options = dict(
        name=_filter_name,
        title="IIR highpass filter",
        type="group",
        removable=True,
        movable=True,
        children=[
            dict(name="enabled", type="bool", value=False, default=False),
            dict(
                name="modify_data",
                title="modify data",
                type="bool",
                value=False,
                default=False,
            ),
            dict(name="order", type="int", value=6, default=6),
            dict(
                name="sampleFrequency", title="sample freq", type="float", visible=True
            ),
            dict(
                name="cutoffFreq", title="cutoff frequency", type="float", visible=True
            ),
        ],
    )

    def __init__(self):
        logging.getLogger(__name__)

    def process_data(self, input_data: np.ndarray, filter_parameter: dict) -> dict:
        try:
            enabled = filter_parameter["enabled"][0]
            order = filter_parameter["order"][0]
            sample_frequency = filter_parameter["sampleFrequency"][0]
            cutoff_freq = filter_parameter["cutoffFreq"][0]
        except KeyError:
            logging.error("unexpected filter parameter: %s", filter_parameter)
            raise

        output_data = input_data

        if enabled:
            b, a = iirfilter(
                order,
                cutoff_freq,
                btype="highpass",
                ftype="butter",
                fs=sample_frequency,
            )
            logging.debug(f"highpass filter b: {b}, a: {a}")
            output_data = filtfilt(b, a, output_data)

        return dict(data=output_data)

    def frequency_response(self, filter_parameter: dict) -> tuple:
        """This function can be used to plot the frequency response of this filter"""
        try:
            order = filter_parameter["order"][0]
            sample_frequency = filter_parameter["sampleFrequency"][0]
            cutoff_freq = filter_parameter["cutoffFreq"][0]
        except KeyError:
            logging.error("unexpected filter parameter: %s", filter_parameter)
            raise
        b, a = iirfilter(
            order,
            cutoff_freq,
            btype="highpass",
            ftype="butter",
            fs=sample_frequency,
        )
        w, h = freqz(b, a, fs=sample_frequency)
        h1 = [20 * np.log10(abs(x)) for x in h]
        return w, h1
