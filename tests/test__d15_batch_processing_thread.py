import filecmp
import os
from pathlib import Path
import shutil
import pytest

from collections import OrderedDict
from align.align_trace_data import AlignTraceDataFactory
from align.batch_processing import BatchProcessingThread

TEST_PATH = Path("tests/resources/testdata/d15/")
COMPARSION_PATH = TEST_PATH / "processed_for_comparsion"
META_FILE = TEST_PATH / "traces.meta"
NUMBER_OF_TRACES = 100
FILTER_DICT = OrderedDict([])
TRIGGER_DICT = OrderedDict(
    [
        (
            "first_peak_trigger",
            (
                None,
                OrderedDict(
                    [
                        ("min_dist", (0, OrderedDict())),
                        ("threshold", (60, OrderedDict())),
                        ("find_max", (True, OrderedDict())),
                    ]
                ),
            ),
        )
    ]
)


def _progress_signal(progress_dict: dict) -> bool:
    """Signal method that will be called when progress in BatchProcessingThread moved on
    Return true if NUMBER_OF_TRACES traces where processed"""
    return progress_dict["total"] == NUMBER_OF_TRACES


def _finished_signal() -> bool:
    """Signal method that will be called when BatchProcessingThread is finished"""
    return True


@pytest.fixture
def batch_processing_thread() -> BatchProcessingThread:
    """Creates a BatchProcessingThread which will be used in the following test cases"""
    trace_count = NUMBER_OF_TRACES
    trace_type = "em"
    region_around_peak = [-165, 191]
    filter_dict = FILTER_DICT
    trigger_dict = TRIGGER_DICT
    align_trace_data = AlignTraceDataFactory.open_trace_data(META_FILE)
    parent = None

    bp_thread = BatchProcessingThread(
        parent,
        align_trace_data,
        filter_dict,
        trigger_dict,
        region_around_peak,
        trace_type,
        trace_count,
    )
    return bp_thread


def test_thread_finished_within_5000ms_and_files_matches(
    qtbot, batch_processing_thread
):
    """Test that BatchProcessingThread finishs within 5000 ms and the output files
    are equal to the expected files which are stored in the COMPARSION_PATH"""
    batch_processing_thread.finished.connect(_finished_signal)

    with qtbot.waitSignal(
        batch_processing_thread.finished,
        raising=True,
        check_params_cb=_finished_signal,
    ) as _:
        batch_processing_thread.start()

    assert os.path.exists(batch_processing_thread.new_filepath)

    _, mismatch, errors = filecmp.cmpfiles(
        COMPARSION_PATH,
        batch_processing_thread.new_filepath,
        ["em_aligned.dat", "plain_aligned.dat"],
    )
    assert len(mismatch) == 0
    assert len(errors) == 0

    # remove temporary folder which was created while running test case
    if os.path.exists(batch_processing_thread.new_filepath):
        shutil.rmtree(batch_processing_thread.new_filepath)

    batch_processing_thread = None
