import random

import pyqtgraph.parametertree.parameterTypes as pTypes
from PySide6.QtGui import QIcon

from align.filter.filter import FilterLoader
from align.trigger.trigger import TriggerLoader


class FilterGroupParameter(pTypes.GroupParameter):
    """Custom GroupParameter that hold the settings for the filters
    to be used on trace in the parent TraceGroupParameter
    """

    def __init__(self, **opts):
        self._filters = FilterLoader()
        opts["type"] = "group"
        opts["addText"] = "add Filter"
        opts["addList"] = self._filters.get_filter_names()
        opts["context"] = dict(set_batch_filters="Set filters for batch processing")
        opts["dropEnabled"] = True
        opts["objectName"] = "highlighted"
        pTypes.GroupParameter.__init__(self, **opts)

    def addNew(self, typ=None):
        self.insertChild(
            len(self.childs), self._filters.get_filter_by_name(typ).get_filter_options()
        )

    def highlight(self, enable: bool = True) -> None:
        """highlight item.
        Sets an icon and add text 'selected for batch processing'
        Else remove icon and additional text.

          Parameters
          ----------
          enable : bool, optional
              if true highlight this item, by default True
        """
        if enable:
            self.item.setIcon(0, QIcon(":icons/selection_gn.png"))
            self.item.setText(0, self.item.text(0) + " - selected for batch processing")
        else:
            self.item.setIcon(0, QIcon())
            self.item.setText(0, self.title())

    def makeTreeItem(self, depth):
        """Overrides the original method pyqtgraph.parametertree.Parameter.makeTreeItem
        to get access to the GroupParameterItem. This is used to change the layout of this Parameter Item.

          Parameters
          ----------
          depth : int
              depth in parameter tree

          Returns
          -------
          pTypes.GroupParameter
             GroupParameter
        """
        self.item = pTypes.GroupParameterItem(self, depth)
        return self.item


class TriggerGroupParameter(pTypes.GroupParameter):
    """Custom GroupParameter that hold the settings for the triggers
    to be used on trace in the parent TraceGroupParameter
    """

    def __init__(self, **opts):
        self._triggers = TriggerLoader()
        opts["type"] = "group"
        opts["addText"] = "add Trigger"
        opts["addList"] = self._triggers.get_trigger_names()
        opts["context"] = dict(set_batch_triggers="Set triggers for batch processing")
        opts["dropEnabled"] = True
        pTypes.GroupParameter.__init__(self, **opts)

    def addNew(self, typ=None):
        self.insertChild(
            len(self.childs),
            self._triggers.get_trigger_by_name(typ).get_trigger_options(),
        )

    def highlight(self, enable: bool = True) -> None:
        """highlight item.
        Sets an icon and add text 'selected for batch processing'
        Else remove icon and additional text.

          Parameters
          ----------
          enable : bool, optional
              if true highlight this item, by default True
        """
        if enable:
            self.item.setIcon(0, QIcon(":icons/selection_gn.png"))
            self.item.setText(0, self.item.text(0) + " - selected for batch processing")
        else:
            self.item.setIcon(0, QIcon())
            self.item.setText(0, self.title())

    def makeTreeItem(self, depth):
        """Overrides the original method pyqtgraph.parametertree.Parameter.makeTreeItem
        to get access to the GroupParameterItem. This is used to change the layout of this Parameter Item.

          Parameters
          ----------
          depth : int
              depth in parameter tree

          Returns
          -------
          pTypes.GroupParameter
              GroupParameter
        """
        self.item = pTypes.GroupParameterItem(self, depth)
        return self.item


class TraceGroupParameter(pTypes.GroupParameter):
    """Custom GroupParameter which holds the main settings for one trace.
    Following values are stored within this GroupParameter:
    - Trace number
    - Trace type
    - Color in the plot view
    - visual shift in the plot view
    - group of filters
    - group of triggers
    """

    def __init__(self, **opts):
        opts["type"] = "group"
        opts["addText"] = "add Trace"
        self.add_counter = 0
        pTypes.GroupParameter.__init__(self, **opts)

    def addNew(self, trace_nr=None, trace_type_list=[""]):
        self.add_counter += 1
        if trace_nr is None:
            trace_nr = self.add_counter

        trace_options = self.addChild(
            dict(
                name="traceoptions",
                autoIncrementName=True,
                title=f"Trace {trace_nr} options",
                type="group",
                removable=True,
                context=dict(duplicate_trace="Duplicate"),
                children=[
                    dict(
                        name="tracenr",
                        title="Trace",
                        type="int",
                        limits=[0, None],
                        value=trace_nr,
                    ),
                    dict(
                        name="tracetype",
                        title="Trace Type",
                        type="list",
                        limits=trace_type_list,
                    ),
                    dict(
                        name="color",
                        title="Color",
                        type="color",
                        value=random_color(),
                        default=(255, 255, 255, 255),
                    ),
                    dict(
                        name="shift",
                        title="Shift",
                        type="slider",
                        limits=[-10000, 10000],
                        value=0,
                    ),
                    FilterGroupParameter(
                        name="filter_group", title="Filter", type="group"
                    ),
                    TriggerGroupParameter(
                        name="trigger_group", title="Trigger", type="group"
                    ),
                ],
            )
        )
        return trace_options

    def removeChild(self, child):
        super().removeChild(child)
        self.add_counter -= 1


class DataFilesGroupParameter(pTypes.GroupParameter):
    """Custom GroupParameter for storing the data filenames"""

    def __init__(self, **opts):
        opts["type"] = "group"
        pTypes.GroupParameter.__init__(self, **opts)
        self.addChild(dict(name="em_file", title="EM file", type="str", readonly=True))
        self.addChild(
            dict(name="power_file", title="Power file", type="str", readonly=True)
        )
        self.addChild(
            dict(name="plain_file", title="Plain file", type="str", readonly=True)
        )
        self.addChild(
            dict(name="cipher_file", title="Cipher file", type="str", readonly=True)
        )

    def set_file_names(self, data_files: dict):
        self.child("em_file").setValue("")
        self.child("power_file").setValue("")
        self.child("plain_file").setValue("")
        self.child("cipher_file").setValue("")
        for trace_data_name, filename in data_files.items():
            if trace_data_name == "em":
                self.child("em_file").setValue(filename)
            elif trace_data_name == "power":
                self.child("power_file").setValue(filename)
            elif trace_data_name == "plain":
                self.child("plain_file").setValue(filename)
            elif trace_data_name == "cipher":
                self.child("cipher_file").setValue(filename)


def random_color() -> list[int]:
    """Returns a 'random' color (tuple of three values between 50 and 256)

    Returns
    -------
    list
        A list of three int values between 50 and 256
        to interpret as RGB values
    """
    color = random.choices(range(50, 256), k=3)
    return color
