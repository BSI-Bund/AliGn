import sys
import os
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import List, Optional
from typing_extensions import Self
import dataconf

APP_NAME = "AliGn"
SETTINGS_FILE = "align_settings.json"


@dataclass
class AlignSettings:
    """Dataclass for re-/storing Align setting from/to file"""

    last_path: Optional[str] = ""
    last_metafile: Optional[str] = ""
    log_level: Optional[str] = "INFO"
    trace_plot_width: Optional[float] = 1.0
    default_region_around_peak: List[int] = field(default_factory=lambda: [-500, 500])

    def save(self) -> None:
        """Stores settings to settings file in the data directory"""
        filename = str(self.get_datadir() / SETTINGS_FILE)
        # self._replace_dataclass_values(None, "")
        dataconf.dump(filename, self, out="json")

    def restore(self) -> Self:
        """Restores settings from settings file in the data directory

        Returns
        -------
        Self
            restored settings
        """
        filename = str(self.get_datadir() / SETTINGS_FILE)
        if os.path.exists(filename):
            settings = dataconf.file(filename, AlignSettings)
            self.__dict__ = settings.__dict__

    def _replace_dataclass_values(self, old_value: str, new_value: any) -> None:
        """Searches in all fields of the given dataclass for the
        given old_value and replaces it with the new_value

          Parameters
          ----------
          old_value : str
              value to replace
          new_value : any
              new value
        """
        for my_field in fields(self):
            field_name = my_field.name
            field_value = getattr(self, field_name)
            if field_value == old_value:
                setattr(self, field_name, new_value)

    def get_datadir(self) -> Path:
        """Returns a parent directory path
        where persistent application data can be stored.
        * linux: ~/.local/share
        * macOS: ~/Library/Application Support
        * windows: C:/Users/<USER>/AppData/Roaming

          Returns
          -------
          Path
              Path of the systems standard application folder
        """
        home = Path.home()
        platform = sys.platform

        if platform == "win32":
            app_data_path = home / "AppData/Roaming"
        elif platform == "linux":
            app_data_path = home / ".local/share"
        elif platform == "darwin":
            app_data_path = home / "Library/Application Support"
        else:
            app_data_path = home

        my_datadir = app_data_path / APP_NAME
        my_datadir.mkdir(parents=True, exist_ok=True)
        return my_datadir
