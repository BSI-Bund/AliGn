import dataconf
from align import align_settings

SETTINGS_FILE = "tests/resources/align_settings.json"


def test_write_read_AlignSettings():
    new_settings = align_settings.AlignSettings("/home/user/path/", "", "DEBUG")
    dataconf.dump(SETTINGS_FILE, new_settings, out="json")

    conf = dataconf.file(SETTINGS_FILE, align_settings.AlignSettings)
    assert conf.log_level == "DEBUG"
    assert conf.last_path == "/home/user/path/"


def test_write_read_default_values_AlignSettings():
    new_settings = align_settings.AlignSettings()
    dataconf.dump(SETTINGS_FILE, new_settings, out="json")

    conf = dataconf.file(SETTINGS_FILE, align_settings.AlignSettings)
    assert conf.log_level == "INFO"
    assert conf.last_path == ""


def test_write_read_partial_AlignSettings():
    new_settings = align_settings.AlignSettings(log_level="WARN")
    dataconf.dump(SETTINGS_FILE, new_settings, out="json")

    conf = dataconf.file(SETTINGS_FILE, align_settings.AlignSettings)
    assert conf.log_level == "WARN"
    assert conf.last_path == ""
    assert conf.default_region_around_peak == [-500, 500]


def test_write_read_later_AlignSettings():
    new_settings = align_settings.AlignSettings()
    new_settings.log_level = "ERROR"
    new_settings.default_region_around_peak = [-100, 100]
    dataconf.dump(SETTINGS_FILE, new_settings, out="json")

    conf = dataconf.file(SETTINGS_FILE, align_settings.AlignSettings)
    assert conf.log_level == "ERROR"
    assert conf.default_region_around_peak == [-100, 100]


def test_write_read_None_AlignSettings():
    new_settings = align_settings.AlignSettings()
    new_settings.log_level = None
    new_settings.last_path = "/tmp/"
    dataconf.dump(SETTINGS_FILE, new_settings, out="json")

    conf = dataconf.file(SETTINGS_FILE, align_settings.AlignSettings)
    assert conf.log_level is None
    assert conf.last_path == "/tmp/"
