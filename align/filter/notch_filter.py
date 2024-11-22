import logging
from scipy.signal import filtfilt, iirnotch, freqz
from align.filter.filter import Filter
import numpy as np


class IrrNotchFilter(Filter):
    """An IIR Notch filter"""

    _filter_name = "irr_notch_filter"
    _filter_options = dict(
        name=_filter_name,
        title="IIR Notch filter",
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
                name="notchFrequency", title="cutout freq", type="float", visible=True
            ),
            dict(name="harmonics", title="harmonics", type="int"),
        ],
    )

    def __init__(self):
        logging.getLogger(__name__)

    def process_data(self, input_data: any, filter_parameter: dict) -> dict:
        try:
            enabled = filter_parameter["enabled"][0]
            order = filter_parameter["order"][0]
            sample_frequency = filter_parameter["sampleFrequency"][0]
            notch_frequency = filter_parameter["notchFrequency"][0]
            harmonics = filter_parameter["harmonics"][0]
        except KeyError:
            logging.error("unexpected filter parameter: %s", filter_parameter)
            raise

        output_data = input_data

        if enabled:
            # filter notch frequency and harmonic 2 to 6
            for harmonic in range(1, harmonics + 1):
                b, a = iirnotch(notch_frequency * harmonic, order, sample_frequency)
                output_data = filtfilt(b, a, output_data)

        return dict(data=output_data)

    def frequency_response(self, filter_parameter: dict) -> list:
        """This function can be used to plot the frequency response of this filter"""
        try:
            order = filter_parameter["order"][0]
            sample_frequency = filter_parameter["sampleFrequency"][0]
            notch_frequency = filter_parameter["notchFrequency"][0]
            harmonics = filter_parameter["harmonics"][0]
        except KeyError:
            logging.error("unexpected filter parameter: %s", filter_parameter)
            raise
        pairs = []
        # we compute the frequency - response for the notch frequency
        # as well as all harmonics and return them as pairs
        for harmonic in range(1, harmonics + 1):
            b, a = iirnotch(notch_frequency * harmonic, order, sample_frequency)
            w, h = freqz(b, a, fs=sample_frequency)
            h1 = [20 * np.log10(abs(x)) for x in h]
            pairs.append((w, h1))
        return pairs
