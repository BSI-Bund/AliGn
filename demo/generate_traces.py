import random
import numpy as np

from align.tracelib.traces import TraceData

# for reproducibility
np.random.seed(42)

# fixed key
key = np.array(
    [
        0xE8,
        0xE9,
        0xEA,
        0xEB,
        0xED,
        0xEE,
        0xEF,
        0xF0,
        0xF2,
        0xF3,
        0xF4,
        0xF5,
        0xF7,
        0xF8,
        0xF9,
        0xFA,
    ]
).astype(np.uint8)

# plain values
plains = np.random.normal(size=(10000, 16))
plains = (plains * 255).astype(np.uint8)

# traces
traces = np.random.normal(scale=1.0, size=(10000, 4000))
traces = (traces * 10).astype(np.int8)

# at a random offset (simulating jitter)
# we have some signal with higher variance,
# where we hide the leakage signal
for i in range(0, 10000):
    if i == 0:
        offset = 100
    else:
        offset = np.random.randint(1, 39) * 100
    high_var_noise = np.random.normal(scale=2.0, size=100)
    for j in range(0, 16):
        leakage_val = ((key[j] ^ plains[i, j]) / 256.0) - 0.5
        high_var_noise[50 + j] = 0.5 * high_var_noise[50 + j] + 0.5 * leakage_val
    high_var_noise = (high_var_noise * 10).astype(np.int8)
    # artificial clock
    high = random.randint(99, 127)
    low = random.randint(-127, -99)
    mid = random.randint(-10, 10)
    traces[i, offset : offset + 3] = high
    traces[i, offset + 3 : offset + 6] = mid
    traces[i, offset + 6 : offset + 9] = low
    # leakage
    traces[i, offset + 10 : offset + 110] = high_var_noise

# save these data as numpy data files
# np.save("traces.npy", traces)
# np.save("plaintext.npy", plains)
# np.save("key.npy", key)

# or employ AliGn's data format
datafile = TraceData()
datafile.startRecord(
    "demo_traces.meta",
    traceCount=10000,
    randomPlain=True,
    randomKey=False,
    algorithm="Unknown",
    needPlain=True,
    needCipher=False,
    needKey=False,
)
datafile.registerEMFile("demo_em.dat", length=4000, dtype=np.int8)
datafile.registerPlainFile("demo_plain.dat", length=16, dtype=np.uint8)

for i in range(0, 10000):
    datafile.em.addTrace(traces[i, :])
    datafile.plain.addTrace(plains[i, :])

datafile.finishRecord()
