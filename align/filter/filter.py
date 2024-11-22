from __future__ import annotations
import importlib
import inspect
import logging
from os import listdir, sep
from os.path import isfile, join
from abc import ABC, abstractmethod
from pathlib import Path

from numpy import ndarray


class FilterLoader:
    """This class searchs in the filter_folder ('./align/filter') for files that contains subclasses from "Filter" class
    and add them to a filter list which contains valid AliGn filters."""

    def __init__(self):
        logging.getLogger(__name__)
        self._filter_classes = []

        # filter_folder = "src/align/filter"
        filter_folder = Path(__file__).resolve().parent
        files_in_filters = [
            f for f in listdir(filter_folder) if isfile(join(filter_folder, f))
        ]
        logging.debug("Files in filters folders: %s", files_in_filters)
        filter_module_names = []

        for f in files_in_filters:
            if f.startswith("_"):
                continue
            filter_module_names.append("align.filter" + "." + f.replace(".py", ""))

        logging.info("filter_module_names: %s", filter_module_names)

        for filter_module_name in filter_module_names:
            try:
                module = importlib.import_module(filter_module_name)
                classes = [
                    cls_obj
                    for cls_name, cls_obj in inspect.getmembers(module)
                    if inspect.isclass(cls_obj)
                ]

                for cl in classes:
                    if cl != Filter and issubclass(cl, Filter):
                        self._filter_classes.append(cl)
                        logging.debug("added class %s", cl.__name__)
            except BaseException as error:
                logging.error("Error while importing module: %s", error)
                continue

        logging.info("Filter classes available: %s", self._filter_classes)

    def get_filter_names(self) -> list:
        """Returns a list with all found filter names

        Returns
        -------
        list
            a list with all found filter names
        """
        filter_names = []
        for filter_class in self._filter_classes:
            fltr = filter_class()
            filter_names.append(fltr.get_filter_name())
        return filter_names

    def get_filter_by_name(self, filter_name: str) -> Filter | None:
        """Returns a Filter object that matches the given name

        Parameters
        ----------
        trigger_name : str
            name of filter

        Returns
        -------
        Filter, None
            Returns a Filter object that matches the given name or None if
            no matching filter was found
        """
        for filter_class in self._filter_classes:
            fltr = filter_class()
            if filter_name == fltr.get_filter_name():
                return fltr
        return None


class Filter(ABC):
    """Abstract class for filter
    _filter_name and _filter_options have to be defined in each subclass derived from this Trigger class
    """

    _filter_name = "example_filter"

    _filter_options = dict(
        name=_filter_name,
        title="Example Filter",
        type="group",
        removable=True,
        movable=True,
        children=[
            dict(name="enabled", type="bool", value=True),
            dict(name="parameter1", type="int"),
        ],
    )

    @classmethod
    def get_filter_name(cls) -> str:
        """Returns the name of the filter

        Returns
        -------
        str
            Returns the name of the filter
        """
        return cls._filter_name

    @classmethod
    def get_filter_options(cls) -> dict:
        """Returns filter options

        Returns
        -------
        dict
            dictionary which contains the current filter options
        """
        return cls._filter_options

    @abstractmethod
    def process_data(self, input_data: ndarray, filter_parameter: dict) -> dict:
        """Applies filters to the input data based on the given parameter
        This abstract method has to be overridden in each subclass derived from Filter class

        Parameters
        ----------
        input_data : ndarray
            trace on which the filter function should be applied on
        filter_parameter : dict
            dictionary which contains the filter(-specific) parameters

        Returns
        -------
        dict
            dictionary with keyword 'data' which contains the processed data: dict(data=output_data)
        """
