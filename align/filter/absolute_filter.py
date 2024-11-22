from numpy import ndarray
from align.filter.filter import Filter
import logging


class AbsoluteFilter(Filter):
    """Filter class to get absolute values"""

    _filter_name = "abs_filter"

    ## This filter uses the following parameters
    #  - enabled: if enabled the filter returns absolte values from input data, else it returns the input data
    _filter_options = dict(
        name=_filter_name,
        title="absolute values",
        type="group",
        removable=True,
        movable=True,
        children=[dict(name="enabled", type="bool", value=True)],
    )

    def __init__(self):
        logging.getLogger(__name__)

    def process_data(self, input_data: ndarray, filter_parameter: dict) -> dict:
        """Applies filters to the input data based on the given parameter

        Parameters
        ----------
        input_data : ndarray
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
        except KeyError:
            logging.error("unexpected filter parameter: %s", filter_parameter)
            raise

        if enabled:
            output_data = abs(input_data)
        else:
            output_data = input_data

        return dict(data=output_data)
