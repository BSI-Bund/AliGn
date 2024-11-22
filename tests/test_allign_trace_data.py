import os
from pathlib import Path
import shutil
import numpy as np
from align.align_trace_data import AlignTraceDataFactory


test_data_path = Path("tests/resources/testdata/npy/")


## Test that AlignTraceDataFactory can open npy files
#  and parse the contained information correct
def test_AlignTraceDataFactory():
    tmp_path = test_data_path / "tmp"
    npy_files = dict()
    npy_files["em"] = test_data_path / "traces.npy"
    trace_data = AlignTraceDataFactory.open_trace_data(npy_files)
    assert trace_data is not None
    assert trace_data.get_trace("em", 1)[0] == 7


## Test add_trace method and ensure that a TraceData object only accepts
#  the predefined number of traces even if more calls of add_trace were performed
def test_add_trace():
    MAX_NUMBER_OF_TRACES = 3
    tmp_path = test_data_path / "tmp"
    npy_files = dict()
    npy_files["em"] = test_data_path / "traces.npy"
    trace_data = AlignTraceDataFactory.open_trace_data(npy_files)

    ## Prepare/init a new TraceData object based on the actual one at the given file path
    new_trace_data = trace_data.prepare_new_tracedata(tmp_path)
    new_trace_data.set_number_of_traces(MAX_NUMBER_OF_TRACES)
    new_trace_data.register_data_file(
        "em",
        (tmp_path / "em.npy"),
        length=5,
        dtype=np.int16,
    )
    new_trace_data.add_trace("em", np.array([1, 2, 3, 4, 5], dtype=np.int16))
    new_trace_data.add_trace("em", np.array([2, 3, 3, 4, 5], dtype=np.int16))
    new_trace_data.add_trace("em", np.array([3, 2, 3, 4, 5], dtype=np.int16))
    new_trace_data.add_trace("em", np.array([4, 2, 3, 4, 5], dtype=np.int16))
    assert new_trace_data.get_number_of_traces() == MAX_NUMBER_OF_TRACES

    # remove temporary folder which was created while running test case
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)


## Ensure that a new TraceData object returns correct value (False) for has_power method
def test_has_power_from_new_tracedata():
    tmp_path = test_data_path / "tmp"
    npy_files = dict()
    npy_files["em"] = test_data_path / "traces.npy"
    trace_data = AlignTraceDataFactory.open_trace_data(npy_files)
    new_trace_data = trace_data.prepare_new_tracedata(tmp_path)
    assert new_trace_data.has_power() is False
    new_trace_data.set_number_of_traces(3)
    new_trace_data.register_data_file(
        "em",
        (tmp_path / "em.npy"),
        length=5,
        dtype=np.int16,
    )
    new_trace_data.add_trace("em", np.array([1, 2, 3, 4, 5], dtype=np.int16))
    assert new_trace_data.has_power() is False
    assert new_trace_data.finish() is None

    # remove temporary folder which was created while running test case
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)


## Test redurce_data_from_mask method. Ensure that after calling this method only the the masked traces remain
def test_npy_reduce_data_from_mask():
    em_file = test_data_path / "traces.npy"
    plain_file = test_data_path / "plaintext.npy"
    trace_data = AlignTraceDataFactory.open_trace_data(
        {"em": em_file, "plain": plain_file}
    )
    valid_traces_array = np.zeros(trace_data.get_number_of_traces(), dtype=bool)
    valid_traces_array[[1, 4, 8, 12, 17]] = True
    input_traces = trace_data.get_traces("plain")
    assert input_traces.shape[0] > 5
    trace_data.reduce_data_from_mask(
        trace_type="plain", input_data=input_traces, trace_mask=valid_traces_array
    )
    output = trace_data.get_traces("plain")
    assert output.shape[0] == 5
