import pyqtgraph as pg
import logging


class FrequencyResponseViewer:
    """Viewer for frequency response for a given filter and it settings
       TODO not in use yet
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.plt = pg.plot()

    def show_frequency_response(self, filter, filter_parameter):

        frequency_respone = getattr(filter, "frequency_respone", None)
        if callable(frequency_respone):
            x, y = filter.frequency_respone(filter_parameter=filter_parameter)
        else:
            return

        self.plt = pg.plot()
        self.plt.showGrid(x=True, y=True)
        self.plt.addLegend()
        self.plt.setLabel("bottom", "Frequency [Hz]")
        self.plt.setLabel("left", "Amplitude response [dB]")
        self.plt.setMouseEnabled(y=False)
        self.plt.setAutoVisible(y=False)
        self.plt.plot(x, y, pen="g")
        self.plt.show()
