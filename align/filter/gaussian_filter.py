from numpy import ndarray
from align.filter.filter import Filter
from scipy.ndimage import gaussian_filter1d
import logging


class GaussianFilter(Filter):
    """Gaussian Filter"""

    _filter_name = "gaussian_filter"
    _filter_options = dict(
        name=_filter_name,
        title="Gaussian filter",
        type="group",
        removable=True,
        movable=True,
        children=[
            dict(name="enabled", type="bool", value=True),
            dict(name="sigma", type="int"),
        ],
    )

    def __init__(self):
        logging.getLogger(__name__)

    def process_data(self, input_data: ndarray, filter_parameter: dict) -> dict:
        try:
            enabled = filter_parameter["enabled"][0]
            sigma = filter_parameter["sigma"][0]
        except KeyError:
            logging.error("unexpected filter parameter: %s", filter_parameter)
            raise

        logging.debug("enabled: %s, sigma: %s", enabled, sigma)

        if sigma > 0 and enabled:
            output_data = gaussian_filter1d(input_data, sigma)
        else:
            output_data = input_data

        return dict(data=output_data)
