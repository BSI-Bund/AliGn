import logging
import numpy as np
import pyqtgraph as pg
from PySide6.QtGui import QIcon


class FrequencyAnalyzer:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.plt = pg.plot()

    def _calc_frequency_scale(self, input_data: np.ndarray, sample_frequency: float):
        """Calculate the frequency scale of the gievn input data

        Parameters
        ----------
        input_data : np.ndarray
            data to analyze
        sample_frequency : float
            sample frequency with which the data was recorded

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            frequency scale and output_data
        """
        number_sample_points = len(input_data)
        self.logger.debug(
            "FrequencyAnalyzer sampleFrequency: {}".format(sample_frequency)
        )
        y_values = np.fft.fft(input_data)
        self.logger.debug("y_values: {}".format(y_values))
        # Calculate the data for the plots
        y_values = np.abs(y_values[: int(number_sample_points / 2)])
        output_data = (100.0 * y_values) / number_sample_points
        output_data[0] = 0
        freq_scale = np.linspace(
            0, sample_frequency // 2, number_sample_points // 2
        )  # linspace needs integer values therefore the use of the "floor" operator (//)
        return freq_scale, output_data

    def plot_data(self, input_data: np.ndarray, sample_frequency: float):
        """Open a new windows and plot the frequency spectrum of the given data

        Parameters
        ----------
        input_data : np.ndarray
            data to analyze
        sample_frequency : float
            sample frequency with which the data was recorded
        """
        freq_scale, output_data = self._calc_frequency_scale(
            input_data, sample_frequency
        )
        self.plt.plot(freq_scale, output_data, pen="g")
        self.plt.showGrid(x=True, y=True)
        self.plt.addLegend()
        self.plt.setLabel("bottom", "Frequency", units="Hz")
        self.plt.setMouseEnabled(y=False)  # Only allow zoom in x-axis
        self.plt.setAutoVisible(y=False)
        self.plt.setLimits(xMin=min(freq_scale), xMax=max(freq_scale))
        self.plt.setWindowTitle("AliGn Frequency Analyzer")
        self.plt.setWindowIcon(QIcon(":/icons/signal-alt-2.png"))
        self.plt.show()
