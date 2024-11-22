from align.filter.filter import Filter
import numpy as np
import logging


class FftFilter(Filter):
    """An FFT filter"""

    _filter_name = "fft_filter"

    _filter_options = dict(
        name=_filter_name,
        title="FFT filter",
        type="group",
        removable=True,
        movable=True,
        children=[
            dict(name="enabled", type="bool", value=False, default=False),
            dict(name="sampleFreq", type="int", value=10000, default=10000),
            dict(name="frequency", type="int", value=1, default=1),
        ],
    )

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG)

    def process_data(self, input_data: np.ndarray, filter_parameter: dict) -> dict:
        """Applies filters to the input data based on the given parameter

        Parameters
        ----------
        input_data : np.ndarray
            trace on which the filter function should be applied on
        filter_parameter : dict
            dictionary which contains the filter(-specific) parameters

        Returns
        -------
        dict
            dictionary with keyword 'data' which contains the processed data
        """
        try:
            enabled = filter_parameter["enabled"][0]
            sample_frequency = filter_parameter["sampleFreq"][0]
            frequency = filter_parameter["frequency"][0]
            fft_length = len(input_data)

        except KeyError as error:
            self.logger.error("Couldn't get filter parameter key: %s", error)
            raise

        self.logger.debug(
            "enabled: %s, frequency: %s, fft_length: %s", enabled, frequency, fft_length
        )

        if enabled:
            # sampleFreq = 1000000000 #hier: 1 GS / s, d.h. 1 * 10^9
            # sampleFreq = 2.5 * (10**9)
            # not sure if need to look at the sample rate to get a good fft shape. tried with sampleFreq = 10000 * frequency. works nice for now
            frequency_axis = np.linspace(
                0, sample_frequency / 2, int(fft_length / 2 + 1), endpoint=True
            )

            fft = np.fft.rfft(input_data, fft_length)
            fft[np.where(frequency_axis > frequency)] = 0
            output_data = np.fft.irfft(fft)
            self.logger.debug(
                "FFT data out: %s, len : %s", output_data, len(output_data)
            )

        else:
            output_data = input_data

        return dict(data=output_data)
