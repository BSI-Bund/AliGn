from __future__ import annotations
import importlib
import inspect
import logging
from os import listdir
from os.path import isfile, join
from abc import ABC, abstractmethod
from pathlib import Path

from numpy import ndarray


class TriggerLoader:
    """This class searches in the trigger_folder ('./align/trigger') for files that
    contains subclasses from "Trigger" class and add them to a trigger list
    which contains valid AliGn triggers."""

    def __init__(self):
        logging.getLogger(__name__)
        self._trigger_classes = []

        trigger_folder = Path(__file__).resolve().parent
        files_in_triggers = [
            f for f in listdir(trigger_folder) if isfile(join(trigger_folder, f))
        ]
        logging.debug("Files in trigger folders: %s", files_in_triggers)
        trigger_module_names = []

        for f in files_in_triggers:
            if f.startswith("_"):
                continue
            trigger_module_names.append("align.trigger" + "." + f.replace(".py", ""))

        logging.info("trigger_module_names: %s", trigger_module_names)

        for trigger_module_name in trigger_module_names:
            try:
                module = importlib.import_module(trigger_module_name)
                classes = [
                    cls_obj
                    for cls_name, cls_obj in inspect.getmembers(module)
                    if inspect.isclass(cls_obj)
                ]

                for cl in classes:
                    if cl != Trigger and issubclass(cl, Trigger):
                        self._trigger_classes.append(cl)
                        logging.debug("added class %s", cl.__name__)
            except BaseException as error:
                logging.error("Error while importing module: %s", error)
                continue

        logging.info("Trigger classes available: %s", self._trigger_classes)

    def get_trigger_names(self) -> list:
        """Returns a list with all found trigger names

        Returns
        -------
        list
            a list with all found trigger names
        """
        trigger_names = []
        for trigger_class in self._trigger_classes:
            trgr = trigger_class()
            trigger_names.append(trgr.get_trigger_name())
        return trigger_names

    def get_trigger_by_name(self, trigger_name: str) -> Trigger | None:
        """Returns a Trigger object that matches the given name

        Parameters
        ----------
        trigger_name : str
            name of trigger

        Returns
        -------
        Trigger, None
            Returns a Trigger object that matches the given name or None if
            no matching trigger was found
        """
        for trigger_class in self._trigger_classes:
            trgr = trigger_class()
            if trigger_name == trgr.get_trigger_name():
                return trgr
        return None


class Trigger(ABC):
    """Abstract class for triggers
    _trigger_name and _trigger_options have to be defined in each subclass derived from this Trigger class
    """

    _trigger_name = "example_trigger"
    _trigger_options = dict(
        name=_trigger_name,
        title="Example Trigger",
        type="group",
        removable=True,
        movable=True,
        children=[
            dict(name="parameter1", type="int"),
        ],
    )

    @classmethod
    def get_trigger_name(cls) -> str:
        """Returns the name of the trigger

        Returns
        -------
        str
            the name of the trigger
        """
        return cls._trigger_name

    @classmethod
    def get_trigger_options(cls) -> dict:
        """Returns trigger options

        Returns
        -------
        dict
            dictionary which contains the current trigger options
        """
        return cls._trigger_options

    @abstractmethod
    def process_data(
        self, input_data: ndarray, offset: int, trigger_parameter: dict
    ) -> dict:
        """Method to search a trigger point based on the given parameter
        This abstract method has to be overridden in each subclass derived from Trigger class

          Parameters
          ----------
          input_data : ndarray
              trace in which the trigger should be found
          offset : int
              start the search for trigger at this offset in input_data
          trigger_parameter : dict
              dictionary which contains the trigger(-specific) parameters

          Returns
          -------
          dict
              dictionary with keyword 'xmarks' which contains a list with x-coordinations of one or more trigger points
        """
